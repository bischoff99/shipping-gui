#!/usr/bin/env python3
"""
Final debug of order creation with proper status handling
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI
from utils import parse_customer_input, normalize_customer_data

print("=== FINAL ORDER CREATION DEBUG ===")

try:
    veeqo_api = VeeqoAPI()
    
    # Test data
    customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
    customer_data = normalize_customer_data(parse_customer_input(customer_input))
    
    # Get minimal data for testing
    products = veeqo_api.get_random_products(1)
    warehouse = veeqo_api.get_warehouse_by_state("NV")
    warehouse_id = warehouse.get("id")
    
    print("1. Test data:")
    print(f"   Customer: {customer_data.get('name')} ({customer_data.get('email')})")
    print(f"   Product: {products[0].get('title')} (${products[0].get('price')})")
    print(f"   Warehouse: {warehouse.get('name')} (ID: {warehouse_id})")
    
    print("\n2. Creating order...")
    result = veeqo_api.create_order(customer_data, products, warehouse_id, "UPS")
    
    if result:
        print("   ORDER CREATED SUCCESSFULLY!")
        print(f"   Order ID: {result.get('id')}")
        print(f"   Order Number: {result.get('number')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Total: ${result.get('total_price')}")
        print(f"   Customer: {result.get('customer', {}).get('full_name')}")
    else:
        print("   ORDER CREATION FAILED")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")