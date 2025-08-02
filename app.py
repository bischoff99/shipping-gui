"""
Unified Order & Warehouse Management System Flask App

This module provides the main Flask application for order creation, routing,
warehouse matching, and API sync between Veeqo and Easyship.
"""

import os
import json
from datetime import datetime
import tempfile
import shutil

from flask import Flask, render_template, request, flash, jsonify
from dotenv import load_dotenv

from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI
from routing import OrderRoutingSystem
from validation import validate_order_data
from utils import parse_customer_input, normalize_customer_data
from fedex_orders import FedExOrderProcessor
from veeqo_orders import VeeqoOrderProcessor
from advanced_product_sync import AdvancedProductSync
from inventory_monitor import RealTimeInventoryMonitor

# Load environment variables from .env file
load_dotenv()

# Template constants
CREATE_ORDER_TEMPLATE = "create_order.html"
DASHBOARD_TEMPLATE = "dashboard.html"
ENHANCED_DASHBOARD_TEMPLATE = "enhanced_dashboard.html"
FEDEX_ORDERS_TEMPLATE = "fedex_orders.html"
VEEQO_ORDERS_TEMPLATE = "veeqo_orders.html"
PRODUCT_SYNC_DASHBOARD_TEMPLATE = "product_sync_dashboard.html"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "unified_order_system_2025")

# Initialize API clients and routing system
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()
fedex_processor = FedExOrderProcessor()
veeqo_processor = VeeqoOrderProcessor()

# Initialize advanced product sync system
product_sync = AdvancedProductSync(veeqo_api, easyship_api)
def create_order():
    """Order creation page"""
    def _render_create_order(errors=None, warnings=None):
        if errors:
            for error in errors:
                flash(error, "error")
        if warnings:
            for warning in warnings:
                flash(warning, "warning")
        return render_template(
            CREATE_ORDER_TEMPLATE, carriers=routing_system.get_carrier_options()
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
            return _render_create_order(errors=validation_result.errors)

        if validation_result.warnings:
            for warning in validation_result.warnings:
                flash(warning, "warning")

        order_result = create_platform_order(
            routing_decision, customer_data, products
        )

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
            return _render_create_order()
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
        warehouse = (
            veeqo_api.get_warehouse_by_state("Nevada")
            or veeqo_api.get_warehouse_by_state("California")
        )
        if warehouse:
            return veeqo_api.create_order(
                customer_data,
                products,
                warehouse.get("id"),
                routing_decision.carrier,
            )
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
        data = request.get_json()
        customer_input = data.get("input", "")
        parsed = parse_customer_input(customer_input)
        if parsed:
            return jsonify({"status": "success", "data": parsed})
        else:
            return jsonify({"status": "error", "message": "Could not parse input"}), 400
    except Exception as e:
        return render_template(DASHBOARD_TEMPLATE, stats=stats)


        return render_template(DASHBOARD_TEMPLATE, stats={})
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
        
        return render_template("dashboard.html", stats=stats)
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Dashboard error: {str(e)}", "error")
        return render_template("dashboard.html", stats={})
    except Exception as e:
        flash(f"Dashboard error: {str(e)}", "error")
        return render_template("dashboard.html", stats={})


@app.route("/enhanced_dashboard")
def enhanced_dashboard():
    """Enhanced system dashboard with advanced features"""
    try:
        veeqo_warehouses = veeqo_api.get_warehouses()
        easyship_addresses = easyship_api.get_addresses()

        stats = {
            "veeqo_warehouses": len(veeqo_warehouses),
            "easyship_addresses": len(easyship_addresses),
            "total_locations": len(veeqo_warehouses) + len(easyship_addresses),
            "routing_rules": len(routing_system.carrier_platform_mapping),
            # Placeholders for future enhancements
            "orders_today": 0,
            "revenue_today": "0",
            "avg_processing_time": "0",
        }

        return render_template("enhanced_dashboard.html", stats=stats)
    except (KeyError, ValueError, RuntimeError) as e:
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
        return render_template("enhanced_dashboard.html", stats=default_stats)
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
        return render_template("enhanced_dashboard.html", stats=default_stats)


@app.route("/fedex_orders")
def fedex_orders():
    """FedEx orders page"""
    try:
        customers = fedex_processor.get_fedex_customers()
        summary = fedex_processor.get_fedex_customer_summary()

        return render_template(
            "fedex_orders.html", customers=customers, summary=summary
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"FedEx orders error: {str(e)}", "error")
        return render_template("fedex_orders.html", customers=[], summary={})
    except Exception as e:
        flash(f"FedEx orders error: {str(e)}", "error")
        return render_template("fedex_orders.html", customers=[], summary={})


@app.route("/process_fedex_orders", methods=["POST"])
def process_fedex_orders():
    """Process all FedEx orders"""
    try:
        results = fedex_processor.process_all_fedex_orders()

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        flash(f"Processed {successful}/{total} FedEx orders successfully!", "success")
        
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

        flash(f"Failed to create FedEx order for {customer_name}", "error")
        return jsonify({"status": "error", "message": "Failed to create order"}), 500
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"FedEx order error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        flash(f"FedEx order error: {str(e)}", "error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/veeqo_orders")
def veeqo_orders():
    """Veeqo orders page"""
    try:
        customers = veeqo_processor.get_veeqo_customers()
        summary = veeqo_processor.get_veeqo_customer_summary()

        return render_template(
            "veeqo_orders.html", customers=customers, summary=summary
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Veeqo orders error: {str(e)}", "error")
        return render_template("veeqo_orders.html", customers=[], summary={})
    except Exception as e:
        flash(f"Veeqo orders error: {str(e)}", "error")
        return render_template("veeqo_orders.html", customers=[], summary={})


@app.route("/process_veeqo_orders", methods=["POST"])
def process_veeqo_orders():
    """Process all Veeqo orders"""
    try:
        results = veeqo_processor.process_all_veeqo_orders()

        successful = sum(1 for r in results if r["success"])
        total = len(results)

        flash(f"Processed {successful}/{total} Veeqo orders successfully!", "success")

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
        customer = veeqo_processor.get_customer_by_name(customer_name)
        result = veeqo_processor.create_veeqo_order(customer_name)
        if result:
            carrier = customer.get("carrier", "UPS") if customer else "UPS"
            flash(
                f'Veeqo {carrier} order created for {customer_name}!',
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
    except (KeyError, ValueError, RuntimeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/product_sync_dashboard")
def product_sync_dashboard():
    """Advanced Product Sync Dashboard"""
    try:
        sync_stats = product_sync.get_sync_stats()
        inventory_alerts = product_sync.get_inventory_alerts()
        performance = product_sync.get_product_performance()

        return render_template(
            "product_sync_dashboard.html",
            sync_stats=sync_stats,
            inventory_alerts=inventory_alerts,
            performance=performance,
        )
    except (KeyError, ValueError, RuntimeError) as e:
        flash(f"Product sync dashboard error: {str(e)}", "error")
        return render_template(
            "product_sync_dashboard.html",
            sync_stats={},
            inventory_alerts=[],
            performance={},
        )
    except Exception as e:
        flash(f"Product sync dashboard error: {str(e)}", "error")
        return render_template(
            "product_sync_dashboard.html",
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
            return jsonify({"status": "error", "message": "Alert not found"}), 404
    except (KeyError, ValueError, RuntimeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# WARNING: Do not use Flask's built-in server in production.
# For production deployments, use a WSGI server like Gunicorn or uWSGI.
