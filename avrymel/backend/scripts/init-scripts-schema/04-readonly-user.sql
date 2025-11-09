-- Create a read-only user for data tables

CREATE USER readonly_user WITH PASSWORD 'readonly123';

-- Grant connection privileges
GRANT CONNECT ON DATABASE multitenant_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;

-- Grant SELECT only on data tables
GRANT SELECT ON merchants TO readonly_user;
GRANT SELECT ON customers TO readonly_user;
GRANT SELECT ON products TO readonly_user;
GRANT SELECT ON addresses TO readonly_user;
GRANT SELECT ON discounts TO readonly_user;
GRANT SELECT ON orders TO readonly_user;
GRANT SELECT ON order_items TO readonly_user;
GRANT SELECT ON fulfillments TO readonly_user;

-- Grant execute on helper functions (needed for merchant context)
GRANT EXECUTE ON FUNCTION set_current_merchant(INTEGER) TO readonly_user;
GRANT EXECUTE ON FUNCTION get_current_merchant() TO readonly_user;
