"""
Production Security Middleware for API Authentication and Rate Limiting
"""
import os
import hashlib
import secrets
from typing import Dict, Optional, Any
from functools import wraps
from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta, timezone

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class SecurityManager:
    """Comprehensive security manager for production deployment"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.limiter: Optional[Limiter] = None
        self.redis_client: Optional[redis.Redis] = None
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize security middleware with Flask app"""
        self.app = app
        self.setup_rate_limiter()
        self.setup_api_key_validation()
        self.load_api_keys()
        self.setup_security_headers()
    
    def setup_rate_limiter(self):
        """Configure Flask-Limiter with Redis backend"""
        redis_url = self.app.config.get('REDIS_URL', 'redis://localhost:6379')
        
        try:
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()  # Test connection
        except redis.ConnectionError:
            self.app.logger.warning("Redis connection failed, using in-memory rate limiting")
            self.redis_client = None
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app=self.app,
            key_func=self._get_rate_limit_key,
            storage_uri=redis_url if self.redis_client else None,
            default_limits=[self.app.config.get('RATELIMIT_DEFAULT', '100 per hour')],
            headers_enabled=self.app.config.get('RATELIMIT_HEADERS_ENABLED', True)
        )
        
        # Custom rate limit exceeded handler
        @self.limiter.request_filter
        def exempt_healthcheck():
            return request.endpoint == 'health_check'
    
    def _get_rate_limit_key(self) -> str:
        """Generate rate limit key based on API key or IP"""
        # Use API key if available for more granular limiting
        api_key = self._extract_api_key()
        if api_key and api_key in self.api_keys:
            return f"api_key:{api_key}"
        
        # Fall back to IP-based limiting
        return get_remote_address()
    
    def setup_api_key_validation(self):
        """Set up API key validation middleware"""
        
        @self.app.before_request
        def validate_api_key():
            # Skip validation for health checks and static files
            if request.endpoint in ['health_check', 'static']:
                return
            
            # Skip validation for GET requests to root/dashboard (public access)
            if request.method == 'GET' and request.endpoint in ['create_order', 'dashboard']:
                return
            
            # Require API key for all API endpoints
            if request.path.startswith('/api/'):
                api_key = self._extract_api_key()
                if not api_key:
                    return jsonify({
                        'error': 'API key required',
                        'message': 'Please provide a valid API key in Authorization header or api_key parameter'
                    }), 401
                
                if not self._validate_api_key(api_key):
                    self._log_security_event('invalid_api_key', api_key)
                    return jsonify({
                        'error': 'Invalid API key',
                        'message': 'The provided API key is invalid or expired'
                    }), 401
                
                # Store validated API key info in request context
                g.api_key_info = self.api_keys.get(api_key, {})
                g.api_key = api_key
    
    def _extract_api_key(self) -> Optional[str]:
        """Extract API key from request headers or parameters"""
        # Try Authorization header first (Bearer token)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Try X-API-Key header
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return api_key
        
        # Try query parameter (less secure, only for development)
        if self.app.config.get('FLASK_ENV') != 'production':
            return request.args.get('api_key')
        
        return None
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key against stored keys"""
        if not api_key or api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        
        # Check if key is active
        if not key_info.get('active', True):
            return False
        
        # Check expiration
        expires_at = key_info.get('expires_at')
        if expires_at and datetime.now(timezone.utc) > expires_at:
            return False
        
        # Update last used timestamp
        key_info['last_used'] = datetime.now(timezone.utc)
        key_info['usage_count'] = key_info.get('usage_count', 0) + 1
        
        return True
    
    def load_api_keys(self):
        """Load API keys from environment and configuration"""
        # Load from environment variables
        internal_api_key = os.environ.get('INTERNAL_API_KEY')
        if internal_api_key:
            self.api_keys[internal_api_key] = {
                'name': 'Internal Service',
                'permissions': ['read', 'write', 'admin'],
                'rate_limit': '1000 per hour',
                'active': True,
                'created_at': datetime.now(timezone.utc),
                'expires_at': None,  # Never expires
                'usage_count': 0
            }
        
        # Load client API keys (would typically come from database)
        client_keys = os.environ.get('CLIENT_API_KEYS', '').split(',')
        for key in client_keys:
            if key.strip():
                self.api_keys[key.strip()] = {
                    'name': 'Client Service',
                    'permissions': ['read', 'write'],
                    'rate_limit': '100 per hour',
                    'active': True,
                    'created_at': datetime.now(timezone.utc),
                    'expires_at': datetime.now(timezone.utc) + timedelta(days=365),
                    'usage_count': 0
                }
        
        # Generate a default API key for development
        if self.app.config.get('FLASK_ENV') == 'development' and not self.api_keys:
            dev_key = 'dev_' + secrets.token_urlsafe(32)
            self.api_keys[dev_key] = {
                'name': 'Development Key',
                'permissions': ['read', 'write', 'admin'],
                'rate_limit': '10000 per hour',
                'active': True,
                'created_at': datetime.now(timezone.utc),
                'expires_at': None,
                'usage_count': 0
            }
            self.app.logger.info(f"Generated development API key: {dev_key}")
    
    def setup_security_headers(self):
        """Add security headers to all responses"""
        
        @self.app.after_request
        def add_security_headers(response):
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # XSS protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Strict transport security (HTTPS only)
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            response.headers['Content-Security-Policy'] = csp
            
            # Remove server header
            response.headers.pop('Server', None)
            
            return response
    
    def _log_security_event(self, event_type: str, details: str = ''):
        """Log security events for monitoring"""
        if hasattr(self.app, '_production_logger'):
            logger = self.app._production_logger
            logger.warning(
                f"Security event: {event_type}",
                extra={
                    'event_type': event_type,
                    'details': details,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'endpoint': request.endpoint,
                    'method': request.method
                }
            )
    
    def require_permission(self, permission: str):
        """Decorator to require specific permissions"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'api_key_info'):
                    return jsonify({'error': 'Authentication required'}), 401
                
                permissions = g.api_key_info.get('permissions', [])
                if permission not in permissions and 'admin' not in permissions:
                    self._log_security_event('insufficient_permissions', f"Required: {permission}")
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def rate_limit(self, limit: str):
        """Custom rate limit decorator"""
        def decorator(f):
            return self.limiter.limit(limit)(f)
        return decorator
    
    def get_api_key_stats(self) -> Dict[str, Any]:
        """Get API key usage statistics"""
        stats = {
            'total_keys': len(self.api_keys),
            'active_keys': sum(1 for key in self.api_keys.values() if key.get('active', True)),
            'keys': []
        }
        
        for key, info in self.api_keys.items():
            # Don't expose actual keys in stats
            key_stats = {
                'name': info.get('name', 'Unknown'),
                'permissions': info.get('permissions', []),
                'active': info.get('active', True),
                'usage_count': info.get('usage_count', 0),
                'last_used': info.get('last_used').isoformat() if info.get('last_used') else None,
                'expires_at': info.get('expires_at').isoformat() if info.get('expires_at') else None
            }
            stats['keys'].append(key_stats)
        
        return stats


def init_security(app: Flask) -> SecurityManager:
    """Initialize security manager with Flask app"""
    return SecurityManager(app)


class APIKeyGenerator:
    """Utility class for generating and managing API keys"""
    
    @staticmethod
    def generate_api_key(prefix: str = '') -> str:
        """Generate a secure API key"""
        key = secrets.token_urlsafe(32)
        return f"{prefix}{key}" if prefix else key
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """Verify API key against hash"""
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key