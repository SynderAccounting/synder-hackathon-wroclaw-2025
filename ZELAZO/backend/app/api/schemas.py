"""Pydantic schemas for API responses"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health check status enum"""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "crit"


class HealthCheck(BaseModel):
    """Health check information"""
    status: HealthStatus = Field(..., description="Current system health status")
    message: str = Field(..., description="Health status message")


class PlatformDetails(BaseModel):
    """Platform-specific statistics"""
    platform: str = Field(..., description="Platform name (amazon, allegro, temu)")
    income_this_month: float = Field(..., description="Total income for current month")
    orders_this_month: int = Field(..., description="Total orders for current month")
    income_difference: float = Field(
        ...,
        description="Income difference compared to previous month (positive = increase, negative = decrease)"
    )


class DashboardResponse(BaseModel):
    """Dashboard summary response"""
    health_check: HealthCheck = Field(..., description="System health information")
    orders_amount_this_month: int = Field(..., description="Total orders across all platforms this month")
    income_this_month: float = Field(..., description="Total income across all platforms this month")
    platforms: List[PlatformDetails] = Field(..., description="Detailed statistics per platform")

    class Config:
        json_schema_extra = {
            "example": {
                "health_check": {
                    "status": "warning",
                    "message": "Warning: decreased amount of sold goods"
                },
                "orders_amount_this_month": 1250,
                "income_this_month": 45780.50,
                "platforms": [
                    {
                        "platform": "amazon",
                        "income_this_month": 25000.00,
                        "orders_this_month": 650,
                        "income_difference": -2500.00
                    },
                    {
                        "platform": "allegro",
                        "income_this_month": 15000.50,
                        "orders_this_month": 450,
                        "income_difference": 1200.50
                    },
                    {
                        "platform": "temu",
                        "income_this_month": 5780.00,
                        "orders_this_month": 150,
                        "income_difference": 780.00
                    }
                ]
            }
        }


# Product CRUD schemas
class ProductCreate(BaseModel):
    """Schema for creating a new product"""
    name: str = Field(..., description="Product name", min_length=1, max_length=255)
    category: str = Field(..., description="Product category", min_length=1, max_length=100)
    price: float = Field(..., description="Base product price", gt=0)
    sku: Optional[str] = Field(None, description="Stock Keeping Unit", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Product description", max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wool socks",
                "category": "Clothing",
                "price": 15.99,
                "sku": "WOOL-SOCK-001",
                "description": "High quality winter wool socks"
            }
        }


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: UUID = Field(..., description="Product UUID")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., description="Base product price")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit")
    description: Optional[str] = Field(None, description="Product description")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Wool socks",
                "category": "Clothing",
                "price": 15.99,
                "created_at": "2025-11-08T12:00:00Z",
                "updated_at": "2025-11-08T12:00:00Z"
            }
        }


class ProductsListResponse(BaseModel):
    """Schema for list of products"""
    products: List[ProductResponse] = Field(..., description="List of all products")
    total: int = Field(..., description="Total number of products")

    class Config:
        json_schema_extra = {
            "example": {
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
        }


# Product-related schemas (for dashboard/analytics)
class ProductPlatform(BaseModel):
    """Platform-specific product information"""
    platform: str = Field(..., description="Platform name (amazon, allegro, temu)")
    price: float = Field(..., description="Product price on this platform")
    amount: int = Field(..., description="Quantity sold on this platform")
    income_this_month: float = Field(..., description="Total income from this product on this platform this month")


class ProductItem(BaseModel):
    """Product information with platform details"""
    name: str = Field(..., description="Product name")
    total_amount: int = Field(..., description="Total quantity sold across all platforms")
    platforms: List[ProductPlatform] = Field(..., description="Platform-specific details for this product")


class ProductsResponse(BaseModel):
    """Response containing list of all products"""
    products: List[ProductItem] = Field(..., description="List of products with platform details")

    class Config:
        json_schema_extra = {
            "example": {
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
                    }
                ]
            }
        }


# Listed Product schemas
class ListedProductCreate(BaseModel):
    """Schema for creating a new listed product"""
    product_id: Optional[UUID] = Field(None, description="Optional UUID of the product to list")
    marketplace: str = Field(..., description="Marketplace name (e.g., amazon, allegro, temu)", min_length=1, max_length=100)
    amount: int = Field(..., description="Quantity of items to list", gt=0)
    price: float = Field(..., description="Selling price on this marketplace", gt=0)
    date_of_listing: datetime = Field(..., description="Date and time when product is listed")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "550e8400-e29b-41d4-a716-446655440000",
                "marketplace": "amazon",
                "amount": 100,
                "price": 19.99,
                "date_of_listing": "2025-11-08T12:00:00Z"
            }
        }


class ListedProductResponse(BaseModel):
    """Schema for listed product response"""
    id: UUID = Field(..., description="Listed product UUID")
    product_id: Optional[UUID] = Field(None, description="Reference to the product (null if not matched)")
    marketplace: str = Field(..., description="Marketplace name")
    amount: int = Field(..., description="Quantity listed")
    price: float = Field(..., description="Selling price on this marketplace")
    date_of_listing: datetime = Field(..., description="Listing date and time")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "product_id": "550e8400-e29b-41d4-a716-446655440000",
                "marketplace": "amazon",
                "amount": 100,
                "price": 19.99,
                "date_of_listing": "2025-11-08T12:00:00Z",
                "created_at": "2025-11-08T12:00:00Z",
                "updated_at": "2025-11-08T12:00:00Z"
            }
        }


class ListedProductsListResponse(BaseModel):
    """Schema for list of listed products"""
    listed_products: List[ListedProductResponse] = Field(..., description="List of all listed products")
    total: int = Field(..., description="Total number of listed products")

    class Config:
        json_schema_extra = {
            "example": {
                "listed_products": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "product_id": "550e8400-e29b-41d4-a716-446655440000",
                        "marketplace": "amazon",
                        "amount": 100,
                        "price": 19.99,
                        "date_of_listing": "2025-11-08T12:00:00Z",
                        "created_at": "2025-11-08T12:00:00Z",
                        "updated_at": "2025-11-08T12:00:00Z"
                    }
                ],
                "total": 1
            }
        }


# AI Insights schemas
class InsightsResponse(BaseModel):
    """Schema for AI-generated insights"""
    insights: List[str] = Field(..., description="List of key insights from the data")
    recommendations: List[str] = Field(..., description="List of strategic recommendations")
    summary: str = Field(..., description="Overall summary of the current situation")
    ai_enabled: bool = Field(..., description="Whether AI service is enabled and functioning")

    class Config:
        json_schema_extra = {
            "example": {
                "insights": [
                    "Amazon generates the highest revenue with £25,000 this month",
                    "Temu shows strong growth with 5% increase month-over-month",
                    "Allegro orders decreased by 10%, indicating potential market challenges"
                ],
                "recommendations": [
                    "Investigate the decline in Allegro sales and adjust pricing strategy",
                    "Expand product listings on Temu to capitalize on growth momentum",
                    "Consider promotional campaigns on underperforming platforms"
                ],
                "summary": "Overall sales are healthy with £48,500 in revenue across all platforms. Amazon remains the strongest performer, while Temu shows promising growth. Allegro requires attention due to declining orders.",
                "ai_enabled": True
            }
        }


# Onboarding schemas
class OnboardingRequest(BaseModel):
    """Schema for onboarding analysis request"""
    country: str = Field(..., description="Target country for selling (e.g., Poland, UK, USA)", min_length=2, max_length=100)
    product_name: str = Field(..., description="Name of the product to sell", min_length=1, max_length=255)
    product_description: str = Field(..., description="Description of the product", min_length=10, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "country": "Poland",
                "product_name": "Handmade Wool Hoodie",
                "product_description": "High-quality streetwear hoodie made from organic wool, featuring unique embroidered designs. Perfect for casual wear and street fashion enthusiasts."
            }
        }


class MarketOverview(BaseModel):
    """Market overview information"""
    demand: str = Field(..., description="Demand level (Low, Medium, High)")
    average_price: str = Field(..., description="Average price range in local currency")
    trend: str = Field(..., description="Market trend (Growing, Stable, Declining)")
    marketplaces: List[str] = Field(..., description="Recommended marketplaces for this product")


class Competition(BaseModel):
    """Competition analysis"""
    level: str = Field(..., description="Competition level (Low, Medium, High)")
    popular_brands: List[str] = Field(..., description="Popular competing brands")


class TargetAudience(BaseModel):
    """Target audience information"""
    age: str = Field(..., description="Target age range")
    gender: str = Field(..., description="Target gender")
    interests: List[str] = Field(..., description="Target audience interests")


class MarketplaceRecommendation(BaseModel):
    """Individual marketplace recommendation"""
    name: str = Field(..., description="Marketplace name")
    description: str = Field(..., description="Why this marketplace is recommended")
    icon: str = Field(..., description="Icon identifier for UI (e.g., flag.fill, globe, iphone)")


class OnboardingResponse(BaseModel):
    """Schema for onboarding analysis response"""
    market_overview: MarketOverview = Field(..., description="Overview of the market")
    competition: Competition = Field(..., description="Competition analysis")
    target_audience: TargetAudience = Field(..., description="Target audience profile")
    marketplaces: List[MarketplaceRecommendation] = Field(..., description="Recommended marketplaces with details")
    tips: List[str] = Field(..., description="Practical tips for starting to sell")
    ai_enabled: bool = Field(..., description="Whether AI service is enabled")

    class Config:
        json_schema_extra = {
            "example": {
                "market_overview": {
                    "demand": "High",
                    "average_price": "120-180 zł",
                    "trend": "Growing",
                    "marketplaces": ["Allegro", "Zalando", "OLX", "Etsy"]
                },
                "competition": {
                    "level": "Medium",
                    "popular_brands": ["Local Heroes", "Reserved", "2005"]
                },
                "target_audience": {
                    "age": "18-35",
                    "gender": "Mostly male",
                    "interests": ["Streetwear", "comfort", "unique design"]
                },
                "marketplaces": [
                    {
                        "name": "Allegro",
                        "description": "easiest to start, high traffic",
                        "icon": "flag.fill"
                    },
                    {
                        "name": "Zalando",
                        "description": "fashion-oriented, higher brand standards",
                        "icon": "flag.fill"
                    },
                    {
                        "name": "Etsy",
                        "description": "good for custom or handmade hoodies",
                        "icon": "globe"
                    },
                    {
                        "name": "OLX",
                        "description": "suitable for local or small-batch sales",
                        "icon": "iphone"
                    }
                ],
                "tips": [
                    "Start with Allegro – lower entry barrier",
                    "Use street-style photos for better engagement",
                    "Set price around 150-160 zł for best conversion"
                ],
                "ai_enabled": True
            }
        }


# Product Matching schemas for external platform imports
class ExternalListingItem(BaseModel):
    """Schema for an external listing item from a marketplace"""
    name: str = Field(..., description="Product name on the external platform")
    description: Optional[str] = Field(None, description="Product description")
    sku: Optional[str] = Field(None, description="SKU/ID from external platform")
    marketplace: str = Field(..., description="Marketplace name (allegro, amazon, etc)")
    amount: int = Field(..., description="Quantity listed", gt=0)
    price: float = Field(..., description="Selling price on the platform", gt=0)
    date_of_listing: datetime = Field(..., description="Date when product was listed")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wool socks premium quality",
                "description": "High quality winter socks",
                "sku": "ALLEGRO-12345",
                "marketplace": "allegro",
                "amount": 50,
                "price": 19.99,
                "date_of_listing": "2025-11-08T12:00:00Z"
            }
        }


class ProductMatchSuggestion(BaseModel):
    """Schema for AI product match suggestion"""
    product_id: UUID = Field(..., description="Matched product ID from database")
    product_name: str = Field(..., description="Product name")
    confidence: float = Field(..., description="Match confidence score (0.0-1.0)", ge=0.0, le=1.0)
    reason: str = Field(..., description="Explanation for the match")


class MatchedListingItem(BaseModel):
    """Schema for external listing with match suggestion"""
    external_listing: ExternalListingItem = Field(..., description="External listing data")
    suggested_match: Optional[ProductMatchSuggestion] = Field(None, description="AI-suggested product match")
    match_status: str = Field(..., description="Match status: exact, suggested, none")

    class Config:
        json_schema_extra = {
            "example": {
                "external_listing": {
                    "name": "Wool socks premium quality",
                    "description": "High quality winter socks",
                    "sku": "WOOL-SOCK-001",
                    "marketplace": "allegro",
                    "amount": 50,
                    "price": 19.99,
                    "date_of_listing": "2025-11-08T12:00:00Z"
                },
                "suggested_match": {
                    "product_id": "550e8400-e29b-41d4-a716-446655440000",
                    "product_name": "Wool socks",
                    "confidence": 0.95,
                    "reason": "SKU exact match"
                },
                "match_status": "exact"
            }
        }


class BulkImportRequest(BaseModel):
    """Schema for bulk import of external listings"""
    listings: List[ExternalListingItem] = Field(..., description="List of external listings to import")

    class Config:
        json_schema_extra = {
            "example": {
                "listings": [
                    {
                        "name": "Wool socks",
                        "sku": "WOOL-SOCK-001",
                        "marketplace": "allegro",
                        "amount": 50,
                        "price": 19.99,
                        "date_of_listing": "2025-11-08T12:00:00Z"
                    }
                ]
            }
        }


class BulkImportResponse(BaseModel):
    """Schema for bulk import response"""
    matched_items: List[MatchedListingItem] = Field(..., description="Items with match suggestions")
    total: int = Field(..., description="Total number of items processed")
    exact_matches: int = Field(..., description="Number of exact matches (SKU)")
    suggested_matches: int = Field(..., description="Number of AI-suggested matches")
    no_matches: int = Field(..., description="Number of items with no match found")
    ai_enabled: bool = Field(..., description="Whether AI matching was used")

    class Config:
        json_schema_extra = {
            "example": {
                "matched_items": [
                    {
                        "external_listing": {
                            "name": "Wool socks",
                            "marketplace": "allegro",
                            "amount": 50,
                            "price": 19.99,
                            "date_of_listing": "2025-11-08T12:00:00Z"
                        },
                        "suggested_match": {
                            "product_id": "550e8400-e29b-41d4-a716-446655440000",
                            "product_name": "Wool socks",
                            "confidence": 0.95,
                            "reason": "SKU exact match"
                        },
                        "match_status": "exact"
                    }
                ],
                "total": 1,
                "exact_matches": 1,
                "suggested_matches": 0,
                "no_matches": 0,
                "ai_enabled": True
            }
        }
