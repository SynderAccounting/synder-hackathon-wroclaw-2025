//
//  MainTabbarView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import SwiftUI

struct MainTabbarView: View {
    enum Tab {
        case home
        case products
    }
    
    @ObservedObject private var coordinator: MainCoordinator
    
    let type: OnboardingViewModel.OnboardingType
    
    init(type: OnboardingViewModel.OnboardingType) {
        self.type = type
        self.coordinator = MainCoordinator(type: type)
    }
    
    var body: some View {
        TabView(selection: $coordinator.selectedTab) {
            HomeRouterView(router: coordinator.homeRouter)
                .tabItem {
                    Label(
                        String("Home"),
                        systemImage: "house.fill"
                    )
                    .symbolRenderingMode(.hierarchical)
                    .environment(\.symbolVariants, .none)
                }
                .tag(Tab.home)
            
            ProductsRouterView(router: coordinator.productsRouter)
                .tabItem {
                    Label(
                        String("Products"),
                        systemImage: "square.grid.2x2.fill"
                    )
                    .symbolRenderingMode(.hierarchical)
                    .environment(\.symbolVariants, .none)
                }
                .tag(Tab.products)
        }
        .tint(.orange)
    }
}
