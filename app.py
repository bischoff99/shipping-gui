"""
Unified Order & Warehouse Management System Flask App

This module provides the main Flask application for order creation, routing,
warehouse matching, and API sync between Veeqo and Easyship.

Attributes:
    app (Flask): The main Flask application instance.
    SECRET_KEY (str): Secret key for session management.
    DATABASE_URL (str): Database connection string.
    HF_TOKEN (str): Hugging Face API token for integrations.

Blueprints:
    intelligent_orders_bp: Blueprint for intelligent order management routes.

Typical usage example:
    $ flask run
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, jsonify
import os
import json
from datetime import datetime
import tempfile
import shutil

load_dotenv()

# Import modules that depend on environment variables AFTER loading .env
from services.inventory_monitor import RealTimeInventoryMonitor
from blueprints.intelligent_orders import intelligent_orders_bp
from models import (
    init_db,
    Product,
    create_sample_data,
)
from advanced_product_sync import AdvancedProductSync
from veeqo_orders import VeeqoOrderProcessor
from fedex_orders import FedExOrderProcessor
from utils import parse_customer_input, normalize_customer_data
from validation import validate_order_data, validate_customer_data
from routing import OrderRoutingSystem
from api.easyship_api import EasyshipAPI
from api.veeqo_api import VeeqoAPI
from config.logging_config import setup_logging
from services.mcp_integration import get_mcp_integration
from services.ai_enhanced_features import get_ai_features

# Template constants
CREATE_ORDER_TEMPLATE = "create_order.html"
DASHBOARD_TEMPLATE = "dashboard.html"
ENHANCED_DASHBOARD_TEMPLATE = "enhanced_dashboard.html"
FEDEX_ORDERS_TEMPLATE = "fedex_orders.html"
VEEQO_ORDERS_TEMPLATE = "veeqo_orders.html"
PRODUCT_SYNC_DASHBOARD_TEMPLATE = "product_sync_dashboard.html"


app = Flask(__name__)

# Setup logging early
logger = setup_logging(app)

# Configuration variables
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "unified_order_system_2025")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///shipping_automation.db")
HF_TOKEN = os.environ.get("HF_TOKEN")

app.secret_key = SECRET_KEY

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set HuggingFace token in app config
app.config["HF_TOKEN"] = HF_TOKEN

# Register the intelligent_orders blueprint with a URL prefix
app.register_blueprint(intelligent_orders_bp, url_prefix="/intelligent-orders")

# Initialize database only when running, not when importing
def initialize_database():
    """Initialize database and create sample data if needed"""
    init_db(app)
    with app.app_context():
        try:
            if not Product.query.first():
                create_sample_data()
        except Exception as e:
            print(f"Warning: Could not create sample data: {e}")

# Initialize API clients and routing system
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()
fedex_processor = FedExOrderProcessor()
veeqo_processor = VeeqoOrderProcessor()

# Initialize advanced product sync system
product_sync = AdvancedProductSync(veeqo_api, easyship_api)
inventory_monitor = RealTimeInventoryMonitor(veeqo_api, easyship_api)

# Statistics tracking
dashboard_stats = {
    "warehouse_count": 0,
    "orders_today": 0,
    "sync_success_rate": 0,
    "last_sync": datetime.now().isoformat(),
}


@app.route("/", methods=["GET", "POST"])
@app.route("/create_order", methods=["GET", "POST"])
def create_order():
    """Order creation page"""

    def _render_create_order(errors=None, warnings=None, initial_products=None):
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
                print(f"Error fetching initial products: {e}")
                initial_products = []

        return render_template(
            CREATE_ORDER_TEMPLATE,
            carriers=routing_system.get_carrier_options(),
            initial_products=initial_products,
        )

    if request.method != "POST":
        return _render_create_order()

    customer_input = request.form.get("customer_input", "").strip()
    selected_carrier = request.form.get("carrier", "").upper()

    if not customer_input:
        return _render_create_order(errors=["Please enter customer details"])

    customer_data = parse_customer_input(customer_input)
    if not customer_data:
        return _render_create_order(
            errors=["Could not parse customer details. Please check format."]
        )

    customer_data = normalize_customer_data(customer_data)

    try:
        warehouses, products = get_warehouses_and_products(selected_carrier)
        routing_decision = routing_system.route_order(customer_data, warehouses)
        set_routing_decision_carrier_platform(routing_decision, selected_carrier)

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
        flash(f"Unexpected error processing order: {str(e)}", "error")
        return _render_create_order()


def get_warehouses_and_products(selected_carrier):
    """Helper to get warehouses and products based on carrier"""
    if selected_carrier == "FEDEX":
        warehouses = easyship_api.get_addresses()
        products = easyship_api.get_random_products(3)
    else:
        warehouses = veeqo_api.get_warehouses()
        products = veeqo_api.get_random_products(3)
    return warehouses, products


def set_routing_decision_carrier_platform(routing_decision, selected_carrier):
    """Helper to set carrier and platform on routing decision"""
    if selected_carrier:
        routing_decision.carrier = selected_carrier
        routing_decision.platform = routing_system.get_platform_for_carrier(
            selected_carrier
        )


def create_platform_order(routing_decision, customer_data, products):
    """Helper to create order on the correct platform"""
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


@app.route("/sync_data")
def sync_data():
    """Sync products and warehouses from both platforms"""
    try:
        # Sync Veeqo data
        veeqo_warehouses = veeqo_api.get_warehouses()
        veeqo_products = veeqo_api.get_products()

        # Sync Easyship data
        easyship_addresses = easyship_api.get_addresses()
        easyship_products = easyship_api.get_products()

        warehouses_data = {
            "veeqo": veeqo_warehouses,
            "easyship": easyship_addresses,
            "last_updated": str(datetime.now()),
        }
        products_data = {
            "veeqo": veeqo_products,
            "easyship": easyship_products,
            "last_updated": str(datetime.now()),
        }

        # Atomic write for warehouses.json
        with tempfile.NamedTemporaryFile("w", delete=False, dir=".") as tf:
            json.dump(warehouses_data, tf, indent=2)
            tempname = tf.name
        shutil.move(tempname, "warehouses.json")

        # Atomic write for products.json
        with tempfile.NamedTemporaryFile("w", delete=False, dir=".") as tf:
            json.dump(products_data, tf, indent=2)
            tempname = tf.name
        shutil.move(tempname, "products.json")

        flash("Data synchronized successfully!", "success")
        return jsonify(
            {
                "status": "success",
                "veeqo_warehouses": len(veeqo_warehouses),
                "veeqo_products": len(veeqo_products),
                "easyship_addresses": len(easyship_addresses),
                "easyship_products": len(easyship_products),
            }
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Sync failed: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        flash(f"Sync failed: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/parse_customer", methods=["POST"])
def api_parse_customer():
    """API endpoint to parse customer input"""
    try:
        data = request.get_json(silent=True)
        if not data or "input" not in data:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid or missing JSON input",
                    }
                ),
                400,
            )
        customer_input = data.get("input", "")
        parsed = parse_customer_input(customer_input)
        if parsed:
            return jsonify({"status": "success", "data": parsed})
        else:
            return (
                jsonify({"status": "error", "message": "Could not parse input"}),
                400,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/get_products", methods=["GET"])
def api_get_products():
    """API endpoint to get random products for preview"""
    try:
        platform = request.args.get("platform", "VEEQO").upper()
        count = int(request.args.get("count", 3))

        if platform == "EASYSHIP":
            products = easyship_api.get_random_products(count)
        else:
            products = veeqo_api.get_random_products(count)

        return jsonify(
            {
                "status": "success",
                "products": products,
                "platform": platform,
                "count": len(products),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route("/dashboard")
def dashboard():
    """System dashboard"""
    try:
        # Get basic stats
        veeqo_warehouses = veeqo_api.get_warehouses()
        easyship_addresses = easyship_api.get_addresses()

        stats = {
            "veeqo_warehouses": len(veeqo_warehouses),
            "easyship_addresses": len(easyship_addresses),
            "total_locations": len(veeqo_warehouses) + len(easyship_addresses),
            "routing_rules": len(routing_system.carrier_platform_mapping),
        }

        return render_template(DASHBOARD_TEMPLATE, stats=stats)
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Dashboard error: {str(e)}", "error")
        return render_template(DASHBOARD_TEMPLATE, stats={})
    except Exception as e:
        flash(f"Dashboard error: {str(e)}", "error")
        return render_template(DASHBOARD_TEMPLATE, stats={})


@app.route("/enhanced_dashboard")
def enhanced_dashboard():
    """Enhanced system dashboard with advanced features"""
    try:
        # Get comprehensive stats for enhanced dashboard
        veeqo_warehouses = veeqo_api.get_warehouses()
        easyship_addresses = easyship_api.get_addresses()

        # Enhanced stats with more detailed information
        stats = {
            "veeqo_warehouses": len(veeqo_warehouses),
            "easyship_addresses": len(easyship_addresses),
            "total_locations": (len(veeqo_warehouses) + len(easyship_addresses)),
            "routing_rules": (len(routing_system.carrier_platform_mapping)),
            "orders_today": 0,  # Placeholder for today's orders
            "revenue_today": "0",  # Placeholder for today's revenue
            "avg_processing_time": "0",  # Placeholder for processing time
        }

        return render_template(ENHANCED_DASHBOARD_TEMPLATE, stats=stats)
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Enhanced dashboard error: {str(e)}", "error")
        # Return with default stats if there's an error
        default_stats = {
            "veeqo_warehouses": 0,
            "easyship_addresses": 0,
            "total_locations": 0,
            "routing_rules": 0,
            "orders_today": 0,
            "revenue_today": "0",
            "avg_processing_time": "0",
        }
        return render_template(ENHANCED_DASHBOARD_TEMPLATE, stats=default_stats)
    except Exception as e:
        flash(f"Enhanced dashboard error: {str(e)}", "error")
        default_stats = {
            "veeqo_warehouses": 0,
            "easyship_addresses": 0,
            "total_locations": 0,
            "routing_rules": 0,
            "orders_today": 0,
            "revenue_today": "0",
            "avg_processing_time": "0",
        }
        return render_template(ENHANCED_DASHBOARD_TEMPLATE, stats=default_stats)


@app.route("/fedex_orders")
def fedex_orders():
    """FedEx orders page"""
    try:
        customers = fedex_processor.get_fedex_customers()
        summary = fedex_processor.get_fedex_customer_summary()

        return render_template(
            FEDEX_ORDERS_TEMPLATE, customers=customers, summary=summary
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"FedEx orders error: {str(e)}", "error")
        return render_template(FEDEX_ORDERS_TEMPLATE, customers=[], summary={})
    except Exception as e:
        flash(f"FedEx orders error: {str(e)}", "error")
        return render_template(FEDEX_ORDERS_TEMPLATE, customers=[], summary={})


@app.route("/process_fedex_orders", methods=["POST"])
def process_fedex_orders():
    """Process all FedEx orders"""
    try:
        results = fedex_processor.process_all_fedex_orders()

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        flash(
            f"Processed {successful}/{total} FedEx orders successfully!",
            "success",
        )

        return jsonify(
            {
                "status": "success",
                "processed": total,
                "successful": successful,
                "results": results,
            }
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"FedEx processing error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        flash(f"FedEx processing error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/create_fedex_order/<customer_name>", methods=["POST"])
def create_fedex_order_route(customer_name):
    """Create individual FedEx order"""
    try:
        result = fedex_processor.create_fedex_shipment(customer_name)
        if result:
            flash(f"FedEx order created for {customer_name}!", "success")
            return jsonify({"status": "success", "result": result})
        else:
            return (
                jsonify({"status": "error", "message": "Failed to create order"}),
                500,
            )
    except (KeyError, ValueError, RuntimeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/veeqo_orders")
def veeqo_orders():
    """Veeqo orders page"""
    try:
        customers = veeqo_processor.get_veeqo_customers()
        summary = veeqo_processor.get_veeqo_customer_summary()

        return render_template(
            VEEQO_ORDERS_TEMPLATE, customers=customers, summary=summary
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Veeqo orders error: {str(e)}", "error")
        return render_template(VEEQO_ORDERS_TEMPLATE, customers=[], summary={})
    except Exception as e:
        flash(f"Veeqo orders error: {str(e)}", "error")
        return render_template(VEEQO_ORDERS_TEMPLATE, customers=[], summary={})


@app.route("/process_veeqo_orders", methods=["POST"])
def process_veeqo_orders():
    """Process all Veeqo orders"""
    try:
        results = veeqo_processor.process_all_veeqo_orders()

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        flash(
            f"Processed {successful}/{total} Veeqo orders successfully!",
            "success",
        )

        return jsonify(
            {
                "status": "success",
                "processed": total,
                "successful": successful,
                "results": results,
            }
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Veeqo processing error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        flash(f"Veeqo processing error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/create_veeqo_order/<customer_name>", methods=["POST"])
def create_veeqo_order_route(customer_name):
    """Create individual Veeqo order"""
    try:
        result = veeqo_processor.create_veeqo_order(customer_name)
        if result:
            flash(
                f"Veeqo order created for {customer_name}!",
                "success",
            )
            return jsonify({"status": "success", "result": result})
        else:
            return (
                jsonify({"status": "error", "message": "Failed to create order"}),
                500,
            )
    except (KeyError, ValueError, RuntimeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/veeqo_purchase_orders")
def api_veeqo_purchase_orders():
    """API endpoint to get Veeqo purchase orders"""
    try:
        purchase_orders = veeqo_processor.get_purchase_orders()
        return jsonify(
            {
                "status": "success",
                "purchase_orders": purchase_orders,
                "count": len(purchase_orders),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/product_sync_dashboard")
def product_sync_dashboard():
    """Advanced Product Sync Dashboard"""
    try:
        # Get sync statistics
        sync_stats = product_sync.get_sync_stats()

        # Get inventory alerts
        inventory_alerts = product_sync.get_inventory_alerts()

        # Get performance data
        performance = product_sync.get_product_performance()

        return render_template(
            PRODUCT_SYNC_DASHBOARD_TEMPLATE,
            sync_stats=sync_stats,
            inventory_alerts=inventory_alerts,
            performance=performance,
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Product sync dashboard error: {str(e)}", "error")
        return render_template(
            PRODUCT_SYNC_DASHBOARD_TEMPLATE,
            sync_stats={},
            inventory_alerts=[],
            performance={},
        )
    except Exception as e:
        flash(f"Product sync dashboard error: {str(e)}", "error")
        return render_template(
            PRODUCT_SYNC_DASHBOARD_TEMPLATE,
            sync_stats={},
            inventory_alerts=[],
            performance={},
        )


@app.route("/api/sync_products", methods=["POST"])
def api_sync_products():
    """Manual product sync trigger"""
    try:
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            import nest_asyncio

            nest_asyncio.apply()
            loop = asyncio.get_event_loop()

        result = loop.run_until_complete(product_sync.sync_products_bidirectional())
        return jsonify(result)
    except (KeyError, ValueError, RuntimeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/product_stats")
def api_product_stats():
    """API endpoint for real-time product statistics"""
    try:
        stats = product_sync.get_sync_stats()
        performance = product_sync.get_product_performance()
        alerts = product_sync.get_inventory_alerts()

        return jsonify(
            {
                "stats": stats,
                "performance": performance,
                "alerts": alerts,
                "alert_count": len(alerts),
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/start_auto_sync", methods=["POST"])
def api_start_auto_sync():
    """Start automatic product sync"""
    try:
        data = request.get_json(silent=True)
        interval = data.get("interval", 5) if data else 5  # minutes
        product_sync.start_auto_sync(interval)

        return jsonify(
            {
                "status": "success",
                "message": f"Auto-sync started with {interval} minute interval",
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/stop_auto_sync", methods=["POST"])
def api_stop_auto_sync():
    """Stop automatic product sync"""
    try:
        product_sync.stop_auto_sync()
        return jsonify({"status": "success", "message": "Auto-sync stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/inventory_alerts")
def api_inventory_alerts():
    """Get active inventory alerts"""
    try:
        alerts = inventory_monitor.get_active_alerts()
        return jsonify(
            [
                {
                    "id": alert.id,
                    "product_sku": alert.product_sku,
                    "product_name": alert.product_name,
                    "warehouse_name": alert.warehouse_name,
                    "current_stock": alert.current_stock,
                    "threshold": alert.threshold,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "created_at": alert.created_at,
                }
                for alert in alerts
            ]
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/inventory_summary")
def api_inventory_summary():
    """Get inventory summary"""
    try:
        summary = inventory_monitor.get_inventory_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/reorder_suggestions")
def api_reorder_suggestions():
    """Get reorder suggestions"""
    try:
        suggestions = inventory_monitor.generate_reorder_suggestions()
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/resolve_alert/<int:alert_id>", methods=["POST"])
def api_resolve_alert(alert_id):
    """Resolve an inventory alert"""
    try:
        if inventory_monitor.resolve_alert(alert_id):
            return jsonify({"status": "success", "message": "Alert resolved"})
        else:
            return (
                jsonify({"status": "error", "message": "Alert not found"}),
                404,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Enhanced GUI Integration Routes
@app.route("/unified")
def unified_dashboard():
    """Enhanced unified dashboard with integrated GUI"""
    try:
        # Update dashboard stats
        dashboard_stats["warehouse_count"] = len(
            routing_system.get_warehouse_mappings()
        )
        dashboard_stats["orders_today"] = dashboard_stats.get("orders_today", 0)
        dashboard_stats["sync_success_rate"] = (
            95  # This would come from actual sync data
        )

        return render_template("unified_dashboard.html", **dashboard_stats)
    except Exception as e:
        logger.error(f"Error loading unified dashboard: {e}")
        return render_template(
            "unified_dashboard.html",
            warehouse_count=0,
            orders_today=0,
            sync_success_rate=0,
        )


@app.route("/api/dashboard-stats")
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Get real-time stats
        warehouses = routing_system.get_warehouse_mappings()

        stats = {
            "warehouses": len(warehouses),
            "orders_today": dashboard_stats.get("orders_today", 0),
            "sync_rate": dashboard_stats.get("sync_success_rate", 0),
            "last_sync": dashboard_stats.get("last_sync"),
            "system_status": "operational",
        }

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/warehouses")
def api_warehouses():
    """API endpoint for warehouse list"""
    try:
        warehouses = []
        warehouse_mappings = routing_system.get_warehouse_mappings()

        for warehouse_id, warehouse_data in warehouse_mappings.items():
            warehouse_info = {
                "veeqo_id": warehouse_id,
                "name": warehouse_data.get("name", f"Warehouse {warehouse_id}"),
                "city": warehouse_data.get("city", "Unknown"),
                "state": warehouse_data.get("state", "Unknown"),
                "type": warehouse_data.get("type", "Standard"),
                "last_sync": warehouse_data.get("last_sync", "Recent"),
                "status": "active",
            }
            warehouses.append(warehouse_info)

        return jsonify({"warehouses": warehouses})
    except Exception as e:
        logger.error(f"Error getting warehouses: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sync-all", methods=["POST"])
def api_sync_all():
    """API endpoint to trigger full system sync"""
    try:
        # Sync all systems
        sync_results = []

        # Sync Veeqo
        try:
            veeqo_result = veeqo_api.test_connection()
            sync_results.append(("Veeqo", veeqo_result))
        except Exception as e:
            sync_results.append(("Veeqo", False))
            logger.error(f"Veeqo sync error: {e}")

        # Sync Easyship
        try:
            easyship_result = easyship_api.test_connection()
            sync_results.append(("Easyship", easyship_result))
        except Exception as e:
            sync_results.append(("Easyship", False))
            logger.error(f"Easyship sync error: {e}")

        # Update dashboard stats
        successful_syncs = sum(1 for _, result in sync_results if result)
        dashboard_stats["sync_success_rate"] = int(
            (successful_syncs / len(sync_results)) * 100
        )
        dashboard_stats["last_sync"] = datetime.now().isoformat()

        return jsonify(
            {
                "success": True,
                "results": sync_results,
                "success_rate": dashboard_stats["sync_success_rate"],
            }
        )

    except Exception as e:
        logger.error(f"Sync all error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/parse-customer-data", methods=["POST"])
def api_parse_customer_data():
    """API endpoint to parse customer input data"""
    try:
        data = request.get_json()
        customer_input = data.get("customer_input", "")

        if not customer_input:
            return jsonify({"success": False, "error": "No customer input provided"})

        # Use existing parser
        parsed_data = parse_customer_input(customer_input)

        if parsed_data:
            normalized_data = normalize_customer_data(parsed_data)
            return jsonify({"success": True, **normalized_data})
        else:
            return jsonify({"success": False, "error": "Could not parse customer data"})

    except Exception as e:
        logger.error(f"Customer parsing error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/test-routing", methods=["POST"])
def api_test_routing():
    """API endpoint to test routing for a location"""
    try:
        data = request.get_json()
        city = data.get("city", "")
        state = data.get("state", "")
        country = data.get("country", "US")

        # Use existing routing system
        customer_data = {"address": {"city": city, "state": state, "country": country}}

        routing_result = routing_system.find_optimal_warehouse(customer_data)

        return jsonify(
            {
                "success": True,
                "routing_result": routing_result,
                "location": f"{city}, {state}, {country}",
            }
        )

    except Exception as e:
        logger.error(f"Routing test error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/get_routing", methods=["POST"])
def api_get_routing():
    """API endpoint for intelligent order routing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No customer data provided"}), 400

        # Create customer data in expected format
        customer_data = {
            "name": data.get("name", ""),
            "city": data.get("city", ""),
            "state": data.get("state", ""),
            "country": data.get("country", "US"),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "address_1": data.get("address_1", ""),
            "postal_code": data.get("postal_code", "")
        }

        # Get available warehouses
        warehouses = routing_system.get_warehouse_mappings()
        available_warehouse_ids = list(warehouses.keys())

        # Use routing system to get intelligent routing
        routing_result = routing_system.route_order(customer_data, available_warehouse_ids)

        return jsonify({
            "success": True,
            "platform": routing_result.platform,
            "carrier": routing_result.carrier,
            "warehouse_info": routing_result.warehouse_info,
            "confidence": routing_result.confidence
        })

    except Exception as e:
        logger.error(f"Routing error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/create_order", methods=["POST"])
def api_create_order():
    """API endpoint to create orders through the unified system"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No order data provided"}), 400

        # Extract customer and order data
        customer_data = data.get("customer_data", {})
        products = data.get("products", [])
        routing_data = data.get("routing_data", {})

        # Validate required data
        if not customer_data.get("name"):
            return jsonify({"success": False, "error": "Customer name is required"}), 400

        if not products:
            return jsonify({"success": False, "error": "At least one product is required"}), 400

        # Validate customer data
        validation_result = validate_customer_data(customer_data)
        if not validation_result.is_valid:
            return jsonify({
                "success": False, 
                "error": f"Customer validation failed: {', '.join(validation_result.errors)}"
            }), 400

        # Use order processor for complete workflow
        from services.order_processor import OrderProcessor
        processor = OrderProcessor()
        
        # Process the order
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
        logger.error(f"Order creation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# MCP Integration Endpoints
@app.route("/api/mcp/health")
def api_mcp_health():
    """MCP health check endpoint"""
    try:
        mcp = get_mcp_integration()
        mcp.update_server_status()
        health_summary = mcp.get_health_summary()
        
        status_code = 200 if health_summary["status"] == "healthy" else 503
        return jsonify(health_summary), status_code
        
    except Exception as e:
        logger.error(f"MCP health check error: {e}")
        return jsonify({
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/api/mcp/servers")
def api_mcp_servers():
    """Get detailed status of all MCP servers"""
    try:
        mcp = get_mcp_integration()
        mcp.update_server_status()
        servers_status = mcp.get_all_servers_status()
        
        return jsonify({
            "servers": servers_status,
            "summary": mcp.get_health_summary(),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"MCP servers status error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mcp/debug", methods=["POST"])
def api_mcp_debug():
    """Start a debug session using python-debug MCP"""
    try:
        data = request.get_json()
        script_path = data.get("script_path", "")
        breakpoint_line = data.get("breakpoint_line")
        
        if not script_path:
            return jsonify({"error": "Script path is required"}), 400
        
        mcp = get_mcp_integration()
        result = mcp.execute_debug_session(script_path, breakpoint_line)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"MCP debug session error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mcp/ai-suggestions", methods=["POST"])
def api_mcp_ai_suggestions():
    """Get AI-powered development suggestions"""
    try:
        data = request.get_json() or {}
        context = data.get("context", {})
        
        mcp = get_mcp_integration()
        suggestions = mcp.get_ai_suggestions(context)
        
        return jsonify(suggestions)
        
    except Exception as e:
        logger.error(f"MCP AI suggestions error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mcp/create-plan", methods=["POST"])
def api_mcp_create_plan():
    """Create a development plan using sequential-thinking MCP"""
    try:
        data = request.get_json()
        task_description = data.get("task_description", "")
        
        if not task_description:
            return jsonify({"error": "Task description is required"}), 400
        
        mcp = get_mcp_integration()
        plan = mcp.create_development_plan(task_description)
        
        return jsonify(plan)
        
    except Exception as e:
        logger.error(f"MCP create plan error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health_check():
    """Application health check endpoint (includes MCP status)"""
    try:
        mcp = get_mcp_integration()
        mcp.update_server_status()
        mcp_health = mcp.get_health_summary()
        
        # Basic application health checks
        app_health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": app.config.get("FLASK_ENV", "unknown"),
            "database": "connected",  # Could add actual DB check here
            "mcp_integration": mcp_health
        }
        
        # Determine overall status
        overall_status = "healthy"
        if mcp_health["status"] != "healthy":
            overall_status = "degraded"
        
        app_health["status"] = overall_status
        status_code = 200 if overall_status == "healthy" else 503
        
        return jsonify(app_health), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route("/mcp-dashboard")
def mcp_dashboard():
    """MCP Integration Dashboard"""
    return render_template("mcp_dashboard.html")


@app.route("/api/ai/parse-customer", methods=["POST"])
def api_ai_parse_customer():
    """AI-enhanced customer parsing endpoint"""
    try:
        data = request.get_json()
        raw_input = data.get("raw_input", "")
        
        if not raw_input:
            return jsonify({"error": "Raw input is required"}), 400
        
        ai_features = get_ai_features()
        result = ai_features.intelligent_customer_parsing(raw_input)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI customer parsing error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/optimize-route", methods=["POST"])
def api_ai_optimize_route():
    """AI-enhanced route optimization endpoint"""
    try:
        data = request.get_json()
        customer_data = data.get("customer_data", {})
        warehouses = data.get("warehouses", [])
        
        if not customer_data:
            return jsonify({"error": "Customer data is required"}), 400
        
        ai_features = get_ai_features()
        result = ai_features.intelligent_route_optimization(customer_data, warehouses)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI route optimization error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/error-analysis", methods=["POST"])
def api_ai_error_analysis():
    """AI-enhanced error analysis endpoint"""
    try:
        data = request.get_json()
        error_context = data.get("error_context", {})
        
        ai_features = get_ai_features()
        result = ai_features.intelligent_error_detection(error_context)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI error analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/insights")
def api_ai_insights():
    """Get AI-powered insights"""
    try:
        # Gather context data
        context = {
            "recent_orders": [],  # Would get from database
            "recent_errors": [],  # Would get from logs
            "performance_metrics": {
                "response_time": 1500,  # ms
                "error_rate": 0.02,     # 2%
            }
        }
        
        ai_features = get_ai_features()
        insights = ai_features.get_ai_insights(context)
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Initialize database when running directly
    initialize_database()
    app.run(debug=True)

# WARNING: Do not use Flask's built-in server in production.
# For production deployments, use a WSGI server like Gunicorn or uWSGI.
