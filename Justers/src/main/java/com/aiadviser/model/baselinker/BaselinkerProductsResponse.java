package com.aiadviser.model.baselinker;

import java.util.Map;

public record BaselinkerProductsResponse(
    String status,
    Map<String, BaselinkerProduct> products
) {}
