#!/usr/bin/env python3
"""
Debug validation to see what's failing in order creation
"""

import os
from dotenv import load_dotenv

load_dotenv()

from utils import parse_customer_input, normalize_customer_data
from validation import validate_order_data
from api.veeqo_api import VeeqoAPI
from routing import OrderRoutingSystem

print("=== DEBUGGING VALIDATION PROCESS ===")

# Test the exact same data that was sent via form
customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"

print("1. Parsing customer input...")
customer_data = parse_customer_input(customer_input)
print(f"   Parsed: {customer_data}")

if customer_data:
    print("\n2. Normalizing customer data...")
    customer_data = normalize_customer_data(customer_data)
    print(f"   Normalized: {customer_data}")
    
    print("\n3. Getting warehouses and products...")
    try:
        veeqo_api = VeeqoAPI()
        routing_system = OrderRoutingSystem()
        
        # Get warehouses (like in app.py get_warehouses_and_products function)
        warehouses = veeqo_api.get_warehouses()
        products = veeqo_api.get_random_products(3)
        
        print(f"   Found {len(warehouses)} warehouses")
        print(f"   Found {len(products)} products")
        
        print("\n4. Getting routing decision...")
        routing_decision = routing_system.route_order(customer_data, warehouses)
        print(f"   Platform: {routing_decision.platform}")
        print(f"   Carrier: {routing_decision.carrier}")
        print(f"   Warehouse: {routing_decision.warehouse_info}")
        
        print("\n5. Validating order data...")
        validation_result = validate_order_data(
            customer_data, 
            routing_decision.warehouse_info, 
            products
        )
        
        print(f"   Is Valid: {validation_result.is_valid}")
        print(f"   Errors: {validation_result.errors}")
        print(f"   Warnings: {validation_result.warnings}")
        
        if validation_result.is_valid:
            print("\n6. Testing order creation...")
            # This is what would happen in create_platform_order
            if routing_decision.platform == "EASYSHIP":
                print("   Would create EASYSHIP order")
            else:
                print("   Would create VEEQO order")
                
                # Test the exact same logic as app.py create_platform_order
                warehouse = veeqo_api.get_warehouse_by_state("NV") or veeqo_api.get_warehouse_by_state("CA")
                if warehouse:
                    warehouse_id = warehouse.get("id")
                    print(f"   Found warehouse: {warehouse.get('name')} (ID: {warehouse_id})")
                    
                    if warehouse_id is not None:
                        try:
                            result = veeqo_api.create_order(
                                customer_data,
                                products,
                                warehouse_id,
                                routing_decision.carrier,
                            )
                            if result:
                                print("   SUCCESS: Order creation SUCCESSFUL")
                                print(f"   Order result: {result}")
                            else:
                                print("   FAILED: Order creation FAILED - API returned None")
                        except Exception as e:
                            print(f"   FAILED: Order creation FAILED - Exception: {e}")
                    else:
                        print("   FAILED: Warehouse ID is None")
                else:
                    print("   FAILED: No suitable warehouse found")
        else:
            print("\n   VALIDATION FAILED - Order would not be created")
            
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        print(traceback.format_exc())

else:
    print("   FAILED - Could not parse customer input")

print("\n=== DEBUGGING COMPLETE ===")