"""Product model for catalogue management"""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """Product model representing product catalogue items"""

    __tablename__ = "products"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )

    # Product details
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, comment="Product name")
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Product category")
    sku: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True, index=True,
        comment="Stock Keeping Unit - unique identifier for matching across platforms"
    )
    description: Mapped[str | None] = mapped_column(
        String(2000), nullable=True, comment="Product description for AI matching"
    )

    # Pricing - using Numeric for precise money values
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, comment="Base product price"
    )

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, name='{self.name}', "
            f"category='{self.category}', price={self.price})>"
        )
