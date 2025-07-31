#!/usr/bin/env python3
"""
Debug warehouse lookup to see why no warehouse is found
"""

import os
from dotenv import load_dotenv

load_dotenv()

from api.veeqo_api import VeeqoAPI

print("=== DEBUGGING WAREHOUSE LOOKUP ===")

try:
    veeqo_api = VeeqoAPI()
    
    print("1. Getting all warehouses...")
    warehouses = veeqo_api.get_warehouses()
    print(f"   Found {len(warehouses)} warehouses")
    
    print("\n2. Examining warehouse regions/states...")
    for i, warehouse in enumerate(warehouses[:10]):  # First 10 for examination
        print(f"   Warehouse {i+1}:")
        print(f"     ID: {warehouse.get('id')}")
        print(f"     Name: {warehouse.get('name')}")
        print(f"     Region: '{warehouse.get('region')}'")
        print(f"     City: '{warehouse.get('city')}'")
        print()
    
    print("\n3. Testing get_warehouse_by_state method...")
    
    test_states = ["Nevada", "California", "CA", "NV", "nevada", "california"]
    
    for state in test_states:
        print(f"   Looking for state: '{state}'")
        warehouse = veeqo_api.get_warehouse_by_state(state)
        if warehouse:
            print(f"     FOUND: {warehouse.get('name')} (ID: {warehouse.get('id')})")
        else:
            print(f"     NOT FOUND")
    
    print("\n4. Looking for any warehouses containing CA or Nevada...")
    ca_warehouses = []
    nv_warehouses = []
    
    for warehouse in warehouses:
        region = warehouse.get('region', '').lower()
        city = warehouse.get('city', '').lower()
        name = warehouse.get('name', '').lower()
        
        if 'ca' in region or 'california' in region or 'ca' in city or 'california' in city:
            ca_warehouses.append(warehouse)
        
        if 'nv' in region or 'nevada' in region or 'nv' in city or 'nevada' in city or 'vegas' in city:
            nv_warehouses.append(warehouse)
    
    print(f"   CA-related warehouses: {len(ca_warehouses)}")
    for wh in ca_warehouses[:3]:
        print(f"     {wh.get('name')} - {wh.get('region')} - {wh.get('city')}")
    
    print(f"   NV-related warehouses: {len(nv_warehouses)}")
    for wh in nv_warehouses[:3]:
        print(f"     {wh.get('name')} - {wh.get('region')} - {wh.get('city')}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    print(traceback.format_exc())

print("\n=== DEBUGGING COMPLETE ===")