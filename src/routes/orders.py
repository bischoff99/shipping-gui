"""
Orders Route Module - MCP Enhanced
Extracted from monolithic app.py for better maintainability
"""
from flask import Blueprint, render_template, request, flash, jsonify, g
from src.middleware.security import validate_json_input, CustomerInputSchema
from utils import parse_customer_input, normalize_customer_data
from validation import validate_order_data, validate_customer_data
from routing import OrderRoutingSystem
from api.easyship_api import EasyshipAPI
from api.veeqo_api import VeeqoAPI

# Create blueprint
orders_bp = Blueprint('orders', __name__)

# Initialize services (these will be dependency injected in production)
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()

# Template constants
CREATE_ORDER_TEMPLATE = "create_order.html"


@orders_bp.route("/", methods=["GET", "POST"])
@orders_bp.route("/create_order", methods=["GET", "POST"])
def create_order():
    """Enhanced order creation with security validation"""
    
    def _render_create_order(errors=None, warnings=None, initial_products=None):
        """Helper to render order creation page"""
        if errors:
            for error in errors:
                flash(error, "error")
        if warnings:
            for warning in warnings:
                flash(warning, "warning")

        # Get initial products for preview (default to Veeqo products)
        if not initial_products:
            try:
                initial_products = veeqo_api.get_random_products(3)
            except (KeyError, ValueError, RuntimeError) as e:
                current_app.logger.error(f"Error fetching initial products: {e}")
                initial_products = []

        return render_template(
            CREATE_ORDER_TEMPLATE,
            carriers=routing_system.get_carrier_options(),
            initial_products=initial_products,
        )

    if request.method != "POST":
        return _render_create_order()

    # Enhanced input validation
    customer_input = request.form.get("customer_input", "").strip()
    selected_carrier = request.form.get("carrier", "").upper()

    if not customer_input:
        return _render_create_order(errors=["Please enter customer details"])

    try:
        # Parse and validate customer data
        customer_data = parse_customer_input(customer_input)
        if not customer_data:
            return _render_create_order(
                errors=["Could not parse customer details. Please check format."]
            )

        customer_data = normalize_customer_data(customer_data)

        # Get warehouses and products based on carrier
        warehouses, products = get_warehouses_and_products(selected_carrier)
        
        # Intelligent routing decision
        routing_decision = routing_system.route_order(customer_data, warehouses)
        set_routing_decision_carrier_platform(routing_decision, selected_carrier)

        # Comprehensive validation
        validation_result = validate_order_data(
            customer_data, routing_decision.warehouse_info, products
        )

        if not validation_result.is_valid:
            return _render_create_order(
                errors=validation_result.errors, initial_products=products
            )

        if validation_result.warnings:
            for warning in validation_result.warnings:
                flash(warning, "warning")

        # Create order on appropriate platform
        order_result = create_platform_order(routing_decision, customer_data, products)

        if order_result:
            flash("Order created successfully!", "success")
            return render_template(
                "order_success.html",
                order=order_result,
                customer=customer_data,
                routing=routing_decision,
                products=products,
            )
        else:
            flash("Failed to create order. Please try again.", "error")
            return _render_create_order(initial_products=products)
            
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Error processing order: {str(e)}", "error")
        return _render_create_order()
    except Exception as e:
        current_app.logger.error(f"Unexpected error processing order: {str(e)}")
        flash(f"Unexpected error processing order: {str(e)}", "error")
        return _render_create_order()


@orders_bp.route("/api/create_order", methods=["POST"])
@validate_json_input(CustomerInputSchema)
def api_create_order():
    """Enhanced API endpoint to create orders with validation"""
    try:
        # Get validated data from middleware
        customer_data = g.validated_data
        
        # Extract additional order data
        raw_data = request.get_json()
        products = raw_data.get("products", [])
        routing_data = raw_data.get("routing_data", {})

        # Validate required data
        if not products:
            return jsonify({
                "success": False, 
                "error": "At least one product is required"
            }), 400

        # Use order processor for complete workflow
        from services.order_processor import OrderProcessor
        processor = OrderProcessor()
        
        # Process the order with enhanced error handling
        order_result = processor.process_order(customer_data, products)
        
        if order_result.get("success"):
            return jsonify({
                "success": True,
                "order_id": order_result.get("order_id"),
                "platform": order_result.get("platform"),
                "tracking_info": order_result.get("tracking_info"),
                "message": "Order created successfully!"
            })
        else:
            return jsonify({
                "success": False,
                "error": order_result.get("error", "Unknown error occurred")
            }), 500

    except Exception as e:
        current_app.logger.error(f"API order creation error: {e}")
        return jsonify({
            "success": False, 
            "error": "Internal server error"
        }), 500


def get_warehouses_and_products(selected_carrier):
    """Helper to get warehouses and products based on carrier"""
    try:
        if selected_carrier == "FEDEX":
            warehouses = easyship_api.get_addresses()
            products = easyship_api.get_random_products(3)
        else:
            warehouses = veeqo_api.get_warehouses()
            products = veeqo_api.get_random_products(3)
        return warehouses, products
    except Exception as e:
        current_app.logger.error(f"Error fetching warehouses/products: {e}")
        return [], []


def set_routing_decision_carrier_platform(routing_decision, selected_carrier):
    """Helper to set carrier and platform on routing decision"""
    if selected_carrier:
        routing_decision.carrier = selected_carrier
        routing_decision.platform = routing_system.get_platform_for_carrier(
            selected_carrier
        )


def create_platform_order(routing_decision, customer_data, products):
    """Helper to create order on the correct platform"""
    try:
        if routing_decision.platform == "EASYSHIP":
            origin_address = easyship_api.get_address_by_state("Nevada")
            if origin_address:
                return easyship_api.create_shipment(
                    customer_data, products, origin_address.get("id")
                )
        else:
            warehouse = veeqo_api.get_warehouse_by_state(
                "NV"
            ) or veeqo_api.get_warehouse_by_state("CA")
            if warehouse:
                warehouse_id = warehouse.get("id")
                if warehouse_id is not None:
                    return veeqo_api.create_order(
                        customer_data,
                        products,
                        warehouse_id,
                        routing_decision.carrier,
                    )
                else:
                    raise ValueError("Warehouse ID is missing.")
        return None
    except Exception as e:
        current_app.logger.error(f"Error creating platform order: {e}")
        return None