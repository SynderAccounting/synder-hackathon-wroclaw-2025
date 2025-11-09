"""Request validation schemas using Pydantic."""
from typing import Optional
from pydantic import BaseModel, Field, validator


class CreateConnectionRequest(BaseModel):
    """Schema for creating a new store connection."""

    name: str = Field(..., min_length=1, max_length=255, description="Connection name")
    platform: str = Field(..., description="Platform type (woocommerce, shopify)")
    store_url: str = Field(..., min_length=1, description="Store URL")
    api_key: str = Field(..., min_length=1, description="API key")
    api_secret: Optional[str] = Field(None, description="API secret (required for WooCommerce)")

    @validator('platform')
    def validate_platform(cls, v: str) -> str:
        """Validate platform is one of supported types."""
        allowed = ['woocommerce', 'shopify']
        if v.lower() not in allowed:
            raise ValueError(f"Platform must be one of: {', '.join(allowed)}")
        return v.lower()

    @validator('store_url')
    def validate_store_url(cls, v: str) -> str:
        """Ensure store_url is not empty."""
        if not v or not v.strip():
            raise ValueError("Store URL cannot be empty")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "name": "My WooCommerce Store",
                "platform": "woocommerce",
                "store_url": "https://mystore.com",
                "api_key": "ck_xxxxx",
                "api_secret": "cs_xxxxx"
            }
        }


class GetSuggestionsRequest(BaseModel):
    """Schema for getting suggestions query parameters."""

    product_id: int = Field(..., gt=0, description="Product ID")

    class Config:
        schema_extra = {
            "example": {
                "product_id": 1
            }
        }


class GetEventsRequest(BaseModel):
    """Schema for getting events query parameters."""

    limit: int = Field(20, ge=1, le=100, description="Number of events to retrieve")

    class Config:
        schema_extra = {
            "example": {
                "limit": 20
            }
        }
