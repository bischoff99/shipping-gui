"""
Test Configuration for API Testing Suite

This module contains centralized configuration for all tests,
including sample data, API settings, and test parameters.
"""

import os
from typing import Dict, Any


class TestConfig:
    """Main test configuration class"""

    # Test Environment Settings
    TESTING = True
    DEBUG = False

    # API Testing Settings
    RUN_INTEGRATION_TESTS = (
        os.environ.get("RUN_INTEGRATION_TESTS", "False").lower() == "true"
    )
    API_CALL_DELAY = float(os.environ.get("API_CALL_DELAY", "1.0"))
    MAX_API_CALLS_PER_TEST = int(os.environ.get("MAX_API_CALLS", "5"))
    API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "30"))

    # Test Data Directories
    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
    FIXTURES_DIR = os.path.join(TEST_DATA_DIR, "fixtures")

    # API Keys (for integration tests)
    VEEQO_API_KEY = os.environ.get("VEEQO_API_KEY")
    EASYSHIP_API_KEY = os.environ.get("EASYSHIP_API_KEY")


class SampleData:
    """Sample data for testing"""

    # Sample customer data for various test scenarios
    VALID_CUSTOMER = {
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john.doe@example.com",
        "address_1": "123 Main Street",
        "address_2": "Apt 4B",
        "city": "Las Vegas",
        "state": "Nevada",
        "postal_code": "89101",
        "country": "US",
    }

    MINIMAL_CUSTOMER = {
        "name": "Jane Smith",
        "address_1": "456 Oak Avenue",
        "city": "Los Angeles",
        "state": "California",
        "postal_code": "90210",
        "country": "US",
    }

    INTERNATIONAL_CUSTOMER = {
        "name": "Alice Johnson",
        "phone": "+44 20 7946 0958",
        "email": "alice@example.co.uk",
        "address_1": "10 Downing Street",
        "city": "London",
        "postal_code": "SW1A 2AA",
        "country": "GB",
    }

    INVALID_CUSTOMER = {
        "name": "",  # Missing name
        "email": "invalid-email",  # Invalid email
        "phone": "123",  # Invalid phone
        "address_1": "789 Pine St",
        "city": "Denver",
        "state": "Colorado",
        "postal_code": "80202",
        "country": "US",
    }

    # Sample warehouse data
    SAMPLE_WAREHOUSES = [
        {
            "id": 1,
            "name": "Nevada Distribution Center",
            "region": "Nevada",
            "address_line_1": "100 Warehouse Way",
            "city": "Las Vegas",
            "state": "Nevada",
            "postal_code": "89101",
            "country": "US",
        },
        {
            "id": 2,
            "name": "California Fulfillment Center",
            "region": "California",
            "address_line_1": "200 Logistics Blvd",
            "city": "Los Angeles",
            "state": "California",
            "postal_code": "90001",
            "country": "US",
        },
    ]

    # Sample product data
    SAMPLE_PRODUCTS = [
        {
            "id": "prod_001",
            "title": "Fashion Dress - Summer Collection",
            "price": "49.99",
            "weight": 0.5,
            "description": "Elegant summer dress in premium fabric",
            "category": "Apparel",
            "sku": "DRESS_SUM_001",
        },
        {
            "id": "prod_002",
            "title": "Designer Jeans - Classic Fit",
            "price": "89.99",
            "weight": 0.8,
            "description": "Premium denim jeans with classic fit",
            "category": "Apparel",
            "sku": "JEANS_CLS_002",
        },
        {
            "id": "prod_003",
            "title": "Leather Handbag - Professional",
            "price": "129.99",
            "weight": 0.6,
            "description": "Professional leather handbag for business",
            "category": "Accessories",
            "sku": "BAG_PRO_003",
        },
    ]

    # Sample API response data
    VEEQO_WAREHOUSE_RESPONSE = [
        {
            "id": 12345,
            "name": "Main Warehouse",
            "region": "Nevada",
            "address_line_1": "123 Warehouse St",
            "city": "Las Vegas",
            "state": "Nevada",
            "postal_code": "89101",
            "country": "US",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]

    EASYSHIP_ADDRESS_RESPONSE = {
        "addresses": [
            {
                "id": "addr_67890",
                "line_1": "456 Shipping Lane",
                "city": "Reno",
                "state": "Nevada",
                "postal_code": "89501",
                "country_alpha2": "US",
                "created_at": "2024-01-01T00:00:00Z",
            }
        ]
    }

    # Sample input formats for parsing tests
    TAB_SEPARATED_INPUT = "John Doe\t+1234567890 john@example.com\t123 Main St\t\tLas Vegas\tNevada\t89101\tUS"
    SPACE_SEPARATED_INPUT = "Jane Smith +1987654321 jane@example.com 456 Oak Ave Los Angeles California 90210"
    MINIMAL_INPUT = "Bob Johnson 789 Pine St Denver Colorado 80202"

    # Error scenarios
    API_ERROR_RESPONSES = {
        "unauthorized": {
            "status_code": 401,
            "response": {
                "error": "Unauthorized",
                "message": "Invalid API key",
            },
        },
        "rate_limited": {
            "status_code": 429,
            "response": {
                "error": "Rate Limited",
                "message": "Too many requests",
            },
        },
        "server_error": {
            "status_code": 500,
            "response": {
                "error": "Internal Server Error",
                "message": "Something went wrong",
            },
        },
        "not_found": {
            "status_code": 404,
            "response": {
                "error": "Not Found",
                "message": "Resource not found",
            },
        },
    }


class TestScenarios:
    """Pre-defined test scenarios"""

    # Order creation scenarios
    ORDER_SCENARIOS = [
        {
            "name": "Standard US Order",
            "customer": SampleData.VALID_CUSTOMER,
            "carrier": "UPS",
            "expected_platform": "VEEQO",
        },
        {
            "name": "FedEx Express Order",
            "customer": SampleData.VALID_CUSTOMER,
            "carrier": "FEDEX",
            "expected_platform": "EASYSHIP",
        },
        {
            "name": "International Order",
            "customer": SampleData.INTERNATIONAL_CUSTOMER,
            "carrier": "DHL",
            "expected_platform": "VEEQO",
        },
        {
            "name": "Minimal Data Order",
            "customer": SampleData.MINIMAL_CUSTOMER,
            "carrier": "USPS",
            "expected_platform": "VEEQO",
        },
    ]

    # Validation scenarios
    VALIDATION_SCENARIOS = [
        {
            "name": "Valid Customer Data",
            "data": SampleData.VALID_CUSTOMER,
            "should_pass": True,
            "expected_errors": 0,
            "expected_warnings": 0,
        },
        {
            "name": "Missing Required Fields",
            "data": {"phone": "+1234567890"},
            "should_pass": False,
            "expected_errors": 3,  # name, address, city
            "expected_warnings": 1,  # country
        },
        {
            "name": "Invalid Email Format",
            "data": {**SampleData.VALID_CUSTOMER, "email": "invalid-email"},
            "should_pass": False,
            "expected_errors": 1,
            "expected_warnings": 0,
        },
    ]

    # API response scenarios
    API_SCENARIOS = [
        {
            "name": "Successful API Call",
            "mock_response": {
                "status_code": 200,
                "json_data": SampleData.VEEQO_WAREHOUSE_RESPONSE,
            },
            "expected_result": SampleData.VEEQO_WAREHOUSE_RESPONSE,
        },
        {
            "name": "API Authentication Error",
            "mock_response": {
                "status_code": 401,
                "json_data": None,
                "text": "Unauthorized",
            },
            "expected_result": None,
        },
        {
            "name": "API Server Error",
            "mock_response": {
                "status_code": 500,
                "json_data": None,
                "text": "Internal Server Error",
            },
            "expected_result": None,
        },
    ]


class TestHelpers:
    """Helper functions for testing"""

    @staticmethod
    def create_mock_response(status_code: int, json_data: Any = None, text: str = ""):
        """Create a mock HTTP response"""
        from unittest.mock import Mock

        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data
        mock_response.text = text
        return mock_response

    @staticmethod
    def assert_valid_json_response(test_case, response, expected_status: int = 200):
        """Helper to assert valid JSON response format"""
        test_case.assertEqual(response.status_code, expected_status)
        test_case.assertEqual(response.content_type, "application/json")

        try:
            import json

            return json.loads(response.data)
        except json.JSONDecodeError:
            test_case.fail("Response is not valid JSON")

    @staticmethod
    def assert_api_success_response(test_case, data: Dict):
        """Assert standard API success response format"""
        test_case.assertIn("status", data)
        test_case.assertEqual(data["status"], "success")

    @staticmethod
    def assert_api_error_response(test_case, data: Dict):
        """Assert standard API error response format"""
        test_case.assertIn("status", data)
        test_case.assertEqual(data["status"], "error")
        test_case.assertIn("message", data)

    @staticmethod
    def create_test_environment():
        """Set up test environment variables"""
        test_env = {
            "FLASK_ENV": "testing",
            "TESTING": "True",
            "API_CALL_DELAY": "0.1",  # Faster for testing
            "MAX_API_CALLS": "3",  # Lower limit for testing
        }

        for key, value in test_env.items():
            os.environ[key] = value

        return test_env
