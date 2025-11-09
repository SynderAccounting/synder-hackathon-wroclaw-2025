//
//  MainCoordinator.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import SwiftUI

final class MainCoordinator: ObservableObject {
    
    // MARK: - Properties
    
    @Published var selectedTab: MainTabbarView.Tab = .home
    @ObservedObject var homeRouter: HomeRouter
    @ObservedObject var productsRouter = ProductsRouter()
    
    // MARK: - Initialization
    
    init(type: OnboardingViewModel.OnboardingType) {
        self.homeRouter = HomeRouter(type: type)
    }
}
