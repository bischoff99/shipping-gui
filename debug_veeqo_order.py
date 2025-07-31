#!/usr/bin/env python3
"""
Debug Veeqo order creation to see what's being sent and what response we get
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI
from utils import parse_customer_input, normalize_customer_data

print("=== DEBUGGING VEEQO ORDER CREATION ===")

try:
    veeqo_api = VeeqoAPI()
    
    # Test data
    customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
    customer_data = normalize_customer_data(parse_customer_input(customer_input))
    
    print("1. Customer data:")
    print(json.dumps(customer_data, indent=2))
    
    # Get products
    products = veeqo_api.get_random_products(1)  # Just 1 product for testing
    print(f"\n2. Products ({len(products)}):")
    for product in products:
        print(f"   ID: {product.get('id')}")
        print(f"   Title: {product.get('title')}")
        print(f"   Price: {product.get('price')}")
    
    # Get warehouse
    warehouse = veeqo_api.get_warehouse_by_state("NV")
    warehouse_id = warehouse.get("id") if warehouse else None
    print(f"\n3. Warehouse:")
    print(f"   ID: {warehouse_id}")
    print(f"   Name: {warehouse.get('name') if warehouse else 'None'}")
    
    if warehouse_id and products:
        print("\n4. Creating order data structure...")
        
        # Manually create the same order data that create_order method would create
        order_data = {
            "order": {
                "customer": {
                    "first_name": customer_data.get("name", "").split()[0] if customer_data.get("name") else "Customer",
                    "last_name": " ".join(customer_data.get("name", "").split()[1:]) if len(customer_data.get("name", "").split()) > 1 else "",
                    "phone": customer_data.get("phone", ""),
                    "email": customer_data.get("email", ""),
                },
                "deliver_to": {
                    "first_name": customer_data.get("name", "").split()[0] if customer_data.get("name") else "Customer",
                    "last_name": " ".join(customer_data.get("name", "").split()[1:]) if len(customer_data.get("name", "").split()) > 1 else "",
                    "address_line_1": customer_data.get("address_1", ""),
                    "city": customer_data.get("city", ""),
                    "state": customer_data.get("state", ""),
                    "zip": customer_data.get("postal_code", ""),
                    "country": customer_data.get("country", "US"),
                    "phone": customer_data.get("phone", ""),
                },
                "line_items": [
                    {
                        "sellable_id": product.get("id"),
                        "quantity": 1,
                        "price_per_unit": product.get("price", "25.00"),
                    }
                    for product in products
                ],
                "warehouse_id": warehouse_id,
                "channel_id": 1,  # Default channel
                "shipping_method": "UPS",
            }
        }
        
        print("   Order data structure:")
        print(json.dumps(order_data, indent=2))
        
        print("\n5. Testing direct API call...")
        
        # Test the API call directly using make_request to get more details
        import requests
        
        url = f"{veeqo_api.base_url}/orders"
        headers = veeqo_api.headers
        
        print(f"   URL: {url}")
        print(f"   Headers: {headers}")
        
        try:
            response = requests.post(url, headers=headers, json=order_data, timeout=30)
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"   Error Response: {response.text}")
            else:
                print(f"   Success Response: {response.json()}")
                
        except Exception as e:
            print(f"   Request Exception: {e}")
        
        print("\n6. Testing with create_order method...")
        try:
            result = veeqo_api.create_order(customer_data, products, warehouse_id, "UPS")
            if result:
                print(f"   SUCCESS: {result}")
            else:
                print("   FAILED: create_order returned None")
        except Exception as e:
            print(f"   EXCEPTION: {e}")
    
    else:
        if not warehouse_id:
            print("   ERROR: No warehouse found")
        if not products:
            print("   ERROR: No products found")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")