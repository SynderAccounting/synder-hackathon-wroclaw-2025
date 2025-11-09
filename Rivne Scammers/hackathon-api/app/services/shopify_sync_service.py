"""Services to synchronise Shopify resources into the local catalog tables."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from api.shopify.client import ShopifyGraphQLClient
from api.shopify.queries import fetch_inventory_levels, fetch_orders, fetch_products
from api.shopify.utils import fetch_all_pages
from db.database import SessionLocal
from models.catalog import InventorySnapshot, Order, OrderItem, Product


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ShopifySyncService:
    """Synchronise Shopify data into SQLAlchemy models."""

    def __init__(self, page_size: int = 50, max_pages: int = 10) -> None:
        self._page_size = page_size
        self._max_pages = max_pages

    async def sync_all(self, client: ShopifyGraphQLClient) -> Dict[str, Any]:
        products_result = await self.sync_products(client)
        orders_result = await self.sync_orders(client)
        inventory_result = await self.sync_inventory(client)

        # Derive a consolidated timestamp using the most recent update across tables.
        synced_at = max(
            filter(
                None,
                [
                    products_result.get("synced_at"),
                    orders_result.get("synced_at"),
                    inventory_result.get("synced_at"),
                ],
            ),
            default=_utcnow(),
        )

        return {
            "synced_at": synced_at,
            "products_synced": products_result.get("processed", 0),
            "orders_synced": orders_result.get("processed", 0),
            "inventory_synced": inventory_result.get("processed", 0),
        }

    async def sync_products(self, client: ShopifyGraphQLClient) -> Dict[str, Any]:
        session = SessionLocal()
        processed = 0
        try:
            products, _ = await fetch_all_pages(
                lambda cursor=None: fetch_products(client, cursor=cursor, limit=self._page_size),
                key="products",
                max_pages=self._max_pages,
            )

            for product in products:
                self._upsert_product(session, product)
                processed += 1

            session.commit()
            synced_at = self._latest_timestamp(session, Product.updated_at)
            return {"processed": processed, "synced_at": synced_at or _utcnow()}
        except Exception:  # pragma: no cover - upstream errors escalate
            session.rollback()
            raise
        finally:
            session.close()

    async def sync_orders(self, client: ShopifyGraphQLClient) -> Dict[str, Any]:
        session = SessionLocal()
        processed = 0
        try:
            orders, _ = await fetch_all_pages(
                lambda cursor=None: fetch_orders(client, cursor=cursor, limit=self._page_size),
                key="orders",
                max_pages=self._max_pages,
            )

            for order in orders:
                self._upsert_order(session, order)
                processed += 1

            session.commit()
            synced_at = self._latest_timestamp(session, Order.updated_at)
            return {"processed": processed, "synced_at": synced_at or _utcnow()}
        except Exception:  # pragma: no cover - upstream errors escalate
            session.rollback()
            raise
        finally:
            session.close()

    async def sync_inventory(self, client: ShopifyGraphQLClient) -> Dict[str, Any]:
        session = SessionLocal()
        processed = 0
        try:
            inventory_items, _ = await fetch_all_pages(
                lambda cursor=None: fetch_inventory_levels(client, cursor=cursor, limit=self._page_size),
                key="inventory_items",
                max_pages=self._max_pages,
            )

            # Track aggregated stock per SKU to keep product inventory in sync.
            sku_totals: Dict[str, int] = {}

            for item in inventory_items:
                sku = (item.get("sku") or (item.get("variant") or {}).get("sku") or "").strip()
                if not sku:
                    continue

                inventory_levels: Iterable[Dict[str, Any]] = item.get("inventoryLevels") or []
                for level in inventory_levels:
                    processed += 1
                    available = int(level.get("available") or 0)
                    location = (level.get("location") or {}).get("name")
                    self._upsert_inventory_snapshot(session, sku, available, location)
                    sku_totals[sku] = sku_totals.get(sku, 0) + available

            if sku_totals:
                self._update_product_stock(session, sku_totals)

            session.commit()
            synced_at = self._latest_snapshot_timestamp(session)
            return {"processed": processed, "synced_at": synced_at or _utcnow()}
        except Exception:  # pragma: no cover - upstream errors escalate
            session.rollback()
            raise
        finally:
            session.close()

    def _upsert_product(self, session: Session, payload: Dict[str, Any]) -> Product:
        shopify_id = str(payload.get("id") or payload.get("gid") or "").strip() or None
        variants = payload.get("variants") or {}
        variant_list = self._extract_variants(variants)
        primary_variant = variant_list[0] if variant_list else {}

        sku = (primary_variant.get("sku") or payload.get("handle") or shopify_id or "").strip()
        if not sku:
            sku = f"product-{payload.get('title', 'unknown')}"

        filters = [Product.sku == sku]
        if shopify_id:
            filters.append(Product.shopify_product_id == shopify_id)

        stmt = select(Product).where(or_(*filters))
        existing = session.execute(stmt).scalars().first()
        price = self._parse_decimal(primary_variant.get("price"))
        inventory = self._parse_int(payload.get("totalInventory"))

        tags = payload.get("tags")
        if isinstance(tags, list):
            tags_value = ",".join(tag.strip() for tag in tags if tag)
        else:
            tags_value = tags

        if existing:
            existing.shopify_product_id = existing.shopify_product_id or shopify_id
            existing.sku = existing.sku or sku
            existing.title = payload.get("title") or existing.title
            existing.category = payload.get("productType") or existing.category
            existing.current_stock = inventory if inventory is not None else existing.current_stock
            if price is not None:
                existing.selling_price = price
            existing.tags = tags_value or existing.tags
            return existing

        product = Product(
            shopify_product_id=shopify_id,
            sku=sku,
            title=payload.get("title"),
            category=payload.get("productType"),
            current_stock=inventory or 0,
            selling_price=price,
            tags=tags_value,
        )
        session.add(product)
        return product

    def _upsert_order(self, session: Session, payload: Dict[str, Any]) -> Order:
        shopify_id = str(payload.get("id") or payload.get("admin_graphql_api_id") or "").strip() or None
        order_number = payload.get("name") or payload.get("orderNumber")

        stmt = select(Order)
        if shopify_id:
            stmt = stmt.where(Order.shopify_order_id == shopify_id)
        else:
            stmt = stmt.where(Order.order_number == order_number)

        existing = session.execute(stmt).scalars().first()

        total_price = self._parse_decimal(
            ((payload.get("totalPriceSet") or {}).get("shopMoney") or {}).get("amount")
            or payload.get("total_price")
        )
        currency = (
            ((payload.get("totalPriceSet") or {}).get("shopMoney") or {}).get("currencyCode")
            or payload.get("currency")
            or "USD"
        )

        created_at = self._parse_datetime(payload.get("createdAt") or payload.get("created_at"))
        updated_at = self._parse_datetime(payload.get("updatedAt") or payload.get("updated_at"))

        fulfillment_status = (
            payload.get("displayFulfillmentStatus")
            or payload.get("fulfillment_status")
            or payload.get("fulfillmentStatus")
        )
        financial_status = (
            payload.get("displayFinancialStatus")
            or payload.get("financial_status")
            or payload.get("financialStatus")
        )

        if existing is None:
            existing = Order(
                shopify_order_id=shopify_id,
                order_number=order_number,
                total_price=total_price,
                currency=currency,
                fulfillment_status=fulfillment_status,
                financial_status=financial_status,
                created_at=created_at or _utcnow(),
                updated_at=updated_at or _utcnow(),
            )
            session.add(existing)
        else:
            existing.order_number = order_number or existing.order_number
            existing.total_price = total_price if total_price is not None else existing.total_price
            existing.currency = currency or existing.currency
            existing.fulfillment_status = fulfillment_status or existing.fulfillment_status
            existing.financial_status = financial_status or existing.financial_status
            existing.created_at = created_at or existing.created_at
            existing.updated_at = updated_at or existing.updated_at
            existing.line_items.clear()

        line_items = self._extract_line_items(payload.get("lineItems") or payload.get("line_items"))
        for item in line_items:
            sku = (item.get("sku") or (item.get("variant") or {}).get("sku") or "").strip()
            quantity = self._parse_int(item.get("quantity")) or 0
            if not sku:
                continue

            product = session.execute(select(Product).where(Product.sku == sku)).scalars().first()
            unit_price = self._parse_float(
                ((item.get("originalUnitPriceSet") or {}).get("shopMoney") or {}).get("amount")
                or (item.get("variant") or {}).get("price")
            )

            existing.line_items.append(
                OrderItem(
                    product=product,
                    sku=sku,
                    quantity=quantity,
                    unit_price=unit_price,
                    variant_id=(item.get("variant") or {}).get("id"),
                )
            )

        return existing

    def _upsert_inventory_snapshot(
        self,
        session: Session,
        sku: str,
        available: int,
        location: Optional[str],
    ) -> InventorySnapshot:
        stmt = select(InventorySnapshot).where(
            InventorySnapshot.sku == sku,
            InventorySnapshot.location == location,
        )
        snapshot = session.execute(stmt).scalars().first()
        if snapshot:
            snapshot.available_quantity = available
            snapshot.snapshot_date = _utcnow()
            return snapshot

        snapshot = InventorySnapshot(
            sku=sku,
            available_quantity=available,
            location=location,
            snapshot_date=_utcnow(),
        )
        session.add(snapshot)
        return snapshot

    def _update_product_stock(self, session: Session, sku_totals: Dict[str, int]) -> None:
        for sku, quantity in sku_totals.items():
            product = session.execute(select(Product).where(Product.sku == sku)).scalars().first()
            if product:
                product.current_stock = quantity

    def _latest_timestamp(self, session: Session, column) -> Optional[datetime]:  # type: ignore[no-untyped-def]
        return session.execute(select(func.max(column))).scalar_one_or_none()

    def _latest_snapshot_timestamp(self, session: Session) -> Optional[datetime]:
        return session.execute(select(func.max(InventorySnapshot.snapshot_date))).scalar_one_or_none()

    def _extract_variants(self, variants: Any) -> list[Dict[str, Any]]:  # type: ignore[list-item]
        if isinstance(variants, dict) and "edges" in variants:
            return [edge.get("node", {}) for edge in variants.get("edges", []) if edge]
        if isinstance(variants, list):
            return variants
        return []

    def _extract_line_items(self, line_items: Any) -> list[Dict[str, Any]]:  # type: ignore[list-item]
        if isinstance(line_items, dict) and "edges" in line_items:
            return [edge.get("node", {}) for edge in line_items.get("edges", []) if edge]
        if isinstance(line_items, list):
            return line_items
        return []

    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        if value is None or value == "":
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None

    def _parse_float(self, value: Any) -> Optional[float]:
        try:
            parsed = float(value)
            if parsed != parsed:  # NaN check
                return None
            return parsed
        except (TypeError, ValueError):
            return None

    def _parse_int(self, value: Any) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            text = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(text)
        except ValueError:
            return None


shopify_sync_service = ShopifySyncService()
"""Singleton instance used across the application."""
