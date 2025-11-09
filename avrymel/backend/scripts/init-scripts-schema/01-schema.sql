-- Create the schema

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Merchants table (app users who own the stores)
CREATE TABLE merchants (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    merchant_id INT REFERENCES merchants(id) ON DELETE CASCADE,
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

-- Products table (product catalog)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER NOT NULL REFERENCES merchants(id) ON DELETE CASCADE,
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(merchant_id, product_id)
);

CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_product_id ON products(product_id);

-- Order items table (line items in orders)
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    variant_name VARCHAR(200) NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

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

-- Trigger to automatically update updated_at on products table
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE fulfillments ENABLE ROW LEVEL SECURITY;

-- merchants policies
CREATE POLICY merchant_isolation_policy ON merchants
    USING (id = current_setting('app.current_merchant_id', TRUE)::INTEGER);

CREATE POLICY merchant_isolation_policy_insert ON merchants
    FOR INSERT
    WITH CHECK (id = current_setting('app.current_merchant_id', TRUE)::INTEGER);

-- customers policies
CREATE POLICY merchant_isolation_policy ON customers
    USING (merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER);

CREATE POLICY merchant_isolation_policy_insert ON customers
    FOR INSERT
    WITH CHECK (merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER);

-- products policies
CREATE POLICY merchant_isolation_policy ON products
    USING (merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER);

CREATE POLICY merchant_isolation_policy_insert ON products
    FOR INSERT
    WITH CHECK (merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER);

-- addresses policies (linked through customers->orders)
CREATE POLICY merchant_isolation_policy ON addresses
    USING (
        id IN (
            SELECT billing_address_id FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE c.merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
            UNION
            SELECT shipping_address_id FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE c.merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

CREATE POLICY merchant_isolation_policy_insert ON addresses
    FOR INSERT
    WITH CHECK (true); -- Addresses can be inserted, but will be protected through orders

-- orders policies
CREATE POLICY merchant_isolation_policy ON orders
    USING (
        customer_id IN (
            SELECT id FROM customers
            WHERE merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

CREATE POLICY merchant_isolation_policy_insert ON orders
    FOR INSERT
    WITH CHECK (
        customer_id IN (
            SELECT id FROM customers
            WHERE merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

-- order_items policies
CREATE POLICY merchant_isolation_policy ON order_items
    USING (
        order_id IN (
            SELECT o.id FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE c.merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
        AND product_id IN (
            SELECT id FROM products
            WHERE merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

CREATE POLICY merchant_isolation_policy_insert ON order_items
    FOR INSERT
    WITH CHECK (
        order_id IN (
            SELECT o.id FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE c.merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
        AND product_id IN (
            SELECT id FROM products
            WHERE merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

-- fulfillments policies
CREATE POLICY merchant_isolation_policy ON fulfillments
    USING (
        order_id IN (
            SELECT o.id FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE c.merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

CREATE POLICY merchant_isolation_policy_insert ON fulfillments
    FOR INSERT
    WITH CHECK (
        order_id IN (
            SELECT o.id FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE c.merchant_id = current_setting('app.current_merchant_id', TRUE)::INTEGER
        )
    );

-- Create a helper function to set the merchant context
CREATE OR REPLACE FUNCTION set_current_merchant(merchant_id_param INTEGER)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_merchant_id', merchant_id_param::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql;

-- Create a helper function to get current merchant
CREATE OR REPLACE FUNCTION get_current_merchant()
RETURNS INTEGER AS $$
BEGIN
    RETURN current_setting('app.current_merchant_id', TRUE)::INTEGER;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
