"""
Repository for listed products database operations.
"""
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listed_product import ListedProduct


class ListedProductsRepository:
    """Repository class for listed products database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialise the repository with a database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, listed_product: ListedProduct) -> ListedProduct:
        """
        Create a new listed product in the database.

        Args:
            listed_product: ListedProduct model instance to create

        Returns:
            ListedProduct: The created listed product with database-generated values
        """
        self.session.add(listed_product)
        await self.session.commit()
        await self.session.refresh(listed_product)
        return listed_product

    async def get_by_id(self, listed_product_id: UUID) -> ListedProduct | None:
        """
        Retrieve a listed product by its ID.

        Args:
            listed_product_id: UUID of the listed product

        Returns:
            ListedProduct | None: The listed product if found, None otherwise
        """
        result = await self.session.execute(
            select(ListedProduct).where(ListedProduct.id == listed_product_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ListedProduct]:
        """
        Retrieve all listed products from the database.

        Returns:
            List[ListedProduct]: List of all listed products
        """
        result = await self.session.execute(
            select(ListedProduct).order_by(ListedProduct.date_of_listing.desc())
        )
        return list(result.scalars().all())

    async def get_by_product_id(self, product_id: UUID) -> List[ListedProduct]:
        """
        Retrieve all listings for a specific product.

        Args:
            product_id: UUID of the product

        Returns:
            List[ListedProduct]: List of all listings for the product
        """
        result = await self.session.execute(
            select(ListedProduct)
            .where(ListedProduct.product_id == product_id)
            .order_by(ListedProduct.date_of_listing.desc())
        )
        return list(result.scalars().all())

    async def get_by_marketplace(self, marketplace: str) -> List[ListedProduct]:
        """
        Retrieve all listings for a specific marketplace.

        Args:
            marketplace: Name of the marketplace

        Returns:
            List[ListedProduct]: List of all listings for the marketplace
        """
        result = await self.session.execute(
            select(ListedProduct)
            .where(ListedProduct.marketplace == marketplace)
            .order_by(ListedProduct.date_of_listing.desc())
        )
        return list(result.scalars().all())

    async def delete(self, listed_product_id: UUID) -> bool:
        """
        Delete a listed product by its ID.

        Args:
            listed_product_id: UUID of the listed product to delete

        Returns:
            bool: True if deleted, False if not found
        """
        listed_product = await self.get_by_id(listed_product_id)
        if listed_product:
            await self.session.delete(listed_product)
            await self.session.commit()
            return True
        return False
