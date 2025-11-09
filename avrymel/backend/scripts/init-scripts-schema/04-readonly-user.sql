-- Create a read-only user for data tables (not tenants table)

CREATE USER readonly_user WITH PASSWORD 'readonly123';

-- Grant connection privileges
GRANT CONNECT ON DATABASE multitenant_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;

-- Grant SELECT only on data tables
-- Explicitly exclude the tenants table
GRANT SELECT ON users TO readonly_user;
GRANT SELECT ON products TO readonly_user;
GRANT SELECT ON orders TO readonly_user;
GRANT SELECT ON order_items TO readonly_user;

-- Grant execute on helper functions (needed for tenant context)
GRANT EXECUTE ON FUNCTION set_tenant(INTEGER) TO readonly_user;
GRANT EXECUTE ON FUNCTION get_current_tenant() TO readonly_user;
