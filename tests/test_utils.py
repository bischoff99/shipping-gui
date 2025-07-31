"""
Test utility functions
"""
import pytest
from unittest.mock import patch, Mock
from utils import parse_customer_input, normalize_customer_data


class TestUtilityFunctions:
    """Test utility functions for customer data processing"""
    
    def test_parse_customer_input_complete_data(self):
        """Test parsing complete customer input"""
        customer_input = """
        John Doe
        john.doe@example.com
        +1-555-0123
        123 Main Street
        Los Angeles, CA 90210
        United States
        """
        
        result = parse_customer_input(customer_input.strip())
        
        assert result is not None
        assert result['name'] == 'John Doe'
        assert result['email'] == 'john.doe@example.com'
        assert result['phone'] == '+1-555-0123'
        assert 'address_1' in result
        assert 'city' in result
        assert 'state' in result
    
    def test_parse_customer_input_minimal_data(self):
        """Test parsing minimal customer input"""
        customer_input = """
        Jane Smith
        jane@example.com
        Los Angeles, CA
        """
        
        result = parse_customer_input(customer_input.strip())
        
        assert result is not None
        assert result['name'] == 'Jane Smith'
        assert result['email'] == 'jane@example.com'
    
    def test_parse_customer_input_empty_string(self):
        """Test parsing empty input"""
        result = parse_customer_input("")
        assert result is None
    
    def test_parse_customer_input_invalid_format(self):
        """Test parsing invalid format"""
        customer_input = "This is not a valid customer format"
        result = parse_customer_input(customer_input)
        
        # Should handle gracefully and extract what it can
        assert result is None or isinstance(result, dict)
    
    def test_normalize_customer_data_complete(self):
        """Test normalizing complete customer data"""
        raw_data = {
            'name': '  John Doe  ',
            'email': '  JOHN@EXAMPLE.COM  ',
            'phone': '(555) 123-4567',
            'address_1': '  123 Main St  ',
            'city': '  los angeles  ',
            'state': '  california  ',
            'postal_code': '  90210  ',
            'country': '  usa  '
        }
        
        normalized = normalize_customer_data(raw_data)
        
        assert normalized['name'] == 'John Doe'
        assert normalized['email'] == 'john@example.com'
        assert normalized['phone'] == '+1-555-123-4567'
        assert normalized['address_1'] == '123 Main St'
        assert normalized['city'] == 'Los Angeles'
        assert normalized['state'] == 'CA'
        assert normalized['country'] == 'US'
    
    def test_normalize_customer_data_missing_fields(self):
        """Test normalizing data with missing fields"""
        raw_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com'
        }
        
        normalized = normalize_customer_data(raw_data)
        
        assert normalized['name'] == 'Jane Smith'
        assert normalized['email'] == 'jane@example.com'
        assert 'phone' in normalized  # Should have default/empty values
        assert 'country' in normalized
    
    def test_normalize_customer_data_phone_formats(self):
        """Test phone number normalization with different formats"""
        test_cases = [
            ('555-123-4567', '+1-555-123-4567'),
            ('(555) 123-4567', '+1-555-123-4567'),
            ('555.123.4567', '+1-555-123-4567'),
            ('5551234567', '+1-555-123-4567'),
            ('+1-555-123-4567', '+1-555-123-4567'),  # Already formatted
        ]
        
        for input_phone, expected in test_cases:
            raw_data = {'name': 'Test', 'phone': input_phone}
            normalized = normalize_customer_data(raw_data)
            assert normalized['phone'] == expected, f"Failed for input: {input_phone}"
    
    def test_normalize_customer_data_state_conversion(self):
        """Test state name to abbreviation conversion"""
        test_cases = [
            ('California', 'CA'),
            ('california', 'CA'),
            ('CALIFORNIA', 'CA'),
            ('New York', 'NY'),
            ('Texas', 'TX'),
            ('CA', 'CA'),  # Already abbreviated
            ('Unknown State', 'Unknown State'),  # Unknown states pass through
        ]
        
        for input_state, expected in test_cases:
            raw_data = {'name': 'Test', 'state': input_state}
            normalized = normalize_customer_data(raw_data)
            assert normalized['state'] == expected, f"Failed for input: {input_state}"
    
    def test_normalize_customer_data_country_conversion(self):
        """Test country name to code conversion"""
        test_cases = [
            ('United States', 'US'),
            ('united states', 'US'),
            ('USA', 'US'),
            ('Canada', 'CA'),
            ('United Kingdom', 'GB'),
            ('US', 'US'),  # Already abbreviated
        ]
        
        for input_country, expected in test_cases:
            raw_data = {'name': 'Test', 'country': input_country}
            normalized = normalize_customer_data(raw_data)
            assert normalized['country'] == expected, f"Failed for input: {input_country}"
    
    def test_normalize_customer_data_empty_input(self):
        """Test normalizing empty input"""
        result = normalize_customer_data({})
        
        assert isinstance(result, dict)
        # Should have default values for required fields
        assert 'name' in result
        assert 'country' in result
    
    def test_normalize_customer_data_none_input(self):
        """Test normalizing None input"""
        result = normalize_customer_data(None)
        
        assert isinstance(result, dict)
        # Should return empty dict or dict with defaults
    
    def test_parse_customer_input_multiline_address(self):
        """Test parsing customer input with multiline address"""
        customer_input = """
        Bob Johnson
        bob@company.com
        +1-555-0987
        456 Oak Avenue
        Suite 100
        San Francisco, CA 94102
        """
        
        result = parse_customer_input(customer_input.strip())
        
        assert result is not None
        assert result['name'] == 'Bob Johnson'
        assert result['email'] == 'bob@company.com'
        assert 'address_1' in result
        # Should handle multi-line addresses
    
    def test_parse_customer_input_international_phone(self):
        """Test parsing international phone numbers"""
        customer_input = """
        Maria Garcia
        maria@example.com
        +44-20-7946-0958
        London, UK
        """
        
        result = parse_customer_input(customer_input.strip())
        
        assert result is not None
        assert result['name'] == 'Maria Garcia'
        assert '+44' in result['phone']
    
    def test_normalize_customer_data_special_characters(self):
        """Test handling special characters in customer data"""
        raw_data = {
            'name': 'José María O\'Connor',
            'email': 'jose.maria@example.com',
            'address_1': '123 Saint-Laurent Blvd',
            'city': 'Montréal'
        }
        
        normalized = normalize_customer_data(raw_data)
        
        # Should preserve special characters
        assert 'José' in normalized['name']
        assert 'O\'Connor' in normalized['name']
        assert 'Saint-Laurent' in normalized['address_1']
        assert 'Montréal' in normalized['city']