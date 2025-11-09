import requests
import logging
from typing import List, Dict, Optional
from .base import StoreIntegration

logger = logging.getLogger(__name__)

class ShopifyIntegration(StoreIntegration):
    """Shopify Admin API integration"""

    def __init__(self, store_url: str, access_token: str):
        # Store URL should be in format: myshop.myshopify.com
        super().__init__(store_url, access_token)
        self.api_base = f"https://{self.store_url}/admin/api/2024-01"

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make authenticated request to Shopify API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        headers = {
            'X-Shopify-Access-Token': self.api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify API request failed: {e}")
            return None

    def test_connection(self) -> bool:
        """Test if API credentials are valid"""
        try:
            result = self._request('GET', '/products.json', params={'limit': 1})
            return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_products(self, limit: int = 100) -> List[Dict]:
        """Fetch products from Shopify store"""
        products = []

        result = self._request('GET', '/products.json', params={'limit': min(limit, 250)})

        if not result or 'products' not in result:
            return []

        for product in result['products']:
            # Shopify products can have multiple variants
            for variant in product.get('variants', []):
                variant_id = variant.get('id')
                if not variant_id:
                    continue

                # Use SKU if available, otherwise generate one
                sku = variant.get('sku')
                if not sku or sku.strip() == '':
                    sku = f"SHOPIFY-{variant_id}"

                products.append({
                    'external_id': str(variant_id),
                    'sku': sku,
                    'name': f"{product['title']} - {variant['title']}" if variant.get('title') != 'Default Title' else product['title'],
                    'price': float(variant.get('price', 0)),
                    'stock': int(variant.get('inventory_quantity', 0)),
                    'status': 'active' if variant.get('inventory_quantity', 0) > 0 else 'low_stock',
                    'channel': 'shopify',
                    'vendor': product.get('vendor', ''),
                    'product_type': product.get('product_type', '')
                })

        return products[:limit]

    def create_coupon(self, coupon_data: Dict) -> Dict:
        """Create a price rule (discount) in Shopify

        Args:
            coupon_data: {
                'code': str,
                'discount_type': 'percentage' | 'fixed_amount',
                'amount': float,
                'description': str
            }
        """
        # First, create the price rule
        price_rule_payload = {
            'price_rule': {
                'title': coupon_data.get('description', coupon_data['code']),
                'target_type': 'line_item',
                'target_selection': 'all',
                'allocation_method': 'across',
                'value_type': 'percentage' if coupon_data.get('discount_type') == 'percentage' else 'fixed_amount',
                'value': f"-{coupon_data['amount']}",
                'customer_selection': 'all',
                'starts_at': coupon_data.get('starts_at', '2024-01-01T00:00:00Z')
            }
        }

        price_rule = self._request('POST', '/price_rules.json', json=price_rule_payload)

        if not price_rule or 'price_rule' not in price_rule:
            return {'success': False, 'error': 'Failed to create price rule'}

        price_rule_id = price_rule['price_rule']['id']

        # Now create the discount code
        discount_code_payload = {
            'discount_code': {
                'code': coupon_data['code']
            }
        }

        discount_code = self._request('POST', f'/price_rules/{price_rule_id}/discount_codes.json', json=discount_code_payload)

        if discount_code and 'discount_code' in discount_code:
            return {
                'success': True,
                'price_rule_id': price_rule_id,
                'code': discount_code['discount_code']['code'],
                'amount': coupon_data['amount']
            }
        else:
            return {'success': False, 'error': 'Failed to create discount code'}

    def update_product_price(self, product_id: str, new_price: float) -> bool:
        """Update product variant price in Shopify"""
        payload = {
            'variant': {
                'id': int(product_id),
                'price': str(new_price)
            }
        }

        result = self._request('PUT', f'/variants/{product_id}.json', json=payload)
        return result is not None

    def update_product_stock(self, product_id: str, new_stock: int) -> bool:
        """Update product variant inventory in Shopify"""
        # First get the inventory item ID
        variant = self._request('GET', f'/variants/{product_id}.json')
        if not variant or 'variant' not in variant:
            logger.error(f"Failed to fetch variant {product_id}")
            return False

        inventory_item_id = variant['variant'].get('inventory_item_id')
        if not inventory_item_id:
            logger.error(f"No inventory_item_id for variant {product_id}")
            return False

        # Get inventory levels to find location_id
        inventory_levels = self._request('GET', f'/inventory_levels.json', params={
            'inventory_item_ids': inventory_item_id
        })

        if not inventory_levels or 'inventory_levels' not in inventory_levels or not inventory_levels['inventory_levels']:
            logger.error(f"No inventory levels found for inventory_item_id {inventory_item_id}")
            return False

        location_id = inventory_levels['inventory_levels'][0]['location_id']

        # Update inventory level
        payload = {
            'location_id': location_id,
            'inventory_item_id': inventory_item_id,
            'available': new_stock
        }

        result = self._request('POST', '/inventory_levels/set.json', json=payload)
        return result is not None

    def create_product(self, product_data: Dict) -> Optional[Dict]:
        """Create a new product in Shopify

        Args:
            product_data: {
                'name': str,
                'price': float,
                'stock': int,
                'sku': str (optional),
                'description': str (optional)
            }

        Returns:
            Created product dict or None
        """
        payload = {
            'product': {
                'title': product_data['name'],
                'body_html': product_data.get('description', ''),
                'vendor': product_data.get('vendor', ''),
                'product_type': product_data.get('product_type', ''),
                'variants': [
                    {
                        'price': str(product_data['price']),
                        'sku': product_data.get('sku', ''),
                        'inventory_management': 'shopify',
                        'inventory_quantity': int(product_data.get('stock', 0))
                    }
                ]
            }
        }

        result = self._request('POST', '/products.json', json=payload)

        if result and 'product' in result:
            created_product = result['product']
            variant = created_product['variants'][0]

            return {
                'external_id': str(variant['id']),
                'sku': variant.get('sku', f"SHOPIFY-{variant['id']}"),
                'name': created_product['title'],
                'price': float(product_data['price']),  # Use the price we sent, not what Shopify returns
                'stock': int(variant.get('inventory_quantity', 0)),
                'status': 'active',
                'channel': 'shopify',
                'vendor': created_product.get('vendor', ''),
                'product_type': created_product.get('product_type', '')
            }

        return None

    def update_product(self, product_id: str, updates: Dict) -> bool:
        """Update product with multiple fields

        Args:
            product_id: Variant ID
            updates: Dict with 'price', 'stock', 'sku', etc.
        """
        success = True

        # Update price if specified
        if 'price' in updates:
            if not self.update_product_price(product_id, updates['price']):
                logger.error(f"Failed to update price for product {product_id}")
                success = False

        # Update stock if specified
        if 'stock' in updates:
            if not self.update_product_stock(product_id, updates['stock']):
                logger.error(f"Failed to update stock for product {product_id}")
                success = False

        # Update SKU or other variant fields if specified
        if 'sku' in updates:
            payload = {
                'variant': {
                    'id': int(product_id),
                    'sku': updates['sku']
                }
            }
            result = self._request('PUT', f'/variants/{product_id}.json', json=payload)
            if not result:
                logger.error(f"Failed to update SKU for product {product_id}")
                success = False

        return success
