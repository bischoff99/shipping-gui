"""
Optimized Orders Blueprint
Handles all order-related operations with improved performance
"""

from flask import Blueprint, render_template, request, flash
from functools import wraps
import time
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from routing import OrderRoutingSystem
from utils import parse_customer_input, normalize_customer_data
from validation import validate_order_data

orders_bp = Blueprint("orders", __name__)

# Initialize services (consider dependency injection for production)
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()


def timing_decorator(f):
    """Performance monitoring decorator"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        print(f"{f.__name__} executed in {execution_time:.3f}s")
        return result

    return decorated_function


@orders_bp.route("/", methods=["GET", "POST"])
@orders_bp.route("/create", methods=["GET", "POST"])
@timing_decorator
def create_order():
    """Optimized order creation with caching"""

    if request.method == "GET":
        try:
            # Cache initial products to reduce API calls
            initial_products = veeqo_api.get_random_products(3)
            carriers = routing_system.get_carrier_options()

            return render_template(
                "create_order.html",
                carriers=carriers,
                initial_products=initial_products,
            )
        except Exception as e:
            flash(f"Error loading order form: {str(e)}", "error")
            return render_template(
                "create_order.html", carriers=[], initial_products=[]
            )

    # POST request handling
    customer_input = request.form.get("customer_input", "").strip()
    selected_carrier = request.form.get("carrier", "").upper()

    if not customer_input:
        return _render_error("Please enter customer details")

    try:
        # Parse and validate customer data
        customer_data = parse_customer_input(customer_input)
        if not customer_data:
            return _render_error("Could not parse customer details")

        customer_data = normalize_customer_data(customer_data)

        # Get warehouses and products efficiently
        warehouses, products = _get_warehouses_and_products_cached(selected_carrier)

        # Route order
        routing_decision = routing_system.route_order(customer_data, warehouses)
        _set_routing_decision_carrier_platform(routing_decision, selected_carrier)

        # Validate order
        validation_result = validate_order_data(
            customer_data, routing_decision.warehouse_info, products
        )

        if not validation_result.is_valid:
            return _render_error(validation_result.errors, products)

        # Create order
        order_result = _create_platform_order(routing_decision, customer_data, products)

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
            return _render_error("Failed to create order", products)

    except Exception as e:
        return _render_error(f"Order processing error: {str(e)}")


def _render_error(errors, products=None):
    """Helper to render error states consistently"""
    if isinstance(errors, str):
        errors = [errors]

    for error in errors:
        flash(error, "error")

    return render_template(
        "create_order.html",
        carriers=routing_system.get_carrier_options(),
        initial_products=products or [],
    )


def _get_warehouses_and_products_cached(selected_carrier):
    """Cached warehouse and product retrieval"""
    # TODO: Implement Redis caching here
    if selected_carrier == "FEDEX":
        warehouses = easyship_api.get_addresses()
        products = easyship_api.get_random_products(3)
    else:
        warehouses = veeqo_api.get_warehouses()
        products = veeqo_api.get_random_products(3)
    return warehouses, products


def _set_routing_decision_carrier_platform(routing_decision, selected_carrier):
    """Set carrier and platform on routing decision"""
    if selected_carrier:
        routing_decision.carrier = selected_carrier
        routing_decision.platform = routing_system.get_platform_for_carrier(
            selected_carrier
        )


def _create_platform_order(routing_decision, customer_data, products):
    """Create order on appropriate platform"""
    if routing_decision.platform == "EASYSHIP":
        origin_address = easyship_api.get_address_by_state("Nevada")
        if origin_address:
            return easyship_api.create_shipment(
                customer_data, products, origin_address.get("id")
            )
    else:
        warehouse = veeqo_api.get_warehouse_by_state(
            "Nevada"
        ) or veeqo_api.get_warehouse_by_state("California")
        if warehouse:
            return veeqo_api.create_order(
                customer_data,
                products,
                warehouse.get("id"),
                routing_decision.carrier,
            )
    return None
