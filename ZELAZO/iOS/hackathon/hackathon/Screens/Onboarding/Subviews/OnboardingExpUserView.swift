//
//  OnboardingExpUserView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

struct OnboardingExpUserView: View {
    var action: () -> Void
    
    var body: some View {
        VStack(spacing: 24) {
            Text("Connect marketplaces you use with the app")
                .font(.title3)
                .fontWeight(.bold)
                .fontDesign(.rounded)
                .multilineTextAlignment(.center)
                .padding(.vertical, 4)
                .padding(.horizontal)
                .frame(maxWidth: .infinity)
                .foregroundStyle(.black)
            
            Spacer()
            
            Button("Connect with Hackathon Marketplaces") {
                action()
            }
            .whiteMainButtonStyle()
            .shadow(color: .orange, radius: 8.0, x: 0, y: -4)
            .padding(.horizontal, 20)
            .padding(.vertical)
            
            Spacer()
        }
        .padding(.top, 48)
    }
}
