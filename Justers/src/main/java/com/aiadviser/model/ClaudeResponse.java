package com.aiadviser.model;

import java.util.List;

public record ClaudeResponse(
    String id,
    String type,
    String role,
    List<Content> content,
    String model,
    String stop_reason,
    Usage usage
) {
    public record Content(
        String type,
        String text
    ) {
    }

    public record Usage(
        int input_tokens,
        int output_tokens
    ) {
    }
}
