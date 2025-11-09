package com.aiadviser.service;

import com.aiadviser.client.BaselinkerClient;
import com.aiadviser.client.ShopifyClient;
import com.aiadviser.model.ProductData;
import com.aiadviser.model.ProductSummary;
import com.aiadviser.model.baselinker.BaselinkerProduct;
import com.aiadviser.model.baselinker.BaselinkerProductsResponse;
import com.aiadviser.model.shopify.ShopifyLineItem;
import com.aiadviser.model.shopify.ShopifyOrder;
import com.aiadviser.model.shopify.ShopifyOrdersResponse;
import com.aiadviser.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Service
public class ProductSummaryService {

    private static final Logger log = LoggerFactory.getLogger(ProductSummaryService.class);
    
    private final ProductRepository productRepository;
    private final ShopifyClient shopifyClient;
    private final BaselinkerClient baselinkerClient;

    public ProductSummaryService(
            ProductRepository productRepository,
            ShopifyClient shopifyClient,
            BaselinkerClient baselinkerClient
    ) {
        this.productRepository = productRepository;
        this.shopifyClient = shopifyClient;
        this.baselinkerClient = baselinkerClient;
    }

    public List<ProductSummary> getAllProductSummaries() {
        List<ProductData> products = productRepository.findAll();
        List<ProductSummary> summaries = new ArrayList<>();

        for (ProductData product : products) {
            try {
                ProductSummary summary = createProductSummary(product);
                summaries.add(summary);
            } catch (Exception e) {
                log.warn("Failed to create summary for product {}: {}", product.sku(), e.getMessage());
                summaries.add(new ProductSummary(
                    product.id(),
                    product.sku(),
                    product.productName(),
                    product.cogs(),
                    product.leadTimeDays(),
                    product.createdAt(),
                    product.updatedAt(),
                    0,
                    0,
                    BigDecimal.ZERO
                ));
            }
        }

        return summaries;
    }

    private ProductSummary createProductSummary(ProductData product) {
        Integer stockQuantity = getStockQuantity(product.sku());
        
        ShopifyOrdersResponse ordersResponse = shopifyClient.fetchOrdersForSku(product.sku(), 30);
        
        int totalQuantitySold = 0;
        BigDecimal totalRevenue = BigDecimal.ZERO;
        
        for (ShopifyOrder order : ordersResponse.orders()) {
            for (ShopifyLineItem lineItem : order.lineItems()) {
                if (product.sku().equals(lineItem.sku())) {
                    int quantity = lineItem.quantity();
                    BigDecimal unitPrice = new BigDecimal(lineItem.price());
                    
                    totalQuantitySold += quantity;
                    totalRevenue = totalRevenue.add(unitPrice.multiply(BigDecimal.valueOf(quantity)));
                }
            }
        }
        
        BigDecimal totalCost = product.cogs().multiply(BigDecimal.valueOf(totalQuantitySold));
        BigDecimal monthlyProfit = totalRevenue.subtract(totalCost);

        return new ProductSummary(
            product.id(),
            product.sku(),
            product.productName(),
            product.cogs(),
            product.leadTimeDays(),
            product.createdAt(),
            product.updatedAt(),
            stockQuantity,
            totalQuantitySold,
            monthlyProfit
        );
    }

    private Integer getStockQuantity(String sku) {
        try {
            BaselinkerProductsResponse response = baselinkerClient.fetchInventoryProductData(sku);
            
            if (!"SUCCESS".equals(response.status())) {
                return 0;
            }

            if (response.products() == null || response.products().isEmpty()) {
                return 0;
            }

            BaselinkerProduct product = response.products().values().stream()
                .filter(p -> sku.equals(p.sku()))
                .findFirst()
                .orElse(null);

            if (product == null || product.stock() == null) {
                return 0;
            }

            return product.stock().values().stream()
                .mapToInt(Integer::intValue)
                .sum();
                
        } catch (Exception e) {
            log.warn("Failed to fetch stock for {}: {}", sku, e.getMessage());
            return 0;
        }
    }
}
