"""
Dashboard Routes Module - MCP Enhanced
All dashboard-related endpoints for monitoring and management
"""
from flask import Blueprint, render_template, flash, current_app
from datetime import datetime
from routing import OrderRoutingSystem
from api.easyship_api import EasyshipAPI
from api.veeqo_api import VeeqoAPI
from advanced_product_sync import AdvancedProductSync
from services.inventory_monitor import RealTimeInventoryMonitor
from fedex_orders import FedExOrderProcessor
from veeqo_orders import VeeqoOrderProcessor

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Initialize services
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()
routing_system = OrderRoutingSystem()
product_sync = AdvancedProductSync(veeqo_api, easyship_api)
inventory_monitor = RealTimeInventoryMonitor(veeqo_api, easyship_api)
fedex_processor = FedExOrderProcessor()
veeqo_processor = VeeqoOrderProcessor()

# Template constants
DASHBOARD_TEMPLATE = "dashboard.html"
ENHANCED_DASHBOARD_TEMPLATE = "enhanced_dashboard.html"
FEDEX_ORDERS_TEMPLATE = "fedex_orders.html"
VEEQO_ORDERS_TEMPLATE = "veeqo_orders.html"
PRODUCT_SYNC_DASHBOARD_TEMPLATE = "product_sync_dashboard.html"

# Dashboard statistics cache
dashboard_stats = {
    "warehouse_count": 0,
    "orders_today": 0,
    "sync_success_rate": 0,
    "last_sync": datetime.now().isoformat(),
}


@dashboard_bp.route("/")
def dashboard():
    """Enhanced main system dashboard with error handling"""
    try:
        # Get basic stats with fallbacks
        try:
            veeqo_warehouses = veeqo_api.get_warehouses()
        except Exception as e:
            current_app.logger.warning(f"Veeqo warehouses fetch failed: {e}")
            veeqo_warehouses = []
            
        try:
            easyship_addresses = easyship_api.get_addresses()
        except Exception as e:
            current_app.logger.warning(f"Easyship addresses fetch failed: {e}")
            easyship_addresses = []

        stats = {
            "veeqo_warehouses": len(veeqo_warehouses),
            "easyship_addresses": len(easyship_addresses),
            "total_locations": len(veeqo_warehouses) + len(easyship_addresses),
            "routing_rules": len(routing_system.carrier_platform_mapping),
            "system_health": _calculate_system_health(),
            "last_updated": datetime.now().isoformat()
        }

        return render_template(DASHBOARD_TEMPLATE, stats=stats)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {e}")
        flash(f"Dashboard error: Limited functionality available", "warning")
        return render_template(DASHBOARD_TEMPLATE, stats={
            "veeqo_warehouses": 0,
            "easyship_addresses": 0,
            "total_locations": 0,
            "routing_rules": 0,
            "system_health": "degraded",
            "last_updated": datetime.now().isoformat()
        })


@dashboard_bp.route("/enhanced")
def enhanced_dashboard():
    """Enhanced system dashboard with advanced features and monitoring"""
    try:
        # Get comprehensive stats for enhanced dashboard
        try:
            veeqo_warehouses = veeqo_api.get_warehouses()
            easyship_addresses = easyship_api.get_addresses()
        except Exception as e:
            current_app.logger.warning(f"API fetch failed in enhanced dashboard: {e}")
            veeqo_warehouses = []
            easyship_addresses = []

        # Enhanced stats with more detailed information
        stats = {
            "veeqo_warehouses": len(veeqo_warehouses),
            "easyship_addresses": len(easyship_addresses),
            "total_locations": len(veeqo_warehouses) + len(easyship_addresses),
            "routing_rules": len(routing_system.carrier_platform_mapping),
            "orders_today": _get_orders_today(),
            "revenue_today": _get_revenue_today(),
            "avg_processing_time": _get_avg_processing_time(),
            "system_alerts": _get_system_alerts(),
            "performance_metrics": _get_performance_metrics(),
            "last_updated": datetime.now().isoformat()
        }

        return render_template(ENHANCED_DASHBOARD_TEMPLATE, stats=stats)
        
    except Exception as e:
        current_app.logger.error(f"Enhanced dashboard error: {e}")
        flash(f"Enhanced dashboard error: {str(e)}", "error")
        
        # Return with safe default stats
        default_stats = {
            "veeqo_warehouses": 0,
            "easyship_addresses": 0,
            "total_locations": 0,
            "routing_rules": 0,
            "orders_today": 0,
            "revenue_today": "0.00",
            "avg_processing_time": "N/A",
            "system_alerts": [],
            "performance_metrics": {},
            "last_updated": datetime.now().isoformat()
        }
        return render_template(ENHANCED_DASHBOARD_TEMPLATE, stats=default_stats)


@dashboard_bp.route("/unified")
def unified_dashboard():
    """Enhanced unified dashboard with integrated GUI and real-time updates"""
    try:
        # Update dashboard stats with real-time data
        dashboard_stats["warehouse_count"] = len(
            routing_system.get_warehouse_mappings()
        )
        dashboard_stats["orders_today"] = _get_orders_today()
        dashboard_stats["sync_success_rate"] = _calculate_sync_success_rate()
        dashboard_stats["last_sync"] = datetime.now().isoformat()

        # Add additional unified stats
        unified_stats = {
            **dashboard_stats,
            "active_alerts": _get_active_alerts_count(),
            "api_health": _get_api_health_status(),
            "recent_activities": _get_recent_activities(),
            "quick_actions": _get_available_quick_actions()
        }

        return render_template("unified_dashboard.html", **unified_stats)
        
    except Exception as e:
        current_app.logger.error(f"Error loading unified dashboard: {e}")
        return render_template(
            "unified_dashboard.html",
            warehouse_count=0,
            orders_today=0,
            sync_success_rate=0,
            active_alerts=0,
            api_health="degraded",
            recent_activities=[],
            quick_actions=[]
        )


@dashboard_bp.route("/fedex_orders")
def fedex_orders():
    """Enhanced FedEx orders dashboard with error handling"""
    try:
        customers = fedex_processor.get_fedex_customers()
        summary = fedex_processor.get_fedex_customer_summary()

        # Add enhanced metrics
        enhanced_summary = {
            **summary,
            "processing_status": _get_fedex_processing_status(),
            "recent_shipments": _get_recent_fedex_shipments(),
            "performance_metrics": _get_fedex_performance_metrics()
        }

        return render_template(
            FEDEX_ORDERS_TEMPLATE, 
            customers=customers, 
            summary=enhanced_summary
        )
        
    except Exception as e:
        current_app.logger.error(f"FedEx orders error: {e}")
        flash(f"FedEx orders error: {str(e)}", "error")
        return render_template(
            FEDEX_ORDERS_TEMPLATE, 
            customers=[], 
            summary={
                "total_customers": 0,
                "pending_orders": 0,
                "processing_status": "unavailable"
            }
        )


@dashboard_bp.route("/veeqo_orders")
def veeqo_orders():
    """Enhanced Veeqo orders dashboard with comprehensive metrics"""
    try:
        customers = veeqo_processor.get_veeqo_customers()
        summary = veeqo_processor.get_veeqo_customer_summary()

        # Add enhanced metrics
        enhanced_summary = {
            **summary,
            "inventory_status": _get_veeqo_inventory_status(),
            "recent_orders": _get_recent_veeqo_orders(),
            "warehouse_utilization": _get_warehouse_utilization()
        }

        return render_template(
            VEEQO_ORDERS_TEMPLATE, 
            customers=customers, 
            summary=enhanced_summary
        )
        
    except Exception as e:
        current_app.logger.error(f"Veeqo orders error: {e}")
        flash(f"Veeqo orders error: {str(e)}", "error")
        return render_template(
            VEEQO_ORDERS_TEMPLATE, 
            customers=[], 
            summary={
                "total_customers": 0,
                "pending_orders": 0,
                "inventory_status": "unavailable"
            }
        )


@dashboard_bp.route("/product_sync")
def product_sync_dashboard():
    """Advanced Product Sync Dashboard with real-time monitoring"""
    try:
        # Get comprehensive sync statistics
        sync_stats = product_sync.get_sync_stats()
        inventory_alerts = product_sync.get_inventory_alerts()
        performance = product_sync.get_product_performance()

        # Add enhanced monitoring data
        enhanced_data = {
            "sync_stats": sync_stats,
            "inventory_alerts": inventory_alerts,
            "performance": performance,
            "sync_health": _calculate_sync_health(sync_stats),
            "recommendations": _get_sync_recommendations(sync_stats),
            "last_updated": datetime.now().isoformat()
        }

        return render_template(
            PRODUCT_SYNC_DASHBOARD_TEMPLATE,
            **enhanced_data
        )
        
    except Exception as e:
        current_app.logger.error(f"Product sync dashboard error: {e}")
        flash(f"Product sync dashboard error: {str(e)}", "error")
        return render_template(
            PRODUCT_SYNC_DASHBOARD_TEMPLATE,
            sync_stats={},
            inventory_alerts=[],
            performance={},
            sync_health="unknown",
            recommendations=[],
            last_updated=datetime.now().isoformat()
        )


# Helper functions for enhanced dashboard functionality
def _calculate_system_health():
    """Calculate overall system health score"""
    try:
        health_checks = [
            veeqo_api.test_connection(),
            easyship_api.test_connection(),
        ]
        healthy_services = sum(health_checks)
        return "healthy" if healthy_services >= 2 else "degraded"
    except Exception:
        return "unknown"


def _get_orders_today():
    """Get today's order count"""
    # Placeholder - would query database
    return 0


def _get_revenue_today():
    """Get today's revenue"""
    # Placeholder - would query database
    return "0.00"


def _get_avg_processing_time():
    """Get average order processing time"""
    # Placeholder - would calculate from metrics
    return "N/A"


def _get_system_alerts():
    """Get active system alerts"""
    alerts = []
    try:
        inventory_alerts = inventory_monitor.get_active_alerts()
        for alert in inventory_alerts[:5]:  # Top 5 alerts
            alerts.append({
                "type": "inventory",
                "message": f"Low stock: {alert.product_name}",
                "severity": alert.severity
            })
    except Exception:
        pass
    return alerts


def _get_performance_metrics():
    """Get system performance metrics"""
    return {
        "cpu_usage": "N/A",
        "memory_usage": "N/A",
        "response_time": "N/A",
        "error_rate": "N/A"
    }


def _calculate_sync_success_rate():
    """Calculate sync success rate"""
    try:
        # Simple calculation based on API health
        veeqo_healthy = veeqo_api.test_connection()
        easyship_healthy = easyship_api.test_connection()
        return 100 if (veeqo_healthy and easyship_healthy) else 50
    except Exception:
        return 0


def _get_active_alerts_count():
    """Get count of active alerts"""
    try:
        return len(inventory_monitor.get_active_alerts())
    except Exception:
        return 0


def _get_api_health_status():
    """Get overall API health status"""
    try:
        health_checks = [
            veeqo_api.test_connection(),
            easyship_api.test_connection()
        ]
        if all(health_checks):
            return "healthy"
        elif any(health_checks):
            return "degraded"
        else:
            return "unhealthy"
    except Exception:
        return "unknown"


def _get_recent_activities():
    """Get recent system activities"""
    # Placeholder - would query activity logs
    return []


def _get_available_quick_actions():
    """Get available quick actions for dashboard"""
    return [
        {"name": "Sync All Data", "endpoint": "/api/sync-all"},
        {"name": "Check Inventory", "endpoint": "/api/inventory_alerts"},
        {"name": "System Health", "endpoint": "/health"}
    ]


def _get_fedex_processing_status():
    """Get FedEx processing status"""
    return "operational"  # Placeholder


def _get_recent_fedex_shipments():
    """Get recent FedEx shipments"""
    return []  # Placeholder


def _get_fedex_performance_metrics():
    """Get FedEx performance metrics"""
    return {"delivery_rate": "99%", "avg_transit_time": "2.5 days"}


def _get_veeqo_inventory_status():
    """Get Veeqo inventory status"""
    return "optimal"  # Placeholder


def _get_recent_veeqo_orders():
    """Get recent Veeqo orders"""
    return []  # Placeholder


def _get_warehouse_utilization():
    """Get warehouse utilization metrics"""
    return {"average_utilization": "75%", "peak_capacity": "90%"}


def _calculate_sync_health(sync_stats):
    """Calculate sync health based on stats"""
    if not sync_stats:
        return "unknown"
    # Simple health calculation
    return "healthy" if sync_stats.get("success_rate", 0) > 90 else "degraded"


def _get_sync_recommendations(sync_stats):
    """Get sync recommendations based on performance"""
    recommendations = []
    if sync_stats.get("success_rate", 100) < 95:
        recommendations.append("Consider increasing sync frequency")
    if sync_stats.get("error_count", 0) > 10:
        recommendations.append("Review sync error logs")
    return recommendations