package com.aiadviser.model;

import java.util.List;

public record ClaudeRequest(
    String model,
    int max_tokens,
    List<Message> messages
) {
    public record Message(
        String role,
        String content
    ) {
    }
}
