#!/usr/bin/env python3
"""
Debug existing Veeqo orders to understand the required structure
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI

print("=== EXAMINING EXISTING VEEQO ORDERS ===")

try:
    veeqo_api = VeeqoAPI()
    
    print("1. Getting existing orders...")
    orders = veeqo_api.make_request("/orders")
    
    if orders:
        print(f"   Found {len(orders)} orders")
        
        # Examine the first order structure
        if len(orders) > 0:
            first_order = orders[0]
            print(f"\n2. First order structure:")
            print(f"   Order ID: {first_order.get('id')}")
            print(f"   Keys: {list(first_order.keys())}")
            
            # Look at important fields
            print(f"\n3. Important fields:")
            print(f"   Channel: {first_order.get('channel')}")
            print(f"   Customer: {first_order.get('customer')}")
            print(f"   Line items: {len(first_order.get('line_items', []))} items")
            print(f"   Warehouse ID: {first_order.get('warehouse_id')}")
            
            # Look at channel structure
            channel = first_order.get('channel')
            if channel:
                print(f"\n4. Channel structure:")
                print(f"   Channel ID: {channel.get('id') if isinstance(channel, dict) else channel}")
                if isinstance(channel, dict):
                    print(f"   Channel keys: {list(channel.keys())}")
            
            # Look at customer structure
            customer = first_order.get('customer')
            if customer:
                print(f"\n5. Customer structure:")
                if isinstance(customer, dict):
                    print(f"   Customer keys: {list(customer.keys())}")
                    print(f"   Customer ID: {customer.get('id')}")
                
            # Look at line items structure
            line_items = first_order.get('line_items', [])
            if line_items and len(line_items) > 0:
                print(f"\n6. Line item structure:")
                first_item = line_items[0]
                print(f"   Line item keys: {list(first_item.keys())}")
                print(f"   Sellable ID: {first_item.get('sellable_id')}")
                print(f"   Quantity: {first_item.get('quantity')}")
                print(f"   Price: {first_item.get('price_per_unit')}")
    
    print("\n7. Getting channels...")
    try:
        channels = veeqo_api.make_request("/channels")
        if channels:
            print(f"   Found {len(channels)} channels")
            if len(channels) > 0:
                print(f"   First channel ID: {channels[0].get('id')}")
                print(f"   First channel name: {channels[0].get('name')}")
        else:
            print("   No channels found or error")
    except Exception as e:
        print(f"   Error getting channels: {e}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== EXAMINATION COMPLETE ===")