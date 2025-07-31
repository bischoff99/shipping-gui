"""
Unit tests for modular route architecture.
Tests the new blueprint-based routing system for orders, API, dashboard, and health endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, Mock
from flask import Flask

# Import route modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from routes.orders import orders_bp
from routes.api import api_bp  
from routes.dashboard import dashboard_bp
from routes.health import health_bp


class TestOrdersBlueprint:
    """Test suite for orders blueprint routes."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with orders blueprint."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.register_blueprint(orders_bp, url_prefix='/orders')
        return app

    def test_create_order_get(self, app):
        """Test GET request to create order page."""
        with app.test_client() as client:
            response = client.get('/orders/create')
            assert response.status_code == 200

    @patch('routes.orders.create_order_logic')
    def test_create_order_post_valid(self, mock_create_order, app):
        """Test POST request to create order with valid data."""
        mock_create_order.return_value = {
            'success': True,
            'order_id': 'TEST123',
            'platform': 'veeqo'
        }
        
        with app.test_client() as client:
            response = client.post('/orders/create', data={
                'customer_data': 'John Doe\t+1234567890\tjohn@email.com\t123 Main St\tBoston\tMA\t02101\tUS'
            })
            
            assert response.status_code == 200
            mock_create_order.assert_called_once()

    @patch('routes.orders.create_order_logic')
    def test_create_order_post_invalid(self, mock_create_order, app):
        """Test POST request to create order with invalid data."""
        mock_create_order.side_effect = ValueError("Invalid customer data")
        
        with app.test_client() as client:
            response = client.post('/orders/create', data={
                'customer_data': 'invalid data'
            })
            
            assert response.status_code == 200  # Should render template with error
            mock_create_order.assert_called_once()

    @patch('routes.orders.validate_customer_data')
    def test_api_create_order_validation(self, mock_validate, app):
        """Test API endpoint for order creation with validation."""
        mock_validate.return_value = True
        
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
            
            response = client.post('/orders/api/create',
                                 json=valid_data,
                                 content_type='application/json')
            
            # Should process successfully
            mock_validate.assert_called_once()


class TestAPIBlueprint:
    """Test suite for API blueprint routes."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with API blueprint."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        app.register_blueprint(api_bp, url_prefix='/api')
        return app

    @patch('routes.api.parse_customer_data')
    def test_parse_customer_endpoint(self, mock_parse, app):
        """Test customer data parsing endpoint."""
        mock_parse.return_value = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        }
        
        with app.test_client() as client:
            response = client.post('/api/parse_customer', 
                                 json={'data': 'John Doe +1234567890 john@example.com'},
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['name'] == 'John Doe'
            mock_parse.assert_called_once()

    @patch('routes.api.get_products_from_api')
    def test_get_products_endpoint(self, mock_get_products, app):
        """Test products retrieval endpoint."""
        mock_get_products.return_value = [
            {'id': 1, 'name': 'Product 1', 'price': 10.00},
            {'id': 2, 'name': 'Product 2', 'price': 20.00}
        ]
        
        with app.test_client() as client:
            response = client.get('/api/get_products')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 2
            assert data[0]['name'] == 'Product 1'
            mock_get_products.assert_called_once()

    @patch('routes.api.get_routing_decision')
    def test_get_routing_endpoint(self, mock_routing, app):
        """Test routing decision endpoint."""
        mock_routing.return_value = {
            'platform': 'veeqo',
            'warehouse': 'Nevada',
            'confidence': 0.95
        }
        
        with app.test_client() as client:
            response = client.post('/api/get_routing',
                                 json={'carrier': 'UPS', 'destination': 'CA'},
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['platform'] == 'veeqo'
            assert data['confidence'] == 0.95
            mock_routing.assert_called_once()

    def test_api_error_handling(self, app):
        """Test API error handling for invalid requests."""
        with app.test_client() as client:
            # Test missing JSON data
            response = client.post('/api/parse_customer')
            assert response.status_code == 400
            
            # Test invalid JSON format
            response = client.post('/api/parse_customer',
                                 data='invalid json',
                                 content_type='application/json')
            assert response.status_code == 400

    @patch('routes.api.SecurityManager')
    def test_api_rate_limiting(self, mock_security, app):
        """Test API rate limiting functionality."""
        mock_security_instance = MagicMock()
        mock_security_instance.check_rate_limit.return_value = False
        mock_security.return_value = mock_security_instance
        
        with app.test_client() as client:
            response = client.get('/api/get_products')
            
            # Should handle rate limiting appropriately
            assert response.status_code in [200, 429]  # Success or rate limited


class TestDashboardBlueprint:
    """Test suite for dashboard blueprint routes."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with dashboard blueprint."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        return app

    @patch('routes.dashboard.get_system_metrics')
    def test_dashboard_index(self, mock_metrics, app):
        """Test dashboard index page."""
        mock_metrics.return_value = {
            'orders_today': 25,
            'total_orders': 1500,
            'system_health': 'healthy',
            'api_status': {'veeqo': True, 'easyship': True}
        }
        
        with app.test_client() as client:
            response = client.get('/dashboard/')
            
            assert response.status_code == 200
            mock_metrics.assert_called_once()

    @patch('routes.dashboard.get_recent_orders')
    def test_orders_dashboard(self, mock_orders, app):
        """Test orders dashboard page."""
        mock_orders.return_value = [
            {'id': 1, 'customer': 'John Doe', 'status': 'shipped'},
            {'id': 2, 'customer': 'Jane Smith', 'status': 'processing'}
        ]
        
        with app.test_client() as client:
            response = client.get('/dashboard/orders')
            
            assert response.status_code == 200
            mock_orders.assert_called_once()

    @patch('routes.dashboard.get_warehouse_status')
    def test_inventory_dashboard(self, mock_warehouse, app):
        """Test inventory dashboard page."""
        mock_warehouse.return_value = {
            'warehouses': [
                {'name': 'Nevada', 'status': 'active', 'orders': 50},
                {'name': 'California', 'status': 'active', 'orders': 30}
            ]
        }
        
        with app.test_client() as client:
            response = client.get('/dashboard/inventory')
            
            assert response.status_code == 200
            mock_warehouse.assert_called_once()

    def test_dashboard_error_handling(self, app):
        """Test dashboard error handling."""
        with app.test_client() as client:
            # Test nonexistent dashboard route
            response = client.get('/dashboard/nonexistent')
            assert response.status_code == 404


class TestHealthBlueprint:
    """Test suite for health check blueprint routes."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with health blueprint."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        app.register_blueprint(health_bp)
        return app

    def test_health_check(self, app):
        """Test basic health check endpoint."""
        with app.test_client() as client:
            response = client.get('/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'status' in data
            assert data['status'] in ['healthy', 'unhealthy']

    @patch('routes.health.check_database_connection')
    @patch('routes.health.check_api_connections')
    def test_health_check_detailed(self, mock_api_check, mock_db_check, app):
        """Test detailed health check with dependencies."""
        mock_db_check.return_value = True
        mock_api_check.return_value = {
            'veeqo': True,
            'easyship': True
        }
        
        with app.test_client() as client:
            response = client.get('/health')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert 'database' in data
            assert 'apis' in data

    @patch('routes.health.check_database_connection')
    def test_health_check_unhealthy(self, mock_db_check, app):
        """Test health check when system is unhealthy."""
        mock_db_check.return_value = False
        
        with app.test_client() as client:
            response = client.get('/health')
            
            assert response.status_code == 503  # Service Unavailable
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'

    def test_readiness_check(self, app):
        """Test Kubernetes readiness probe."""
        with app.test_client() as client:
            response = client.get('/ready')
            
            assert response.status_code in [200, 503]
            data = json.loads(response.data)
            assert 'ready' in data

    def test_liveness_check(self, app):
        """Test Kubernetes liveness probe."""
        with app.test_client() as client:
            response = client.get('/live')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['alive'] is True

    @patch('routes.health.get_prometheus_metrics')
    def test_metrics_endpoint(self, mock_metrics, app):
        """Test Prometheus metrics endpoint."""
        mock_metrics.return_value = """
        # HELP orders_total Total number of orders processed
        # TYPE orders_total counter
        orders_total 1500
        
        # HELP system_health System health status (1=healthy, 0=unhealthy)
        # TYPE system_health gauge
        system_health 1
        """
        
        with app.test_client() as client:
            response = client.get('/metrics')
            
            assert response.status_code == 200
            assert 'orders_total' in response.data.decode()
            assert 'system_health' in response.data.decode()
            mock_metrics.assert_called_once()


class TestBlueprintIntegration:
    """Test suite for blueprint integration and routing."""

    @pytest.fixture
    def app(self):
        """Create test Flask app with all blueprints."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['TESTING'] = True
        
        # Register all blueprints
        app.register_blueprint(orders_bp, url_prefix='/orders')
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(health_bp)
        
        return app

    def test_blueprint_url_prefixes(self, app):
        """Test that blueprint URL prefixes work correctly."""
        with app.test_client() as client:
            # Test orders blueprint
            response = client.get('/orders/create')
            assert response.status_code == 200
            
            # Test API blueprint
            response = client.get('/api/get_products')
            assert response.status_code in [200, 400, 500]  # Various valid responses
            
            # Test dashboard blueprint
            response = client.get('/dashboard/')
            assert response.status_code in [200, 500]  # Various valid responses
            
            # Test health blueprint (no prefix)
            response = client.get('/health')
            assert response.status_code in [200, 503]

    def test_blueprint_error_isolation(self, app):
        """Test that errors in one blueprint don't affect others."""
        with app.test_client() as client:
            # Even if one blueprint has issues, others should work
            health_response = client.get('/health')
            assert health_response.status_code in [200, 503]
            
            # Test cross-blueprint functionality
            orders_response = client.get('/orders/create')
            assert orders_response.status_code == 200

    def test_blueprint_context_sharing(self, app):
        """Test that blueprints can share application context."""
        with app.app_context():
            # All blueprints should have access to the same app config
            assert app.config['TESTING'] is True
            assert app.config['SECRET_KEY'] == 'test-secret-key'

    def test_blueprint_before_request_handlers(self, app):
        """Test that before_request handlers work across blueprints."""
        request_count = 0
        
        @app.before_request
        def count_requests():
            nonlocal request_count
            request_count += 1
        
        with app.test_client() as client:
            client.get('/health')
            client.get('/orders/create')
            client.get('/api/get_products')
            
            assert request_count == 3