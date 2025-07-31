#!/usr/bin/env python3
"""
Example integration of the enhanced AI-powered customer input parsing system.

This script demonstrates how to integrate the new parsing capabilities into
existing Flask applications, with proper error handling and fallbacks.
"""

import os
import sys
import logging
from typing import Dict, Optional, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demonstrate_enhanced_parsing():
    """Demonstrate the enhanced parsing system with various input formats"""
    
    # Import the enhanced parsing functions
    try:
        from utils import parse_customer_input, normalize_customer_data
        logger.info("Successfully imported enhanced parsing functions")
    except ImportError as e:
        logger.error(f"Failed to import parsing functions: {e}")
        return
    
    # Test cases representing real-world scenarios
    test_cases = [
        {
            "name": "E-commerce Order",
            "input": "John Smith, phone: 555-123-4567, email: john@example.com, shipping to: 123 Main St, Springfield, IL 62704"
        },
        {
            "name": "Customer Service Input", 
            "input": "Customer: Sarah Johnson at sarah.j@company.com, mobile (555) 987-6543, address: 456 Oak Avenue, Apt 2B, Chicago, Illinois 60601"
        },
        {
            "name": "International Customer",
            "input": "Emma Wilson, +44 20 7946 0958, emma@uk.co.uk, 10 Downing Street, London SW1A 2AA, United Kingdom"
        },
        {
            "name": "Minimal Information",
            "input": "Bob Jones, call 555-111-2222, California resident"
        },
        {
            "name": "Traditional CSV Format",
            "input": "Alice Brown,321 Cedar Dr,Miami,FL,33101,alice@email.com,305-555-0123"
        }
    ]
    
    print("=" * 80)
    print("ENHANCED AI-POWERED CUSTOMER PARSING INTEGRATION DEMO")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'-' * 60}")
        print(f"Input: {test_case['input']}")
        
        try:
            # Parse the customer input
            parsed_result = parse_customer_input(test_case['input'])
            
            if parsed_result:
                # Normalize and clean the data
                normalized_result = normalize_customer_data(parsed_result)
                
                # Display results
                print("\n✅ PARSING SUCCESSFUL")
                print(f"   Method: {normalized_result.get('detected_format', 'Unknown')}")
                print(f"   Confidence: {normalized_result.get('confidence', 0.0):.2f}")
                print(f"   Quality Score: {normalized_result.get('data_quality_score', 0.0):.2f}")
                
                print("\n📋 EXTRACTED DATA:")
                print(f"   Name: {normalized_result.get('name', 'N/A')}")
                print(f"   Phone: {normalized_result.get('phone', 'N/A')}")
                print(f"   Email: {normalized_result.get('email', 'N/A')}")
                print(f"   Address: {normalized_result.get('address_1', 'N/A')}")
                print(f"   City: {normalized_result.get('city', 'N/A')}")
                print(f"   State: {normalized_result.get('state', 'N/A')}")
                print(f"   Postal Code: {normalized_result.get('postal_code', 'N/A')}")
                print(f"   Country: {normalized_result.get('country', 'N/A')}")
                
                # Show validation suggestions if any
                suggestions = normalized_result.get('validation_suggestions', [])
                if suggestions:
                    print("\n⚠️  VALIDATION SUGGESTIONS:")
                    for suggestion in suggestions:
                        print(f"   • {suggestion}")
                
                # Show how to integrate with existing systems
                print("\n🔧 INTEGRATION EXAMPLE:")
                integration_example = create_integration_example(normalized_result)
                print(integration_example)
                
            else:
                print("\n❌ PARSING FAILED")
                print("   No customer data could be extracted from the input")
                
        except Exception as e:
            print(f"\n💥 ERROR: {str(e)}")
            logger.exception("Error during parsing demonstration")

def create_integration_example(customer_data: Dict[str, Any]) -> str:
    """Create an example of how to integrate parsed data into existing systems"""
    
    # Example: Convert to database insert format
    db_format = {
        "customer_name": customer_data.get('name', ''),
        "phone_number": customer_data.get('phone', ''),
        "email_address": customer_data.get('email', ''),
        "street_address": customer_data.get('address_1', ''),
        "city_name": customer_data.get('city', ''),
        "state_code": customer_data.get('state', ''),
        "zip_code": customer_data.get('postal_code', ''),
        "country_code": customer_data.get('country', 'US'),
        "data_quality": customer_data.get('data_quality_score', 0.0),
        "parsing_method": customer_data.get('detected_format', 'Unknown')
    }
    
    # Generate SQL insert example
    sql_example = f"""
   # Database Integration Example:
   INSERT INTO customers (name, phone, email, address, city, state, postal_code, country)
   VALUES ('{db_format["customer_name"]}', '{db_format["phone_number"]}', 
           '{db_format["email_address"]}', '{db_format["street_address"]}',
           '{db_format["city_name"]}', '{db_format["state_code"]}', 
           '{db_format["zip_code"]}', '{db_format["country_code"]}');
   
   # Flask Route Integration:
   @app.route('/parse-customer', methods=['POST'])
   def parse_customer():
       input_text = request.json.get('customer_input', '')
       result = parse_customer_input(input_text)
       if result:
           normalized = normalize_customer_data(result)
           return jsonify({{'success': True, 'data': normalized}})
       return jsonify({{'success': False, 'error': 'Parsing failed'}})"""
    
    return sql_example

def performance_benchmark():
    """Run a performance benchmark of the parsing system"""
    
    print(f"\n\n{'=' * 80}")
    print("PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    try:
        import time
        from utils import parse_customer_input
        
        # Test inputs of varying complexity
        test_inputs = [
            "John Doe, 555-123-4567, john@example.com",  # Simple
            "Sarah Johnson, phone: (555) 987-6543, email sarah.j@gmail.com, address: 456 Oak Ave, Apartment 2B, Chicago Illinois 60601",  # Complex
            "Mike Smith - call me at 555.444.3333 or email mike@company.org - I'm at 789 Pine St, Austin TX 78701",  # Natural language
        ]
        
        print("Testing parsing performance with different input complexities...\n")
        
        for i, test_input in enumerate(test_inputs, 1):
            # Warm up (first call may be slower due to model loading)
            parse_customer_input(test_input)
            
            # Measure parsing time
            start_time = time.time()
            result = parse_customer_input(test_input)
            end_time = time.time()
            
            parsing_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            print(f"Test {i} - Input Length: {len(test_input)} chars")
            print(f"         Parsing Time: {parsing_time:.2f}ms")
            print(f"         Success: {'Yes' if result else 'No'}")
            print(f"         Method: {result.get('detected_format', 'N/A') if result else 'N/A'}")
            print()
        
    except Exception as e:
        print(f"Benchmark failed: {e}")

def main():
    """Main demonstration function"""
    
    print("Enhanced AI-Powered Customer Input Parsing System")
    print("Integration Demonstration")
    print("=" * 80)
    
    # Check if required dependencies are available
    try:
        import torch
        import transformers
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ Transformers version: {transformers.__version__}")
        print(f"✅ CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✅ CUDA device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"⚠️  Missing dependencies: {e}")
        print("   Install with: pip install torch transformers tokenizers")
        print("   System will fall back to traditional parsing methods.")
    
    # Run the demonstration
    demonstrate_enhanced_parsing()
    
    # Run performance benchmark
    performance_benchmark()
    
    print(f"\n\n{'=' * 80}")
    print("INTEGRATION COMPLETE")
    print("=" * 80)
    print("\n📚 Documentation:")
    print("   • All parsing functions are backward compatible")
    print("   • AI features gracefully degrade if models unavailable")
    print("   • Configuration can be customized via ai_config.py")
    print("   • Environment variables can override default settings")
    
    print("\n🚀 Next Steps:")
    print("   1. Install dependencies: pip install torch transformers tokenizers")
    print("   2. Test with your data: python test_enhanced_parsing.py")
    print("   3. Integrate into your Flask app using the examples above")
    print("   4. Monitor performance and adjust ai_config.py as needed")
    print("   5. Set environment variables for production configuration")

if __name__ == "__main__":
    main()