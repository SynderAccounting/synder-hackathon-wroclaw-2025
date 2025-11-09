package com.aiadviser.model;

import java.math.BigDecimal;
import java.util.List;

public record LLMInputData(
    String sku,
    String productName,
    BigDecimal cogs,
    Integer leadTimeDays,
    List<SaleData> recentSales,
    StockData currentStock
) {
}
