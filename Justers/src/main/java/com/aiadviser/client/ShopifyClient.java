package com.aiadviser.client;

import com.aiadviser.config.ShopifyConfig;
import com.aiadviser.model.shopify.ShopifyCustomer;
import com.aiadviser.model.shopify.ShopifyLineItem;
import com.aiadviser.model.shopify.ShopifyOrder;
import com.aiadviser.model.shopify.ShopifyOrdersResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

@Component
public class ShopifyClient {

    private static final Logger log = LoggerFactory.getLogger(ShopifyClient.class);
    private final Random random = new Random();
    private static final DateTimeFormatter ISO_FORMATTER = DateTimeFormatter.ISO_DATE_TIME;
    private final ShopifyConfig config;

    public ShopifyClient(ShopifyConfig config) {
        this.config = config;
        log.info("ShopifyClient initialized with base URL: {}", config.getBaseUrl());
    }

    /**
     * Fetches orders from Shopify API (stub implementation)
     * Returns realistic Shopify API structure matching real API response
     */
    public ShopifyOrdersResponse fetchOrdersForSku(String sku, int days) {
        List<ShopifyOrder> orders = new ArrayList<>();
        LocalDate today = LocalDate.now();

        for (int i = 0; i < days; i++) {
            LocalDate orderDate = today.minusDays(i);
            int quantity = random.nextInt(5) + 1;
            double unitPrice = 99.99 + (random.nextDouble() * 50);
            double subtotal = unitPrice * quantity;
            double tax = subtotal * 0.08;
            double total = subtotal + tax;

            ShopifyCustomer customer = new ShopifyCustomer(
                1000000000L + random.nextInt(1000000),
                "customer" + i + "@example.com",
                "John",
                "Doe",
                random.nextInt(10) + 1,
                String.format("%.2f", total * 2),
                true,
                "+1234567890"
            );

            ShopifyLineItem lineItem = new ShopifyLineItem(
                2000000000L + random.nextInt(1000000),
                3000000000L + random.nextInt(1000000),
                4000000000L + random.nextInt(1000000),
                "Product Name",
                "Default Variant",
                sku,
                "Test Vendor",
                quantity,
                String.format("%.2f", unitPrice),
                500 + random.nextInt(1000),
                true,
                true,
                null,
                "Product Name - Default Variant"
            );

            ShopifyOrder order = new ShopifyOrder(
                5000000000L + random.nextInt(1000000),
                "#" + (1000 + i),
                1000 + i,
                orderDate.atTime(10, random.nextInt(60)).format(ISO_FORMATTER),
                orderDate.atTime(10, random.nextInt(60)).format(ISO_FORMATTER),
                "USD",
                String.format("%.2f", total),
                String.format("%.2f", subtotal),
                String.format("%.2f", tax),
                random.nextBoolean() ? "paid" : "pending",
                random.nextBoolean() ? "fulfilled" : null,
                List.of(lineItem),
                customer,
                customer.email()
            );

            orders.add(order);
        }

        return new ShopifyOrdersResponse(orders);
    }
}
