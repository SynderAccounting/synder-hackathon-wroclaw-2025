"""FastAPI routes for Shopify Admin API integration."""
from __future__ import annotations

from typing import Optional
import logging
import csv
import io
import json
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator

from api.shopify.analytics import calculate_sales_metrics, get_top_products, get_sales_trend
from api.shopify.client import ShopifyGraphQLClient, ShopifyAuthenticationError, ShopifyRateLimitError, ShopifyAPIError
from api.shopify.queries import fetch_products, fetch_orders, fetch_inventory_levels, fetch_locations, fetch_customers
from api.shopify.utils import fetch_all_pages
from app.services.shopify_settings_service import (
    ShopifySettings,
    ShopifySettingsNotConfigured,
    shopify_settings_service,
)

load_dotenv()

router = APIRouter(prefix="/api/v1/shopify", tags=["shopify"])


class ShopifySettingsPayload(BaseModel):
    """Incoming payload for saving or testing Shopify credentials."""

    shop_url: str = Field(..., description="Shopify shop domain")
    access_token: Optional[str] = Field(
        default=None,
        description="Admin API access token. Leave empty to reuse stored token.",
    )
    api_version: str = Field(default="2025-01", description="Shopify Admin API version")

    @validator("shop_url")
    def _normalize_shop_url(cls, value: str) -> str:  # pylint: disable=E0213
        cleaned = value.strip()
        if cleaned.startswith("https://"):
            cleaned = cleaned[len("https://") :]
        if cleaned.startswith("http://"):
            cleaned = cleaned[len("http://") :]
        return cleaned.rstrip("/")


async def get_client() -> ShopifyGraphQLClient:
    try:
        settings = shopify_settings_service.get_settings()
    except ShopifySettingsNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ShopifyGraphQLClient(
        shop_url=settings.shop_url,
        access_token=settings.access_token,
        api_version=settings.api_version,
    )


def _handle_query_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ShopifyAuthenticationError):
        return HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, ShopifyRateLimitError):
        return HTTPException(status_code=429, detail=str(exc))
    if isinstance(exc, ShopifyAPIError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail="Unexpected Shopify integration error")


@router.get("/config")
async def get_shopify_config() -> dict[str, object]:
    """Expose whether Shopify credentials have been configured."""

    if not shopify_settings_service.has_settings():
        return {"configured": False}

    settings = shopify_settings_service.get_settings()

    # Mask the access token for security (show only last 4 characters)
    masked_token = None
    if settings.access_token:
        token = settings.access_token
        if len(token) > 4:
            masked_token = f"{'*' * (len(token) - 4)}{token[-4:]}"
        else:
            masked_token = "****"

    return {
        "configured": True,
        "shop_url": settings.shop_url,
        "api_version": settings.api_version,
        "access_token_masked": masked_token,  # Add masked token
        "access_token": settings.access_token,
        "has_access_token": bool(settings.access_token),
    }


@router.post("/config")
async def save_shopify_config(payload: ShopifySettingsPayload) -> dict[str, object]:
    """Persist Shopify credentials for subsequent API calls."""

    token_to_use: Optional[str] = payload.access_token
    existing_settings: Optional[ShopifySettings] = None

    if shopify_settings_service.has_settings():
        existing_settings = shopify_settings_service.get_settings()
        if token_to_use is None:
            token_to_use = existing_settings.access_token

    if not token_to_use:
        raise HTTPException(status_code=400, detail="Access token is required")

    settings_model = ShopifySettings(
        shop_url=payload.shop_url,
        access_token=token_to_use,
        api_version=payload.api_version,
    )

    shopify_settings_service.save_settings(settings_model)
    shopify_settings_service.reset_cache()
    return {"message": "Shopify settings saved", "has_access_token": True}



@router.post("/test-credentials")
async def test_shopify_credentials(payload: ShopifySettingsPayload) -> dict[str, object]:
    """Validate provided Shopify credentials by querying the shop object."""

    token_to_use = payload.access_token
    if token_to_use is None and shopify_settings_service.has_settings():
        try:
            token_to_use = shopify_settings_service.get_settings().access_token
        except ShopifySettingsNotConfigured:  # pragma: no cover - race condition guard
            token_to_use = None

    if not token_to_use:
        raise HTTPException(status_code=400, detail="Access token is required to test credentials")

    client = ShopifyGraphQLClient(
        shop_url=payload.shop_url,
        access_token=token_to_use,
        api_version=payload.api_version,
    )

    try:
        response = await client.execute_query(
            """
            query getShopInfo {
              shop {
                name
                primaryDomain { url }
              }
            }
            """
        )
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc

    shop_data = (response or {}).get("data", {}).get("shop", {})
    return {
        "success": True,
        "shop_name": shop_data.get("name"),
        "primary_domain": (shop_data.get("primaryDomain") or {}).get("url"),
    }


@router.get("/products")
async def get_products(
    cursor: Optional[str] = Query(default=None),
    query: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=250),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    try:
        result = await fetch_products(client, cursor=cursor, query=query, limit=limit)
        store_slug = getattr(client, "store_slug", None)
        if store_slug:
            for product in result.get("products", []) or []:
                product.setdefault("store_domain", store_slug)
            result.setdefault("store_domain", store_slug)
        return result
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/orders")
async def get_orders(
    cursor: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    query: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=250),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    filters = []
    if status:
        filters.append(f"fulfillment_status:{status}")
    if query:
        filters.append(query)
    combined_query = " ".join(filters) or None

    try:
        result = await fetch_orders(client, cursor=cursor, query=combined_query, limit=limit)
        store_slug = getattr(client, "store_slug", None)
        if store_slug:
            for order in result.get("orders", []) or []:
                order.setdefault("store_domain", store_slug)
            result.setdefault("store_domain", store_slug)
        return result
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/inventory")
async def get_inventory(
    cursor: Optional[str] = Query(default=None),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    try:
        return await fetch_inventory_levels(client, cursor=cursor)
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/inventory/locations")
async def get_inventory_locations(client: ShopifyGraphQLClient = Depends(get_client)):
    try:
        return await fetch_locations(client)
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/customers")
async def get_customers(
    cursor: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    query_string = None
    if search:
        query_string = search if ":" in search else f"{search}"
    try:
        return await fetch_customers(client, cursor=cursor, query=query_string)
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/analytics/sales")
async def get_sales_analytics(
    days: int = Query(default=30, le=365),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    try:
        metrics = await calculate_sales_metrics(client, days=days)
        return {**metrics, "days": days}
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/analytics/top-products")
async def get_top_products_endpoint(
    days: int = Query(default=30, le=365),
    limit: int = Query(default=10, le=100),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    try:
        products = await get_top_products(client, days=days, limit=limit)
        return {"products": products, "days": days, "limit": limit}
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/analytics/sales-trend")
async def get_sales_trend_endpoint(
    days: int = Query(default=30, le=365),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    try:
        trend = await get_sales_trend(client, days=days)
        return {"trend": trend, "days": days}
    except Exception as exc:  # pylint: disable=broad-except
        raise _handle_query_error(exc) from exc


@router.get("/bulk/products")
async def get_all_products(
    max_pages: int = Query(default=10, le=40),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    try:
        products, page_info = await fetch_all_pages(
            lambda **kwargs: fetch_products(client, **kwargs), key="products", max_pages=max_pages
        )
        return {"products": products, "page_info": page_info}
    except Exception as exc:
        raise _handle_query_error(exc) from exc


@router.get("/export/sales")
async def export_sales_data(
    format: str = Query(default="csv", regex="^(csv|json|excel)$"),
    days: int = Query(default=30, le=365),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    client: ShopifyGraphQLClient = Depends(get_client),
):
    """Export sales data in CSV, JSON, or Excel format."""
    try:
        # Get sales trend data
        trend_data = await get_sales_trend(client, days=days)

        # Get top products
        top_products = await get_top_products(client, days=days, limit=100)

        # Get sales metrics
        sales_metrics = await calculate_sales_metrics(client, days=days)

        # Prepare data for export
        export_data = {
            "sales_trend": trend_data,
            "top_products": top_products,
            "summary": {
                "total_revenue": float(sales_metrics["total_revenue"]),
                "order_count": sales_metrics["order_count"],
                "average_order_value": float(sales_metrics["average_order_value"]),
                "period_days": days,
                "export_date": datetime.now(timezone.utc).isoformat(),
            }
        }

        if format == "json":
            # JSON export
            json_str = json.dumps(export_data, indent=2, default=str)
            return StreamingResponse(
                io.BytesIO(json_str.encode()),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )

        elif format == "csv":
            # CSV export - create multiple sections
            output = io.StringIO()
            writer = csv.writer(output)

            # Summary section
            writer.writerow(["Sales Summary"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Revenue", f"${export_data['summary']['total_revenue']:.2f}"])
            writer.writerow(["Order Count", export_data['summary']['order_count']])
            writer.writerow(["Average Order Value", f"${export_data['summary']['average_order_value']:.2f}"])
            writer.writerow(["Period (days)", export_data['summary']['period_days']])
            writer.writerow(["Export Date", export_data['summary']['export_date']])
            writer.writerow([])

            # Sales trend section
            writer.writerow(["Daily Sales Trend"])
            writer.writerow(["Date", "Revenue"])
            for item in trend_data:
                writer.writerow([item["date"], f"${float(item['total_revenue']):.2f}"])
            writer.writerow([])

            # Top products section
            writer.writerow(["Top Products"])
            writer.writerow(["Product ID", "Title", "Revenue", "Quantity Sold"])
            for product in top_products:
                writer.writerow([
                    product["product_id"],
                    product["title"],
                    f"${float(product['total_revenue']):.2f}",
                    product["quantity_sold"]
                ])

            csv_content = output.getvalue()
            return StreamingResponse(
                io.BytesIO(csv_content.encode()),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )

        elif format == "excel":
            # For Excel, we'll use CSV format with .xlsx extension
            # In production, you'd use openpyxl or xlsxwriter
            output = io.StringIO()
            writer = csv.writer(output)

            # Summary sheet
            writer.writerow(["Sales Summary"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Revenue", export_data['summary']['total_revenue']])
            writer.writerow(["Order Count", export_data['summary']['order_count']])
            writer.writerow(["Average Order Value", export_data['summary']['average_order_value']])
            writer.writerow(["Period (days)", export_data['summary']['period_days']])
            writer.writerow([])

            # Sales trend
            writer.writerow(["Daily Sales Trend"])
            writer.writerow(["Date", "Revenue"])
            for item in trend_data:
                writer.writerow([item["date"], float(item['total_revenue'])])
            writer.writerow([])

            # Top products
            writer.writerow(["Top Products"])
            writer.writerow(["Product ID", "Title", "Revenue", "Quantity Sold"])
            for product in top_products:
                writer.writerow([
                    product["product_id"],
                    product["title"],
                    float(product['total_revenue']),
                    product["quantity_sold"]
                ])

            csv_content = output.getvalue()
            return StreamingResponse(
                io.BytesIO(csv_content.encode()),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=sales_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                }
            )

    except Exception as exc:
        logger.error(f"Error exporting sales data: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(exc)}") from exc
