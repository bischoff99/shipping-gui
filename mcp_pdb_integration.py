#!/usr/bin/env python3
"""
MCP-PDB Integration Helper for FedEx Shipping Debug

This script demonstrates how to integrate the debugging setup with MCP-PDB
when the MCP-PDB server is active and available.
"""

import json
import sys
import os

def check_mcp_pdb_availability():
    """Check if MCP-PDB tools are available"""
    # This would normally check the MCP server status
    # For now, we'll check the permissions in the settings file
    
    settings_path = "/root/projects/SHIPPING_GUI/.claude/settings.local.json"
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        mcp_pdb_permissions = [
            perm for perm in settings.get('permissions', {}).get('allow', [])
            if 'mcp-pdb' in perm
        ]
        
        print("🔍 MCP-PDB Permissions Found:")
        for perm in mcp_pdb_permissions:
            print(f"   - {perm}")
        
        return len(mcp_pdb_permissions) > 0
    except Exception as e:
        print(f"❌ Error checking MCP-PDB availability: {e}")
        return False

def show_mcp_pdb_integration_example():
    """Show how to integrate with MCP-PDB when available"""
    print("\n🚀 MCP-PDB Integration Example:")
    print("When MCP-PDB server is active, you can use these commands:")
    
    print("\n1. Start debugging session:")
    print("   mcp__mcp-pdb__start_debug('fedex_orders.py')")
    
    print("\n2. Set breakpoints at strategic locations:")
    print("   # At function entry (line ~136)")
    print("   mcp__mcp-pdb__send_pdb_command('b 136')")
    print("   # At product retrieval (line ~167)")
    print("   mcp__mcp-pdb__send_pdb_command('b 167')")
    print("   # At API response (line ~220)")
    print("   mcp__mcp-pdb__send_pdb_command('b 220')")
    
    print("\n3. Run the function:")
    print("   # Execute the create_fedex_shipment function")
    print("   mcp__mcp-pdb__send_pdb_command('c')")
    
    print("\n4. Inspect variables at breakpoints:")
    print("   mcp__mcp-pdb__examine_variable('customer_data')")
    print("   mcp__mcp-pdb__examine_variable('products')")
    print("   mcp__mcp-pdb__examine_variable('result')")
    
    print("\n5. Get debug status:")
    print("   mcp__mcp-pdb__get_debug_status()")
    
    print("\n6. End debugging session:")
    print("   mcp__mcp-pdb__end_debug()")

def create_debug_session_script():
    """Create a script that can be used with MCP-PDB"""
    script_content = '''# MCP-PDB Debug Session Script for FedEx Shipping
# Use this script when MCP-PDB server is active

# 1. Start debug session
mcp__mcp-pdb__start_debug("fedex_orders.py")

# 2. Set strategic breakpoints
mcp__mcp-pdb__send_pdb_command("b 136")  # Function entry
mcp__mcp-pdb__send_pdb_command("b 167")  # Product retrieval
mcp__mcp-pdb__send_pdb_command("b 220")  # API response

# 3. Run the test
# (Execute your FedEx shipping function here)

# 4. At each breakpoint, examine key variables:
# mcp__mcp-pdb__examine_variable("customer_data")
# mcp__mcp-pdb__examine_variable("products") 
# mcp__mcp-pdb__examine_variable("result")
# mcp__mcp-pdb__examine_variable("fedex_booking")

# 5. Continue execution
# mcp__mcp-pdb__send_pdb_command("c")

# 6. End session when done
# mcp__mcp-pdb__end_debug()
'''
    
    script_path = "/root/projects/SHIPPING_GUI/mcp_debug_session.txt"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"📝 Created MCP-PDB session script: {script_path}")

def show_debug_variable_mapping():
    """Show which variables to inspect at each breakpoint"""
    print("\n🔍 Variable Inspection Guide by Breakpoint:")
    
    breakpoints = {
        "Breakpoint 1 (Line ~136)": [
            "customer_data - Input customer information",
            "origin_address_id - Address parameter (may be None)",
            "self.easyship_api - API instance"
        ],
        "Breakpoint 2 (Line ~157)": [
            "origin_address_id - Resolved address ID",
            "addresses - Available addresses from API",
            "addr - Current address being processed"
        ],
        "Breakpoint 3 (Line ~167)": [
            "products - Retrieved products list",
            "len(products) - Number of products",
            "products[0] - First product details"
        ],
        "Breakpoint 4 (Line ~207)": [
            "formatted_customer - Normalized customer data",
            "customer_data - Original customer data",
            "Comparison between original and formatted"
        ],
        "Breakpoint 5 (Line ~220)": [
            "result - Complete API response",
            "result.keys() - Response structure",
            "result['shipment']['id'] - Shipment ID"
        ],
        "Breakpoint 6 (Line ~233)": [
            "fedex_booking - Booking response",
            "shipment_id - ID used for booking",
            "fedex_booking.keys() - Booking structure"
        ]
    }
    
    for bp, variables in breakpoints.items():
        print(f"\n{bp}:")
        for var in variables:
            print(f"   • {var}")

if __name__ == "__main__":
    print("🔧 MCP-PDB Integration Helper for FedEx Shipping Debug\n")
    
    # Check availability
    is_available = check_mcp_pdb_availability()
    
    if is_available:
        print("✅ MCP-PDB permissions are configured")
        show_mcp_pdb_integration_example()
        create_debug_session_script()
    else:
        print("⚠️ MCP-PDB permissions not found or server not active")
        print("💡 Use the standard PDB debugging setup with debug_fedex_shipping.py")
    
    show_debug_variable_mapping()
    
    print("\n📚 Next Steps:")
    print("1. Use debug_fedex_shipping.py for immediate debugging")
    print("2. When MCP-PDB is active, use the integration commands above")
    print("3. Follow the variable inspection guide for thorough debugging")
    print("4. Check FEDEX_DEBUG_GUIDE.md for complete documentation")