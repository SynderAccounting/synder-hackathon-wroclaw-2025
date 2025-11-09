//
//  DashboardModels.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import SwiftUI

// MARK: - Dashboard State

struct DashboardState {
    var warningMessage: String?
    var monthlyIncomeChange: MetricCard
    var monthlyIncome: MetricCard
    var platformStatistics: [PlatformStatistic]
    var aiRecommendations: AIRecommendations?
}

// MARK: - Metric Card

struct MetricCard {
    let value: String
    let description: String
    let trend: TrendDirection
}

enum TrendDirection {
    case up
    case down
    case neutral
    
    var color: Color {
        switch self {
        case .up:
            return .green
        case .down:
            return .red
        case .neutral:
            return .gray
        }
    }
    
    var icon: String {
        switch self {
        case .up:
            return "arrow.up.right"
        case .down:
            return "arrow.down.right"
        case .neutral:
            return "minus"
        }
    }
}

// MARK: - Platform Statistic

struct PlatformStatistic: Identifiable {
    let id = UUID()
    let platformName: String
    let value: String
    let percentageChange: String
    let trend: TrendDirection
}

// MARK: - AI Recommendations

struct AIRecommendations {
    var insights: [String]
    var recommendations: [Recommendation]
}

struct Recommendation: Identifiable {
    let id = UUID()
    let text: String
    var isCompleted: Bool
}

