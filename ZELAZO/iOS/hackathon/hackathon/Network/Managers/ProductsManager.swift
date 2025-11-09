//
//  ProductsManager.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import SwiftUI

// MARK: - Products Manager

class ProductsManager {
    
    // MARK: - Properties
    
    private let apiManager: BaseAPIManager
    
    // MARK: - Initialization
    
    init(apiManager: BaseAPIManager = BaseAPIManager()) {
        self.apiManager = apiManager
    }
    
    // MARK: - Public Methods
    
    /// Fetches products list from the API
    /// - Returns: Array of Product objects
    func fetchProducts() async throws -> [Product] {
        let response: ProductsResponse = try await apiManager.get(endpoint: "products/v1/products-stats")
        return mapToProducts(response)
    }
    
    /// Adds a new product to the API
    /// - Parameters:
    ///   - category: Product category (e.g., "Clothing")
    ///   - name: Product name (e.g., "Wool socks")
    ///   - price: Product price (e.g., 15.99)
    /// - Returns: The created product response
    func addNewProduct(category: String, name: String, price: Double) async throws -> AddProductResponse {
        let request = AddProductRequest(category: category, name: name, price: price)
        let response: AddProductResponse = try await apiManager.post(
            endpoint: "products/v1/product",
            body: request
        )
        return response
    }
    
    // MARK: - Private Methods
    
    private func mapToProducts(_ response: ProductsResponse) -> [Product] {
        return response.products.map { productResponse in
            Product(
                name: productResponse.name,
                itemCount: productResponse.totalAmount,
                initials: generateInitials(from: productResponse.name),
                avatarColor: generateAvatarColor(from: productResponse.name),
                platforms: productResponse.platforms.map { productPlatformResponse in
                    ProductPlatform(
                        platform: productPlatformResponse.platform,
                        price: productPlatformResponse.price,
                        amount: productPlatformResponse.amount,
                        incomeThisMonth: productPlatformResponse.incomeThisMonth
                    )
                }
            )
        }
    }
    
    private func generateInitials(from name: String) -> String {
        let words = name.components(separatedBy: .whitespaces)
        guard !words.isEmpty else { return "?" }
        
        if words.count == 1 {
            // Single word: take first 2 characters
            let word = words[0]
            return String(word.prefix(2)).uppercased()
        } else {
            // Multiple words: take first character of first 2 words
            let first = String(words[0].prefix(1))
            let second = String(words[1].prefix(1))
            return (first + second).uppercased()
        }
    }
    
    private func generateAvatarColor(from name: String) -> Color {
        // Generate a consistent color based on the product name
        let colors: [Color] = [
            Color(red: 1.0, green: 0.4, blue: 0.2),      // orange
            Color(red: 0.2, green: 0.7, blue: 0.8),      // teal
            .green,
            Color(red: 0.1, green: 0.3, blue: 0.6),      // dark blue
            Color(red: 1.0, green: 0.4, blue: 0.6),      // pink
            Color(red: 0.8, green: 0.5, blue: 0.9),     // purple
            Color(red: 0.9, green: 0.6, blue: 0.2),     // orange-yellow
            Color(red: 0.3, green: 0.6, blue: 0.9)      // light blue
        ]
        
        // Use hash of name to pick a color
        let hash = abs(name.hashValue)
        return colors[hash % colors.count]
    }
}

// MARK: - API Response Models

struct ProductsResponse: Decodable {
    let products: [ProductResponse]
}

struct ProductResponse: Decodable {
    let name: String
    let totalAmount: Int
    let platforms: [ProductPlatformResponse]
}

struct ProductPlatformResponse: Decodable {
    let platform: String
    let price: Double
    let amount: Int
    let incomeThisMonth: Double
}

// MARK: - Add Product Request/Response Models

struct AddProductRequest: Encodable {
    let category: String
    let name: String
    let price: Double
}

struct AddProductResponse: Decodable {
    // Add response fields based on API response
    // For now, using a simple structure that can be extended
    let id: String?
    let category: String?
    let name: String?
    let price: Double?
}

