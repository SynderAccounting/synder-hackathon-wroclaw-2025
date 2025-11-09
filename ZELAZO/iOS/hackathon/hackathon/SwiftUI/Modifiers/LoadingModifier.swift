//
//  LoadingModifier.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//

import SwiftUI

struct LoadingModifier: ViewModifier {
    var isLoading: Bool
    
    func body(content: Content) -> some View {
        content
            .overlay {
                if isLoading {
                    ZStack {
                        SpinningView()
                    }
                }
            }
    }
}


extension View {
    func loader(isPresented: Bool) -> some View {
        modifier(LoadingModifier(isLoading: isPresented))
    }
}
