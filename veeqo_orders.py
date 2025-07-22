# Veeqo Orders Processing Module
# Handle UPS and DHL orders that should be routed through Veeqo based on state preferences

from typing import Dict, List, Optional
from api.veeqo_api import VeeqoAPI
from utils import normalize_customer_data
import json

class VeeqoOrderProcessor:
    def __init__(self):
        self.veeqo_api = VeeqoAPI()
        
        # Predefined Veeqo customer data (UPS and DHL orders based on state preferences)
        self.veeqo_customers = [
            {
                "state_preference": "Nevada",
                "carrier": "UPS",
                "first_name": "Michael",
                "last_name": "Donagh",
                "phone": "447950846699",
                "email": "donagh.michael@gmail.com",
                "name": "Michael Donagh",
                "address_1": "8 Oak Mount Lane",
                "address_2": "",
                "city": "Birmingham",
                "state": "West Midlands",
                "postal_code": "B31 5HL",
                "country": "GB"
            },
            {
                "state_preference": "Nevada",
                "carrier": "DHL",
                "first_name": "Michael",
                "last_name": "Cregan",
                "phone": "353876888888",
                "email": "michaelcregan76@gmail.com",
                "name": "Michael Cregan",
                "address_1": "3 The Court",
                "address_2": "Crosbie Gardens",
                "city": "Dun Laoghaire",
                "state": "Dublin",
                "postal_code": "A96 D2N0",
                "country": "IE"
            },
            {
                "state_preference": "Nevada",
                "carrier": "UPS",
                "first_name": "John",
                "last_name": "Doyle",
                "phone": "353863857799",
                "email": "johndoyle@gmail.com",
                "name": "John Doyle",
                "address_1": "45 Abbey Street",
                "address_2": "",
                "city": "Dublin",
                "state": "Dublin",
                "postal_code": "D01 K5P2",
                "country": "IE"
            },
            {
                "state_preference": "California",
                "carrier": "DHL",
                "first_name": "Robert",
                "last_name": "Williams",
                "phone": "447123456789",
                "email": "rob.williams@email.com",
                "name": "Robert Williams",
                "address_1": "12 High Street",
                "address_2": "",
                "city": "Manchester",
                "state": "Greater Manchester",
                "postal_code": "M1 1AA",
                "country": "GB"
            },
            {
                "state_preference": "Florida",
                "carrier": "UPS",
                "first_name": "James",
                "last_name": "Smith",
                "phone": "447987654321",
                "email": "james.smith@email.com",
                "name": "James Smith",
                "address_1": "78 Queen Street",
                "address_2": "Apt 4",
                "city": "Liverpool",
                "state": "Merseyside",
                "postal_code": "L1 4AA",
                "country": "GB"
            },
            {
                "state_preference": "California",
                "carrier": "DHL",
                "first_name": "David",
                "last_name": "Brown",
                "phone": "447456789123",
                "email": "david.brown@email.com",
                "name": "David Brown",
                "address_1": "32 Victoria Road",
                "address_2": "",
                "city": "Leeds",
                "state": "West Yorkshire",
                "postal_code": "LS1 4BR",
                "country": "GB"
            },
            {
                "state_preference": "California",
                "carrier": "DHL",
                "first_name": "Paul",
                "last_name": "Wilson",
                "phone": "447321654987",
                "email": "paul.wilson@email.com",
                "name": "Paul Wilson",
                "address_1": "89 Church Lane",
                "address_2": "",
                "city": "Bristol",
                "state": "Bristol",
                "postal_code": "BS1 5DF",
                "country": "GB"
            },
            {
                "state_preference": "Florida",
                "carrier": "UPS",
                "first_name": "Andrew",
                "last_name": "Foster",
                "phone": "447654321098",
                "email": "andrew.foster@email.com",
                "name": "Andrew Foster",
                "address_1": "67 Park Avenue",
                "address_2": "Flat 2",
                "city": "Newcastle",
                "state": "Tyne and Wear",
                "postal_code": "NE1 4ST",
                "country": "GB"
            }
        ]
    
    def get_veeqo_customers(self) -> List[Dict]:
        """Get all predefined Veeqo customers"""
        return self.veeqo_customers
    
    def get_veeqo_customer_by_name(self, name: str) -> Optional[Dict]:
        """Get specific Veeqo customer by name"""
        for customer in self.veeqo_customers:
            if customer['name'].lower() == name.lower():
                return customer
        return None
    
    def get_customers_by_state_preference(self, state: str) -> List[Dict]:
        """Get customers filtered by state preference"""
        return [c for c in self.veeqo_customers if c['state_preference'].lower() == state.lower()]
    
    def get_customers_by_carrier(self, carrier: str) -> List[Dict]:
        """Get customers filtered by carrier"""
        return [c for c in self.veeqo_customers if c['carrier'].upper() == carrier.upper()]
    
    def create_veeqo_order(self, customer_data: Dict, warehouse_id: int = None) -> Optional[Dict]:
        """Create Veeqo order for customer"""
        
        # Get warehouse based on state preference
        if not warehouse_id:
            state_pref = customer_data.get('state_preference', 'Nevada')
            if state_pref.lower() == 'nevada':
                warehouse = self.veeqo_api.get_warehouse_by_state('Nevada')
            elif state_pref.lower() == 'california':
                warehouse = self.veeqo_api.get_warehouse_by_state('California')
            else:
                # Default to Nevada or California
                warehouse = self.veeqo_api.get_warehouse_by_state('Nevada') or self.veeqo_api.get_warehouse_by_state('California')
            
            if warehouse:
                warehouse_id = warehouse.get('id')
            else:
                print(f"❌ No suitable warehouse found for {customer_data.get('name')}")
                return None
        
        # Get some products for the order
        products = self.veeqo_api.get_random_products(3)
        if not products:
            print(f"⚠️ No products available, using fallback products for {customer_data.get('name')}")
            # Fallback products - this shouldn't happen with improved get_random_products
            products = [
                {
                    'id': 'fallback_1',
                    'title': 'Premium Fashion Item',
                    'price': '35.00',
                    'description': 'High-quality fashion apparel'
                },
                {
                    'id': 'fallback_2',
                    'title': 'Designer Accessory', 
                    'price': '25.00',
                    'description': 'Elegant fashion accessory'
                },
                {
                    'id': 'fallback_3',
                    'title': 'Luxury Fashion Piece',
                    'price': '45.00',
                    'description': 'Premium fashion item'
                }
            ]
        
        # Format customer data for Veeqo
        formatted_customer = normalize_customer_data({
            'name': customer_data.get('name', ''),
            'address_1': customer_data.get('address_1', ''),
            'city': customer_data.get('city', ''),
            'state': customer_data.get('state', ''),
            'postal_code': customer_data.get('postal_code', ''),
            'country': self._get_country_code_for_veeqo(customer_data.get('country', 'US')),
            'phone': customer_data.get('phone', ''),
            'email': customer_data.get('email', '')
        })
        
        # Create order
        carrier = customer_data.get('carrier', 'UPS')
        result = self.veeqo_api.create_order(formatted_customer, products, warehouse_id, carrier)
        
        if result:
            print(f"✅ Veeqo {carrier} order created for {customer_data.get('name')}")
            return result
        else:
            print(f"❌ Failed to create Veeqo order for {customer_data.get('name')}")
            return None
    
    def _get_country_code_for_veeqo(self, country_code: str) -> str:
        """Convert country codes to format expected by Veeqo"""
        country_mapping = {
            'GB': 'GB',  # United Kingdom
            'IE': 'IE',  # Ireland
            'US': 'US',  # United States
            'UK': 'GB'   # UK -> GB conversion
        }
        return country_mapping.get(country_code.upper(), 'US')
    
    def process_all_veeqo_orders(self) -> List[Dict]:
        """Process all predefined Veeqo customers"""
        results = []
        
        print(f"🚀 Processing {len(self.veeqo_customers)} Veeqo orders...")
        
        for customer in self.veeqo_customers:
            print(f"Processing {customer['carrier']} order for {customer['name']} (State pref: {customer['state_preference']})...")
            result = self.create_veeqo_order(customer)
            results.append({
                'customer': customer,
                'result': result,
                'success': result is not None
            })
        
        successful = sum(1 for r in results if r['success'])
        print(f"✅ Processed {successful}/{len(results)} Veeqo orders successfully")
        
        return results
    
    def get_veeqo_customer_summary(self) -> Dict:
        """Get summary of Veeqo customers by state preference and carrier"""
        summary = {
            'by_state': {},
            'by_carrier': {},
            'by_country': {}
        }
        
        for customer in self.veeqo_customers:
            # By state preference
            state = customer['state_preference']
            if state not in summary['by_state']:
                summary['by_state'][state] = []
            summary['by_state'][state].append(customer['name'])
            
            # By carrier
            carrier = customer['carrier']
            if carrier not in summary['by_carrier']:
                summary['by_carrier'][carrier] = []
            summary['by_carrier'][carrier].append(customer['name'])
            
            # By country
            country = customer['country']
            if country not in summary['by_country']:
                summary['by_country'][country] = []
            summary['by_country'][country].append(customer['name'])
        
        return summary
    
    def get_purchase_orders(self) -> List[Dict]:
        """Get Veeqo purchase orders using the API"""
        try:
            purchase_orders = self.veeqo_api.get_purchase_orders()
            return purchase_orders if purchase_orders else []
        except Exception as e:
            print(f"❌ Error fetching purchase orders: {e}")
            return []
