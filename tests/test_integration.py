"""
Integration tests for the shipping GUI application
"""
import json
import pytest
from unittest.mock import patch, Mock
from models import db, Product, Supplier, Warehouse


class TestIntegrationFlows:
    """Test end-to-end integration flows"""
    
    def test_complete_order_creation_flow_veeqo(self, client, auth_headers, app):
        """Test complete order creation flow using Veeqo"""
        with patch('api.veeqo_api.VeeqoAPI') as mock_veeqo, \
             patch('routing.OrderRoutingSystem.route_order') as mock_routing, \
             patch('services.order_processor.OrderProcessor') as mock_processor:
            
            # Setup mocks
            mock_veeqo_instance = Mock()
            mock_veeqo_instance.get_warehouses.return_value = [
                {'id': '338489', 'name': 'Nevada Warehouse', 'region': 'NV', 'city': 'Las Vegas'}
            ]
            mock_veeqo_instance.get_random_products.return_value = [
                {'id': '1001', 'title': 'Test Product', 'sku': 'TEST-001', 'price': '19.99'}
            ]
            mock_veeqo_instance.create_order.return_value = {
                'id': 'ORDER-001',
                'status': 'created',
                'tracking_number': 'TRACK-123'
            }
            mock_veeqo.return_value = mock_veeqo_instance
            
            # Mock routing decision
            from routing import RoutingDecision
            mock_routing.return_value = RoutingDecision(
                platform='VEEQO',
                carrier='UPS',
                warehouse_info={'id': '338489', 'name': 'Nevada Warehouse'},
                confidence=95.0
            )
            
            # Mock order processor
            mock_processor_instance = Mock()
            mock_processor_instance.process_order.return_value = {
                'success': True,
                'order_id': 'ORDER-001',
                'platform': 'VEEQO',
                'tracking_info': 'TRACK-123'
            }
            mock_processor.return_value = mock_processor_instance
            
            # Step 1: Parse customer data
            customer_input = {
                "input": "John Doe\njohn@example.com\n+1-555-0123\n123 Main St\nLos Angeles, CA 90210"
            }
            
            response = client.post(
                '/api/parse_customer',
                data=json.dumps(customer_input),
                headers=auth_headers
            )
            
            assert response.status_code == 200
            customer_data = json.loads(response.data)['data']
            
            # Step 2: Get routing decision
            response = client.post(
                '/api/get_routing',
                data=json.dumps(customer_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
            routing_data = json.loads(response.data)
            assert routing_data['success'] is True
            assert routing_data['platform'] == 'VEEQO'
            
            # Step 3: Create order
            order_data = {
                'customer_data': customer_data,
                'products': [{'id': '1001', 'sku': 'TEST-001', 'quantity': 1, 'price': 19.99}],
                'routing_data': routing_data
            }
            
            response = client.post(
                '/api/create_order',
                data=json.dumps(order_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
            order_result = json.loads(response.data)
            assert order_result['success'] is True
            assert order_result['order_id'] == 'ORDER-001'
    
    def test_complete_order_creation_flow_easyship(self, client, auth_headers):
        """Test complete order creation flow using Easyship"""
        with patch('api.easyship_api.EasyshipAPI') as mock_easyship, \
             patch('routing.OrderRoutingSystem.route_order') as mock_routing, \
             patch('services.order_processor.OrderProcessor') as mock_processor:
            
            # Setup mocks for Easyship
            mock_easyship_instance = Mock()
            mock_easyship_instance.get_addresses.return_value = [
                {'id': 'addr_001', 'name': 'CA Warehouse', 'state': 'CA', 'city': 'Los Angeles'}
            ]
            mock_easyship_instance.create_shipment.return_value = {
                'id': 'SHIP-001',
                'status': 'created',
                'tracking_number': 'FEDEX-789'
            }
            mock_easyship.return_value = mock_easyship_instance
            
            # Mock routing for FedEx/Easyship
            from routing import RoutingDecision
            mock_routing.return_value = RoutingDecision(
                platform='EASYSHIP',
                carrier='FEDEX',
                warehouse_info={'id': 'addr_001', 'name': 'CA Warehouse'},
                confidence=90.0
            )
            
            # Mock order processor
            mock_processor_instance = Mock()
            mock_processor_instance.process_order.return_value = {
                'success': True,
                'order_id': 'SHIP-001',
                'platform': 'EASYSHIP',
                'tracking_info': 'FEDEX-789'
            }
            mock_processor.return_value = mock_processor_instance
            
            # Customer data for Nevada (should route to FedEx/Easyship)
            customer_data = {
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'phone': '+1-555-0456',
                'address_1': '456 Nevada St',
                'city': 'Las Vegas',
                'state': 'NV',
                'postal_code': '89101',
                'country': 'US'
            }
            
            # Test routing
            response = client.post(
                '/api/get_routing',
                data=json.dumps(customer_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
            routing_data = json.loads(response.data)
            assert routing_data['success'] is True
            assert routing_data['platform'] == 'EASYSHIP'
            
            # Test order creation
            order_data = {
                'customer_data': customer_data,
                'products': [{'id': 'prod_001', 'sku': 'ES-001', 'quantity': 2, 'price': 25.99}],
                'routing_data': routing_data
            }
            
            response = client.post(
                '/api/create_order',
                data=json.dumps(order_data),
                headers=auth_headers
            )
            
            assert response.status_code == 200
            order_result = json.loads(response.data)
            assert order_result['success'] is True
            assert order_result['platform'] == 'EASYSHIP'
    
    def test_data_sync_integration(self, client, mock_veeqo_api, mock_easyship_api):
        """Test data synchronization integration"""
        # Test sync endpoint
        response = client.get('/sync_data')
        
        assert response.status_code == 200
        sync_result = json.loads(response.data)
        assert sync_result['status'] == 'success'
        assert 'veeqo_warehouses' in sync_result
        assert 'easyship_addresses' in sync_result
        
        # Verify data was cached/stored
        # Check if warehouses.json and products.json were created
        import os
        assert os.path.exists('warehouses.json') or os.path.exists('/root/projects/SHIPPING_GUI/warehouses.json')

    def test_api_authentication_flow(self, client):
        """Test API authentication flow"""
        # Test without API key
        response = client.post(
            '/api/create_order',
            data=json.dumps({'test': 'data'}),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 401
        
        # Test with invalid API key
        response = client.post(
            '/api/create_order',
            data=json.dumps({'test': 'data'}),
            headers={
                'Authorization': 'Bearer invalid_key',
                'Content-Type': 'application/json'
            }
        )
        assert response.status_code == 401
        
        # Test with valid API key (from conftest.py)
        response = client.post(
            '/api/parse_customer',
            data=json.dumps({'input': 'test data'}),
            headers={
                'Authorization': 'Bearer test-internal-key',
                'Content-Type': 'application/json'
            }
        )
        # Should not return 401 (may return other errors due to invalid data)
        assert response.status_code != 401
    
    def test_error_handling_integration(self, client, auth_headers):
        """Test error handling across the application"""
        # Test with malformed JSON
        response = client.post(
            '/api/create_order',
            data='invalid json',
            headers=auth_headers
        )
        assert response.status_code == 400
        
        # Test with missing required fields
        response = client.post(
            '/api/create_order',
            data=json.dumps({}),
            headers=auth_headers
        )
        assert response.status_code == 400
        
        # Test 404 error
        response = client.get('/api/nonexistent_endpoint', headers=auth_headers)
        assert response.status_code == 404
    
    def test_dashboard_integration(self, client, mock_veeqo_api, mock_easyship_api):
        """Test dashboard integration with real data"""
        # Test main dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # Test enhanced dashboard
        response = client.get('/enhanced_dashboard')
        assert response.status_code == 200
        
        # Test unified dashboard
        response = client.get('/unified')
        assert response.status_code == 200
        
        # Test dashboard stats API
        response = client.get('/api/dashboard-stats')
        assert response.status_code == 200
        
        stats = json.loads(response.data)
        assert 'warehouses' in stats
        assert 'system_status' in stats
    
    def test_product_and_warehouse_integration(self, client, auth_headers, mock_veeqo_api, mock_easyship_api):
        """Test product and warehouse data integration"""
        # Test getting products from different platforms
        response = client.get('/api/get_products?platform=VEEQO&count=3', headers=auth_headers)
        assert response.status_code == 200
        
        veeqo_data = json.loads(response.data)
        assert veeqo_data['platform'] == 'VEEQO'
        assert 'products' in veeqo_data
        
        # Test Easyship products
        response = client.get('/api/get_products?platform=EASYSHIP&count=3', headers=auth_headers)
        assert response.status_code == 200
        
        easyship_data = json.loads(response.data)
        assert easyship_data['platform'] == 'EASYSHIP'
        
        # Test warehouses API
        response = client.get('/api/warehouses', headers=auth_headers)
        assert response.status_code == 200
        
        warehouses_data = json.loads(response.data)
        assert 'warehouses' in warehouses_data
    
    @patch('api.veeqo_api.VeeqoAPI')
    @patch('api.easyship_api.EasyshipAPI')
    def test_api_failure_handling(self, mock_easyship, mock_veeqo, client, auth_headers):
        """Test handling of API failures"""
        # Setup API to fail
        mock_veeqo.return_value.get_warehouses.side_effect = Exception("API Error")
        mock_easyship.return_value.get_addresses.side_effect = Exception("API Error")
        
        # Test sync with API failures
        response = client.get('/sync_data')
        assert response.status_code == 500
        
        # Test dashboard with API failures (should still work with cached data)
        response = client.get('/dashboard')
        # Should return 200 with default/cached data rather than failing
        assert response.status_code == 200
    
    def test_database_integration(self, app):
        """Test database operations integration"""
        with app.app_context():
            # Test creating related objects
            supplier = Supplier(
                name='Integration Test Supplier',
                contact_email='supplier@test.com',
                city='Test City',
                state='CA',
                country='US'
            )
            db.session.add(supplier)
            db.session.flush()
            
            warehouse = Warehouse(
                name='Integration Test Warehouse',
                address_line_1='123 Test St',
                city='Test City',
                state='CA',
                postal_code='12345',
                country='US',
                platform='both'
            )
            db.session.add(warehouse)
            db.session.flush()
            
            product = Product(
                sku='INTEGRATION-001',
                title='Integration Test Product',
                price=29.99,
                supplier_id=supplier.id,
                active=True
            )
            db.session.add(product)
            db.session.commit()
            
            # Verify relationships work
            assert product.supplier.name == 'Integration Test Supplier'
            assert len(supplier.products) == 1
    
    def test_health_check_integration(self, client):
        """Test health check endpoints integration"""
        # Test main health check
        response = client.get('/health')
        assert response.status_code in [200, 503]
        
        health_data = json.loads(response.data)
        assert 'status' in health_data
        assert 'checks' in health_data
        assert 'database' in health_data['checks']
        
        # Test readiness probe
        response = client.get('/health/ready')
        assert response.status_code in [200, 503]
        
        # Test liveness probe
        response = client.get('/health/live')
        assert response.status_code == 200