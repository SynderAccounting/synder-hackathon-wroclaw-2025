//
//  HomeViewModel.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import Foundation
import SwiftUI

class HomeViewModel: ObservableObject {

    // MARK: - Published
    
    @Published var dashboardState: DashboardState = DashboardState(
        warningMessage: nil,
        monthlyIncomeChange: MetricCard(
            value: "0%",
            description: "income higher this month",
            trend: .neutral
        ),
        monthlyIncome: MetricCard(
            value: "$0",
            description: "monthly income",
            trend: .neutral
        ),
        platformStatistics: [],
        aiRecommendations: nil
    )
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    // MARK: - Properties
    
    let type: OnboardingViewModel.OnboardingType
    private var router: HomeRouter?
    private let dashboardManager: DashboardManager

    // MARK: - Functions

    init(
        router: HomeRouter,
        type: OnboardingViewModel.OnboardingType,
        dashboardManager: DashboardManager = DashboardManager()
    ) {
        self.router = router
        self.type = type
        self.dashboardManager = dashboardManager
        
        loadDashboardData()
    }
    
    // MARK: - Public Methods
    
    func loadDashboardData() {
        guard type == .exisitng else { return }
        
        isLoading = true
        errorMessage = nil
        
        Task { @MainActor in
            do {
                // Fetch both dashboard and insights in parallel
                async let dashboardData = dashboardManager.fetchDashboard()
                async let insightsData = dashboardManager.fetchInsights()
                
                var dashboard = try await dashboardData
                let insights = try await insightsData
                
                // Combine the results
                dashboard.aiRecommendations = insights
                dashboardState = dashboard
            } catch {
                errorMessage = error.localizedDescription
            }
            
            isLoading = false
        }
    }
    
    func dismissWarning() {
        dashboardState.warningMessage = nil
    }
    
    func toggleRecommendation(_ recommendation: Recommendation) {
        guard var aiRecs = dashboardState.aiRecommendations else { return }
        if let index = aiRecs.recommendations.firstIndex(where: { $0.id == recommendation.id }) {
            aiRecs.recommendations[index].isCompleted.toggle()
            dashboardState.aiRecommendations = aiRecs
        }
    }

}
