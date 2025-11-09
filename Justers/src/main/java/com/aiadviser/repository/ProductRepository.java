package com.aiadviser.repository;

import com.aiadviser.model.ProductData;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class ProductRepository {

    private final JdbcClient jdbcClient;

    public ProductRepository(JdbcClient jdbcClient) {
        this.jdbcClient = jdbcClient;
    }

    public ProductData save(ProductData product) {
        if (product.id() == null) {
            KeyHolder keyHolder = new GeneratedKeyHolder();
            jdbcClient.sql("""
                INSERT INTO product_data (sku, product_name, cogs, lead_time_days)
                VALUES (:sku, :productName, :cogs, :leadTimeDays)
                """)
                .param("sku", product.sku())
                .param("productName", product.productName())
                .param("cogs", product.cogs())
                .param("leadTimeDays", product.leadTimeDays())
                .update(keyHolder);

            Long generatedId = keyHolder.getKey().longValue();
            return new ProductData(
                generatedId,
                product.sku(),
                product.productName(),
                product.cogs(),
                product.leadTimeDays(),
                null,
                null
            );
        } else {
            jdbcClient.sql("""
                UPDATE product_data
                SET product_name = :productName, cogs = :cogs, lead_time_days = :leadTimeDays
                WHERE id = :id
                """)
                .param("id", product.id())
                .param("productName", product.productName())
                .param("cogs", product.cogs())
                .param("leadTimeDays", product.leadTimeDays())
                .update();

            return product;
        }
    }

    public Optional<ProductData> findBySku(String sku) {
        return jdbcClient.sql("""
            SELECT id, sku, product_name, cogs, lead_time_days, created_at, updated_at
            FROM product_data
            WHERE sku = :sku
            """)
            .param("sku", sku)
            .query((rs, rowNum) -> new ProductData(
                rs.getLong("id"),
                rs.getString("sku"),
                rs.getString("product_name"),
                rs.getBigDecimal("cogs"),
                rs.getInt("lead_time_days"),
                rs.getTimestamp("created_at").toLocalDateTime(),
                rs.getTimestamp("updated_at").toLocalDateTime()
            ))
            .optional();
    }

    public void upsertBySku(ProductData product) {
        jdbcClient.sql("""
            MERGE INTO product_data (sku, product_name, cogs, lead_time_days)
            KEY (sku)
            VALUES (:sku, :productName, :cogs, :leadTimeDays)
            """)
            .param("sku", product.sku())
            .param("productName", product.productName())
            .param("cogs", product.cogs())
            .param("leadTimeDays", product.leadTimeDays())
            .update();
    }

    public List<ProductData> findAll() {
        return jdbcClient.sql("""
            SELECT id, sku, product_name, cogs, lead_time_days, created_at, updated_at
            FROM product_data
            ORDER BY sku
            """)
            .query((rs, rowNum) -> new ProductData(
                rs.getLong("id"),
                rs.getString("sku"),
                rs.getString("product_name"),
                rs.getBigDecimal("cogs"),
                rs.getInt("lead_time_days"),
                rs.getTimestamp("created_at").toLocalDateTime(),
                rs.getTimestamp("updated_at").toLocalDateTime()
            ))
            .list();
    }
}
