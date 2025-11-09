import datetime
import json
from dataclasses import dataclass
from typing import Optional

from .enums import OrderFinancialStatus, TrackingCompany


@dataclass
class Item:
    item_id: str
    item_name: str
    item_price: float


@dataclass
class Address:
    first_name: str
    last_name: str
    company: str
    address: str
    city: str
    state_or_region: str
    country: str
    postal_code: str
    country_code: str

    def to_dict(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company": self.company,
            "street_name": self.address,
            "city": self.city,
            "province": self.state_or_region,
            "country": self.country,
            "zip": self.postal_code,
            "country_code": self.country_code,
        }


@dataclass
class OrderItem:
    item: Item
    variant_name: str
    quantity: int


@dataclass
class Discount:
    discount_percent: float
    discount_code: str


@dataclass
class OrderFulfillment:
    tracking_company: TrackingCompany
    created_at: datetime.datetime
    tracking_number: str

    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at.isoformat() + "Z",
            "tracking_company": self.tracking_company.value,
            "tracking_number": self.tracking_number,
        }


@dataclass
class Customer:
    email: str
    first_name: str
    last_name: str

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }


@dataclass
class OrderData:
    """Base class containing common order data across all services."""

    order_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    currency: str
    financial_status: OrderFinancialStatus
    subtotal: float
    discount: Optional[Discount]
    total_tax: float
    final_price: float
    billing_address: Address
    shipping_address: Address
    items: list[OrderItem]
    fulfillment: OrderFulfillment
    customer: Customer

    def to_json(self) -> str:
        """Convert OrderData to JSON string representation.

        Returns:
            JSON string representation of the order.
        """
        discount_amount = 0.0
        discount_codes = []

        if self.discount:
            discount_amount = round(
                (self.subtotal * self.discount.discount_percent) / 100, 2
            )
            discount_codes = [self.discount.discount_code]

        order_dict = {
            "order": {
                "order_id": self.order_id,
                "created_at": self.created_at.isoformat() + "Z",
                "updated_at": self.updated_at.isoformat() + "Z",
                "currency": self.currency,
                "financial_status": self.financial_status.value,
                "subtotal": round(self.subtotal, 2),
                "discount": discount_amount if discount_amount > 0 else None,
                "discount_codes": discount_codes if discount_codes else None,
                "total_tax": round(self.total_tax, 2),
                "total_price": round(self.final_price, 2),
                "billing_address": self.billing_address.to_dict(),
                "shipping_address": self.shipping_address.to_dict(),
                "items": [
                    {
                        "item_id": item.item.item_id,
                        "item_name": item.item.item_name,
                        "variant_name": item.variant_name,
                        "quantity": item.quantity,
                        "item_price": round(item.item.item_price, 2),
                        "item_total_discount": round(
                            (
                                item.item.item_price
                                * item.quantity
                                * self.discount.discount_percent
                                / 100
                            )
                            if self.discount
                            else 0,
                            2,
                        ),
                    }
                    for item in self.items
                ],
                "fulfillments": [self.fulfillment.to_dict()],
                "customer": self.customer.to_dict(),
            }
        }

        return json.dumps(order_dict, indent=2)
