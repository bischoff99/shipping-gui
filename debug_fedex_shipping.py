#!/usr/bin/env python3
"""
Debug script for FedEx shipping function
This script helps activate debugging breakpoints and inspect variables in the create_fedex_shipment function.
"""

import os
import sys
import re

def activate_debug_breakpoints():
    """Activate all debug breakpoints in fedex_orders.py"""
    fedex_file_path = "/root/projects/SHIPPING_GUI/fedex_orders.py"
    
    # Read the file
    with open(fedex_file_path, 'r') as file:
        content = file.read()
    
    # Uncomment all pdb.set_trace() lines
    content = re.sub(r'# pdb\.set_trace\(\)', 'pdb.set_trace()', content)
    
    # Write back to file
    with open(fedex_file_path, 'w') as file:
        file.write(content)
    
    print("✅ All debug breakpoints activated in fedex_orders.py")
    print("🔍 Breakpoints are now active at:")
    print("   1. Function entry - inspect customer_data")
    print("   2. Origin address resolution")
    print("   3. Product retrieval")
    print("   4. Customer data formatting")
    print("   5. API response inspection")
    print("   6. FedEx booking response")

def deactivate_debug_breakpoints():
    """Deactivate all debug breakpoints in fedex_orders.py"""
    fedex_file_path = "/root/projects/SHIPPING_GUI/fedex_orders.py"
    
    # Read the file
    with open(fedex_file_path, 'r') as file:
        content = file.read()
    
    # Comment out all pdb.set_trace() lines
    content = re.sub(r'(\s+)pdb\.set_trace\(\)', r'\1# pdb.set_trace()', content)
    
    # Write back to file
    with open(fedex_file_path, 'w') as file:
        file.write(content)
    
    print("✅ All debug breakpoints deactivated in fedex_orders.py")

def test_fedex_shipping_with_debug():
    """Test FedEx shipping function with debug output"""
    print("🚀 Testing FedEx shipping function with debug output...")
    
    # Check if API key is available
    if not os.getenv('EASYSHIP_API_KEY'):
        print("⚠️ EASYSHIP_API_KEY not found - showing mock test instead")
        show_mock_debug_flow()
        return
    
    # Import the module
    sys.path.append('/root/projects/SHIPPING_GUI')
    try:
        from fedex_orders import FedExOrderProcessor
        
        # Create processor instance
        processor = FedExOrderProcessor()
        
        # Get first customer for testing
        customers = processor.get_fedex_customers()
        if not customers:
            print("❌ No FedEx customers available for testing")
            return
        
        test_customer = customers[0]  # Harry Armani
        print(f"🧪 Testing with customer: {test_customer['name']}")
        
        # Run the function (with debug output)
        result = processor.create_fedex_shipment(test_customer)
        
        print(f"📊 Final result: {result is not None}")
        if result:
            print(f"📊 Result structure: {list(result.keys())}")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("💡 Use mock test to see debug flow without API calls")

def show_mock_debug_flow():
    """Show what the debug output would look like"""
    print("\n📋 Mock Debug Flow (what you'd see with real API calls):")
    print("🔍 DEBUG: Starting create_fedex_shipment for customer: Harry Armani")
    print("🔍 DEBUG: customer_data keys: ['carrier', 'first_name', 'last_name', 'phone', 'email', 'name', 'address_1', 'address_2', 'city', 'state', 'postal_code', 'country']")
    print("🔍 DEBUG: Using origin_address_id: addr_12345")
    print("🔍 DEBUG: Retrieved 2 products")
    print("🔍 DEBUG: First product: {'title': 'Premium Fashion Item', 'weight': 0.5, 'price': 35.0}")
    print("🔍 DEBUG: Formatted customer data: {'name': 'Harry Armani', 'address_1': '2 Merestone Court', 'city': 'Birmingham', ...}")
    print("🔍 DEBUG: Shipment creation result: True")
    print("🔍 DEBUG: Result keys: ['shipment', 'rates']")
    print("🔍 DEBUG: Shipment ID: ship_67890")
    print("🔍 DEBUG: FedEx booking result: True")
    print("🔍 DEBUG: Booking keys: ['booking_id', 'tracking_number', 'label_url']")
    print("✅ FedEx shipment created and booked for Harry Armani")
    print("\n💡 At each DEBUG line, you could set a breakpoint to inspect variables in detail")

def show_debug_commands():
    """Show useful debugging commands for PDB"""
    print("🔧 Useful PDB debugging commands:")
    print("   l or list          - Show current code")
    print("   n or next          - Execute next line")
    print("   s or step          - Step into function calls")
    print("   c or continue      - Continue execution")
    print("   p <variable>       - Print variable value")
    print("   pp <variable>      - Pretty print variable")
    print("   locals()           - Show all local variables")
    print("   globals()          - Show all global variables")
    print("   type(<variable>)   - Show variable type")
    print("   dir(<variable>)    - Show variable attributes")
    print("   q or quit          - Quit debugger")
    print("")
    print("🔍 Key variables to inspect:")
    print("   customer_data      - Input customer information")
    print("   origin_address_id  - Resolved origin address")
    print("   products           - Retrieved products for shipment")
    print("   formatted_customer - Normalized customer data")
    print("   result             - API response from create_shipment")
    print("   fedex_booking      - Response from FedEx booking")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug FedEx shipping function")
    parser.add_argument("--activate", action="store_true", help="Activate debug breakpoints")
    parser.add_argument("--deactivate", action="store_true", help="Deactivate debug breakpoints")
    parser.add_argument("--test", action="store_true", help="Test shipping function with debug output")
    parser.add_argument("--help-debug", action="store_true", help="Show debugging commands")
    
    args = parser.parse_args()
    
    if args.activate:
        activate_debug_breakpoints()
    elif args.deactivate:
        deactivate_debug_breakpoints()
    elif args.test:
        test_fedex_shipping_with_debug()
    elif args.help_debug:
        show_debug_commands()
    else:
        print("FedEx Shipping Debug Helper")
        print("Usage:")
        print("  python debug_fedex_shipping.py --activate     # Activate breakpoints")
        print("  python debug_fedex_shipping.py --test         # Test with debug output")
        print("  python debug_fedex_shipping.py --help-debug   # Show PDB commands")
        print("  python debug_fedex_shipping.py --deactivate   # Deactivate breakpoints")