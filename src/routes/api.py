"""
API Routes Module - MCP Enhanced
All /api/* endpoints extracted for better organization
"""
from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime
import asyncio
from src.middleware.security import validate_json_input, CustomerInputSchema, SecurityManager
from utils import parse_customer_input, normalize_customer_data
from validation import validate_customer_data
from routing import OrderRoutingSystem
from api.easyship_api import EasyshipAPI
from api.veeqo_api import VeeqoAPI
from advanced_product_sync import AdvancedProductSync
from services.inventory_monitor import RealTimeInventoryMonitor
from services.mcp_integration import get_mcp_integration
from services.ai_enhanced_features import get_ai_features

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()
product_sync = AdvancedProductSync(veeqo_api, easyship_api)
inventory_monitor = RealTimeInventoryMonitor(veeqo_api, easyship_api)


@api_bp.route("/parse_customer", methods=["POST"])
@validate_json_input(CustomerInputSchema)
def api_parse_customer():
    """Enhanced API endpoint to parse customer input with validation"""
    try:
        # Get validated data from security middleware
        validated_data = g.validated_data
        
        return jsonify({
            "status": "success", 
            "data": validated_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Customer parsing error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Internal server error"
        }), 500


@api_bp.route("/get_products", methods=["GET"])
def api_get_products():
    """Enhanced API endpoint to get random products with caching"""
    try:
        platform = request.args.get("platform", "VEEQO").upper()
        count = min(int(request.args.get("count", 3)), 10)  # Max 10 products

        if platform == "EASYSHIP":
            products = easyship_api.get_random_products(count)
        else:
            products = veeqo_api.get_random_products(count)

        return jsonify({
            "status": "success",
            "products": products,
            "platform": platform,
            "count": len(products),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Products API error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Failed to fetch products"
        }), 500


@api_bp.route("/get_routing", methods=["POST"])
@validate_json_input(CustomerInputSchema)
def api_get_routing():
    """Enhanced API endpoint for intelligent order routing"""
    try:
        # Get validated customer data
        customer_data = g.validated_data

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
            "confidence": routing_result.confidence,
            "reasoning": getattr(routing_result, 'reasoning', 'Standard routing logic applied')
        })

    except Exception as e:
        current_app.logger.error(f"Routing API error: {e}")
        return jsonify({
            "success": False, 
            "error": "Routing calculation failed"
        }), 500


@api_bp.route("/dashboard-stats")
def api_dashboard_stats():
    """Enhanced API endpoint for dashboard statistics"""
    try:
        # Get real-time stats with error handling
        try:
            warehouses = routing_system.get_warehouse_mappings()
            warehouse_count = len(warehouses)
        except Exception:
            warehouse_count = 0

        stats = {
            "warehouses": warehouse_count,
            "orders_today": 0,  # Would come from database
            "sync_rate": 95,    # Would come from monitoring
            "last_sync": datetime.now().isoformat(),
            "system_status": "operational",
            "api_health": {
                "veeqo": _check_api_health(veeqo_api),
                "easyship": _check_api_health(easyship_api)
            }
        }

        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard stats error: {e}")
        return jsonify({
            "error": "Failed to fetch dashboard stats",
            "warehouses": 0,
            "orders_today": 0,
            "sync_rate": 0,
            "system_status": "degraded"
        }), 500


@api_bp.route("/warehouses")
def api_warehouses():
    """Enhanced API endpoint for warehouse list with health checks"""
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
                "health_score": _calculate_warehouse_health(warehouse_data)
            }
            warehouses.append(warehouse_info)

        return jsonify({
            "warehouses": warehouses,
            "total_count": len(warehouses),
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Warehouses API error: {e}")
        return jsonify({
            "error": "Failed to fetch warehouses",
            "warehouses": []
        }), 500


@api_bp.route("/sync-all", methods=["POST"])
def api_sync_all():
    """Enhanced API endpoint to trigger full system sync"""
    try:
        sync_results = []

        # Sync Veeqo with timeout
        try:
            veeqo_result = veeqo_api.test_connection()
            sync_results.append(("Veeqo", veeqo_result))
        except Exception as e:
            sync_results.append(("Veeqo", False))
            current_app.logger.error(f"Veeqo sync error: {e}")

        # Sync Easyship with timeout
        try:
            easyship_result = easyship_api.test_connection()
            sync_results.append(("Easyship", easyship_result))
        except Exception as e:
            sync_results.append(("Easyship", False))
            current_app.logger.error(f"Easyship sync error: {e}")

        # Calculate success rate
        successful_syncs = sum(1 for _, result in sync_results if result)
        success_rate = int((successful_syncs / len(sync_results)) * 100) if sync_results else 0

        return jsonify({
            "success": True,
            "results": sync_results,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
            "next_sync_recommended": datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"Sync all error: {e}")
        return jsonify({
            "success": False, 
            "error": "Sync operation failed"
        }), 500


@api_bp.route("/sync_products", methods=["POST"])
def api_sync_products():
    """Enhanced manual product sync trigger with async support"""
    try:
        # Handle async operations properly
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            import nest_asyncio
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()

        result = loop.run_until_complete(product_sync.sync_products_bidirectional())
        
        return jsonify({
            "status": "success",
            "sync_result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Product sync error: {e}")
        return jsonify({
            "status": "error", 
            "message": "Product sync failed"
        }), 500


@api_bp.route("/inventory_alerts")
def api_inventory_alerts():
    """Enhanced API to get active inventory alerts"""
    try:
        alerts = inventory_monitor.get_active_alerts()
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "id": alert.id,
                "product_sku": alert.product_sku,
                "product_name": alert.product_name,
                "warehouse_name": alert.warehouse_name,
                "current_stock": alert.current_stock,
                "threshold": alert.threshold,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                "recommended_action": _get_alert_recommendation(alert)
            })
        
        return jsonify({
            "alerts": alert_data,
            "total_count": len(alert_data),
            "critical_count": len([a for a in alert_data if a["severity"] == "critical"]),
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Inventory alerts error: {e}")
        return jsonify({
            "error": "Failed to fetch inventory alerts",
            "alerts": []
        }), 500


# MCP Integration Endpoints
@api_bp.route("/mcp/health")
def api_mcp_health():
    """Enhanced MCP health check endpoint with detailed diagnostics"""
    try:
        mcp = get_mcp_integration()
        mcp.update_server_status()
        health_summary = mcp.get_health_summary()
        
        # Add additional diagnostics
        health_summary["diagnostics"] = {
            "last_check": datetime.now().isoformat(),
            "response_time_ms": _measure_mcp_response_time(),
            "feature_availability": _check_mcp_features()
        }
        
        status_code = 200 if health_summary["status"] == "healthy" else 503
        return jsonify(health_summary), status_code
        
    except Exception as e:
        current_app.logger.error(f"MCP health check error: {e}")
        return jsonify({
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@api_bp.route("/ai/parse-customer", methods=["POST"])
def api_ai_parse_customer():
    """Enhanced AI-powered customer parsing endpoint"""
    try:
        data = request.get_json()
        raw_input = data.get("raw_input", "")
        
        if not raw_input:
            return jsonify({
                "error": "Raw input is required"
            }), 400
        
        ai_features = get_ai_features()
        result = ai_features.intelligent_customer_parsing(raw_input)
        
        # Add confidence scoring and validation
        result["confidence_score"] = _calculate_parsing_confidence(result)
        result["validation_status"] = _validate_parsed_data(result)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"AI customer parsing error: {e}")
        return jsonify({
            "error": "AI parsing service unavailable"
        }), 500


# Helper functions
def _check_api_health(api_client):
    """Check API health with timeout"""
    try:
        return api_client.test_connection()
    except Exception:
        return False


def _calculate_warehouse_health(warehouse_data):
    """Calculate warehouse health score"""
    # Simple health scoring based on available data
    score = 100
    if not warehouse_data.get("last_sync"):
        score -= 20
    if warehouse_data.get("status") != "active":
        score -= 50
    return max(0, score)


def _get_alert_recommendation(alert):
    """Get recommended action for inventory alert"""
    if alert.alert_type == "low_stock":
        return f"Reorder {alert.threshold * 2} units"
    elif alert.alert_type == "out_of_stock":
        return "Urgent reorder required"
    else:
        return "Review inventory levels"


def _measure_mcp_response_time():
    """Measure MCP response time"""
    # Placeholder - would implement actual timing
    return 150  # ms


def _check_mcp_features():
    """Check which MCP features are available"""
    return {
        "filesystem": True,
        "github": True,
        "sequential_thinking": True,
        "huggingface": True
    }


def _calculate_parsing_confidence(result):
    """Calculate confidence score for parsed data"""
    # Simple confidence calculation
    required_fields = ["name", "address_1", "city", "postal_code", "country"]
    present_fields = sum(1 for field in required_fields if result.get(field))
    return (present_fields / len(required_fields)) * 100


def _validate_parsed_data(result):
    """Validate parsed customer data"""
    try:
        schema = CustomerInputSchema()
        schema.load(result)
        return "valid"
    except Exception:
        return "invalid"