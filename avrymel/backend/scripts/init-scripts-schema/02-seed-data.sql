-- Seed data for e-commerce database

-- Insert merchants (app users who own the stores)
INSERT INTO merchants (email, full_name, role) VALUES
    ('john.doe@example.com', 'John Doe', 'admin'),
    ('jane.smith@example.com', 'Jane Smith', 'user'),
    ('bob.johnson@example.com', 'Bob Johnson', 'user');

-- Insert customers (linked to merchants)
INSERT INTO customers (merchant_id, email, first_name, last_name) VALUES
    (1, 'john.doe@example.com', 'John', 'Doe'),
    (2, 'jane.smith@example.com', 'Jane', 'Smith'),
    (3, 'bob.johnson@example.com', 'Bob', 'Johnson');

-- Insert addresses
INSERT INTO addresses (first_name, last_name, company, address, city, state_or_region, country, postal_code, country_code) VALUES
    -- Billing and shipping for customer 1
    ('John', 'Doe', 'Acme Corp', '123 Main St', 'New York', 'NY', 'United States', '10001', 'US'),
    ('John', 'Doe', NULL, '123 Main St', 'New York', 'NY', 'United States', '10001', 'US'),
    -- Billing and shipping for customer 2
    ('Jane', 'Smith', NULL, '456 Oak Ave', 'Los Angeles', 'CA', 'United States', '90001', 'US'),
    ('Jane', 'Smith', NULL, '789 Pine Rd', 'San Francisco', 'CA', 'United States', '94102', 'US'),
    -- Billing and shipping for customer 3
    ('Bob', 'Johnson', 'Tech Industries', '321 Elm St', 'Chicago', 'IL', 'United States', '60601', 'US'),
    ('Bob', 'Johnson', 'Tech Industries', '321 Elm St', 'Chicago', 'IL', 'United States', '60601', 'US');

-- Insert discounts
INSERT INTO discounts (discount_code, discount_percent) VALUES
    ('SAVE10', 10.00),
    ('SUMMER20', 20.00),
    ('WELCOME15', 15.00);

-- Insert products (product catalog for each merchant)
INSERT INTO products (merchant_id, product_id, product_name, base_price) VALUES
    -- Merchant 1 products
    (1, 'AMZ-ITEM-001', 'Wireless Headphones', 149.99),
    (1, 'AMZ-ITEM-002', 'Phone Case', 24.99),
    (1, 'AMZ-ITEM-003', 'USB Cable', 12.99),
    (1, 'AMZ-ITEM-004', 'Bluetooth Speaker', 89.99),
    -- Merchant 2 products
    (2, 'ETSY-ITEM-001', 'Handmade Ceramic Mug', 35.99),
    (2, 'ETSY-ITEM-002', 'Wooden Coasters Set', 28.99),
    -- Merchant 3 products
    (3, 'SHOP-ITEM-001', 'Smart Watch', 399.99),
    (3, 'SHOP-ITEM-002', 'Watch Band', 49.99);

-- Insert orders
INSERT INTO orders (order_id, service, customer_id, billing_address_id, shipping_address_id, discount_id, created_at, updated_at, currency, financial_status, subtotal, total_tax, final_price) VALUES
    ('AMZ-2024-001', 'Amazon', 1, 1, 2, 1, '2024-01-15 10:30:00', '2024-01-15 10:30:00', 'USD', 'paid', 299.99, 24.00, 293.99),
    ('ETSY-2024-001', 'Etsy', 2, 3, 4, 2, '2024-01-16 14:20:00', '2024-01-16 14:20:00', 'USD', 'paid', 149.99, 12.00, 131.99),
    ('SHOP-2024-001', 'Shopify', 3, 5, 6, NULL, '2024-01-17 09:15:00', '2024-01-17 09:15:00', 'USD', 'pending', 499.99, 40.00, 539.99),
    ('AMZ-2024-002', 'Amazon', 1, 1, 2, 3, '2024-01-18 16:45:00', '2024-01-18 16:45:00', 'USD', 'paid', 89.99, 7.20, 83.69);

-- Insert order items (references products catalog)
INSERT INTO order_items (order_id, product_id, variant_name, price_at_purchase, quantity) VALUES
    -- Order 1 (AMZ-2024-001) - Merchant 1
    (1, 1, 'Black', 149.99, 1),        -- Wireless Headphones
    (1, 2, 'Blue', 24.99, 2),          -- Phone Case
    (1, 3, '6ft', 12.99, 1),           -- USB Cable
    -- Order 2 (ETSY-2024-001) - Merchant 2
    (2, 5, 'Blue Glaze', 35.99, 2),    -- Handmade Ceramic Mug
    (2, 6, 'Natural Oak', 28.99, 1),   -- Wooden Coasters Set
    -- Order 3 (SHOP-2024-001) - Merchant 3
    (3, 7, 'Silver 42mm', 399.99, 1),  -- Smart Watch
    (3, 8, 'Leather Black', 49.99, 2), -- Watch Band
    -- Order 4 (AMZ-2024-002) - Merchant 1
    (4, 4, 'Portable', 89.99, 1);      -- Bluetooth Speaker

-- Insert fulfillments
INSERT INTO fulfillments (order_id, tracking_company, tracking_number, created_at) VALUES
    (1, 'UPS', '1Z999AA10123456784', '2024-01-15 12:00:00'),
    (2, 'USPS', '9400111899562317453821', '2024-01-16 15:30:00'),
    (4, 'FEDEX', '123456789012', '2024-01-18 17:00:00');

-- Display summary
SELECT
    'Merchants' as table_name,
    COUNT(*) as count
FROM merchants
UNION ALL
SELECT 'Customers', COUNT(*) FROM customers
UNION ALL
SELECT 'Products', COUNT(*) FROM products
UNION ALL
SELECT 'Addresses', COUNT(*) FROM addresses
UNION ALL
SELECT 'Discounts', COUNT(*) FROM discounts
UNION ALL
SELECT 'Orders', COUNT(*) FROM orders
UNION ALL
SELECT 'Order Items', COUNT(*) FROM order_items
UNION ALL
SELECT 'Fulfillments', COUNT(*) FROM fulfillments;
