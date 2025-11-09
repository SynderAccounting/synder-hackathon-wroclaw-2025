from typing import List

from fastapi import APIRouter, HTTPException

from configs.logger import LOGGER
from schemas.shopify import ShopifySchema
from services.shopify_service import get_shopify_data

shopify_router = APIRouter()


@shopify_router.get(
    "/all",
    summary="Get all products from Shopify.",
    description="Get all products from Shopify.",
    response_model=List[ShopifySchema]
)
async def get_all_products_from_shopify() -> List[ShopifySchema]:
    """
    Get all products from Shopify.

    Returns:
        List[ShopifySchema]: All products data from Shopify.
    """
    LOGGER.debug("Fetching all products from Shopify")
    try:
        return await get_shopify_data()
    except Exception as e:
        LOGGER.error(f"Error fetching products from Shopify: {e}")
        raise HTTPException(status_code=404, detail=f"Products not found: {e}")


@shopify_router.get(
    "/name/{product_name}",
    summary="Get products by name.",
    description="Get products by name.",
    response_model=List[ShopifySchema]
)
async def get_products_by_product_name(product_name: str) -> List[ShopifySchema]:
    """
    Get products by name.

    Args:
        product_name (str): Name of the product to search for.

    Returns:
        List[ShopifySchema]: Shopify products.
    """
    LOGGER.debug("Fetching products by name from Shopify")
    try:
        not_filtered_result = await get_shopify_data()
        return list(filter(lambda item: item.title.lower() == product_name.lower(), not_filtered_result))
    except Exception as e:
        LOGGER.error(f"Error fetching products from Shopify: {e}")
        raise HTTPException(status_code=404, detail=f"Products not found: {e}")
