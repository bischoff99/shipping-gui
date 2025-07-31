#!/usr/bin/env python3
"""
Test script to validate actual order creation via web form
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
        os.chdir(r"C:\Users\Zubru\SHIPPING_GUI")
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Failed to start Flask server: {e}")
        return None

def test_order_creation():
    """Test the complete order creation workflow via web form POST"""
    base_url = "http://localhost:5000"
    
    print("Starting Flask server...")
    server_process = start_flask_server()
    
    if not server_process:
        print("Failed to start server")
        return
    
    # Give server time to start
    time.sleep(5)
    
    try:
        print("\n=== TESTING ACTUAL ORDER CREATION ===")
        
        # Test 1: Create order via web form (POST to /create_order)
        print("\n1. Testing order creation via web form:")
        
        # Test data - tab-separated format (corrected)
        customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
        
        form_data = {
            'customer_input': customer_input,
            'carrier': 'UPS'
        }
        
        try:
            response = requests.post(
                f"{base_url}/create_order",
                data=form_data,
                timeout=30,
                allow_redirects=False  # Don't follow redirects to see the response
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   SUCCESS: Order form processed")
                print(f"   Response length: {len(response.text)} characters")
                
                # Check if it's the success page
                if "order_success.html" in response.text or "Order created successfully" in response.text:
                    print("   ✓ Order creation appears successful")
                elif "error" in response.text.lower() or "failed" in response.text.lower():
                    print("   ⚠ Order creation may have encountered issues")
                    # Look for error messages
                    if "flash" in response.text:
                        print("   Flash messages may contain error details")
                else:
                    print("   ? Order creation status unclear from response")
                    
            elif response.status_code == 302:
                # Redirect - check location header
                location = response.headers.get('Location', 'No location header')
                print(f"   REDIRECT to: {location}")
                
                if "order_success" in location:
                    print("   ✓ Redirected to success page")
                else:
                    print("   ? Redirect destination unclear")
                    
            else:
                print(f"   ERROR: Unexpected status code")
                print(f"   Response: {response.text[:500]}...")
                
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 2: Try different carriers
        print("\n2. Testing different carriers:")
        
        carriers_to_test = ['FEDEX', 'UPS', 'DHL', 'USPS']
        
        for carrier in carriers_to_test:
            print(f"\n   Testing {carrier}:")
            
            form_data_carrier = {
                'customer_input': customer_input,
                'carrier': carrier
            }
            
            try:
                response = requests.post(
                    f"{base_url}/create_order",
                    data=form_data_carrier,
                    timeout=20,
                    allow_redirects=False
                )
                
                print(f"     Status: {response.status_code}")
                
                if response.status_code in [200, 302]:
                    print(f"     SUCCESS: {carrier} carrier processed")
                else:
                    print(f"     ERROR: {carrier} carrier failed")
                    
            except Exception as e:
                print(f"     ERROR: {e}")
        
        # Test 3: Test with invalid input
        print("\n3. Testing with invalid customer input:")
        
        invalid_inputs = [
            "",  # Empty input
            "invalid data",  # Invalid format
            "John Doe",  # Too few fields
        ]
        
        for i, invalid_input in enumerate(invalid_inputs, 1):
            print(f"\n   Invalid Test {i}: '{invalid_input}'")
            
            form_data_invalid = {
                'customer_input': invalid_input,
                'carrier': 'UPS'
            }
            
            try:
                response = requests.post(
                    f"{base_url}/create_order",
                    data=form_data_invalid,
                    timeout=15,
                    allow_redirects=False
                )
                
                print(f"     Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Should show error message
                    if "error" in response.text.lower() or "could not parse" in response.text.lower():
                        print("     ✓ Correctly handled invalid input with error message")
                    else:
                        print("     ⚠ Invalid input may not have been properly handled")
                else:
                    print(f"     ? Unexpected response to invalid input")
                    
            except Exception as e:
                print(f"     ERROR: {e}")
        
        print("\n=== ORDER CREATION TESTING COMPLETE ===")
        
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
    test_order_creation()