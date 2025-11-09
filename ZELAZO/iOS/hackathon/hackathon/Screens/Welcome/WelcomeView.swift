//  WelcomeView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI

struct WelcomeView: View {
    @ObservedObject var viewModel: WelcomeViewModel

    var body: some View {
        VStack {
            Spacer()
            
            VStack(spacing: 24) {
                Text("Welcome to hackhaton app")
                    .font(.title3)
                    .fontWeight(.heavy)
                    .fontDesign(.rounded)
                    .foregroundStyle(.black)
                
                Text("Know what to sell, where to sell, and how to win — powered by AI.")
                    .font(.headline)
                    .fontWeight(.medium)
                    .fontDesign(.rounded)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.gray)
            }
            .padding(.horizontal, 24)
            
            Spacer()
            
            VStack(spacing: 16) {
                Button("I would like to start business") {
                    viewModel.onStartTapped(.new)
                }
                .whiteMainButtonStyle()
                
                Button("I have existing business") {
                    viewModel.onStartTapped(.exisitng)
                }
                .mainButtonStyle()
                
            }
            .padding(.horizontal, 24)
        }
        .dottedBackground(spacing: 20, dotSize: 3)
        .frame(maxWidth: .infinity)
        .background(.background.secondary)
    }
}
