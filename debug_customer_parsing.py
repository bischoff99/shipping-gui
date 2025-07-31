#!/usr/bin/env python3
"""
Debug script to test customer parsing API functionality
"""

import os
import json
from dotenv import load_dotenv

print("=== DEBUGGING CUSTOMER PARSING API ===")

# Load environment variables
load_dotenv()

# Test customer parsing function directly
from utils import parse_customer_input, normalize_customer_data

test_inputs = [
    # Tab-separated format
    "John Doe\t5551234567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS",
    
    # Comma-separated format
    "Jane Smith, 123 Oak Ave, Los Angeles, CA, 90210, US, jane@email.com, +1-555-987-6543",
    
    # Space-separated format  
    "Bob Johnson +1-555-123-4567 bob@email.com 456 Pine St Seattle WA 98101",
    
    # Invalid format
    "Invalid data",
    
    # Empty input
    ""
]

print("1. Testing parse_customer_input function:")
for i, test_input in enumerate(test_inputs, 1):
    print(f"\n   Test {i}: '{test_input[:50]}{'...' if len(test_input) > 50 else ''}'")
    try:
        result = parse_customer_input(test_input)
        if result:
            print(f"   SUCCESS - Parsed successfully:")
            print(f"     Name: {result.get('name', 'N/A')}")
            print(f"     Email: {result.get('email', 'N/A')}")
            print(f"     Phone: {result.get('phone', 'N/A')}")
            print(f"     City: {result.get('city', 'N/A')}")
            print(f"     State: {result.get('state', 'N/A')}")
            print(f"     Format: {result.get('detected_format', 'N/A')}")
        else:
            print("   FAILED - Failed to parse")
    except Exception as e:
        print(f"   ERROR - Error: {e}")

print("\n2. Testing API endpoint simulation:")

# Simulate the API endpoint logic
def simulate_api_parse_customer(input_data):
    """Simulate the /api/parse_customer endpoint"""
    try:
        if not input_data or "input" not in input_data:
            return {
                "status": "error",
                "message": "Invalid or missing JSON input"
            }, 400
        
        customer_input = input_data.get("input", "")
        parsed = parse_customer_input(customer_input)
        
        if parsed:
            return {"status": "success", "data": parsed}, 200
        else:
            return {
                "status": "error", 
                "message": "Could not parse input"
            }, 400
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

# Test API endpoint scenarios
api_test_cases = [
    # Valid JSON with valid input
    {"input": "John Doe\t5551234567\tjohn@email.com\t123 Main St\t\tAnywhere\tCA\t90210\tUS"},
    
    # Valid JSON with invalid input
    {"input": "invalid"},
    
    # Missing input field
    {"data": "some data"},
    
    # Empty input
    {"input": ""},
    
    # No JSON (None)
    None
]

for i, test_case in enumerate(api_test_cases, 1):
    print(f"\n   API Test {i}: {json.dumps(test_case) if test_case else 'None'}")
    try:
        response, status_code = simulate_api_parse_customer(test_case)
        print(f"   Status: {status_code}")
        print(f"   Response: {json.dumps(response, indent=2)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

print("\n=== DEBUGGING COMPLETE ===")