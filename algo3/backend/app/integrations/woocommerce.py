import requests
import logging
from typing import List, Dict, Optional
from .base import StoreIntegration

logger = logging.getLogger(__name__)

class WooCommerceIntegration(StoreIntegration):
    """WooCommerce REST API integration"""

    def __init__(self, store_url: str, consumer_key: str, consumer_secret: str):
        super().__init__(store_url, consumer_key, consumer_secret)
        self.api_base = f"{self.store_url}/wp-json/wc/v3"

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make authenticated request to WooCommerce API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        auth = (self.api_key, self.api_secret)

        try:
            response = requests.request(method, url, auth=auth, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"WooCommerce API request failed: {e}")
            return None

    def test_connection(self) -> bool:
        """Test if API credentials are valid"""
        try:
            result = self._request('GET', '/products', params={'per_page': 1})
            return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_products(self, limit: int = 100) -> List[Dict]:
        """Fetch products from WooCommerce store"""
        products = []
        page = 1
        per_page = min(limit, 100)

        while len(products) < limit:
            result = self._request('GET', '/products', params={
                'per_page': per_page,
                'page': page,
                'status': 'publish'
            })

            if not result:
                break

            for product in result:
                products.append({
                    'external_id': str(product['id']),
                    'sku': product.get('sku', f"WC-{product['id']}"),
                    'name': product['name'],
                    'price': float(product.get('price', 0) or 0),
                    'status': 'active' if product['stock_status'] == 'instock' else 'low_stock',
                    'channel': 'woocommerce'
                })

            if len(result) < per_page:
                break

            page += 1

        return products[:limit]

    def create_coupon(self, coupon_data: Dict) -> Dict:
        """Create a discount coupon in WooCommerce

        Args:
            coupon_data: {
                'code': str,
                'discount_type': 'percent' | 'fixed_cart' | 'fixed_product',
                'amount': float,
                'description': str
            }
        """
        payload = {
            'code': coupon_data['code'],
            'discount_type': coupon_data.get('discount_type', 'percent'),
            'amount': str(coupon_data['amount']),
            'description': coupon_data.get('description', ''),
            'individual_use': False,
            'usage_limit': coupon_data.get('usage_limit'),
        }

        result = self._request('POST', '/coupons', json=payload)

        if result:
            return {
                'success': True,
                'coupon_id': result['id'],
                'code': result['code'],
                'amount': result['amount']
            }
        else:
            return {'success': False, 'error': 'Failed to create coupon'}

    def update_product_price(self, product_id: str, new_price: float) -> bool:
        """Update product price in WooCommerce"""
        payload = {
            'regular_price': str(new_price)
        }

        result = self._request('PUT', f'/products/{product_id}', json=payload)
        return result is not None
