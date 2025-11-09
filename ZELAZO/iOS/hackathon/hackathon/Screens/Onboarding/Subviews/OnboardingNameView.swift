//
//  OnboardingNameView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI

struct OnboardingNameView: View {
    @Binding var productName: String
    @Binding var description: String
    @Binding var country: String?
    
    var countryListTrigger: () -> Void
    
    var body: some View {
        VStack(spacing: 24) {
            Text("What product you want to sell")
                .font(.title2)
                .fontWeight(.bold)
                .fontDesign(.rounded)
                .multilineTextAlignment(.center)
                .padding(.vertical, 4)
                .padding(.horizontal)
                .frame(maxWidth: .infinity)
                .foregroundStyle(.onboardingTitle)
            
            InputTextfield(
                title: "Product name",
                error: .constant(nil),
                placeholder: "e.g. Socks",
                inputText: $productName
            )
            
            InputTextfield(
                title: "Description",
                error: .constant(nil),
                placeholder: "e.g. Handmade wool socks",
                inputText: $description
            )
            
            TapToListView(
                title: "Country of distribution",
                placeholder: "USA",
                value: country
            )
            .onTapGesture {
                countryListTrigger()
            }
            
            Spacer()
        }
        .padding(.top, 48)
    }
}
