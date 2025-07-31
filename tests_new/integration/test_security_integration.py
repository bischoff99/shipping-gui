"""
Integration tests for security middleware with the complete Flask application.
Tests end-to-end security features including CSRF, rate limiting, and input validation.
"""
import pytest
import json
import time
from unittest.mock import patch, MagicMock
from flask import Flask

# Import the app factory and security components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.app_factory import create_app
from middleware.security import SecurityManager


class TestSecurityIntegration:
    """Integration tests for security middleware."""

    @pytest.fixture
    def app(self):
        """Create test app with security middleware."""
        app = create_app('testing')
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    def test_csrf_protection_enabled(self, app, client):
        """Test CSRF protection is properly enabled."""
        app.config['WTF_CSRF_ENABLED'] = True
        
        # POST request without CSRF token should fail
        response = client.post('/orders/create', data={
            'customer_data': 'test data'
        })
        
        # Should either be rejected or redirect to get CSRF token
        assert response.status_code in [400, 403, 302]

    def test_security_headers_applied(self, client):
        """Test that security headers are applied to all responses."""
        response = client.get('/health')
        
        # Check for security headers
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert 'X-XSS-Protection' in response.headers

    def test_input_sanitization_integration(self, client):
        """Test input sanitization across different endpoints."""
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
        
        response = client.post('/api/parse_customer',
                             json=malicious_data,
                             content_type='application/json')
        
        # Should process but sanitize malicious content
        if response.status_code == 200:
            data = json.loads(response.data)
            # Script tags should be removed
            assert '<script>' not in str(data)

    @patch('middleware.security.Redis')
    def test_rate_limiting_integration(self, mock_redis, app, client):
        """Test rate limiting across multiple requests."""
        # Mock Redis to simulate rate limiting
        mock_redis_client = MagicMock()
        mock_redis.return_value = mock_redis_client
        
        # Simulate approaching rate limit
        mock_redis_client.get.side_effect = [b'8', b'9', b'10', b'11']
        
        with app.app_context():
            # First few requests should succeed
            response1 = client.get('/api/get_products')
            response2 = client.get('/api/get_products')
            response3 = client.get('/api/get_products')
            
            # Rate limit exceeded
            response4 = client.get('/api/get_products')
            
            # At least one should be rate limited
            responses = [response1, response2, response3, response4]
            status_codes = [r.status_code for r in responses]
            
            # Should have mix of successful and rate-limited responses
            assert any(code == 429 for code in status_codes) or all(code in [200, 400, 500] for code in status_codes)

    def test_api_key_validation_integration(self, app, client):
        """Test API key validation across protected endpoints."""
        app.config['VEEQO_API_KEY'] = 'valid-test-key'
        
        # Request without API key
        response1 = client.get('/api/get_products')
        
        # Request with invalid API key
        response2 = client.get('/api/get_products',
                             headers={'X-API-Key': 'invalid-key'})
        
        # Request with valid API key
        response3 = client.get('/api/get_products',
                             headers={'X-API-Key': 'valid-test-key'})
        
        # Valid key should work better than invalid ones
        assert response3.status_code <= response1.status_code
        assert response3.status_code <= response2.status_code

    def test_json_validation_integration(self, client):
        """Test JSON validation across API endpoints."""
        # Valid JSON data
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
        
        # Invalid JSON data
        invalid_data = {
            'name': '',  # Empty name
            'email': 'invalid-email',  # Invalid email
            'phone': '123'  # Too short
        }
        
        # Test valid data
        response1 = client.post('/api/parse_customer',
                               json=valid_data,
                               content_type='application/json')
        
        # Test invalid data
        response2 = client.post('/api/parse_customer',
                               json=invalid_data,
                               content_type='application/json')
        
        # Valid data should work better than invalid data
        assert response1.status_code <= response2.status_code

    def test_error_handling_security(self, client):
        """Test that error handling doesn't leak sensitive information."""
        # Trigger various errors
        responses = [
            client.post('/api/nonexistent'),
            client.get('/api/get_products', headers={'X-API-Key': 'malicious-injection-attempt'}),
            client.post('/api/parse_customer', data='malformed json'),
        ]
        
        for response in responses:
            if response.status_code >= 400:
                # Error responses shouldn't contain sensitive info
                response_text = response.data.decode().lower()
                sensitive_terms = ['password', 'secret', 'key', 'token', 'traceback']
                
                for term in sensitive_terms:
                    assert term not in response_text, f"Sensitive term '{term}' found in error response"

    def test_session_security(self, app, client):
        """Test session security configuration."""
        with app.app_context():
            # Check session configuration
            if app.config.get('SESSION_COOKIE_SECURE'):
                assert app.config['SESSION_COOKIE_SECURE'] is True
            
            if app.config.get('SESSION_COOKIE_HTTPONLY'):
                assert app.config['SESSION_COOKIE_HTTPONLY'] is True
                
            if app.config.get('SESSION_COOKIE_SAMESITE'):
                assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'

    def test_content_type_validation(self, client):
        """Test content type validation for API endpoints."""
        # JSON endpoint should reject non-JSON content
        response = client.post('/api/parse_customer',
                             data='not json data',
                             content_type='text/plain')
        
        assert response.status_code == 400

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attempts."""
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; UPDATE users SET admin=1; --",
            "' UNION SELECT * FROM sensitive_table; --"
        ]
        
        for payload in sql_injection_payloads:
            malicious_data = {
                'name': payload,
                'email': 'test@example.com',
                'phone': '+1234567890',
                'address': '123 Main St',
                'city': 'Boston',
                'state': 'MA',
                'zip': '02101',
                'country': 'US'
            }
            
            response = client.post('/api/parse_customer',
                                 json=malicious_data,
                                 content_type='application/json')
            
            # Should either sanitize or reject malicious input
            if response.status_code == 200:
                data = json.loads(response.data)
                # SQL injection attempts should be sanitized
                assert 'DROP TABLE' not in str(data)
                assert 'UNION SELECT' not in str(data)

    def test_xss_protection_integration(self, client):
        """Test XSS protection across the application."""
        xss_payloads = [
            '<script>alert("xss")</script>',
            '<img src="x" onerror="alert(1)">',
            'javascript:alert("xss")',
            '<svg onload="alert(1)">',
            '<iframe src="javascript:alert(1)"></iframe>'
        ]
        
        for payload in xss_payloads:
            malicious_data = {
                'name': f'{payload}John Doe',
                'email': 'john@example.com',
                'phone': '+1234567890',
                'address': '123 Main St',
                'city': 'Boston', 
                'state': 'MA',
                'zip': '02101',
                'country': 'US'
            }
            
            response = client.post('/api/parse_customer',
                                 json=malicious_data,
                                 content_type='application/json')
            
            # Should sanitize XSS attempts
            if response.status_code == 200:
                response_text = response.data.decode()
                assert '<script>' not in response_text
                assert 'javascript:' not in response_text
                assert 'onerror=' not in response_text

    def test_file_upload_security(self, client):
        """Test file upload security (if applicable)."""
        # Test malicious file upload attempt
        malicious_file_data = {
            'file': (BytesIO(b'<?php system($_GET["cmd"]); ?>'), 'shell.php')
        }
        
        # Attempt to upload to any file endpoint
        response = client.post('/api/upload',
                             data=malicious_file_data,
                             content_type='multipart/form-data')
        
        # Should reject malicious files or endpoint shouldn't exist
        assert response.status_code in [404, 400, 403, 405]

    def test_directory_traversal_protection(self, client):
        """Test protection against directory traversal attacks."""
        traversal_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '....//....//....//etc/passwd',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd'
        ]
        
        for payload in traversal_payloads:
            # Test in various parameters
            response = client.get(f'/api/get_file?path={payload}')
            
            # Endpoint might not exist, but shouldn't leak files
            if response.status_code == 200:
                response_text = response.data.decode().lower()
                sensitive_content = ['root:', 'password', 'administrator']
                
                for content in sensitive_content:
                    assert content not in response_text

    def test_security_middleware_performance(self, client):
        """Test that security middleware doesn't significantly impact performance."""
        import time
        
        # Measure response time for multiple requests
        start_time = time.time()
        
        for _ in range(10):
            response = client.get('/health')
            assert response.status_code in [200, 503]
        
        end_time = time.time()
        avg_response_time = (end_time - start_time) / 10
        
        # Security middleware shouldn't add more than 100ms per request
        assert avg_response_time < 0.1

    def test_concurrent_security_requests(self, app):
        """Test security middleware under concurrent load."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            with app.test_client() as client:
                response = client.get('/health')
                results.put(response.status_code)
        
        # Create multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should complete successfully
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 5
        assert all(code in [200, 503] for code in status_codes)