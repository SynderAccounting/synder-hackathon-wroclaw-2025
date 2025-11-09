"""Utility helpers to normalise Shopify order webhook payloads."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


@dataclass
class OrderRecord:
    id: str
    order_number: str
    customer_name: str
    total_price: float
    status: str
    created_at: datetime


class OrderService:
    async def process_webhook_order(self, payload: Dict[str, Any]) -> OrderRecord:
        return self._build_order_record(payload)

    async def update_order_from_webhook(self, payload: Dict[str, Any]) -> OrderRecord:
        return self._build_order_record(payload)

    def _build_order_record(self, payload: Dict[str, Any]) -> OrderRecord:
        order_id = str(
            payload.get("id")
            or payload.get("order_id")
            or payload.get("admin_graphql_api_id")
            or uuid4()
        )
        order_number = str(payload.get("order_number") or payload.get("name") or order_id)

        customer_info = payload.get("customer") or {}
        customer_name = self._build_customer_name(customer_info)

        total_price = self._parse_float(
            payload.get("total_price")
            or payload.get("current_total_price")
            or payload.get("subtotal_price")
        )
        status = (
            payload.get("financial_status")
            or payload.get("fulfillment_status")
            or payload.get("status")
            or "unknown"
        )
        created_at = self._parse_datetime(
            payload.get("created_at")
            or payload.get("processed_at")
            or payload.get("updated_at")
        )

        return OrderRecord(
            id=order_id,
            order_number=order_number,
            customer_name=customer_name,
            total_price=total_price,
            status=str(status),
            created_at=created_at,
        )

    def _build_customer_name(self, customer_info: Dict[str, Any]) -> str:
        first_name = (customer_info or {}).get("first_name")
        last_name = (customer_info or {}).get("last_name")
        email = (customer_info or {}).get("email")

        name_parts = [part for part in [first_name, last_name] if part]
        if name_parts:
            return " ".join(name_parts)
        if email:
            return str(email)
        return "Unknown customer"

    def _parse_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _parse_datetime(self, value: Any) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        if isinstance(value, datetime):
            return value
        try:
            text = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(text)
        except ValueError:
            return datetime.now(timezone.utc)


order_service = OrderService()
