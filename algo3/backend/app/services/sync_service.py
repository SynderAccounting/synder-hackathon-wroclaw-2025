"""Product synchronization business logic."""
from typing import Dict
from datetime import datetime
from database import get_db
from crypto import decrypt
from integrations.woocommerce import WooCommerceIntegration
from integrations.shopify import ShopifyIntegration
from suggestions_generator import generate_suggestions_for_product
from utils.logger import get_logger

logger = get_logger(__name__)


def sync_connection(connection_id: int) -> Dict:
    """
    Synchronize products from a store connection.

    Fetches products from external platform and upserts them to the database.
    For demo connections, also generates suggestions for new products.

    Args:
        connection_id: ID of the connection to sync.

    Returns:
        Dict with success status and number of products synced.

    Raises:
        ValueError: If connection not found, inactive, or unsupported platform.
        Exception: If sync operation fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get connection details
        connection = _get_connection_details(cursor, connection_id)

        # Decrypt credentials
        api_key = decrypt(connection['api_key_encrypted'])
        api_secret = decrypt(connection['api_secret_encrypted']) if connection['api_secret_encrypted'] else None

        # Create integration instance
        integration = _create_integration_instance(
            connection['platform'],
            connection['store_url'],
            api_key,
            api_secret,
            is_demo=False
        )

        # Fetch products
        products = integration.get_products(limit=100)

        if not products:
            _log_failed_sync(connection_id, 'No products fetched')
            raise Exception('No products fetched or sync failed')

        # Upsert products to database
        products_synced = 0

        for product in products:
            try:
                product_id = _upsert_product(cursor, product, connection_id)
                products_synced += 1
            except Exception as e:
                logger.error(f"Error syncing product {product.get('sku')}: {e}")
                continue

        # Update last_sync timestamp
        now = datetime.utcnow().isoformat()
        cursor.execute('UPDATE store_connections SET last_sync = ? WHERE id = ?', (now, connection_id))

        # Log successful sync
        _log_successful_sync(cursor, connection_id, products_synced, connection['name'])

    logger.info(f"Synced {products_synced} products from connection {connection_id}")
    return {
        'success': True,
        'products_synced': products_synced,
        'message': f'Synchronized {products_synced} products'
    }


def _get_connection_details(cursor, connection_id: int) -> Dict:
    """
    Retrieve connection details from database.

    Args:
        cursor: Database cursor.
        connection_id: Connection ID.

    Returns:
        Connection details dict.

    Raises:
        ValueError: If connection not found or not active.
    """
    cursor.execute('''
        SELECT name, platform, store_url, api_key_encrypted, api_secret_encrypted, is_active
        FROM store_connections WHERE id = ?
    ''', (connection_id,))
    row = cursor.fetchone()

    if not row:
        raise ValueError(f"Connection {connection_id} not found")

    connection = dict(row)
    if not connection['is_active']:
        raise ValueError(f"Connection {connection_id} is not active")

    return connection


def _create_integration_instance(platform: str, store_url: str, api_key: str,
                                  api_secret: str = None, is_demo: bool = False):
    """
    Create appropriate integration instance based on platform.

    Args:
        platform: Platform type (woocommerce, shopify).
        store_url: Store URL.
        api_key: API key.
        api_secret: API secret (optional).
        is_demo: Whether this is a demo connection (deprecated, raises error).

    Returns:
        Integration instance.

    Raises:
        ValueError: If platform is unsupported or demo mode attempted.
    """
    if is_demo:
        raise ValueError('Demo mode is no longer supported. Please provide real API credentials.')

    if platform == 'woocommerce':
        return WooCommerceIntegration(store_url, api_key, api_secret)

    if platform == 'shopify':
        return ShopifyIntegration(store_url, api_key)

    raise ValueError(f'Unsupported platform: {platform}')


def _upsert_product(cursor, product: Dict, connection_id: int) -> int:
    """
    Insert or update a product in the database.

    Args:
        cursor: Database cursor.
        product: Product data dict.
        connection_id: Connection ID.

    Returns:
        Product ID.
    """
    # Check if product exists by SKU
    cursor.execute('SELECT id FROM products WHERE sku = ?', (product['sku'],))
    existing = cursor.fetchone()

    if existing:
        # Update existing product
        cursor.execute('''
            UPDATE products
            SET name = ?, price = ?, stock = ?, status = ?, connection_id = ?,
                external_id = ?, vendor = ?, product_type = ?, updated_at = CURRENT_TIMESTAMP
            WHERE sku = ?
        ''', (product['name'], product['price'], product.get('stock', 0), product['status'],
              connection_id, product['external_id'], product.get('vendor', ''),
              product.get('product_type', ''), product['sku']))
        return existing[0]
    else:
        # Insert new product
        cursor.execute('''
            INSERT INTO products
            (sku, name, price, stock, status, channel, connection_id, external_id, vendor, product_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product['sku'], product['name'], product['price'], product.get('stock', 0),
              product['status'], product['channel'], connection_id, product['external_id'],
              product.get('vendor', ''), product.get('product_type', '')))
        return cursor.lastrowid


def _is_new_product(cursor, sku: str) -> bool:
    """
    Check if product was just created (not updated).

    Args:
        cursor: Database cursor.
        sku: Product SKU.

    Returns:
        True if product is new, False otherwise.
    """
    cursor.execute('''
        SELECT created_at, updated_at FROM products WHERE sku = ?
    ''', (sku,))
    row = cursor.fetchone()
    if not row:
        return False
    # If created_at == updated_at, it's a new product
    return row[0] == row[1]


def _generate_suggestions_for_new_products(cursor, new_products: list) -> None:
    """
    Generate suggestions for newly synced products (demo mode).

    Args:
        cursor: Database cursor.
        new_products: List of new product dicts with id, name, price.
    """
    suggestions_created = 0
    for prod in new_products:
        suggestions = generate_suggestions_for_product(prod['id'], prod['name'], prod['price'])
        for suggestion in suggestions:
            try:
                cursor.execute('''
                    INSERT INTO suggestions (product_id, type, description, status)
                    VALUES (?, ?, ?, ?)
                ''', (suggestion['product_id'], suggestion['type'],
                      suggestion['description'], suggestion['status']))
                suggestions_created += 1
            except Exception as e:
                logger.error(f"Error creating suggestion: {e}")
                continue

    logger.info(f"Generated {suggestions_created} suggestions for {len(new_products)} new products")


def _log_successful_sync(cursor, connection_id: int, products_synced: int, connection_name: str) -> None:
    """
    Log successful sync to database.

    Args:
        cursor: Database cursor.
        connection_id: Connection ID.
        products_synced: Number of products synced.
        connection_name: Name of the connection.
    """
    cursor.execute('''
        INSERT INTO sync_logs (connection_id, sync_type, status, products_synced)
        VALUES (?, 'products', 'success', ?)
    ''', (connection_id, products_synced))

    cursor.execute('''
        INSERT INTO events (event_type, description)
        VALUES ('products_synced', ?)
    ''', (f"Synchronized {products_synced} products from {connection_name}",))


def _log_failed_sync(connection_id: int, error_message: str) -> None:
    """
    Log failed sync to database.

    Args:
        connection_id: Connection ID.
        error_message: Error message.
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sync_logs (connection_id, sync_type, status, error_message)
                VALUES (?, 'products', 'failed', ?)
            ''', (connection_id, error_message))
    except Exception as e:
        logger.error(f"Failed to log sync error: {e}")
