package com.aiadviser.model;

import java.util.List;

public record ChatRequest(
    String sku,
    List<ChatMessage> messages
) {
}
