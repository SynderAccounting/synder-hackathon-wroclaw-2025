package com.aiadviser.service;

import com.aiadviser.client.BaselinkerClient;
import com.aiadviser.client.ShopifyClient;
import com.aiadviser.model.ProductData;
import com.aiadviser.model.baselinker.BaselinkerProduct;
import com.aiadviser.model.baselinker.BaselinkerProductsResponse;
import com.aiadviser.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

@Service
public class DataSyncService {

    private static final Logger log = LoggerFactory.getLogger(DataSyncService.class);

    private final ShopifyClient shopifyClient;
    private final BaselinkerClient baselinkerClient;
    private final ProductRepository productRepository;

    public DataSyncService(
            ShopifyClient shopifyClient,
            BaselinkerClient baselinkerClient,
            ProductRepository productRepository
    ) {
        this.shopifyClient = shopifyClient;
        this.baselinkerClient = baselinkerClient;
        this.productRepository = productRepository;
    }

    public void syncProductsFromExternalSources() {
        log.info("Starting product synchronization from Baselinker (fetching all products)...");

        int syncedCount = 0;
        int errorCount = 0;

        try {
            BaselinkerProductsResponse response = baselinkerClient.fetchAllProducts();
            
            if (!"SUCCESS".equals(response.status())) {
                log.error("Baselinker API returned status: {}", response.status());
                return;
            }

            if (response.products() == null || response.products().isEmpty()) {
                log.warn("No products returned from Baselinker");
                return;
            }

            log.info("Fetched {} products from Baselinker", response.products().size());

            for (BaselinkerProduct baselinkerProduct : response.products().values()) {
                try {
                    syncProduct(baselinkerProduct);
                    syncedCount++;
                    log.info("Successfully synced product: {} - {}", 
                        baselinkerProduct.sku(), baselinkerProduct.name());
                } catch (Exception e) {
                    errorCount++;
                    log.error("Failed to sync product {}: {}", 
                        baselinkerProduct.sku(), e.getMessage(), e);
                }
            }

            log.info("Product synchronization completed. Synced: {}, Errors: {}", syncedCount, errorCount);
        } catch (Exception e) {
            log.error("Failed to fetch products from Baselinker: {}", e.getMessage(), e);
        }
    }

    private void syncProduct(BaselinkerProduct baselinkerProduct) {
        BigDecimal cogs = baselinkerProduct.priceWholesaleNetto() != null 
            ? BigDecimal.valueOf(baselinkerProduct.priceWholesaleNetto())
            : BigDecimal.ZERO;

        int leadTimeDays = calculateLeadTime(baselinkerProduct);

        ProductData productData = new ProductData(
            null,
            baselinkerProduct.sku(),
            baselinkerProduct.name(),
            cogs,
            leadTimeDays,
            null,
            null
        );

        productRepository.upsertBySku(productData);
    }

    private int calculateLeadTime(BaselinkerProduct product) {
        if (product.stock() != null && !product.stock().isEmpty()) {
            int totalStock = product.stock().values().stream()
                .mapToInt(Integer::intValue)
                .sum();
            
            if (totalStock > 100) return 7;
            if (totalStock > 50) return 14;
            return 21;
        }
        return 30;
    }
}
