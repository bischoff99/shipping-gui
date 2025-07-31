"""
Routing logic for Unified Order & Warehouse Management System.

Provides order routing logic, carrier/platform selection, and warehouse matching.

Classes:
    RoutingDecision: Represents a routing decision for an order.
    OrderRoutingSystem: Main routing logic for orders.

Typical usage example:
    router = OrderRoutingSystem()
    decision = router.route_order(customer_data, warehouses)
"""

from typing import Dict, List, Tuple
import random


class RoutingDecision:
    def __init__(
        self,
        platform: str,
        carrier: str,
        warehouse_info: Dict,
        confidence: float = 0.0,
    ):
        """Initialize a routing decision.

        Args:
            platform (str): The platform for the order, e.g., 'VEEQO' or 'EASYSHIP'.
            carrier (str): The carrier for the order, e.g., 'FEDEX', 'UPS', 'DHL', 'USPS'.
            warehouse_info (Dict): Information about the selected warehouse.
            confidence (float, optional): Confidence score for the routing decision. Defaults to 0.0.
        """
        self.platform = platform  # 'VEEQO' or 'EASYSHIP'
        self.carrier = carrier  # 'FEDEX', 'UPS', 'DHL', 'USPS'
        self.warehouse_info = warehouse_info
        self.confidence = confidence


class OrderRoutingSystem:
    def __init__(self):
        """Initialize the order routing system with default carrier/platform mappings
        and state-based carrier preferences.
        """
        # Routing rules based on your existing logic
        self.carrier_platform_mapping = {
            "FEDEX": "EASYSHIP",
            "UPS": "VEEQO",
            "DHL": "VEEQO",
            "USPS": "VEEQO",
        }

        # State-based carrier preferences (from your scripts)
        self.state_carrier_preferences = {
            "NEVADA": ["FEDEX", "UPS"],
            "CALIFORNIA": ["DHL", "UPS"],
            "NEW YORK": ["UPS", "DHL"],
            "FLORIDA": ["USPS", "UPS"],
            "TEXAS": ["UPS", "FEDEX"],
        }

    def route_order(
        self, customer_data: Dict, available_warehouses: List[Dict]
    ) -> RoutingDecision:
        """Main routing logic - decide platform and carrier

        Args:
            customer_data (Dict): Information about the customer and order.
            available_warehouses (List[Dict]): List of available warehouses for fulfillment.

        Returns:
            RoutingDecision: The routing decision including platform, carrier, warehouse info, and confidence score.
        """

        # 1. Determine best carrier based on destination
        destination_state = customer_data.get("state", "").upper()
        preferred_carriers = self.state_carrier_preferences.get(
            destination_state, ["UPS"]
        )
        selected_carrier = preferred_carriers[0]  # Take first preference

        # 2. Determine platform based on carrier
        platform = self.carrier_platform_mapping.get(selected_carrier, "VEEQO")

        # 3. Find best warehouse (Nevada, California preference)
        # Convert warehouse dictionaries to proper format
        available_warehouse_objects = []
        for warehouse in available_warehouses:
            if isinstance(warehouse, dict):
                # Extract ID and convert to proper format
                wh_id = warehouse.get('id')
                if wh_id:
                    available_warehouse_objects.append({
                        "id": str(wh_id),
                        "name": warehouse.get('name', f'Warehouse {wh_id}'),
                        "state": warehouse.get('region', ''),
                        "city": warehouse.get('city', ''),
                        "country": warehouse.get('country', 'US')
                    })
        
        warehouse = self._select_warehouse(customer_data, available_warehouse_objects)

        # 4. Calculate confidence score
        confidence = self._calculate_confidence(
            customer_data, selected_carrier, warehouse
        )

        return RoutingDecision(platform, selected_carrier, warehouse, confidence)

    def select_optimal_warehouse(self, customer_data: Dict) -> Tuple[Dict, str]:
        """Select optimal warehouse based on customer location using smart routing logic.

        Args:
            customer_data (Dict): Customer data including address information

        Returns:
            Tuple[Dict, str]: (warehouse_info, routing_reason)
        """
        customer_state = customer_data.get("address", {}).get("state", "CA")

        # Smart routing logic from GUI components
        if customer_state in ["NV", "UT", "AZ", "CO"]:
            preferred_states = ["NV", "CA", "DE"]
            routing_reason = "Western States → Nevada Priority"
        elif customer_state in ["CA", "OR", "WA"]:
            preferred_states = ["CA", "NV", "DE"]
            routing_reason = "Pacific States → California Priority"
        elif customer_state in ["DE", "MD", "VA", "NJ", "NY"]:
            preferred_states = ["DE", "CA", "NV"]
            routing_reason = "Eastern States → Delaware Priority"
        else:
            preferred_states = ["CA", "NV", "DE"]
            routing_reason = "General → Any Available Warehouse"

        # Get warehouse mappings (this would normally come from database or
        # config)
        warehouse_mappings = self.get_warehouse_mappings()

        # Find best warehouse by preferred state order
        for preferred_state in preferred_states:
            for warehouse_id, warehouse_info in warehouse_mappings.items():
                if warehouse_info.get("state") == preferred_state:
                    return {
                        "veeqo_id": warehouse_id,
                        "easyship_id": warehouse_info.get("easyship_id"),
                        "name": warehouse_info.get("name"),
                        "state": warehouse_info.get("state"),
                        "city": warehouse_info.get("city", "Unknown"),
                    }, routing_reason

        # Fallback - return first available warehouse
        if warehouse_mappings:
            first_warehouse = next(iter(warehouse_mappings.items()))
            warehouse_id, warehouse_info = first_warehouse
            return {
                "veeqo_id": warehouse_id,
                "easyship_id": warehouse_info.get("easyship_id"),
                "name": warehouse_info.get("name"),
                "state": warehouse_info.get("state"),
                "city": warehouse_info.get("city", "Unknown"),
            }, "Fallback → First Available Warehouse"

        # Ultimate fallback
        return {
            "veeqo_id": "default",
            "name": "Default Warehouse",
            "state": "CA",
            "city": "Los Angeles",
        }, "Default Warehouse"

    def get_warehouse_mappings(self) -> Dict:
        """Get warehouse mappings from real warehouses.json data"""
        # Load real warehouse mappings from warehouses.json
        try:
            import json
            with open("warehouses.json", "r") as f:
                warehouse_data = json.load(f)
            
            # Convert real data to routing format
            mappings = {}
            
            # Add Veeqo warehouses
            for warehouse in warehouse_data.get("veeqo", []):
                mappings[str(warehouse["id"])] = {
                    "name": warehouse["name"],
                    "state": warehouse["region"],
                    "city": warehouse["city"],
                    "country": warehouse["country"],
                    "easyship_id": None,  # Will be mapped separately
                }
            
            return mappings
            
        except Exception as e:
            # Fallback to key warehouses if file loading fails
            return {
                "338489": {
                    "name": "Third and Arrow - Downtown Container Park",
                    "state": "NV",
                    "city": "Las Vegas",
                    "country": "US",
                    "easyship_id": None,
                },
                "338491": {
                    "name": "Oak and Fort",
                    "state": "CA", 
                    "city": "Los Angeles",
                    "country": "US",
                    "easyship_id": None,
                },
                "321377": {
                    "name": "Thrivz",
                    "state": "DE",
                    "city": "Dover",
                    "country": "US",
                    "easyship_id": None,
                },
            }

    def find_optimal_warehouse(self, customer_data: Dict) -> Dict:
        """Find optimal warehouse for customer - wrapper for backward compatibility"""
        warehouse_info, routing_reason = self.select_optimal_warehouse(customer_data)
        warehouse_info["routing_reason"] = routing_reason
        return warehouse_info

    def _select_warehouse(self, customer_data: Dict, warehouses: List[Dict]) -> Dict:
        """Select best warehouse for order (legacy method)

        Args:
            customer_data (Dict): Information about the customer and order.
            warehouses (List[Dict]): List of available warehouses for fulfillment.

        Returns:
            Dict: The selected warehouse for the order.
        """
        customer_state = customer_data.get("state", "").upper()

        # Priority: same state > nearby states > random
        for warehouse in warehouses:
            warehouse_state = warehouse.get("state", "").upper()
            if customer_state in warehouse_state:
                return warehouse

        # Look for Nevada or California warehouses (your preferences)
        priority_states = ["NV", "CA", "NEVADA", "CALIFORNIA"]
        for state in priority_states:
            for warehouse in warehouses:
                warehouse_state = warehouse.get("state", "").upper()
                if state in warehouse_state:
                    return warehouse

        # Random selection if no good match
        return random.choice(warehouses) if warehouses else {}

    def _calculate_confidence(
        self, customer_data: Dict, carrier: str, warehouse: Dict
    ) -> float:
        """Calculate routing confidence score

        Args:
            customer_data (Dict): Information about the customer and order.
            carrier (str): The carrier for the order.
            warehouse (Dict): Information about the selected warehouse.

        Returns:
            float: The confidence score for the routing decision.
        """
        score = 50.0  # Base score

        # Higher confidence for complete customer data
        if customer_data.get("phone"):
            score += 10
        if customer_data.get("email"):
            score += 10
        if customer_data.get("address_1"):
            score += 15
        if customer_data.get("postal_code"):
            score += 10

        # Higher confidence for warehouse match
        if warehouse:
            score += 20

        # Carrier-specific adjustments
        if carrier == "FEDEX":
            score += 5  # FedEx generally reliable

        return min(score, 100.0)

    def get_carrier_options(self) -> List[str]:
        """Get available carriers

        Returns:
            List[str]: List of available carriers.
        """
        return list(self.carrier_platform_mapping.keys())

    def get_platform_for_carrier(self, carrier: str) -> str:
        """Get platform for specific carrier

        Args:
            carrier (str): The carrier for which to get the platform.

        Returns:
            str: The platform for the specified carrier.
        """
        return self.carrier_platform_mapping.get(carrier.upper(), "VEEQO")
