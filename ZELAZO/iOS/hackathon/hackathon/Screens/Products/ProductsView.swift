//
//  ProductsView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI
import UIKit

struct ProductsView: View {
    @ObservedObject var viewModel: ProductsViewModel
    
    var body: some View {
        List {
            ForEach(viewModel.productsState.products) { product in
                ProductRow(product: product)
                    .listRowSeparator(.hidden)
                    .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
            }
        }
        .dottedBackground(spacing: 20, dotSize: 3)
        .listStyle(.plain)
        .navigationTitle("Products")
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: viewModel.addProduct) {
                    Image(systemName: "plus")
                        .font(.system(size: 20, weight: .semibold))
                        .symbolRenderingMode(.hierarchical)
                }
            }
        }
        .refreshable {
            viewModel.loadProducts()
        }
        .loader(isPresented: viewModel.isLoading)
        .alert("Error", isPresented: Binding(
            get: { viewModel.errorMessage != nil },
            set: { if !$0 { viewModel.errorMessage = nil } }
        )) {
            Button("OK") {
                viewModel.errorMessage = nil
            }
        } message: {
            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
            }
        }
        .onAppear {
            configureNavigationBarAppearance()
        }
    }
}

// MARK: - Product Row

struct ProductRow: View {
    let product: Product
    
    var body: some View {
        HStack(spacing: 16) {
            // Circular Avatar
            ZStack {
                Circle()
                    .fill(product.avatarColor)
                    .frame(width: 50, height: 50)
                
                Text(product.initials)
                    .font(.system(size: 18, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
            }
            
            // Product Info
            VStack(alignment: .leading, spacing: 4) {
                Text(product.name)
                    .font(.system(size: 17, weight: .bold, design: .rounded))
                    .foregroundColor(.primary)
                
                Text("\(product.itemCount) items")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Navigation Bar Appearance

extension ProductsView {
    func configureNavigationBarAppearance() {
        let appearance = UINavigationBarAppearance()
        
        // Large title font (rounded, heavy)
        let largeTitleFont = UIFont.systemFont(ofSize: 34, weight: .heavy)
        if let roundedDescriptor = largeTitleFont.fontDescriptor.withDesign(.rounded) {
            let roundedFont = UIFont(descriptor: roundedDescriptor, size: 34)
            appearance.largeTitleTextAttributes = [.font: roundedFont]
        } else {
            appearance.largeTitleTextAttributes = [.font: largeTitleFont]
        }
        
        // Regular title font (rounded, heavy)
        let titleFont = UIFont.systemFont(ofSize: 17, weight: .heavy)
        if let roundedDescriptor = titleFont.fontDescriptor.withDesign(.rounded) {
            let roundedFont = UIFont(descriptor: roundedDescriptor, size: 17)
            appearance.titleTextAttributes = [.font: roundedFont]
        } else {
            appearance.titleTextAttributes = [.font: titleFont]
        }
        
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().compactAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
    }
}

// MARK: - Previews

#Preview {
    NavigationStack {
        ProductsView(viewModel: .preview)
    }
}

