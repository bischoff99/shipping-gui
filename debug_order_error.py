#!/usr/bin/env python3
"""
Debug the exact error message from Veeqo order creation
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI
from utils import parse_customer_input, normalize_customer_data

print("=== DEBUGGING ORDER CREATION ERROR ===")

try:
    veeqo_api = VeeqoAPI()
    
    # Test data
    customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
    customer_data = normalize_customer_data(parse_customer_input(customer_input))
    
    # Get minimal data for testing
    products = veeqo_api.get_random_products(1)
    warehouse = veeqo_api.get_warehouse_by_state("NV")
    warehouse_id = warehouse.get("id")
    
    print("1. Testing with updated create_order method...")
    
    # Monkey patch the make_request method to capture the exact error
    original_make_request = veeqo_api.make_request
    
    def debug_make_request(endpoint, method="GET", data=None, timeout=30):
        print(f"   API Call: {method} {endpoint}")
        if data:
            print("   Data being sent:")
            print(json.dumps(data, indent=2))
        
        try:
            import requests
            url = f"{veeqo_api.base_url}{endpoint}"
            
            if method == "POST":
                response = requests.post(url, headers=veeqo_api.headers, json=data, timeout=timeout)
            else:
                response = requests.get(url, headers=veeqo_api.headers, timeout=timeout)
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   Error Response: {response.text}")
                return None
            else:
                result = response.json()
                print(f"   Success: {type(result)} returned")
                return result
                
        except Exception as e:
            print(f"   Exception: {e}")
            return None
    
    # Replace the method temporarily
    veeqo_api.make_request = debug_make_request
    
    # Now try to create the order
    result = veeqo_api.create_order(customer_data, products, warehouse_id, "UPS")
    
    if result:
        print(f"   ORDER CREATED SUCCESSFULLY: {result}")
    else:
        print("   ORDER CREATION FAILED")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")