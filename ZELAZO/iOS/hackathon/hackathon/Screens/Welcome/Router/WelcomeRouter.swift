//
//  WelcomeRouter.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import Foundation

class WelcomeRouter: ObservableObject {
    
    // MARK: - Published
    
    private let parentCoordinator: RootCoordinator
    
    // MARK: - Methods
    
    init(parentCoordinator: RootCoordinator) {
        self.parentCoordinator = parentCoordinator
    }
    
    @MainActor
    func showOnboardingScreen(with type: OnboardingViewModel.OnboardingType) {
        parentCoordinator.showOnboarding(type)
    }
}
