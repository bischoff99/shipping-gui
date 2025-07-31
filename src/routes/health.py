"""
Health & System Routes Module - MCP Enhanced
Health checks, monitoring, and system status endpoints
"""
from flask import Blueprint, jsonify, current_app
from datetime import datetime
import time
import psutil
from services.mcp_integration import get_mcp_integration
from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI

# Create blueprint
health_bp = Blueprint('health', __name__)

# Initialize services
veeqo_api = VeeqoAPI()
easyship_api = EasyshipAPI()


@health_bp.route('/health')
def health_check():
    """Comprehensive application health check with MCP integration"""
    try:
        start_time = time.time()
        
        # Basic application health
        app_health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-mcp",
            "environment": current_app.config.get("FLASK_ENV", "unknown"),
            "uptime": _get_uptime(),
        }
        
        # Database health check
        try:
            from models import db
            db.engine.execute("SELECT 1")
            app_health["database"] = "connected"
        except Exception as e:
            app_health["database"] = f"error: {str(e)}"
            app_health["status"] = "degraded"
        
        # External API health checks
        api_health = {}
        try:
            api_health["veeqo"] = "healthy" if veeqo_api.test_connection() else "unhealthy"
        except Exception:
            api_health["veeqo"] = "unhealthy"
            
        try:
            api_health["easyship"] = "healthy" if easyship_api.test_connection() else "unhealthy"
        except Exception:
            api_health["easyship"] = "unhealthy"
        
        app_health["external_apis"] = api_health
        
        # MCP integration health
        try:
            mcp = get_mcp_integration()
            mcp.update_server_status()
            mcp_health = mcp.get_health_summary()
            app_health["mcp_integration"] = mcp_health
        except Exception as e:
            app_health["mcp_integration"] = {"status": "error", "error": str(e)}
        
        # System resources
        app_health["system_resources"] = _get_system_resources()
        
        # Calculate response time
        app_health["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        # Determine overall status
        overall_status = "healthy"
        if app_health["database"] != "connected":
            overall_status = "degraded"
        if any(status == "unhealthy" for status in api_health.values()):
            overall_status = "degraded"
        if app_health["mcp_integration"].get("status") not in ["healthy", "degraded"]:
            overall_status = "degraded"
        
        app_health["status"] = overall_status
        status_code = 200 if overall_status in ["healthy", "degraded"] else 503
        
        return jsonify(app_health), status_code
        
    except Exception as e:
        current_app.logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-mcp"
        }), 500


@health_bp.route('/ready')
def readiness_check():
    """Kubernetes readiness probe with comprehensive checks"""
    try:
        checks = {}
        overall_ready = True
        
        # Database readiness
        try:
            from models import db
            db.engine.execute("SELECT 1")
            checks["database"] = "ready"
        except Exception as e:
            checks["database"] = f"not_ready: {str(e)}"
            overall_ready = False
        
        # Redis readiness (if configured)
        try:
            import redis
            import os
            redis_url = os.environ.get('REDIS_URL')
            if redis_url:
                r = redis.from_url(redis_url)
                r.ping()
                checks["redis"] = "ready"
            else:
                checks["redis"] = "not_configured"
        except Exception as e:
            checks["redis"] = f"not_ready: {str(e)}"
            # Redis is optional, don't fail readiness
        
        # External API readiness
        api_checks = {}
        try:
            api_checks["veeqo"] = "ready" if veeqo_api.test_connection() else "not_ready"
        except Exception:
            api_checks["veeqo"] = "not_ready"
            
        try:
            api_checks["easyship"] = "ready" if easyship_api.test_connection() else "not_ready"
        except Exception:
            api_checks["easyship"] = "not_ready"
        
        # At least one API should be ready
        if not any(status == "ready" for status in api_checks.values()):
            overall_ready = False
        
        checks["external_apis"] = api_checks
        
        # MCP services readiness
        try:
            mcp = get_mcp_integration()
            mcp_status = mcp.get_health_summary()
            checks["mcp"] = "ready" if mcp_status["status"] == "healthy" else "degraded"
        except Exception:
            checks["mcp"] = "not_ready"
            # MCP is optional for basic functionality
        
        status = "ready" if overall_ready else "not_ready"
        status_code = 200 if overall_ready else 503
        
        return jsonify({
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "checks": checks
        }), status_code
        
    except Exception as e:
        current_app.logger.error(f"Readiness check error: {e}")
        return jsonify({
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503


@health_bp.route('/live')
def liveness_check():
    """Kubernetes liveness probe - basic application responsiveness"""
    try:
        return jsonify({
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "pid": os.getpid() if hasattr(os, 'getpid') else None
        })
    except Exception as e:
        current_app.logger.error(f"Liveness check error: {e}")
        return jsonify({
            "status": "dead",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@health_bp.route('/metrics')
def metrics_endpoint():
    """Prometheus-compatible metrics endpoint"""
    try:
        metrics = []
        
        # Application metrics
        metrics.append('# HELP shipping_gui_uptime_seconds Application uptime in seconds')
        metrics.append('# TYPE shipping_gui_uptime_seconds gauge')
        metrics.append(f'shipping_gui_uptime_seconds {_get_uptime()}')
        
        # API health metrics
        for api_name, api_client in [("veeqo", veeqo_api), ("easyship", easyship_api)]:
            try:
                healthy = 1 if api_client.test_connection() else 0
            except Exception:
                healthy = 0
            
            metrics.append(f'# HELP shipping_gui_api_health API health status (1=healthy, 0=unhealthy)')
            metrics.append(f'# TYPE shipping_gui_api_health gauge')
            metrics.append(f'shipping_gui_api_health{{api="{api_name}"}} {healthy}')
        
        # System resource metrics
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            metrics.append(f'# HELP shipping_gui_cpu_usage_percent CPU usage percentage')
            metrics.append(f'# TYPE shipping_gui_cpu_usage_percent gauge')
            metrics.append(f'shipping_gui_cpu_usage_percent {cpu_percent}')
            
            metrics.append(f'# HELP shipping_gui_memory_usage_percent Memory usage percentage')
            metrics.append(f'# TYPE shipping_gui_memory_usage_percent gauge')
            metrics.append(f'shipping_gui_memory_usage_percent {memory.percent}')
        except Exception:
            pass  # psutil might not be available
        
        # MCP metrics
        try:
            mcp = get_mcp_integration()
            mcp_health = mcp.get_health_summary()
            mcp_healthy = 1 if mcp_health["status"] == "healthy" else 0
            
            metrics.append(f'# HELP shipping_gui_mcp_health MCP integration health (1=healthy, 0=unhealthy)')
            metrics.append(f'# TYPE shipping_gui_mcp_health gauge')
            metrics.append(f'shipping_gui_mcp_health {mcp_healthy}')
        except Exception:
            pass
        
        return '\n'.join(metrics), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        current_app.logger.error(f"Metrics endpoint error: {e}")
        return f"# Error generating metrics: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}


@health_bp.route('/debug/info')
def debug_info():
    """Debug information endpoint (development only)"""
    if current_app.config.get('FLASK_ENV') != 'development':
        return jsonify({"error": "Debug endpoint only available in development"}), 403
    
    try:
        import sys
        import platform
        
        debug_data = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "flask_config": {k: str(v) for k, v in current_app.config.items() if 'SECRET' not in k and 'KEY' not in k},
            "environment_vars": {k: v for k, v in os.environ.items() if 'SECRET' not in k and 'KEY' not in k and 'TOKEN' not in k},
            "system_resources": _get_system_resources(),
            "mcp_status": _get_mcp_debug_info()
        }
        
        return jsonify(debug_data)
        
    except Exception as e:
        return jsonify({"error": f"Debug info error: {str(e)}"}), 500


# Helper functions
def _get_uptime():
    """Get application uptime in seconds"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return time.time() - process.create_time()
    except Exception:
        return 0


def _get_system_resources():
    """Get system resource information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024 * 1024 * 1024)
        }
    except Exception:
        return {"error": "psutil not available"}


def _get_mcp_debug_info():
    """Get MCP debug information"""
    try:
        mcp = get_mcp_integration()
        return {
            "servers_status": mcp.get_all_servers_status(),
            "health_summary": mcp.get_health_summary(),
            "last_update": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}