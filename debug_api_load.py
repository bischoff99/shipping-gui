#!/usr/bin/env python3
"""
Debug script to test API loading and environment variables
"""

import os
from dotenv import load_dotenv

print("=== DEBUGGING API LOADING ===")

# Load environment variables
print("1. Loading .env file...")
load_dotenv()

# Check environment variables
print("2. Checking environment variables:")
veeqo_key = os.environ.get("VEEQO_API_KEY")
easyship_key = os.environ.get("EASYSHIP_API_KEY")
print(f"   VEEQO_API_KEY: {'Present' if veeqo_key else 'Missing'}")
print(f"   EASYSHIP_API_KEY: {'Present' if easyship_key else 'Missing'}")

if veeqo_key:
    print(f"   VEEQO_API_KEY length: {len(veeqo_key)}")
if easyship_key:
    print(f"   EASYSHIP_API_KEY length: {len(easyship_key)}")

# Test API imports
print("3. Testing API imports:")
try:
    from api.veeqo_api import VeeqoAPI
    print("   VeeqoAPI imported successfully")
    
    # Test API initialization
    veeqo_api = VeeqoAPI()
    print("   VeeqoAPI initialized successfully")
    
    # Test connection
    result = veeqo_api.make_request("/warehouses")
    if result:
        print(f"   Veeqo API connection successful - Found {len(result)} warehouses")
    else:
        print("   Veeqo API connection failed or returned empty")
        
except Exception as e:
    print(f"   VeeqoAPI error: {e}")

try:
    from api.easyship_api import EasyshipAPI
    print("   EasyshipAPI imported successfully")
    
    # Test API initialization
    easyship_api = EasyshipAPI()
    print("   EasyshipAPI initialized successfully")
    
    # Test connection
    result = easyship_api.get_addresses()
    if result:
        print(f"   Easyship API connection successful - Found {len(result)} addresses")
    else:
        print("   Easyship API connection failed or returned empty")
        
except Exception as e:
    print(f"   EasyshipAPI error: {e}")

print("=== DEBUGGING COMPLETE ===")