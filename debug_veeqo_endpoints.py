#!/usr/bin/env python3
"""
Debug Veeqo API endpoints to see what's available
"""

import os
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI

print("=== DEBUGGING VEEQO API ENDPOINTS ===")

try:
    veeqo_api = VeeqoAPI()
    
    # Test various endpoints to see what works
    endpoints_to_test = [
        "/",
        "/warehouses",
        "/products", 
        "/sellables",
        "/orders",
        "/order",
        "/api/orders",
        "/v1/orders"
    ]
    
    print("Testing API endpoints...")
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting {endpoint}:")
        try:
            result = veeqo_api.make_request(endpoint, "GET")
            if result is not None:
                if isinstance(result, list):
                    print(f"   SUCCESS: Returned list with {len(result)} items")
                elif isinstance(result, dict):
                    print(f"   SUCCESS: Returned dict with keys: {list(result.keys())[:5]}")
                else:
                    print(f"   SUCCESS: Returned {type(result)}")
            else:
                print(f"   FAILED: Returned None")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "="*50)
    print("Testing POST to orders endpoints...")
    
    # Test POST requests to different order endpoints
    test_order_data = {"order": {"test": True}}
    
    order_endpoints = ["/orders", "/order", "/api/orders"]
    
    for endpoint in order_endpoints:
        print(f"\nTesting POST to {endpoint}:")
        try:
            import requests
            url = f"{veeqo_api.base_url}{endpoint}"
            response = requests.post(url, headers=veeqo_api.headers, json=test_order_data, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.text[:200]}")
            else:
                print(f"   Success: {response.json()}")
        except Exception as e:
            print(f"   Exception: {e}")

except Exception as e:
    print(f"ERROR: {e}")

print("\n=== DEBUGGING COMPLETE ===")