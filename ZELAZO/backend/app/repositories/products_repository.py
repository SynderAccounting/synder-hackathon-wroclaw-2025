"""
Repository for products database operations.
"""
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductsRepository:
    """Repository class for products database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialise the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, product: Product) -> Product:
        """
        Create a new product in the database.

        Args:
            product: Product model instance to create

        Returns:
            Product: The created product with database-generated values
        """
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_by_id(self, product_id: UUID) -> Product | None:
        """
        Retrieve a product by its ID.

        Args:
            product_id: UUID of the product

        Returns:
            Product | None: The product if found, None otherwise
        """
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Product]:
        """
        Retrieve all products from the database.

        Returns:
            List[Product]: List of all products ordered by creation date
        """
        result = await self.session.execute(
            select(Product).order_by(Product.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> List[Product]:
        """
        Retrieve all products in a specific category.

        Args:
            category: Product category name

        Returns:
            List[Product]: List of products in the category
        """
        result = await self.session.execute(
            select(Product)
            .where(Product.category == category)
            .order_by(Product.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_sku(self, sku: str) -> Product | None:
        """
        Retrieve a product by its SKU.

        Args:
            sku: Stock Keeping Unit

        Returns:
            Product | None: The product if found, None otherwise
        """
        result = await self.session.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def get_by_sku_or_id(self, identifier: str) -> Product | None:
        """
        Retrieve a product by SKU or ID.

        First tries to match against product.sku, then falls back to product.id.
        This is useful for external platform matching where the identifier could be either.

        Args:
            identifier: SKU string or UUID string

        Returns:
            Product | None: The product if found, None otherwise
        """
        from uuid import UUID

        # First try SKU match (exact string match)
        result = await self.session.execute(
            select(Product).where(Product.sku == identifier)
        )
        product = result.scalar_one_or_none()

        if product:
            return product

        # If not found by SKU, try to parse as UUID and match against ID
        try:
            uuid_id = UUID(identifier)
            result = await self.session.execute(
                select(Product).where(Product.id == uuid_id)
            )
            return result.scalar_one_or_none()
        except (ValueError, AttributeError):
            # Not a valid UUID, return None
            return None

    async def update(self, product: Product) -> Product:
        """
        Update an existing product.

        Args:
            product: Product model instance with updated values

        Returns:
            Product: The updated product
        """
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product_id: UUID) -> bool:
        """
        Delete a product by its ID.

        Args:
            product_id: UUID of the product to delete

        Returns:
            bool: True if deleted, False if not found
        """
        product = await self.get_by_id(product_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()
            return True
        return False
