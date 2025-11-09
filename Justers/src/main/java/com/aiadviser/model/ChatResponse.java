package com.aiadviser.model;

public record ChatResponse(
    String message,
    String role,
    String timestamp
) {
}
