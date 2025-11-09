//
//  DottedBackgroundModifier.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//


import SwiftUI

struct DottedBackgroundModifier: ViewModifier {
    var dotColor: Color = .gray.opacity(0.4)
    var spacing: CGFloat = 16
    var dotSize: CGFloat = 2
    var fadeRadiusMultiplier: CGFloat = 0.6

    func body(content: Content) -> some View {
        content
            .background(
                GeometryReader { geo in
                    Canvas { context, size in
                        for x in stride(from: 0, to: size.width, by: spacing) {
                            for y in stride(from: 0, to: size.height, by: spacing) {
                                let rect = CGRect(x: x, y: y, width: dotSize, height: dotSize)
                                context.fill(Path(ellipseIn: rect), with: .color(dotColor))
                            }
                        }
                    }
                    .mask(
                        RadialGradient(
                            gradient: Gradient(colors: [.black, .black.opacity(0)]),
                            center: .center,
                            startRadius: 0,
                            endRadius: geo.size.width * fadeRadiusMultiplier
                        )
                    )
                }
            )
    }
}

extension View {
    func dottedBackground(
        color: Color = .gray.opacity(0.2),
        spacing: CGFloat = 8,
        dotSize: CGFloat = 2,
        fadeRadiusMultiplier: CGFloat = 0.8
    ) -> some View {
        modifier(
            DottedBackgroundModifier(
                dotColor: color,
                spacing: spacing,
                dotSize: dotSize,
                fadeRadiusMultiplier: fadeRadiusMultiplier
            )
        )
    }
}
