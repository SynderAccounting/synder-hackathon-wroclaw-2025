package com.aiadviser.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import org.mockserver.integration.ClientAndServer;
import org.mockserver.matchers.Times;
import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;

import java.util.*;

import static org.mockserver.model.HttpRequest.request;
import static org.mockserver.model.HttpResponse.response;

@Configuration
@Profile("demo")
@ConditionalOnProperty(name = "mockserver.enabled", havingValue = "true")
public class MockServerConfiguration {

    private static final Logger log = LoggerFactory.getLogger(MockServerConfiguration.class);
    private ClientAndServer mockServer;
    private final MockServerConfig config;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Random random = new Random();

    public MockServerConfiguration(MockServerConfig config) {
        this.config = config;
    }

    @PostConstruct
    public void startMockServer() {
        log.info("Starting MockServer on port {}...", config.getPort());
        mockServer = ClientAndServer.startClientAndServer(config.getPort());
        setupMockExpectations();
        log.info("MockServer started successfully with dynamic random data generation");
    }

    @PreDestroy
    public void stopMockServer() {
        if (mockServer != null && mockServer.isRunning()) {
            log.info("Stopping MockServer...");
            mockServer.stop();
            log.info("MockServer stopped");
        }
    }

    private void setupMockExpectations() {
        setupBaselinkerMocks();
        setupShopifyMocks();
        setupClaudeMocks();
    }

    private void setupBaselinkerMocks() {
        log.info("Setting up Baselinker mock expectations with random data generation...");
        
        mockServer
            .when(
                request()
                    .withMethod("POST")
                    .withPath("/connector.php"),
                Times.unlimited()
            )
            .respond(
                httpRequest -> {
                    try {
                        Map<String, Object> response = generateRandomBaselinkerResponse();
                        String json = objectMapper.writeValueAsString(response);
                        return response()
                            .withStatusCode(200)
                            .withHeader("Content-Type", "application/json; charset=utf-8")
                            .withBody(json);
                    } catch (Exception e) {
                        log.error("Error generating Baselinker response", e);
                        return response().withStatusCode(500);
                    }
                }
            );
        
        log.info("Baselinker dynamic mocks configured");
    }

    private void setupShopifyMocks() {
        log.info("Setting up Shopify mock expectations with random data generation...");
        
        mockServer
            .when(
                request()
                    .withMethod("GET")
                    .withPath("/admin/api/.*"),
                Times.unlimited()
            )
            .respond(
                httpRequest -> {
                    try {
                        Map<String, Object> response = generateRandomShopifyResponse();
                        String json = objectMapper.writeValueAsString(response);
                        return response()
                            .withStatusCode(200)
                            .withHeader("Content-Type", "application/json; charset=utf-8")
                            .withBody(json);
                    } catch (Exception e) {
                        log.error("Error generating Shopify response", e);
                        return response().withStatusCode(500);
                    }
                }
            );
        
        log.info("Shopify dynamic mocks configured");
    }

    private void setupClaudeMocks() {
        log.info("Setting up Claude mock expectations with random data generation...");
        
        mockServer
            .when(
                request()
                    .withMethod("POST")
                    .withPath("/v1/messages"),
                Times.unlimited()
            )
            .respond(
                httpRequest -> {
                    try {
                        String requestBody = httpRequest.getBodyAsString();
                        boolean isChatRequest = requestBody != null && 
                            (requestBody.contains("How can I help") || 
                             requestBody.contains("explain") ||
                             requestBody.contains("What") ||
                             requestBody.contains("Why") ||
                             !requestBody.contains("JSON format"));
                        
                        Map<String, Object> response;
                        if (isChatRequest) {
                            response = generateRandomChatResponse(requestBody);
                        } else {
                            response = generateRandomClaudeResponse();
                        }
                        
                        String json = objectMapper.writeValueAsString(response);
                        return response()
                            .withStatusCode(200)
                            .withHeader("Content-Type", "application/json; charset=utf-8")
                            .withBody(json);
                    } catch (Exception e) {
                        log.error("Error generating Claude response", e);
                        return response().withStatusCode(500);
                    }
                }
            );
        
        log.info("Claude dynamic mocks configured for recommendations and chat");
    }

    private Map<String, Object> generateRandomBaselinkerResponse() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "SUCCESS");
        
        Map<String, Map<String, Object>> products = new HashMap<>();
        
        String[] productNames = {
            "Premium Wireless Headphones",
            "Smart Watch Pro",
            "USB-C Cable 2m",
            "Bluetooth Speaker",
            "Laptop Stand Aluminum"
        };
        
        String[] skus = {"SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005"};
        
        for (int i = 0; i < productNames.length; i++) {
            String productId = String.valueOf(10000 + i);
            Map<String, Object> product = generateRandomProductData(productId, skus[i], productNames[i]);
            products.put(productId, product);
        }
        
        response.put("products", products);
        return response;
    }

    private Map<String, Object> generateRandomProductData(String productId, String sku, String name) {
        Map<String, Object> product = new HashMap<>();
        
        int stockLevel = pickRandomStockLevel();
        
        product.put("product_id", productId);
        product.put("ean", "590" + random.nextInt(9) + String.format("%09d", random.nextInt(1000000000)));
        product.put("sku", sku);
        product.put("name", name);
        product.put("quantity", stockLevel);
        
        double retailPrice = pickRandomRetailPrice();
        double cogs = pickRandomCOGS(retailPrice);
        
        product.put("price_brutto", retailPrice);
        product.put("price_wholesale_netto", cogs);
        product.put("tax_rate", 23);
        product.put("weight", 0.3 + (random.nextDouble() * 2.5));
        product.put("description", pickRandomDescription(name));
        product.put("manufacturer", pickRandomManufacturer());
        product.put("category_id", 100 + random.nextInt(50));
        product.put("images", List.of("https://example.com/images/" + sku + "-1.jpg"));
        
        int warehouse1Stock = (int)(stockLevel * (0.6 + random.nextDouble() * 0.3));
        int warehouse2Stock = stockLevel - warehouse1Stock;
        
        Map<String, Integer> stock = new HashMap<>();
        stock.put("bl_1234", warehouse1Stock);
        stock.put("bl_5678", warehouse2Stock);
        product.put("stock", stock);
        
        Map<String, String> locations = new HashMap<>();
        locations.put("bl_1234", pickRandomLocation('A'));
        locations.put("bl_5678", pickRandomLocation('B'));
        product.put("locations", locations);
        
        return product;
    }

    private int pickRandomStockLevel() {
        int[] stockLevels = {
            15, 23, 35, 42, 58, 67, 74, 88, 95, 103,
            112, 127, 134, 145, 156, 168, 175, 189, 198, 210
        };
        return stockLevels[random.nextInt(stockLevels.length)];
    }

    private double pickRandomRetailPrice() {
        double[] prices = {
            19.99, 29.99, 39.99, 49.99, 59.99,
            69.99, 79.99, 89.99, 99.99, 119.99,
            129.99, 149.99, 169.99, 189.99, 199.99,
            219.99, 239.99, 249.99, 279.99, 299.99
        };
        return prices[random.nextInt(prices.length)];
    }

    private double pickRandomCOGS(double retailPrice) {
        double[] marginPercentages = {
            0.35, 0.38, 0.40, 0.42, 0.45,
            0.48, 0.50, 0.52, 0.55, 0.58,
            0.60, 0.62, 0.65, 0.67, 0.70,
            0.72, 0.75, 0.77, 0.80, 0.82
        };
        double margin = marginPercentages[random.nextInt(marginPercentages.length)];
        return Math.round(retailPrice * margin * 100.0) / 100.0;
    }

    private String pickRandomDescription(String productName) {
        String[] adjectives = {
            "Premium quality", "Professional grade", "High-performance",
            "Cutting-edge", "Innovative", "Ergonomic", "Sleek and modern",
            "Industry-leading", "State-of-the-art", "Advanced technology",
            "Superior design", "Top-rated", "Award-winning", "Best-in-class",
            "Next-generation", "Ultra-durable", "Feature-rich", "Versatile",
            "Compact and powerful", "Stylish and functional"
        };
        String adjective = adjectives[random.nextInt(adjectives.length)];
        return adjective + " " + productName.toLowerCase() + " for modern consumers";
    }

    private String pickRandomManufacturer() {
        String[] manufacturers = {
            "TechCorp", "InnovateTech", "GlobalElectronics", "PrimeTech Solutions",
            "NextGen Industries", "Quantum Devices", "FutureTech", "Precision Manufacturing",
            "Elite Electronics", "ProTech Systems", "Advanced Components", "SmartTech Inc",
            "Digital Dynamics", "CoreTech", "Supreme Electronics", "VisionTech",
            "MegaTech Corp", "UltraTech", "PowerTech Solutions", "TechMasters"
        };
        return manufacturers[random.nextInt(manufacturers.length)];
    }

    private String pickRandomLocation(char warehouse) {
        String row = String.valueOf((char)('A' + random.nextInt(10)));
        int shelf = random.nextInt(20) + 1;
        int bin = random.nextInt(30) + 1;
        return warehouse + "-" + row + shelf + "-" + String.format("%02d", bin);
    }

    private Map<String, Object> generateRandomShopifyResponse() {
        Map<String, Object> response = new HashMap<>();
        List<Map<String, Object>> orders = new ArrayList<>();
        
        for (int i = 0; i < 5; i++) {
            orders.add(generateRandomShopifyOrder(i));
        }
        
        response.put("orders", orders);
        return response;
    }

    private Map<String, Object> generateRandomShopifyOrder(int index) {
        Map<String, Object> order = new HashMap<>();
        
        long baseOrderId = 5000000000L + random.nextInt(1000000);
        int orderNumber = 1000 + index;
        
        order.put("id", baseOrderId);
        order.put("name", "#" + orderNumber);
        order.put("order_number", orderNumber);
        order.put("created_at", "2024-11-0" + (1 + random.nextInt(8)) + "T10:30:00");
        order.put("updated_at", "2024-11-0" + (1 + random.nextInt(8)) + "T10:30:00");
        order.put("currency", "USD");
        
        int quantity = pickRandomOrderQuantity();
        double unitPrice = pickRandomRetailPrice();
        double subtotal = unitPrice * quantity;
        double tax = subtotal * 0.08;
        double total = subtotal + tax;
        
        order.put("total_price", String.format("%.2f", total));
        order.put("subtotal_price", String.format("%.2f", subtotal));
        order.put("total_tax", String.format("%.2f", tax));
        order.put("financial_status", pickRandomStatus());
        order.put("fulfillment_status", pickRandomFulfillmentStatus());
        
        Map<String, Object> customer = generateRandomCustomer();
        order.put("customer", customer);
        order.put("contact_email", customer.get("email"));
        
        List<Map<String, Object>> lineItems = List.of(
            generateRandomLineItem(quantity, unitPrice)
        );
        order.put("line_items", lineItems);
        
        return order;
    }

    private int pickRandomOrderQuantity() {
        int[] quantities = {1, 1, 2, 2, 3, 3, 4, 5, 5, 6, 7, 8, 10, 12, 15, 18, 20, 25, 30, 40};
        return quantities[random.nextInt(quantities.length)];
    }

    private String pickRandomStatus() {
        String[] statuses = {"paid", "paid", "paid", "pending", "refunded"};
        return statuses[random.nextInt(statuses.length)];
    }

    private String pickRandomFulfillmentStatus() {
        String[] statuses = {"fulfilled", "fulfilled", "partial", null, null};
        return statuses[random.nextInt(statuses.length)];
    }

    private Map<String, Object> generateRandomCustomer() {
        Map<String, Object> customer = new HashMap<>();
        customer.put("id", 1000000000L + random.nextInt(1000000));
        customer.put("email", "customer" + random.nextInt(1000) + "@example.com");
        customer.put("first_name", pickRandomFirstName());
        customer.put("last_name", pickRandomLastName());
        customer.put("orders_count", random.nextInt(20) + 1);
        customer.put("total_spent", String.format("%.2f", 100 + random.nextDouble() * 500));
        customer.put("verified_email", true);
        customer.put("phone", "+1" + (200 + random.nextInt(799)) + random.nextInt(9000000));
        return customer;
    }

    private String pickRandomFirstName() {
        String[] names = {"John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Lisa", 
                         "Robert", "Maria", "William", "Jennifer", "Richard", "Linda", "Thomas", 
                         "Patricia", "Daniel", "Nancy", "Matthew", "Barbara"};
        return names[random.nextInt(names.length)];
    }

    private String pickRandomLastName() {
        String[] names = {"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
                         "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", 
                         "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"};
        return names[random.nextInt(names.length)];
    }

    private Map<String, Object> generateRandomLineItem(int quantity, double unitPrice) {
        Map<String, Object> item = new HashMap<>();
        item.put("id", 2000000000L + random.nextInt(1000000));
        item.put("product_id", 3000000000L + random.nextInt(1000000));
        item.put("variant_id", 4000000000L + random.nextInt(1000000));
        item.put("name", "Product Name");
        item.put("variant_title", "Default Variant");
        item.put("sku", "SKU-00" + (random.nextInt(5) + 1));
        item.put("vendor", "Test Vendor");
        item.put("quantity", quantity);
        item.put("price", String.format("%.2f", unitPrice));
        item.put("grams", 500 + random.nextInt(1500));
        item.put("requires_shipping", true);
        item.put("taxable", true);
        item.put("gift_card", null);
        item.put("title", "Product Name - Default Variant");
        return item;
    }

    private Map<String, Object> generateRandomClaudeResponse() {
        Map<String, Object> response = new HashMap<>();
        response.put("id", "msg_demo_" + UUID.randomUUID().toString().substring(0, 8));
        response.put("type", "message");
        response.put("role", "assistant");
        
        Map<String, Object> recommendation = generateRandomAIRecommendation();
        String recommendationJson = convertToJsonString(recommendation);
        
        Map<String, Object> content = new HashMap<>();
        content.put("type", "text");
        content.put("text", recommendationJson);
        
        response.put("content", List.of(content));
        response.put("model", "claude-3-5-sonnet-20241022");
        response.put("stop_reason", "end_turn");
        
        Map<String, Integer> usage = new HashMap<>();
        usage.put("input_tokens", 200 + random.nextInt(100));
        usage.put("output_tokens", 80 + random.nextInt(50));
        response.put("usage", usage);
        
        return response;
    }

    private Map<String, Object> generateRandomAIRecommendation() {
        Map<String, Object> rec = new HashMap<>();
        
        String[] decisions = {"yes", "yes", "yes", "no", "monitor"};
        String decision = decisions[random.nextInt(decisions.length)];
        rec.put("reorderRecommendation", decision);
        
        int[] quantities = {50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 
                           400, 450, 500, 600, 750, 800, 1000, 1200, 1500, 2000};
        rec.put("suggestedOrderQuantity", quantities[random.nextInt(quantities.length)]);
        
        String[] risks = {"low", "low", "medium", "medium", "medium", "high"};
        rec.put("stockoutRisk", risks[random.nextInt(risks.length)]);
        
        int[] daysUntilStockout = {7, 10, 14, 15, 21, 25, 30, 35, 40, 45, 50, 
                                   60, 70, 75, 90, 100, 120, 150, 180, 200};
        rec.put("daysUntilStockout", daysUntilStockout[random.nextInt(daysUntilStockout.length)]);
        
        String[] reasonings = {
            "Based on current stock levels and sales velocity, recommend reordering to maintain optimal inventory levels and prevent stockouts.",
            "Current inventory levels are healthy. Monitor sales trends over the next 2 weeks before placing a new order.",
            "High sales velocity detected. Immediate reorder recommended to avoid stockout within the lead time window.",
            "Stock levels are adequate for current demand. Consider reordering in 3-4 weeks based on seasonal trends.",
            "Critical stock level approaching. Place urgent order to prevent service disruption to customers.",
            "Stable sales pattern observed. Standard reorder quantity will maintain 60-day supply buffer.",
            "Demand spike detected in recent weeks. Increase order quantity to capture growth opportunity.",
            "Slow-moving inventory. Reduce order quantity and evaluate product performance before next cycle.",
            "Lead time exceeds current runway. Priority order needed to bridge the gap until next shipment arrives.",
            "Optimal stock rotation achieved. Continue current ordering pattern to maximize inventory turnover.",
            "Seasonal demand increase anticipated. Proactive restocking recommended to prepare for peak period.",
            "Inventory aging analysis suggests reducing order frequency. Switch to smaller, more frequent orders.",
            "Strong correlation between marketing campaigns and sales. Align reorder timing with promotional calendar.",
            "Competitor pricing pressure detected. Maintain higher stock levels to support aggressive pricing strategy.",
            "Supply chain disruptions possible. Build safety stock buffer by ordering additional units now.",
            "Product lifecycle entering maturity phase. Standard reorder maintains market presence without excess.",
            "New product launch momentum strong. Aggressive restocking supports continued growth trajectory.",
            "Customer reviews indicate quality satisfaction. Steady reordering supports brand reputation.",
            "Multi-channel sales distribution balanced. Current inventory allocation strategy performing well.",
            "Data-driven forecast indicates stable demand. Recommended order quantity optimizes carrying costs."
        };
        rec.put("reasoning", reasonings[random.nextInt(reasonings.length)]);
        
        int[] ttlHoursOptions = {3, 6, 12, 24, 48, 72};
        rec.put("ttlHours", ttlHoursOptions[random.nextInt(ttlHoursOptions.length)]);
        
        return rec;
    }

    private Map<String, Object> generateRandomChatResponse(String requestBody) {
        Map<String, Object> response = new HashMap<>();
        response.put("id", "msg_chat_" + UUID.randomUUID().toString().substring(0, 8));
        response.put("type", "message");
        response.put("role", "assistant");
        
        String chatResponseText = generateRandomChatText(requestBody);
        
        Map<String, Object> content = new HashMap<>();
        content.put("type", "text");
        content.put("text", chatResponseText);
        
        response.put("content", List.of(content));
        response.put("model", "claude-3-5-sonnet-20241022");
        response.put("stop_reason", "end_turn");
        
        Map<String, Integer> usage = new HashMap<>();
        usage.put("input_tokens", 150 + random.nextInt(100));
        usage.put("output_tokens", 100 + random.nextInt(80));
        response.put("usage", usage);
        
        return response;
    }

    private String generateRandomChatText(String requestBody) {
        String[] responses = {
            "Based on the sales data and lead time, I'd recommend placing an order soon. The current stock levels show a healthy buffer, but with consistent daily sales, you'll want to reorder before hitting your safety stock threshold. This ensures you maintain service levels without tying up too much capital in inventory.",
            
            "Looking at the velocity and COGS, this product shows strong performance. The key consideration here is balancing order frequency with carrying costs. Given the 7-14 day lead time, I'd suggest maintaining a 30-45 day supply on hand to buffer against demand variability.",
            
            "The stockout risk depends largely on your sales consistency. If sales remain stable at current levels, you have adequate runway. However, if you're planning promotions or seasonal increases, you'll want to order proactively. Safety stock calculations suggest keeping at least 2 weeks of buffer above your lead time demand.",
            
            "This is a great question about inventory optimization. The relationship between lead time and order quantity is critical. With your current COGS and sales velocity, ordering in larger quantities reduces your ordering frequency costs, but ties up more capital. The sweet spot is typically 1.5-2x your lead time demand.",
            
            "Consider the total cost of ownership here. While ordering larger quantities gives you better unit economics, you need to factor in carrying costs, storage, and capital tied up. For products with consistent demand like this, I'd recommend ordering every 3-4 weeks to balance these factors.",
            
            "The data shows stable demand patterns, which is excellent for planning. Your current inventory position gives you flexibility. I'd recommend monitoring the next 7 days of sales closely - if the trend continues, placing an order around day 10-12 would be optimal timing.",
            
            "Great insight! Lead time variability is indeed a risk factor. Given standard supply chain uncertainties, I'd recommend building in a safety buffer of about 20-30% above your calculated reorder point. This protects against both demand spikes and supply delays.",
            
            "The COGS relative to your selling price indicates healthy margins, which gives you room for strategic inventory decisions. You could afford to carry slightly more stock to ensure availability, or optimize for cash flow with just-in-time ordering. Your competitive position should guide this choice.",
            
            "Looking at the broader picture, this product's performance justifies maintaining strong stock levels. The combination of consistent sales and reasonable COGS makes it a core SKU. I'd treat it as a priority for stock availability rather than minimizing inventory investment.",
            
            "That's a strategic question. If you're seeing growth trends, increasing your order quantity now could position you well. However, ensure your cash flow can support the larger inventory investment. A phased approach - gradually increasing order sizes as sales confirm the trend - often works best."
        };
        
        return responses[random.nextInt(responses.length)];
    }

    private String convertToJsonString(Map<String, Object> map) {
        try {
            return objectMapper.writeValueAsString(map);
        } catch (Exception e) {
            log.error("Error converting map to JSON string", e);
            return "{}";
        }
    }
}
