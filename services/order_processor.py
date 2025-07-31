"""
Enhanced Order Processing Service
Handles order creation with improved error handling and inventory management
"""

import logging
from typing import Dict, List
from datetime import datetime
from models import db, Product, Warehouse, ProductInventory
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from routing import OrderRoutingSystem, RoutingDecision

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderProcessor:
    """Enhanced order processing with manual inventory management"""

    def __init__(self):
        self.veeqo_api = VeeqoAPI()
        self.easyship_api = EasyshipAPI()
        self.routing_system = OrderRoutingSystem()

    def process_order(
        self, customer_data: Dict, requested_products: List[Dict]
    ) -> Dict:
        """
        Process complete order with inventory validation and API integration

        Args:
            customer_data: Customer information (name, address, etc.)
            requested_products: List of products with quantities

        Returns:
            Dict with order result, success status, and any errors
        """
        try:
            logger.info(
                f"Processing order for customer: {
                    customer_data.get(
                        'name', 'Unknown')}"
            )

            # Step 1: Validate customer data
            validation_result = self._validate_customer_data(customer_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Customer data validation failed",
                    "details": validation_result["errors"],
                }

            # Step 2: Check inventory availability
            inventory_check = self._check_inventory_availability(requested_products)
            if not inventory_check["available"]:
                return {
                    "success": False,
                    "error": "Insufficient inventory",
                    "details": inventory_check["details"],
                }

            # Step 3: Determine routing (Nevada -> Veeqo, California ->
            # Easyship)
            routing_decision = self._determine_routing(
                customer_data, inventory_check["warehouses"]
            )

            # Step 4: Reserve inventory
            reservation_result = self._reserve_inventory(
                requested_products, inventory_check["inventory_items"]
            )
            if not reservation_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to reserve inventory",
                    "details": reservation_result["error"],
                }

            # Step 5: Create order on appropriate platform
            order_result = self._create_platform_order(
                customer_data, requested_products, routing_decision
            )

            if order_result["success"]:
                # Step 6: Commit inventory allocation
                self._commit_inventory_allocation(reservation_result["reservation_id"])

                logger.info(
                    f"Order processed successfully via {
                        routing_decision.platform}"
                )
                return {
                    "success": True,
                    "order_id": order_result.get("order_id"),
                    "platform": routing_decision.platform,
                    "carrier": routing_decision.carrier,
                    "warehouse": routing_decision.warehouse_info.get("name"),
                    "tracking_info": order_result.get("tracking_info"),
                    "total_cost": self._calculate_order_total(requested_products),
                }
            else:
                # Rollback inventory reservation
                self._rollback_inventory_reservation(
                    reservation_result["reservation_id"]
                )
                return {
                    "success": False,
                    "error": "Platform order creation failed",
                    "details": order_result.get("error"),
                }

        except Exception as e:
            logger.error(f"Order processing error: {str(e)}")
            return {
                "success": False,
                "error": "Order processing failed",
                "details": str(e),
            }

    def _validate_customer_data(self, customer_data: Dict) -> Dict:
        """Validate required customer data"""
        required_fields = ["name", "address_1", "city", "state", "postal_code"]
        errors = []

        for field in required_fields:
            if not customer_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Email or phone required
        if not customer_data.get("email") and not customer_data.get("phone"):
            errors.append("Either email or phone number is required")

        return {"valid": len(errors) == 0, "errors": errors}

    def _check_inventory_availability(self, requested_products: List[Dict]) -> Dict:
        """Check if all requested products are available in inventory"""
        availability_details = []
        available_inventory = []
        all_warehouses = []

        for product_request in requested_products:
            product_id = product_request.get("id") or product_request.get("product_id")
            requested_qty = product_request.get("quantity", 1)

            if not product_id:
                availability_details.append(
                    {
                        "product": "Unknown",
                        "available": False,
                        "reason": "Product ID missing",
                    }
                )
                continue

            # Get product and its inventory
            product = Product.query.get(product_id)
            if not product or not product.active:
                availability_details.append(
                    {
                        "product": product.title if product else "Unknown",
                        "available": False,
                        "reason": "Product not found or inactive",
                    }
                )
                continue

            # Check inventory across all warehouses
            inventory_items = (
                ProductInventory.query.filter_by(product_id=product_id)
                .join(Warehouse)
                .filter(ProductInventory.quantity > ProductInventory.allocated_quantity)
                .all()
            )

            total_available = sum(item.available_quantity for item in inventory_items)

            if total_available >= requested_qty:
                availability_details.append(
                    {
                        "product": product.title,
                        "sku": product.sku,
                        "requested": requested_qty,
                        "available": True,
                        "total_available": total_available,
                    }
                )
                available_inventory.append(
                    {
                        "product_id": product_id,
                        "requested_qty": requested_qty,
                        "inventory_items": inventory_items,
                    }
                )
                all_warehouses.extend([item.warehouse for item in inventory_items])
            else:
                availability_details.append(
                    {
                        "product": product.title,
                        "sku": product.sku,
                        "requested": requested_qty,
                        "available": False,
                        "total_available": total_available,
                        "reason": "Insufficient inventory",
                    }
                )

        all_available = all(detail["available"] for detail in availability_details)

        return {
            "available": all_available,
            "details": availability_details,
            "inventory_items": available_inventory,
            "warehouses": list(set(all_warehouses)),
        }

    def _determine_routing(
        self, customer_data: Dict, available_warehouses: List
    ) -> RoutingDecision:
        """Determine the best routing for the order"""
        # Convert warehouse objects to dicts for routing system
        warehouse_dicts = []
        for warehouse in available_warehouses:
            warehouse_dicts.append(
                {
                    "id": warehouse.id,
                    "name": warehouse.name,
                    "region": warehouse.state,
                    "platform": warehouse.platform,
                }
            )

        # Use routing system to make decision
        routing_decision = self.routing_system.route_order(
            customer_data, warehouse_dicts
        )

        # Override platform based on warehouse location if needed
        customer_state = customer_data.get("state", "").upper()
        if "CALIFORNIA" in customer_state:
            routing_decision.platform = "EASYSHIP"
            routing_decision.carrier = "FEDEX"
        elif "NEVADA" in customer_state:
            routing_decision.platform = "VEEQO"
            routing_decision.carrier = customer_data.get("carrier", "UPS")

        return routing_decision

    def _reserve_inventory(
        self, requested_products: List[Dict], inventory_items: List[Dict]
    ) -> Dict:
        """Reserve inventory for the order"""
        try:
            reservation_id = f"res_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            for product_request in requested_products:
                product_id = product_request.get("id") or product_request.get(
                    "product_id"
                )
                requested_qty = product_request.get("quantity", 1)

                # Find matching inventory items
                matching_inventory = next(
                    (
                        item
                        for item in inventory_items
                        if item["product_id"] == product_id
                    ),
                    None,
                )

                if not matching_inventory:
                    continue

                # Allocate inventory from available warehouses
                remaining_qty = requested_qty
                for inventory_item in matching_inventory["inventory_items"]:
                    if remaining_qty <= 0:
                        break

                    available = inventory_item.available_quantity
                    to_allocate = min(remaining_qty, available)

                    if to_allocate > 0:
                        inventory_item.allocated_quantity += to_allocate
                        remaining_qty -= to_allocate

            # Commit the allocation
            db.session.commit()

            return {"success": True, "reservation_id": reservation_id}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    def _create_platform_order(
        self,
        customer_data: Dict,
        products: List[Dict],
        routing: RoutingDecision,
    ) -> Dict:
        """Create order on the appropriate platform"""
        try:
            if routing.platform == "EASYSHIP":
                return self._create_easyship_order(customer_data, products, routing)
            else:
                return self._create_veeqo_order(customer_data, products, routing)

        except Exception as e:
            logger.error(f"Platform order creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    def _create_easyship_order(
        self,
        customer_data: Dict,
        products: List[Dict],
        routing: RoutingDecision,
    ) -> Dict:
        """Create order via Easyship API"""
        try:
            # Get California warehouse/address
            california_address = self.easyship_api.get_address_by_state("California")
            if not california_address:
                return {
                    "success": False,
                    "error": "No California address found in Easyship",
                }

            # Create shipment
            result = self.easyship_api.create_shipment(
                customer_data, products, california_address.get("id")
            )

            if result:
                return {
                    "success": True,
                    "order_id": result.get("id"),
                    "tracking_info": result.get("tracking_code"),
                    "platform_response": result,
                }
            else:
                return {
                    "success": False,
                    "error": "Easyship shipment creation failed",
                }

        except Exception as e:
            return {"success": False, "error": f"Easyship API error: {str(e)}"}

    def _create_veeqo_order(
        self,
        customer_data: Dict,
        products: List[Dict],
        routing: RoutingDecision,
    ) -> Dict:
        """Create order via Veeqo API"""
        try:
            # Get Nevada warehouse
            nevada_warehouse = self.veeqo_api.get_warehouse_by_state("Nevada")
            if not nevada_warehouse:
                return {
                    "success": False,
                    "error": "No Nevada warehouse found in Veeqo",
                }

            # Create order
            result = self.veeqo_api.create_order(
                customer_data,
                products,
                nevada_warehouse.get("id"),
                routing.carrier,
            )

            if result:
                return {
                    "success": True,
                    "order_id": result.get("id"),
                    "tracking_info": result.get("tracking_number"),
                    "platform_response": result,
                }
            else:
                return {
                    "success": False,
                    "error": "Veeqo order creation failed",
                }

        except Exception as e:
            return {"success": False, "error": f"Veeqo API error: {str(e)}"}

    def _commit_inventory_allocation(self, reservation_id: str):
        """Commit the inventory allocation (reduce physical quantity)"""
        try:
            # In this simplified version, allocated quantity is already updated
            # In a more complex system, you might want to track reservations
            # separately
            logger.info(
                f"Inventory allocation committed for reservation: {reservation_id}"
            )
        except Exception as e:
            logger.error(f"Error committing inventory allocation: {str(e)}")

    def _rollback_inventory_reservation(self, reservation_id: str):
        """Rollback inventory reservation in case of order failure"""
        try:
            # This would reverse the allocated quantity changes
            # For now, just log the rollback
            logger.warning(f"Rolling back inventory reservation: {reservation_id}")
            # Note: In production, implement actual rollback logic
        except Exception as e:
            logger.error(f"Error rolling back reservation: {str(e)}")

    def _calculate_order_total(self, products: List[Dict]) -> float:
        """Calculate total order cost"""
        total = 0.0
        for product in products:
            price = float(product.get("price", 0))
            quantity = product.get("quantity", 1)
            total += price * quantity
        return round(total, 2)

    def get_shipping_quote(self, customer_data: Dict, products: List[Dict]) -> Dict:
        """Get shipping quote without creating order"""
        try:
            routing_decision = self._determine_routing(customer_data, [])

            # Mock shipping rates (in production, call actual APIs)
            base_rate = 8.50
            weight_factor = (
                sum(float(p.get("weight_grams", 500)) for p in products) / 1000
            )  # kg
            distance_factor = (
                1.2
                if customer_data.get("state", "").upper()
                not in ["NEVADA", "CALIFORNIA"]
                else 1.0
            )

            estimated_cost = base_rate + (weight_factor * 2.0) * distance_factor

            return {
                "success": True,
                "estimated_cost": round(estimated_cost, 2),
                "carrier": routing_decision.carrier,
                "platform": routing_decision.platform,
                "estimated_days": "3-5 business days",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
