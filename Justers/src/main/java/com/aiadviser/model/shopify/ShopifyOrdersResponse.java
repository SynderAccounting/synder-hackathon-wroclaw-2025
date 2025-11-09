package com.aiadviser.model.shopify;

import java.util.List;

public record ShopifyOrdersResponse(
    List<ShopifyOrder> orders
) {}
