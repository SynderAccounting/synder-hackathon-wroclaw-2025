"""DummyJSON API integration service for fetching market data."""
import requests
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

DUMMYJSON_BASE_URL = "https://dummyjson.com"


def fetch_all_products(limit: int = 100) -> List[Dict]:
    """
    Fetch products from DummyJSON API.

    Args:
        limit: Maximum number of products to fetch.

    Returns:
        List of product dictionaries.
    """
    try:
        url = f"{DUMMYJSON_BASE_URL}/products"
        params = {'limit': limit}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get('products', [])

        logger.info(f"Fetched {len(products)} products from DummyJSON")
        return products

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch products from DummyJSON: {e}")
        return []


def search_products(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for products on DummyJSON by query.

    Args:
        query: Search query string.
        limit: Maximum number of results.

    Returns:
        List of matching product dictionaries.
    """
    try:
        url = f"{DUMMYJSON_BASE_URL}/products/search"
        params = {'q': query, 'limit': limit}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get('products', [])

        logger.info(f"Found {len(products)} products for query: '{query}'")
        return products

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to search DummyJSON for '{query}': {e}")
        return []


def get_product_by_id(product_id: int) -> Optional[Dict]:
    """
    Get a specific product by ID from DummyJSON.

    Args:
        product_id: Product ID.

    Returns:
        Product dictionary or None if not found.
    """
    try:
        url = f"{DUMMYJSON_BASE_URL}/products/{product_id}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        product = response.json()
        logger.info(f"Fetched product {product_id} from DummyJSON")
        return product

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch product {product_id} from DummyJSON: {e}")
        return None


def get_products_by_category(category: str, limit: int = 20) -> List[Dict]:
    """
    Get products by category from DummyJSON.

    Args:
        category: Category name.
        limit: Maximum number of products.

    Returns:
        List of product dictionaries.
    """
    try:
        url = f"{DUMMYJSON_BASE_URL}/products/category/{category}"
        params = {'limit': limit}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        products = data.get('products', [])

        logger.info(f"Fetched {len(products)} products from category '{category}'")
        return products

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch category '{category}' from DummyJSON: {e}")
        return []


def find_similar_products(product_name: str, product_price: float) -> List[Dict]:
    """
    Find similar products based on name and price range.

    This is a helper function that combines search and filtering
    to find products similar to a given product.

    Args:
        product_name: Name of the product to find similar items for.
        product_price: Price of the product (for range filtering).

    Returns:
        List of similar product dictionaries.
    """
    # Extract keywords from product name
    keywords = product_name.lower().split()[:3]  # Use first 3 words

    similar_products = []

    # Search for each keyword
    for keyword in keywords:
        if len(keyword) > 2:  # Skip very short words
            results = search_products(keyword, limit=5)
            similar_products.extend(results)

    # Remove duplicates based on ID
    seen_ids = set()
    unique_products = []
    for product in similar_products:
        if product.get('id') not in seen_ids:
            seen_ids.add(product.get('id'))
            unique_products.append(product)

    # If no products found, fetch general products
    if not unique_products:
        logger.warning(f"No keyword matches for '{product_name}', fetching general products")
        unique_products = fetch_all_products(limit=20)

    # Filter by price range (±50% for more flexibility)
    price_min = product_price * 0.5
    price_max = product_price * 2.0

    filtered_products = [
        p for p in unique_products
        if price_min <= p.get('price', 0) <= price_max
    ]

    # If no products in price range, return all unique ones
    if not filtered_products:
        filtered_products = unique_products[:10]

    logger.info(f"Found {len(filtered_products)} similar products for '{product_name}'")
    return filtered_products[:10]
