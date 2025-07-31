"""
Advanced Security Middleware - MCP Enhanced
Generated with AI assistance for enterprise-grade security
"""
import os
import secrets
import hashlib
import hmac
import time
from functools import wraps
from typing import Dict, List, Optional, Callable
from flask import request, jsonify, g, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import jwt
import redis


class SecurityManager:
    """Enterprise-grade security manager with MCP integration"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.csrf = None
        self.limiter = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security components"""
        self.app = app
        
        # Initialize Redis for rate limiting
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url)
        
        # Initialize CSRF protection
        self.csrf = CSRFProtect(app)
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            storage_uri=redis_url,
            default_limits=["1000 per hour", "100 per minute"]
        )
        
        # Configure secure defaults
        app.config.update({
            'WTF_CSRF_TIME_LIMIT': 3600,  # 1 hour
            'WTF_CSRF_SSL_STRICT': app.config.get('SSL_ENABLED', False),
            'SESSION_COOKIE_SECURE': app.config.get('SSL_ENABLED', False),
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
        })
    
    def generate_secure_secret_key(self) -> str:
        """Generate cryptographically secure secret key"""
        if os.environ.get('FLASK_ENV') == 'production':
            secret_key = os.environ.get('FLASK_SECRET_KEY')
            if not secret_key:
                raise ValueError(
                    "🔴 CRITICAL: FLASK_SECRET_KEY must be set in production! "
                    "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
                )
            return secret_key
        else:
            # Development mode - generate and warn
            generated_key = secrets.token_hex(32)
            print(f"⚠️  WARNING: Using generated SECRET_KEY for development: {generated_key[:16]}...")
            return generated_key
    
    def validate_api_key(self, api_key: str, required_scopes: List[str] = None) -> bool:
        """Validate API key with scope checking"""
        if not api_key:
            return False
        
        # Check against valid API keys (stored in Redis or database)
        valid_keys = self.get_valid_api_keys()
        
        for key_data in valid_keys:
            if hmac.compare_digest(api_key, key_data['key']):
                if required_scopes:
                    return all(scope in key_data.get('scopes', []) for scope in required_scopes)
                return True
        return False
    
    def get_valid_api_keys(self) -> List[Dict]:
        """Get valid API keys from secure storage"""
        # In production, this would fetch from a secure key management system
        # For now, return example structure
        return [
            {
                'key': os.environ.get('INTERNAL_API_KEY', 'dev-key-123'),
                'scopes': ['read', 'write', 'admin'],
                'expires': None
            }
        ]
    
    def require_api_key(self, scopes: List[str] = None):
        """Decorator to require valid API key"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
                
                if not self.validate_api_key(api_key, scopes):
                    return jsonify({
                        'error': 'Invalid or missing API key',
                        'code': 'UNAUTHORIZED'
                    }), 401
                
                g.api_key = api_key
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def audit_log(self, action: str, details: Dict = None):
        """Log security-relevant actions"""
        audit_entry = {
            'timestamp': time.time(),
            'action': action,
            'user_ip': get_remote_address(),
            'user_agent': request.headers.get('User-Agent', ''),
            'endpoint': request.endpoint,
            'method': request.method,
            'details': details or {}
        }
        
        # Store in Redis with expiration (30 days)
        audit_key = f"audit:{int(time.time())}:{secrets.token_hex(8)}"
        self.redis_client.setex(audit_key, 2592000, str(audit_entry))
        
        # Also log to application logger
        current_app.logger.info(f"AUDIT: {action}", extra=audit_entry)


# Input validation schemas using marshmallow
from marshmallow import Schema, fields, validate, ValidationError

class CustomerInputSchema(Schema):
    """Secure customer input validation schema"""
    name = fields.Str(
        required=True, 
        validate=validate.And(
            validate.Length(min=1, max=200),
            validate.Regexp(r'^[a-zA-Z\s\-\.\']+$', error='Invalid characters in name')
        )
    )
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(
        required=False, 
        allow_none=True,
        validate=validate.Regexp(r'^\+?[\d\s\-\(\)]+$', error='Invalid phone format')
    )
    address_1 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    address_2 = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=200)
    )
    city = fields.Str(
        required=True,
        validate=validate.And(
            validate.Length(min=1, max=100),
            validate.Regexp(r'^[a-zA-Z\s\-\.\']+$', error='Invalid characters in city')
        )
    )
    state = fields.Str(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50)
    )
    postal_code = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20)
    )
    country = fields.Str(
        required=True,
        validate=validate.And(
            validate.Length(min=2, max=2),
            validate.Regexp(r'^[A-Z]{2}$', error='Country must be 2-letter ISO code')
        )
    )


def validate_json_input(schema_class: Schema):
    """Decorator to validate JSON input against schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json(force=True)
                if not data:
                    return jsonify({
                        'error': 'Invalid JSON or empty request body',
                        'code': 'INVALID_INPUT'
                    }), 400
                
                schema = schema_class()
                validated_data = schema.load(data)
                g.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation failed',
                    'code': 'VALIDATION_ERROR',
                    'details': err.messages
                }), 400
            except Exception as err:
                current_app.logger.error(f"Input validation error: {err}")
                return jsonify({
                    'error': 'Invalid request format',
                    'code': 'INVALID_REQUEST'
                }), 400
                
        return decorated_function
    return decorator


# Security headers middleware
def add_security_headers(response):
    """Add comprehensive security headers"""
    security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response


# Example usage patterns
def setup_security(app):
    """Setup all security components"""
    security = SecurityManager(app)
    
    # Add security headers to all responses
    app.after_request(add_security_headers)
    
    # Configure secure secret key
    app.secret_key = security.generate_secure_secret_key()
    
    return security