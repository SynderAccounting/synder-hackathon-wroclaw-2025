from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

import pytest

from api.shopify import (
    SALES_ANALYTICS_QUERY,
    calculate_sales_metrics,
    get_sales_trend,
    get_top_products,
)
from api.shopify import (
    GET_CUSTOMERS_QUERY,
    GET_INVENTORY_LEVELS_QUERY,
    GET_ORDERS_QUERY,
    GET_PRODUCTS_QUERY,
    fetch_customers,
    fetch_inventory_levels,
    fetch_orders,
    fetch_products,
)
from api.shopify import parse_graphql_edges


class FakeClient:
    def __init__(self, payloads: Dict[str, Dict[str, Any]]) -> None:
        self._payloads = payloads

    async def execute_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self._payloads[query]
        except KeyError as exc:  # pragma: no cover - sanity fallback
            raise AssertionError(f"Unexpected query executed: {query}") from exc


@pytest.mark.asyncio
async def test_fetch_products_parses_edges() -> None:
    fake_payload = {
        "data": {
            "products": {
                "edges": [
                    {"node": {"id": "gid://shopify/Product/1", "title": "Example"}}
                ],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    }
    client = FakeClient({GET_PRODUCTS_QUERY: fake_payload})
    result = await fetch_products(client, limit=5)
    assert result["products"][0]["title"] == "Example"
    assert result["page_info"]["hasNextPage"] is False


@pytest.mark.asyncio
async def test_fetch_orders_combines_edges() -> None:
    fake_payload = {
        "data": {
            "orders": {
                "edges": [
                    {"node": {"id": "gid://shopify/Order/1", "name": "#1001"}}
                ],
                "pageInfo": {"hasNextPage": True, "endCursor": "abc"},
            }
        }
    }
    client = FakeClient({GET_ORDERS_QUERY: fake_payload})
    result = await fetch_orders(client)
    assert result["orders"][0]["name"] == "#1001"
    assert result["page_info"]["hasNextPage"] is True


@pytest.mark.asyncio
async def test_fetch_inventory_levels_computes_totals() -> None:
    fake_payload = {
        "data": {
            "inventoryItems": {
                "edges": [
                    {
                        "node": {
                            "id": "gid://shopify/InventoryItem/1",
                            "inventoryLevels": {
                                "edges": [
                                    {"node": {"id": "1", "available": 5}},
                                    {"node": {"id": "2", "available": 7}},
                                ]
                            },
                        }
                    }
                ],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    }
    client = FakeClient({GET_INVENTORY_LEVELS_QUERY: fake_payload})
    result = await fetch_inventory_levels(client)
    assert result["inventory_items"][0]["totalAvailable"] == 12


@pytest.mark.asyncio
async def test_fetch_customers_returns_nodes() -> None:
    fake_payload = {
        "data": {
            "customers": {
                "edges": [
                    {"node": {"id": "gid://shopify/Customer/1", "displayName": "Ada"}}
                ],
                "pageInfo": {"hasNextPage": False, "endCursor": None},
            }
        }
    }
    client = FakeClient({GET_CUSTOMERS_QUERY: fake_payload})
    result = await fetch_customers(client)
    assert result["customers"][0]["displayName"] == "Ada"


def test_parse_graphql_edges_handles_none() -> None:
    assert parse_graphql_edges(None) == []
    assert parse_graphql_edges([{ "node": 1 }]) == [1]


@pytest.mark.asyncio
async def test_calculate_sales_metrics_returns_decimals() -> None:
    fake_payload = {
        "data": {
            "orders": {
                "edges": [
                    {
                        "node": {
                            "id": "gid://shopify/Order/1",
                            "name": "#1001",
                            "createdAt": "2025-01-01T00:00:00Z",
                            "totalPriceSet": {"shopMoney": {"amount": "100.50", "currencyCode": "USD"}},
                            "lineItems": {"edges": []},
                        }
                    }
                ]
            }
        }
    }
    client = FakeClient({SALES_ANALYTICS_QUERY: fake_payload})
    metrics = await calculate_sales_metrics(client, days=7)
    assert metrics["total_revenue"] == Decimal("100.50")
    assert metrics["order_count"] == 1
    assert metrics["average_order_value"] == Decimal("100.50")


@pytest.mark.asyncio
async def test_get_top_products_sorts_by_revenue() -> None:
    fake_payload = {
        "data": {
            "orders": {
                "edges": [
                    {
                        "node": {
                            "id": "gid://shopify/Order/1",
                            "name": "#1001",
                            "createdAt": "2025-01-01T00:00:00Z",
                            "totalPriceSet": {"shopMoney": {"amount": "100.00", "currencyCode": "USD"}},
                            "lineItems": {
                                "edges": [
                                    {
                                        "node": {
                                            "id": "gid://shopify/LineItem/1",
                                            "name": "Widget",
                                            "quantity": 2,
                                            "variant": {
                                                "id": "gid://shopify/ProductVariant/1",
                                                "title": "Widget",
                                                "product": {"id": "gid://shopify/Product/1", "title": "Widget"},
                                            },
                                            "originalUnitPriceSet": {
                                                "shopMoney": {"amount": "25.00", "currencyCode": "USD"}
                                            },
                                        }
                                    }
                                ]
                            },
                        }
                    }
                ]
            }
        }
    }
    client = FakeClient({SALES_ANALYTICS_QUERY: fake_payload})
    products = await get_top_products(client, days=7, limit=5)
    assert products[0]["quantity_sold"] == 2
    assert products[0]["total_revenue"] == Decimal("50.00")


@pytest.mark.asyncio
async def test_get_sales_trend_groups_by_date() -> None:
    fake_payload = {
        "data": {
            "orders": {
                "edges": [
                    {
                        "node": {
                            "id": "gid://shopify/Order/1",
                            "name": "#1001",
                            "createdAt": "2025-01-01T10:00:00Z",
                            "totalPriceSet": {"shopMoney": {"amount": "100.00", "currencyCode": "USD"}},
                            "lineItems": {"edges": []},
                        }
                    },
                    {
                        "node": {
                            "id": "gid://shopify/Order/2",
                            "name": "#1002",
                            "createdAt": "2025-01-01T12:00:00Z",
                            "totalPriceSet": {"shopMoney": {"amount": "50.00", "currencyCode": "USD"}},
                            "lineItems": {"edges": []},
                        }
                    },
                ]
            }
        }
    }
    client = FakeClient({SALES_ANALYTICS_QUERY: fake_payload})
    trend = await get_sales_trend(client, days=7)
    assert trend == [{"date": "2025-01-01", "total_revenue": Decimal("150.00")}]
