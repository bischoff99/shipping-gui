"""
Test configuration and fixtures
"""
import os
import pytest
import tempfile
from unittest.mock import Mock, patch
from app_factory import create_app
from models import db, Product, Supplier, Warehouse


@pytest.fixture(scope='session')
def app():
    """Create test application"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Test configuration
    config = {
        'FLASK_ENV': 'testing',
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'REDIS_URL': 'redis://localhost:6379/1',  # Use test database
        'LOG_TO_STDOUT': False,
        'VEEQO_API_KEY': 'test-veeqo-key',
        'EASYSHIP_API_KEY': 'test-easyship-key',
        'INTERNAL_API_KEY': 'test-internal-key'
    }
    
    app = create_app('testing')
    app.config.update(config)
    
    with app.app_context():
        db.create_all()
        create_test_data()
        yield app
        db.drop_all()
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


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
    """Headers with API key for authenticated requests"""
    return {
        'Authorization': 'Bearer test-internal-key',
        'Content-Type': 'application/json'
    }


def create_test_data():
    """Create test data for testing"""
    # Create test supplier
    supplier = Supplier(
        name='Test Supplier',
        contact_email='test@supplier.com',
        city='Test City',
        state='CA',
        country='US'
    )
    db.session.add(supplier)
    db.session.flush()
    
    # Create test warehouse
    warehouse = Warehouse(
        name='Test Warehouse',
        address_line_1='123 Test St',
        city='Test City',
        state='CA',
        postal_code='12345',
        country='US',
        platform='both'
    )
    db.session.add(warehouse)
    db.session.flush()
    
    # Create test products
    products = [
        Product(
            sku='TEST-001',
            title='Test Product 1',
            description='Test description 1',
            weight_grams=100.0,
            price=19.99,
            supplier_id=supplier.id,
            active=True
        ),
        Product(
            sku='TEST-002',
            title='Test Product 2',
            description='Test description 2',
            weight_grams=200.0,
            price=29.99,
            supplier_id=supplier.id,
            active=True
        )
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.commit()


@pytest.fixture
def mock_veeqo_api():
    """Mock Veeqo API responses"""
    with patch('api.veeqo_api.VeeqoAPI') as mock:
        mock_instance = Mock()
        mock_instance.get_warehouses.return_value = [
            {
                'id': '338489',
                'name': 'Test Warehouse',
                'city': 'Las Vegas',
                'region': 'NV',
                'country': 'US'
            }
        ]
        mock_instance.get_products.return_value = [
            {
                'id': '1001',
                'title': 'Mock Product 1',
                'sku': 'MOCK-001',
                'price': '19.99'
            }
        ]
        mock_instance.get_random_products.return_value = [
            {
                'id': '1001',
                'title': 'Mock Product 1',
                'sku': 'MOCK-001',
                'price': '19.99'
            }
        ]
        mock_instance.test_connection.return_value = True
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_easyship_api():
    """Mock Easyship API responses"""
    with patch('api.easyship_api.EasyshipAPI') as mock:
        mock_instance = Mock()
        mock_instance.get_addresses.return_value = [
            {
                'id': 'addr_001',
                'name': 'Test Address',
                'city': 'Los Angeles',
                'state': 'CA',
                'country': 'US'
            }
        ]
        mock_instance.get_products.return_value = [
            {
                'id': 'prod_001',
                'name': 'Mock Easyship Product',
                'sku': 'ES-001',
                'price': 25.99
            }
        ]
        mock_instance.get_random_products.return_value = [
            {
                'id': 'prod_001',
                'name': 'Mock Easyship Product',
                'sku': 'ES-001',
                'price': 25.99
            }
        ]
        mock_instance.test_connection.return_value = True
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1-555-0123',
        'address_1': '123 Main St',
        'city': 'Los Angeles',
        'state': 'CA',
        'postal_code': '90210',
        'country': 'US'
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing"""
    return {
        'customer_data': {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+1-555-0456',
            'address_1': '456 Oak Ave',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94102',
            'country': 'US'
        },
        'products': [
            {
                'id': '1001',
                'sku': 'TEST-001',
                'quantity': 2,
                'price': 19.99
            }
        ],
        'routing_data': {
            'carrier': 'UPS',
            'platform': 'VEEQO'
        }
    }