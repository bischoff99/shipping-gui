# FedEx Orders Processing Module
# Handle specific FedEx customer data and shipment creation

import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
from api.easyship_api import EasyshipAPI
from utils import normalize_customer_data
from models import db, Order
from services.csv_integration import CSVProcessor


class FedExOrderProcessor:
    def __init__(self):
        self.easyship_api = EasyshipAPI()
        self.csv_processor = CSVProcessor(db.session)

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
                "country": "GB",
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
                "country": "DE",
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
                "country": "PH",
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
                "country": "PH",
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
                "country": "PH",
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
                "country": "PH",
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
                "country": "PH",
            },
        ]

    def get_fedex_customers(self) -> List[Dict]:
        """Get all predefined FedEx customers"""
        return self.fedex_customers

    def get_fedex_customer_by_name(self, name: str) -> Optional[Dict]:
        """Get specific FedEx customer by name"""
        for customer in self.fedex_customers:
            if customer["name"].lower() == name.lower():
                return customer
        return None

    def create_fedex_shipment(
        self, customer_data: Dict, origin_address_id: str = None
    ) -> Optional[Dict]:
        """Create FedEx shipment through Easyship"""
        
        # DEBUG BREAKPOINT 1: Inspect initial customer_data
        print(f"🔍 DEBUG: Starting create_fedex_shipment for customer: {customer_data.get('name')}")
        print(f"🔍 DEBUG: customer_data keys: {list(customer_data.keys())}")
        # Uncomment the line below to set a breakpoint here
        # pdb.set_trace()

        # Get origin address if not provided
        if not origin_address_id:
            addresses = self.easyship_api.get_addresses()
            if addresses:
                # Use first available sender address
                for addr in addresses:
                    if addr.get("default_for", {}).get("sender", False):
                        origin_address_id = addr.get("id")
                        break
                if not origin_address_id and addresses:
                    origin_address_id = addresses[0].get("id")

        if not origin_address_id:
            print("❌ No origin address available for FedEx shipment")
            return None

        # DEBUG BREAKPOINT 2: Inspect origin address resolution
        print(f"🔍 DEBUG: Using origin_address_id: {origin_address_id}")
        # Uncomment the line below to set a breakpoint here
        # pdb.set_trace()

        # Get some products for the shipment
        products = self.easyship_api.get_random_products(2)
        
        # DEBUG BREAKPOINT 3: Inspect products
        print(f"🔍 DEBUG: Retrieved {len(products) if products else 0} products")
        if products:
            print(f"🔍 DEBUG: First product: {products[0] if products else 'None'}")
        # Uncomment the line below to set a breakpoint here
        # pdb.set_trace()
        
        if not products:
            print(
                f"⚠️ No products available, using fallback products for {
                    customer_data.get('name')}"
            )
            # Fallback products - this shouldn't happen with improved
            # get_random_products
            products = [
                {
                    "title": "Premium Fashion Item",
                    "weight": 0.5,
                    "price": 35.00,
                    "description": "High-quality fashion apparel",
                },
                {
                    "title": "Designer Accessory",
                    "weight": 0.3,
                    "price": 20.00,
                    "description": "Elegant fashion accessory",
                },
            ]

        # Format customer data for Easyship
        formatted_customer = normalize_customer_data(
            {
                "name": customer_data.get("name", ""),
                "address_1": customer_data.get("address_1", ""),
                "city": customer_data.get("city", ""),
                "postal_code": customer_data.get("postal_code", ""),
                "country": customer_data.get("country", "US"),
                "phone": customer_data.get("phone", ""),
                "email": customer_data.get("email", ""),
            }
        )
        
        # DEBUG BREAKPOINT 4: Inspect formatted customer data
        print(f"🔍 DEBUG: Formatted customer data: {formatted_customer}")
        # Uncomment the line below to set a breakpoint here
        # pdb.set_trace()

        # Create shipment
        result = self.easyship_api.create_shipment(
            formatted_customer, products, origin_address_id
        )
        
        # DEBUG BREAKPOINT 5: Inspect API response
        print(f"🔍 DEBUG: Shipment creation result: {result is not None}")
        if result:
            print(f"🔍 DEBUG: Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"🔍 DEBUG: Shipment ID: {result.get('shipment', {}).get('id') if isinstance(result, dict) else 'N/A'}")
        # Uncomment the line below to set a breakpoint here
        # pdb.set_trace()

        if result:
            shipment_id = result.get("shipment", {}).get("id")
            if shipment_id:
                # Try to book FedEx rate
                fedex_booking = self.easyship_api.book_fedex_rate(shipment_id)
                
                # DEBUG BREAKPOINT 6: Inspect FedEx booking response
                print(f"🔍 DEBUG: FedEx booking result: {fedex_booking is not None}")
                if fedex_booking:
                    print(f"🔍 DEBUG: Booking keys: {list(fedex_booking.keys()) if isinstance(fedex_booking, dict) else 'Not a dict'}")
                # Uncomment the line below to set a breakpoint here
                # pdb.set_trace()
                
                if fedex_booking:
                    print(
                        f"✅ FedEx shipment created and booked for {
                            customer_data.get('name')}"
                    )
                    return {"shipment": result, "booking": fedex_booking}
                else:
                    print(
                        f"⚠️ FedEx shipment created but booking failed for {
                            customer_data.get('name')}"
                    )
                    return {"shipment": result, "booking": None}

        print(
            f"❌ Failed to create FedEx shipment for {
                customer_data.get('name')}"
        )
        return None

    def process_all_fedex_orders(self) -> List[Dict]:
        """Process all predefined FedEx customers"""
        results = []

        print(f"🚀 Processing {len(self.fedex_customers)} FedEx orders...")

        for customer in self.fedex_customers:
            print(f"Processing order for {customer['name']}...")
            result = self.create_fedex_shipment(customer)
            results.append(
                {
                    "customer": customer,
                    "result": result,
                    "success": result is not None,
                }
            )

        successful = sum(1 for r in results if r["success"])
        print(
            f"✅ Processed {successful}/{
                len(results)} FedEx orders successfully"
        )

        return results

    def get_fedex_customer_summary(self) -> Dict:
        """Get summary of FedEx customers by country"""
        summary = {}
        for customer in self.fedex_customers:
            country = customer["country"]
            if country not in summary:
                summary[country] = []
            summary[country].append(customer["name"])

        return summary

    def save_order_to_database(self, customer_data: Dict, shipment_result: Dict, products: List[Dict]) -> Optional[Order]:
        """Save FedEx order to database after successful shipment creation"""
        try:
            shipment_data = shipment_result.get("shipment", {})
            booking_data = shipment_result.get("booking", {})
            
            # Calculate total weight and value from products
            total_weight = sum(product.get("weight", 0) for product in products) * 1000  # Convert to grams
            total_value = sum(product.get("price", 0) for product in products)
            
            # Extract cost information from booking if available
            shipping_cost = None
            if booking_data:
                rates = booking_data.get("rates", [])
                if rates:
                    shipping_cost = rates[0].get("total_charge", 0)
            
            # Create order record
            order = Order(
                easyship_shipment_id=shipment_data.get("id"),
                tracking_number=booking_data.get("tracking_number") if booking_data else None,
                customer_name=customer_data.get("name", ""),
                customer_email=customer_data.get("email", ""),
                customer_phone=customer_data.get("phone", ""),
                address_line_1=customer_data.get("address_1", ""),
                address_line_2=customer_data.get("address_2", ""),
                city=customer_data.get("city", ""),
                state=customer_data.get("state", ""),
                postal_code=customer_data.get("postal_code", ""),
                country=customer_data.get("country", ""),
                carrier="FEDEX",
                service_type=booking_data.get("service", "") if booking_data else "",
                total_weight_grams=total_weight,
                total_value=total_value,
                order_status="shipped" if booking_data else "pending",
                booking_status="confirmed" if booking_data else "failed",
                shipping_cost=shipping_cost,
                total_cost=shipping_cost,
                platform="easyship",
                shipped_at=datetime.utcnow() if booking_data else None
            )
            
            db.session.add(order)
            db.session.commit()
            
            print(f"✅ Order saved to database: ID {order.id} for {customer_data.get('name')}")
            return order
            
        except Exception as e:
            print(f"❌ Failed to save order to database: {str(e)}")
            db.session.rollback()
            return None

    def create_fedex_shipment_with_persistence(self, customer_data: Dict, origin_address_id: str = None) -> Optional[Dict]:
        """Create FedEx shipment and save to database"""
        # Create the shipment using existing method
        result = self.create_fedex_shipment(customer_data, origin_address_id)
        
        if result:
            # Get products that were used (replicate the logic from create_fedex_shipment)
            products = self.easyship_api.get_random_products(2)
            if not products:
                products = [
                    {"title": "Premium Fashion Item", "weight": 0.5, "price": 35.00, "description": "High-quality fashion apparel"},
                    {"title": "Designer Accessory", "weight": 0.3, "price": 20.00, "description": "Elegant fashion accessory"},
                ]
            
            # Save to database
            order = self.save_order_to_database(customer_data, result, products)
            if order:
                result["order_id"] = order.id
                result["database_saved"] = True
            else:
                result["database_saved"] = False
        
        return result

    def export_fedex_orders_to_csv(self, file_path: str = None, date_range: Optional[Dict] = None) -> str:
        """Export FedEx orders to CSV file"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exports_dir = os.path.join("data", "exports")
            os.makedirs(exports_dir, exist_ok=True)
            file_path = os.path.join(exports_dir, f"fedex_orders_{timestamp}.csv")
        
        success = self.csv_processor.export_fedex_orders_csv(file_path, date_range)
        
        if success:
            print(f"✅ FedEx orders exported to: {file_path}")
            return file_path
        else:
            print(f"❌ Failed to export FedEx orders")
            print(f"Errors: {self.csv_processor.get_errors()}")
            return None

    def get_fedex_orders_summary(self) -> Dict:
        """Get summary of FedEx orders in database"""
        filters = {'carrier': 'FEDEX'}
        return self.csv_processor.get_order_export_summary(filters)

    def process_all_fedex_orders_with_persistence(self) -> List[Dict]:
        """Process all predefined FedEx customers and save to database"""
        results = []

        print(f"🚀 Processing {len(self.fedex_customers)} FedEx orders with database persistence...")

        for customer in self.fedex_customers:
            print(f"Processing order for {customer['name']}...")
            result = self.create_fedex_shipment_with_persistence(customer)
            results.append({
                "customer": customer,
                "result": result,
                "success": result is not None,
                "database_saved": result.get("database_saved", False) if result else False
            })

        successful = sum(1 for r in results if r["success"])
        saved_to_db = sum(1 for r in results if r.get("database_saved", False))
        
        print(f"✅ Processed {successful}/{len(results)} FedEx orders successfully")
        print(f"💾 Saved {saved_to_db}/{successful} orders to database")

        return results

    def export_recent_fedex_orders(self, days: int = 7) -> str:
        """Export FedEx orders from the last N days"""
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_range = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self.export_fedex_orders_to_csv(date_range=date_range)
