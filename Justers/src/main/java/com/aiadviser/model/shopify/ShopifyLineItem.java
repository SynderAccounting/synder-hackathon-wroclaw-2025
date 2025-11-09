package com.aiadviser.model.shopify;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ShopifyLineItem(
    Long id,
    
    @JsonProperty("product_id")
    Long productId,
    
    @JsonProperty("variant_id")
    Long variantId,
    
    String title,
    
    @JsonProperty("variant_title")
    String variantTitle,
    
    String sku,
    
    String vendor,
    
    Integer quantity,
    
    String price,
    
    Integer grams,
    
    @JsonProperty("requires_shipping")
    Boolean requiresShipping,
    
    Boolean taxable,
    
    @JsonProperty("fulfillment_status")
    String fulfillmentStatus,
    
    String name
) {}
