# Veeqo Orders Processing Module
# Handle UPS and DHL orders that should be routed through Veeqo based on
# state preferences


from typing import Dict, List, Optional
from api.veeqo_api import VeeqoAPI
from utils import normalize_customer_data
import logging
import time
from requests.exceptions import Timeout, RequestException


class VeeqoOrderProcessor:
    def __init__(self):
        self.veeqo_api = VeeqoAPI()
        self.logger = logging.getLogger("VeeqoOrderProcessor")
        if not self.logger.handlers:
            handler = logging.FileHandler("veeqo_orders.log")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        # Predefined Veeqo customer data (UPS and DHL orders based on state
        # preferences)
        self.veeqo_customers = [
            # ...existing customer dicts...
        ]

    def _safe_api_call(self, func, *args, retries=3, delay=2, **kwargs):
        """Call API with timeout/retry handling"""
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Timeout as e:
                self.logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                time.sleep(delay)
            except RequestException as e:
                self.logger.error(f"API request failed: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                break
        return None

    def get_veeqo_customers(self) -> List[Dict]:
        """Get all predefined Veeqo customers"""
        return self.veeqo_customers

    def get_veeqo_customer_by_name(self, name: str) -> Optional[Dict]:
        """Get specific Veeqo customer by name"""
        for customer in self.veeqo_customers:
            if customer["name"].lower() == name.lower():
                return customer
        return None

    def get_customers_by_state_preference(self, state: str) -> List[Dict]:
        """Get customers filtered by state preference"""
        return [
            c
            for c in self.veeqo_customers
            if c["state_preference"].lower() == state.lower()
        ]

    def get_customers_by_carrier(self, carrier: str) -> List[Dict]:
        """Get customers filtered by carrier"""
        return [
            c for c in self.veeqo_customers if c["carrier"].upper() == carrier.upper()
        ]

    def create_veeqo_order(
        self, customer_data: Dict, warehouse_id: int = None
    ) -> Optional[Dict]:
        """Create Veeqo order for customer with logging and error handling"""
        try:
            # Get warehouse based on state preference
            if not warehouse_id:
                state_pref = customer_data.get("state_preference", "Nevada")
                if state_pref.lower() == "nevada":
                    warehouse = self._safe_api_call(
                        self.veeqo_api.get_warehouse_by_state, "Nevada"
                    )
                elif state_pref.lower() == "california":
                    warehouse = self._safe_api_call(
                        self.veeqo_api.get_warehouse_by_state, "California"
                    )
                else:
                    warehouse = self._safe_api_call(
                        self.veeqo_api.get_warehouse_by_state, "Nevada"
                    ) or self._safe_api_call(
                        self.veeqo_api.get_warehouse_by_state, "California"
                    )
                if warehouse:
                    warehouse_id = warehouse.get("id")
                else:
                    self.logger.error(
                        f"No suitable warehouse found for {
                            customer_data.get('name')}"
                    )
                    return None
            # Get some products for the order
            products = self._safe_api_call(self.veeqo_api.get_random_products, 3)
            if not products:
                self.logger.warning(
                    f"No products available, using fallback products for {
                        customer_data.get('name')}"
                )
                products = [
                    {
                        "id": "fallback_1",
                        "title": "Premium Fashion Item",
                        "price": "35.00",
                        "description": "High-quality fashion apparel",
                    },
                    {
                        "id": "fallback_2",
                        "title": "Designer Accessory",
                        "price": "25.00",
                        "description": "Elegant fashion accessory",
                    },
                    {
                        "id": "fallback_3",
                        "title": "Luxury Fashion Piece",
                        "price": "45.00",
                        "description": "Premium fashion item",
                    },
                ]

            # Format customer data for Veeqo
            formatted_customer = normalize_customer_data(
                {
                    "name": customer_data.get("name", ""),
                    "address_1": customer_data.get("address_1", ""),
                    "city": customer_data.get("city", ""),
                    "state": customer_data.get("state", ""),
                    "postal_code": customer_data.get("postal_code", ""),
                    "country": self._get_country_code_for_veeqo(
                        customer_data.get("country", "US")
                    ),
                    "phone": customer_data.get("phone", ""),
                    "email": customer_data.get("email", ""),
                }
            )
            carrier = customer_data.get("carrier", "UPS")
            self.logger.info(
                f"Creating order for {
                    customer_data.get('name')} at warehouse {warehouse_id}"
            )
            result = self._safe_api_call(
                self.veeqo_api.create_order,
                formatted_customer,
                products,
                warehouse_id,
                carrier,
            )
            if result:
                self.logger.info(f"Order created: {result.get('id', 'N/A')}")
            else:
                self.logger.error(
                    f"Order creation failed for {customer_data.get('name')}"
                )
            return result
        except Exception as e:
            self.logger.error(f"Exception in create_veeqo_order: {e}")
            return None

    def _get_country_code_for_veeqo(self, country_code: str) -> str:
        """Convert country codes to format expected by Veeqo"""
        country_mapping = {
            "GB": "GB",  # United Kingdom
            "IE": "IE",  # Ireland
            "US": "US",  # United States
            "UK": "GB",  # UK -> GB conversion
        }
        return country_mapping.get(country_code.upper(), "US")

    def process_all_veeqo_orders(self) -> List[Dict]:
        """Process all predefined Veeqo customers efficiently with logging"""
        results = []
        self.logger.info(f"Processing {len(self.veeqo_customers)} Veeqo orders...")
        for customer in self.veeqo_customers:
            self.logger.info(
                f"Processing {
                    customer['carrier']} order for {
                    customer['name']} (State pref: {
                    customer['state_preference']})..."
            )
            result = self.create_veeqo_order(customer)
            results.append(
                {"customer": customer, "result": result, "success": result is not None}
            )
        successful = sum(1 for r in results if r["success"])
        self.logger.info(
            f"Processed {successful}/{len(results)} Veeqo orders successfully"
        )
        return results

    def get_veeqo_customer_summary(self) -> Dict:
        """Get summary of Veeqo customers by state preference and carrier"""
        summary = {"by_state": {}, "by_carrier": {}, "by_country": {}}

        for customer in self.veeqo_customers:
            # By state preference
            state = customer["state_preference"]
            if state not in summary["by_state"]:
                summary["by_state"][state] = []
            summary["by_state"][state].append(customer["name"])

            # By carrier
            carrier = customer["carrier"]
            if carrier not in summary["by_carrier"]:
                summary["by_carrier"][carrier] = []
            summary["by_carrier"][carrier].append(customer["name"])

            # By country
            country = customer["country"]
            if country not in summary["by_country"]:
                summary["by_country"][country] = []
            summary["by_country"][country].append(customer["name"])

        return summary

    def get_purchase_orders(self) -> List[Dict]:
        """Get Veeqo purchase orders using the API with robust parsing and logging"""
        try:
            response = self._safe_api_call(self.veeqo_api.get_purchase_orders)
            if not response:
                self.logger.warning("No purchase orders returned from API")
                return []
            # Ensure response is a list or dict with 'purchase_orders'
            if isinstance(response, dict) and "purchase_orders" in response:
                orders = response.get("purchase_orders", [])
            elif isinstance(response, list):
                orders = response
            else:
                self.logger.error(
                    f"Unexpected response format: {
                        type(response)}"
                )
                return []
            # Only keep necessary fields for efficiency
            return [
                {
                    "id": order.get("id"),
                    "reference": order.get("reference"),
                    "status": order.get("status"),
                    "created_at": order.get("created_at"),
                }
                for order in orders
            ]
        except Exception as e:
            self.logger.error(f"Error fetching purchase orders: {e}")
            return []
