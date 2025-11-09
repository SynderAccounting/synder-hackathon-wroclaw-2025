//
//  HomeRouter.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import Foundation

final class HomeRouter: ObservableObject {
    
    // MARK: - Published
    
    @Published var homeViewModel: HomeViewModel?
    
    // MARK: - Properties
    
    let type: OnboardingViewModel.OnboardingType
    
    // MARK: - Methods
    
    init(type: OnboardingViewModel.OnboardingType) {
        self.type = type
        homeViewModel = HomeViewModel(router: self, type: type)
    }
}
