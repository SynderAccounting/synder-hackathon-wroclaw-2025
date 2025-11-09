//
//  OnboardingRoter.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import Foundation

class OnboardingRouter: ObservableObject {
    
    // MARK: - Published
    
    @Published var parentCoordinator: RootCoordinator
    @Published var onboardingViewModel: OnboardingViewModel?
    
    //MARK: - Properties
    
    private let type: OnboardingViewModel.OnboardingType
    
    // MARK: - Methods
    
    init(parentCoordinator: RootCoordinator, type: OnboardingViewModel.OnboardingType) {
        self.parentCoordinator = parentCoordinator
        self.type = type
        
        restart()
    }
    
    func restart() {
        onboardingViewModel = OnboardingViewModel(coordinator: parentCoordinator, type: type)
    }
}
