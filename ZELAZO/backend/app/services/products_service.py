"""
Products service containing business logic for product operations.
"""
from decimal import Decimal

from app.api.schemas import (
    ProductCreate,
    ProductResponse,
    ProductsListResponse,
    ProductsResponse,
    ProductItem,
    ProductPlatform
)
from app.models.product import Product
from app.repositories.products_repository import ProductsRepository


class ProductsService:
    """Service class for product-related business logic."""

    def __init__(self, repository: ProductsRepository):
        """
        Initialise the products service.

        Args:
            repository: ProductsRepository for database operations
        """
        self.repository = repository

    async def create_product(self, data: ProductCreate) -> ProductResponse:
        """
        Create a new product in the catalogue.

        Args:
            data: ProductCreate schema with product details

        Returns:
            ProductResponse: Created product with generated ID and timestamps
        """
        # Create Product model instance
        product = Product(
            name=data.name,
            category=data.category,
            price=Decimal(str(data.price)),
            sku=data.sku,
            description=data.description
        )

        # Save to database via repository
        created_product = await self.repository.create(product)

        # Return as response schema
        return ProductResponse.model_validate(created_product)

    async def get_all_products(self) -> ProductsListResponse:
        """
        Retrieve all products from the database.

        Returns:
            ProductsListResponse: List of all products with total count
        """
        # Retrieve all from database via repository
        products_db = await self.repository.get_all()

        # Convert to response schemas
        products = [
            ProductResponse.model_validate(product) for product in products_db
        ]

        return ProductsListResponse(
            products=products,
            total=len(products)
        )

    def get_all_products_analytics(self) -> ProductsResponse:
        """
        Retrieve all products with platform-specific analytics details.
        This is hardcoded for now and used by the analytics dashboard.

        Returns:
            ProductsResponse: List of all products with their platform information
        """
        # Hardcoded product analytics data (for dashboard)
        products_data = [
            ProductItem(
                name="Wool socks",
                total_amount=150,
                platforms=[
                    ProductPlatform(
                        platform="amazon",
                        price=12.99,
                        amount=80,
                        income_this_month=1039.20
                    ),
                    ProductPlatform(
                        platform="allegro",
                        price=11.50,
                        amount=50,
                        income_this_month=575.00
                    ),
                    ProductPlatform(
                        platform="temu",
                        price=9.99,
                        amount=20,
                        income_this_month=199.80
                    )
                ]
            ),
            ProductItem(
                name="Cotton socks",
                total_amount=220,
                platforms=[
                    ProductPlatform(
                        platform="amazon",
                        price=8.99,
                        amount=120,
                        income_this_month=1078.80
                    ),
                    ProductPlatform(
                        platform="allegro",
                        price=7.50,
                        amount=70,
                        income_this_month=525.00
                    ),
                    ProductPlatform(
                        platform="temu",
                        price=6.99,
                        amount=30,
                        income_this_month=209.70
                    )
                ]
            ),
            ProductItem(
                name="Winter gloves",
                total_amount=95,
                platforms=[
                    ProductPlatform(
                        platform="amazon",
                        price=15.99,
                        amount=45,
                        income_this_month=719.55
                    ),
                    ProductPlatform(
                        platform="allegro",
                        price=14.99,
                        amount=35,
                        income_this_month=524.65
                    ),
                    ProductPlatform(
                        platform="temu",
                        price=12.99,
                        amount=15,
                        income_this_month=194.85
                    )
                ]
            ),
            ProductItem(
                name="Scarf",
                total_amount=130,
                platforms=[
                    ProductPlatform(
                        platform="amazon",
                        price=18.99,
                        amount=60,
                        income_this_month=1139.40
                    ),
                    ProductPlatform(
                        platform="allegro",
                        price=16.50,
                        amount=50,
                        income_this_month=825.00
                    ),
                    ProductPlatform(
                        platform="temu",
                        price=14.99,
                        amount=20,
                        income_this_month=299.80
                    )
                ]
            )
        ]

        return ProductsResponse(products=products_data)
