"""Unified Order model with service identifier."""

import json
from dataclasses import dataclass

from order_generator.models import OrderData


@dataclass
class Order(OrderData):
    """Standardized order object with service identifier."""

    service: str  # "Amazon", "Etsy", or "Shopify"

    def to_json(self) -> str:
        """Convert Order to JSON string representation.

        Returns:
            JSON string representation of the order with service field.
        """
        # Get base order JSON and parse it
        base_json = super().to_json()
        order_dict = json.loads(base_json)

        # Add service field
        order_dict["order"]["service"] = self.service

        return json.dumps(order_dict, indent=2)
