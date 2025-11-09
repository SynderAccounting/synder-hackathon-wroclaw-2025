package com.aiadviser.model.shopify;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ShopifyCustomer(
    Long id,
    
    String email,
    
    @JsonProperty("first_name")
    String firstName,
    
    @JsonProperty("last_name")
    String lastName,
    
    @JsonProperty("orders_count")
    Integer ordersCount,
    
    @JsonProperty("total_spent")
    String totalSpent,
    
    @JsonProperty("verified_email")
    Boolean verifiedEmail,
    
    String phone
) {}
