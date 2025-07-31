"""
Enhanced Test Configuration - MCP Powered
Comprehensive test fixtures and setup for all test types
"""
import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch
from flask import Flask
from datetime import datetime, timezone

# Import the new app factory
from src.core.app_factory import create_test_app
from models import db, Product, Supplier, Warehouse, ProductInventory, Order


@pytest.fixture(scope='session')
def app():
    """Create test Flask application"""
    test_app = create_test_app()
    
    # Additional test configuration
    test_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key-not-for-production',
        'VEEQO_API_KEY': 'test-veeqo-key',
        'EASYSHIP_API_KEY': 'test-easyship-key',
        'HF_TOKEN': 'test-hf-token'
    })
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Standard authentication headers for API tests"""
    return {
        'Content-Type': 'application/json',
        'X-API-Key': 'test-api-key'
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1-555-0123',
        'address_1': '123 Main Street',
        'address_2': 'Apt 4B',
        'city': 'New York',
        'state': 'NY',
        'postal_code': '10001',
        'country': 'US'
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        'sku': 'TEST-001',
        'title': 'Test Product',
        'description': 'A test product for unit testing',
        'weight_grams': 500.0,
        'length_cm': 20.0,
        'width_cm': 15.0,
        'height_cm': 5.0,
        'price': 29.99,
        'cost_price': 15.00,
        'category': 'Test Category',
        'brand': 'Test Brand',
        'hs_code': '1234.56',
        'origin_country': 'US'
    }


@pytest.fixture
def sample_warehouse_data():
    """Sample warehouse data for testing"""
    return {
        'name': 'Test Warehouse',
        'address_line_1': '456 Warehouse Ave',
        'city': 'Los Angeles',
        'state': 'CA',
        'postal_code': '90210',
        'country': 'US',
        'phone': '+1-555-0456',
        'platform': 'both'
    }


@pytest.fixture
def db_session(app):
    """Database session fixture with automatic cleanup"""
    with app.app_context():
        # Clean up any existing data
        db.drop_all()
        db.create_all()
        
        yield db.session
        
        # Clean up after test
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def sample_supplier(db_session):
    """Create a sample supplier in the database"""
    supplier = Supplier(
        name="Test Supplier Inc.",
        contact_email="supplier@test.com",
        contact_phone="+1-555-0789",
        address_line_1="789 Supplier Blvd",
        city="Chicago",
        state="IL",
        postal_code="60601",
        country="US"
    )
    db_session.add(supplier)
    db_session.commit()
    return supplier


@pytest.fixture
def sample_warehouse(db_session):
    """Create a sample warehouse in the database"""
    warehouse = Warehouse(
        name="Test Warehouse",
        address_line_1="456 Warehouse Ave",
        city="Los Angeles",
        state="CA",
        postal_code="90210",
        country="US",
        phone="+1-555-0456",
        platform="both"
    )
    db_session.add(warehouse)
    db_session.commit()
    return warehouse


@pytest.fixture
def sample_product(db_session, sample_supplier):
    """Create a sample product in the database"""
    product = Product(
        sku="TEST-001",
        title="Test Product",
        description="A test product for unit testing",
        weight_grams=500.0,
        length_cm=20.0,
        width_cm=15.0,
        height_cm=5.0,
        price=29.99,
        cost_price=15.00,
        category="Test Category",
        brand="Test Brand",
        supplier_id=sample_supplier.id,
        hs_code="1234.56",
        origin_country="US",
        active=True
    )
    db_session.add(product)
    db_session.commit()
    return product


@pytest.fixture
def sample_inventory(db_session, sample_product, sample_warehouse):
    """Create sample inventory data"""
    inventory = ProductInventory(
        product_id=sample_product.id,
        warehouse_id=sample_warehouse.id,
        quantity=100,
        allocated_quantity=10,
        min_reorder_level=20,
        reorder_quantity=50,
        location="A1-B2-C3"
    )
    db_session.add(inventory)
    db_session.commit()
    return inventory


@pytest.fixture
def sample_order(db_session):
    """Create a sample order in the database"""
    order = Order(
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        customer_phone="+1-555-0123",
        address_line_1="123 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
        country="US",
        carrier="FEDEX",
        service_type="FEDEX_GROUND",
        total_weight_grams=500.0,
        total_value=29.99,
        currency="USD",
        order_status="pending",
        platform="easyship"
    )
    db_session.add(order)
    db_session.commit()
    return order


@pytest.fixture
def mock_veeqo_api():
    """Mock Veeqo API responses"""
    with patch('api.veeqo_api.VeeqoAPI') as mock:
        mock_instance = Mock()
        
        # Mock successful connection test
        mock_instance.test_connection.return_value = True
        
        # Mock warehouse data
        mock_instance.get_warehouses.return_value = [
            {
                'id': 1,
                'name': 'Main Warehouse',
                'city': 'Las Vegas',
                'state': 'NV',
                'country': 'US'
            }
        ]
        
        # Mock product data
        mock_instance.get_products.return_value = [
            {
                'id': 1,
                'sku': 'TEST-001',
                'title': 'Test Product',
                'price': 29.99
            }
        ]
        
        mock_instance.get_random_products.return_value = [
            {
                'id': 1,
                'sku': 'TEST-001',
                'title': 'Test Product',
                'price': 29.99
            }
        ]
        
        # Mock order creation
        mock_instance.create_order.return_value = {
            'id': 1,
            'status': 'created',
            'tracking_number': 'TEST123456'
        }
        
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_easyship_api():
    """Mock Easyship API responses"""
    with patch('api.easyship_api.EasyshipAPI') as mock:
        mock_instance = Mock()
        
        # Mock successful connection test
        mock_instance.test_connection.return_value = True
        
        # Mock address data
        mock_instance.get_addresses.return_value = [
            {
                'id': 'addr_1',
                'name': 'Nevada Warehouse',
                'city': 'Las Vegas',
                'state': 'NV',
                'country': 'US'
            }
        ]
        
        # Mock product data
        mock_instance.get_products.return_value = [
            {
                'id': 'prod_1',
                'sku': 'ES-001',
                'name': 'Easyship Product',
                'price': 39.99
            }
        ]
        
        mock_instance.get_random_products.return_value = [
            {
                'id': 'prod_1',
                'sku': 'ES-001',
                'name': 'Easyship Product',
                'price': 39.99
            }
        ]
        
        # Mock shipment creation
        mock_instance.create_shipment.return_value = {
            'id': 'ship_1',
            'status': 'created',
            'tracking_number': 'ES123456'
        }
        
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    with patch('redis.from_url') as mock_redis:
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.setex.return_value = True
        mock_client.delete.return_value = True
        
        mock_redis.return_value = mock_client
        yield mock_client


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing"""
    fixed_datetime = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    with patch('datetime.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_datetime
        mock_dt.utcnow.return_value = fixed_datetime
        yield fixed_datetime


@pytest.fixture
def api_response_success():
    """Standard successful API response"""
    return {
        'status': 'success',
        'data': {},
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def api_response_error():
    """Standard error API response"""
    return {
        'status': 'error',
        'message': 'Test error message',
        'code': 'TEST_ERROR',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean up environment variables after each test"""
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def performance_monitor():
    """Monitor test performance"""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    duration = end_time - start_time
    if duration > 1.0:  # Tests taking longer than 1 second
        pytest.warnings.warn(
            f"Slow test detected: {duration:.2f}s", 
            pytest.PytestWarning
        )


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to tests in unit directory
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add api marker to tests in api directory
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ['load', 'performance', 'stress']):
            item.add_marker(pytest.mark.slow)


# Utility functions for tests
def assert_api_response_structure(response_data, expected_keys=None):
    """Assert that API response has the expected structure"""
    if expected_keys is None:
        expected_keys = ['status', 'timestamp']
    
    for key in expected_keys:
        assert key in response_data, f"Missing key '{key}' in API response"


def create_test_customer_input(format_type='tab_separated'):
    """Create test customer input in various formats"""
    customer_data = {
        'name': 'Jane Smith',
        'phone': '+1-555-0199',
        'email': 'jane.smith@example.com',
        'address': '789 Test Ave',
        'city': 'Boston',
        'state': 'MA',
        'postal_code': '02101',
        'country': 'US'
    }
    
    if format_type == 'tab_separated':
        return f"{customer_data['name']}\t{customer_data['phone']}\t{customer_data['email']}\t{customer_data['address']}\t{customer_data['city']}\t{customer_data['state']}\t{customer_data['postal_code']}\t{customer_data['country']}"
    elif format_type == 'space_separated':
        return f"{customer_data['name']} {customer_data['phone']} {customer_data['email']} {customer_data['address']} {customer_data['city']} {customer_data['state']} {customer_data['postal_code']} {customer_data['country']}"
    else:
        return customer_data


def mock_external_api_error():
    """Create a mock external API error response"""
    from requests.exceptions import RequestException
    return RequestException("External API temporarily unavailable")