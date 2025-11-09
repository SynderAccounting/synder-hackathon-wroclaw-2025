//
//  AnalyticsModels.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import SwiftUI

// MARK: - Analytics State

struct AnalyticsState {
    var marketOverview: MarketOverview
    var competition: Competition
    var targetAudience: TargetAudience
    var marketplaces: [MarketplaceItem]
    var tips: [String]
}

// MARK: - Market Overview

struct MarketOverview {
    let demand: String
    let averagePrice: String
    let trend: String
    let marketplaces: [String]
}

// MARK: - Competition

struct Competition {
    let level: String
    let popularBrands: [String]
}

// MARK: - Target Audience

struct TargetAudience {
    let age: String
    let gender: String
    let interests: [String]
}

// MARK: - Marketplace Item

struct MarketplaceItem: Identifiable {
    let id = UUID()
    let name: String
    let description: String
    let icon: String?
}

