"""Amazon-specific order model."""

from dataclasses import dataclass

from order_generator.models import OrderData


@dataclass
class AmazonOrder(OrderData):
    """Order data from Amazon API."""

    pass
