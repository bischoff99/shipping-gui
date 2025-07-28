"""
Example Orders API Blueprint
Demonstrates how to refactor monolithic routes into organized, secure endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError
from functools import wraps
import logging
from datetime import datetime

# Create blueprint
orders_bp = Blueprint('orders', __name__)

# Schemas for request validation
class CustomerDataSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    phone = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)
    address_1 = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    address_2 = fields.Str(required=False, allow_none=True)
    city = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    state = fields.Str(required=False, allow_none=True)
    postal_code = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    country = fields.Str(required=True, validate=lambda x: x.upper() in ['US', 'GB', 'DE', 'PH', 'IE'])

class ProductSchema(Schema):
    id = fields.Str(required=False, allow_none=True)
    title = fields.Str(required=False, allow_none=True)
    price = fields.Float(required=False, allow_none=True, validate=lambda x: x > 0)
    weight = fields.Float(required=False, allow_none=True, validate=lambda x: x > 0)
    sku = fields.Str(required=False, allow_none=True)

class CreateOrderSchema(Schema):
    customer_data = fields.Nested(CustomerDataSchema, required=True)
    products = fields.List(fields.Nested(ProductSchema), required=True, validate=lambda x: len(x) > 0)
    carrier = fields.Str(required=False, validate=lambda x: x.upper() in ['FEDEX', 'UPS', 'DHL', 'USPS'])

# Middleware decorators
def require_api_key(f):
    """Require valid API key for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key (implement your validation logic)
        if not _validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_json(schema_class):
    """Validate JSON request data against schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not request.is_json:
                    return jsonify({'error': 'Content-Type must be application/json'}), 400
                
                schema = schema_class()
                validated_data = schema.load(request.json)
                request.validated_data = validated_data
                
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation failed',
                    'details': e.messages
                }), 400
            except Exception as e:
                current_app.logger.error(f'Validation error: {str(e)}')
                return jsonify({'error': 'Invalid request data'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_request(f):
    """Log API requests for monitoring"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.utcnow()
        
        # Log request
        current_app.logger.info(f'API Request: {request.method} {request.path} from {request.remote_addr}')
        
        try:
            response = f(*args, **kwargs)
            
            # Log successful response
            duration = (datetime.utcnow() - start_time).total_seconds()
            current_app.logger.info(f'API Response: {request.path} completed in {duration:.3f}s')
            
            return response
            
        except Exception as e:
            # Log error
            duration = (datetime.utcnow() - start_time).total_seconds()
            current_app.logger.error(f'API Error: {request.path} failed in {duration:.3f}s - {str(e)}')
            raise
    
    return decorated_function

# API Routes
@orders_bp.route('/', methods=['POST'])
@require_api_key
@validate_json(CreateOrderSchema)
@log_request
def create_order():
    """
    Create a new order
    
    Creates an order by routing it to the appropriate platform (Veeqo or Easyship)
    based on the selected carrier and customer location.
    
    Returns:
        201: Order created successfully
        400: Validation error
        500: Internal server error
    """
    try:
        from app.services.order_service import OrderService
        
        order_service = OrderService()
        result = order_service.create_order(request.validated_data)
        
        return jsonify({
            'status': 'success',
            'order': result,
            'message': 'Order created successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Order validation failed',
            'details': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f'Order creation failed: {str(e)}')
        return jsonify({
            'error': 'Failed to create order',
            'message': 'Please try again later'
        }), 500

@orders_bp.route('/bulk', methods=['POST'])
@require_api_key
@log_request
def create_bulk_orders():
    """
    Create multiple orders in batch
    
    Processes multiple orders asynchronously for better performance.
    Returns a task ID for tracking progress.
    
    Returns:
        202: Batch processing started
        400: Validation error
        500: Internal server error
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        orders_data = request.json.get('orders', [])
        if not orders_data:
            return jsonify({'error': 'No orders provided'}), 400
        
        # Validate each order
        schema = CreateOrderSchema()
        validated_orders = []
        
        for i, order_data in enumerate(orders_data):
            try:
                validated_order = schema.load(order_data)
                validated_orders.append(validated_order)
            except ValidationError as e:
                return jsonify({
                    'error': f'Validation failed for order {i+1}',
                    'details': e.messages
                }), 400
        
        # Queue batch processing task
        from app.tasks.order_tasks import process_bulk_orders
        task = process_bulk_orders.delay(validated_orders)
        
        return jsonify({
            'status': 'processing',
            'task_id': task.id,
            'orders_count': len(validated_orders),
            'message': 'Batch processing started'
        }), 202
        
    except Exception as e:
        current_app.logger.error(f'Bulk order processing failed: {str(e)}')
        return jsonify({
            'error': 'Failed to process bulk orders',
            'message': 'Please try again later'
        }), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@require_api_key
@log_request
def get_order(order_id):
    """
    Get order details by ID
    
    Returns:
        200: Order details
        404: Order not found
        500: Internal server error
    """
    try:
        from app.services.order_service import OrderService
        
        order_service = OrderService()
        order = order_service.get_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'status': 'success',
            'order': order
        })
        
    except Exception as e:
        current_app.logger.error(f'Failed to get order {order_id}: {str(e)}')
        return jsonify({
            'error': 'Failed to retrieve order',
            'message': 'Please try again later'
        }), 500

@orders_bp.route('/', methods=['GET'])
@require_api_key
@log_request
def list_orders():
    """
    List orders with pagination and filtering
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        status: Filter by status
        platform: Filter by platform (veeqo, easyship)
        carrier: Filter by carrier
        
    Returns:
        200: List of orders
        400: Invalid parameters
        500: Internal server error
    """
    try:
        from app.services.order_service import OrderService
        
        # Parse query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        status = request.args.get('status')
        platform = request.args.get('platform')
        carrier = request.args.get('carrier')
        
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Invalid pagination parameters'}), 400
        
        # Get filtered orders
        order_service = OrderService()
        result = order_service.list_orders(
            page=page,
            per_page=per_page,
            status=status,
            platform=platform,
            carrier=carrier
        )
        
        return jsonify({
            'status': 'success',
            'orders': result['orders'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': result['total'],
                'pages': result['pages']
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Failed to list orders: {str(e)}')
        return jsonify({
            'error': 'Failed to retrieve orders',
            'message': 'Please try again later'
        }), 500

@orders_bp.route('/stats', methods=['GET'])
@require_api_key
@log_request
def get_order_stats():
    """
    Get order statistics
    
    Returns aggregated statistics about orders including counts by status,
    platform, carrier, and time-based metrics.
    
    Returns:
        200: Order statistics
        500: Internal server error
    """
    try:
        from app.services.order_service import OrderService
        
        order_service = OrderService()
        stats = order_service.get_order_statistics()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f'Failed to get order stats: {str(e)}')
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'message': 'Please try again later'
        }), 500

# Error handlers specific to this blueprint
@orders_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle Marshmallow validation errors"""
    return jsonify({
        'error': 'Validation failed',
        'details': error.messages
    }), 400

@orders_bp.errorhandler(429)
def handle_rate_limit(error):
    """Handle rate limit errors"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': str(error.retry_after)
    }), 429

# Helper functions
def _validate_api_key(api_key):
    """Validate API key (implement your validation logic)"""
    # This is a placeholder - implement your actual API key validation
    # You might check against a database, cache, or external service
    valid_keys = current_app.config.get('VALID_API_KEYS', [])
    return api_key in valid_keys or api_key == 'development-key'  # Remove dev key in production

# Blueprint configuration
@orders_bp.before_request
def before_request():
    """Execute before each request to this blueprint"""
    # Add any common pre-processing logic here
    pass

@orders_bp.after_request
def after_request(response):
    """Execute after each request to this blueprint"""
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response
