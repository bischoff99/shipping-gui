#!/usr/bin/env python3
"""
Demo script showing the unified system's customer parsing capabilities
This demonstrates the logic integrated from your existing GUI scripts
"""

from utils import parse_customer_input, format_customer_data


def demo_customer_parsing():
    """Demo the customer input parsing from your GUI scripts"""

    print("🧪 UNIFIED SYSTEM - CUSTOMER PARSING DEMO")
    print("=" * 50)

    # Test data from your existing scripts
    test_inputs = [
        # Tab-separated format (from your enhanced_routing_gui.py)
        "Jojet Gamboa\t+639691645226 embreikz123@gmail.com\tRSJF Apartelle B. Viscarra St Pasay City, Manila\t\tPasay\tManila\t1302\tPhilippines",
        # Space-separated format
        "John Doe +1234567890 john@email.com 123 Main St Boston MA 02101 US",
        # Another test case
        "Katherine Smith\t+15551234567 ksmith@email.com\t456 Oak Avenue\tApartment 2B\tLas Vegas\tNV\t89101\tUS",
    ]

    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n📋 TEST CASE {i}:")
        print(f"Input: {input_text[:80]}{'...' if len(input_text) > 80 else ''}")

        parsed = parse_customer_input(input_text)

        if parsed:
            print("✅ PARSING SUCCESSFUL!")
            print(
                f"Format Detected: {
                    parsed.get(
                        'detected_format',
                        'Unknown')}"
            )
            print(format_customer_data(parsed))
        else:
            print("❌ PARSING FAILED!")

    print(f"\n🎉 DEMO COMPLETE")
    print("✅ Customer parsing logic successfully integrated from your GUI scripts")
    print("🌐 Web interface running at: http://127.0.0.1:5000/")


if __name__ == "__main__":
    demo_customer_parsing()
