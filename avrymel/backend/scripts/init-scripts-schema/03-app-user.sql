-- Create application user that respects RLS
CREATE USER app_user WITH PASSWORD 'app123';

-- Grant necessary privileges
GRANT CONNECT ON DATABASE multitenant_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION set_tenant(INTEGER) TO app_user;
GRANT EXECUTE ON FUNCTION get_current_tenant() TO app_user;

-- Force RLS even for table owner (admin user)
-- This makes RLS work for demonstration purposes even with admin user
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE products FORCE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
ALTER TABLE order_items FORCE ROW LEVEL SECURITY;

-- Display user info
\echo ''
\echo 'Application user created!'
\echo 'Username: app_user'
\echo 'Password: app123'
\echo ''
\echo 'RLS is now FORCED on all tables - it will apply even to the admin user.'
\echo ''
