package com.aiadviser.model;

import java.util.Map;

public record AdviceResponse(
    String sku,
    String analysis,
    Map<String, Object> recommendations,
    FinancialMetrics financialMetrics,
    String timestamp,
    Integer ttlHours
) {
}
