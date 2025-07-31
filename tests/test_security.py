"""
Test security middleware functionality
"""
import pytest
import json
from unittest.mock import patch, Mock
from middleware.security import SecurityManager, APIKeyGenerator


class TestSecurityManager:
    """Test security manager functionality"""
    
    def test_api_key_generation(self):
        """Test API key generation"""
        key1 = APIKeyGenerator.generate_api_key()
        key2 = APIKeyGenerator.generate_api_key('test_')
        
        assert len(key1) > 20  # Should be reasonably long
        assert key2.startswith('test_')
        assert key1 != key2  # Should be unique
    
    def test_api_key_hashing(self):
        """Test API key hashing and verification"""
        api_key = 'test_api_key_123'
        hashed = APIKeyGenerator.hash_api_key(api_key)
        
        assert len(hashed) == 64  # SHA256 hex string length
        assert APIKeyGenerator.verify_api_key(api_key, hashed) is True
        assert APIKeyGenerator.verify_api_key('wrong_key', hashed) is False
    
    def test_unauthorized_api_access(self, client):
        """Test API access without authentication"""
        response = client.post('/api/create_order', 
                             data=json.dumps({'test': 'data'}),
                             headers={'Content-Type': 'application/json'})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'API key required' in data['error']
    
    def test_invalid_api_key(self, client):
        """Test API access with invalid key"""
        headers = {
            'Authorization': 'Bearer invalid_key',
            'Content-Type': 'application/json'
        }
        
        response = client.post('/api/create_order',
                             data=json.dumps({'test': 'data'}),
                             headers=headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid API key' in data['error']
    
    def test_valid_api_key_access(self, client, auth_headers):
        """Test API access with valid key"""
        # This should pass authentication (but may fail for other reasons)
        response = client.post('/api/parse_customer',
                             data=json.dumps({'input': 'test data'}),
                             headers=auth_headers)
        
        # Should not get 401 (authentication error)
        assert response.status_code != 401
    
    def test_public_endpoint_access(self, client):
        """Test access to public endpoints without authentication"""
        # Health check should be accessible without auth
        response = client.get('/health')
        assert response.status_code == 200
        
        # Dashboard should be accessible without auth (GET only)
        response = client.get('/dashboard')
        assert response.status_code == 200
    
    def test_security_headers(self, client):
        """Test security headers are added to responses"""
        response = client.get('/health')
        
        # Check for security headers
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-XSS-Protection' in response.headers
        assert '1; mode=block' in response.headers['X-XSS-Protection']
    
    @patch('middleware.security.redis')
    def test_rate_limiting_setup(self, mock_redis, app):
        """Test rate limiting configuration"""
        mock_redis.from_url.return_value.ping.return_value = True
        
        with app.app_context():
            security_manager = SecurityManager(app)
            assert security_manager.limiter is not None
    
    def test_api_key_extraction_bearer_token(self, app):
        """Test API key extraction from Bearer token"""
        with app.test_request_context(
            '/api/test', 
            headers={'Authorization': 'Bearer test_key_123'}
        ):
            security_manager = SecurityManager()
            extracted_key = security_manager._extract_api_key()
            assert extracted_key == 'test_key_123'
    
    def test_api_key_extraction_x_api_key(self, app):
        """Test API key extraction from X-API-Key header"""
        with app.test_request_context(
            '/api/test',
            headers={'X-API-Key': 'test_key_456'}
        ):
            security_manager = SecurityManager()
            extracted_key = security_manager._extract_api_key()
            assert extracted_key == 'test_key_456'
    
    def test_api_key_extraction_query_param(self, app):
        """Test API key extraction from query parameter (development only)"""
        app.config['FLASK_ENV'] = 'development'
        
        with app.test_request_context('/api/test?api_key=test_key_789'):
            security_manager = SecurityManager()
            extracted_key = security_manager._extract_api_key()
            assert extracted_key == 'test_key_789'
    
    def test_api_key_extraction_no_key(self, app):
        """Test API key extraction when no key is provided"""
        with app.test_request_context('/api/test'):
            security_manager = SecurityManager()
            extracted_key = security_manager._extract_api_key()
            assert extracted_key is None


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_not_exceeded(self, client, auth_headers):
        """Test normal request within rate limits"""
        # Make a few requests that should be within limits
        for _ in range(3):
            response = client.get('/api/dashboard-stats', headers=auth_headers)
            assert response.status_code != 429  # Not rate limited
    
    @patch('flask_limiter.Limiter.limit')
    def test_rate_limit_exceeded_simulation(self, mock_limit, app):
        """Test rate limit exceeded scenario (simulated)"""
        # This is a unit test simulation since we can't easily trigger
        # actual rate limiting in tests
        mock_limit.side_effect = Exception("Rate limit exceeded")
        
        with app.app_context():
            security_manager = SecurityManager(app)
            # Test that rate limiting is configured
            assert security_manager.limiter is not None


class TestAPIKeyManagement:
    """Test API key management functionality"""
    
    def test_api_key_validation_active_key(self, app):
        """Test validation of active API key"""
        with app.app_context():
            security_manager = SecurityManager(app)
            
            # Add a test key
            test_key = 'test_active_key'
            security_manager.api_keys[test_key] = {
                'active': True,
                'expires_at': None,
                'usage_count': 0
            }
            
            assert security_manager._validate_api_key(test_key) is True
    
    def test_api_key_validation_inactive_key(self, app):
        """Test validation of inactive API key"""
        with app.app_context():
            security_manager = SecurityManager(app)
            
            # Add an inactive test key
            test_key = 'test_inactive_key'
            security_manager.api_keys[test_key] = {
                'active': False,
                'expires_at': None,
                'usage_count': 0
            }
            
            assert security_manager._validate_api_key(test_key) is False
    
    def test_api_key_validation_nonexistent_key(self, app):
        """Test validation of nonexistent API key"""
        with app.app_context():
            security_manager = SecurityManager(app)
            assert security_manager._validate_api_key('nonexistent_key') is False
    
    def test_get_api_key_stats(self, app):
        """Test getting API key statistics"""
        with app.app_context():
            security_manager = SecurityManager(app)
            
            # Add some test keys
            security_manager.api_keys['key1'] = {
                'name': 'Test Key 1',
                'active': True,
                'permissions': ['read'],
                'usage_count': 10
            }
            security_manager.api_keys['key2'] = {
                'name': 'Test Key 2',
                'active': False,
                'permissions': ['read', 'write'],
                'usage_count': 5
            }
            
            stats = security_manager.get_api_key_stats()
            
            assert stats['total_keys'] == 2
            assert stats['active_keys'] == 1
            assert len(stats['keys']) == 2