package com.aiadviser.model.baselinker;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public record BaselinkerProduct(
    @JsonProperty("product_id")
    String productId,
    
    String ean,
    
    String sku,
    
    String name,
    
    Integer quantity,
    
    @JsonProperty("price_brutto")
    Double priceBrutto,
    
    @JsonProperty("price_wholesale_netto")
    Double priceWholesaleNetto,
    
    @JsonProperty("tax_rate")
    Integer taxRate,
    
    Double weight,
    
    String description,
    
    @JsonProperty("man_name")
    String manufacturerName,
    
    @JsonProperty("category_id")
    Integer categoryId,
    
    List<String> images,
    
    Map<String, Integer> stock,
    
    Map<String, String> locations,
    
    Double width,
    
    Double height,
    
    Double length,
    
    Integer star,
    
    @JsonProperty("manufacturer_id")
    Integer manufacturerId
) {}
