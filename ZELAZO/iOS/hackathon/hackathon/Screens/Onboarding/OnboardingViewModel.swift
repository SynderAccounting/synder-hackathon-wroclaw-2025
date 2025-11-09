//  OnboardingViewModel.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import UIKit
import Combine
import SwiftData
import SwiftUI

class OnboardingViewModel: ObservableObject, Hashable {
    
    enum OnboardingType {
        case exisitng
        case new
    }
    
    // MARK: - Hashable
    
    static func == (lhs: OnboardingViewModel, rhs: OnboardingViewModel) -> Bool {
        lhs.id == rhs.id
    }
    
    func hash(into hasher: inout Hasher) {}

    // MARK: - Published
    
    @Published var isBackButtonHidden = true
    @Published var selectedTab: Int? = 0
    @Published var isEnabledNextButton = false
    
    @Published var productName: String = ""
    @Published var description: String = ""
    @Published var country: String?
    @Published var analyticsState: AnalyticsState?
    @Published var isLoadingAnalytics: Bool = false
    @Published var analyticsError: String?

    // MARK: - Properties
    
    let type: OnboardingType
    private let coordinator: RootCoordinator
    private let id = UUID()
    private var cancellables: Set<AnyCancellable> = []
    private let onboardingManager: OnboardingManager
    
    // MARK: - Functions

    init(coordinator: RootCoordinator, type: OnboardingType, onboardingManager: OnboardingManager = OnboardingManager()) {
        self.coordinator = coordinator
        self.type = type
        self.onboardingManager = onboardingManager
        
        bind()
    }
    
    func onConnectTap() {
        coordinator.showMain(type: .exisitng)
    }
    
    func onBackTapped() {
        if selectedTab == 0 {
            withAnimation {
                coordinator.showWelcome()
            }
            return
        }
        selectedTab! -= 1
    }
    
    func onNextTapped() {
        // If we're on page 0 and type is new, fetch analytics before moving to next page
        if type == .new && selectedTab == 0 {
            fetchAnalytics()
        } else {
            if selectedTab == 1 {
                coordinator.showMain(type: .new)
            } else {
                selectedTab! += 1
            }
        }
    }
    
    // MARK: - Analytics
    
    private func fetchAnalytics() {
        guard let country = country, !productName.isEmpty, !description.isEmpty else {
            return
        }
        
        isLoadingAnalytics = true
        analyticsError = nil
        
        Task { @MainActor in
            do {
                let analytics = try await onboardingManager.fetchAnalytics(
                    productName: productName,
                    productDescription: description,
                    country: country
                )
                
                analyticsState = analytics
                isLoadingAnalytics = false
                
                // Move to next page after successful fetch
                selectedTab! += 1
            } catch {
                analyticsError = error.localizedDescription
                isLoadingAnalytics = false
                // Optionally: show error to user or fallback to sample data
                #warning("TODO: Handle error - show alert or fallback")
            }
        }
    }

    // MARK: - Private
    
    func bind() {
        Publishers
            .CombineLatest($productName, $country)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] product, country in
                guard let self else { return }
                isEnabledNextButton = !product.isEmpty && country != nil
            }
            .store(in: &cancellables)
    }

}
