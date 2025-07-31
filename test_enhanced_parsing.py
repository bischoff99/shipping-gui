#!/usr/bin/env python3
"""
Test suite for the enhanced AI-powered customer input parsing system.

This demonstrates the capabilities of the new parsing system including:
- Natural language parsing
- Multiple format support
- AI-enhanced entity recognition
- Data quality scoring
- Auto-correction features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    parse_customer_input, 
    normalize_customer_data, 
    extract_contact_info,
    auto_correct_common_mistakes,
    calculate_data_quality_score,
    get_validation_suggestions
)

def test_natural_language_parsing():
    """Test parsing of natural language customer input"""
    
    print("=" * 80)
    print("ENHANCED AI-POWERED CUSTOMER INPUT PARSING SYSTEM")
    print("=" * 80)
    
    test_cases = [
        # Natural language format
        "John Doe lives at 123 Main Street, Springfield, IL 62704, email john.doe@example.com, phone +1-555-123-4567",
        
        # Messy real-world input
        "sarah johnson, phone: (555) 987-6543, email sarah.j@gmail.com, address: 456 Oak Ave, Apartment 2B, Chicago Illinois 60601",
        
        # Informal format
        "Mike Smith - call me at 555.444.3333 or email mike@company.org - I'm at 789 Pine St, Austin TX 78701",
        
        # International format
        "Emma Wilson, +44 20 7946 0958, emma.wilson@uk.co.uk, 10 Downing Street, London, SW1A 2AA, United Kingdom",
        
        # Minimal information
        "Bob Jones, 555-111-2222, somewhere in California",
        
        # Traditional formats (should still work)
        "Jane Smith\t555-555-5555 jane@test.com\t123 Elm St\t\tDallas\tTX\t75201\tUS",
        "Alice Brown, 321 Cedar Dr, Miami, FL, 33101, alice@email.com, 305-555-0123",
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{'-' * 60}")
        print(f"TEST CASE {i}: Natural Language Input")
        print(f"{'-' * 60}")
        print(f"Input: {test_input}")
        print()
        
        # Parse the input
        try:
            result = parse_customer_input(test_input)
            
            if result:
                # Normalize the data
                normalized = normalize_customer_data(result)
                
                print("PARSED RESULT:")
                print(f"  Name: {normalized.get('name', 'N/A')}")
                print(f"  Phone: {normalized.get('phone', 'N/A')}")
                print(f"  Email: {normalized.get('email', 'N/A')}")
                print(f"  Address: {normalized.get('address_1', 'N/A')}")
                print(f"  City: {normalized.get('city', 'N/A')}")
                print(f"  State: {normalized.get('state', 'N/A')}")
                print(f"  Postal Code: {normalized.get('postal_code', 'N/A')}")
                print(f"  Country: {normalized.get('country', 'N/A')}")
                print(f"  Detected Format: {normalized.get('detected_format', 'N/A')}")
                print(f"  Confidence Score: {normalized.get('confidence', 0.0):.2f}")
                print(f"  Data Quality Score: {normalized.get('data_quality_score', 0.0):.2f}")
                
                suggestions = normalized.get('validation_suggestions', [])
                if suggestions:
                    print("  Validation Suggestions:")
                    for suggestion in suggestions:
                        print(f"    - {suggestion}")
                        
                # Show AI entities if available
                if 'ai_entities' in normalized:
                    print("  AI Detected Entities:")
                    for entity in normalized['ai_entities']:
                        print(f"    - {entity.get('entity_group', entity.get('label', 'UNKNOWN'))}: {entity['word']} (confidence: {entity.get('score', 0.0):.2f})")
                
            else:
                print("❌ PARSING FAILED - No data extracted")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

def test_contact_extraction():
    """Test enhanced contact information extraction"""
    
    print(f"\n\n{'-' * 60}")
    print("ENHANCED CONTACT EXTRACTION TEST")
    print(f"{'-' * 60}")
    
    test_texts = [
        "Call me at +1-555-123-4567 or email john@example.com",
        "My numbers are 555.987.6543 and (212) 555-0199, email: test@domain.org",
        "International: +44 20 7946 0958, +49 30 12345678, contact@global.co.uk",
        "Reach out via sarah.johnson+work@company.com or 555-444-3333 ext 1234",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        contact_info = extract_contact_info(text)
        print(f"  Primary Phone: {contact_info.get('phone', 'None')}")
        print(f"  Primary Email: {contact_info.get('email', 'None')}")
        print(f"  All Phones: {contact_info.get('all_phones', [])}")
        print(f"  All Emails: {contact_info.get('all_emails', [])}")

def test_auto_correction():
    """Test auto-correction features"""
    
    print(f"\n\n{'-' * 60}")
    print("AUTO-CORRECTION TEST")
    print(f"{'-' * 60}")
    
    test_data = {
        "name": "john smith",
        "phone": "5551234567",
        "email": "JOHN.SMITH@EXAMPLE.COM",
        "address_1": "123 main st",
        "city": "los angeles",
        "state": "california",
        "postal_code": "90210",
        "country": "us"
    }
    
    print("Before correction:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    corrected = auto_correct_common_mistakes(test_data)
    
    print("\nAfter auto-correction:")
    for key, value in corrected.items():
        print(f"  {key}: {value}")

def test_data_quality_scoring():
    """Test data quality scoring system"""
    
    print(f"\n\n{'-' * 60}")
    print("DATA QUALITY SCORING TEST")
    print(f"{'-' * 60}")
    
    test_datasets = [
        # Complete, high-quality data
        {
            "name": "John Doe",
            "phone": "+1-555-123-4567",
            "email": "john.doe@example.com",
            "address_1": "123 Main Street",
            "city": "Springfield",
            "state": "IL",
            "postal_code": "62704",
            "country": "US"
        },
        # Incomplete data
        {
            "name": "Jane Smith",
            "phone": "555-invalid",
            "email": "not-an-email",
            "address_1": "456 Oak Ave",
            "city": "",
            "state": "",
            "postal_code": "invalid-zip"
        },
        # Minimal data
        {
            "name": "Bob Wilson",
            "phone": "",
            "email": "",
            "address_1": "",
            "city": "",
            "state": "",
            "postal_code": ""
        }
    ]
    
    for i, data in enumerate(test_datasets, 1):
        print(f"\nDataset {i}:")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Phone: {data.get('phone', 'N/A')}")
        print(f"  Email: {data.get('email', 'N/A')}")
        
        score = calculate_data_quality_score(data)
        suggestions = get_validation_suggestions(data)
        
        print(f"  Quality Score: {score:.2f} ({score*100:.0f}%)")
        
        if suggestions:
            print("  Suggestions:")
            for suggestion in suggestions:
                print(f"    - {suggestion}")
        else:
            print("  ✅ No validation issues found")

def main():
    """Run all tests"""
    print("Testing Enhanced AI-Powered Customer Input Parsing System")
    print("=" * 80)
    
    try:
        test_natural_language_parsing()
        test_contact_extraction()
        test_auto_correction()
        test_data_quality_scoring()
        
        print(f"\n\n{'=' * 80}")
        print("TESTING COMPLETE")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("✅ Natural language input parsing")
        print("✅ AI-powered named entity recognition")
        print("✅ Multiple phone/email format detection")
        print("✅ Address component extraction")
        print("✅ Auto-correction of common mistakes")
        print("✅ Data quality scoring and validation")
        print("✅ Confidence scoring for parsed results")
        print("✅ Backward compatibility with traditional formats")
        
        print(f"\nTo use this enhanced parsing system:")
        print("1. Install dependencies: pip install torch transformers tokenizers")
        print("2. Import: from utils import parse_customer_input, normalize_customer_data")
        print("3. Parse: result = parse_customer_input('John Doe, 123 Main St, ...')")
        print("4. Normalize: clean_data = normalize_customer_data(result)")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()