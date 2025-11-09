"""Shopify-specific order model."""

from dataclasses import dataclass

from order_generator.models import OrderData


@dataclass
class ShopifyOrder(OrderData):
    """Order data from Shopify API."""

    pass
