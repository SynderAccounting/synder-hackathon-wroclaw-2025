DROP TABLE IF EXISTS sales_history;
DROP TABLE IF EXISTS product_data;

CREATE TABLE product_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(100) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    cogs DECIMAL(10, 2) NOT NULL,
    lead_time_days INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(100) NOT NULL,
    sale_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES product_data(sku) ON DELETE CASCADE
);

CREATE INDEX idx_sales_sku ON sales_history(sku);
CREATE INDEX idx_sales_date ON sales_history(sale_date);

CREATE TABLE chat_sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(100) NOT NULL,
    session_data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES product_data(sku) ON DELETE CASCADE
);

CREATE INDEX idx_chat_sku ON chat_sessions(sku);
CREATE INDEX idx_chat_expires ON chat_sessions(expires_at);

INSERT INTO product_data (sku, product_name, cogs, lead_time_days) VALUES
('SKU-001', 'Premium Wireless Headphones', 45.00, 14),
('SKU-002', 'Smart Watch Pro', 120.00, 21),
('SKU-003', 'USB-C Cable 2m', 3.50, 7);
