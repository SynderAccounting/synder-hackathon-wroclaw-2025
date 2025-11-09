"""GraphQL queries and helper functions for Shopify resources."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .client import ShopifyGraphQLClient
from .utils import parse_graphql_edges

GET_PRODUCTS_QUERY = """
query getProducts($first: Int!, $after: String, $query: String) {
  products(first: $first, after: $after, query: $query) {
    edges {
      node {
        id
        title
        description
        vendor
        productType
        status
        totalInventory
        createdAt
        updatedAt
        variants(first: 100) {
          edges {
            node {
              id
              title
              sku
              price
              inventoryQuantity
              barcode
            }
          }
        }
        images(first: 5) {
          edges {
            node {
              id
              url
              altText
            }
          }
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

GET_ORDERS_QUERY = """
query getOrders($first: Int!, $after: String, $query: String) {
  orders(first: $first, after: $after, sortKey: CREATED_AT, reverse: true, query: $query) {
    edges {
      node {
        id
        name
        createdAt
        updatedAt
        displayFulfillmentStatus
        displayFinancialStatus
        totalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        subtotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }
        customer {
          id
          displayName
          email
        }
        email
        phone
        shippingAddress {
          address1
          address2
          city
          provinceCode
          zip
          country
        }
        lineItems(first: 50) {
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
                price
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
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

GET_INVENTORY_LEVELS_QUERY = """
query getInventoryLevels($first: Int!, $after: String) {
  inventoryItems(first: $first, after: $after) {
    edges {
      node {
        id
        sku
        tracked
        requiresShipping
        inventoryLevels(first: 10) {
          edges {
            node {
              id
              available
              incoming
              location {
                id
                name
              }
            }
          }
        }
        variant {
          id
          title
          product {
            id
            title
          }
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

GET_LOCATIONS_QUERY = """
query getLocations {
  locations(first: 10) {
    edges {
      node {
        id
        name
        isActive
        address {
          city
          country
        }
      }
    }
  }
}
"""

GET_CUSTOMERS_QUERY = """
query getCustomers($first: Int!, $after: String, $query: String) {
  customers(first: $first, after: $after, query: $query) {
    edges {
      node {
        id
        displayName
        email
        phone
        createdAt
        updatedAt
        state
        verifiedEmail
        defaultAddress {
          id
          address1
          address2
          city
          province
          zip
          country
        }
        numberOfOrders
        lifetimeDuration
        amountSpent {
          amount
          currencyCode
        }
        tags
        note
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


GET_CUSTOMERS_COUNT_QUERY = """
query getCustomersCount($query: String) {
  customersCount(query: $query)
}
"""


def _clean_variables(variables: Dict[str, Optional[Any]]) -> Dict[str, Any]:
    return {key: value for key, value in variables.items() if value is not None}


async def fetch_products(
    client: ShopifyGraphQLClient,
    *,
    cursor: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    variables = _clean_variables({"first": min(limit, 250), "after": cursor, "query": query})
    response = await client.execute_query(GET_PRODUCTS_QUERY, variables)
    products_data = response["data"]["products"]
    products = parse_graphql_edges(products_data.get("edges"))
    return {"products": products, "page_info": products_data.get("pageInfo", {})}


async def fetch_orders(
    client: ShopifyGraphQLClient,
    *,
    cursor: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    variables = _clean_variables({"first": min(limit, 250), "after": cursor, "query": query})
    response = await client.execute_query(GET_ORDERS_QUERY, variables)
    orders_data = response["data"]["orders"]
    orders = parse_graphql_edges(orders_data.get("edges"))
    return {"orders": orders, "page_info": orders_data.get("pageInfo", {})}


async def fetch_inventory_levels(
    client: ShopifyGraphQLClient,
    *,
    cursor: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    variables = _clean_variables({"first": min(limit, 250), "after": cursor})
    response = await client.execute_query(GET_INVENTORY_LEVELS_QUERY, variables)
    inventory_data = response["data"]["inventoryItems"]
    inventory_items = []

    for item in parse_graphql_edges(inventory_data.get("edges")):
        levels = parse_graphql_edges(item.get("inventoryLevels", {}).get("edges"))
        total_available = sum((level.get("available") or 0) for level in levels)
        inventory_items.append({**item, "inventoryLevels": levels, "totalAvailable": total_available})

    return {"inventory_items": inventory_items, "page_info": inventory_data.get("pageInfo", {})}


async def fetch_locations(client: ShopifyGraphQLClient) -> Dict[str, Any]:
    response = await client.execute_query(GET_LOCATIONS_QUERY, {})
    location_edges = response["data"]["locations"]["edges"]
    return {"locations": parse_graphql_edges(location_edges)}


async def fetch_customers(
    client: ShopifyGraphQLClient,
    *,
    cursor: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    variables = _clean_variables({"first": min(limit, 250), "after": cursor, "query": query})
    response = await client.execute_query(GET_CUSTOMERS_QUERY, variables)
    customers_data = response["data"]["customers"]
    customers = parse_graphql_edges(customers_data.get("edges"))
    return {"customers": customers, "page_info": customers_data.get("pageInfo", {})}


async def fetch_customers_count(
  client: ShopifyGraphQLClient,
  *,
  query: Optional[str] = None,
) -> int:
  variables = _clean_variables({"query": query})
  response = await client.execute_query(GET_CUSTOMERS_COUNT_QUERY, variables)
  return int(response["data"].get("customersCount", 0) or 0)
