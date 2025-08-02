-- Database initialization script for shipping GUI
-- Creates core tables and seeds them with sample data

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    contact_email VARCHAR(120),
    contact_phone VARCHAR(50),
    address_line_1 VARCHAR(200),
    address_line_2 VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'US',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Warehouses table
CREATE TABLE IF NOT EXISTS warehouses (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    address_line_1 VARCHAR(200) NOT NULL,
    address_line_2 VARCHAR(200),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL DEFAULT 'US',
    phone VARCHAR(50),
    platform VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    weight_grams FLOAT,
    length_cm FLOAT,
    width_cm FLOAT,
    height_cm FLOAT,
    dimensions_unit VARCHAR(20) DEFAULT 'cm',
    price NUMERIC(10,2),
    cost_price NUMERIC(10,2),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    category VARCHAR(100),
    brand VARCHAR(100),
    veeqo_id VARCHAR(100),
    easyship_id VARCHAR(100),
    hs_code VARCHAR(20),
    origin_country VARCHAR(2) DEFAULT 'US',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Product inventory table
CREATE TABLE IF NOT EXISTS product_inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    warehouse_id INTEGER NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    allocated_quantity INTEGER NOT NULL DEFAULT 0,
    incoming_quantity INTEGER NOT NULL DEFAULT 0,
    min_reorder_level INTEGER NOT NULL DEFAULT 0,
    max_stock_level INTEGER,
    reorder_quantity INTEGER NOT NULL DEFAULT 0,
    location VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, warehouse_id)
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    easyship_shipment_id VARCHAR(100),
    tracking_number VARCHAR(100),
    customer_name VARCHAR(200) NOT NULL,
    customer_email VARCHAR(120),
    customer_phone VARCHAR(50),
    address_line_1 VARCHAR(200) NOT NULL,
    address_line_2 VARCHAR(200),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(2) NOT NULL,
    carrier VARCHAR(50) NOT NULL,
    service_type VARCHAR(100),
    total_weight_grams FLOAT,
    total_value NUMERIC(10,2),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    order_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    booking_status VARCHAR(50),
    shipping_cost NUMERIC(10,2),
    insurance_cost NUMERIC(10,2),
    total_cost NUMERIC(10,2),
    platform VARCHAR(50),
    origin_address_id VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ
);

-- Seed sample data
INSERT INTO suppliers (name, contact_email, contact_phone, address_line_1, city, state, postal_code, country)
VALUES ('Fashion Supplier Inc.', 'orders@fashionsupplier.com', '+1-555-0123', '123 Supplier St', 'Los Angeles', 'CA', '90210', 'US');

INSERT INTO warehouses (name, address_line_1, city, state, postal_code, country, phone, platform)
VALUES ('Main Warehouse', '456 Warehouse Ave', 'Las Vegas', 'NV', '89101', 'US', '+1-555-0456', 'both');

INSERT INTO products (sku, title, description, weight_grams, length_cm, width_cm, height_cm, price, cost_price, category, brand, supplier_id, hs_code, origin_country, active)
VALUES ('SAMPLE-001', 'Sample Fashion Item', 'A high-quality sample fashion item for testing', 500.0, 30.0, 20.0, 5.0, 49.99, 25.00, 'Apparel', 'Sample Brand', currval('suppliers_id_seq'), '6203.42', 'US', TRUE);

INSERT INTO product_inventory (product_id, warehouse_id, quantity, allocated_quantity, min_reorder_level, reorder_quantity, location)
VALUES (currval('products_id_seq'), currval('warehouses_id_seq'), 100, 10, 20, 50, 'A1-B2-C3');

