"""
Advanced Flask App Factory - MCP Enhanced
Created with Sequential-Thinking MCP for intelligent architecture
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import our new security middleware
from src.middleware.security import setup_security

# Import existing components
from models import init_db
from config.logging_config import setup_logging


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure Flask application using factory pattern
    Enhanced with MCP Sequential-Thinking for optimal architecture
    """
    
    # Load environment variables first
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Determine configuration
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Configure app based on environment
    configure_app(app, config_name)
    
    # Setup security (this replaces the old insecure patterns)
    security = setup_security(app)
    
    # Setup logging
    logger = setup_logging(app)
    
    # Setup CORS if needed
    if app.config.get('CORS_ENABLED', False):
        CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
    
    # Initialize database
    init_db(app)
    
    # Register blueprints (modular routes)
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup health checks
    setup_health_checks(app)
    
    return app


def configure_app(app: Flask, config_name: str):
    """Configure app based on environment"""
    
    # Base configuration
    app.config.update({
        'SECRET_KEY': None,  # Will be set by security middleware
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True,
    })
    
    if config_name == 'production':
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'SQLALCHEMY_DATABASE_URI': os.environ.get(
                'DATABASE_URL',
                'postgresql://username:password@localhost:5432/shipping_gui'
            ),
            'CORS_ENABLED': True,
            'CORS_ORIGINS': os.environ.get('CORS_ORIGINS', '').split(','),
            'SSL_ENABLED': True,
            'WTF_CSRF_ENABLED': True,
        })
    elif config_name == 'testing':
        app.config.update({
            'DEBUG': False,
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
        })
    else:  # development
        app.config.update({
            'DEBUG': True,
            'TESTING': False,
            'SQLALCHEMY_DATABASE_URI': os.environ.get(
                'DATABASE_URL',
                'sqlite:///instance/shipping_automation.db'
            ),
            'WTF_CSRF_ENABLED': False,  # Easier for development
        })
    
    # Set additional config from environment
    app.config['HF_TOKEN'] = os.environ.get('HF_TOKEN')
    app.config['VEEQO_API_KEY'] = os.environ.get('VEEQO_API_KEY')
    app.config['EASYSHIP_API_KEY'] = os.environ.get('EASYSHIP_API_KEY')


def register_blueprints(app: Flask):
    """Register all blueprint modules"""
    
    # Import blueprints (avoiding circular imports)
    from src.routes.orders import orders_bp
    from src.routes.dashboard import dashboard_bp
    from src.routes.api import api_bp
    from src.routes.health import health_bp
    
    # Register with appropriate URL prefixes
    app.register_blueprint(orders_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(health_bp)
    
    # Keep existing intelligent orders blueprint
    from blueprints.intelligent_orders import intelligent_orders_bp
    app.register_blueprint(intelligent_orders_bp, url_prefix="/intelligent-orders")


def register_error_handlers(app: Flask):
    """Register comprehensive error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server',
            'code': 400
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'code': 401
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'code': 403
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'code': 404
        }, 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'code': 429
        }, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'code': 500
        }, 500


def setup_health_checks(app: Flask):
    """Setup basic health check endpoints"""
    
    @app.route('/health')
    def health_check():
        """Basic health check"""
        return {
            'status': 'healthy',
            'service': 'shipping-gui',
            'version': '2.0.0'
        }
    
    @app.route('/ready')
    def readiness_check():
        """Kubernetes readiness probe"""
        # Add actual readiness checks here
        return {
            'status': 'ready',
            'checks': {
                'database': 'ok',
                'redis': 'ok',
                'external_apis': 'ok'
            }
        }


# Development helpers
def create_dev_app():
    """Create app for development"""
    return create_app('development')


def create_test_app():
    """Create app for testing"""
    return create_app('testing')


def create_prod_app():
    """Create app for production"""
    return create_app('production')