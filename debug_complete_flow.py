#!/usr/bin/env python3
"""
Complete debug of the entire order creation flow
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI
from utils import parse_customer_input, normalize_customer_data

print("=== COMPLETE ORDER CREATION FLOW DEBUG ===")

try:
    veeqo_api = VeeqoAPI()
    
    # Test data
    customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
    customer_data = normalize_customer_data(parse_customer_input(customer_input))
    
    print("1. Customer data:")
    print(json.dumps(customer_data, indent=2))
    
    print("\n2. Getting channels...")
    channels = veeqo_api.make_request("/channels")
    suitable_channel = None
    for channel in channels:
        type_code = channel.get('type_code', '').lower()
        state = channel.get('state', '').lower()
        if type_code in ['direct', 'manual', 'pos', 'phone'] and state == 'active':
            suitable_channel = channel
            break
    
    print(f"   Using channel: {suitable_channel.get('name')} (ID: {suitable_channel.get('id')})")
    
    print("\n3. Creating customer...")
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
    
    print(f"   Customer creation status: {customer_response.status_code}")
    if customer_response.status_code in [200, 201]:
        created_customer = customer_response.json()
        customer_id = created_customer.get("id")
        print(f"   Customer created: ID {customer_id}")
        print(f"   Customer name: '{created_customer.get('full_name')}'")
    else:
        print(f"   Customer creation failed: {customer_response.text}")
        print("   Exiting due to customer creation failure")
        exit(1)
    
    print("\n4. Getting products and warehouse...")
    products = veeqo_api.get_random_products(1)
    warehouse = veeqo_api.get_warehouse_by_state("NV")
    warehouse_id = warehouse.get("id")
    
    print(f"   Product: {products[0].get('title')} (ID: {products[0].get('id')})")
    print(f"   Warehouse: {warehouse.get('name')} (ID: {warehouse_id})")
    
    print("\n5. Creating order structure...")
    
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
    
    line_items = [
        {
            "sellable_id": products[0].get("id"),
            "quantity": 1,
            "price_per_unit": float(products[0].get("price", "25.00")),
        }
    ]
    
    order_data = {
        "order": {
            "channel_id": suitable_channel.get("id"),
            "customer_id": customer_id,
            "deliver_to": deliver_to_payload,
            "line_items": line_items,
            "warehouse_id": warehouse_id,
            "shipping_method": "UPS",
        }
    }
    
    print("   Order data:")
    print(json.dumps(order_data, indent=2))
    
    print("\n6. Creating order...")
    order_response = requests.post(
        f"{veeqo_api.base_url}/orders",
        headers=veeqo_api.headers,
        json=order_data,
        timeout=30
    )
    
    print(f"   Order creation status: {order_response.status_code}")
    if order_response.status_code in [200, 201]:
        created_order = order_response.json()
        print(f"   ORDER CREATED SUCCESSFULLY!")
        print(f"   Order ID: {created_order.get('id')}")
        print(f"   Order Number: {created_order.get('number')}")
    else:
        print(f"   Order creation failed: {order_response.text}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")