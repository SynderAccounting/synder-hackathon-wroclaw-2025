//
//  HomeView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import SwiftUI
import UIKit

struct HomeView: View {
    @ObservedObject var viewModel: HomeViewModel
    
    var body: some View {
        Group {
            if viewModel.type == .new {
                emptyStateView
            } else {
                dashboardView
            }
        }
        .dottedBackground(spacing: 20, dotSize: 3)
        .navigationTitle("Dashboard")
        .navigationBarTitleDisplayMode(.large)
        .toolbarTitleDisplayMode(.large)
        .onAppear {
            configureNavigationBarAppearance()
        }
        .loader(isPresented: viewModel.isLoading)
        .alert("Error", isPresented: Binding(
            get: { viewModel.errorMessage != nil },
            set: { if !$0 { viewModel.errorMessage = nil } }
        )) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
            }
        }
    }
    
    private var dashboardView: some View {
        ScrollView {
            VStack(spacing: 20) {
                // AI Recommendations
                if let aiRecommendations = viewModel.dashboardState.aiRecommendations {
                    AIRecommendationsView(
                        recommendations: aiRecommendations,
                        onToggleRecommendation: { recommendation in
                            viewModel.toggleRecommendation(recommendation)
                        }
                    )
                    .padding(.horizontal)
                }
                
                // Only show data when not loading and has actual data
                if !viewModel.isLoading {
                    // Warning Banner
                    if let warningMessage = viewModel.dashboardState.warningMessage {
                        WarningBanner(message: warningMessage) {
                            viewModel.dismissWarning()
                        }
                    }
                    
                    // Metric Cards - only show if we have meaningful data
                    if !viewModel.dashboardState.platformStatistics.isEmpty || 
                       viewModel.dashboardState.monthlyIncome.value != "$0" {
                        HStack(spacing: 16) {
                            MetricCardView(metric: viewModel.dashboardState.monthlyIncomeChange)
                            MetricCardView(metric: viewModel.dashboardState.monthlyIncome)
                        }
                        .padding(.horizontal)
                    }
                    
                    // Platform Statistics - only show if we have data
                    if !viewModel.dashboardState.platformStatistics.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Platform Statistics")
                                .font(.system(size: 20, weight: .heavy, design: .rounded))
                                .padding(.horizontal)
                            
                            ForEach(viewModel.dashboardState.platformStatistics) { statistic in
                                PlatformStatisticRow(statistic: statistic)
                            }
                        }
                        .padding(.top, 8)
                    }
                }
            }
            .padding(.vertical)
        }
        .refreshable {
            viewModel.loadDashboardData()
        }
    }
    
    private var emptyStateView: some View {
        VStack(spacing: 24) {
            Spacer()
            
            Image(systemName: "chart.bar.doc.horizontal")
                .font(.system(size: 64, weight: .light))
                .foregroundColor(.secondary)
                .symbolRenderingMode(.hierarchical)
            
            VStack(spacing: 8) {
                Text("No Data Yet")
                    .font(.system(size: 24, weight: .heavy, design: .rounded))
                    .foregroundColor(.primary)
                
                Text("Start by adding your first product to see your dashboard statistics")
                    .font(.system(size: 16, weight: .regular))
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Warning Banner

struct WarningBanner: View {
    let message: String
    let onDismiss: () -> Void
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.title3)
                .foregroundColor(.orange)
                .symbolRenderingMode(.hierarchical)
            
            Text(message)
                .font(.system(size: 13, weight: .regular))
                .foregroundColor(.primary)
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
            
            Spacer()
            
            Button(action: onDismiss) {
                Image(systemName: "xmark.circle.fill")
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.orange.opacity(0.1))
        }
        .padding(.horizontal)
    }
}

// MARK: - Metric Card View

struct MetricCardView: View {
    let metric: MetricCard
    
    // Calculate adaptive font size based on text length
    private var valueFontSize: CGFloat {
        let length = metric.value.count
        if length > 12 {
            return 20
        } else if length > 8 {
            return 24
        } else {
            return 28
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text(metric.value)
                    .font(.system(size: valueFontSize, weight: .heavy, design: .rounded))
                    .foregroundColor(.primary)
                    .lineLimit(2)
                    .minimumScaleFactor(0.7)
                
                Image(systemName: metric.trend.icon)
                    .font(.caption)
                    .foregroundColor(metric.trend.color)
                    .symbolRenderingMode(.hierarchical)
            }
            
            Text(metric.description)
                .font(.system(size: 11, weight: .regular))
                .foregroundColor(.secondary)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.systemBackground))
                .shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 2)
        }
    }
}

// MARK: - AI Recommendations View

struct AIRecommendationsView: View {
    let recommendations: AIRecommendations
    let onToggleRecommendation: (Recommendation) -> Void
    
    @State private var isExpanded: Bool = true
    @State private var animationFlag = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Header
            Button(action: {
                withAnimation(.easeInOut(duration: 0.2)) {
                    isExpanded.toggle()
                }
            }) {
                HStack(spacing: 8) {
                    Image(systemName: "sparkles")
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundColor(Color(red: 0.6, green: 0.4, blue: 0.9))
                        .symbolRenderingMode(.hierarchical)
                    
                    Text("AI Suggestions & Risk management")
                        .font(.system(size: 18, weight: .bold))
                        .fontDesign(.rounded)
                        .foregroundColor(Color(red: 0.6, green: 0.4, blue: 0.9))
                    
                    Spacer()
                    
                    Image(systemName: "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(Color(red: 0.6, green: 0.4, blue: 0.9))
                        .rotationEffect(.degrees(isExpanded ? 0 : -90))
                        .animation(.easeInOut(duration: 0.2), value: isExpanded)
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            if isExpanded {
                // Insights Section
                VStack(alignment: .leading, spacing: 12) {
                    Text("Insights")
                        .font(.system(size: 16, weight: .bold))
                        .fontDesign(.rounded)
                        .foregroundColor(.primary)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(recommendations.insights, id: \.self) { insight in
                            if animationFlag {
                                Text(insight)
                                    .customAttribute(EmphasisAttribute())
                                    .transition(TextTransition())
                                    .font(.system(size: 12, weight: .regular))
                                    .fontDesign(.rounded)
                                    .foregroundColor(.primary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
                .onAppear {
                    animationFlag = true
                }
                
                // Recommendations Section
                VStack(alignment: .leading, spacing: 12) {
                    Text("Recommendations")
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.primary)
                    
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(recommendations.recommendations) { recommendation in
                            RecommendationRow(
                                recommendation: recommendation,
                                onToggle: {
                                    onToggleRecommendation(recommendation)
                                }
                            )
                        }
                    }
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(20)
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(red: 0.95, green: 0.92, blue: 1.0))
        }
    }
}

// MARK: - Recommendation Row

struct RecommendationRow: View {
    let recommendation: Recommendation
    let onToggle: () -> Void
    @State private var animationFlag = false
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Button(action: onToggle) {
                ZStack {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(recommendation.isCompleted ? Color(red: 0.6, green: 0.4, blue: 0.9) : Color(.systemGray5))
                        .frame(width: 24, height: 24)
                    
                    if recommendation.isCompleted {
                        Image(systemName: "checkmark")
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.white)
                    }
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            if animationFlag {
                Text(recommendation.text)
                    .customAttribute(EmphasisAttribute())
                    .transition(TextTransition())
                    .font(.system(size: 14, weight: .medium))
                    .fontDesign(.rounded)
                    .foregroundColor(.primary)
                    .fixedSize(horizontal: false, vertical: true)
                    .strikethrough(recommendation.isCompleted)
                    .opacity(recommendation.isCompleted ? 0.6 : 1.0)
            }
        }
        .onAppear {
            animationFlag = true
        }
    }
}

// MARK: - Platform Statistic Row

struct PlatformStatisticRow: View {
    let statistic: PlatformStatistic
    
    // Calculate adaptive font size for platform value
    private var valueFontSize: CGFloat {
        let length = statistic.value.count
        if length > 12 {
            return 16
        } else if length > 8 {
            return 18
        } else {
            return 20
        }
    }
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(statistic.platformName)
                    .font(.system(size: 16, weight: .heavy, design: .rounded))
                    .foregroundColor(.primary)
                
                Text(statistic.value)
                    .font(.system(size: valueFontSize, weight: .semibold))
                    .foregroundColor(.primary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            
            Spacer()
            
            HStack(spacing: 6) {
                Text(statistic.percentageChange)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(statistic.trend.color)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                
                Image(systemName: statistic.trend.icon)
                    .font(.caption)
                    .foregroundColor(statistic.trend.color)
                    .symbolRenderingMode(.hierarchical)
            }
        }
        .padding()
        .background {
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.secondarySystemBackground))
        }
        .padding(.horizontal)
    }
}

// MARK: - Navigation Bar Appearance

extension HomeView {
    func configureNavigationBarAppearance() {
        let appearance = UINavigationBarAppearance()
        
        // Large title font (rounded, heavy)
        let largeTitleFont = UIFont.systemFont(ofSize: 34, weight: .heavy)
        if let roundedDescriptor = largeTitleFont.fontDescriptor.withDesign(.rounded) {
            let roundedFont = UIFont(descriptor: roundedDescriptor, size: 34)
            appearance.largeTitleTextAttributes = [.font: roundedFont]
        } else {
            appearance.largeTitleTextAttributes = [.font: largeTitleFont]
        }
        
        // Regular title font (rounded, heavy)
        let titleFont = UIFont.systemFont(ofSize: 17, weight: .heavy)
        if let roundedDescriptor = titleFont.fontDescriptor.withDesign(.rounded) {
            let roundedFont = UIFont(descriptor: roundedDescriptor, size: 17)
            appearance.titleTextAttributes = [.font: roundedFont]
        } else {
            appearance.titleTextAttributes = [.font: titleFont]
        }
        
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().compactAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
    }
}

// MARK: - Previews

#Preview("Existing User") {
    NavigationStack {
        HomeView(viewModel: HomeViewModel(
            router: HomeRouter(type: .exisitng),
            type: .exisitng
        ))
    }
}

#Preview("New User") {
    NavigationStack {
        HomeView(viewModel: HomeViewModel(
            router: HomeRouter(type: .new),
            type: .new
        ))
    }
}
