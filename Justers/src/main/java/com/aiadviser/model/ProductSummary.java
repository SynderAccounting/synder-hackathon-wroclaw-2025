package com.aiadviser.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ProductSummary(
    Long id,
    String sku,
    String productName,
    BigDecimal cogs,
    Integer leadTimeDays,
    LocalDateTime createdAt,
    LocalDateTime updatedAt,
    Integer stockQuantity,
    Integer monthlySales,
    BigDecimal monthlyProfit
) {
}
