#!/usr/bin/env python3
"""
Generate extensive test data for the multi-tenant PostgreSQL database.
Keeps the existing 3 tenants but adds significantly more users, products, orders, and order items.
"""

import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': "multitenant_db",
    'user': "synderhacks",
    'password': 'synderhacks_password'
}

# Configuration for data generation
CONFIG = {
    'users_per_tenant': 50,      # Generate 50 users per tenant
    'products_per_tenant': 100,  # Generate 100 products per tenant
    'orders_per_tenant': 200,    # Generate 200 orders per tenant
    'max_items_per_order': 5     # Maximum items in each order
}

# Product categories with realistic product names and price ranges
PRODUCT_CATEGORIES = {
    'Electronics': {
        'items': [
            ('Laptop', 500, 2500), ('Desktop Computer', 600, 3000), ('Tablet', 200, 1200),
            ('Smartphone', 300, 1500), ('Smartwatch', 150, 800), ('Wireless Earbuds', 50, 300),
            ('Bluetooth Speaker', 30, 400), ('Webcam', 40, 250), ('Microphone', 50, 400),
            ('Monitor', 150, 1500), ('Keyboard', 30, 300), ('Mouse', 15, 150),
            ('Headphones', 40, 500), ('Gaming Console', 300, 600), ('VR Headset', 300, 1000),
            ('External Hard Drive', 50, 300), ('USB Flash Drive', 10, 100), ('Power Bank', 20, 150),
            ('Laptop Charger', 30, 100), ('Phone Case', 10, 60)
        ]
    },
    'Home & Kitchen': {
        'items': [
            ('Coffee Maker', 50, 400), ('Blender', 40, 300), ('Air Fryer', 60, 250),
            ('Rice Cooker', 40, 200), ('Toaster', 25, 150), ('Microwave', 80, 500),
            ('Vacuum Cleaner', 100, 800), ('Dishwasher', 400, 1500), ('Refrigerator', 600, 3000),
            ('Washing Machine', 500, 2000), ('Dryer', 500, 1800), ('Iron', 20, 100),
            ('Food Processor', 60, 400), ('Pressure Cooker', 50, 300), ('Stand Mixer', 100, 600),
            ('Electric Kettle', 20, 100), ('Slow Cooker', 40, 200), ('Toaster Oven', 60, 250),
            ('Garbage Disposal', 100, 400), ('Water Purifier', 150, 800)
        ]
    },
    'Furniture': {
        'items': [
            ('Office Chair', 100, 800), ('Desk', 150, 1200), ('Bookshelf', 80, 500),
            ('Sofa', 400, 3000), ('Dining Table', 300, 2000), ('Bed Frame', 200, 1500),
            ('Nightstand', 50, 300), ('Dresser', 150, 1000), ('Coffee Table', 80, 600),
            ('TV Stand', 100, 700), ('Wardrobe', 200, 1500), ('Cabinet', 120, 800),
            ('Bar Stool', 40, 200), ('Recliner', 300, 2000), ('Ottoman', 60, 400),
            ('Side Table', 40, 250), ('Filing Cabinet', 80, 500), ('Coat Rack', 30, 150),
            ('Bean Bag', 50, 300), ('Bench', 80, 500)
        ]
    },
    'Sports & Outdoors': {
        'items': [
            ('Yoga Mat', 15, 80), ('Dumbbells', 20, 300), ('Resistance Bands', 10, 50),
            ('Treadmill', 400, 3000), ('Exercise Bike', 200, 2000), ('Tent', 80, 600),
            ('Sleeping Bag', 40, 300), ('Backpack', 30, 250), ('Hiking Boots', 60, 300),
            ('Bicycle', 200, 2000), ('Skateboard', 40, 300), ('Football', 15, 80),
            ('Basketball', 15, 100), ('Tennis Racket', 40, 400), ('Golf Clubs', 200, 2000),
            ('Fishing Rod', 30, 500), ('Camping Stove', 40, 250), ('Cooler', 30, 300),
            ('Kayak', 300, 1500), ('SUP Board', 400, 2000)
        ]
    },
    'Fashion': {
        'items': [
            ('T-Shirt', 10, 80), ('Jeans', 30, 200), ('Jacket', 50, 500),
            ('Sneakers', 40, 300), ('Dress Shoes', 60, 400), ('Sandals', 20, 150),
            ('Dress', 30, 300), ('Suit', 150, 1200), ('Sweater', 30, 250),
            ('Coat', 80, 800), ('Shorts', 20, 100), ('Skirt', 20, 150),
            ('Belt', 15, 100), ('Watch', 50, 2000), ('Sunglasses', 20, 500),
            ('Hat', 15, 100), ('Scarf', 15, 120), ('Gloves', 15, 100),
            ('Socks', 5, 40), ('Tie', 15, 150)
        ]
    }
}

ORDER_STATUSES = ['pending', 'processing', 'shipped', 'completed', 'cancelled']
USER_ROLES = ['admin', 'user', 'manager']

def get_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_tenants(conn):
    """Get existing tenants"""
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM tenants ORDER BY id")
        return cur.fetchall()

def generate_users(conn, tenant_id, tenant_name, count):
    """Generate users for a tenant"""
    print(f"Generating {count} users for {tenant_name}...")

    domain = tenant_name.lower().replace(' ', '').replace('.', '')
    users = []

    with conn.cursor() as cur:
        for _ in range(count):
            email = f"{fake.user_name()}@{domain}.com"
            full_name = fake.name()
            role = random.choice(USER_ROLES)

            try:
                cur.execute(
                    """INSERT INTO users (tenant_id, email, full_name, role)
                       VALUES (%s, %s, %s, %s) RETURNING id""",
                    (tenant_id, email, full_name, role)
                )
                user_id = cur.fetchone()[0]
                users.append(user_id)
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                continue

        conn.commit()

    return users

def generate_products(conn, tenant_id, tenant_name, count):
    """Generate products for a tenant"""
    print(f"Generating {count} products for {tenant_name}...")

    products = []

    with conn.cursor() as cur:
        for _ in range(count):
            category = random.choice(list(PRODUCT_CATEGORIES.keys()))
            item_template = random.choice(PRODUCT_CATEGORIES[category]['items'])

            # Create unique product name with model/variant
            name = f"{item_template[0]} {fake.word().capitalize()} {random.randint(100, 999)}"
            description = fake.text(max_nb_chars=200)
            price = round(random.uniform(item_template[1], item_template[2]), 2)
            stock_quantity = random.randint(0, 500)

            cur.execute(
                """INSERT INTO products (tenant_id, name, description, price, stock_quantity)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (tenant_id, name, description, price, stock_quantity)
            )
            product_id = cur.fetchone()[0]
            products.append((product_id, price))

        conn.commit()

    return products

def generate_orders(conn, tenant_id, tenant_name, user_ids, product_data, count):
    """Generate orders with order items for a tenant"""
    print(f"Generating {count} orders for {tenant_name}...")

    tenant_prefix = ''.join([c for c in tenant_name if c.isupper()])[:4]
    if not tenant_prefix:
        tenant_prefix = tenant_name[:4].upper()

    with conn.cursor() as cur:
        order_counter = 1

        for _ in range(count):
            user_id = random.choice(user_ids)
            order_number = f"{tenant_prefix}-{datetime.now().year}-{order_counter:05d}"
            order_counter += 1

            status = random.choice(ORDER_STATUSES)

            # Create random date in the last 6 months
            days_ago = random.randint(0, 180)
            created_at = datetime.now() - timedelta(days=days_ago)

            # First insert order with total_amount = 0
            cur.execute(
                """INSERT INTO orders (tenant_id, user_id, order_number, status, total_amount, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (tenant_id, user_id, order_number, status, 0, created_at)
            )
            order_id = cur.fetchone()[0]

            # Generate order items
            num_items = random.randint(1, CONFIG['max_items_per_order'])
            selected_products = random.sample(product_data, min(num_items, len(product_data)))

            total_amount = 0
            for product_id, price in selected_products:
                quantity = random.randint(1, 5)
                unit_price = price
                subtotal = round(unit_price * quantity, 2)
                total_amount += subtotal

                cur.execute(
                    """INSERT INTO order_items (tenant_id, order_id, product_id, quantity, unit_price, subtotal)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (tenant_id, order_id, product_id, quantity, unit_price, subtotal)
                )

            # Update order with correct total amount
            cur.execute(
                "UPDATE orders SET total_amount = %s WHERE id = %s",
                (total_amount, order_id)
            )

        conn.commit()

def display_summary(conn):
    """Display summary of data in database"""
    print("\n" + "="*70)
    print("DATABASE SUMMARY")
    print("="*70)

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                t.name as tenant,
                COUNT(DISTINCT u.id) as users,
                COUNT(DISTINCT p.id) as products,
                COUNT(DISTINCT o.id) as orders,
                COUNT(DISTINCT oi.id) as order_items,
                COALESCE(SUM(o.total_amount), 0) as total_revenue
            FROM tenants t
            LEFT JOIN users u ON t.id = u.tenant_id
            LEFT JOIN products p ON t.id = p.tenant_id
            LEFT JOIN orders o ON t.id = o.tenant_id
            LEFT JOIN order_items oi ON t.id = oi.tenant_id
            GROUP BY t.id, t.name
            ORDER BY t.id
        """)

        results = cur.fetchall()

        print(f"\n{'Tenant':<25} {'Users':<8} {'Products':<10} {'Orders':<8} {'Items':<8} {'Revenue':<12}")
        print("-" * 70)

        for row in results:
            tenant, users, products, orders, items, revenue = row
            print(f"{tenant:<25} {users:<8} {products:<10} {orders:<8} {items:<8} ${revenue:<11,.2f}")

        # Overall totals
        cur.execute("""
            SELECT
                COUNT(DISTINCT id) as total_tenants,
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM products) as total_products,
                (SELECT COUNT(*) FROM orders) as total_orders,
                (SELECT COUNT(*) FROM order_items) as total_items,
                (SELECT COALESCE(SUM(total_amount), 0) FROM orders) as total_revenue
            FROM tenants
        """)

        totals = cur.fetchone()
        print("-" * 70)
        print(f"{'TOTAL':<25} {totals[1]:<8} {totals[2]:<10} {totals[3]:<8} {totals[4]:<8} ${totals[5]:<11,.2f}")

    print("="*70 + "\n")

def main():
    print("="*70)
    print("MULTI-TENANT DATABASE - TEST DATA GENERATOR")
    print("="*70)
    print("\nConfiguration:")
    print(f"  - Users per tenant: {CONFIG['users_per_tenant']}")
    print(f"  - Products per tenant: {CONFIG['products_per_tenant']}")
    print(f"  - Orders per tenant: {CONFIG['orders_per_tenant']}")
    print(f"  - Max items per order: {CONFIG['max_items_per_order']}")
    print("\n" + "="*70 + "\n")

    conn = get_connection()

    try:
        # Get existing tenants
        tenants = get_tenants(conn)
        print(f"Found {len(tenants)} existing tenants\n")

        # Generate data for each tenant
        for tenant_id, tenant_name in tenants:
            print(f"\n{'='*70}")
            print(f"Processing: {tenant_name} (ID: {tenant_id})")
            print(f"{'='*70}\n")

            # Generate users
            user_ids = generate_users(conn, tenant_id, tenant_name, CONFIG['users_per_tenant'])

            # If no new users were created, get existing users
            if not user_ids:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM users WHERE tenant_id = %s", (tenant_id,))
                    user_ids = [row[0] for row in cur.fetchall()]

            print(f"  ✓ Created/found {len(user_ids)} users")

            # Generate products
            product_data = generate_products(conn, tenant_id, tenant_name, CONFIG['products_per_tenant'])
            print(f"  ✓ Created {len(product_data)} products")

            # Generate orders and order items
            generate_orders(conn, tenant_id, tenant_name, user_ids, product_data, CONFIG['orders_per_tenant'])
            print(f"  ✓ Created {CONFIG['orders_per_tenant']} orders with items")

        # Display summary
        display_summary(conn)

        print("✓ Test data generation completed successfully!\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
