package com.aiadviser.model.shopify;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;
import java.util.List;

public record ShopifyOrder(
    Long id,
    String name,
    
    @JsonProperty("order_number")
    Integer orderNumber,
    
    @JsonProperty("created_at")
    String createdAt,
    
    @JsonProperty("updated_at")
    String updatedAt,
    
    String currency,
    
    @JsonProperty("total_price")
    String totalPrice,
    
    @JsonProperty("subtotal_price")
    String subtotalPrice,
    
    @JsonProperty("total_tax")
    String totalTax,
    
    @JsonProperty("financial_status")
    String financialStatus,
    
    @JsonProperty("fulfillment_status")
    String fulfillmentStatus,
    
    @JsonProperty("line_items")
    List<ShopifyLineItem> lineItems,
    
    ShopifyCustomer customer,
    
    String email
) {}
