"""Parser for converting Shopify API responses to standardized Order format."""

import datetime
from typing import Dict, Any

from order_generator import OrderFinancialStatus, TrackingCompany
from order_generator.models import (
    Address,
    Customer,
    Discount,
    Item,
    OrderFulfillment,
    OrderItem,
)
from models import ShopifyOrder, Order


def parse_shopify_order(order_json: Dict[str, Any]) -> Order:
    """Parse Shopify API JSON response to standardized Order object.

    Args:
        order_json: JSON dict from Shopify API response

    Returns:
        Standardized Order object with service identifier set to "Shopify"
    """
    order_data = order_json["order"]

    # Parse addresses
    billing_address = Address(
        first_name=order_data["billing_address"]["first_name"],
        last_name=order_data["billing_address"]["last_name"],
        company=order_data["billing_address"]["company"],
        address=order_data["billing_address"]["street_name"],
        city=order_data["billing_address"]["city"],
        state_or_region=order_data["billing_address"]["province"],
        country=order_data["billing_address"]["country"],
        postal_code=order_data["billing_address"]["zip"],
        country_code=order_data["billing_address"]["country_code"],
    )

    shipping_address = Address(
        first_name=order_data["shipping_address"]["first_name"],
        last_name=order_data["shipping_address"]["last_name"],
        company=order_data["shipping_address"]["company"],
        address=order_data["shipping_address"]["street_name"],
        city=order_data["shipping_address"]["city"],
        state_or_region=order_data["shipping_address"]["province"],
        country=order_data["shipping_address"]["country"],
        postal_code=order_data["shipping_address"]["zip"],
        country_code=order_data["shipping_address"]["country_code"],
    )

    # Parse customer
    customer = Customer(
        email=order_data["customer"]["email"],
        first_name=order_data["customer"]["first_name"],
        last_name=order_data["customer"]["last_name"],
    )

    # Parse items
    items = []
    for item_data in order_data["items"]:
        item = Item(
            item_id=item_data["item_id"],
            item_name=item_data["item_name"],
            item_price=item_data["item_price"],
        )
        order_item = OrderItem(
            item=item,
            variant_name=item_data["variant_name"],
            quantity=item_data["quantity"],
        )
        items.append(order_item)

    # Parse discount
    discount = None
    if order_data.get("discount") and order_data.get("discount_codes"):
        # Calculate discount percent from amount
        discount_amount = order_data["discount"]
        subtotal = order_data["subtotal"]
        discount_percent = (discount_amount / subtotal) * 100 if subtotal > 0 else 0
        discount = Discount(
            discount_percent=discount_percent,
            discount_code=order_data["discount_codes"][0],
        )

    # Parse fulfillment
    fulfillment_data = order_data["fulfillments"][0]
    fulfillment = OrderFulfillment(
        tracking_company=TrackingCompany(fulfillment_data["tracking_company"]),
        created_at=datetime.datetime.fromisoformat(
            fulfillment_data["created_at"].replace("Z", "+00:00")
        ),
        tracking_number=fulfillment_data["tracking_number"],
    )

    # Create ShopifyOrder
    shopify_order = ShopifyOrder(
        order_id=order_data["order_id"],
        created_at=datetime.datetime.fromisoformat(
            order_data["created_at"].replace("Z", "+00:00")
        ),
        updated_at=datetime.datetime.fromisoformat(
            order_data["updated_at"].replace("Z", "+00:00")
        ),
        currency=order_data["currency"],
        financial_status=OrderFinancialStatus(order_data["financial_status"]),
        subtotal=order_data["subtotal"],
        discount=discount,
        total_tax=order_data["total_tax"],
        final_price=order_data["total_price"],
        billing_address=billing_address,
        shipping_address=shipping_address,
        items=items,
        fulfillment=fulfillment,
        customer=customer,
    )

    # Convert to unified Order
    return Order(
        order_id=shopify_order.order_id,
        created_at=shopify_order.created_at,
        updated_at=shopify_order.updated_at,
        currency=shopify_order.currency,
        financial_status=shopify_order.financial_status,
        subtotal=shopify_order.subtotal,
        discount=shopify_order.discount,
        total_tax=shopify_order.total_tax,
        final_price=shopify_order.final_price,
        billing_address=shopify_order.billing_address,
        shipping_address=shopify_order.shipping_address,
        items=shopify_order.items,
        fulfillment=shopify_order.fulfillment,
        customer=shopify_order.customer,
        service="Shopify",
    )
