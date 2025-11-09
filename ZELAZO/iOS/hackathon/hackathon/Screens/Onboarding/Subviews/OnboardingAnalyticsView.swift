//
//  OnboardingAnalyticsView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

struct OnboardingAnalyticsView: View {
    let analyticsState: AnalyticsState
    @State private var animationFlag: Bool = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                if animationFlag {
                    // Market Overview Section
                    AnalyticsSection(
                        icon: "chart.bar.fill",
                        title: "Market Overview",
                        iconColor: .blue
                    ) {
                        marketOverviewContent
                    }
                    .scrollCardAnimation()
                    
                    // Competition Section
                    AnalyticsSection(
                        icon: "arrow.up.arrow.down",
                        title: "Competition",
                        iconColor: .orange
                    ) {
                        competitionContent
                    }
                    .scrollCardAnimation()
                    
                    // Target Audience Section
                    AnalyticsSection(
                        icon: "person.2.fill",
                        title: "Target Audience",
                        iconColor: .purple
                    ) {
                        targetAudienceContent
                    }
                    .scrollCardAnimation()
                    
                    // Marketplaces Section
                    AnalyticsSection(
                        icon: "calendar",
                        title: "Marketplaces",
                        iconColor: .green
                    ) {
                        marketplacesContent
                    }
                    .scrollCardAnimation()
                    
                    // Tips Section
                    AnalyticsSection(
                        icon: "lightbulb.fill",
                        title: "Tips",
                        iconColor: .yellow
                    ) {
                        tipsContent
                    }
                    .scrollCardAnimation()
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 16)
            .transition(TextTransition())
        }
        .scrollIndicators(.hidden)
        .onAppear {
            withAnimation {
                animationFlag = true
            }
        }
        .onDisappear {
            withAnimation {
                animationFlag = false
            }
        }
    }
    
    // MARK: - Content Builders
    
    @ViewBuilder
    private var marketOverviewContent: some View {
        VStack(alignment: .leading, spacing: 12) {
            InfoRow(label: "Demand", value: analyticsState.marketOverview.demand)
            Divider()
            InfoRow(label: "Average Price", value: analyticsState.marketOverview.averagePrice)
            Divider()
            InfoRow(label: "Trend", value: analyticsState.marketOverview.trend)
            Divider()
            InfoRow(label: "Marketplaces", value: analyticsState.marketOverview.marketplaces.joined(separator: ", "))
        }
    }
    
    @ViewBuilder
    private var competitionContent: some View {
        VStack(alignment: .leading, spacing: 12) {
            InfoRow(label: "Level", value: analyticsState.competition.level)
            Divider()
            InfoRow(label: "Popular Brands", value: analyticsState.competition.popularBrands.joined(separator: ", "))
        }
    }
    
    @ViewBuilder
    private var targetAudienceContent: some View {
        VStack(alignment: .leading, spacing: 12) {
            InfoRow(label: "Age", value: analyticsState.targetAudience.age)
            Divider()
            InfoRow(label: "Gender", value: analyticsState.targetAudience.gender)
            Divider()
            InfoRow(label: "Interests", value: analyticsState.targetAudience.interests.joined(separator: ", "))
        }
    }
    
    @ViewBuilder
    private var marketplacesContent: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(analyticsState.marketplaces.enumerated()), id: \.element.id) { index, marketplace in
                MarketplaceRow(marketplace: marketplace)
                if index < analyticsState.marketplaces.count - 1 {
                    Divider()
                }
            }
        }
    }
    
    @ViewBuilder
    private var tipsContent: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(analyticsState.tips.enumerated()), id: \.offset) { index, tip in
                HStack(alignment: .top, spacing: 12) {
                    Circle()
                        .fill(Color.yellow.opacity(0.3))
                        .frame(width: 6, height: 6)
                        .padding(.top, 6)
                    
                    Text(tip)
                        .customAttribute(EmphasisAttribute())
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .fontDesign(.monospaced)
                        .multilineTextAlignment(.leading)
                        .fixedSize(horizontal: false, vertical: true)
                }
                
                if index < analyticsState.tips.count - 1 {
                    Divider()
                        .padding(.leading, 18)
                }
            }
        }
    }
}

// MARK: - Analytics Section

struct AnalyticsSection<Content: View>: View {
    let icon: String
    let title: String
    let iconColor: Color
    let content: Content
    
    init(icon: String, title: String, iconColor: Color = .blue, @ViewBuilder content: () -> Content) {
        self.icon = icon
        self.title = title
        self.iconColor = iconColor
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack(spacing: 12) {
                ZStack {
                    Circle()
                        .fill(iconColor.opacity(0.15))
                        .frame(width: 36, height: 36)
                    
                    Image(systemName: icon)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundStyle(iconColor)
                }
                
                Text(title)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .fontDesign(.rounded)
                    .foregroundStyle(.primary)
            }
            .padding(.bottom, 16)
            
            // Content
            content
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background {
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.systemBackground))
                .shadow(color: Color.black.opacity(0.05), radius: 8, x: 0, y: 2)
        }
    }
}

// MARK: - Info Row

struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text(label)
                .font(.subheadline)
                .fontWeight(.medium)
                .fontDesign(.rounded)
                .foregroundStyle(.secondary)
                .frame(width: 120, alignment: .leading)
            
            Text(value)
                .customAttribute(EmphasisAttribute())
                .font(.subheadline)
                .fontWeight(.semibold)
                .fontDesign(.monospaced)
                .foregroundStyle(.primary)
                .multilineTextAlignment(.leading)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

// MARK: - Marketplace Row

struct MarketplaceRow: View {
    let marketplace: MarketplaceItem
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if let icon = marketplace.icon {
                ZStack {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.1))
                        .frame(width: 32, height: 32)
                    
                    Image(systemName: icon)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(.secondary)
                }
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(marketplace.name)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .fontDesign(.rounded)
                    .foregroundStyle(.primary)
                
                Text(marketplace.description)
                    .customAttribute(EmphasisAttribute())
                    .font(.subheadline)
                    .fontWeight(.regular)
                    .fontDesign(.monospaced)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

// MARK: - View Extension for Scroll Animation

extension View {
    func scrollCardAnimation() -> some View {
        self.scrollTransition(.animated.threshold(.visible(0.5))) { content, phase in
            content
                .opacity(phase.isIdentity ? 1 : 0.3)
                .scaleEffect(phase.isIdentity ? 1 : 0.95)
                .blur(radius: phase.isIdentity ? 0 : 2)
        }
    }
}
