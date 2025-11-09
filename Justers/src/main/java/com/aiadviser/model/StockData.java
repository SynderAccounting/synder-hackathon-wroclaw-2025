package com.aiadviser.model;

public record StockData(
    String sku,
    Integer quantity,
    String warehouse
) {
}
