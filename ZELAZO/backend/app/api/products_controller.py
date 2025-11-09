"""Products API controller"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    ProductCreate,
    ProductResponse,
    ProductsListResponse,
    ProductsResponse
)
from app.core.database import get_db
from app.repositories.products_repository import ProductsRepository
from app.services.products_service import ProductsService

router = APIRouter(prefix="/products/v1", tags=["products"])


def get_products_service(db: AsyncSession = Depends(get_db)) -> ProductsService:
    """
    Dependency function to create service instance with repository.

    Args:
        db: Database session from dependency injection

    Returns:
        ProductsService: Service instance with injected repository
    """
    repository = ProductsRepository(db)
    return ProductsService(repository)


@router.get(
    "/products",
    response_model=ProductsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all products",
    description="Returns a list of all products with their IDs and details"
)
async def get_all_products(
    service: ProductsService = Depends(get_products_service)
) -> ProductsListResponse:
    """
    Get all products from the catalogue database.

    Returns:
        ProductsListResponse: List of all products with IDs including:
            - Product UUID
            - Product name
            - Category
            - Base price
            - Timestamps

    Example response:
        ```json
        {
            "products": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Wool socks",
                    "category": "Clothing",
                    "price": 15.99,
                    "created_at": "2025-11-08T12:00:00Z",
                    "updated_at": "2025-11-08T12:00:00Z"
                }
            ],
            "total": 1
        }
        ```
    """
    return await service.get_all_products()


@router.post(
    "/product",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product entry in the database"
)
async def create_product(
    data: ProductCreate,
    service: ProductsService = Depends(get_products_service)
) -> ProductResponse:
    """
    Create a new product in the catalogue.

    Args:
        data: ProductCreate containing:
            - name: Product name
            - category: Product category
            - price: Base product price

    Returns:
        ProductResponse: Created product with generated ID and timestamps

    Example request:
        ```json
        {
            "name": "Wool socks",
            "category": "Clothing",
            "price": 15.99
        }
        ```

    Example response:
        ```json
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Wool socks",
            "category": "Clothing",
            "price": 15.99,
            "created_at": "2025-11-08T12:00:00Z",
            "updated_at": "2025-11-08T12:00:00Z"
        }
        ```
    """
    return await service.create_product(data)


@router.get(
    "/products-stats",
    response_model=ProductsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all products with analytics",
    description="Returns a list of all products with their platform-specific details including price, quantity, and income"
)
async def get_products_analytics(
    service: ProductsService = Depends(get_products_service)
) -> ProductsResponse:
    """
    Get all products with platform details.

    Returns:
        ProductsResponse: Complete list of products including:
            - Product name
            - Total amount sold across all platforms
            - Platform-specific details (Amazon, Allegro, Temu):
                - Price on that platform
                - Quantity sold on that platform
                - Income this month from that platform

    Example response:
        ```json
        {
            "products": [
                {
                    "name": "Wool socks",
                    "total_amount": 150,
                    "platforms": [
                        {
                            "platform": "amazon",
                            "price": 12.99,
                            "amount": 80,
                            "income_this_month": 1039.20
                        },
                        {
                            "platform": "allegro",
                            "price": 11.50,
                            "amount": 50,
                            "income_this_month": 575.00
                        },
                        {
                            "platform": "temu",
                            "price": 9.99,
                            "amount": 20,
                            "income_this_month": 199.80
                        }
                    ]
                },
                {
                    "name": "Cotton socks",
                    "total_amount": 220,
                    "platforms": [...]
                }
            ]
        }
        ```
    """
    return service.get_all_products_analytics()
