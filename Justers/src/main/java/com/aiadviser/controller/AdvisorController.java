package com.aiadviser.controller;

import com.aiadviser.model.*;
import com.aiadviser.repository.ChatSessionRepository;
import com.aiadviser.repository.ProductRepository;
import com.aiadviser.service.ClaudeService;
import com.aiadviser.service.DataAggregatorService;
import com.aiadviser.service.FinancialForecastService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class AdvisorController {

    private final DataAggregatorService dataAggregatorService;
    private final ClaudeService claudeService;
    private final ProductRepository productRepository;
    private final ChatSessionRepository chatSessionRepository;
    private final FinancialForecastService financialForecastService;
    private final ObjectMapper objectMapper;
    private final com.aiadviser.service.ProductSummaryService productSummaryService;

    public AdvisorController(
            DataAggregatorService dataAggregatorService,
            ClaudeService claudeService,
            ProductRepository productRepository,
            ChatSessionRepository chatSessionRepository,
            FinancialForecastService financialForecastService,
            ObjectMapper objectMapper,
            com.aiadviser.service.ProductSummaryService productSummaryService
    ) {
        this.dataAggregatorService = dataAggregatorService;
        this.claudeService = claudeService;
        this.productRepository = productRepository;
        this.chatSessionRepository = chatSessionRepository;
        this.financialForecastService = financialForecastService;
        this.objectMapper = objectMapper;
        this.productSummaryService = productSummaryService;
    }

    @PostMapping("/advise/{sku}")
    public ResponseEntity<AdviceResponse> getAdvice(@PathVariable String sku) {
        try {
            LLMInputData aggregatedData = dataAggregatorService.aggregateDataForLLM(sku);

            Map<String, Object> recommendations = claudeService.analyzeProductData(aggregatedData);

            int daysUntilStockout = extractIntValue(recommendations, "daysUntilStockout", 30);
            int suggestedOrderQuantity = extractIntValue(recommendations, "suggestedOrderQuantity", 0);

            FinancialMetrics financialMetrics = financialForecastService.calculateFinancialMetrics(
                aggregatedData,
                daysUntilStockout,
                suggestedOrderQuantity
            );

            String analysis = String.format(
                "Analysis for %s (%s) - Current stock: %d units, Lead time: %d days",
                aggregatedData.productName(),
                aggregatedData.sku(),
                aggregatedData.currentStock().quantity(),
                aggregatedData.leadTimeDays()
            );

            Integer ttlHours = extractIntValue(recommendations, "ttlHours", 24);

            AdviceResponse response = new AdviceResponse(
                sku,
                analysis,
                recommendations,
                financialMetrics,
                LocalDateTime.now().toString(),
                ttlHours
            );

            return ResponseEntity.ok(response);

        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/products")
    public ResponseEntity<List<ProductSummary>> getAllProducts() {
        try {
            List<ProductSummary> products = productSummaryService.getAllProductSummaries();
            return ResponseEntity.ok(products);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest chatRequest) {
        try {
            LLMInputData aggregatedData = dataAggregatorService.aggregateDataForLLM(chatRequest.sku());
            
            String aiResponse = claudeService.sendChatMessage(
                chatRequest.sku(),
                chatRequest.messages(),
                aggregatedData
            );

            ChatResponse response = new ChatResponse(
                aiResponse,
                "assistant",
                LocalDateTime.now().toString()
            );

            return ResponseEntity.ok(response);

        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/chat/session/{sku}")
    public ResponseEntity<Map<String, Object>> getChatSession(@PathVariable String sku) {
        try {
            var session = chatSessionRepository.findBySku(sku);
            if (session.isPresent()) {
                List<ChatMessage> messages = objectMapper.readValue(
                    session.get().sessionData(),
                    objectMapper.getTypeFactory().constructCollectionType(List.class, ChatMessage.class)
                );
                return ResponseEntity.ok(Map.of(
                    "messages", messages,
                    "expiresAt", session.get().expiresAt().toString()
                ));
            }
            return ResponseEntity.ok(Map.of("messages", List.of()));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @PostMapping("/chat/session")
    public ResponseEntity<Map<String, String>> saveChatSession(@RequestBody ChatSessionRequest request) {
        try {
            String sessionData = objectMapper.writeValueAsString(request.messages());
            LocalDateTime expiresAt = LocalDateTime.now().plusHours(request.ttlHours() != null ? request.ttlHours() : 24);
            
            chatSessionRepository.save(request.sku(), sessionData, expiresAt);
            
            return ResponseEntity.ok(Map.of(
                "status", "saved",
                "expiresAt", expiresAt.toString()
            ));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @DeleteMapping("/chat/session/{sku}")
    public ResponseEntity<Map<String, String>> deleteChatSession(@PathVariable String sku) {
        try {
            chatSessionRepository.deleteBySku(sku);
            return ResponseEntity.ok(Map.of("status", "deleted"));
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
            "status", "UP",
            "service", "AI Adviser",
            "timestamp", LocalDateTime.now().toString()
        ));
    }

    private int extractIntValue(Map<String, Object> map, String key, int defaultValue) {
        Object value = map.get(key);
        if (value == null) {
            return defaultValue;
        }
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(value.toString());
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }
}
