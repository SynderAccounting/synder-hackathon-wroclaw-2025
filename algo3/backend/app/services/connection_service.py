"""Store connection management business logic."""
from typing import List, Dict
from datetime import datetime
from database import get_db
from crypto import encrypt, decrypt
from integrations.woocommerce import WooCommerceIntegration
from integrations.shopify import ShopifyIntegration
from utils.logger import get_logger

logger = get_logger(__name__)


def get_all_connections() -> List[Dict]:
    """
    Retrieve all store connections.

    Returns:
        List of store connections ordered by creation date (newest first).

    Raises:
        Exception: If database query fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, platform, store_url, is_active, last_sync, created_at
            FROM store_connections
            ORDER BY created_at DESC
        ''')
        rows = cursor.fetchall()
        connections = [dict(row) for row in rows]

    logger.info(f"Retrieved {len(connections)} connections")
    return connections


def create_connection(data: Dict) -> Dict:
    """
    Create a new store connection with encrypted credentials.

    Tests the connection before saving to database.

    Args:
        data: Dict containing name, platform, store_url, api_key, optional api_secret.

    Returns:
        Dict with success status and connection_id.

    Raises:
        ValueError: If connection test fails or invalid platform.
        Exception: If database operation fails.
    """
    # Encrypt credentials
    api_key_encrypted = encrypt(data['api_key'])
    api_secret_encrypted = encrypt(data.get('api_secret', '')) if data.get('api_secret') else None

    # Test connection before saving
    platform = data['platform'].lower()

    integration = _create_integration(
        platform=platform,
        store_url=data['store_url'],
        api_key=data['api_key'],
        api_secret=data.get('api_secret'),
        is_demo=False
    )

    if not integration.test_connection():
        raise ValueError('Connection test failed. Please check your credentials.')

    # Save connection
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO store_connections
            (name, platform, store_url, api_key_encrypted, api_secret_encrypted, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (data['name'], platform, data['store_url'], api_key_encrypted, api_secret_encrypted))

        connection_id = cursor.lastrowid

        # Log event
        event_time = datetime.now().isoformat(sep=' ', timespec='seconds')
        cursor.execute('''
            INSERT INTO events (event_type, description, created_at)
            VALUES ('connection_created', ?, ?)
        ''', (f"Dodano nowe połączenie: {data['name']} ({platform})", event_time))

    logger.info(f"Created connection {connection_id}: {data['name']}")
    return {
        'success': True,
        'connection_id': connection_id,
        'message': 'Połączenie zostało pomyślnie utworzone'
    }


def delete_connection(connection_id: int) -> None:
    """
    Delete a store connection and its associated products.

    Args:
        connection_id: ID of the connection to delete.

    Raises:
        ValueError: If connection not found.
        Exception: If database operation fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get connection name for logging
        cursor.execute('SELECT name FROM store_connections WHERE id = ?', (connection_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Connection {connection_id} not found")

        connection_name = row[0]

        # Delete associated products first
        cursor.execute('DELETE FROM products WHERE connection_id = ?', (connection_id,))

        # Delete connection
        cursor.execute('DELETE FROM store_connections WHERE id = ?', (connection_id,))

        # Log event
        event_time = datetime.now().isoformat(sep=' ', timespec='seconds')
        cursor.execute('''
            INSERT INTO events (event_type, description, created_at)
            VALUES ('connection_deleted', ?, ?)
        ''', (f"Usunięto połączenie: {connection_name}", event_time))

    logger.info(f"Deleted connection {connection_id}")


def toggle_connection(connection_id: int) -> bool:
    """
    Toggle connection active/inactive status.

    Args:
        connection_id: ID of the connection to toggle.

    Returns:
        New active status (True/False).

    Raises:
        ValueError: If connection not found.
        Exception: If database operation fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT is_active, name FROM store_connections WHERE id = ?', (connection_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Connection {connection_id} not found")

        is_active, name = row
        new_status = 0 if is_active else 1

        cursor.execute('UPDATE store_connections SET is_active = ? WHERE id = ?', (new_status, connection_id))

        status_text = 'aktywowano' if new_status else 'dezaktywowano'
        cursor.execute('''
            INSERT INTO events (event_type, description)
            VALUES ('connection_toggled', ?)
        ''', (f"{status_text.capitalize()} połączenie: {name}",))

    logger.info(f"Toggled connection {connection_id} to {bool(new_status)}")
    return bool(new_status)


def quick_demo_setup() -> List[int]:
    """
    Quickly create demo stores for testing.

    DEPRECATED: Demo mode is no longer supported.

    Returns:
        List of created connection IDs.

    Raises:
        ValueError: Always raised as demo mode is deprecated.
    """
    raise ValueError('Demo mode is no longer supported. Please create real store connections with valid API credentials.')


def get_integration_for_product(product_id: int):
    """
    Get integration instance for a product's store connection.

    Args:
        product_id: Product ID.

    Returns:
        Integration instance (ShopifyIntegration or WooCommerceIntegration).

    Raises:
        ValueError: If product or connection not found, or connection inactive.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get product and connection details
        cursor.execute('''
            SELECT p.connection_id, p.channel,
                   sc.platform, sc.store_url, sc.api_key_encrypted, sc.api_secret_encrypted, sc.is_active
            FROM products p
            LEFT JOIN store_connections sc ON p.connection_id = sc.id
            WHERE p.id = ?
        ''', (product_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Product {product_id} not found")

        connection_id, channel, platform, store_url, api_key_encrypted, api_secret_encrypted, is_active = row

        if not connection_id:
            raise ValueError(f"Product {product_id} has no store connection")

        if not is_active:
            raise ValueError(f"Store connection for product {product_id} is inactive")

        # Decrypt credentials
        api_key = decrypt(api_key_encrypted)
        api_secret = decrypt(api_secret_encrypted) if api_secret_encrypted else None

        # Create integration
        return _create_integration(platform, store_url, api_key, api_secret, is_demo=False)


def _create_integration(platform: str, store_url: str, api_key: str,
                        api_secret: str = None, is_demo: bool = False):
    """
    Factory function to create appropriate integration instance.

    Args:
        platform: Platform type (woocommerce, shopify).
        store_url: Store URL.
        api_key: API key.
        api_secret: API secret (optional, required for WooCommerce).
        is_demo: Whether this is a demo connection (deprecated, raises error).

    Returns:
        Integration instance.

    Raises:
        ValueError: If platform is unsupported or WooCommerce missing api_secret.
    """
    if is_demo or platform == 'demo':
        raise ValueError('Demo mode is no longer supported. Please provide real API credentials.')

    if platform == 'woocommerce':
        if not api_secret:
            raise ValueError('WooCommerce requires both api_key and api_secret')
        return WooCommerceIntegration(store_url, api_key, api_secret)

    if platform == 'shopify':
        return ShopifyIntegration(store_url, api_key)

    raise ValueError(f'Unsupported platform: {platform}')
