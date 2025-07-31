"""
Test routing system functionality
"""
import pytest
from routing import OrderRoutingSystem, RoutingDecision


class TestOrderRoutingSystem:
    """Test order routing system"""
    
    def setup_method(self):
        """Set up test data"""
        self.routing_system = OrderRoutingSystem()
        
        self.sample_warehouses = [
            {
                'id': '338489',
                'name': 'Nevada Warehouse',
                'state': 'NV',
                'city': 'Las Vegas',
                'country': 'US'
            },
            {
                'id': '338491',
                'name': 'California Warehouse',
                'state': 'CA',
                'city': 'Los Angeles',
                'country': 'US'
            }
        ]
    
    def test_routing_decision_creation(self):
        """Test RoutingDecision creation"""
        warehouse_info = {'id': '123', 'name': 'Test Warehouse'}
        decision = RoutingDecision(
            platform='VEEQO',
            carrier='UPS',
            warehouse_info=warehouse_info,
            confidence=85.0
        )
        
        assert decision.platform == 'VEEQO'
        assert decision.carrier == 'UPS'
        assert decision.warehouse_info == warehouse_info
        assert decision.confidence == 85.0
    
    def test_carrier_platform_mapping(self):
        """Test carrier to platform mapping"""
        assert self.routing_system.get_platform_for_carrier('FEDEX') == 'EASYSHIP'
        assert self.routing_system.get_platform_for_carrier('UPS') == 'VEEQO'
        assert self.routing_system.get_platform_for_carrier('DHL') == 'VEEQO'
        assert self.routing_system.get_platform_for_carrier('USPS') == 'VEEQO'
        assert self.routing_system.get_platform_for_carrier('UNKNOWN') == 'VEEQO'  # Default
    
    def test_get_carrier_options(self):
        """Test getting available carrier options"""
        carriers = self.routing_system.get_carrier_options()
        expected_carriers = ['FEDEX', 'UPS', 'DHL', 'USPS']
        
        assert all(carrier in carriers for carrier in expected_carriers)
        assert len(carriers) == len(expected_carriers)
    
    def test_route_order_nevada_customer(self):
        """Test routing for Nevada customer"""
        customer_data = {
            'name': 'John Doe',
            'state': 'NEVADA',
            'city': 'Las Vegas',
            'country': 'US'
        }
        
        decision = self.routing_system.route_order(customer_data, self.sample_warehouses)
        
        assert isinstance(decision, RoutingDecision)
        assert decision.carrier in ['FEDEX', 'UPS']  # Nevada preferences
        assert decision.confidence > 0
    
    def test_route_order_california_customer(self):
        """Test routing for California customer"""
        customer_data = {
            'name': 'Jane Smith',
            'state': 'CALIFORNIA',
            'city': 'Los Angeles',
            'country': 'US'
        }
        
        decision = self.routing_system.route_order(customer_data, self.sample_warehouses)
        
        assert isinstance(decision, RoutingDecision)
        assert decision.carrier in ['DHL', 'UPS']  # California preferences
        assert decision.platform in ['VEEQO', 'EASYSHIP']
    
    def test_route_order_unknown_state(self):
        """Test routing for customer from unknown state"""
        customer_data = {
            'name': 'Bob Johnson',
            'state': 'UNKNOWN_STATE',
            'city': 'Unknown City',
            'country': 'US'
        }
        
        decision = self.routing_system.route_order(customer_data, self.sample_warehouses)
        
        assert isinstance(decision, RoutingDecision)
        assert decision.carrier == 'UPS'  # Default carrier
        assert decision.platform == 'VEEQO'  # UPS maps to VEEQO
    
    def test_select_optimal_warehouse_nevada_priority(self):
        """Test warehouse selection with Nevada priority"""
        customer_data = {
            'address': {
                'state': 'NV',
                'city': 'Las Vegas'
            }
        }
        
        warehouse_info, routing_reason = self.routing_system.select_optimal_warehouse(customer_data)
        
        assert isinstance(warehouse_info, dict)
        assert 'veeqo_id' in warehouse_info
        assert 'routing_reason' in routing_reason or routing_reason
    
    def test_select_optimal_warehouse_california_priority(self):
        """Test warehouse selection with California priority"""
        customer_data = {
            'address': {
                'state': 'CA',
                'city': 'Los Angeles'
            }
        }
        
        warehouse_info, routing_reason = self.routing_system.select_optimal_warehouse(customer_data)
        
        assert isinstance(warehouse_info, dict)
        assert routing_reason  # Should have a reason
    
    def test_select_optimal_warehouse_eastern_states(self):
        """Test warehouse selection for eastern states"""
        customer_data = {
            'address': {
                'state': 'NY',
                'city': 'New York'
            }
        }
        
        warehouse_info, routing_reason = self.routing_system.select_optimal_warehouse(customer_data)
        
        assert isinstance(warehouse_info, dict)
        assert 'Eastern States' in routing_reason
    
    def test_find_optimal_warehouse(self):
        """Test find optimal warehouse wrapper method"""
        customer_data = {
            'address': {
                'state': 'CA',
                'city': 'San Francisco'
            }
        }
        
        warehouse_info = self.routing_system.find_optimal_warehouse(customer_data)
        
        assert isinstance(warehouse_info, dict)
        assert 'routing_reason' in warehouse_info
    
    def test_warehouse_mappings_loading(self):
        """Test warehouse mappings loading"""
        mappings = self.routing_system.get_warehouse_mappings()
        
        assert isinstance(mappings, dict)
        # Should at least have fallback warehouses
        assert len(mappings) > 0
        
        # Test fallback warehouse structure
        for warehouse_id, warehouse_info in mappings.items():
            assert 'name' in warehouse_info
            assert 'state' in warehouse_info
            assert 'city' in warehouse_info
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        # Complete customer data should have high confidence
        complete_customer = {
            'name': 'John Doe',
            'phone': '+1-555-0123',
            'email': 'john@example.com',
            'address_1': '123 Main St',
            'postal_code': '90210',
            'state': 'CA'
        }
        
        warehouse = {'id': '123', 'name': 'Test Warehouse'}
        decision = self.routing_system.route_order(complete_customer, self.sample_warehouses)
        
        # Should have high confidence with complete data
        assert decision.confidence >= 80.0
        
        # Incomplete customer data should have lower confidence
        incomplete_customer = {
            'name': 'Jane Doe',
            'state': 'CA'
        }
        
        decision_incomplete = self.routing_system.route_order(incomplete_customer, self.sample_warehouses)
        assert decision_incomplete.confidence < decision.confidence
    
    def test_empty_warehouses_handling(self):
        """Test handling of empty warehouses list"""
        customer_data = {
            'name': 'Test Customer',
            'state': 'CA'
        }
        
        decision = self.routing_system.route_order(customer_data, [])
        
        assert isinstance(decision, RoutingDecision)
        # Should still return a decision even with empty warehouses
        assert decision.platform in ['VEEQO', 'EASYSHIP']
        assert decision.carrier in ['FEDEX', 'UPS', 'DHL', 'USPS']