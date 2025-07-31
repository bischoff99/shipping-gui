#!/usr/bin/env python3
"""
Debug script to isolate the routing issue
"""

import os
from dotenv import load_dotenv
import traceback

load_dotenv()

# Import after loading environment
from api.veeqo_api import VeeqoAPI
from routing import OrderRoutingSystem

print("=== DEBUGGING ROUTING ISSUE ===")

try:
    # Initialize components
    veeqo_api = VeeqoAPI()
    routing_system = OrderRoutingSystem()
    
    print("1. Getting warehouses from Veeqo...")
    warehouses = veeqo_api.get_warehouses()
    print(f"   Found {len(warehouses)} warehouses")
    
    # Show first warehouse structure
    if warehouses:
        print(f"   First warehouse structure: {type(warehouses[0])}")
        first_warehouse = warehouses[0]
        print(f"   Keys: {list(first_warehouse.keys()) if isinstance(first_warehouse, dict) else 'Not a dict'}")
        if isinstance(first_warehouse, dict):
            print(f"   ID: {first_warehouse.get('id', 'No ID')}")
            print(f"   Name: {first_warehouse.get('name', 'No name')}")
    
    print("\n2. Testing customer data...")
    customer_data = {
        "name": "John Doe",
        "email": "john@email.com",
        "address_1": "123 Main St",
        "city": "Anywhere",
        "state": "CA",
        "postal_code": "90210",
        "country": "US"
    }
    print(f"   Customer state: {customer_data.get('state')}")
    
    print("\n3. Testing routing...")
    try:
        routing_decision = routing_system.route_order(customer_data, warehouses)
        print(f"   SUCCESS: Platform = {routing_decision.platform}")
        print(f"   Carrier = {routing_decision.carrier}")
        print(f"   Warehouse = {routing_decision.warehouse_info}")
        print(f"   Confidence = {routing_decision.confidence}")
    except Exception as e:
        print(f"   ERROR in route_order: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        
        # Let's debug the issue step by step
        print("\n4. Debugging step by step...")
        
        # Check warehouse mappings
        try:
            warehouse_mappings = routing_system.get_warehouse_mappings()
            print(f"   Warehouse mappings: {len(warehouse_mappings)} entries")
            print(f"   Mapping keys (first 5): {list(warehouse_mappings.keys())[:5]}")
        except Exception as e2:
            print(f"   ERROR getting warehouse mappings: {e2}")
        
        # Check warehouse processing line that's failing
        try:
            print(f"   Warehouses type: {type(warehouses)}")
            print(f"   First warehouse type: {type(warehouses[0]) if warehouses else 'No warehouses'}")
            
            # This is the problematic line from routing.py:88-92
            warehouse_mappings = routing_system.get_warehouse_mappings()
            print(f"   Attempting to process warehouses...")
            
            for i, wh in enumerate(warehouses[:3]):  # Just first 3 for debugging
                wh_id = wh if isinstance(wh, (str, int)) else wh.get('id')
                print(f"   Warehouse {i}: ID = {wh_id}, Type = {type(wh_id)}")
                print(f"   In mappings: {wh_id in warehouse_mappings if warehouse_mappings else 'No mappings'}")
                
        except Exception as e3:
            print(f"   ERROR in step-by-step debug: {e3}")
            print(f"   Traceback: {traceback.format_exc()}")

except Exception as e:
    print(f"ERROR: {e}")
    print(f"Traceback: {traceback.format_exc()}")

print("\n=== DEBUGGING COMPLETE ===")