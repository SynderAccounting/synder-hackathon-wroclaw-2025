//
//  RootView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import SwiftUI

struct RootView: View {
    @ObservedObject private var coordinator = RootCoordinator()
    
    var body: some View {
        switch coordinator.route {
        case .main(let type):
            MainTabbarView(type: type)
        case .onboarding(let type):
            OnboardingRouteView(router: .init(parentCoordinator: coordinator, type: type))
        case .welcome:
            WelcomeRouterView(router: .init(parentCoordinator: coordinator))
        }
    }
}

#Preview {
    RootView()
}
