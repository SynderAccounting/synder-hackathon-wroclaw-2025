package com.aiadviser.model;

import java.time.LocalDateTime;

public record ChatSession(
    Long id,
    String sku,
    String sessionData,
    LocalDateTime expiresAt,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {
}
