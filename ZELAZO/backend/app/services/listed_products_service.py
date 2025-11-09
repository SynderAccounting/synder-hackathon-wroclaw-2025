"""
Listed products service containing business logic for marketplace listings.
"""
from uuid import uuid4

from app.api.schemas import (
    ListedProductCreate,
    ListedProductResponse,
    ListedProductsListResponse
)
from app.models.listed_product import ListedProduct
from app.repositories.listed_products_repository import ListedProductsRepository


class ListedProductsService:
    """Service class for listed product-related business logic."""

    def __init__(self, repository: ListedProductsRepository):
        """
        Initialise the listed products service.

        Args:
            repository: ListedProductsRepository for database operations
        """
        self.repository = repository

    async def create_listed_product(self, data: ListedProductCreate) -> ListedProductResponse:
        """
        Create a new listed product entry.

        Args:
            data: ListedProductCreate schema with product listing details

        Returns:
            ListedProductResponse: Created listed product with generated ID and timestamps
        """
        # Create ListedProduct model instance
        # product_id can be None for unmatched external listings
        listed_product = ListedProduct(
            product_id=data.product_id,  # Can be None
            marketplace=data.marketplace,
            amount=data.amount,
            price=data.price,
            date_of_listing=data.date_of_listing
        )

        # Save to database via repository
        created_product = await self.repository.create(listed_product)

        # Return as response schema
        return ListedProductResponse.model_validate(created_product)

    async def get_all_listed_products(self) -> ListedProductsListResponse:
        """
        Retrieve all listed products.

        Returns:
            ListedProductsListResponse: List of all listed products with total count
        """
        # Retrieve all from database via repository
        listed_products_db = await self.repository.get_all()

        # Convert to response schemas
        listed_products = [
            ListedProductResponse.model_validate(lp) for lp in listed_products_db
        ]

        return ListedProductsListResponse(
            listed_products=listed_products,
            total=len(listed_products)
        )
