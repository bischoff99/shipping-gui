"""
Unit tests for the enhanced security middleware.
Tests CSRF protection, input validation, rate limiting, and security headers.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, Mock
from flask import Flask, request
from werkzeug.test import Client

# Import security middleware
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from middleware.security import SecurityManager, validate_json_input, CustomerInputSchema


class TestSecurityManager:
    """Test suite for SecurityManager middleware."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable for most tests
        return app

    @pytest.fixture
    def security_manager(self, app):
        """Create SecurityManager instance."""
        return SecurityManager(app)

    def test_security_manager_initialization(self, app):
        """Test SecurityManager initializes correctly."""
        security = SecurityManager(app)
        
        assert security.app == app
        assert security.redis_client is None  # Not initialized in test
        assert security.csrf is None
        assert security.limiter is None

    @patch('middleware.security.Redis')
    def test_init_security_with_redis(self, mock_redis, app, security_manager):
        """Test security initialization with Redis."""
        mock_redis_client = MagicMock()
        mock_redis.return_value = mock_redis_client
        
        app.config['CACHE_TYPE'] = 'RedisCache'
        app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379'
        
        security_manager.init_security()
        
        mock_redis.assert_called_once()
        assert security_manager.redis_client == mock_redis_client

    def test_init_security_without_redis(self, app, security_manager):
        """Test security initialization without Redis."""
        app.config['CACHE_TYPE'] = 'simple'
        
        security_manager.init_security()
        
        assert security_manager.redis_client is None

    @patch('middleware.security.CSRFProtect')
    def test_csrf_initialization(self, mock_csrf, app, security_manager):
        """Test CSRF protection initialization."""
        mock_csrf_instance = MagicMock()
        mock_csrf.return_value = mock_csrf_instance
        
        security_manager.init_security()
        
        mock_csrf.assert_called_once_with(app)
        assert security_manager.csrf == mock_csrf_instance

    @patch('middleware.security.Limiter')
    def test_rate_limiter_initialization(self, mock_limiter, app, security_manager):
        """Test rate limiter initialization."""
        mock_limiter_instance = MagicMock()
        mock_limiter.return_value = mock_limiter_instance
        
        security_manager.init_security()
        
        mock_limiter.assert_called_once()
        assert security_manager.limiter == mock_limiter_instance

    def test_validate_api_key_valid(self, app, security_manager):
        """Test API key validation with valid key."""
        app.config['VEEQO_API_KEY'] = 'valid-api-key'
        
        with app.test_request_context(headers={'X-API-Key': 'valid-api-key'}):
            result = security_manager.validate_api_key()
            assert result is True

    def test_validate_api_key_invalid(self, app, security_manager):
        """Test API key validation with invalid key."""
        app.config['VEEQO_API_KEY'] = 'valid-api-key'
        
        with app.test_request_context(headers={'X-API-Key': 'invalid-api-key'}):
            result = security_manager.validate_api_key()
            assert result is False

    def test_validate_api_key_missing(self, app, security_manager):
        """Test API key validation with missing key."""
        app.config['VEEQO_API_KEY'] = 'valid-api-key'
        
        with app.test_request_context():
            result = security_manager.validate_api_key()
            assert result is False

    def test_validate_api_key_no_config(self, app, security_manager):
        """Test API key validation with no configured key."""
        # No API key configured
        with app.test_request_context(headers={'X-API-Key': 'any-key'}):
            result = security_manager.validate_api_key()
            assert result is True  # Should pass if no key configured

    def test_sanitize_input_basic(self, security_manager):
        """Test basic input sanitization."""
        dirty_input = "<script>alert('xss')</script>Hello"
        clean_input = security_manager.sanitize_input(dirty_input)
        
        assert "<script>" not in clean_input
        assert "alert" not in clean_input
        assert "Hello" in clean_input

    def test_sanitize_input_sql_injection(self, security_manager):
        """Test SQL injection sanitization."""
        sql_input = "'; DROP TABLE users; --"
        clean_input = security_manager.sanitize_input(sql_input)
        
        assert "DROP TABLE" not in clean_input
        assert "--" not in clean_input

    def test_sanitize_input_none(self, security_manager):
        """Test sanitization with None input."""
        result = security_manager.sanitize_input(None)
        assert result is None

    def test_sanitize_input_non_string(self, security_manager):
        """Test sanitization with non-string input."""
        result = security_manager.sanitize_input(123)
        assert result == 123

    def test_check_rate_limit_with_redis(self, app, security_manager):
        """Test rate limiting with Redis backend."""
        mock_redis = MagicMock()
        security_manager.redis_client = mock_redis
        mock_redis.get.return_value = b'5'  # Current count
        
        with app.test_request_context():
            result = security_manager.check_rate_limit('test-endpoint', limit=10)
            
        assert result is True
        mock_redis.get.assert_called_once()
        mock_redis.setex.assert_called_once()

    def test_check_rate_limit_exceeded(self, app, security_manager):
        """Test rate limiting when limit exceeded."""
        mock_redis = MagicMock()
        security_manager.redis_client = mock_redis
        mock_redis.get.return_value = b'15'  # Over limit
        
        with app.test_request_context():
            result = security_manager.check_rate_limit('test-endpoint', limit=10)
            
        assert result is False

    def test_check_rate_limit_without_redis(self, app, security_manager):
        """Test rate limiting without Redis (should pass)."""
        with app.test_request_context():
            result = security_manager.check_rate_limit('test-endpoint', limit=10)
            
        assert result is True  # No Redis = no rate limiting

    def test_add_security_headers(self, app, security_manager):
        """Test security headers addition."""
        @app.route('/test')
        def test_route():
            return 'test'
        
        security_manager.init_security()
        
        with app.test_client() as client:
            response = client.get('/test')
            
            # Check for security headers
            assert 'X-Content-Type-Options' in response.headers
            assert response.headers['X-Content-Type-Options'] == 'nosniff'
            assert 'X-Frame-Options' in response.headers
            assert response.headers['X-Frame-Options'] == 'DENY'
            assert 'X-XSS-Protection' in response.headers


class TestValidateJsonInput:
    """Test suite for JSON input validation decorator."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        return app

    def test_validate_json_input_valid(self, app):
        """Test JSON validation with valid input."""
        @app.route('/test', methods=['POST'])
        @validate_json_input(CustomerInputSchema)
        def test_route():
            return {'status': 'success'}
        
        with app.test_client() as client:
            valid_data = {
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+1234567890',
                'address': '123 Main St',
                'city': 'Boston',
                'state': 'MA',
                'zip': '02101',
                'country': 'US'
            }
            
            response = client.post('/test', 
                                 json=valid_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'

    def test_validate_json_input_invalid(self, app):
        """Test JSON validation with invalid input."""
        @app.route('/test', methods=['POST'])
        @validate_json_input(CustomerInputSchema)
        def test_route():
            return {'status': 'success'}
        
        with app.test_client() as client:
            invalid_data = {
                'name': '',  # Empty name should fail validation
                'email': 'invalid-email',  # Invalid email format
                'phone': '123'  # Too short phone number
            }
            
            response = client.post('/test', 
                                 json=invalid_data,
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'validation' in data['error'].lower()

    def test_validate_json_input_missing_json(self, app):
        """Test JSON validation with missing JSON data."""
        @app.route('/test', methods=['POST'])
        @validate_json_input(CustomerInputSchema)
        def test_route():
            return {'status': 'success'}
        
        with app.test_client() as client:
            response = client.post('/test')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    def test_validate_json_input_malformed_json(self, app):
        """Test JSON validation with malformed JSON."""
        @app.route('/test', methods=['POST'])
        @validate_json_input(CustomerInputSchema)
        def test_route():
            return {'status': 'success'}
        
        with app.test_client() as client:
            response = client.post('/test', 
                                 data='{"invalid": json}',
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data


class TestCustomerInputSchema:
    """Test suite for CustomerInputSchema validation."""

    def test_schema_valid_data(self):
        """Test schema with valid customer data."""
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'address': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'country': 'US'
        }
        
        schema = CustomerInputSchema()
        result = schema.load(valid_data)
        
        assert result['name'] == 'John Doe'
        assert result['email'] == 'john@example.com'
        assert result['phone'] == '+1234567890'

    def test_schema_invalid_email(self):
        """Test schema with invalid email."""
        invalid_data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'phone': '+1234567890',
            'address': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'country': 'US'
        }
        
        schema = CustomerInputSchema()
        
        with pytest.raises(Exception):  # ValidationError
            schema.load(invalid_data)

    def test_schema_missing_required_fields(self):
        """Test schema with missing required fields."""
        incomplete_data = {
            'name': 'John Doe'
            # Missing other required fields
        }
        
        schema = CustomerInputSchema()
        
        with pytest.raises(Exception):  # ValidationError
            schema.load(incomplete_data)

    def test_schema_empty_strings(self):
        """Test schema with empty string values."""
        empty_data = {
            'name': '',
            'email': '',
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'zip': '',
            'country': ''
        }
        
        schema = CustomerInputSchema()
        
        with pytest.raises(Exception):  # ValidationError
            schema.load(empty_data)

    def test_schema_data_sanitization(self):
        """Test that schema sanitizes input data."""
        malicious_data = {
            'name': '<script>alert("xss")</script>John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'address': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'country': 'US'
        }
        
        schema = CustomerInputSchema()
        result = schema.load(malicious_data)
        
        # Script tags should be sanitized
        assert '<script>' not in result['name']
        assert 'John Doe' in result['name']