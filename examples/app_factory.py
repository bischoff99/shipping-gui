"""
Example Application Factory Pattern Implementation
This demonstrates how to restructure the monolithic app.py into a modular Flask application
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
cors = CORS()

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Validate required configuration
    validate_config(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {"origins": app.config.get('CORS_ORIGINS', ['*'])}
    })
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize background services
    initialize_services(app)
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    
    # API v1 blueprints
    from app.api.v1.orders import orders_bp
    from app.api.v1.products import products_bp
    from app.api.v1.inventory import inventory_bp
    from app.api.v1.sync import sync_bp
    
    # Web interface blueprints
    from app.web.dashboard import dashboard_bp
    from app.web.orders import web_orders_bp
    
    # Register API blueprints
    app.register_blueprint(orders_bp, url_prefix='/api/v1/orders')
    app.register_blueprint(products_bp, url_prefix='/api/v1/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/v1/inventory')
    app.register_blueprint(sync_bp, url_prefix='/api/v1/sync')
    
    # Register web blueprints
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(web_orders_bp, url_prefix='/orders')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}

def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {'error': 'Rate limit exceeded', 'retry_after': str(error.retry_after)}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {str(error)}')
        return {'error': 'Internal server error'}, 500

def setup_logging(app):
    """Setup application logging"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            'logs/shipping_automation.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Shipping Automation startup')

def validate_config(app):
    """Validate required configuration values"""
    required_config = [
        'SECRET_KEY',
        'VEEQO_API_KEY',
        'EASYSHIP_API_KEY'
    ]
    
    missing_config = []
    for config_key in required_config:
        if not app.config.get(config_key):
            missing_config.append(config_key)
    
    if missing_config:
        raise ValueError(f"Missing required configuration: {', '.join(missing_config)}")

def initialize_services(app):
    """Initialize background services and monitoring"""
    with app.app_context():
        # Initialize database tables
        db.create_all()
        
        # Start background services if not in testing mode
        if not app.testing:
            from app.services.inventory_monitor import InventoryMonitorService
            from app.services.product_sync import ProductSyncService
            
            # Start inventory monitoring
            inventory_monitor = InventoryMonitorService()
            inventory_monitor.start_monitoring()
            
            # Start product sync if auto-sync is enabled
            if app.config.get('AUTO_SYNC_ENABLED', False):
                product_sync = ProductSyncService()
                product_sync.start_auto_sync()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
