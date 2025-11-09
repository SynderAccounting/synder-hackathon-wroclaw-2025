//
//  RootCoordinator.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import Foundation

enum RootRoute {
    case main(type: OnboardingViewModel.OnboardingType)
    case onboarding(type: OnboardingViewModel.OnboardingType)
    case welcome
}

final class RootCoordinator: ObservableObject {
    @Published var route: RootRoute = .welcome
    
    func showMain(type: OnboardingViewModel.OnboardingType) {
        route = .main(type: type)
    }
    
    func showWelcome() {
        route = .welcome
    }
    
    func showOnboarding(_ type: OnboardingViewModel.OnboardingType) {
        route = .onboarding(type: type)
    }
}
