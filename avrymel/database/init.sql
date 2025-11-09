-- Orders Database Schema
-- This schema stores orders from multiple e-commerce platforms (Amazon, Etsy, Shopify)

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);

-- Addresses table
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company VARCHAR(255),
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_or_region VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country_code VARCHAR(3) NOT NULL
);

-- Discounts table
CREATE TABLE IF NOT EXISTS discounts (
    id SERIAL PRIMARY KEY,
    discount_code VARCHAR(100) NOT NULL UNIQUE,
    discount_percent DECIMAL(5, 2) NOT NULL CHECK (discount_percent >= 0 AND discount_percent <= 100)
);

CREATE INDEX idx_discounts_code ON discounts(discount_code);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) NOT NULL UNIQUE,
    service VARCHAR(20) NOT NULL CHECK (service IN ('Amazon', 'Etsy', 'Shopify')),
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    billing_address_id INTEGER NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
    shipping_address_id INTEGER NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
    discount_id INTEGER REFERENCES discounts(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    currency VARCHAR(3) NOT NULL,
    financial_status VARCHAR(20) NOT NULL CHECK (financial_status IN ('paid', 'pending', 'refunded')),
    subtotal DECIMAL(10, 2) NOT NULL,
    total_tax DECIMAL(10, 2) NOT NULL,
    final_price DECIMAL(10, 2) NOT NULL
);

CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_service ON orders(service);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_financial_status ON orders(financial_status);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    item_id VARCHAR(100) NOT NULL,
    item_name VARCHAR(500) NOT NULL,
    variant_name VARCHAR(200) NOT NULL,
    item_price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_item_id ON order_items(item_id);

-- Fulfillments table
CREATE TABLE IF NOT EXISTS fulfillments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    tracking_company VARCHAR(20) NOT NULL CHECK (tracking_company IN ('UPS', 'DPD', 'FEDEX', 'USPS')),
    tracking_number VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_fulfillments_order_id ON fulfillments(order_id);
CREATE INDEX idx_fulfillments_tracking_number ON fulfillments(tracking_number);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at on customers table
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
