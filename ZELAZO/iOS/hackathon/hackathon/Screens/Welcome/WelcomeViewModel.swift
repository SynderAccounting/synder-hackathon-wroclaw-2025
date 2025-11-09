//  WelcomeViewModel.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI

class WelcomeViewModel: ObservableObject {
    
    // MARK: - Properties
    
    private let router: WelcomeRouter

    // MARK: - Functions

    init(router: WelcomeRouter) {
        self.router = router
    }

    deinit {
        print("~deinit \(type(of: self))")
    }
    
    @MainActor
    func onStartTapped(_ type: OnboardingViewModel.OnboardingType) {
        withAnimation {
            router.showOnboardingScreen(with: type)
        }
    }

}
