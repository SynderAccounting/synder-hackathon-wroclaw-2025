package com.aiadviser.service;

import com.aiadviser.client.BaselinkerClient;
import com.aiadviser.client.ShopifyClient;
import com.aiadviser.model.LLMInputData;
import com.aiadviser.model.ProductData;
import com.aiadviser.model.SaleData;
import com.aiadviser.model.StockData;
import com.aiadviser.model.baselinker.BaselinkerProduct;
import com.aiadviser.model.baselinker.BaselinkerProductsResponse;
import com.aiadviser.model.shopify.ShopifyLineItem;
import com.aiadviser.model.shopify.ShopifyOrder;
import com.aiadviser.model.shopify.ShopifyOrdersResponse;
import com.aiadviser.repository.ProductRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class DataAggregatorService {

    private final ShopifyClient shopifyClient;
    private final BaselinkerClient baselinkerClient;
    private final ProductRepository productRepository;

    public DataAggregatorService(
            ShopifyClient shopifyClient,
            BaselinkerClient baselinkerClient,
            ProductRepository productRepository
    ) {
        this.shopifyClient = shopifyClient;
        this.baselinkerClient = baselinkerClient;
        this.productRepository = productRepository;
    }

    /**
     * Aggregates data from multiple sources for LLM analysis
     * Parses real API structures from Shopify and Baselinker
     */
    public LLMInputData aggregateDataForLLM(String sku) {
        ProductData product = productRepository.findBySku(sku)
            .orElseThrow(() -> new RuntimeException("Product not found: " + sku));

        List<SaleData> recentSales = parseShopifyOrders(sku, 30);
        StockData currentStock = parseBaselinkerInventory(sku);

        return new LLMInputData(
            product.sku(),
            product.productName(),
            product.cogs(),
            product.leadTimeDays(),
            recentSales,
            currentStock
        );
    }

    /**
     * Fetches and parses Shopify orders into SaleData
     */
    private List<SaleData> parseShopifyOrders(String sku, int days) {
        ShopifyOrdersResponse response = shopifyClient.fetchOrdersForSku(sku, days);
        List<SaleData> sales = new ArrayList<>();

        for (ShopifyOrder order : response.orders()) {
            LocalDate saleDate = parseShopifyDate(order.createdAt());
            
            for (ShopifyLineItem lineItem : order.lineItems()) {
                if (sku.equals(lineItem.sku())) {
                    BigDecimal unitPrice = new BigDecimal(lineItem.price());
                    int quantity = lineItem.quantity();
                    BigDecimal totalAmount = unitPrice.multiply(BigDecimal.valueOf(quantity));
                    
                    sales.add(new SaleData(saleDate, quantity, unitPrice, totalAmount));
                }
            }
        }

        return sales;
    }

    /**
     * Fetches and parses Baselinker inventory into StockData
     * Filters products by SKU to handle multi-product responses
     */
    private StockData parseBaselinkerInventory(String sku) {
        BaselinkerProductsResponse response = baselinkerClient.fetchInventoryProductData(sku);
        
        if (!"SUCCESS".equals(response.status())) {
            throw new RuntimeException("Baselinker API error: " + response.status());
        }

        if (response.products() == null || response.products().isEmpty()) {
            throw new RuntimeException("No products returned from Baselinker for SKU: " + sku);
        }

        BaselinkerProduct product = response.products().values().stream()
            .filter(p -> sku.equals(p.sku()))
            .findFirst()
            .orElseThrow(() -> new RuntimeException("Product with SKU " + sku + " not found in Baselinker response"));

        if (product.stock() == null || product.stock().isEmpty()) {
            return new StockData(sku, 0, "No warehouse stock data available");
        }

        int totalQuantity = product.stock().values().stream()
            .mapToInt(Integer::intValue)
            .sum();

        String warehouseInfo = buildWarehouseInfo(product.stock(), product.locations());

        return new StockData(sku, totalQuantity, warehouseInfo);
    }

    private LocalDate parseShopifyDate(String dateString) {
        return LocalDate.parse(dateString.substring(0, 10));
    }

    private String buildWarehouseInfo(Map<String, Integer> stock, Map<String, String> locations) {
        StringBuilder info = new StringBuilder();
        stock.forEach((warehouse, qty) -> {
            String location = locations.getOrDefault(warehouse, "Unknown");
            if (info.length() > 0) info.append(", ");
            info.append(warehouse).append(" (").append(location).append("): ").append(qty);
        });
        return info.toString();
    }
}
