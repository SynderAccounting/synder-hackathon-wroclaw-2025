package com.aiadviser.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ProductData(
    Long id,
    String sku,
    String productName,
    BigDecimal cogs,
    Integer leadTimeDays,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {
    public ProductData(String sku, String productName, BigDecimal cogs, Integer leadTimeDays) {
        this(null, sku, productName, cogs, leadTimeDays, null, null);
    }
}
