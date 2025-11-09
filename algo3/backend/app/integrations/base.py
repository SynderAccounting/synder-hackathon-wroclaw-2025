from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class StoreIntegration(ABC):
    """Base class for store integrations"""

    def __init__(self, store_url: str, api_key: str, api_secret: Optional[str] = None):
        self.store_url = store_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if API credentials are valid"""
        pass

    @abstractmethod
    def get_products(self, limit: int = 100) -> List[Dict]:
        """Fetch products from the store"""
        pass

    @abstractmethod
    def create_coupon(self, coupon_data: Dict) -> Dict:
        """Create a discount coupon/code"""
        pass

    @abstractmethod
    def update_product_price(self, product_id: str, new_price: float) -> bool:
        """Update product price"""
        pass
