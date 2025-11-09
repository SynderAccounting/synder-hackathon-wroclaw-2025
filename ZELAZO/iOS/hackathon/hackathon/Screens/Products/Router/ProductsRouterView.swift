//
//  ProductsRouterView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

struct ProductsRouterView: View {
    @ObservedObject var router: ProductsRouter
    
    var body: some View {
        if let vm = router.productsViewModel {
            NavigationStack {
                ProductsView(viewModel: vm)
                    .sheet(item: $router.newProductViewModel) { vm in
                        NewProductView(viewModel: vm)
                    }
            }
        }
    }
}

#Preview {
    ProductsRouterView(router: .init())
}

