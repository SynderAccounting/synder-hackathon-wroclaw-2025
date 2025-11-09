"""Suggestion-related business logic."""
from typing import List, Dict, Optional
import re
import json
from datetime import datetime
from database import get_db
from utils.logger import get_logger
from services.connection_service import get_integration_for_product

logger = get_logger(__name__)


def get_suggestions_for_product(product_id: int) -> Optional[List[Dict]]:
    """
    Retrieve all suggestions for a specific product.

    Args:
        product_id: ID of the product.

    Returns:
        List of suggestions ordered by status (new first) and creation date,
        or None if product doesn't exist.

    Raises:
        Exception: If database query fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if product exists
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            logger.warning(f"Product {product_id} not found")
            return None

        # Get suggestions
        cursor.execute('''
            SELECT id, product_id, type, description, status, created_at, applied_at
            FROM suggestions
            WHERE product_id = ?
            ORDER BY
                CASE status
                    WHEN 'new' THEN 1
                    WHEN 'applied' THEN 2
                    ELSE 3
                END,
                created_at DESC
        ''', (product_id,))
        rows = cursor.fetchall()

        suggestions = [dict(row) for row in rows]

    logger.info(f"Retrieved {len(suggestions)} suggestions for product {product_id}")
    return suggestions


def apply_suggestion(suggestion_id: int) -> Dict:
    """
    Apply a suggestion and update product in both database and Shopify/WooCommerce.

    For price suggestions, extracts the new price and updates the product.
    For promo suggestions, creates discount codes in the store.
    Creates an event in the history.

    Args:
        suggestion_id: ID of the suggestion to apply.

    Returns:
        Dict with success status and details.

    Raises:
        ValueError: If suggestion not found or already applied.
        Exception: If database operation fails.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Get suggestion details with product external_id
        cursor.execute('''
            SELECT s.id, s.product_id, s.type, s.description, s.status, s.related_product_ids,
                   p.name as product_name, p.external_id, p.channel
            FROM suggestions s
            JOIN products p ON s.product_id = p.id
            WHERE s.id = ?
        ''', (suggestion_id,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Suggestion {suggestion_id} not found")

        suggestion = dict(row)

        if suggestion['status'] == 'applied':
            raise ValueError(f"Suggestion {suggestion_id} already applied")

        # Update suggestion status
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        cursor.execute('''
            UPDATE suggestions
            SET status = 'applied', applied_at = ?
            WHERE id = ?
        ''', (now, suggestion_id))

        # Get store integration for this product
        try:
            integration = get_integration_for_product(suggestion['product_id'])
        except Exception as e:
            logger.warning(f"Could not get integration for product {suggestion['product_id']}: {e}")
            integration = None

        applied_actions = []

        # Handle different suggestion types
        if suggestion['type'] == 'price':
            new_price = _extract_price_from_suggestion(suggestion, cursor)
            if new_price is not None:
                # Update in database
                cursor.execute('''
                    UPDATE products
                    SET price = ?, updated_at = ?
                    WHERE id = ?
                ''', (new_price, now, suggestion['product_id']))
                logger.info(f"Updated product {suggestion['product_id']} price to {new_price} in database")
                applied_actions.append(f"Changed price to {new_price} PLN in database")

                # Update in Shopify/WooCommerce
                if integration and suggestion['external_id']:
                    try:
                        if integration.update_product_price(suggestion['external_id'], new_price):
                            logger.info(f"Updated product {suggestion['external_id']} price to {new_price} in {suggestion['channel']}")
                            applied_actions.append(f"Changed price to {new_price} PLN in {suggestion['channel']} store")
                        else:
                            logger.error(f"Failed to update price in {suggestion['channel']}")
                            applied_actions.append(f"ERROR: Failed to change price in {suggestion['channel']} store")
                    except Exception as e:
                        logger.error(f"Error updating price in store: {e}")
                        applied_actions.append(f"ERROR: {str(e)}")

        elif suggestion['type'] == 'promo':
            # Promo: Create new product (1+1), reduce stock of originals
            related_ids = _parse_related_product_ids(suggestion.get('related_product_ids'))
            if related_ids and len(related_ids) >= 1 and integration:
                try:
                    # Get products to combine
                    product_ids_to_combine = [suggestion['product_id']] + related_ids[:1]  # Main + 1 other
                    cursor.execute(f'''
                        SELECT id, name, price, stock, external_id, product_type
                        FROM products
                        WHERE id IN ({','.join(['?'] * len(product_ids_to_combine))})
                    ''', product_ids_to_combine)
                    products_to_combine = [dict(row) for row in cursor.fetchall()]

                    # Validate: cannot create promo from bundles or other promos
                    invalid_products = [p for p in products_to_combine if p.get('product_type') in ['bundle', 'promotion', 'Zestaw', 'Promocja']]
                    if invalid_products:
                        invalid_names = ', '.join([p['name'] for p in invalid_products])
                        applied_actions.append(f"ERROR: Cannot create promo from bundles or other promos: {invalid_names}")
                        logger.warning(f"Cannot create promo from bundles/promos: {invalid_names}")
                    elif len(products_to_combine) < 2:
                        applied_actions.append("ERROR: Not all products found for promo")
                    else:
                        # Create promo product name and price
                        promo_name = f"PROMO 1+1: {products_to_combine[0]['name']} + {products_to_combine[1]['name']}"
                        promo_price = products_to_combine[0]['price'] + products_to_combine[1]['price'] * 0.5  # Second one 50% off
                        promo_sku = f"PROMO-{suggestion['product_id']}-{'-'.join(str(p['id']) for p in products_to_combine[:2])}"

                        # Create new promo product in Shopify
                        new_product = integration.create_product({
                            'name': promo_name,
                            'sku': promo_sku,
                            'price': promo_price,
                            'stock': min(p['stock'] for p in products_to_combine),
                            'vendor': 'AI Promo',
                            'product_type': 'promotion'
                        })

                        if new_product:
                            # Save promo to database
                            cursor.execute('''
                                SELECT connection_id FROM products WHERE id = ? LIMIT 1
                            ''', (suggestion['product_id'],))
                            connection_row = cursor.fetchone()
                            connection_id = connection_row[0] if connection_row else None

                            cursor.execute('''
                                INSERT INTO products (sku, name, price, stock, status, channel, connection_id, external_id, vendor, product_type, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                new_product['sku'],
                                new_product['name'],
                                new_product['price'],
                                new_product['stock'],
                                new_product['status'],
                                new_product['channel'],
                                connection_id,
                                new_product['external_id'],
                                new_product.get('vendor', 'AI Promo'),
                                'promotion',
                                now,
                                now
                            ))
                            promo_product_id = cursor.lastrowid

                            # Reduce stock of original products to 0
                            for prod in products_to_combine:
                                integration.update_product_stock(prod['external_id'], 0)
                                cursor.execute('UPDATE products SET stock = 0, status = ? WHERE id = ?',
                                             ('promo_used', prod['id']))

                            applied_actions.append(f"Created PROMO product: {promo_name} ({promo_price} PLN)")
                            applied_actions.append(f"Promo saved in database (ID: {promo_product_id})")
                            applied_actions.append(f"Reduced stock of products: {', '.join([p['name'] for p in products_to_combine])}")
                        else:
                            applied_actions.append("ERROR: Failed to create promo product")
                except Exception as e:
                    logger.error(f"Error creating promo product: {e}")
                    applied_actions.append(f"ERROR: {str(e)}")
            else:
                applied_actions.append("Promo suggestion saved - no related products")

        elif suggestion['type'] == 'bundle':
            # Bundle: Create new product (2-3 items), reduce stock of originals
            related_ids = _parse_related_product_ids(suggestion.get('related_product_ids'))
            if related_ids and len(related_ids) >= 1 and integration:
                try:
                    # Get products to bundle
                    product_ids_to_bundle = [suggestion['product_id']] + related_ids[:2]  # Main + up to 2 others
                    cursor.execute(f'''
                        SELECT id, name, price, stock, external_id, product_type
                        FROM products
                        WHERE id IN ({','.join(['?'] * len(product_ids_to_bundle))})
                    ''', product_ids_to_bundle)
                    products_to_bundle = [dict(row) for row in cursor.fetchall()]

                    # Validate: cannot create bundle from bundles or promos
                    invalid_products = [p for p in products_to_bundle if p.get('product_type') in ['bundle', 'promotion', 'Zestaw', 'Promocja']]
                    if invalid_products:
                        invalid_names = ', '.join([p['name'] for p in invalid_products])
                        applied_actions.append(f"ERROR: Cannot create bundle from bundles or promos: {invalid_names}")
                        logger.warning(f"Cannot create bundle from bundles/promos: {invalid_names}")
                    elif len(products_to_bundle) < 2:
                        applied_actions.append("ERROR: Not all products found for bundle")
                    else:
                        # Create bundle product name and price (10% discount)
                        bundle_name = f"BUNDLE: " + " + ".join([p['name'] for p in products_to_bundle])
                        bundle_price = sum(p['price'] for p in products_to_bundle) * 0.9  # 10% discount
                        bundle_sku = f"BUNDLE-{suggestion['product_id']}-{'-'.join(str(p['id']) for p in products_to_bundle[:3])}"

                        # Create new bundle product in Shopify
                        new_product = integration.create_product({
                            'name': bundle_name[:100],  # Limit name length
                            'sku': bundle_sku,
                            'price': bundle_price,
                            'stock': min(p['stock'] for p in products_to_bundle),
                            'vendor': 'AI Bundle',
                            'product_type': 'bundle'
                        })

                        if new_product:
                            # Save bundle to database
                            cursor.execute('''
                                SELECT connection_id FROM products WHERE id = ? LIMIT 1
                            ''', (suggestion['product_id'],))
                            connection_row = cursor.fetchone()
                            connection_id = connection_row[0] if connection_row else None

                            cursor.execute('''
                                INSERT INTO products (sku, name, price, stock, status, channel, connection_id, external_id, vendor, product_type, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                new_product['sku'],
                                new_product['name'],
                                new_product['price'],
                                new_product['stock'],
                                new_product['status'],
                                new_product['channel'],
                                connection_id,
                                new_product['external_id'],
                                new_product.get('vendor', 'AI Bundle'),
                                'bundle',
                                now,
                                now
                            ))
                            bundle_product_id = cursor.lastrowid

                            # Reduce stock of original products to 0
                            for prod in products_to_bundle:
                                integration.update_product_stock(prod['external_id'], 0)
                                cursor.execute('UPDATE products SET stock = 0, status = ? WHERE id = ?',
                                             ('bundled', prod['id']))

                            applied_actions.append(f"Created BUNDLE: {bundle_name[:50]}... ({bundle_price:.2f} PLN)")
                            applied_actions.append(f"Bundle saved in database (ID: {bundle_product_id})")
                            applied_actions.append(f"Reduced stock of {len(products_to_bundle)} products")
                        else:
                            applied_actions.append("ERROR: Failed to create bundle")
                except Exception as e:
                    logger.error(f"Error creating bundle: {e}")
                    applied_actions.append(f"ERROR: {str(e)}")
            else:
                applied_actions.append("Bundle suggestion saved - no related products")

        # Create event in history
        actions_text = "; ".join(applied_actions) if applied_actions else "Suggestion applied"
        event_description = (
            f"Applied suggestion [{suggestion['type']}] for product "
            f"'{suggestion['product_name']}': {actions_text}"
        )
        cursor.execute('''
            INSERT INTO events (product_id, suggestion_id, event_type, description, created_at)
            VALUES (?, ?, 'suggestion_applied', ?, ?)
        ''', (suggestion['product_id'], suggestion_id, event_description, now))

        event_id = cursor.lastrowid

    logger.info(f"Applied suggestion {suggestion_id} for product {suggestion['product_id']}")

    return {
        'success': True,
        'message': 'Suggestion successfully applied',
        'suggestion_id': suggestion_id,
        'event_id': event_id,
        'applied_at': now,
        'actions': applied_actions
    }


def _extract_price_from_suggestion(suggestion: Dict, cursor) -> Optional[float]:
    """
    Extract new price from a price suggestion description.

    Supports patterns:
    - "Podwyższ cenę do 299.99" -> 299.99
    - "Obniż cenę o 15%" -> calculates from current price
    - "Zwiększenie ceny do 2.49 PLN" -> 2.49
    - "Obniżenie ceny LEWANDORATOR 2000 do 64999 PLN" -> 64999

    Args:
        suggestion: Suggestion dict with 'type', 'description', 'product_id'.
        cursor: Database cursor for fetching current price if needed.

    Returns:
        New price as float, or None if not a price suggestion or can't extract.
    """
    if suggestion['type'] != 'price':
        return None

    description = suggestion['description']

    # Pattern 1: "do X PLN" or "do X"
    match = re.search(r'do\s+(\d+\.?\d*)\s*PLN', description)
    if match:
        return float(match.group(1))

    match = re.search(r'do\s+(\d+\.?\d*)', description)
    if match:
        return float(match.group(1))

    # Pattern 2: "o X%" - percentage change
    match = re.search(r'o\s+(\d+)%', description)
    if match:
        percent = int(match.group(1))
        # Get current price
        cursor.execute('SELECT price FROM products WHERE id = ?', (suggestion['product_id'],))
        current_price = cursor.fetchone()[0]
        return round(current_price * (1 - percent / 100.0), 2)

    logger.warning(f"Could not extract price from suggestion: {description}")
    return None


def _extract_promo_from_suggestion(suggestion: Dict) -> Optional[Dict]:
    """
    Extract promo/discount information from a promo suggestion.

    Patterns:
    - "10% rabatu" -> 10% discount
    - "50% zniżki" -> 50% discount
    - "2 za 1" -> Buy one get one

    Args:
        suggestion: Suggestion dict with 'type' and 'description'.

    Returns:
        Dict with coupon data or None if can't extract.
    """
    if suggestion['type'] != 'promo':
        return None

    description = suggestion['description']

    # Extract percentage discount
    match = re.search(r'(\d+)%\s*(rabatu|zniżki|zni)', description, re.IGNORECASE)
    if match:
        percent = int(match.group(1))
        code = f"PROMO{percent}_{suggestion['product_id']}"
        return {
            'code': code,
            'discount_type': 'percentage',
            'amount': percent,
            'description': description[:100]
        }

    # "2 za 1" or "kup jeden drugi za 50%"
    if '2 za 1' in description.lower() or 'buy one get one' in description.lower():
        return {
            'code': f"BOGO_{suggestion['product_id']}",
            'discount_type': 'percentage',
            'amount': 50,
            'description': 'Buy one get one 50% off'
        }

    # Default: create 10% discount if we can't extract specific amount
    logger.warning(f"Could not extract specific discount from: {description}, using 10% default")
    return {
        'code': f"PROMO10_{suggestion['product_id']}",
        'discount_type': 'percentage',
        'amount': 10,
        'description': description[:100]
    }


def _parse_related_product_ids(related_product_ids_json: Optional[str]) -> List[int]:
    """
    Parse related product IDs from JSON string.

    Args:
        related_product_ids_json: JSON string with list of product IDs.

    Returns:
        List of product IDs.
    """
    if not related_product_ids_json:
        return []

    try:
        ids = json.loads(related_product_ids_json)
        return [int(id) for id in ids if isinstance(id, (int, str))]
    except Exception as e:
        logger.error(f"Failed to parse related_product_ids: {e}")
        return []
