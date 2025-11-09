//
//  DashboardManager.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation

// MARK: - Dashboard Manager

class DashboardManager {
    
    // MARK: - Properties
    
    private let apiManager: BaseAPIManager
    
    // MARK: - Initialization
    
    init(apiManager: BaseAPIManager = BaseAPIManager()) {
        self.apiManager = apiManager
    }
    
    // MARK: - Public Methods
    
    /// Fetches dashboard data from the API
    /// - Returns: DashboardState containing all dashboard information
    func fetchDashboard() async throws -> DashboardState {
        let response: DashboardResponse = try await apiManager.get(endpoint: "v1/dashboard")
        return mapToDashboardState(response)
    }
    
    /// Fetches AI insights and recommendations from the API
    /// - Returns: AIRecommendations containing insights and recommendations
    func fetchInsights() async throws -> AIRecommendations {
        let response: InsightsResponse = try await apiManager.get(endpoint: "v1/insights")
        return mapToAIRecommendations(response)
    }
    
    // MARK: - Private Methods
    
    private func mapToDashboardState(_ response: DashboardResponse) -> DashboardState {
        // Calculate total income difference from all platforms
        let totalIncomeDifference = response.platforms.reduce(0.0) { $0 + $1.incomeDifference }
        let totalOrders = response.platforms.reduce(0) { $0 + $1.ordersThisMonth }
        
        // Format income values
        let incomeFormatted = formatCurrency(response.incomeThisMonth)
        let incomeDifferenceFormatted = formatCurrency(abs(totalIncomeDifference))
        
        // Determine trend for monthly income change based on total difference
        let incomeChangeTrend: TrendDirection = totalIncomeDifference > 0 ? .up : (totalIncomeDifference < 0 ? .down : .neutral)
        let incomeChangeDescription = totalIncomeDifference >= 0 ? "Increased" : "Decreased"
        
        // Determine trend for monthly income (neutral as it's current month total)
        let monthlyIncomeTrend: TrendDirection = .neutral
        
        return DashboardState(
            warningMessage: response.healthCheck?.message,
            monthlyIncomeChange: MetricCard(
                value: incomeDifferenceFormatted,
                description: "\(incomeChangeDescription) by \(incomeDifferenceFormatted) vs last month",
                trend: incomeChangeTrend
            ),
            monthlyIncome: MetricCard(
                value: incomeFormatted,
                description: "\(totalOrders) orders this month",
                trend: monthlyIncomeTrend
            ),
            platformStatistics: response.platforms.map { platform in
                let trend: TrendDirection = platform.incomeDifference > 0 ? .up : (platform.incomeDifference < 0 ? .down : .neutral)
                let percentageChange = calculatePercentageChange(
                    current: platform.incomeThisMonth,
                    difference: platform.incomeDifference
                )
                
                return PlatformStatistic(
                    platformName: platform.platform.capitalized,
                    value: formatCurrency(platform.incomeThisMonth),
                    percentageChange: percentageChange,
                    trend: trend
                )
            },
            aiRecommendations: nil // Will be set separately from insights API
        )
    }
    
    private func mapToAIRecommendations(_ response: InsightsResponse) -> AIRecommendations {
        return AIRecommendations(
            insights: response.insights,
            recommendations: response.recommendations.map { text in
                Recommendation(
                    text: text,
                    isCompleted: false
                )
            }
        )
    }
    
    private func formatCurrency(_ amount: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"
        formatter.maximumFractionDigits = 0
        return formatter.string(from: NSNumber(value: amount)) ?? "$\(Int(amount))"
    }
    
    private func calculatePercentageChange(current: Double, difference: Double) -> String {
        let previous = current - difference
        guard previous > 0 else {
            return difference >= 0 ? "+100%" : "-100%"
        }
        let percentage = (difference / previous) * 100
        let sign = percentage >= 0 ? "+" : ""
        return String(format: "%@%.1f%%", sign, percentage)
    }
    
}

// MARK: - API Response Models

struct DashboardResponse: Decodable {
    let healthCheck: HealthCheck?
    let ordersAmountThisMonth: Int
    let incomeThisMonth: Double
    let platforms: [PlatformResponse]
}

struct HealthCheck: Decodable {
    let status: String
    let message: String
}

struct PlatformResponse: Decodable {
    let platform: String
    let incomeThisMonth: Double
    let ordersThisMonth: Int
    let incomeDifference: Double
}

// MARK: - Insights API Response Models

struct InsightsResponse: Decodable {
    let insights: [String]
    let recommendations: [String]
    let summary: String?
    let aiEnabled: Bool?
    
    enum CodingKeys: String, CodingKey {
        case insights
        case recommendations
        case summary
        case aiEnabled = "ai_enabled"
    }
}

