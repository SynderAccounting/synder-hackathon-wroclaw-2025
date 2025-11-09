//
//  HomeRouterView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 07/11/2025.
//

import SwiftUI

struct HomeRouterView: View {
    @ObservedObject var router: HomeRouter
    
    var body: some View {
        if let vm = router.homeViewModel {
            NavigationStack {
                HomeView(viewModel: vm)
            }
        }
    }
}

#Preview {
    HomeRouterView(router: .init(type: .new))
}
