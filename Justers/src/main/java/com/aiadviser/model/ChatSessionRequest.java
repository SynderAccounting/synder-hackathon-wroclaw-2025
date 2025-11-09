package com.aiadviser.model;

import java.util.List;

public record ChatSessionRequest(
    String sku,
    List<ChatMessage> messages,
    Integer ttlHours
) {
}
