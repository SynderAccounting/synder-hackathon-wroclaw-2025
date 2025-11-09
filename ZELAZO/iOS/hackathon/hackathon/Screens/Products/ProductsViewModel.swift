//
//  ProductsViewModel.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import SwiftUI

class ProductsViewModel: ObservableObject {

    // MARK: - Published
    
    @Published var productsState: ProductsState = ProductsState()
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    // MARK: - Properties
    
    private var router: ProductsRouter?
    private let productsManager: ProductsManager

    // MARK: - Functions

    init(router: ProductsRouter, productsManager: ProductsManager = ProductsManager()) {
        self.router = router
        self.productsManager = productsManager
        bind()
        loadProducts()
    }

    deinit {
        print("~deinit \(type(of: self))")
    }
    
    // MARK: - Public Methods
    
    func loadProducts() {
        isLoading = true
        errorMessage = nil
        
        Task { @MainActor in
            do {
                let products = try await productsManager.fetchProducts()
                productsState.products = products
            } catch {
                errorMessage = error.localizedDescription
                // Fallback to simulated data on error (for development)
                #warning("TODO: remove")
                await simulateDataLoad()
            }
            isLoading = false
        }
    }
    
    func addProduct() {
        router?.showNewProductScreen()
    }

    // MARK: - Private

    private func bind() {
        
    }
    
    private func simulateDataLoad() async {
        // Simulate network delay
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        
        // Update with sample data
        productsState.products = [
            Product(
                name: "Xiaomi1 123123213",
                itemCount: 156,
                initials: "XI",
                avatarColor: Color(red: 1.0, green: 0.4, blue: 0.2), // Orange-red
                platforms: []
            ),
            Product(
                name: "Product JD",
                itemCount: 150,
                initials: "JD",
                avatarColor: Color(red: 0.2, green: 0.7, blue: 0.8), // Teal-blue
                platforms: []
            ),
            Product(
                name: "Product AD",
                itemCount: 137,
                initials: "AD",
                avatarColor: .green,
                platforms: []
            ),
            Product(
                name: "Product KN",
                itemCount: 137,
                initials: "KN",
                avatarColor: Color(red: 0.1, green: 0.3, blue: 0.6), // Dark blue
                platforms: []
            ),
            Product(
                name: "Product GB",
                itemCount: 137,
                initials: "GB",
                avatarColor: Color(red: 1.0, green: 0.4, blue: 0.6), // Pink-red
                platforms: []
            )
        ]
    }

}

// MARK: - Previews

extension ProductsViewModel {

    class var preview: ProductsViewModel {
        let viewModel = ProductsViewModel(router: .init())
        viewModel.productsState.products = [
            Product(
                name: "Xiaomi1 123123213",
                itemCount: 156,
                initials: "XI",
                avatarColor: .orange,
                platforms: []
            ),
            Product(
                name: "Product JD",
                itemCount: 150,
                initials: "JD",
                avatarColor: .teal,
                platforms: []
            ),
            Product(
                name: "Product AD",
                itemCount: 137,
                initials: "AD",
                avatarColor: .green,
                platforms: []
            )
        ]
        return viewModel
    }

}

