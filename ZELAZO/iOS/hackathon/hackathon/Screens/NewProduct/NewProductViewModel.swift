//
//  NewProductViewModel.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import Combine

class NewProductViewModel: ObservableObject, Identifiable {
    
    private var router: ProductsRouter?
    private var productsManager: ProductsManager
    
    @Published var isEnabledNextButton = false
    @Published var category: String = ""
    @Published var name: String = ""
    @Published var price: String = ""
    
    private var cancellables: Set<AnyCancellable> = []
    
    init(router: ProductsRouter, productsManager: ProductsManager = ProductsManager()) {
        self.router = router
        self.productsManager = productsManager
        
        bind()
    }
    
    @MainActor
    func onCloseTap() {
        router?.closeNewProductScreen()
    }
    
    @MainActor
    func onAddTap() {
        guard let priceDouble = Double(price), priceDouble > 0 else {
            return
        }
        
        Task {
            do {
                _ = try await productsManager.addNewProduct(
                    category: category,
                    name: name,
                    price: priceDouble
                )
                // Product added successfully, close the screen
                onCloseTap()
            } catch {
                // Handle error - you might want to show an alert or error message
                print("Error adding product: \(error.localizedDescription)")
            }
        }
    }
    
    func bind() {
        Publishers
            .CombineLatest3($category, $name, $price)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] category, name, price in
                guard let self, let priceDouble = Double(price) else { return }
                isEnabledNextButton = !category.isEmpty && !name.isEmpty && priceDouble > 0
            }
            .store(in: &cancellables)
    }
    
}
