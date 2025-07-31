#!/usr/bin/env python3
"""
Detailed test of order creation to see what's actually happening
"""

import requests
import time
import subprocess
import sys
import os

def start_flask_server():
    """Start the Flask server"""
    try:
        os.chdir(r"C:\Users\Zubru\SHIPPING_GUI")
        process = subprocess.Popen([sys.executable, "app.py"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Failed to start Flask server: {e}")
        return None

def test_detailed_order():
    """Test order creation in detail"""
    base_url = "http://localhost:5000"
    
    print("Starting Flask server...")
    server_process = start_flask_server()
    
    if not server_process:
        return
    
    time.sleep(5)
    
    try:
        print("\n=== DETAILED ORDER CREATION TEST ===")
        
        # Valid customer data
        customer_input = "John Doe\t555-123-4567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"
        
        form_data = {
            'customer_input': customer_input,
            'carrier': 'UPS'
        }
        
        print("\n1. Creating order with valid data:")
        print(f"   Customer: {customer_input[:50]}...")
        print(f"   Carrier: UPS")
        
        response = requests.post(f"{base_url}/create_order", data=form_data, timeout=30)
        
        print(f"   Status: {response.status_code}")
        
        # Check for specific indicators in the response
        response_text = response.text
        
        # Look for success indicators
        success_indicators = [
            "Order created successfully",
            "order_success.html",
            "success",
            "Order ID:",
            "created"
        ]
        
        error_indicators = [
            "error",
            "failed",
            "could not parse",
            "Invalid",
            "Error"
        ]
        
        print("\n   Checking response content:")
        
        found_success = False
        found_error = False
        
        for indicator in success_indicators:
            if indicator.lower() in response_text.lower():
                print(f"   FOUND SUCCESS: '{indicator}'")
                found_success = True
        
        for indicator in error_indicators:
            if indicator.lower() in response_text.lower():
                print(f"   FOUND ERROR: '{indicator}'")
                found_error = True
        
        if found_success and not found_error:
            print("   RESULT: Order creation appears SUCCESSFUL")
        elif found_error and not found_success:
            print("   RESULT: Order creation FAILED")
        elif found_success and found_error:
            print("   RESULT: Mixed signals - order may have partial success")
        else:
            print("   RESULT: Unclear - returned to form page")
            
        # Check if we got redirected back to the form (indicating failure)
        if "create_order.html" in response_text or "customer_input" in response_text:
            print("   NOTE: Returned to order form (may indicate validation issue)")
        
        # Look for specific form elements that would indicate we're back at the form
        if '<form' in response_text and 'customer_input' in response_text:
            print("   ANALYSIS: Back at the form page")
            
            # Look for any flash messages
            if 'flash' in response_text.lower() or 'alert' in response_text.lower():
                print("   NOTE: May contain flash messages with error details")
        
        # Test invalid data
        print("\n2. Testing with invalid data:")
        invalid_form = {
            'customer_input': 'invalid',
            'carrier': 'UPS'
        }
        
        response = requests.post(f"{base_url}/create_order", data=invalid_form, timeout=20)
        print(f"   Status: {response.status_code}")
        
        if "could not parse" in response.text.lower() or "please enter" in response.text.lower():
            print("   RESULT: Correctly handled invalid input")
        else:
            print("   RESULT: Invalid input handling unclear")
        
        print("\n=== TEST COMPLETE ===")
        
    finally:
        if server_process:
            print("\nStopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    test_detailed_order()