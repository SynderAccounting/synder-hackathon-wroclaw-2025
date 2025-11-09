package com.aiadviser.model;

import java.math.BigDecimal;

public record FinancialMetrics(
    BigDecimal expectedRevenue,
    BigDecimal expectedProfit,
    BigDecimal carryingCost,
    BigDecimal stockoutLoss,
    BigDecimal opportunityCost,
    String assumptions
) {
}
