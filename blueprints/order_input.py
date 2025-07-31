"""
Copy-Paste Order Input System Blueprint
Intelligent text parsing for customer orders with routing automation
"""

from flask import Blueprint, render_template, request, jsonify, flash
import re
from typing import Dict, List
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from routing import OrderRoutingSystem
from models import db, Product, Warehouse, ProductInventory

order_input_bp = Blueprint("order_input", __name__)


class OrderInputParser:
    """Intelligent order input parser for copy-paste customer data"""

    def __init__(self):
        self.patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(
                r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
            ),
            "state_abbr": re.compile(r"\b[A-Z]{2}\b"),
            "zip_code": re.compile(r"\b\d{5}(?:-\d{4})?\b"),
            "carrier": re.compile(r"\b(FEDEX|UPS|DHL|USPS)\b", re.IGNORECASE),
            "price": re.compile(r"\$(\d+\.?\d*)"),
        }

        # US State mappings
        self.state_mapping = {
            "NV": "Nevada",
            "CA": "California",
            "NY": "New York",
            "FL": "Florida",
            "TX": "Texas",
            "WA": "Washington",
        }

    def parse_customer_input(self, text: str) -> Dict:
        """Parse customer order input text"""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        customer_data = {
            "name": "",
            "email": "",
            "phone": "",
            "address_1": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "country": "US",
            "carrier": "",
            "products_requested": [],
        }

        # Extract structured data
        for line in lines:
            self._extract_from_line(line, customer_data)

        # Post-processing
        self._post_process_data(customer_data)

        return customer_data

    def _extract_from_line(self, line: str, data: Dict):
        """Extract information from a single line"""
        line_lower = line.lower()

        # Email extraction
        if email_match := self.patterns["email"].search(line):
            data["email"] = email_match.group()

        # Phone extraction
        if phone_match := self.patterns["phone"].search(line):
            data["phone"] = (
                f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"
            )

        # Carrier extraction
        if carrier_match := self.patterns["carrier"].search(line):
            data["carrier"] = carrier_match.group().upper()

        # State and ZIP extraction
        if state_match := self.patterns["state_abbr"].search(line):
            state_code = state_match.group()
            if state_code in self.state_mapping:
                data["state"] = self.state_mapping[state_code]

        if zip_match := self.patterns["zip_code"].search(line):
            data["postal_code"] = zip_match.group()

        # Name extraction (heuristic)
        if not data["name"] and not any(
            pattern in line_lower for pattern in ["@", "phone", "tel", "email"]
        ):
            if len(line.split()) <= 4 and all(
                word.isalpha() or word.capitalize() == word for word in line.split()
            ):
                data["name"] = line

        # Address extraction (heuristic)
        if not data["address_1"] and any(
            indicator in line_lower
            for indicator in ["st", "ave", "rd", "blvd", "street", "avenue"]
        ):
            data["address_1"] = line

        # City extraction (between address and state)
        if data["address_1"] and not data["city"] and data["state"]:
            if line != data["address_1"] and data["state"].lower() not in line_lower:
                data["city"] = line

    def _post_process_data(self, data: Dict):
        """Post-process extracted data"""
        # Default carrier based on state
        if not data["carrier"]:
            state = data["state"].upper()
            if "NEVADA" in state:
                data["carrier"] = "UPS"  # Nevada → Veeqo (UPS preferred)
            elif "CALIFORNIA" in state:
                data["carrier"] = "FEDEX"  # California → Easyship (FedEx)
            else:
                data["carrier"] = "UPS"  # Default

        # Clean up name
        if data["name"]:
            data["name"] = " ".join(word.capitalize() for word in data["name"].split())


class InventoryManager:
    """Manual inventory management for order processing"""

    @staticmethod
    def get_available_products_by_state(state: str, limit: int = 10) -> List[Dict]:
        """Get available products based on customer state (Nevada/California routing)"""
        # Determine warehouse region based on state
        if "NEVADA" in state.upper():
            platform = "veeqo"
        elif "CALIFORNIA" in state.upper():
            platform = "easyship"
        else:
            platform = "veeqo"  # Default

        # Get warehouses for the platform
        warehouses = Warehouse.query.filter(
            Warehouse.platform.in_([platform, "both"])
        ).all()

        warehouse_ids = [w.id for w in warehouses]

        # Get products with available inventory in these warehouses
        available_products = (
            db.session.query(Product, ProductInventory)
            .join(ProductInventory, ProductInventory.product_id == Product.id)
            .filter(
                ProductInventory.warehouse_id.in_(warehouse_ids),
                ProductInventory.quantity > ProductInventory.allocated_quantity,
                Product.active == True,
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "title": product.title,
                "price": float(product.price) if product.price else 29.99,
                "weight_grams": product.weight_grams,
                "available_qty": inventory.available_quantity,
                "warehouse_id": inventory.warehouse_id,
            }
            for product, inventory in available_products
        ]

    @staticmethod
    def check_inventory_availability(
        product_ids: List[int], quantities: List[int]
    ) -> Dict:
        """Check if requested products are available"""
        availability = {}

        for product_id, requested_qty in zip(product_ids, quantities):
            product = Product.query.get(product_id)
            if not product:
                availability[product_id] = {
                    "available": False,
                    "reason": "Product not found",
                }
                continue

            total_available = sum(
                inv.available_quantity for inv in product.inventory_items
            )

            availability[product_id] = {
                "available": total_available >= requested_qty,
                "available_qty": total_available,
                "requested_qty": requested_qty,
                "product_title": product.title,
            }

        return availability


@order_input_bp.route("/paste_order", methods=["GET", "POST"])
def paste_order():
    """Copy-paste order input interface"""
    if request.method == "GET":
        return render_template("order_input/paste_order.html")

    # Parse the pasted input
    parser = OrderInputParser()
    raw_input = request.form.get("order_input", "").strip()

    if not raw_input:
        flash("Please paste customer order details", "error")
        return render_template("order_input/paste_order.html")

    try:
        # Parse customer data
        customer_data = parser.parse_customer_input(raw_input)

        # Get available products based on customer location
        available_products = InventoryManager.get_available_products_by_state(
            customer_data.get("state", ""), limit=15
        )

        # Initialize routing system
        routing_system = OrderRoutingSystem()

        # Get dummy warehouses for routing (will be replaced with real API
        # calls)
        dummy_warehouses = [{"id": 1, "region": customer_data.get("state", "Nevada")}]
        routing_decision = routing_system.route_order(customer_data, dummy_warehouses)

        return render_template(
            "order_input/order_preview.html",
            customer_data=customer_data,
            available_products=available_products,
            routing_decision=routing_decision,
            raw_input=raw_input,
        )

    except Exception as e:
        flash(f"Error parsing order: {str(e)}", "error")
        return render_template("order_input/paste_order.html", raw_input=raw_input)


@order_input_bp.route("/api/process_order", methods=["POST"])
def api_process_order():
    """API endpoint to process the parsed order"""
    try:
        data = request.get_json()
        customer_data = data.get("customer_data", {})
        selected_products = data.get("selected_products", [])

        if not customer_data or not selected_products:
            return jsonify({"error": "Missing customer data or products"}), 400

        # Check inventory availability
        product_ids = [p["id"] for p in selected_products]
        quantities = [p.get("quantity", 1) for p in selected_products]

        availability = InventoryManager.check_inventory_availability(
            product_ids, quantities
        )

        # Check if all products are available
        unavailable_products = [
            avail for avail in availability.values() if not avail["available"]
        ]

        if unavailable_products:
            return (
                jsonify(
                    {
                        "error": "Some products are not available",
                        "unavailable_products": unavailable_products,
                    }
                ),
                400,
            )

        # Process order based on routing decision
        platform = customer_data.get("routing_platform", "veeqo").lower()

        if platform == "easyship":
            # Process with Easyship API (California/FedEx)
            easyship_api = EasyshipAPI()
            # Get California warehouse/address
            origin_address = easyship_api.get_address_by_state("California")
            if origin_address:
                result = easyship_api.create_shipment(
                    customer_data, selected_products, origin_address.get("id")
                )
        else:
            # Process with Veeqo API (Nevada/UPS/DHL/USPS)
            veeqo_api = VeeqoAPI()
            warehouse = veeqo_api.get_warehouse_by_state("Nevada")
            if warehouse:
                result = veeqo_api.create_order(
                    customer_data,
                    selected_products,
                    warehouse.get("id"),
                    customer_data.get("carrier", "UPS"),
                )

        return jsonify(
            {
                "success": True,
                "order_result": result,
                "platform": platform,
                "message": f"Order processed successfully via {platform.title()}",
            }
        )

    except Exception as e:
        return jsonify({"error": f"Order processing failed: {str(e)}"}), 500


@order_input_bp.route("/api/parse_preview", methods=["POST"])
def api_parse_preview():
    """API endpoint for real-time parsing preview"""
    try:
        data = request.get_json()
        raw_input = data.get("input", "")

        parser = OrderInputParser()
        parsed_data = parser.parse_customer_input(raw_input)

        return jsonify(
            {
                "parsed_data": parsed_data,
                "confidence": _calculate_parsing_confidence(parsed_data),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _calculate_parsing_confidence(data: Dict) -> float:
    """Calculate confidence score for parsed data"""
    score = 0.0
    max_score = 100.0

    # Essential fields
    if data.get("name"):
        score += 15
    if data.get("email"):
        score += 20
    if data.get("phone"):
        score += 15
    if data.get("address_1"):
        score += 20
    if data.get("city"):
        score += 10
    if data.get("state"):
        score += 10
    if data.get("postal_code"):
        score += 10

    return min(score, max_score)
