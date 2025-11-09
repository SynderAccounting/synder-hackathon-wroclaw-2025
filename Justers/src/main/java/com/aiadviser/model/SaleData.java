package com.aiadviser.model;

import java.math.BigDecimal;
import java.time.LocalDate;

public record SaleData(
    LocalDate date,
    Integer quantity,
    BigDecimal unitPrice,
    BigDecimal totalAmount
) {
}
