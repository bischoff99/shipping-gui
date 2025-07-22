# Routing logic module
# Reuse CarrierBasedRoutingSystem and related logic

from typing import Dict, List, Optional, Tuple
import random

class RoutingDecision:
    def __init__(self, platform: str, carrier: str, warehouse_info: Dict, confidence: float = 0.0):
        self.platform = platform  # 'VEEQO' or 'EASYSHIP'
        self.carrier = carrier    # 'FEDEX', 'UPS', 'DHL', 'USPS'
        self.warehouse_info = warehouse_info
        self.confidence = confidence

class OrderRoutingSystem:
    def __init__(self):
        # Routing rules based on your existing logic
        self.carrier_platform_mapping = {
            'FEDEX': 'EASYSHIP',
            'UPS': 'VEEQO',
            'DHL': 'VEEQO',
            'USPS': 'VEEQO'
        }
        
        # State-based carrier preferences (from your scripts)
        self.state_carrier_preferences = {
            'NEVADA': ['FEDEX', 'UPS'],
            'CALIFORNIA': ['DHL', 'UPS'],
            'NEW YORK': ['UPS', 'DHL'],
            'FLORIDA': ['USPS', 'UPS'],
            'TEXAS': ['UPS', 'FEDEX']
        }
    
    def route_order(self, customer_data: Dict, available_warehouses: List[Dict]) -> RoutingDecision:
        """Main routing logic - decide platform and carrier"""
        
        # 1. Determine best carrier based on destination
        destination_state = customer_data.get('state', '').upper()
        preferred_carriers = self.state_carrier_preferences.get(destination_state, ['UPS'])
        selected_carrier = preferred_carriers[0]  # Take first preference
        
        # 2. Determine platform based on carrier
        platform = self.carrier_platform_mapping.get(selected_carrier, 'VEEQO')
        
        # 3. Find best warehouse (Nevada, California preference)
        warehouse = self._select_warehouse(customer_data, available_warehouses)
        
        # 4. Calculate confidence score
        confidence = self._calculate_confidence(customer_data, selected_carrier, warehouse)
        
        return RoutingDecision(platform, selected_carrier, warehouse, confidence)
    
    def _select_warehouse(self, customer_data: Dict, warehouses: List[Dict]) -> Dict:
        """Select best warehouse for order"""
        customer_state = customer_data.get('state', '').upper()
        
        # Priority: same state > nearby states > random
        for warehouse in warehouses:
            warehouse_state = warehouse.get('region', '').upper()
            if customer_state in warehouse_state:
                return warehouse
        
        # Look for Nevada or California warehouses (your preferences)
        priority_states = ['NEVADA', 'CALIFORNIA']
        for state in priority_states:
            for warehouse in warehouses:
                warehouse_state = warehouse.get('region', '').upper()
                if state in warehouse_state:
                    return warehouse
        
        # Random selection if no good match
        return random.choice(warehouses) if warehouses else {}
    
    def _calculate_confidence(self, customer_data: Dict, carrier: str, warehouse: Dict) -> float:
        """Calculate routing confidence score"""
        score = 50.0  # Base score
        
        # Higher confidence for complete customer data
        if customer_data.get('phone'): score += 10
        if customer_data.get('email'): score += 10
        if customer_data.get('address_1'): score += 15
        if customer_data.get('postal_code'): score += 10
        
        # Higher confidence for warehouse match
        if warehouse:
            score += 20
        
        # Carrier-specific adjustments
        if carrier == 'FEDEX': score += 5  # FedEx generally reliable
        
        return min(score, 100.0)
    
    def get_carrier_options(self) -> List[str]:
        """Get available carriers"""
        return list(self.carrier_platform_mapping.keys())
    
    def get_platform_for_carrier(self, carrier: str) -> str:
        """Get platform for specific carrier"""
        return self.carrier_platform_mapping.get(carrier.upper(), 'VEEQO')
