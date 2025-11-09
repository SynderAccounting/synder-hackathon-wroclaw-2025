//
//  ProductModels.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation
import SwiftUI

// MARK: - Product

struct Product: Identifiable {
    let id = UUID()
    let name: String
    let itemCount: Int
    let initials: String
    let avatarColor: Color
    let platforms: [ProductPlatform]
}

// MARK: - Product Platform

struct ProductPlatform: Identifiable {
    let id = UUID()
    let platform: String
    let price: Double
    let amount: Int
    let incomeThisMonth: Double
}

// MARK: - Products State

struct ProductsState {
    var products: [Product] = []
}

