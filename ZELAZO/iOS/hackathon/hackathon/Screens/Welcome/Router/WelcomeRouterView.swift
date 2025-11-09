//
//  WelcomeRouterView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI

struct WelcomeRouterView: View {
    @ObservedObject var router: WelcomeRouter
    
    var body: some View {
        NavigationStack {
            WelcomeView(viewModel: .init(router: router))
        }
    }
}
