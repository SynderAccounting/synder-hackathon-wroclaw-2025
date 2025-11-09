package com.aiadviser.client;

import com.aiadviser.config.BaselinkerConfig;
import com.aiadviser.model.baselinker.BaselinkerProduct;
import com.aiadviser.model.baselinker.BaselinkerProductsResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

@Component
public class BaselinkerClient {

    private static final Logger log = LoggerFactory.getLogger(BaselinkerClient.class);
    private final Random random = new Random();
    private final BaselinkerConfig config;

    public BaselinkerClient(BaselinkerConfig config) {
        this.config = config;
        log.info("BaselinkerClient initialized with base URL: {}", config.getBaseUrl());
    }

    /**
     * Fetches ALL products from Baselinker inventory (stub implementation)
     * In real API: call getInventoryProductsList to get all products
     */
    public BaselinkerProductsResponse fetchAllProducts() {
        Map<String, BaselinkerProduct> allProducts = new HashMap<>();
        
        String[] productNames = {
            "Premium Wireless Headphones",
            "Smart Watch Pro",
            "USB-C Cable 2m",
            "Bluetooth Speaker",
            "Laptop Stand Aluminum"
        };
        
        String[] skus = {
            "SKU-001",
            "SKU-002", 
            "SKU-003",
            "SKU-004",
            "SKU-005"
        };
        
        for (int i = 0; i < productNames.length; i++) {
            String productId = String.valueOf(10000 + i);
            String sku = skus[i];
            int baseStock = random.nextInt(150) + 10;
            
            Map<String, Integer> stock = new HashMap<>();
            stock.put("bl_1234", baseStock);
            stock.put("bl_5678", random.nextInt(50));
            
            Map<String, String> locations = new HashMap<>();
            locations.put("bl_1234", "A-" + (i + 1) + "-01");
            locations.put("bl_5678", "B-" + (i + 1) + "-02");
            
            BaselinkerProduct product = new BaselinkerProduct(
                productId,
                "590" + random.nextInt(9) + String.format("%09d", random.nextInt(1000000000)),
                sku,
                productNames[i],
                baseStock,
                (50.0 + (i * 20)) + random.nextDouble() * 50,
                (30.0 + (i * 15)) + random.nextDouble() * 30,
                23,
                0.5 + (random.nextDouble() * 2),
                "Professional quality " + productNames[i].toLowerCase(),
                "TechBrand " + ((i % 3) + 1),
                100 + (i * 10),
                List.of(
                    "https://example.com/images/" + sku + "-1.jpg",
                    "https://example.com/images/" + sku + "-2.jpg"
                ),
                stock,
                locations,
                15.0 + (i * 3),
                10.0 + (i * 2),
                25.0 + (i * 5),
                random.nextInt(2),
                (i % 3) + 1
            );
            
            allProducts.put(productId, product);
        }
        
        return new BaselinkerProductsResponse("SUCCESS", allProducts);
    }

    /**
     * Fetches product inventory data from Baselinker API (stub implementation)
     * Returns realistic Baselinker API structure matching real API response
     */
    public BaselinkerProductsResponse fetchInventoryProductData(String sku) {
        int quantity = random.nextInt(100) + 10;
        String productId = String.valueOf(10000 + random.nextInt(90000));
        
        Map<String, Integer> stock = new HashMap<>();
        stock.put("bl_1234", quantity);
        stock.put("bl_5678", random.nextInt(50));
        
        Map<String, String> locations = new HashMap<>();
        locations.put("bl_1234", "A-" + (random.nextInt(10) + 1) + "-" + (random.nextInt(20) + 1));
        locations.put("bl_5678", "B-" + (random.nextInt(10) + 1) + "-" + (random.nextInt(20) + 1));
        
        BaselinkerProduct product = new BaselinkerProduct(
            productId,
            "590" + random.nextInt(9) + String.format("%09d", random.nextInt(1000000000)),
            sku,
            "Sample Product Name",
            quantity,
            99.99 + (random.nextDouble() * 100),
            75.00 + (random.nextDouble() * 50),
            23,
            1.5 + (random.nextDouble() * 2),
            "Full product description for " + sku,
            "Manufacturer " + (random.nextInt(10) + 1),
            100 + random.nextInt(50),
            List.of(
                "https://example.com/images/" + sku + "-1.jpg",
                "https://example.com/images/" + sku + "-2.jpg"
            ),
            stock,
            locations,
            20.0 + (random.nextDouble() * 10),
            15.0 + (random.nextDouble() * 10),
            30.0 + (random.nextDouble() * 20),
            random.nextInt(2),
            random.nextInt(20) + 1
        );
        
        Map<String, BaselinkerProduct> products = new HashMap<>();
        products.put(productId, product);
        
        return new BaselinkerProductsResponse("SUCCESS", products);
    }
}
