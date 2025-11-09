package com.aiadviser.model;

public record ChatMessage(
    String role,
    String content
) {
}
