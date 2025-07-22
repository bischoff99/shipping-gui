# Easyship API integration module
# Reuse and adapt logic from your previous scripts

import os
import requests
import json
from typing import Dict, List, Optional, Any

EASYSHIP_API_KEY = os.environ.get('EASYSHIP_API_KEY', 'prod_VC6QKi48mtqwXpXJubfmT/MsOmzTIG0Qyd89/X61ylc=')
EASYSHIP_BASE_URL = 'https://public-api.easyship.com/2024-09'

class EasyshipAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or EASYSHIP_API_KEY
        self.base_url = EASYSHIP_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def make_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Optional[Any]:
        """Make API request to Easyship"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"❌ Easyship API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Easyship Request Error: {e}")
            return None
    
    def get_addresses(self) -> List[Dict]:
        """Get all Easyship addresses/warehouses"""
        result = self.make_request('/addresses')
        return result.get('addresses', []) if result else []
    
    def get_products(self) -> List[Dict]:
        """Get Easyship products"""
        result = self.make_request('/products')
        return result.get('products', []) if result else []
    
    def get_address_by_state(self, state: str) -> Optional[Dict]:
        """Find address by state (Nevada, California, etc.)"""
        addresses = self.get_addresses()
        for address in addresses:
            address_state = address.get('state', '').lower()
            if state.lower() in address_state:
                return address
        return None
    
    def get_random_products(self, count: int = 3) -> List[Dict]:
        """Get random products for order with fallback to dummy products"""
        import random
        
        # Try to get real products first
        try:
            products = self.get_products()
            if products and len(products) >= count:
                selected_products = random.sample(products, count)
                
                # Ensure each product has required fields
                for i, product in enumerate(selected_products):
                    if not product.get('title'):
                        product['title'] = f"Fashion Item {i+1}"
                    if not product.get('price'):
                        product['price'] = random.choice([25.0, 35.0, 45.0, 55.0])
                    if not product.get('weight'):
                        product['weight'] = round(random.uniform(0.3, 1.2), 1)
                
                return selected_products
                
            # If we have some products but not enough, use what we have and add dummies
            elif products:
                selected_products = products.copy()
                needed = count - len(products)
                selected_products.extend(self._generate_dummy_products(needed, start_index=len(products)))
                return selected_products[:count]
        
        except Exception as e:
            print(f"❌ Error fetching real products, using dummy products: {e}")
        
        # Fallback to dummy products
        return self._generate_dummy_products(count)
    
    def _generate_dummy_products(self, count: int, start_index: int = 0) -> List[Dict]:
        """Generate dummy products for Easyship with realistic data"""
        import random
        
        product_names = [
            "Fashion Dress", "Designer Jeans", "Casual Shirt", "Summer Top", 
            "Winter Jacket", "Sneakers", "Handbag", "Jewelry Set",
            "Silk Scarf", "Leather Belt", "Sunglasses", "Fashion Boots",
            "Blouse", "Cardigan", "Trousers", "Skirt", "T-Shirt", "Hoodie"
        ]
        
        prices = [19.99, 25.0, 29.99, 35.0, 39.99, 45.0, 49.99, 55.0, 65.0, 75.0]
        
        dummy_products = []
        for i in range(count):
            index = start_index + i
            dummy_products.append({
                'title': f"{random.choice(product_names)} #{index + 1}",
                'price': random.choice(prices),
                'weight': round(random.uniform(0.3, 1.2), 1),  # Random weight between 0.3-1.2 kg
                'description': f'High-quality fashion item #{index + 1}',
                'category': random.choice(['Apparel', 'Accessories', 'Footwear', 'Jewelry'])
            })
        
        return dummy_products
    
    def create_shipment(self, customer_data: Dict, products: List[Dict], origin_address_id: str) -> Optional[Dict]:
        """Create Easyship shipment/order"""
        
        # Convert country code for Easyship API
        country_code = self._get_country_alpha2(customer_data.get('country', 'US'))
        
        shipment_data = {
            "origin_address_id": origin_address_id,
            "destination_address": {
                "line_1": customer_data.get('address_1', ''),
                "city": customer_data.get('city', ''),
                "postal_code": customer_data.get('postal_code', ''),
                "country_alpha2": country_code,
                "contact_name": customer_data.get('name', ''),
                "contact_phone": customer_data.get('phone', ''),
                "contact_email": customer_data.get('email', ''),
                "state": customer_data.get('state', '') if country_code == 'US' else None
            },
            "parcels": [
                {
                    "total_actual_weight": sum(float(p.get('weight', 0.5)) for p in products),
                    "box": {
                        "length": 30,
                        "width": 25,
                        "height": 15
                    },
                    "items": [
                        {
                            "description": product.get('title', 'Product'),
                            "quantity": 1,
                            "weight": float(product.get('weight', 0.5)),
                            "value": float(product.get('price', 25.0))
                        } for product in products
                    ]
                }
            ]
        }
        
        # Remove None values from destination_address
        shipment_data["destination_address"] = {k: v for k, v in shipment_data["destination_address"].items() if v is not None}
        
        return self.make_request('/shipments', 'POST', shipment_data)
    
    def _get_country_alpha2(self, country_code: str) -> str:
        """Convert country codes to alpha-2 format for Easyship"""
        country_mapping = {
            'GB': 'GB',  # United Kingdom
            'DE': 'DE',  # Germany  
            'PH': 'PH',  # Philippines
            'US': 'US',  # United States
            'UK': 'GB'   # UK -> GB conversion
        }
        return country_mapping.get(country_code.upper(), 'US')
    
    def book_fedex_rate(self, shipment_id: str) -> Optional[Dict]:
        """Book FedEx rate for shipment"""
        # Get rates first
        result = self.make_request(f'/shipments/{shipment_id}')
        if not result:
            return None
            
        rates = result.get('rates', [])
        fedex_rate = None
        
        for rate in rates:
            if 'fedex' in rate.get('courier_name', '').lower():
                fedex_rate = rate
                break
        
        if fedex_rate:
            booking_data = {"courier_id": fedex_rate.get('courier_id')}
            return self.make_request(f'/shipments/{shipment_id}/buy', 'PATCH', booking_data)
        
        return None
