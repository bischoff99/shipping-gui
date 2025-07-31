"""
Test models and database operations
"""
import pytest
from models import db, Product, Supplier, Warehouse, ProductInventory


class TestModels:
    """Test database models"""
    
    def test_supplier_creation(self, app):
        """Test supplier model creation"""
        with app.app_context():
            supplier = Supplier(
                name='Test Supplier 2',
                contact_email='test2@supplier.com',
                city='San Francisco',
                state='CA',
                country='US'
            )
            db.session.add(supplier)
            db.session.commit()
            
            assert supplier.id is not None
            assert supplier.name == 'Test Supplier 2'
            assert supplier.to_dict()['name'] == 'Test Supplier 2'
    
    def test_warehouse_creation(self, app):
        """Test warehouse model creation"""
        with app.app_context():
            warehouse = Warehouse(
                name='Test Warehouse 2',
                address_line_1='456 Test Ave',
                city='Los Angeles',
                state='CA',
                postal_code='90210',
                country='US',
                platform='veeqo'
            )
            db.session.add(warehouse)
            db.session.commit()
            
            assert warehouse.id is not None
            assert warehouse.platform == 'veeqo'
            assert warehouse.to_dict()['platform'] == 'veeqo'
    
    def test_product_creation_and_queries(self, app):
        """Test product model creation and queries"""
        with app.app_context():
            # Get existing supplier
            supplier = Supplier.query.first()
            assert supplier is not None
            
            product = Product(
                sku='TEST-NEW-001',
                title='New Test Product',
                description='New test description',
                weight_grams=150.0,
                price=39.99,
                cost_price=20.00,
                supplier_id=supplier.id,
                active=True,
                veeqo_id='veeqo_123',
                easyship_id='easyship_456'
            )
            db.session.add(product)
            db.session.commit()
            
            # Test queries
            found_by_sku = Product.find_by_sku('TEST-NEW-001')
            assert found_by_sku is not None
            assert found_by_sku.title == 'New Test Product'
            
            found_by_veeqo = Product.find_by_external_id('veeqo', 'veeqo_123')
            assert found_by_veeqo is not None
            assert found_by_veeqo.sku == 'TEST-NEW-001'
            
            found_by_easyship = Product.find_by_external_id('easyship', 'easyship_456')
            assert found_by_easyship is not None
            assert found_by_easyship.sku == 'TEST-NEW-001'
    
    def test_product_inventory(self, app):
        """Test product inventory functionality"""
        with app.app_context():
            product = Product.query.first()
            warehouse = Warehouse.query.first()
            assert product is not None
            assert warehouse is not None
            
            # Create inventory item
            inventory = ProductInventory(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=100,
                allocated_quantity=10,
                min_reorder_level=20,
                reorder_quantity=50
            )
            db.session.add(inventory)
            db.session.commit()
            
            # Test properties
            assert inventory.available_quantity == 90  # 100 - 10
            assert inventory.needs_reorder is False  # 90 > 20
            assert inventory.stock_status == 'in_stock'
            
            # Test low stock
            inventory.quantity = 15
            db.session.commit()
            assert inventory.available_quantity == 5  # 15 - 10
            assert inventory.needs_reorder is True  # 5 <= 20
            assert inventory.stock_status == 'low_stock'
            
            # Test out of stock
            inventory.allocated_quantity = 15
            db.session.commit()
            assert inventory.available_quantity == 0
            assert inventory.stock_status == 'out_of_stock'
    
    def test_product_dimensions(self, app):
        """Test product dimensions property"""
        with app.app_context():
            product = Product.query.first()
            assert product is not None
            
            # Set dimensions using property
            product.dimensions = {
                'length': 10.0,
                'width': 5.0,
                'height': 2.0,
                'unit': 'cm'
            }
            
            # Verify dimensions
            dims = product.dimensions
            assert dims['length'] == 10.0
            assert dims['width'] == 5.0
            assert dims['height'] == 2.0
            assert dims['unit'] == 'cm'
    
    def test_product_inventory_queries(self, app):
        """Test inventory query methods"""
        with app.app_context():
            # Create test data for low stock query
            product1 = Product.query.first()
            product2 = Product.query.filter_by(sku='TEST-002').first()
            warehouse = Warehouse.query.first()
            
            # Create low stock inventory
            low_stock_inventory = ProductInventory(
                product_id=product1.id,
                warehouse_id=warehouse.id,
                quantity=5,
                allocated_quantity=0,
                min_reorder_level=10,
                reorder_quantity=20
            )
            db.session.add(low_stock_inventory)
            
            # Create normal stock inventory
            normal_inventory = ProductInventory(
                product_id=product2.id,
                warehouse_id=warehouse.id,
                quantity=50,
                allocated_quantity=5,
                min_reorder_level=10,
                reorder_quantity=20
            )
            db.session.add(normal_inventory)
            db.session.commit()
            
            # Test low stock query
            low_stock_items = ProductInventory.get_low_stock_items()
            assert len(low_stock_items) >= 1
            
            # Test specific query
            found_inventory = ProductInventory.get_by_product_warehouse(
                product1.id, warehouse.id
            )
            assert found_inventory is not None
            assert found_inventory.quantity == 5