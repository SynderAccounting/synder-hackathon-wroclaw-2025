"""ListedProduct model for marketplace listings"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from decimal import Decimal

from .base import Base, TimestampMixin


class ListedProduct(Base, TimestampMixin):
    """ListedProduct model representing products listed on marketplaces"""

    __tablename__ = "listed_products"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )

    # Foreign key to products table (nullable to allow unmatched listings)
    product_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Reference to the product being listed (can be null for unmatched external listings)"
    )

    # Marketplace information
    marketplace: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Marketplace where product is listed (e.g., amazon, allegro, temu)"
    )

    # Listing details
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity of items listed"
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
        comment="Selling price on this marketplace"
    )

    date_of_listing: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Date and time when product was listed"
    )

    # Relationship to Product (optional, for convenient access)
    # product: Mapped["Product"] = relationship("Product", back_populates="listings")

    def __repr__(self) -> str:
        return (
            f"<ListedProduct(id={self.id}, product_id={self.product_id}, "
            f"marketplace='{self.marketplace}', amount={self.amount}, price={self.price})>"
        )
