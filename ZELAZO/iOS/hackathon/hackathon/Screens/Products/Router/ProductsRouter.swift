//
//  ProductsRouter.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation

final class ProductsRouter: ObservableObject {
    
    // MARK: - Published
    
    @Published var productsViewModel: ProductsViewModel?
    @Published var newProductViewModel: NewProductViewModel?
    
    // MARK: - Methods
    
    init() {
        productsViewModel = ProductsViewModel(router: self)
    }
    
    deinit {
        print("~deinit \(type(of: self))")
    }
    
    func showNewProductScreen() {
        newProductViewModel = NewProductViewModel(router: self)
    }
    
    func closeNewProductScreen() {
        newProductViewModel = nil
    }
}

