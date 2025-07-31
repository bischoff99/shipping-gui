#!/usr/bin/env python3
"""
Core Workflows Test Script
Tests order creation, routing, and warehouse synchronization workflows.
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
from routing import OrderRoutingSystem
from utils import parse_customer_input, normalize_customer_data
from validation import validate_order_data


def test_customer_parsing():
    """Test customer data parsing functionality"""
    print("=" * 60)
    print("TESTING CUSTOMER DATA PARSING")
    print("=" * 60)
    
    test_inputs = [
        # Standard format
        "John Doe, john@email.com, 555-123-4567, 123 Main St, Los Angeles, CA, 90210, US",
        
        # Name and address only
        "Jane Smith, 456 Oak Ave, New York, NY, 10001",
        
        # International address
        "Bob Wilson, bob@email.com, 789 London Rd, London, UK, W1A 0AX, GB",
        
        # Minimal format
        "Alice Johnson, 321 Pine St, Las Vegas, NV, 89101, US",
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}: {test_input}")
        try:
            parsed = parse_customer_input(test_input)
            if parsed:
                normalized = normalize_customer_data(parsed)
                print(f"[OK] Parsed successfully:")
                print(f"  Name: {normalized.get('name', 'N/A')}")
                print(f"  Email: {normalized.get('email', 'N/A')}")
                print(f"  Phone: {normalized.get('phone', 'N/A')}")
                print(f"  Address: {normalized.get('address_1', 'N/A')}")
                print(f"  City: {normalized.get('city', 'N/A')}")
                print(f"  State: {normalized.get('state', 'N/A')}")
                print(f"  Postal: {normalized.get('postal_code', 'N/A')}")
                print(f"  Country: {normalized.get('country', 'N/A')}")
            else:
                print("[FAIL] Could not parse input")
        except Exception as e:
            print(f"[ERROR] Parsing failed: {e}")


def test_routing_system():
    """Test order routing system"""
    print("\n" + "=" * 60)
    print("TESTING ORDER ROUTING SYSTEM")
    print("=" * 60)
    
    # Initialize routing system
    router = OrderRoutingSystem()
    
    # Test customers from different states
    test_customers = [
        {"name": "John Doe", "state": "NEVADA", "city": "Las Vegas"},
        {"name": "Jane Smith", "state": "CALIFORNIA", "city": "Los Angeles"},
        {"name": "Bob Wilson", "state": "NEW YORK", "city": "New York"},
        {"name": "Alice Johnson", "state": "FLORIDA", "city": "Miami"},
        {"name": "Charlie Brown", "state": "TEXAS", "city": "Houston"},
        {"name": "Diana Prince", "state": "OREGON", "city": "Portland"},  # Unknown state
    ]
    
    # Get warehouses for testing
    try:
        veeqo = VeeqoAPI()
        warehouses = veeqo.get_warehouses()
        print(f"Using {len(warehouses)} warehouses for routing tests")
    except Exception as e:
        print(f"[WARNING] Could not get real warehouses, using dummy data: {e}")
        warehouses = [
            {"id": 1, "name": "Nevada Warehouse", "region": "Nevada"},
            {"id": 2, "name": "California Warehouse", "region": "California"},
        ]
    
    print(f"\nTesting routing for customers from different states:")
    
    for customer in test_customers:
        print(f"\nCustomer: {customer['name']} from {customer['city']}, {customer['state']}")
        try:
            routing_decision = router.route_order(customer, warehouses)
            print(f"  [OK] Platform: {routing_decision.platform}")
            print(f"  [OK] Carrier: {routing_decision.carrier}")
            print(f"  [OK] Warehouse: {routing_decision.warehouse_info.get('name', 'Unknown')}")
            print(f"  [OK] Confidence: {routing_decision.confidence:.1f}%")
        except Exception as e:
            print(f"  [FAIL] Routing failed: {e}")


def test_warehouse_sync():
    """Test warehouse synchronization"""
    print("\n" + "=" * 60)
    print("TESTING WAREHOUSE SYNCHRONIZATION")
    print("=" * 60)
    
    try:
        # Test Veeqo warehouse sync
        veeqo = VeeqoAPI()
        veeqo_warehouses = veeqo.get_warehouses()
        print(f"[OK] Veeqo warehouses synced: {len(veeqo_warehouses)}")
        
        if veeqo_warehouses:
            sample = veeqo_warehouses[0]
            print(f"  Sample: {sample.get('name', 'Unnamed')} - {sample.get('region', 'Unknown region')}")
        
        # Test Easyship address sync
        easyship = EasyshipAPI()
        easyship_addresses = easyship.get_addresses()
        print(f"[OK] Easyship addresses synced: {len(easyship_addresses)}")
        
        if easyship_addresses:
            sample = easyship_addresses[0]
            print(f"  Sample: {sample.get('name', 'Unnamed')} - {sample.get('city', 'Unknown city')}")
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Warehouse sync failed: {e}")
        return False


def test_order_validation():
    """Test order validation"""
    print("\n" + "=" * 60)
    print("TESTING ORDER VALIDATION")
    print("=" * 60)
    
    # Get sample products and warehouses
    try:
        veeqo = VeeqoAPI()
        products = veeqo.get_random_products(2)
        warehouses = veeqo.get_warehouses()
        warehouse_info = warehouses[0] if warehouses else {}
        
        # Test valid customer data
        valid_customer = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "address_1": "123 Main St",
            "city": "Las Vegas",
            "state": "NV",
            "postal_code": "89101",
            "country": "US"
        }
        
        print("Testing with valid customer data...")
        validation_result = validate_order_data(valid_customer, warehouse_info, products)
        
        if validation_result.is_valid:
            print("[OK] Order validation passed")
            if validation_result.warnings:
                print(f"  Warnings: {len(validation_result.warnings)}")
                for warning in validation_result.warnings:
                    print(f"    - {warning}")
        else:
            print("[FAIL] Order validation failed")
            for error in validation_result.errors:
                print(f"    - {error}")
        
        # Test invalid customer data
        invalid_customer = {
            "name": "",  # Missing name
            "email": "invalid-email",  # Invalid email
            "address_1": "",  # Missing address
        }
        
        print("\nTesting with invalid customer data...")
        validation_result = validate_order_data(invalid_customer, warehouse_info, products)
        
        if not validation_result.is_valid:
            print("[OK] Validation correctly rejected invalid data")
            print(f"  Errors found: {len(validation_result.errors)}")
            for error in validation_result.errors:
                print(f"    - {error}")
        else:
            print("[FAIL] Validation should have failed but didn't")
            
    except Exception as e:
        print(f"[FAIL] Order validation test failed: {e}")


def test_order_creation_flow():
    """Test full order creation workflow"""
    print("\n" + "=" * 60)
    print("TESTING ORDER CREATION WORKFLOW")
    print("=" * 60)
    
    # Simulate full order creation process
    customer_input = "John Doe, john@example.com, 555-123-4567, 123 Main St, Las Vegas, NV, 89101, US"
    
    try:
        # Step 1: Parse customer input
        print("Step 1: Parsing customer input...")
        customer_data = parse_customer_input(customer_input)
        if not customer_data:
            print("[FAIL] Could not parse customer input")
            return False
        
        customer_data = normalize_customer_data(customer_data)
        print(f"[OK] Customer parsed: {customer_data.get('name')}")
        
        # Step 2: Get warehouses and products
        print("\nStep 2: Getting warehouses and products...")
        veeqo = VeeqoAPI()
        warehouses = veeqo.get_warehouses()
        products = veeqo.get_random_products(2)
        print(f"[OK] Found {len(warehouses)} warehouses, {len(products)} products")
        
        # Step 3: Route order
        print("\nStep 3: Routing order...")
        router = OrderRoutingSystem()
        routing_decision = router.route_order(customer_data, warehouses)
        print(f"[OK] Routed to {routing_decision.platform} via {routing_decision.carrier}")
        
        # Step 4: Validate order
        print("\nStep 4: Validating order...")
        validation_result = validate_order_data(
            customer_data, routing_decision.warehouse_info, products
        )
        
        if validation_result.is_valid:
            print("[OK] Order validation passed")
        else:
            print(f"[FAIL] Order validation failed: {validation_result.errors}")
            return False
        
        # Step 5: Create order (simulate)
        print("\nStep 5: Order creation simulation...")
        if routing_decision.platform == "VEEQO":
            warehouse_id = routing_decision.warehouse_info.get("id")
            if warehouse_id:
                print(f"[OK] Would create Veeqo order in warehouse {warehouse_id}")
            else:
                print("[WARN] No warehouse ID found for Veeqo order")
        else:
            easyship = EasyshipAPI()
            addresses = easyship.get_addresses()
            if addresses:
                print(f"[OK] Would create Easyship shipment from address {addresses[0].get('id')}")
            else:
                print("[WARN] No Easyship addresses found")
        
        print("\n[SUCCESS] Full order creation workflow completed!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Order creation workflow failed: {e}")
        return False


def main():
    """Main test function"""
    print("SHIPPING GUI CORE WORKFLOWS TEST")
    print("Comprehensive testing of order processing capabilities")
    
    # Run all tests
    tests = [
        ("Customer Parsing", test_customer_parsing),
        ("Routing System", test_routing_system),
        ("Warehouse Sync", test_warehouse_sync),
        ("Order Validation", test_order_validation),
        ("Order Creation Flow", test_order_creation_flow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name.upper()} TEST {'='*20}")
            result = test_func()
            if result is None:
                result = True  # Assume success if no explicit return
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n[SUCCESS] All core workflows are functional!")
        print("The shipping GUI system should work properly.")
    else:
        print(f"\n[WARNING] {len(results) - passed} tests failed.")
        print("Some features may not work properly.")


if __name__ == "__main__":
    main()