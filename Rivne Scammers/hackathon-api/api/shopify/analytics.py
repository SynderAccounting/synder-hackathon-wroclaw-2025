"""Analytics utilities built on top of Shopify Admin API data."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from .client import ShopifyGraphQLClient
from .utils import parse_graphql_edges

SALES_ANALYTICS_QUERY = """
query getSalesAnalytics($first: Int!, $query: String) {
  orders(first: $first, query: $query, sortKey: CREATED_AT, reverse: true) {
    edges {
      node {
        id
        name
        createdAt
        displayFinancialStatus
        displayFulfillmentStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        lineItems(first: 100) {
          edges {
            node {
              id
              name
              quantity
              sku
              variant {
                id
                title
                sku
                product {
                  id
                  title
                }
              }
              originalUnitPriceSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


def _format_created_at_filter(days: int) -> str:
    interval_start = datetime.now(timezone.utc) - timedelta(days=days)
    # Shopify expects RFC 3339 timestamps (ISO 8601 with Z)
    return interval_start.isoformat().replace("+00:00", "Z")


def _money_to_decimal(money: Dict[str, Any]) -> Decimal:
    amount = money.get("amount", "0") if money else "0"
    return Decimal(str(amount))


def _is_valid_order(order: Dict[str, Any]) -> bool:
    """
    Check if an order should be included in revenue calculations.
    Excludes refunded, voided, canceled orders, and gift card purchases to calculate pure revenue.
    """
    financial_status = (order.get("displayFinancialStatus") or "").upper()
    excluded_statuses = {"REFUNDED", "VOIDED", "CANCELED", "CANCELLED"}
    
    if financial_status in excluded_statuses:
        return False
    
    # Check if order contains only gift cards
    line_items = parse_graphql_edges(order.get("lineItems", {}).get("edges", []))
    if not line_items:
        return True
    
    # Exclude orders where all items are gift cards
    for item in line_items:
        item_name = (item.get("name") or "").lower()
        variant = item.get("variant") or {}
        product = variant.get("product") or {}
        product_title = (product.get("title") or "").lower()
        
        # If any item is NOT a gift card, include the order
        if "gift card" not in item_name and "gift card" not in product_title:
            return True
    
    # All items are gift cards, exclude this order
    return False


async def _fetch_sales_orders(client: ShopifyGraphQLClient, days: int, first: int = 250) -> List[Dict[str, Any]]:
    created_at_min = _format_created_at_filter(days)
    query_filter = f"created_at:>={created_at_min}"
    response = await client.execute_query(
        SALES_ANALYTICS_QUERY,
        {"first": min(first, 250), "query": query_filter},
    )
    orders = response["data"]["orders"]
    all_orders = parse_graphql_edges(orders.get("edges"))
    # Filter out refunded, voided, and canceled orders for pure revenue
    return [order for order in all_orders if _is_valid_order(order)]


async def calculate_sales_metrics(client: ShopifyGraphQLClient, days: int = 30) -> Dict[str, Any]:
    orders = await _fetch_sales_orders(client, days)
    if not orders:
        return {"total_revenue": Decimal("0"), "order_count": 0, "average_order_value": Decimal("0")}

    totals = [
        _money_to_decimal(order.get("totalPriceSet", {}).get("shopMoney")) for order in orders
    ]
    total_revenue = sum(totals, start=Decimal("0"))
    order_count = len(orders)
    average_order_value = total_revenue / order_count if order_count else Decimal("0")
    return {
        "total_revenue": total_revenue,
        "order_count": order_count,
        "average_order_value": average_order_value,
    }


async def get_top_products(
    client: ShopifyGraphQLClient,
    *,
    days: int = 30,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    orders = await _fetch_sales_orders(client, days)
    product_totals: Dict[str, Dict[str, Any]] = {}

    for order in orders:
        line_items = parse_graphql_edges(order.get("lineItems", {}).get("edges"))
        for item in line_items:
            quantity = item.get("quantity") or 0
            price = _money_to_decimal(
                item.get("originalUnitPriceSet", {}).get("shopMoney")
            )
            revenue = price * quantity
            variant = item.get("variant") or {}
            product = (variant.get("product") or {})
            product_id = product.get("id") or variant.get("id") or item.get("id")
            entry = product_totals.setdefault(
                product_id,
                {
                    "product_id": product_id,
                    "title": product.get("title") or variant.get("title") or item.get("name"),
                    "total_revenue": Decimal("0"),
                    "quantity_sold": 0,
                },
            )
            entry["total_revenue"] += revenue
            entry["quantity_sold"] += quantity

    sorted_products = sorted(
        product_totals.values(),
        key=lambda product: (product["total_revenue"], product["quantity_sold"]),
        reverse=True,
    )
    return sorted_products[: limit or 10]


async def get_sales_trend(client: ShopifyGraphQLClient, *, days: int = 30) -> List[Dict[str, Any]]:
    orders = await _fetch_sales_orders(client, days)
    daily_totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for order in orders:
        created_at = order.get("createdAt")
        if not created_at:
            continue
        day_key = created_at[:10]  # YYYY-MM-DD
        daily_totals[day_key] += _money_to_decimal(order.get("totalPriceSet", {}).get("shopMoney"))

    return [
        {"date": day, "total_revenue": total}
        for day, total in sorted(daily_totals.items())
    ]
