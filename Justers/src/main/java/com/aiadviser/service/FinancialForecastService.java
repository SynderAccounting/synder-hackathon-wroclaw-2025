package com.aiadviser.service;

import com.aiadviser.model.LLMInputData;
import com.aiadviser.model.FinancialMetrics;
import com.aiadviser.model.SaleData;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.List;

@Service
public class FinancialForecastService {

    @Value("${financial.carrying-cost-rate:0.20}")
    private double carryingCostRate;

    @Value("${financial.stockout-penalty-rate:0.15}")
    private double stockoutPenaltyRate;

    @Value("${financial.forecast-horizon-days:30}")
    private int defaultForecastHorizonDays;

    public FinancialMetrics calculateFinancialMetrics(
            LLMInputData data,
            int daysUntilStockout,
            int suggestedOrderQuantity
    ) {
        List<SaleData> salesHistory = data.recentSales();
        BigDecimal cogs = data.cogs();
        int currentStock = data.currentStock().quantity();
        int leadTimeDays = data.leadTimeDays();

        double avgDailySales = calculateAverageDailySales(salesHistory);
        BigDecimal avgUnitPrice = calculateAverageUnitPrice(salesHistory);

        int forecastHorizon = Math.min(daysUntilStockout > 0 ? daysUntilStockout : defaultForecastHorizonDays, 90);

        BigDecimal expectedRevenue = calculateExpectedRevenue(avgDailySales, avgUnitPrice, forecastHorizon);
        BigDecimal expectedProfit = calculateExpectedProfit(avgDailySales, cogs, avgUnitPrice, forecastHorizon);
        BigDecimal carryingCost = calculateCarryingCost(currentStock, cogs, forecastHorizon);
        BigDecimal stockoutLoss = calculateStockoutLoss(avgDailySales, avgUnitPrice, cogs, daysUntilStockout, leadTimeDays);
        BigDecimal opportunityCost = calculateOpportunityCost(avgDailySales, suggestedOrderQuantity, avgUnitPrice, cogs, leadTimeDays);

        String assumptions = buildAssumptions(avgDailySales, avgUnitPrice, forecastHorizon, salesHistory.size());

        return new FinancialMetrics(
            expectedRevenue,
            expectedProfit,
            carryingCost,
            stockoutLoss,
            opportunityCost,
            assumptions
        );
    }

    private double calculateAverageDailySales(List<SaleData> salesHistory) {
        if (salesHistory.isEmpty()) {
            return 0.0;
        }

        LocalDate earliest = salesHistory.stream()
            .map(SaleData::date)
            .min(LocalDate::compareTo)
            .orElse(LocalDate.now().minusDays(30));

        LocalDate latest = salesHistory.stream()
            .map(SaleData::date)
            .max(LocalDate::compareTo)
            .orElse(LocalDate.now());

        long daysCovered = ChronoUnit.DAYS.between(earliest, latest) + 1;

        int totalQuantity = salesHistory.stream()
            .mapToInt(SaleData::quantity)
            .sum();

        return daysCovered > 0 ? (double) totalQuantity / daysCovered : 0.0;
    }

    private BigDecimal calculateAverageUnitPrice(List<SaleData> salesHistory) {
        if (salesHistory.isEmpty()) {
            return BigDecimal.ZERO;
        }

        int totalQuantity = salesHistory.stream()
            .mapToInt(SaleData::quantity)
            .sum();

        if (totalQuantity == 0) {
            return BigDecimal.ZERO;
        }

        BigDecimal totalRevenue = salesHistory.stream()
            .map(SaleData::totalAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        return totalRevenue.divide(BigDecimal.valueOf(totalQuantity), 2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateExpectedRevenue(double avgDailySales, BigDecimal avgUnitPrice, int forecastHorizon) {
        double expectedUnits = avgDailySales * forecastHorizon;
        return avgUnitPrice.multiply(BigDecimal.valueOf(expectedUnits))
            .setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateExpectedProfit(double avgDailySales, BigDecimal cogs, BigDecimal avgUnitPrice, int forecastHorizon) {
        double expectedUnits = avgDailySales * forecastHorizon;
        BigDecimal unitProfit = avgUnitPrice.subtract(cogs);
        return unitProfit.multiply(BigDecimal.valueOf(expectedUnits))
            .setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateCarryingCost(int currentStock, BigDecimal cogs, int forecastHorizon) {
        BigDecimal inventoryValue = cogs.multiply(BigDecimal.valueOf(currentStock));
        double holdingPeriodYears = forecastHorizon / 365.0;
        return inventoryValue.multiply(BigDecimal.valueOf(carryingCostRate * holdingPeriodYears))
            .setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateStockoutLoss(double avgDailySales, BigDecimal avgUnitPrice, BigDecimal cogs, int daysUntilStockout, int leadTimeDays) {
        if (daysUntilStockout > leadTimeDays) {
            return BigDecimal.ZERO;
        }

        int stockoutDays = leadTimeDays - Math.max(daysUntilStockout, 0);
        double unmetDemand = avgDailySales * stockoutDays;
        BigDecimal contributionMargin = avgUnitPrice.subtract(cogs);
        
        BigDecimal lostProfit = contributionMargin.multiply(BigDecimal.valueOf(unmetDemand));
        BigDecimal penaltyCost = avgUnitPrice.multiply(BigDecimal.valueOf(unmetDemand * stockoutPenaltyRate));

        return lostProfit.add(penaltyCost)
            .setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateOpportunityCost(double avgDailySales, int suggestedOrderQuantity, BigDecimal avgUnitPrice, BigDecimal cogs, int leadTimeDays) {
        if (suggestedOrderQuantity <= 0) {
            return BigDecimal.ZERO;
        }

        double expectedSalesDuringLeadTime = avgDailySales * leadTimeDays;
        double additionalRevenuePotential = Math.max(0, suggestedOrderQuantity - expectedSalesDuringLeadTime);
        BigDecimal contributionMargin = avgUnitPrice.subtract(cogs);

        return contributionMargin.multiply(BigDecimal.valueOf(additionalRevenuePotential))
            .setScale(2, RoundingMode.HALF_UP);
    }

    private String buildAssumptions(double avgDailySales, BigDecimal avgUnitPrice, int forecastHorizon, int historicalDataPoints) {
        return String.format(
            "Based on %d sales records. Avg daily sales: %.1f units @ $%.2f. Forecast horizon: %d days. " +
            "Carrying cost rate: %.0f%%, Stockout penalty: %.0f%%",
            historicalDataPoints,
            avgDailySales,
            avgUnitPrice,
            forecastHorizon,
            carryingCostRate * 100,
            stockoutPenaltyRate * 100
        );
    }
}
