package com.aiadviser.scheduled;

import com.aiadviser.repository.ChatSessionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class ChatSessionCleanupTask {

    private static final Logger log = LoggerFactory.getLogger(ChatSessionCleanupTask.class);
    private final ChatSessionRepository chatSessionRepository;

    public ChatSessionCleanupTask(ChatSessionRepository chatSessionRepository) {
        this.chatSessionRepository = chatSessionRepository;
    }

    @Scheduled(fixedRate = 3600000)
    public void cleanupExpiredSessions() {
        log.info("Running chat session cleanup task...");
        int deleted = chatSessionRepository.deleteExpired();
        if (deleted > 0) {
            log.info("Deleted {} expired chat session(s)", deleted);
        } else {
            log.debug("No expired chat sessions to delete");
        }
    }
}
