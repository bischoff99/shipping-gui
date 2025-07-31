"""
Test API endpoints
"""
import json
import pytest
from unittest.mock import patch, Mock


class TestAPIEndpoints:
    """Test API endpoints functionality"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'checks' in data
    
    def test_readiness_check(self, client):
        """Test readiness probe endpoint"""
        response = client.get('/health/ready')
        assert response.status_code in [200, 503]
        
        data = json.loads(response.data)
        assert 'ready' in data
        assert 'checks' in data
    
    def test_liveness_check(self, client):
        """Test liveness probe endpoint"""
        response = client.get('/health/live')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['alive'] is True
        assert 'timestamp' in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get('/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'app_info' in data
        assert 'version' in data['app_info']
    
    def test_api_parse_customer(self, client, auth_headers):
        """Test customer parsing API"""
        customer_input = {
            "input": "John Doe\njohn@example.com\n+1-555-0123\n123 Main St\nLos Angeles, CA 90210"
        }
        
        response = client.post(
            '/api/parse_customer',
            data=json.dumps(customer_input),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
    
    def test_api_parse_customer_invalid_input(self, client, auth_headers):
        """Test customer parsing with invalid input"""
        response = client.post(
            '/api/parse_customer',
            data=json.dumps({}),
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    @patch('api.veeqo_api.VeeqoAPI')
    def test_api_get_products_veeqo(self, mock_veeqo, client, auth_headers):
        """Test get products API for Veeqo"""
        mock_instance = Mock()
        mock_instance.get_random_products.return_value = [
            {'id': '1', 'title': 'Test Product', 'sku': 'TEST-001'}
        ]
        mock_veeqo.return_value = mock_instance
        
        response = client.get(
            '/api/get_products?platform=VEEQO&count=1',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['platform'] == 'VEEQO'
        assert len(data['products']) == 1
    
    @patch('api.easyship_api.EasyshipAPI')
    def test_api_get_products_easyship(self, mock_easyship, client, auth_headers):
        """Test get products API for Easyship"""
        mock_instance = Mock()
        mock_instance.get_random_products.return_value = [
            {'id': '1', 'name': 'Test Product', 'sku': 'TEST-001'}
        ]
        mock_easyship.return_value = mock_instance
        
        response = client.get(
            '/api/get_products?platform=EASYSHIP&count=1',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['platform'] == 'EASYSHIP'
    
    def test_api_get_routing(self, client, auth_headers, sample_customer_data):
        """Test routing API"""
        response = client.post(
            '/api/get_routing',
            data=json.dumps(sample_customer_data),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'platform' in data
        assert 'carrier' in data
        assert 'warehouse_info' in data
    
    def test_api_create_order(self, client, auth_headers, sample_order_data):
        """Test order creation API"""
        with patch('services.order_processor.OrderProcessor') as mock_processor:
            mock_instance = Mock()
            mock_instance.process_order.return_value = {
                'success': True,
                'order_id': 'ORD-001',
                'platform': 'VEEQO',
                'tracking_info': 'TRACK-123'
            }
            mock_processor.return_value = mock_instance
            
            response = client.post(
                '/api/create_order',
                data=json.dumps(sample_order_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['order_id'] == 'ORD-001'
    
    def test_api_create_order_validation_error(self, client, auth_headers):
        """Test order creation with validation errors"""
        invalid_order = {
            'customer_data': {},  # Missing required fields
            'products': []  # Empty products
        }
        
        response = client.post(
            '/api/create_order',
            data=json.dumps(invalid_order),
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_sync_data(self, client, mock_veeqo_api, mock_easyship_api):
        """Test data synchronization endpoint"""
        response = client.get('/sync_data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'veeqo_warehouses' in data
        assert 'easyship_addresses' in data
    
    def test_api_dashboard_stats(self, client, auth_headers):
        """Test dashboard statistics API"""
        response = client.get('/api/dashboard-stats', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'warehouses' in data
        assert 'system_status' in data
    
    def test_api_warehouses(self, client, auth_headers):
        """Test warehouses API"""
        response = client.get('/api/warehouses', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'warehouses' in data
        assert isinstance(data['warehouses'], list)
    
    def test_api_sync_all(self, client, auth_headers, mock_veeqo_api, mock_easyship_api):
        """Test sync all API"""
        response = client.post('/api/sync-all', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert 'results' in data
    
    def test_api_test_routing(self, client, auth_headers):
        """Test routing test API"""
        test_data = {
            'city': 'Los Angeles',
            'state': 'CA',
            'country': 'US'
        }
        
        response = client.post(
            '/api/test-routing',
            data=json.dumps(test_data),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'routing_result' in data