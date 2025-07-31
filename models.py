"""
Database models for Unified Order & Warehouse Management System.

Defines SQLAlchemy models for suppliers, warehouses, products, and related entities.

Classes:
    Supplier: Supplier model for tracking product suppliers.
    Warehouse: Warehouse model for tracking product locations.
    Product: Product model for inventory and order management.

Typical usage example:
    from models import Supplier, Warehouse, Product
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

db = SQLAlchemy()


class Supplier(db.Model):
    """Supplier model for tracking product suppliers"""

    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    address_line_1 = db.Column(db.String(200), nullable=True)
    address_line_2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(50), nullable=True, default="US")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    products = db.relationship("Product", backref="supplier", lazy=True)

    def __repr__(self):
        return f"<Supplier {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class Warehouse(db.Model):
    """Warehouse model for tracking product locations"""

    __tablename__ = "warehouses"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), nullable=True)  # For Veeqo/Easyship IDs
    name = db.Column(db.String(200), nullable=False)
    address_line_1 = db.Column(db.String(200), nullable=False)
    address_line_2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False, default="US")
    phone = db.Column(db.String(50), nullable=True)
    # 'veeqo', 'easyship', 'both'
    platform = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    inventory_items = db.relationship(
        "ProductInventory",
        backref="warehouse",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Warehouse {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "name": self.name,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "phone": self.phone,
            "platform": self.platform,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }


class Product(db.Model):
    """Product model with comprehensive fields for e-commerce operations"""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), nullable=False, unique=True, index=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Weight and dimensions
    weight_grams = db.Column(db.Float, nullable=True)
    length_cm = db.Column(db.Float, nullable=True)
    width_cm = db.Column(db.Float, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    dimensions_unit = db.Column(db.String(20), nullable=True, default="cm")

    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=True)
    cost_price = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="USD")

    # Product categorization
    category = db.Column(db.String(100), nullable=True)
    brand = db.Column(db.String(100), nullable=True)

    # External platform IDs
    veeqo_id = db.Column(db.String(100), nullable=True, index=True)
    easyship_id = db.Column(db.String(100), nullable=True, index=True)

    # Customs and shipping
    hs_code = db.Column(db.String(20), nullable=True)
    origin_country = db.Column(db.String(2), nullable=True, default="US")

    # Product status
    active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    supplier_id = db.Column(
        db.Integer, db.ForeignKey("suppliers.id"), nullable=True, index=True
    )

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    inventory_items = db.relationship(
        "ProductInventory",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Product {self.sku}: {self.title}>"

    @property
    def dimensions(self) -> Dict[str, Any]:
        """Get dimensions as a dictionary"""
        return {
            "length": float(self.length_cm) if self.length_cm is not None else 0.0,
            "width": float(self.width_cm) if self.width_cm is not None else 0.0,
            "height": float(self.height_cm) if self.height_cm is not None else 0.0,
            "unit": self.dimensions_unit or "cm",
        }

    @dimensions.setter
    def dimensions(self, value: Dict[str, float]):
        """Set dimensions from a dictionary"""
        if isinstance(value, dict):
            self.length_cm = value.get("length")
            self.width_cm = value.get("width")
            self.height_cm = value.get("height")
            self.dimensions_unit = value.get("unit", "cm")

    def get_total_inventory(self) -> int:
        """Get total inventory across all warehouses"""
        if not hasattr(self, "inventory_items") or self.inventory_items is None:
            return 0
        return sum(item.quantity for item in self.inventory_items)

    def get_available_inventory(self) -> int:
        """Get available inventory (physical - allocated)"""
        if not hasattr(self, "inventory_items") or self.inventory_items is None:
            return 0
        return sum(item.available_quantity for item in self.inventory_items)

    def get_inventory_by_warehouse(self) -> Dict[int, int]:
        """Get inventory breakdown by warehouse"""
        if not hasattr(self, "inventory_items") or self.inventory_items is None:
            return {}
        return {item.warehouse_id: item.quantity for item in self.inventory_items}

    def to_dict(self, include_inventory=False):
        """Convert to dictionary representation"""
        data = {
            "id": self.id,
            "sku": self.sku,
            "title": self.title,
            "description": self.description,
            "weight_grams": (float(self.weight_grams) if self.weight_grams else None),
            "dimensions": self.dimensions,
            "price": float(self.price) if self.price else None,
            "cost_price": float(self.cost_price) if self.cost_price else None,
            "currency": self.currency,
            "category": self.category,
            "brand": self.brand,
            "veeqo_id": self.veeqo_id,
            "easyship_id": self.easyship_id,
            "hs_code": self.hs_code,
            "origin_country": self.origin_country,
            "active": self.active,
            "supplier_id": self.supplier_id,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }

        if include_inventory:
            data["total_inventory"] = self.get_total_inventory()
            data["available_inventory"] = self.get_available_inventory()
            data["inventory_by_warehouse"] = self.get_inventory_by_warehouse()

        return data

    @classmethod
    def find_by_sku(cls, sku: str) -> Optional["Product"]:
        """Find product by SKU"""
        return cls.query.filter_by(sku=sku).first()

    @classmethod
    def find_by_external_id(
        cls, platform: str, external_id: str
    ) -> Optional["Product"]:
        """Find product by external platform ID"""
        if platform.lower() == "veeqo":
            return cls.query.filter_by(veeqo_id=external_id).first()
        elif platform.lower() == "easyship":
            return cls.query.filter_by(easyship_id=external_id).first()
        return None


class ProductInventory(db.Model):
    """Product inventory tracking per warehouse"""

    __tablename__ = "product_inventory"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False, index=True
    )
    warehouse_id = db.Column(
        db.Integer, db.ForeignKey("warehouses.id"), nullable=False, index=True
    )

    # Inventory quantities
    quantity = db.Column(db.Integer, nullable=False, default=0)
    allocated_quantity = db.Column(db.Integer, nullable=False, default=0)
    incoming_quantity = db.Column(db.Integer, nullable=False, default=0)

    # Inventory settings
    min_reorder_level = db.Column(db.Integer, nullable=False, default=0)
    max_stock_level = db.Column(db.Integer, nullable=True)
    reorder_quantity = db.Column(db.Integer, nullable=False, default=0)

    # Location within warehouse
    location = db.Column(db.String(100), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Unique constraint to prevent duplicate entries
    __table_args__ = (
        db.UniqueConstraint(
            "product_id", "warehouse_id", name="unique_product_warehouse"
        ),
    )

    def __repr__(self):
        return f"<ProductInventory Product:{self.product_id} Warehouse:{self.warehouse_id} Qty:{self.quantity}>"

    @property
    def available_quantity(self) -> int:
        """Calculate available quantity (physical - allocated)"""
        return max(0, self.quantity - self.allocated_quantity)

    @property
    def needs_reorder(self) -> bool:
        """Check if inventory is below reorder level"""
        return self.available_quantity <= self.min_reorder_level

    @property
    def stock_status(self) -> str:
        """Get stock status string"""
        available = self.available_quantity
        if available == 0:
            return "out_of_stock"
        elif available <= self.min_reorder_level:
            return "low_stock"
        elif self.max_stock_level and available >= self.max_stock_level:
            return "overstock"
        else:
            return "in_stock"

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "warehouse_id": self.warehouse_id,
            "quantity": self.quantity,
            "allocated_quantity": self.allocated_quantity,
            "available_quantity": self.available_quantity,
            "incoming_quantity": self.incoming_quantity,
            "min_reorder_level": self.min_reorder_level,
            "max_stock_level": self.max_stock_level,
            "reorder_quantity": self.reorder_quantity,
            "location": self.location,
            "needs_reorder": self.needs_reorder,
            "stock_status": self.stock_status,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
        }

    @classmethod
    def get_by_product_warehouse(
        cls, product_id: int, warehouse_id: int
    ) -> Optional["ProductInventory"]:
        """Get ProductInventory by product and warehouse"""
        return cls.query.filter_by(product_id=product_id, warehouse_id=warehouse_id).first()

    @classmethod
    def get_low_stock_items(cls, threshold: Optional[int] = None) -> List["ProductInventory"]:
        """Get all items that need reordering"""
        query = cls.query.join(Product).filter(Product.active == True)
        if threshold is not None:
            query = query.filter(cls.quantity - cls.allocated_quantity <= threshold)
        else:
            query = query.filter(
                cls.quantity - cls.allocated_quantity <= cls.min_reorder_level
            )
        return query.all()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)

    with app.app_context():
        db.create_all()


class Order(db.Model):
    """Order model for tracking shipments and orders"""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    
    # External IDs
    easyship_shipment_id = db.Column(db.String(100), nullable=True, index=True)
    tracking_number = db.Column(db.String(100), nullable=True, index=True)
    
    # Customer information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_phone = db.Column(db.String(50), nullable=True)
    
    # Shipping address
    address_line_1 = db.Column(db.String(200), nullable=False)
    address_line_2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    
    # Order details
    carrier = db.Column(db.String(50), nullable=False)  # FEDEX, UPS, etc.
    service_type = db.Column(db.String(100), nullable=True)
    total_weight_grams = db.Column(db.Float, nullable=True)
    total_value = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    
    # Status tracking
    order_status = db.Column(db.String(50), nullable=False, default="pending")  # pending, shipped, delivered, failed
    booking_status = db.Column(db.String(50), nullable=True)  # For carrier booking status
    
    # Costs
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=True)
    insurance_cost = db.Column(db.Numeric(10, 2), nullable=True)
    total_cost = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Platform info
    platform = db.Column(db.String(50), nullable=True)  # easyship, direct, etc.
    origin_address_id = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    shipped_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Order {self.id}: {self.customer_name} - {self.carrier}>"

    def to_dict(self):
        """Convert to dictionary representation"""
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "easyship_shipment_id": self.easyship_shipment_id,
            "tracking_number": self.tracking_number,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "carrier": self.carrier,
            "service_type": self.service_type,
            "total_weight_grams": float(self.total_weight_grams) if self.total_weight_grams else None,
            "total_value": float(self.total_value) if self.total_value else None,
            "currency": self.currency,
            "order_status": self.order_status,
            "booking_status": self.booking_status,
            "shipping_cost": float(self.shipping_cost) if self.shipping_cost else None,
            "insurance_cost": float(self.insurance_cost) if self.insurance_cost else None,
            "total_cost": float(self.total_cost) if self.total_cost else None,
            "platform": self.platform,
            "origin_address_id": self.origin_address_id,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "updated_at": (self.updated_at.isoformat() if self.updated_at else None),
            "shipped_at": (self.shipped_at.isoformat() if self.shipped_at else None),
            "delivered_at": (self.delivered_at.isoformat() if self.delivered_at else None),
        }

    def to_csv_dict(self):
        """Convert to CSV-friendly dictionary format"""
        def safe_strftime(dt, fmt):
            return dt.strftime(fmt) if dt else ""

        def safe_float(val):
            return float(val) if val else 0

        return {
            "order_id": self.id,
            "easyship_shipment_id": self.easyship_shipment_id or "",
            "tracking_number": self.tracking_number or "",
            "customer_name": self.customer_name,
            "customer_email": self.customer_email or "",
            "customer_phone": self.customer_phone or "",
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2 or "",
            "city": self.city,
            "state": self.state or "",
            "postal_code": self.postal_code,
            "country": self.country,
            "carrier": self.carrier,
            "service_type": self.service_type or "",
            "total_weight_grams": self.total_weight_grams if self.total_weight_grams is not None else 0,
            "total_value": safe_float(self.total_value),
            "currency": self.currency,
            "order_status": self.order_status,
            "booking_status": self.booking_status or "",
            "shipping_cost": safe_float(self.shipping_cost),
            "insurance_cost": safe_float(self.insurance_cost),
            "total_cost": safe_float(self.total_cost),
            "platform": self.platform or "",
            "created_date": safe_strftime(self.created_at, "%Y-%m-%d"),
            "created_time": safe_strftime(self.created_at, "%H:%M:%S"),
            "shipped_date": safe_strftime(self.shipped_at, "%Y-%m-%d"),
            "delivered_date": safe_strftime(self.delivered_at, "%Y-%m-%d"),
        }
    def find_by_tracking_number(cls, tracking_number: str) -> Optional["Order"]:
        """Find order by tracking number"""
        return cls.query.filter_by(tracking_number=tracking_number).first()

    @classmethod
    def find_by_easyship_id(cls, easyship_id: str) -> Optional["Order"]:
        """Find order by Easyship shipment ID"""
        return cls.query.filter_by(easyship_shipment_id=easyship_id).first()

    @classmethod
    def get_orders_by_carrier(cls, carrier: str) -> List["Order"]:
        """Get all orders for a specific carrier"""
        return cls.query.filter_by(carrier=carrier.upper()).all()

    @classmethod
    def get_orders_by_status(cls, status: str) -> List["Order"]:
        """Get all orders with a specific status"""
        return cls.query.filter_by(order_status=status.lower()).all()

def create_sample_data():
    """Create sample data for testing"""
    # Create sample supplier
    supplier = Supplier(
        name="Fashion Supplier Inc.",
        contact_email="orders@fashionsupplier.com",
        contact_phone="+1-555-0123",
        address_line_1="123 Supplier St",
        city="Los Angeles",
        state="CA",
        postal_code="90210",
        country="US",
    )
    db.session.add(supplier)
    db.session.flush()  # Get the ID

    # Create sample warehouse
    warehouse = Warehouse(
        name="Main Warehouse",
        address_line_1="456 Warehouse Ave",
        city="Las Vegas",
        state="NV",
        postal_code="89101",
        country="US",
        phone="+1-555-0456",
        platform="both",
    )
    db.session.add(warehouse)
    db.session.flush()  # Get the ID

    # Create sample product
    product = Product(
        sku="SAMPLE-001",
        title="Sample Fashion Item",
        description="A high-quality sample fashion item for testing",
        weight_grams=500.0,
        length_cm=30.0,
        width_cm=20.0,
        height_cm=5.0,
        price=49.99,
        cost_price=25.00,
        category="Apparel",
        brand="Sample Brand",
        supplier_id=supplier.id,
        hs_code="6203.42",
        origin_country="US",
    )
    db.session.add(product)
    db.session.flush()  # Get the ID

    # Create sample inventory
    inventory = ProductInventory(
        product_id=product.id,
        warehouse_id=warehouse.id,
        quantity=100,
        allocated_quantity=10,
        min_reorder_level=20,
        reorder_quantity=50,
        location="A1-B2-C3",
    )
    db.session.add(inventory)

    db.session.commit()
    print("✅ Sample data created successfully!")
