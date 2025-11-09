"""Order Generator - A library for generating simulated order data."""

from .config import Config
from .constants import COUNTRY_CODES, DISCOUNTS, ITEM_VARIANTS, ITEMS
from .enums import OrderFinancialStatus, TrackingCompany
from .generator import OrderGenerator
from .models import (
    Address,
    Customer,
    Discount,
    Item,
    OrderData,
    OrderFulfillment,
    OrderItem,
)

__all__ = [
    # Main classes
    "OrderGenerator",
    "Config",
    # Models
    "OrderData",
    "OrderItem",
    "Item",
    "Address",
    "Discount",
    "OrderFulfillment",
    "Customer",
    # Enums
    "OrderFinancialStatus",
    "TrackingCompany",
    # Constants
    "ITEMS",
    "ITEM_VARIANTS",
    "DISCOUNTS",
    "COUNTRY_CODES",
]
