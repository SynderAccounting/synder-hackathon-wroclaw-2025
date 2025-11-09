package com.aiadviser.service;

import com.aiadviser.config.ClaudeConfig;
import com.aiadviser.model.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class ClaudeService {

    private static final Logger log = LoggerFactory.getLogger(ClaudeService.class);
    private final WebClient webClient;
    private final ClaudeConfig config;
    private final ObjectMapper objectMapper;

    public ClaudeService(
            ClaudeConfig config,
            WebClient.Builder webClientBuilder,
            ObjectMapper objectMapper
    ) {
        this.config = config;
        this.webClient = webClientBuilder
            .baseUrl(config.getBaseUrl())
            .defaultHeader("content-type", "application/json")
            .build();
        this.objectMapper = objectMapper;
        log.info("ClaudeService initialized with base URL: {}, model: {}", 
                 config.getBaseUrl(), config.getModel());
    }

    public Map<String, Object> analyzeProductData(LLMInputData inputData) {
        String prompt = buildAnalysisPrompt(inputData);

        ClaudeRequest request = new ClaudeRequest(
            config.getModel(),
            config.getMaxTokens(),
            List.of(new ClaudeRequest.Message("user", prompt))
        );

        try {
            ClaudeResponse response = webClient.post()
                .uri("/v1/messages")
                .header("x-api-key", config.getApiKey())
                .header("anthropic-version", config.getApiVersion())
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ClaudeResponse.class)
                .block();

            return parseResponse(response);
        } catch (Exception e) {
            log.error("Error calling Claude API: {}", e.getMessage());
            return Map.of(
                "error", "Failed to get AI analysis",
                "details", e.getMessage(),
                "reorderRecommendation", "error"
            );
        }
    }

    private String buildAnalysisPrompt(LLMInputData data) {
        StringBuilder sb = new StringBuilder();
        sb.append("Analyze the following product data and provide recommendations in JSON format.\n\n");
        sb.append("Product: ").append(data.productName()).append(" (").append(data.sku()).append(")\n");
        sb.append("Cost of Goods Sold (COGS): $").append(data.cogs()).append("\n");
        sb.append("Lead Time: ").append(data.leadTimeDays()).append(" days\n");
        sb.append("Current Stock: ").append(data.currentStock().quantity()).append(" units in ")
          .append(data.currentStock().warehouse()).append("\n\n");

        sb.append("Recent Sales (last 30 days):\n");
        int totalQuantitySold = data.recentSales().stream()
            .mapToInt(sale -> sale.quantity())
            .sum();
        sb.append("Total units sold: ").append(totalQuantitySold).append("\n");
        sb.append("Average daily sales: ").append(totalQuantitySold / 30.0).append("\n\n");

        sb.append("Please provide a JSON response with the following structure:\n");
        sb.append("{\n");
        sb.append("  \"reorderRecommendation\": \"yes\" or \"no\",\n");
        sb.append("  \"suggestedOrderQuantity\": <number>,\n");
        sb.append("  \"stockoutRisk\": \"low\", \"medium\", or \"high\",\n");
        sb.append("  \"daysUntilStockout\": <number>,\n");
        sb.append("  \"reasoning\": \"<brief explanation>\"\n");
        sb.append("}\n\n");
        sb.append("Only return valid JSON, no additional text.");

        return sb.toString();
    }

    private Map<String, Object> parseResponse(ClaudeResponse response) {
        try {
            if (response != null && response.content() != null && !response.content().isEmpty()) {
                String jsonText = response.content().get(0).text();
                return objectMapper.readValue(jsonText, Map.class);
            }
        } catch (Exception e) {
            System.err.println("Error parsing Claude response: " + e.getMessage());
        }

        return Map.of(
            "reorderRecommendation", "unknown",
            "reasoning", "Failed to get recommendation from AI"
        );
    }

    public String sendChatMessage(String sku, List<ChatMessage> messageHistory, LLMInputData productData) {
        List<ClaudeRequest.Message> claudeMessages = new ArrayList<>();
        
        if (messageHistory.isEmpty() || !messageHistory.get(0).role().equals("system")) {
            String systemContext = buildProductContext(productData);
            claudeMessages.add(new ClaudeRequest.Message("user", systemContext));
            claudeMessages.add(new ClaudeRequest.Message("assistant", "I understand the product data. How can I help you with inventory decisions for " + productData.productName() + "?"));
        }
        
        claudeMessages.addAll(
            messageHistory.stream()
                .filter(msg -> !msg.role().equals("system"))
                .map(msg -> new ClaudeRequest.Message(msg.role(), msg.content()))
                .collect(Collectors.toList())
        );

        ClaudeRequest request = new ClaudeRequest(
            config.getModel(),
            config.getMaxTokens(),
            claudeMessages
        );

        try {
            ClaudeResponse response = webClient.post()
                .uri("/v1/messages")
                .header("x-api-key", config.getApiKey())
                .header("anthropic-version", config.getApiVersion())
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ClaudeResponse.class)
                .block();

            if (response != null && response.content() != null && !response.content().isEmpty()) {
                return response.content().get(0).text();
            }
            
            return "I apologize, but I couldn't generate a response. Please try again.";
        } catch (Exception e) {
            log.error("Error in chat with Claude API: {}", e.getMessage());
            return "I'm experiencing technical difficulties. Please try again later.";
        }
    }

    private String buildProductContext(LLMInputData data) {
        StringBuilder sb = new StringBuilder();
        sb.append("You are an AI inventory management advisor. Here is the product information:\n\n");
        sb.append("Product: ").append(data.productName()).append(" (SKU: ").append(data.sku()).append(")\n");
        sb.append("Cost of Goods Sold (COGS): $").append(data.cogs()).append("\n");
        sb.append("Lead Time: ").append(data.leadTimeDays()).append(" days\n");
        sb.append("Current Stock: ").append(data.currentStock().quantity()).append(" units in ")
          .append(data.currentStock().warehouse()).append("\n\n");

        sb.append("Recent Sales (last 30 days):\n");
        int totalQuantitySold = data.recentSales().stream()
            .mapToInt(sale -> sale.quantity())
            .sum();
        sb.append("Total units sold: ").append(totalQuantitySold).append("\n");
        sb.append("Average daily sales: ").append(String.format("%.2f", totalQuantitySold / 30.0)).append("\n\n");

        sb.append("Please provide helpful, detailed advice about inventory management for this product. ");
        sb.append("Be conversational and explain your reasoning clearly.");

        return sb.toString();
    }
}
