"""Listed Products API controller"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    ListedProductCreate,
    ListedProductResponse,
    ListedProductsListResponse,
    BulkImportRequest,
    BulkImportResponse,
    MatchedListingItem,
    ProductMatchSuggestion,
    ExternalListingItem
)
from app.core.database import get_db
from app.repositories.listed_products_repository import ListedProductsRepository
from app.repositories.products_repository import ProductsRepository
from app.services.listed_products_service import ListedProductsService
from app.services.product_matching_service import ProductMatchingService
from app.ai.ai_service import create_ai_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/listed-products/v1", tags=["listed-products"])


def get_listed_products_service(db: AsyncSession = Depends(get_db)) -> ListedProductsService:
    """
    Dependency function to create service instance with repository.

    Args:
        db: Database session from dependency injection

    Returns:
        ListedProductsService: Service instance with injected repository
    """
    repository = ListedProductsRepository(db)
    return ListedProductsService(repository)


@router.post(
    "/listings",
    response_model=ListedProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product listing",
    description="List a product on a marketplace with specified quantity and listing date"
)
async def create_listing(
    data: ListedProductCreate,
    service: ListedProductsService = Depends(get_listed_products_service)
) -> ListedProductResponse:
    """
    Create a new product listing on a marketplace.

    Args:
        data: ListedProductCreate containing:
            - product_id (optional): UUID of the product to list
            - marketplace: Name of the marketplace (amazon, allegro, temu, etc.)
            - amount: Quantity of items to list
            - date_of_listing: Date and time when product is listed

    Returns:
        ListedProductResponse: Created listing with generated ID and timestamps

    Example request:
        ```json
        {
            "product_id": "550e8400-e29b-41d4-a716-446655440000",
            "marketplace": "amazon",
            "amount": 100,
            "date_of_listing": "2025-11-08T12:00:00Z"
        }
        ```

    Example response:
        ```json
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "product_id": "550e8400-e29b-41d4-a716-446655440000",
            "marketplace": "amazon",
            "amount": 100,
            "date_of_listing": "2025-11-08T12:00:00Z",
            "created_at": "2025-11-08T12:05:30Z",
            "updated_at": "2025-11-08T12:05:30Z"
        }
        ```
    """
    return await service.create_listed_product(data)


@router.get(
    "/listings",
    response_model=ListedProductsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all product listings",
    description="Retrieve all products that have been listed on marketplaces"
)
async def get_all_listings(
    service: ListedProductsService = Depends(get_listed_products_service)
) -> ListedProductsListResponse:
    """
    Get all product listings across all marketplaces.

    Returns:
        ListedProductsListResponse: List of all product listings with total count

    Example response:
        ```json
        {
            "listed_products": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "product_id": "550e8400-e29b-41d4-a716-446655440000",
                    "marketplace": "amazon",
                    "amount": 150,
                    "date_of_listing": "2025-11-01T10:00:00Z",
                    "created_at": "2025-11-01T10:00:00Z",
                    "updated_at": "2025-11-01T10:00:00Z"
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426614174001",
                    "product_id": "550e8400-e29b-41d4-a716-446655440001",
                    "marketplace": "allegro",
                    "amount": 200,
                    "date_of_listing": "2025-11-02T14:30:00Z",
                    "created_at": "2025-11-02T14:30:00Z",
                    "updated_at": "2025-11-02T14:30:00Z"
                }
            ],
            "total": 2
        }
        ```
    """
    return await service.get_all_listed_products()


@router.post(
    "/import-bulk",
    response_model=BulkImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk import external listings with auto-matching",
    description="""Import multiple external listings and automatically match them to products.

    This endpoint uses a 3-tier matching strategy:
    1. **SKU Exact Match**: If listing has SKU matching a product → instant match
    2. **AI Fuzzy Match**: Uses AI to find best match based on name, description, price
    3. **No Match**: Saves listing without product_id for manual review

    **Automatic Saving**: All listings are saved to database with matched product_id (or None).

    Returns match status and confidence for each listing for your review.
    """
)
async def import_bulk_listings(
    request: BulkImportRequest,
    db: AsyncSession = Depends(get_db)
) -> BulkImportResponse:
    """
    Import external listings in bulk with automatic product matching and saving.

    This endpoint:
    1. Receives external listings from marketplaces
    2. Matches each to internal products using 3-tier strategy
    3. **Automatically saves** all listings to database
    4. Returns match results with confidence scores

    Args:
        request: BulkImportRequest with list of external listings
        db: Database session

    Returns:
        BulkImportResponse with matched items, stats, and saved listing IDs

    Example request:
        ```json
        {
            "listings": [
                {
                    "name": "Wool socks premium",
                    "description": "High quality winter socks",
                    "sku": "SOCK-WOOL-001",
                    "marketplace": "allegro",
                    "amount": 50,
                    "price": 19.99,
                    "date_of_listing": "2025-11-08T12:00:00Z"
                }
            ]
        }
        ```

    Example response:
        ```json
        {
            "matched_items": [
                {
                    "external_listing": {...},
                    "suggested_match": {
                        "product_id": "uuid",
                        "product_name": "Wool socks",
                        "confidence": 1.0,
                        "reason": "SKU exact match"
                    },
                    "match_status": "exact",
                    "saved_listing_id": "uuid"
                }
            ],
            "total": 1,
            "exact_matches": 1,
            "suggested_matches": 0,
            "no_matches": 0,
            "ai_enabled": true
        }
        ```
    """
    # Initialise services
    products_repo = ProductsRepository(db)
    listed_products_repo = ListedProductsRepository(db)
    ai_service = create_ai_service(settings.OPENAI_API_KEY)
    matching_service = ProductMatchingService(products_repo, ai_service)
    listed_products_service = ListedProductsService(listed_products_repo)

    # Track stats
    exact_matches = 0
    suggested_matches = 0
    no_matches = 0
    matched_items = []

    # Process each listing
    for external_listing_data in request.listings:
        # Convert to dict for matching service
        external_dict = external_listing_data.model_dump()

        # Match to internal product
        match_result = await matching_service.match_external_listing(external_dict)
        logger.info(f"Match result: product_id={match_result['product_id']}, confidence={match_result['confidence']}, status={match_result['match_status']}")

        # Validate that matched product_id actually exists in database
        validated_product_id = None
        if match_result["product_id"]:
            logger.info(f"Validating product_id: {match_result['product_id']}")
            # Double-check the product exists (prevents AI hallucinations)
            existing_product = await products_repo.get_by_id(match_result["product_id"])
            if existing_product:
                logger.info(f"Product validation SUCCESS - found product: {existing_product.name}")
                validated_product_id = match_result["product_id"]
            else:
                logger.warning(f"Product validation FAILED - product_id {match_result['product_id']} not found in database")
                # AI returned invalid product_id, treat as no match
                match_result["product_id"] = None
                match_result["product_name"] = None
                match_result["confidence"] = 0.0
                match_result["reason"] = "AI suggested invalid product_id (not found in database)"
                match_result["match_status"] = "none"

        logger.info(f"Final validated_product_id: {validated_product_id}")

        # Prepare ListedProductCreate schema
        listing_create = ListedProductCreate(
            product_id=validated_product_id,  # Can be None
            marketplace=external_listing_data.marketplace,
            amount=external_listing_data.amount,
            price=external_listing_data.price,
            date_of_listing=external_listing_data.date_of_listing
        )

        # Save to database
        saved_listing = await listed_products_service.create_listed_product(listing_create)

        # Track stats
        if match_result["match_status"] == "exact":
            exact_matches += 1
        elif match_result["match_status"] == "suggested":
            suggested_matches += 1
        else:
            no_matches += 1

        # Build response item
        matched_item = MatchedListingItem(
            external_listing=external_listing_data,
            suggested_match=ProductMatchSuggestion(
                product_id=match_result["product_id"],
                product_name=match_result["product_name"] or "No match",
                confidence=match_result["confidence"],
                reason=match_result["reason"]
            ) if match_result["product_id"] else None,
            match_status=match_result["match_status"]
        )

        matched_items.append(matched_item)

    # Return response
    return BulkImportResponse(
        matched_items=matched_items,
        total=len(request.listings),
        exact_matches=exact_matches,
        suggested_matches=suggested_matches,
        no_matches=no_matches,
        ai_enabled=ai_service.is_enabled()
    )
