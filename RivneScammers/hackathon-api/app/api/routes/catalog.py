"""Catalog API routes backed by the local database."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from api.routes.shopify import get_client
from api.shopify.client import ShopifyGraphQLClient
from api.shopify.queries import fetch_customers_count
from app.services.shopify_sync_service import shopify_sync_service
from db.database import get_db
from models.catalog import InventorySnapshot, Order, OrderItem, Product

router = APIRouter(prefix="/api/v1", tags=["catalog"])


def _isoformat(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _serialize_product(product: Product) -> Dict[str, Any]:
    amount = float(product.selling_price) if product.selling_price is not None else None
    return {
        "id": product.shopify_product_id or str(product.id),
        "gid": product.shopify_product_id,
        "sku": product.sku,
        "title": product.title,
        "name": product.title,
        "category": product.category,
        "productType": product.category,
        "totalInventory": product.current_stock,
        "current_stock": product.current_stock,
        "selling_price": amount,
        "variants": [
            {
                "id": product.shopify_product_id,
                "sku": product.sku,
                "price": amount,
                "inventoryQuantity": product.current_stock,
            }
        ],
        "updatedAt": _isoformat(product.updated_at),
        "createdAt": _isoformat(product.created_at),
    }


def _serialize_order_item(order: Order, item: OrderItem) -> Dict[str, Any]:
    unit_price = item.unit_price if item.unit_price is None else float(item.unit_price)
    product_title = item.product.title if item.product else item.sku
    return {
        "id": str(item.id),
        "name": product_title,
        "quantity": item.quantity,
        "sku": item.sku,
        "variant": {
            "id": item.variant_id,
            "title": product_title,
            "sku": item.sku,
            "price": unit_price,
        },
        "originalUnitPriceSet": {
            "shopMoney": {
                "amount": unit_price,
                "currencyCode": order.currency or "USD",
            }
        },
    }


def _serialize_order(order: Order) -> Dict[str, Any]:
    total_price = float(order.total_price) if order.total_price is not None else 0.0
    return {
        "id": order.shopify_order_id or str(order.id),
        "name": order.order_number,
        "orderNumber": order.order_number,
        "createdAt": _isoformat(order.created_at),
        "updatedAt": _isoformat(order.updated_at),
        "displayFulfillmentStatus": order.fulfillment_status,
        "displayFinancialStatus": order.financial_status,
        "totalPriceSet": {
            "shopMoney": {
                "amount": total_price,
                "currencyCode": order.currency or "USD",
            }
        },
        "subtotalPriceSet": {
            "shopMoney": {
                "amount": total_price,
                "currencyCode": order.currency or "USD",
            }
        },
        "customer": {
            "displayName": None,
            "email": None,
        },
        "lineItems": {
            "edges": [
                {"node": _serialize_order_item(order, item)} for item in order.line_items
            ],
        },
    }


def _serialize_inventory(snapshot: InventorySnapshot) -> Dict[str, Any]:
    return {
        "sku": snapshot.sku,
        "available_quantity": snapshot.available_quantity,
        "location": snapshot.location,
        "snapshot_date": _isoformat(snapshot.snapshot_date),
    }


@router.get("/products")
def list_products(
    *,
    search: Optional[str] = Query(default=None, description="Optional search across SKU, name, or category"),
    limit: int = Query(default=200, le=500),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    filters = []
    if search:
        pattern = f"%{search.lower()}%"
        filters.append(
            or_(
                func.lower(Product.sku).like(pattern),
                func.lower(Product.title).like(pattern),
                func.lower(Product.category).like(pattern),
            )
        )

    query = select(Product).order_by(Product.updated_at.desc())
    count_stmt = select(func.count()).select_from(Product)
    if filters:
        condition = filters[0]
        query = query.where(condition)
        count_stmt = count_stmt.where(condition)

    products = db.execute(query.limit(limit)).scalars().all()
    total = db.execute(count_stmt).scalar() or 0
    last_update = db.execute(select(func.max(Product.updated_at))).scalar()

    return {
        "items": [_serialize_product(product) for product in products],
        "total": total,
        "synced_at": _isoformat(last_update),
        "page_info": {"hasNextPage": False, "endCursor": None},
    }


@router.get("/products/{product_identifier}")
def get_product(
    product_identifier: str,
    *,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    predicates: List[Any] = [
        Product.sku == product_identifier,
        Product.shopify_product_id == product_identifier,
    ]
    if product_identifier.isdigit():
        predicates.append(Product.id == int(product_identifier))

    stmt = select(Product).where(or_(*predicates))
    product = db.execute(stmt).scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _serialize_product(product)


@router.post("/products/sync")
async def sync_products(
    client: ShopifyGraphQLClient = Depends(get_client),
) -> Dict[str, Any]:
    result = await shopify_sync_service.sync_products(client)
    result["synced_at"] = _isoformat(result.get("synced_at"))
    return result


@router.get("/orders")
def list_orders(
    *,
    limit: int = Query(default=100, le=250),
    include_canceled: bool = Query(default=False, description="Include canceled/voided orders"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    # Build query to filter orders
    query = select(Order).order_by(Order.created_at.desc())
    count_query = select(func.count()).select_from(Order)

    # Filter out canceled orders unless explicitly requested
    if not include_canceled:
        valid_statuses = ['paid', 'pending', 'partially_paid', 'authorized', 'partially_refunded']
        normalized_status = func.lower(Order.financial_status)
        status_filter = or_(
            normalized_status.in_(valid_statuses),
            Order.financial_status.is_(None)
        )
        query = query.where(status_filter)
        count_query = count_query.where(status_filter)

    orders = db.execute(query.limit(limit)).scalars().all()
    total = db.execute(count_query).scalar() or 0
    last_update = db.execute(select(func.max(Order.updated_at))).scalar()

    return {
        "items": [_serialize_order(order) for order in orders],
        "total": total,
        "synced_at": _isoformat(last_update),
        "page_info": {"hasNextPage": False, "endCursor": None},
    }


@router.get("/orders/recent")
async def get_recent_orders(
    *,
    limit: int = Query(default=10, le=50),
    days: int = Query(default=30, le=365),
    client: ShopifyGraphQLClient = Depends(get_client),
) -> Dict[str, Any]:
    """
    Get recent orders from Shopify API, excluding canceled/voided orders.
    Returns orders with customer information and financial/fulfillment status.
    """
    from api.shopify.analytics import _fetch_sales_orders

    try:
        # Fetch orders from Shopify (already filters out canceled orders)
        orders = await _fetch_sales_orders(client, days=days, first=limit)

        # Format orders for frontend
        formatted_orders = []
        for order in orders[:limit]:
            customer = order.get("customer", {})
            total_price = order.get("totalPriceSet", {}).get("shopMoney", {})

            formatted_orders.append({
                "id": order.get("id"),
                "orderNumber": order.get("name"),
                "createdAt": order.get("createdAt"),
                "customerName": customer.get("displayName") if customer else None,
                "customerEmail": customer.get("email") if customer else None,
                "total": float(total_price.get("amount", 0)) if total_price else 0,
                "currency": total_price.get("currencyCode", "USD") if total_price else "USD",
                "fulfillmentStatus": order.get("displayFulfillmentStatus"),
                "financialStatus": order.get("displayFinancialStatus"),
                "status": order.get("displayFinancialStatus"),
            })

        return {
            "orders": formatted_orders,
            "total": len(formatted_orders),
            "syncedAt": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent orders: {str(e)}")


@router.get("/orders/{order_identifier}")
def get_order(
    order_identifier: str,
    *,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    predicates: List[Any] = [
        Order.shopify_order_id == order_identifier,
        Order.order_number == order_identifier,
    ]
    if order_identifier.isdigit():
        predicates.append(Order.id == int(order_identifier))

    stmt = select(Order).where(or_(*predicates))
    order = db.execute(stmt).scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)


@router.post("/orders/sync")
async def sync_orders(
    client: ShopifyGraphQLClient = Depends(get_client),
) -> Dict[str, Any]:
    result = await shopify_sync_service.sync_orders(client)
    result["synced_at"] = _isoformat(result.get("synced_at"))
    return result


@router.get("/inventory")
def list_inventory(
    *,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    snapshots = db.execute(select(InventorySnapshot)).scalars().all()
    last_snapshot = (
        db.execute(select(func.max(InventorySnapshot.snapshot_date))).scalar()
    )
    return {
        "items": [_serialize_inventory(snapshot) for snapshot in snapshots],
        "synced_at": _isoformat(last_snapshot),
    }


@router.post("/inventory/sync")
async def sync_inventory(
    client: ShopifyGraphQLClient = Depends(get_client),
) -> Dict[str, Any]:
    result = await shopify_sync_service.sync_inventory(client)
    result["synced_at"] = _isoformat(result.get("synced_at"))
    return result


@router.post("/catalog/sync")
async def sync_catalog(
    client: ShopifyGraphQLClient = Depends(get_client),
) -> Dict[str, Any]:
    result = await shopify_sync_service.sync_all(client)
    result["synced_at"] = _isoformat(result.get("synced_at"))
    return result


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    *,
    days: int = Query(default=36500, description="Number of days to look back for orders (default: ~100 years for all-time)"),
    db: Session = Depends(get_db),
    client: ShopifyGraphQLClient = Depends(get_client),
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard statistics including:
    - Total revenue (excluding canceled orders) - from Shopify API
    - Order count (excluding canceled orders) - from Shopify API
    - Product count - from local database
    - Customer count - from Shopify API

    Optimized: All API calls run in parallel for faster response
    """
    import asyncio
    from api.shopify.analytics import calculate_sales_metrics

    # Run all operations in parallel for better performance
    async def get_sales_metrics():
        try:
            metrics = await calculate_sales_metrics(client, days=days)
            return float(metrics.get("total_revenue", 0)), metrics.get("order_count", 0)
        except Exception as e:
            print(f"Failed to fetch sales metrics from Shopify API: {e}")
            # Fallback to database
            valid_order_statuses = ['paid', 'pending', 'partially_paid', 'authorized', 'partially_refunded']
            orders_query = select(func.count()).select_from(Order).where(
                or_(
                    Order.financial_status.in_(valid_order_statuses),
                    Order.financial_status.is_(None)
                )
            )
            orders_count = db.execute(orders_query).scalar() or 0

            revenue_query = select(func.sum(Order.total_price)).where(
                or_(
                    Order.financial_status.in_(valid_order_statuses),
                    Order.financial_status.is_(None)
                )
            )
            total_revenue = float(db.execute(revenue_query).scalar() or 0)
            return total_revenue, orders_count

    async def get_customers():
        try:
            return await fetch_customers_count(client)
        except Exception as e:
            print(f"Failed to fetch customers from Shopify API: {e}")
            return 0

    def get_products():
        # Synchronous DB call
        return db.execute(select(func.count()).select_from(Product)).scalar() or 0

    # Execute all operations in parallel
    (total_revenue, orders_count), customers_count = await asyncio.gather(
        get_sales_metrics(),
        get_customers()
    )

    # Products count from DB (synchronous but fast)
    products_count = get_products()

    return {
        "revenue": total_revenue,
        "orders": orders_count,
        "products": products_count,
        "customers": customers_count,
    }
