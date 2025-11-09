"""SQLAlchemy models representing commerce catalog and order data."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shopify_product_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True)
    sku: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    safety_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_price: Mapped[Optional[Numeric]] = mapped_column(Numeric(10, 2), nullable=True)
    selling_price: Mapped[Optional[Numeric]] = mapped_column(Numeric(10, 2), nullable=True)
    holding_cost: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shopify_order_id: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    order_number: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_price: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    fulfillment_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    financial_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    line_items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    variant_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sku: Mapped[str] = mapped_column(String, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit_price: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped[Order] = relationship(back_populates="line_items")
    product: Mapped[Optional[Product]] = relationship(back_populates="order_items")


class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String, index=True)
    available_quantity: Mapped[int] = mapped_column(Integer, default=0)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


__all__ = ["InventorySnapshot", "Order", "OrderItem", "Product"]
