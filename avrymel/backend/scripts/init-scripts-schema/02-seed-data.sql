-- Seed data for multi-tenant e-commerce database

-- Insert tenants
INSERT INTO tenants (name) VALUES
    ('Acme Corporation'),
    ('TechStart Industries'),
    ('Global Retail Co');

-- Insert users for Acme Corporation (tenant_id = 1)
INSERT INTO users (tenant_id, email, full_name, role) VALUES
    (1, 'john.doe@acme.com', 'John Doe', 'admin'),
    (1, 'jane.smith@acme.com', 'Jane Smith', 'user'),
    (1, 'bob.johnson@acme.com', 'Bob Johnson', 'user');

-- Insert users for TechStart Industries (tenant_id = 2)
INSERT INTO users (tenant_id, email, full_name, role) VALUES
    (2, 'alice.wong@techstart.com', 'Alice Wong', 'admin'),
    (2, 'charlie.brown@techstart.com', 'Charlie Brown', 'user'),
    (2, 'diana.prince@techstart.com', 'Diana Prince', 'user');

-- Insert users for Global Retail Co (tenant_id = 3)
INSERT INTO users (tenant_id, email, full_name, role) VALUES
    (3, 'emma.watson@globalretail.com', 'Emma Watson', 'admin'),
    (3, 'frank.miller@globalretail.com', 'Frank Miller', 'user');

-- Insert products for Acme Corporation
INSERT INTO products (tenant_id, name, description, price, stock_quantity) VALUES
    (1, 'Laptop Pro 15', 'High-performance laptop for professionals', 1299.99, 50),
    (1, 'Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 200),
    (1, 'USB-C Hub', '7-in-1 USB-C multiport adapter', 49.99, 150),
    (1, 'Monitor 27"', '4K UHD monitor with HDR', 399.99, 75),
    (1, 'Keyboard Mechanical', 'RGB mechanical gaming keyboard', 129.99, 100);

-- Insert products for TechStart Industries
INSERT INTO products (tenant_id, name, description, price, stock_quantity) VALUES
    (2, 'Smart Watch Pro', 'Advanced fitness and health tracking', 349.99, 120),
    (2, 'Wireless Earbuds', 'Noise-cancelling true wireless earbuds', 179.99, 250),
    (2, 'Phone Stand', 'Adjustable aluminum phone stand', 24.99, 300),
    (2, 'Power Bank 20000mAh', 'Fast charging portable power bank', 59.99, 180),
    (2, 'Tablet 10"', 'Android tablet with stylus', 299.99, 90);

-- Insert products for Global Retail Co
INSERT INTO products (tenant_id, name, description, price, stock_quantity) VALUES
    (3, 'Coffee Maker Deluxe', 'Programmable coffee maker with grinder', 149.99, 60),
    (3, 'Blender Pro', 'High-speed professional blender', 89.99, 80),
    (3, 'Air Fryer XL', 'Extra large capacity air fryer', 119.99, 70),
    (3, 'Rice Cooker Smart', 'Multi-function smart rice cooker', 79.99, 100),
    (3, 'Toaster Oven', '6-slice convection toaster oven', 99.99, 55);

-- Insert orders for Acme Corporation
INSERT INTO orders (tenant_id, user_id, order_number, status, total_amount) VALUES
    (1, 2, 'ACME-2024-001', 'completed', 1379.97),
    (1, 3, 'ACME-2024-002', 'pending', 479.98),
    (1, 2, 'ACME-2024-003', 'shipped', 129.99);

-- Insert orders for TechStart Industries
INSERT INTO orders (tenant_id, user_id, order_number, status, total_amount) VALUES
    (2, 5, 'TECH-2024-001', 'completed', 529.98),
    (2, 6, 'TECH-2024-002', 'processing', 384.98),
    (2, 5, 'TECH-2024-003', 'completed', 59.99);

-- Insert orders for Global Retail Co
INSERT INTO orders (tenant_id, user_id, order_number, status, total_amount) VALUES
    (3, 8, 'GLOB-2024-001', 'completed', 369.97),
    (3, 8, 'GLOB-2024-002', 'shipped', 179.98);

-- Insert order items for Acme Corporation orders
-- Order 1 (ACME-2024-001)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (1, 1, 1, 1, 1299.99, 1299.99),
    (1, 1, 2, 1, 29.99, 29.99),
    (1, 1, 3, 1, 49.99, 49.99);

-- Order 2 (ACME-2024-002)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (1, 2, 4, 1, 399.99, 399.99),
    (1, 2, 2, 2, 29.99, 59.98),
    (1, 2, 3, 1, 49.99, 49.99);

-- Order 3 (ACME-2024-003)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (1, 3, 5, 1, 129.99, 129.99);

-- Insert order items for TechStart Industries orders
-- Order 4 (TECH-2024-001)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (2, 4, 6, 1, 349.99, 349.99),
    (2, 4, 7, 1, 179.99, 179.99);

-- Order 5 (TECH-2024-002)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (2, 5, 10, 1, 299.99, 299.99),
    (2, 5, 8, 2, 24.99, 49.98),
    (2, 5, 9, 1, 59.99, 59.99);

-- Order 6 (TECH-2024-003)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (2, 6, 9, 1, 59.99, 59.99);

-- Insert order items for Global Retail Co orders
-- Order 7 (GLOB-2024-001)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (3, 7, 11, 1, 149.99, 149.99),
    (3, 7, 12, 1, 89.99, 89.99),
    (3, 7, 14, 1, 79.99, 79.99),
    (3, 7, 3, 1, 49.99, 49.99);

-- Order 8 (GLOB-2024-002)
INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal) VALUES
    (3, 8, 13, 1, 119.99, 119.99),
    (3, 8, 15, 1, 99.99, 99.99);

-- Display summary
SELECT
    t.name as tenant,
    COUNT(DISTINCT u.id) as users,
    COUNT(DISTINCT p.id) as products,
    COUNT(DISTINCT o.id) as orders,
    COUNT(DISTINCT oi.id) as order_items
FROM tenants t
LEFT JOIN users u ON t.id = u.tenant_id
LEFT JOIN products p ON t.id = p.tenant_id
LEFT JOIN orders o ON t.id = o.tenant_id
LEFT JOIN order_items oi ON t.id = oi.tenant_id
GROUP BY t.id, t.name
ORDER BY t.id;
