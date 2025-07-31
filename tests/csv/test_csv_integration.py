import pytest
from services.csv_integration import CSVProcessor
from models import db, Product, Warehouse
from flask import Flask


@pytest.fixture(scope="module")
def test_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def session(test_app):
    with test_app.app_context():
        yield db.session


def test_product_csv_import(session, tmp_path):
    csv_content = "sku_code,product_title,weight,sales_price,cost_price\nDENIM-JACKET-001,Classic Denim Jacket,40,59.99,30.0"
    csv_file = tmp_path / "products.csv"
    csv_file.write_text(csv_content)
    processor = CSVProcessor(session)
    processor.process_products_csv(str(csv_file), source="veeqo")
    product = session.query(Product).filter_by(sku="DENIM-JACKET-001").first()
    assert product is not None
    assert float(product.price) == 59.99


def test_warehouse_csv_import(session, tmp_path):
    csv_content = "external_id,name,address1,city,region,postal_code,country_code,phone,email\nBOUTQ001,Test Warehouse,123 Main St,Las Vegas,NV,89139,US,123-456-7890,test@example.com"
    csv_file = tmp_path / "warehouses.csv"
    csv_file.write_text(csv_content)
    processor = CSVProcessor(session)
    processor.process_warehouses_csv(str(csv_file), source="veeqo")
    warehouse = session.query(Warehouse).filter_by(external_id="BOUTQ001").first()
    assert warehouse is not None
    assert warehouse.city == "Las Vegas"
