"""Helpers to normalise Shopify inventory webhook payloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class InventoryRecord:
    sku: str
    product_name: str
    available_quantity: int
    location: str
    reorder_point: int


class InventoryService:
    async def update_from_webhook(self, payload: Dict[str, Any]) -> InventoryRecord:
        inventory_item = payload.get("inventory_item") or {}
        product = payload.get("product") or {}

        sku = str(
            payload.get("sku")
            or inventory_item.get("sku")
            or product.get("sku")
            or payload.get("inventory_item_id")
            or "unknown"
        )
        product_name = str(
            payload.get("title")
            or product.get("title")
            or inventory_item.get("title")
            or payload.get("product_title")
            or "Unnamed product"
        )
        available_quantity = self._parse_int(
            payload.get("available")
            or payload.get("quantity")
            or inventory_item.get("available")
            or inventory_item.get("quantity")
        )
        location = str(
            payload.get("location")
            or payload.get("location_name")
            or payload.get("location_id")
            or inventory_item.get("location")
            or "default"
        )
        reorder_point = self._parse_int(
            payload.get("reorder_point")
            or inventory_item.get("reorder_point")
            or 0
        )

        return InventoryRecord(
            sku=sku,
            product_name=product_name,
            available_quantity=available_quantity,
            location=location,
            reorder_point=reorder_point,
        )

    def _parse_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0


inventory_service = InventoryService()
