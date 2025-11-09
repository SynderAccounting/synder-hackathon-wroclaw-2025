//
//  NewProductView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

struct NewProductView: View {
    @ObservedObject var viewModel: NewProductViewModel
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                VStack {
                    InputTextfield(
                        title: "Category",
                        error: .constant(nil),
                        placeholder: "e.g. Clothing",
                        inputText: $viewModel.category
                    )
                    
                    InputTextfield(
                        title: "Name",
                        error: .constant(nil),
                        placeholder: "e.g. Wool socks",
                        inputText: $viewModel.name
                    )
                    
                    InputTextfield(
                        title: "Price",
                        error: .constant(nil),
                        placeholder: "e.g. 300$",
                        keyboardType: .numberPad,
                        inputText: $viewModel.price
                    )
                }
                .padding(.horizontal, 20)
                .padding(.top, 24)
                
                Spacer()
            }
            .dottedBackground(spacing: 20, dotSize: 3)
            .background(.background.secondary)
            .navigationTitle("Adding new product")
            .navigationBarTitleDisplayMode(.automatic)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button {
                        viewModel.onCloseTap()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 24)
                            .foregroundStyle(.black)
                    }
                }
            }
        }
        .safeAreaInset(edge: .bottom) {
            ZStack {
                Button("Add the product") {
                    viewModel.onAddTap()
                }
                .mainButtonStyle()
                .disabled(!viewModel.isEnabledNextButton)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 80)
            .padding(.horizontal, 20)
        }
        .ignoresSafeArea(.keyboard, edges: .bottom)
    }
}
