#!/usr/bin/env python3
"""
Test script to validate the complete order creation workflow
"""

import requests
import json
import time
from threading import Thread
import subprocess
import sys
import os

def start_flask_server():
    """Start the Flask server in a separate process"""
    try:
        # Change to the correct directory
        os.chdir(r"C:\Users\Zubru\SHIPPING_GUI")
        
        # Start the Flask server
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return process
    except Exception as e:
        print(f"Failed to start Flask server: {e}")
        return None

def test_api_endpoints():
    """Test all the critical API endpoints"""
    base_url = "http://localhost:5000"
    
    # Wait for server to start
    print("Starting Flask server...")
    server_process = start_flask_server()
    
    if not server_process:
        print("Failed to start server")
        return
    
    # Give server time to start
    time.sleep(5)
    
    try:
        print("\n=== TESTING ORDER CREATION WORKFLOW ===")
        
        # Test 1: Parse customer data
        print("\n1. Testing customer parsing API:")
        customer_data = {
            "input": "John Doe\t5551234567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/parse_customer",
                json=customer_data,
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: {result['status']}")
                parsed_data = result.get('data', {})
                print(f"   Parsed Name: {parsed_data.get('name', 'N/A')}")
                print(f"   Parsed Email: {parsed_data.get('email', 'N/A')}")
                print(f"   Parsed City: {parsed_data.get('city', 'N/A')}")
            else:
                print(f"   ERROR: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 2: Get products
        print("\n2. Testing products API:")
        try:
            response = requests.get(f"{base_url}/api/get_products?platform=VEEQO&count=3", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: Found {result.get('count', 0)} products")
                products = result.get('products', [])
                for i, product in enumerate(products[:2], 1):
                    print(f"   Product {i}: {product.get('title', 'No title')} - ${product.get('price', 'No price')}")
            else:
                print(f"   ERROR: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 3: Get routing decision
        print("\n3. Testing routing API:")
        routing_data = {
            "customer_data": {
                "name": "John Doe",
                "email": "john@email.com",
                "address_1": "123 Main St",
                "city": "Anywhere",
                "state": "CA",
                "postal_code": "90210",
                "country": "US"
            },
            "carrier": "UPS"
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/get_routing",
                json=routing_data,
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: {result['status']}")
                routing = result.get('routing', {})
                print(f"   Platform: {routing.get('platform', 'N/A')}")
                print(f"   Carrier: {routing.get('carrier', 'N/A')}")
                print(f"   Warehouse: {routing.get('warehouse', 'N/A')}")
                print(f"   Confidence: {routing.get('confidence', 'N/A')}")
            else:
                print(f"   ERROR: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 4: Test sync functionality
        print("\n4. Testing sync API:")
        try:
            response = requests.get(f"{base_url}/sync_data", timeout=20)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS: {result['status']}")
                print(f"   Veeqo warehouses: {result.get('veeqo_warehouses', 0)}")
                print(f"   Veeqo products: {result.get('veeqo_products', 0)}")
                print(f"   Easyship addresses: {result.get('easyship_addresses', 0)}")
                print(f"   Easyship products: {result.get('easyship_products', 0)}")
            else:
                print(f"   ERROR: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 5: Test dashboard
        print("\n5. Testing dashboard:")
        try:
            response = requests.get(f"{base_url}/dashboard", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   SUCCESS: Dashboard loads correctly")
            else:
                print(f"   ERROR: {response.status_code}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 6: Test main order creation page
        print("\n6. Testing main order creation page:")
        try:
            response = requests.get(f"{base_url}/create_order", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   SUCCESS: Order creation page loads correctly")
                print(f"   Page length: {len(response.text)} characters")
            else:
                print(f"   ERROR: {response.status_code}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        print("\n=== WORKFLOW TESTING COMPLETE ===")
        
    finally:
        # Clean up
        if server_process:
            print("\nStopping Flask server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    test_api_endpoints()