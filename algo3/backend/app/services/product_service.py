"""Product-related business logic."""
from typing import List, Dict, Optional
from datetime import datetime
from database import get_db
from models import db_row_to_product
from utils.logger import get_logger
from services.connection_service import get_integration_for_product
from crypto import decrypt

logger = get_logger(__name__)


def get_all_products() -> List[Dict]:
    """
    Retrieve all products with their applied suggestions.

    Returns:
        List of products in standardized ProductRecord format.

    Raises:
        Exception: If database query fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                p.id, p.sku, p.name, p.price, p.stock, p.status, p.channel, p.created_at,
                p.vendor, p.product_type,
                s.id as applied_suggestion_id,
                s.type as applied_suggestion_type,
                s.description as applied_suggestion_desc
            FROM products p
            LEFT JOIN suggestions s ON p.id = s.product_id AND s.status = 'applied'
            ORDER BY p.id
        ''')
        rows = cursor.fetchall()

        # Group by product (in case multiple suggestions applied)
        products_dict = {}
        for row in rows:
            row_dict = dict(row)
            product_id = row_dict['id']

            if product_id not in products_dict:
                products_dict[product_id] = {
                    'row': row_dict,
                    'promotions': []
                }

            # Add applied suggestion if exists
            if row_dict['applied_suggestion_id']:
                products_dict[product_id]['promotions'].append({
                    'id': row_dict['applied_suggestion_id'],
                    'type': row_dict['applied_suggestion_type'],
                    'description': row_dict['applied_suggestion_desc']
                })

        # Convert to ProductRecord using our standard function
        products = []
        for product_data in products_dict.values():
            product = db_row_to_product(product_data['row'], product_data['promotions'])
            products.append(product.dict())

    logger.info(f"Retrieved {len(products)} products")
    return products


def get_product_details(product_id: int) -> Optional[Dict]:
    """
    Get detailed product information including applied suggestions and event history.

    Args:
        product_id: ID of the product to retrieve.

    Returns:
        Product details dict including applied_suggestions and event_history,
        or None if product not found.

    Raises:
        Exception: If database query fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get product details
        cursor.execute('''
            SELECT id, sku, name, price, stock, status, channel, connection_id, vendor, product_type, created_at, updated_at
            FROM products
            WHERE id = ?
        ''', (product_id,))
        row = cursor.fetchone()

        if not row:
            logger.warning(f"Product {product_id} not found")
            return None

        product = dict(row)

        # Get applied suggestions for this product
        cursor.execute('''
            SELECT id, type, description, applied_at
            FROM suggestions
            WHERE product_id = ? AND status = 'applied'
            ORDER BY applied_at DESC
        ''', (product_id,))
        product['applied_suggestions'] = [dict(row) for row in cursor.fetchall()]

        # Get event history for this product
        cursor.execute('''
            SELECT id, event_type, description, created_at
            FROM events
            WHERE product_id = ?
            ORDER BY created_at DESC
            LIMIT 20
        ''', (product_id,))
        product['event_history'] = [dict(row) for row in cursor.fetchall()]

    logger.info(f"Retrieved details for product {product_id}")
    return product


def create_product_in_store(data: Dict) -> Dict:
    """
    Create a new product in a connected store (Shopify/WooCommerce).

    Args:
        data: Dict with:
            - connection_id: int (required)
            - name: str (required)
            - price: float (required)
            - stock: int (optional, default 0)
            - sku: str (optional)
            - description: str (optional)

    Returns:
        Dict with created product details.

    Raises:
        ValueError: If connection not found or inactive.
        Exception: If creation fails.
    """
    connection_id = data.get('connection_id')
    if not connection_id:
        raise ValueError("connection_id is required")

    # Get store connection and credentials
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT platform, store_url, api_key_encrypted, api_secret_encrypted, is_active
            FROM store_connections
            WHERE id = ?
        ''', (connection_id,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Connection {connection_id} not found")

        platform, store_url, api_key_encrypted, api_secret_encrypted, is_active = row

        if not is_active:
            raise ValueError(f"Connection {connection_id} is inactive")

        # Decrypt credentials
        api_key = decrypt(api_key_encrypted)
        api_secret = decrypt(api_secret_encrypted) if api_secret_encrypted else None

        # Create integration
        from services.connection_service import _create_integration
        integration = _create_integration(platform, store_url, api_key, api_secret)

        # Create product in store
        product_data = {
            'name': data['name'],
            'price': data['price'],
            'stock': data.get('stock', 0),
            'sku': data.get('sku', ''),
            'description': data.get('description', '')
        }

        created_product = integration.create_product(product_data)
        if not created_product:
            raise Exception("Failed to create product in store")

        # Ensure SKU is not empty
        if not created_product.get('sku') or created_product['sku'].strip() == '':
            created_product['sku'] = f"{platform.upper()}-{created_product['external_id']}"

        # Save to database
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        cursor.execute('''
            INSERT INTO products (connection_id, external_id, sku, name, price, stock, status, channel, vendor, product_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            connection_id,
            created_product['external_id'],
            created_product['sku'],
            created_product['name'],
            created_product['price'],
            created_product['stock'],
            created_product['status'],
            created_product['channel'],
            created_product.get('vendor', ''),
            created_product.get('product_type', ''),
            now,
            now
        ))

        product_id = cursor.lastrowid

        # Log event
        cursor.execute('''
            INSERT INTO events (product_id, event_type, description, created_at)
            VALUES (?, 'product_created', ?, ?)
        ''', (product_id, f"Created product: {created_product['name']}", now))

    logger.info(f"Created product {product_id}: {created_product['name']} in {platform}")

    return {
        'success': True,
        'product_id': product_id,
        'external_id': created_product['external_id'],
        'name': created_product['name'],
        'price': created_product['price'],
        'stock': created_product['stock'],
        'message': f'Product created in {platform} store'
    }


def update_product_in_store(product_id: int, updates: Dict) -> Dict:
    """
    Update a product in connected store (Shopify/WooCommerce).

    Args:
        product_id: Product ID to update.
        updates: Dict with optional fields:
            - price: float
            - stock: int
            - sku: str

    Returns:
        Dict with success status and updated fields.

    Raises:
        ValueError: If product not found or no updates provided.
        Exception: If update fails.
    """
    if not updates:
        raise ValueError("No updates provided")

    with get_db() as conn:
        cursor = conn.cursor()

        # Get product details
        cursor.execute('''
            SELECT id, external_id, name, channel, connection_id
            FROM products
            WHERE id = ?
        ''', (product_id,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Product {product_id} not found")

        product = dict(row)

        # Get integration
        integration = get_integration_for_product(product_id)

        # Update in store
        success = integration.update_product(product['external_id'], updates)
        if not success:
            raise Exception(f"Failed to update product in {product['channel']}")

        # Update in database
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        update_fields = []
        update_values = []

        if 'price' in updates:
            update_fields.append('price = ?')
            update_values.append(updates['price'])

        if 'stock' in updates:
            update_fields.append('stock = ?')
            update_values.append(updates['stock'])

        if 'sku' in updates:
            update_fields.append('sku = ?')
            update_values.append(updates['sku'])

        update_fields.append('updated_at = ?')
        update_values.append(now)

        update_values.append(product_id)

        cursor.execute(f'''
            UPDATE products
            SET {', '.join(update_fields)}
            WHERE id = ?
        ''', update_values)

        # Log event
        updates_desc = ', '.join([f"{k}={v}" for k, v in updates.items()])
        cursor.execute('''
            INSERT INTO events (product_id, event_type, description, created_at)
            VALUES (?, 'product_updated', ?, ?)
        ''', (product_id, f"Zaktualizowano produkt: {updates_desc}", now))

    logger.info(f"Updated product {product_id} in {product['channel']}: {updates_desc}")

    return {
        'success': True,
        'product_id': product_id,
        'updates_applied': updates,
        'message': f'Produkt został zaktualizowany w sklepie {product["channel"]}'
    }
