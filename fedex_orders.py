# FedEx Orders Processing Module
# Handle specific FedEx customer data and shipment creation

from typing import Dict, List, Optional
from api.easyship_api import EasyshipAPI
from utils import normalize_customer_data
import json

class FedExOrderProcessor:
    def __init__(self):
        self.easyship_api = EasyshipAPI()
        
        # Predefined FedEx customer data
        self.fedex_customers = [
            {
                "carrier": "FEDEX",
                "first_name": "Harry",
                "last_name": "Armani", 
                "phone": "447985262624",
                "email": "harrycarmani@googlemail.com",
                "name": "Harry Armani",
                "address_1": "2 Merestone Court",
                "address_2": "Merestone Road",
                "city": "Birmingham",
                "state": "Westmidlands", 
                "postal_code": "B32 2UG",
                "country": "GB"
            },
            {
                "carrier": "FEDEX",
                "first_name": "Adrian",
                "last_name": "Naujok",
                "phone": "491634528373", 
                "email": "purchiwosumonc3m@mail.com",
                "name": "Adrian Naujok",
                "address_1": "Buchenweg 8",
                "address_2": "",
                "city": "Göttingen",
                "state": "Niedersachsen",
                "postal_code": "37079", 
                "country": "DE"
            },
            {
                "carrier": "FEDEX",
                "first_name": "Jojet",
                "last_name": "Gamboa",
                "phone": "639691645226",
                "email": "embreikz123@gmail.com", 
                "name": "Jojet Gamboa",
                "address_1": "RSJF Apartelle B. Viscarra St Pasay City, Manila",
                "address_2": "",
                "city": "Pasay",
                "state": "Manila",
                "postal_code": "1302",
                "country": "PH"
            },
            {
                "carrier": "FEDEX", 
                "first_name": "Rainielle",
                "last_name": "Natividad",
                "phone": "639623385091",
                "email": "embreikz123@gmail.com",
                "name": "Rainielle Natividad", 
                "address_1": "Block 28 Lot 31 Phase 1 San Isidro Heights",
                "address_2": "",
                "city": "Cabuyao City",
                "state": "Laguna",
                "postal_code": "4025",
                "country": "PH"
            },
            {
                "carrier": "FEDEX",
                "first_name": "Katherine Carol", 
                "last_name": "Rivera",
                "phone": "639270437267",
                "email": "embreikz123@gmail.com",
                "name": "Katherine Carol Rivera",
                "address_1": "241 Blk 1 Lot 15 Mandarin St, Pag asa 1, Aguado", 
                "address_2": "",
                "city": "Trece Martires",
                "state": "Cavite",
                "postal_code": "4109",
                "country": "PH"
            },
            {
                "carrier": "FEDEX",
                "first_name": "Samson",
                "last_name": "Padilla",
                "phone": "639690391761",
                "email": "embreikz123@gmail.com",
                "name": "Samson Padilla",
                "address_1": "170 GSIS, Ampid 1, Zone 12, San Mateo, Rizal",
                "address_2": "",
                "city": "San Mateo", 
                "state": "Rizal",
                "postal_code": "1850",
                "country": "PH"
            },
            {
                "carrier": "FEDEX",
                "first_name": "King Louise",
                "last_name": "Rj",
                "phone": "639603497928", 
                "email": "embreikz123@gmail.com",
                "name": "King Louise Rj",
                "address_1": "E1 J. Martin St. Pasolo Valenzuela City",
                "address_2": "",
                "city": "Valenzuela",
                "state": "NCR",
                "postal_code": "1444",
                "country": "PH"
            }
        ]
    
    def get_fedex_customers(self) -> List[Dict]:
        """Get all predefined FedEx customers"""
        return self.fedex_customers
    
    def get_fedex_customer_by_name(self, name: str) -> Optional[Dict]:
        """Get specific FedEx customer by name"""
        for customer in self.fedex_customers:
            if customer['name'].lower() == name.lower():
                return customer
        return None
    
    def create_fedex_shipment(self, customer_data: Dict, origin_address_id: str = None) -> Optional[Dict]:
        """Create FedEx shipment through Easyship"""
        
        # Get origin address if not provided
        if not origin_address_id:
            addresses = self.easyship_api.get_addresses()
            if addresses:
                # Use first available sender address
                for addr in addresses:
                    if addr.get('default_for', {}).get('sender', False):
                        origin_address_id = addr.get('id')
                        break
                if not origin_address_id and addresses:
                    origin_address_id = addresses[0].get('id')
        
        if not origin_address_id:
            print("❌ No origin address available for FedEx shipment")
            return None
        
        # Get some products for the shipment
        products = self.easyship_api.get_random_products(2)
        if not products:
            print(f"⚠️ No products available, using fallback products for {customer_data.get('name')}")
            # Fallback products - this shouldn't happen with improved get_random_products
            products = [
                {
                    'title': 'Premium Fashion Item',
                    'weight': 0.5,
                    'price': 35.00,
                    'description': 'High-quality fashion apparel'
                },
                {
                    'title': 'Designer Accessory', 
                    'weight': 0.3,
                    'price': 20.00,
                    'description': 'Elegant fashion accessory'
                }
            ]
        
        # Format customer data for Easyship
        formatted_customer = normalize_customer_data({
            'name': customer_data.get('name', ''),
            'address_1': customer_data.get('address_1', ''),
            'city': customer_data.get('city', ''),
            'postal_code': customer_data.get('postal_code', ''),
            'country': customer_data.get('country', 'US'),
            'phone': customer_data.get('phone', ''),
            'email': customer_data.get('email', '')
        })
        
        # Create shipment
        result = self.easyship_api.create_shipment(formatted_customer, products, origin_address_id)
        
        if result:
            shipment_id = result.get('shipment', {}).get('id')
            if shipment_id:
                # Try to book FedEx rate
                fedex_booking = self.easyship_api.book_fedex_rate(shipment_id)
                if fedex_booking:
                    print(f"✅ FedEx shipment created and booked for {customer_data.get('name')}")
                    return {'shipment': result, 'booking': fedex_booking}
                else:
                    print(f"⚠️ FedEx shipment created but booking failed for {customer_data.get('name')}")
                    return {'shipment': result, 'booking': None}
        
        print(f"❌ Failed to create FedEx shipment for {customer_data.get('name')}")
        return None
    
    def process_all_fedex_orders(self) -> List[Dict]:
        """Process all predefined FedEx customers"""
        results = []
        
        print(f"🚀 Processing {len(self.fedex_customers)} FedEx orders...")
        
        for customer in self.fedex_customers:
            print(f"Processing order for {customer['name']}...")
            result = self.create_fedex_shipment(customer)
            results.append({
                'customer': customer,
                'result': result,
                'success': result is not None
            })
        
        successful = sum(1 for r in results if r['success'])
        print(f"✅ Processed {successful}/{len(results)} FedEx orders successfully")
        
        return results
    
    def get_fedex_customer_summary(self) -> Dict:
        """Get summary of FedEx customers by country"""
        summary = {}
        for customer in self.fedex_customers:
            country = customer['country']
            if country not in summary:
                summary[country] = []
            summary[country].append(customer['name'])
        
        return summary
