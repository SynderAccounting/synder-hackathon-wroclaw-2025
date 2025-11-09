//
//  SpinningView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//

import SwiftUI

struct SpinningView: View {
    @State var degreesRotating = 0.0
    
    var body: some View {
        ZStack(alignment: .center) {
            Rectangle()
                .foregroundColor(.loaderBg)
                .cornerRadius(24)
                .frame(width: 88, height: 88)
            
            Image(.loader)
                .rotationEffect(.degrees(degreesRotating))
                .onAppear {
                    withAnimation(.linear(duration: 1).speed(1.5).repeatForever(autoreverses: false)) {
                        degreesRotating = 360.0
                    }
                }
        }
    }
}
