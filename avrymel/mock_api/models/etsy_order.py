"""Etsy-specific order model."""

from dataclasses import dataclass

from order_generator.models import OrderData


@dataclass
class EtsyOrder(OrderData):
    """Order data from Etsy API."""

    pass
