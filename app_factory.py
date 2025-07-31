"""
Production Flask Application Factory
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config.production import get_config
from utils.logging_config import setup_logging
from middleware.security import init_security
from models import init_db
from blueprints.intelligent_orders import intelligent_orders_bp


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application using application factory pattern
    
    Args:
        config_name: Configuration environment ('development', 'staging', 'production')
        
    Returns:
        Configured Flask application
    """
    # Create Flask instance
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Validate required environment variables in production
    if config_name == 'production':
        try:
            config_class.validate_required_env_vars()
        except EnvironmentError as e:
            app.logger.error(f"Configuration error: {e}")
            raise
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add health check endpoint
    register_health_check(app)
    
    return app


def init_extensions(app: Flask):
    """Initialize Flask extensions"""
    
    # Initialize CORS
    CORS(app, origins=os.environ.get('CORS_ORIGINS', '*').split(','))
    
    # Initialize database
    init_db(app)
    
    # Initialize logging
    setup_logging(app)
    
    # Initialize security middleware
    init_security(app)
    
    app.logger.info(f"Initialized Flask app in {app.config.get('FLASK_ENV', 'unknown')} mode")


def register_blueprints(app: Flask):
    """Register application blueprints"""
    
    # Register intelligent orders blueprint
    app.register_blueprint(intelligent_orders_bp, url_prefix='/intelligent-orders')
    
    # Import and register main routes
    with app.app_context():
        from app import (
            create_order, sync_data, api_parse_customer, api_get_products,
            dashboard, enhanced_dashboard, fedex_orders, process_fedex_orders,
            create_fedex_order_route, veeqo_orders, process_veeqo_orders,
            create_veeqo_order_route, api_veeqo_purchase_orders,
            product_sync_dashboard, api_sync_products, api_product_stats,
            api_start_auto_sync, api_stop_auto_sync, api_inventory_alerts,
            api_inventory_summary, api_reorder_suggestions, api_resolve_alert,
            unified_dashboard, api_dashboard_stats, api_warehouses,
            api_sync_all, api_parse_customer_data, api_test_routing,
            api_get_routing, api_create_order
        )


def register_error_handlers(app: Flask):
    """Register global error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500


def register_health_check(app: Flask):
    """Register health check and monitoring endpoints"""
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers and monitoring"""
        try:
            # Check database connection
            from models import db
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            app.logger.error(f"Database health check failed: {e}")
            db_status = 'unhealthy'
        
        # Check Redis connection (if configured)
        redis_status = 'not_configured'
        if app.config.get('REDIS_URL'):
            try:
                import redis
                r = redis.from_url(app.config['REDIS_URL'])
                r.ping()
                redis_status = 'healthy'
            except Exception as e:
                app.logger.error(f"Redis health check failed: {e}")
                redis_status = 'unhealthy'
        
        # Overall health status
        is_healthy = db_status == 'healthy' and (redis_status in ['healthy', 'not_configured'])
        
        health_data = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': '2025-07-30T14:30:00Z',
            'version': '1.0.0',
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'checks': {
                'database': db_status,
                'redis': redis_status
            }
        }
        
        status_code = 200 if is_healthy else 503
        return jsonify(health_data), status_code
    
    @app.route('/health/ready')
    def readiness_check():
        """Readiness check for Kubernetes"""
        # More comprehensive readiness check
        checks = {}
        
        # Database readiness
        try:
            from models import db, Product
            Product.query.first()  # Try to query a table
            checks['database'] = True
        except Exception:
            checks['database'] = False
        
        # External API readiness (optional)
        checks['external_apis'] = True  # Would check Veeqo/Easyship APIs
        
        all_ready = all(checks.values())
        
        return jsonify({
            'ready': all_ready,
            'checks': checks
        }), 200 if all_ready else 503
    
    @app.route('/health/live')
    def liveness_check():
        """Liveness check for Kubernetes"""
        # Simple liveness check - just verify app is running
        return jsonify({
            'alive': True,
            'timestamp': '2025-07-30T14:30:00Z'
        }), 200
    
    @app.route('/metrics')
    def metrics():
        """Basic metrics endpoint (Prometheus format would be better)"""
        if not app.config.get('METRICS_ENABLED', True):
            return jsonify({'error': 'Metrics disabled'}), 404
        
        # Basic application metrics
        metrics_data = {
            'app_info': {
                'version': '1.0.0',
                'environment': app.config.get('FLASK_ENV', 'unknown'),
                'uptime_seconds': 0  # Would track actual uptime
            },
            'http_requests_total': 0,  # Would track from middleware
            'database_connections': 0,  # Would get from connection pool
            'api_key_count': 0  # Would get from security manager
        }
        
        return jsonify(metrics_data)


if __name__ == '__main__':
    # For development only
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)