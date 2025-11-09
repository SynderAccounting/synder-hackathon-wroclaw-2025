package com.aiadviser.repository;

import com.aiadviser.model.ChatSession;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

@Repository
public class ChatSessionRepository {

    private final JdbcClient jdbcClient;

    public ChatSessionRepository(JdbcClient jdbcClient) {
        this.jdbcClient = jdbcClient;
    }

    public Optional<ChatSession> findBySku(String sku) {
        String sql = """
            SELECT id, sku, session_data, expires_at, created_at, updated_at
            FROM chat_sessions
            WHERE sku = :sku AND expires_at > CURRENT_TIMESTAMP
            ORDER BY updated_at DESC
            LIMIT 1
            """;

        return jdbcClient.sql(sql)
            .param("sku", sku)
            .query((rs, rowNum) -> new ChatSession(
                rs.getLong("id"),
                rs.getString("sku"),
                rs.getString("session_data"),
                rs.getTimestamp("expires_at").toLocalDateTime(),
                rs.getTimestamp("created_at").toLocalDateTime(),
                rs.getTimestamp("updated_at").toLocalDateTime()
            ))
            .optional();
    }

    public ChatSession save(String sku, String sessionData, LocalDateTime expiresAt) {
        Optional<ChatSession> existing = findBySku(sku);

        if (existing.isPresent()) {
            String updateSql = """
                UPDATE chat_sessions
                SET session_data = :sessionData, expires_at = :expiresAt, updated_at = CURRENT_TIMESTAMP
                WHERE sku = :sku
                """;

            jdbcClient.sql(updateSql)
                .param("sessionData", sessionData)
                .param("expiresAt", expiresAt)
                .param("sku", sku)
                .update();

            return findBySku(sku).orElseThrow();
        } else {
            String insertSql = """
                INSERT INTO chat_sessions (sku, session_data, expires_at)
                VALUES (:sku, :sessionData, :expiresAt)
                """;

            jdbcClient.sql(insertSql)
                .param("sku", sku)
                .param("sessionData", sessionData)
                .param("expiresAt", expiresAt)
                .update();

            return findBySku(sku).orElseThrow();
        }
    }

    public int deleteExpired() {
        String sql = "DELETE FROM chat_sessions WHERE expires_at <= CURRENT_TIMESTAMP";
        return jdbcClient.sql(sql).update();
    }

    public void deleteBySku(String sku) {
        String sql = "DELETE FROM chat_sessions WHERE sku = :sku";
        jdbcClient.sql(sql).param("sku", sku).update();
    }
}
