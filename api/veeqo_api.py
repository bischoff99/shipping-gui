# Veeqo API integration module
# Reuse and adapt logic from your previous scripts

import os
import requests
import logging
from typing import Dict, List, Optional, Any

VEEQO_API_KEY = os.environ.get("VEEQO_API_KEY")
VEEQO_BASE_URL = "https://api.veeqo.com"


class VeeqoAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or VEEQO_API_KEY
        if not self.api_key:
            raise ValueError("VEEQO_API_KEY environment variable is required")
        self.base_url = VEEQO_BASE_URL
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        self.logger = logging.getLogger("api.veeqo")

    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
        timeout: int = 30,
    ) -> Optional[Any]:
        """Make API request to Veeqo with comprehensive error handling"""
        try:
            url = f"{self.base_url}{endpoint}"

            # Add timeout to prevent hanging requests
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(
                    url, headers=self.headers, json=data, timeout=timeout
                )
            elif method == "PUT":
                response = requests.put(
                    url, headers=self.headers, json=data, timeout=timeout
                )
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Raise for HTTP errors (4xx and 5xx)
            response.raise_for_status()

            # Return JSON response for successful requests
            if response.status_code in [200, 201]:
                try:
                    self.logger.info(f"Veeqo API success: {method} {endpoint}")
                    return response.json()
                except ValueError as json_error:
                    self.logger.error(f"Veeqo JSON Parse Error: {json_error}")
                    return None
            else:
                self.logger.warning(
                    f"Veeqo API Unexpected Status: {
                        response.status_code} - {
                        response.text}"
                )
                return None

        except requests.exceptions.Timeout:
            self.logger.error(
                f"Veeqo API Timeout: Request to {endpoint} timed out after {timeout}s"
            )
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(
                f"Veeqo API Connection Error: Unable to connect to {
                    self.base_url}"
            )
            return None
        except requests.exceptions.HTTPError as http_error:
            self.logger.error(f"Veeqo API HTTP Error: {http_error}")
            return None
        except requests.exceptions.RequestException as req_error:
            self.logger.error(f"Veeqo API Request Error: {req_error}")
            return None
        except Exception as e:
            self.logger.error(f"Veeqo Unexpected Error: {e}")
            return None

    def get_warehouses(self) -> List[Dict]:
        """Get all Veeqo warehouses"""
        warehouses = self.make_request("/warehouses")
        return warehouses if warehouses else []

    def get_products(self, limit: int = 100) -> List[Dict]:
        """Get Veeqo products/sellables"""
        products = self.make_request(f"/sellables?per_page={limit}")
        return products if products else []

    def get_warehouse_by_state(self, state: str) -> Optional[Dict]:
        """Find warehouse by state (Nevada, California, etc.)"""
        warehouses = self.get_warehouses()
        for warehouse in warehouses:
            warehouse_state = warehouse.get("region", "").lower()
            if state.lower() in warehouse_state:
                return warehouse
        return None

    def get_random_products(self, count: int = 3) -> List[Dict]:
        """Get random products for order with fallback to dummy products"""
        import random

        # Try to get real products first
        try:
            products = self.get_products(50)  # Get 50 to have good selection
            if products and len(products) >= count:
                selected_products = random.sample(products, count)

                # Ensure each product has required fields
                for i, product in enumerate(selected_products):
                    if not product.get("title"):
                        product["title"] = f"Fashion Item {i + 1}"
                    if not product.get("price"):
                        product["price"] = random.choice(
                            ["25.00", "35.00", "45.00", "55.00"]
                        )
                    if not product.get("id"):
                        product["id"] = f"dummy_{i + 1}"

                return selected_products

            # If we have some products but not enough, use what we have and add
            # dummies
            elif products:
                selected_products = products.copy()
                needed = count - len(products)
                selected_products.extend(
                    self._generate_dummy_products(needed, start_index=len(products))
                )
                return selected_products[:count]

        except Exception as e:
            print(f"❌ Error fetching real products, using dummy products: {e}")

        # Fallback to dummy products
        return self._generate_dummy_products(count)

    def _generate_dummy_products(self, count: int, start_index: int = 0) -> List[Dict]:
        """Generate dummy products with realistic data"""
        import random

        product_names = [
            "Fashion Dress",
            "Designer Jeans",
            "Casual Shirt",
            "Summer Top",
            "Winter Jacket",
            "Sneakers",
            "Handbag",
            "Jewelry Set",
            "Silk Scarf",
            "Leather Belt",
            "Sunglasses",
            "Fashion Boots",
            "Blouse",
            "Cardigan",
            "Trousers",
            "Skirt",
            "T-Shirt",
            "Hoodie",
        ]

        prices = [
            "19.99",
            "25.00",
            "29.99",
            "35.00",
            "39.99",
            "45.00",
            "49.99",
            "55.00",
            "65.00",
            "75.00",
        ]

        dummy_products = []
        for i in range(count):
            index = start_index + i
            dummy_products.append(
                {
                    "id": f"dummy_{index + 1}",
                    "title": f"{random.choice(product_names)} #{index + 1}",
                    "price": random.choice(prices),
                    "description": f"High-quality fashion item #{index + 1}",
                    "weight": round(
                        random.uniform(0.3, 1.2), 1
                    ),  # Random weight between 0.3-1.2 kg
                    "category": random.choice(
                        ["Apparel", "Accessories", "Footwear", "Jewelry"]
                    ),
                }
            )

        return dummy_products

    def create_order(
        self,
        customer_data: Dict,
        products: List[Dict],
        warehouse_id: int,
        carrier: str = "UPS",
    ) -> Optional[Dict]:
        """Create Veeqo order with proper channel ID and structure"""
        try:
            # Get a valid channel ID from available channels
            channels = self.make_request("/channels")
            if not channels or len(channels) == 0:
                self.logger.error("No channels available for order creation")
                return None
            
            # Find a channel that supports order creation (direct, manual, pos, phone types)
            suitable_channel = None
            for channel in channels:
                type_code = channel.get('type_code', '').lower()
                state = channel.get('state', '').lower()
                if type_code in ['direct', 'manual', 'pos', 'phone'] and state == 'active':
                    suitable_channel = channel
                    break
            
            if not suitable_channel:
                self.logger.error("No suitable channels found for order creation")
                return None
                
            channel_id = suitable_channel.get("id")
            
            # Create customer first
            customer_creation_data = {
                "customer": {
                    "email": customer_data.get("email", ""),
                    "phone": customer_data.get("phone", ""),
                    "full_name": customer_data.get("name", "Customer"),
                    "customer_type": "retail"
                }
            }
            
            created_customer = self.make_request("/customers", "POST", customer_creation_data)
            if not created_customer:
                self.logger.error("Failed to create customer")
                return None
                
            customer_id = created_customer.get("id")
            self.logger.info(f"Created customer with ID: {customer_id}")
            
            # Extract name parts for deliver_to
            name_parts = customer_data.get("name", "Customer").split()
            first_name = name_parts[0] if name_parts else "Customer"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            deliver_to_payload = {
                "first_name": first_name,
                "last_name": last_name,
                "address_line_1": customer_data.get("address_1", ""),
                "city": customer_data.get("city", ""),
                "state": customer_data.get("state", ""),
                "zip": customer_data.get("postal_code", ""),
                "country": customer_data.get("country", "US"),
                "phone": customer_data.get("phone", ""),
            }
            
            # Create line items with proper structure
            line_items = []
            for product in products:
                line_item = {
                    "sellable_id": product.get("id"),
                    "quantity": 1,
                    "price_per_unit": float(product.get("price", "25.00")),
                }
                line_items.append(line_item)
            
            order_data = {
                "order": {
                    "channel_id": channel_id,
                    "customer_id": customer_id,
                    "deliver_to": deliver_to_payload,
                    "line_items": line_items,
                    "warehouse_id": warehouse_id,
                    "shipping_method": carrier,
                }
            }
            
            self.logger.info(f"Creating order with channel_id: {channel_id}, warehouse_id: {warehouse_id}")
            return self.make_request("/orders", "POST", order_data)
            
        except Exception as e:
            self.logger.error(f"Error in create_order: {e}")
            return None

    def get_purchase_orders(self, limit: int = 50) -> List[Dict]:
        """Get Veeqo purchase orders"""
        purchase_orders = self.make_request(f"/purchase_orders?per_page={limit}")
        return purchase_orders if purchase_orders else []

    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Get product by SKU"""
        products = self.make_request(f"/products?sku={sku}")
        if products and len(products) > 0:
            return products[0]
        return None

    def create_product(self, product_data: Dict) -> Optional[Dict]:
        """Create new product"""
        return self.make_request("/products", "POST", product_data)

    def update_product(self, product_id: str, product_data: Dict) -> Optional[Dict]:
        """Update existing product"""
        return self.make_request(f"/products/{product_id}", "PUT", product_data)

    def delete_product(self, product_id: str) -> bool:
        """Delete product"""
        result = self.make_request(f"/products/{product_id}", "DELETE")
        return result is not None
