from typing import List, Optional

from pydantic import BaseModel


class ShopifyVariant(BaseModel):
    id: Optional[int] = None
    product_id: Optional[int] = None
    title: Optional[str] = None
    price: Optional[str] = None
    position: Optional[int] = None
    inventory_policy: Optional[str] = None
    compare_at_price: Optional[str] = None
    option1: Optional[str] = None
    option2: Optional[str] = None
    option3: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    taxable: Optional[bool] = None
    barcode: Optional[str] = None
    fulfillment_service: Optional[str] = None
    grams: Optional[int] = None
    inventory_management: Optional[str] = None
    requires_shipping: Optional[bool] = None
    sku: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    inventory_item_id: Optional[int] = None
    inventory_quantity: Optional[int] = None
    old_inventory_quantity: Optional[int] = None
    admin_graphql_api_id: Optional[str] = None
    image_id: Optional[str] = None


class ShopifySchema(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    body_html: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    created_at: Optional[str] = None
    handle: Optional[str] = None
    updated_at: Optional[str] = None
    published_at: Optional[str] = None
    template_suffix: Optional[str] = None
    published_scope: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    admin_graphql_api_id: Optional[str] = None
    variants: List[ShopifyVariant] = []
