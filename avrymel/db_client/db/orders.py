"""Database operations for Order objects."""

import sys
from pathlib import Path
from typing import Optional

from psycopg2.extensions import connection as Connection
from psycopg2.extras import RealDictCursor

# Add mock_api to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "mock_api"))

from models.order import Order


def _insert_customer(conn: Connection, order: Order, merchant_id: int) -> int:
    """Insert or get existing customer.

    Args:
        conn: Database connection.
        order: Order object containing customer data.
        merchant_id: Merchant ID to link to customer.

    Returns:
        Customer ID.
    """
    cursor = conn.cursor()

    # Try to get existing customer by email
    cursor.execute(
        """
        SELECT id FROM customers WHERE email = %s
        """,
        (order.customer.email,),
    )
    result = cursor.fetchone()

    if result:
        return result[0]

    # Insert new customer
    cursor.execute(
        """
        INSERT INTO customers (merchant_id, email, first_name, last_name)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (merchant_id, order.customer.email, order.customer.first_name, order.customer.last_name),
    )
    return cursor.fetchone()[0]


def _insert_address(conn: Connection, address) -> int:
    """Insert address and return its ID.

    Args:
        conn: Database connection.
        address: Address object.

    Returns:
        Address ID.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO addresses (
            first_name, last_name, company, address, city,
            state_or_region, country, postal_code, country_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            address.first_name,
            address.last_name,
            address.company,
            address.address,
            address.city,
            address.state_or_region,
            address.country,
            address.postal_code,
            address.country_code,
        ),
    )
    return cursor.fetchone()[0]


def _insert_discount(conn: Connection, order: Order) -> Optional[int]:
    """Insert or get existing discount.

    Args:
        conn: Database connection.
        order: Order object containing discount data.

    Returns:
        Discount ID or None if no discount.
    """
    if not order.discount:
        return None

    cursor = conn.cursor()

    # Try to get existing discount by code
    cursor.execute(
        """
        SELECT id FROM discounts WHERE discount_code = %s
        """,
        (order.discount.discount_code,),
    )
    result = cursor.fetchone()

    if result:
        return result[0]

    # Insert new discount
    cursor.execute(
        """
        INSERT INTO discounts (discount_code, discount_percent)
        VALUES (%s, %s)
        RETURNING id
        """,
        (order.discount.discount_code, order.discount.discount_percent),
    )
    return cursor.fetchone()[0]


def _insert_or_get_product(conn: Connection, merchant_id: int, item) -> int:
    """Insert or get existing product.

    Args:
        conn: Database connection.
        merchant_id: Merchant ID who owns this product.
        item: Item object containing product data.

    Returns:
        Product ID.
    """
    cursor = conn.cursor()

    # Try to get existing product by product_id and merchant_id
    cursor.execute(
        """
        SELECT id FROM products WHERE merchant_id = %s AND product_id = %s
        """,
        (merchant_id, item.item_id),
    )
    result = cursor.fetchone()

    if result:
        return result[0]

    # Insert new product
    cursor.execute(
        """
        INSERT INTO products (merchant_id, product_id, product_name, base_price)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (merchant_id, item.item_id, item.item_name, item.item_price),
    )
    return cursor.fetchone()[0]


def _insert_order_items(conn: Connection, order_db_id: int, merchant_id: int, order: Order) -> None:
    """Insert order items.

    Args:
        conn: Database connection.
        order_db_id: Database ID of the order.
        merchant_id: Merchant ID who owns the products.
        order: Order object containing items.
    """
    cursor = conn.cursor()

    for item in order.items:
        # Get or create product
        product_id = _insert_or_get_product(conn, merchant_id, item.item)

        # Insert order item referencing the product
        cursor.execute(
            """
            INSERT INTO order_items (
                order_id, product_id, variant_name, price_at_purchase, quantity
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                order_db_id,
                product_id,
                item.variant_name,
                item.item.item_price,
                item.quantity,
            ),
        )


def _insert_fulfillment(conn: Connection, order_db_id: int, order: Order) -> None:
    """Insert fulfillment information.

    Args:
        conn: Database connection.
        order_db_id: Database ID of the order.
        order: Order object containing fulfillment data.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO fulfillments (
            order_id, tracking_company, tracking_number, created_at
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            order_db_id,
            order.fulfillment.tracking_company.value,
            order.fulfillment.tracking_number,
            order.fulfillment.created_at,
        ),
    )


def insert_order(conn: Connection, order: Order, merchant_id: int) -> int:
    """Insert a complete Order into the database.

    This function handles inserting all related data (customer, addresses,
    discount, items, fulfillment) in the correct order with proper foreign
    key relationships.

    Args:
        conn: Database connection.
        order: Order instance to insert.
        merchant_id: ID of the merchant who owns this order.

    Returns:
        The database ID of the inserted order.
    """
    cursor = conn.cursor()

    # Set RLS context for the current merchant
    cursor.execute("SELECT set_current_merchant(%s)", (merchant_id,))

    customer_id = _insert_customer(conn, order, merchant_id)
    billing_address_id = _insert_address(conn, order.billing_address)
    shipping_address_id = _insert_address(conn, order.shipping_address)
    discount_id = _insert_discount(conn, order)

    # Insert the main order
    cursor.execute(
        """
        INSERT INTO orders (
            order_id, service, customer_id, billing_address_id,
            shipping_address_id, discount_id, created_at, updated_at,
            currency, financial_status, subtotal, total_tax, final_price
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            order.order_id,
            order.service,
            customer_id,
            billing_address_id,
            shipping_address_id,
            discount_id,
            order.created_at,
            order.updated_at,
            order.currency,
            order.financial_status.value,
            order.subtotal,
            order.total_tax,
            order.final_price,
        ),
    )

    order_db_id = cursor.fetchone()[0]

    # Insert order items and fulfillment
    _insert_order_items(conn, order_db_id, merchant_id, order)
    _insert_fulfillment(conn, order_db_id, order)

    return order_db_id


def get_order_by_order_id(conn: Connection, order_id: str) -> Optional[dict]:
    """Retrieve an order by its order_id.

    Args:
        conn: Database connection.
        order_id: The order_id to search for.

    Returns:
        Dictionary containing order data or None if not found.
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT
            o.*,
            c.email, c.first_name as customer_first_name, c.last_name as customer_last_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.order_id = %s
        """,
        (order_id,),
    )
    return cursor.fetchone()


def get_orders_by_service(
    conn: Connection, service: str, limit: int = 100
) -> list[dict]:
    """Retrieve orders for a specific service.

    Args:
        conn: Database connection.
        service: Service name (Amazon, Etsy, or Shopify).
        limit: Maximum number of orders to return.

    Returns:
        List of order dictionaries.
    """
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT
            o.*,
            c.email, c.first_name as customer_first_name, c.last_name as customer_last_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.service = %s
        ORDER BY o.created_at DESC
        LIMIT %s
        """,
        (service, limit),
    )
    return cursor.fetchall()
