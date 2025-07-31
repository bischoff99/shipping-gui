#!/usr/bin/env python3
"""
API Connectivity Test Script
Tests both Veeqo and Easyship API connections to identify connectivity issues.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.veeqo_api import VeeqoAPI
from api.easyship_api import EasyshipAPI


def test_veeqo_api():
    """Test Veeqo API connectivity"""
    print("Testing Veeqo API...")
    
    try:
        veeqo = VeeqoAPI()
        print(f"[OK] Veeqo API initialized with key: {veeqo.api_key[:10]}...")
        
        # Test basic connectivity
        warehouses = veeqo.get_warehouses()
        if warehouses is not None:
            print(f"[OK] Veeqo API connected successfully! Found {len(warehouses)} warehouses")
            if warehouses:
                print(f"   Sample warehouse: {warehouses[0].get('name', 'Unnamed')}")
            return True, warehouses
        else:
            print("[FAIL] Veeqo API connection failed - no warehouses returned")
            return False, None
            
    except ValueError as e:
        if "VEEQO_API_KEY" in str(e):
            print("[FAIL] Veeqo API Key missing from environment variables")
        else:
            print(f"[FAIL] Veeqo API ValueError: {e}")
        return False, None
    except Exception as e:
        print(f"[FAIL] Veeqo API Error: {e}")
        return False, None


def test_easyship_api():
    """Test Easyship API connectivity"""
    print("\nTesting Easyship API...")
    
    try:
        easyship = EasyshipAPI()
        print(f"[OK] Easyship API initialized with key: {easyship.api_key[:10]}...")
        
        # Test basic connectivity
        addresses = easyship.get_addresses()
        if addresses is not None:
            print(f"[OK] Easyship API connected successfully! Found {len(addresses)} addresses")
            if addresses:
                print(f"   Sample address: {addresses[0].get('name', 'Unnamed')}")
            return True, addresses
        else:
            print("[FAIL] Easyship API connection failed - no addresses returned")
            return False, None
            
    except ValueError as e:
        if "EASYSHIP_API_KEY" in str(e):
            print("[FAIL] Easyship API Key missing from environment variables")
        else:
            print(f"[FAIL] Easyship API ValueError: {e}")
        return False, None
    except Exception as e:
        print(f"[FAIL] Easyship API Error: {e}")
        return False, None


def test_products():
    """Test product retrieval from both APIs"""
    print("\nTesting Product Retrieval...")
    
    # Test Veeqo products
    try:
        veeqo = VeeqoAPI()
        veeqo_products = veeqo.get_random_products(3)
        print(f"[OK] Veeqo products: {len(veeqo_products)} retrieved")
        if veeqo_products:
            print(f"   Sample: {veeqo_products[0].get('title', 'Unnamed')}")
    except Exception as e:
        print(f"[FAIL] Veeqo products error: {e}")
    
    # Test Easyship products
    try:
        easyship = EasyshipAPI()
        easyship_products = easyship.get_random_products(3)
        print(f"[OK] Easyship products: {len(easyship_products)} retrieved")
        if easyship_products:
            print(f"   Sample: {easyship_products[0].get('title', 'Unnamed')}")
    except Exception as e:
        print(f"[FAIL] Easyship products error: {e}")


def main():
    """Main test function"""
    print("=" * 60)
    print("SHIPPING GUI API CONNECTIVITY TEST")
    print("=" * 60)
    
    # Check environment variables
    print("Environment Variables Check:")
    veeqo_key = os.environ.get("VEEQO_API_KEY")
    easyship_key = os.environ.get("EASYSHIP_API_KEY")
    
    if veeqo_key:
        print(f"[OK] VEEQO_API_KEY: Present ({len(veeqo_key)} chars)")
    else:
        print("[FAIL] VEEQO_API_KEY: Missing")
        
    if easyship_key:
        print(f"[OK] EASYSHIP_API_KEY: Present ({len(easyship_key)} chars)")
    else:
        print("[FAIL] EASYSHIP_API_KEY: Missing")
    
    # Test APIs
    veeqo_success, veeqo_warehouses = test_veeqo_api()
    easyship_success, easyship_addresses = test_easyship_api()
    
    # Test products
    test_products()
    
    # Summary
    print("\n" + "=" * 60)
    print("CONNECTIVITY TEST SUMMARY")
    print("=" * 60)
    
    if veeqo_success:
        print(f"[OK] Veeqo API: CONNECTED ({len(veeqo_warehouses or [])} warehouses)")
    else:
        print("[FAIL] Veeqo API: FAILED")
        
    if easyship_success:
        print(f"[OK] Easyship API: CONNECTED ({len(easyship_addresses or [])} addresses)")
    else:
        print("[FAIL] Easyship API: FAILED")
    
    if veeqo_success and easyship_success:
        print("\n[SUCCESS] All APIs are working! The system should be functional.")
    elif veeqo_success or easyship_success:
        print("\n[WARNING] Partial connectivity - some features may not work.")
    else:
        print("\n[ERROR] No API connectivity - system will not work properly.")
        print("   Check your API keys and network connection.")


if __name__ == "__main__":
    main()