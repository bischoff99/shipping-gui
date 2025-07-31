#!/usr/bin/env python3
"""
Debug by matching the exact structure of existing orders
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI

print("=== DEBUGGING ORDER STRUCTURE ===")

try:
    veeqo_api = VeeqoAPI()
    
    print("1. Getting existing order structure...")
    orders = veeqo_api.make_request("/orders")
    if orders and len(orders) > 0:
        existing_order = orders[0]
        
        print("2. Analyzing customer structure from existing order...")
        customer = existing_order.get('customer', {})
        print("   Customer fields in existing order:")
        print(json.dumps({
            'id': customer.get('id'),
            'email': customer.get('email'),
            'phone': customer.get('phone'),
            'full_name': customer.get('full_name'),
            'customer_type': customer.get('customer_type')
        }, indent=2))
        
        print("3. Analyzing line items structure...")
        line_items = existing_order.get('line_items', [])
        if line_items:
            first_item = line_items[0]
            print("   Line item fields in existing order:")
            print(json.dumps({
                'id': first_item.get('id'),
                'sellable_id': first_item.get('sellable', {}).get('id') if first_item.get('sellable') else None,
                'quantity': first_item.get('quantity'),
                'price_per_unit': first_item.get('price_per_unit'),
                'sellable_structure': first_item.get('sellable', {}) if first_item.get('sellable') else "No sellable"
            }, indent=2))
        
        print("4. Analyzing deliver_to structure...")
        deliver_to = existing_order.get('deliver_to', {})
        print("   Deliver_to fields:")
        print(json.dumps({
            'first_name': deliver_to.get('first_name'),
            'last_name': deliver_to.get('last_name'),
            'address_line_1': deliver_to.get('address_line_1'),
            'city': deliver_to.get('city'),
            'state': deliver_to.get('state'),
            'zip': deliver_to.get('zip'),
            'country': deliver_to.get('country'),
            'phone': deliver_to.get('phone')
        }, indent=2))
    
    print("\n5. Testing minimal order structure...")
    # Try a very minimal structure based on the exact error message
    
    # Get a sellable/product to use
    sellables = veeqo_api.make_request("/sellables", "GET")
    if sellables and len(sellables) > 0:
        sellable = sellables[0]
        print(f"   Using sellable: {sellable.get('id')} - {sellable.get('title')}")
        
        # Get suitable channel
        channels = veeqo_api.make_request("/channels")
        suitable_channel = None
        for channel in channels:
            if channel.get('type_code') == 'direct' and channel.get('state') == 'active':
                suitable_channel = channel
                break
        
        if suitable_channel:
            print(f"   Using channel: {suitable_channel.get('id')} - {suitable_channel.get('name')}")
            
            # Try creating a customer first
            print("\n6. Trying to create customer first...")
            customer_data = {
                "customer": {
                    "email": "john@email.com",
                    "phone": "5551234567",
                    "full_name": "John Doe",
                    "customer_type": "retail"
                }
            }
            
            # Test if customers endpoint exists
            try:
                import requests
                url = f"{veeqo_api.base_url}/customers"
                response = requests.post(url, headers=veeqo_api.headers, json=customer_data, timeout=10)
                print(f"   Customer creation: Status {response.status_code}")
                if response.status_code in [200, 201]:
                    customer_result = response.json()
                    print(f"   Customer created: ID {customer_result.get('id')}")
                else:
                    print(f"   Customer creation failed: {response.text}")
            except Exception as e:
                print(f"   Customer creation error: {e}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")