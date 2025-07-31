#!/usr/bin/env python3
"""
Debug line items structure to match what Veeqo expects
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI
from utils import parse_customer_input, normalize_customer_data

print("=== DEBUGGING LINE ITEMS STRUCTURE ===")

try:
    veeqo_api = VeeqoAPI()
    
    # Get the same test data
    customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
    customer_data = normalize_customer_data(parse_customer_input(customer_input))
    
    # Get channels and customer like before
    channels = veeqo_api.make_request("/channels")
    suitable_channel = None
    for channel in channels:
        type_code = channel.get('type_code', '').lower()
        state = channel.get('state', '').lower()
        if type_code in ['direct', 'manual', 'pos', 'phone'] and state == 'active':
            suitable_channel = channel
            break
    
    # Create customer
    customer_creation_data = {
        "customer": {
            "email": customer_data.get("email", ""),
            "phone": customer_data.get("phone", ""),
            "full_name": customer_data.get("name", "Customer"),
            "customer_type": "retail"
        }
    }
    
    customer_response = requests.post(
        f"{veeqo_api.base_url}/customers",
        headers=veeqo_api.headers,
        json=customer_creation_data,
        timeout=30
    )
    
    customer_id = customer_response.json().get("id")
    
    # Get product details
    products = veeqo_api.get_random_products(1)
    product = products[0]
    
    print("1. Product details:")
    print(f"   ID: {product.get('id')}")
    print(f"   Title: {product.get('title')}")
    print(f"   Price: {product.get('price')}")
    print(f"   Full product keys: {list(product.keys())}")
    
    print("\n2. Testing different line item structures...")
    
    warehouse = veeqo_api.get_warehouse_by_state("NV")
    warehouse_id = warehouse.get("id")
    
    # Test 1: Basic structure
    print("\n   Test 1: Basic structure")
    line_items_basic = [
        {
            "sellable_id": product.get("id"),
            "quantity": 1,
            "price_per_unit": float(product.get("price", "25.00")),
        }
    ]
    
    order_data_basic = {
        "order": {
            "channel_id": suitable_channel.get("id"),
            "customer_id": customer_id,
            "deliver_to": {
                "first_name": "John",
                "last_name": "Doe",
                "address_line_1": "123 Main St",
                "city": "Anywhere",
                "state": "CA",
                "zip": "90210",
                "country": "US",
                "phone": "5551234567",
            },
            "line_items": line_items_basic,
            "warehouse_id": warehouse_id,
            "shipping_method": "UPS",
        }
    }
    
    response = requests.post(
        f"{veeqo_api.base_url}/orders",
        headers=veeqo_api.headers,
        json=order_data_basic,
        timeout=30
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code not in [200, 201]:
        print(f"   Error: {response.text}")
    else:
        print(f"   SUCCESS: Order created")
        created_order = response.json()
        print(f"   Order ID: {created_order.get('id')}")
        
    # Test 2: With title field
    if response.status_code not in [200, 201]:
        print("\n   Test 2: With title field")
        line_items_with_title = [
            {
                "sellable_id": product.get("id"),
                "quantity": 1,
                "price_per_unit": float(product.get("price", "25.00")),
                "title": product.get("title", "Product"),
            }
        ]
        
        order_data_with_title = order_data_basic.copy()
        order_data_with_title["order"]["line_items"] = line_items_with_title
        
        response2 = requests.post(
            f"{veeqo_api.base_url}/orders",
            headers=veeqo_api.headers,
            json=order_data_with_title,
            timeout=30
        )
        
        print(f"   Status: {response2.status_code}")
        if response2.status_code not in [200, 201]:
            print(f"   Error: {response2.text}")
        else:
            print(f"   SUCCESS: Order created with title")
            created_order = response2.json()
            print(f"   Order ID: {created_order.get('id')}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")