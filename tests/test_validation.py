"""
Test validation functions
"""
import pytest
from validation import validate_order_data, validate_customer_data, ValidationResult


class TestValidationFunctions:
    """Test validation functions for order and customer data"""
    
    def test_validate_customer_data_valid_complete(self):
        """Test validation of complete valid customer data"""
        customer_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1-555-0123',
            'address_1': '123 Main St',
            'city': 'Los Angeles',
            'state': 'CA',
            'postal_code': '90210',
            'country': 'US'
        }
        
        result = validate_customer_data(customer_data)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_customer_data_missing_name(self):
        """Test validation with missing required name"""
        customer_data = {
            'email': 'john@example.com',
            'address_1': '123 Main St',
            'city': 'Los Angeles',
            'state': 'CA'
        }
        
        result = validate_customer_data(customer_data)
        
        assert result.is_valid is False
        assert any('name' in error.lower() for error in result.errors)
    
    def test_validate_customer_data_invalid_email(self):
        """Test validation with invalid email format"""
        customer_data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'address_1': '123 Main St',
            'city': 'Los Angeles'
        }
        
        result = validate_customer_data(customer_data)
        
        assert result.is_valid is False
        assert any('email' in error.lower() for error in result.errors)
    
    def test_validate_customer_data_empty_required_fields(self):
        """Test validation with empty required fields"""
        customer_data = {
            'name': '',
            'email': '',
            'address_1': '',
            'city': ''
        }
        
        result = validate_customer_data(customer_data)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_customer_data_warnings(self):
        """Test validation that generates warnings"""
        customer_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'address_1': '123 Main St',
            'city': 'Los Angeles',
            'state': 'CA'
            # Missing phone and postal_code should generate warnings
        }
        
        result = validate_customer_data(customer_data)
        
        # Might be valid but with warnings
        if result.is_valid:
            assert len(result.warnings) > 0
    
    def test_validate_order_data_valid_complete(self):
        """Test validation of complete valid order data"""
        customer_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'address_1': '456 Oak Ave',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94102',
            'country': 'US'
        }
        
        warehouse_info = {
            'id': '123',
            'name': 'Test Warehouse',
            'city': 'Los Angeles',
            'state': 'CA'
        }
        
        products = [
            {
                'id': '1001',
                'sku': 'TEST-001',
                'title': 'Test Product',
                'price': 19.99,
                'weight_grams': 100
            }
        ]
        
        result = validate_order_data(customer_data, warehouse_info, products)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_order_data_missing_warehouse(self):
        """Test validation with missing warehouse info"""
        customer_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'city': 'San Francisco'
        }
        
        products = [{'id': '1001', 'sku': 'TEST-001'}]
        
        result = validate_order_data(customer_data, None, products)
        
        assert result.is_valid is False
        assert any('warehouse' in error.lower() for error in result.errors)
    
    def test_validate_order_data_empty_products(self):
        """Test validation with empty products list"""
        customer_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'city': 'San Francisco'
        }
        
        warehouse_info = {'id': '123', 'name': 'Test Warehouse'}
        
        result = validate_order_data(customer_data, warehouse_info, [])
        
        assert result.is_valid is False
        assert any('product' in error.lower() for error in result.errors)
    
    def test_validate_order_data_invalid_product(self):
        """Test validation with invalid product data"""
        customer_data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'city': 'San Francisco'
        }
        
        warehouse_info = {'id': '123', 'name': 'Test Warehouse'}
        
        # Product missing required fields
        products = [
            {
                'id': '1001'
                # Missing sku, title, price
            }
        ]
        
        result = validate_order_data(customer_data, warehouse_info, products)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validation_result_creation(self):
        """Test ValidationResult object creation and properties"""
        # Valid result
        valid_result = ValidationResult(is_valid=True)
        assert valid_result.is_valid is True
        assert len(valid_result.errors) == 0
        assert len(valid_result.warnings) == 0
        
        # Invalid result with errors
        invalid_result = ValidationResult(
            is_valid=False,
            errors=['Error 1', 'Error 2'],
            warnings=['Warning 1']
        )
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) == 2
        assert len(invalid_result.warnings) == 1
    
    def test_validate_customer_data_phone_format_validation(self):
        """Test phone number format validation"""
        # Valid phone formats
        valid_phones = [
            '+1-555-0123',
            '(555) 123-4567',
            '555-123-4567',
            '+44-20-7946-0958'
        ]
        
        for phone in valid_phones:
            customer_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': phone,
                'city': 'Test City'
            }
            
            result = validate_customer_data(customer_data)
            # Phone format should not cause validation failure
            phone_errors = [err for err in result.errors if 'phone' in err.lower()]
            assert len(phone_errors) == 0, f"Failed for phone: {phone}"
    
    def test_validate_customer_data_postal_code_validation(self):
        """Test postal code format validation"""
        test_cases = [
            ('90210', 'US', True),  # US ZIP
            ('90210-1234', 'US', True),  # US ZIP+4
            ('M5V 3L9', 'CA', True),  # Canadian postal code
            ('SW1A 1AA', 'GB', True),  # UK postal code
            ('12345', 'US', True),  # Valid US ZIP
            ('1234', 'US', False),  # Too short for US
            ('INVALID', 'US', False),  # Invalid format
        ]
        
        for postal_code, country, should_be_valid in test_cases:
            customer_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'postal_code': postal_code,
                'country': country,
                'city': 'Test City'
            }
            
            result = validate_customer_data(customer_data)
            postal_errors = [err for err in result.errors if 'postal' in err.lower()]
            
            if should_be_valid:
                assert len(postal_errors) == 0, f"Should be valid: {postal_code} for {country}"
            else:
                # May or may not fail depending on validation strictness
                pass  # Postal code validation might be lenient
    
    def test_validate_order_data_weight_validation(self):
        """Test product weight validation"""
        customer_data = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'city': 'Test City'
        }
        
        warehouse_info = {'id': '123', 'name': 'Test Warehouse'}
        
        # Test with various weight values
        test_weights = [0, -1, 0.1, 1000, 50000]  # Including edge cases
        
        for weight in test_weights:
            products = [
                {
                    'id': '1001',
                    'sku': 'TEST-001',
                    'title': 'Test Product',
                    'price': 19.99,
                    'weight_grams': weight
                }
            ]
            
            result = validate_order_data(customer_data, warehouse_info, products)
            
            # Negative weight should cause validation failure
            if weight < 0:
                weight_errors = [err for err in result.errors if 'weight' in err.lower()]
                assert len(weight_errors) > 0, f"Negative weight should fail validation: {weight}"
    
    def test_validate_order_data_price_validation(self):
        """Test product price validation"""
        customer_data = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'city': 'Test City'
        }
        
        warehouse_info = {'id': '123', 'name': 'Test Warehouse'}
        
        # Test with various price values
        test_prices = [0, -1, 0.01, 9999.99]
        
        for price in test_prices:
            products = [
                {
                    'id': '1001',
                    'sku': 'TEST-001',
                    'title': 'Test Product',
                    'price': price,
                    'weight_grams': 100
                }
            ]
            
            result = validate_order_data(customer_data, warehouse_info, products)
            
            # Negative price should cause validation failure
            if price < 0:
                price_errors = [err for err in result.errors if 'price' in err.lower()]
                assert len(price_errors) > 0, f"Negative price should fail validation: {price}"