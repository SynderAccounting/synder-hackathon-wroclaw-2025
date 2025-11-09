//
//  OnboardingRoterView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI

struct OnboardingRouteView: View {
    @ObservedObject var router: OnboardingRouter
    
    var body: some View {
        NavigationStack {
            if let viewModel = router.onboardingViewModel {
                OnboardingView(viewModel: viewModel)
            }
        }
    }
}
