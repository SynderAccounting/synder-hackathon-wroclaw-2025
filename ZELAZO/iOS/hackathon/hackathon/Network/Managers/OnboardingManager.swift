//
//  OnboardingManager.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import SwiftUI

// MARK: - Onboarding Manager

class OnboardingManager {
    
    // MARK: - Properties
    
    private let apiManager: BaseAPIManager
    
    // MARK: - Initialization
    
    init(apiManager: BaseAPIManager = BaseAPIManager()) {
        self.apiManager = apiManager
    }
    
    // MARK: - Public Methods
    
    /// Fetches analytics data based on user's product name, description, and country
    /// - Parameters:
    ///   - productName: The name of the product
    ///   - productDescription: The description of the product
    ///   - country: The country name
    /// - Returns: AnalyticsState containing market analysis data
    func fetchAnalytics(productName: String, productDescription: String, country: String) async throws -> AnalyticsState {
        let request = AnalyticsRequest(productName: productName, productDescription: productDescription, country: country)
        let response: AnalyticsResponse = try await apiManager.post(
            endpoint: "onboarding/v1/analyse",
            body: request
        )
        return mapToAnalyticsState(response)
    }
    
    // MARK: - Private Methods
    
    private func mapToAnalyticsState(_ response: AnalyticsResponse) -> AnalyticsState {
        return AnalyticsState(
            marketOverview: MarketOverview(
                demand: response.marketOverview.demand,
                averagePrice: response.marketOverview.averagePrice,
                trend: response.marketOverview.trend,
                marketplaces: response.marketOverview.marketplaces
            ),
            competition: Competition(
                level: response.competition.level,
                popularBrands: response.competition.popularBrands
            ),
            targetAudience: TargetAudience(
                age: response.targetAudience.age,
                gender: response.targetAudience.gender,
                interests: response.targetAudience.interests
            ),
            marketplaces: response.marketplaces.map { marketplace in
                MarketplaceItem(
                    name: marketplace.name,
                    description: marketplace.description,
                    icon: marketplace.icon
                )
            },
            tips: response.tips
        )
    }
}

// MARK: - API Request Models

struct AnalyticsRequest: Encodable {
    let productName: String
    let productDescription: String
    let country: String
    
    enum CodingKeys: String, CodingKey {
        case productName = "product_name"
        case productDescription = "product_description"
        case country
    }
}

// MARK: - API Response Models

struct AnalyticsResponse: Decodable {
    let marketOverview: MarketOverviewResponse
    let competition: CompetitionResponse
    let targetAudience: TargetAudienceResponse
    let marketplaces: [MarketplaceItemResponse]
    let tips: [String]
}

struct MarketOverviewResponse: Decodable {
    let demand: String
    let averagePrice: String
    let trend: String
    let marketplaces: [String]
}

struct CompetitionResponse: Decodable {
    let level: String
    let popularBrands: [String]
}

struct TargetAudienceResponse: Decodable {
    let age: String
    let gender: String
    let interests: [String]
}

struct MarketplaceItemResponse: Decodable {
    let name: String
    let description: String
    let icon: String?
}

