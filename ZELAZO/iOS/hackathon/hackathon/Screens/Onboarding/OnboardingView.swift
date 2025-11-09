//  OnboardingView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI
import UIKit

struct OnboardingView: View {
    @ObservedObject var viewModel: OnboardingViewModel
    @State private var isCountriesListShowing = false

    var body: some View {
        NavigationStack {
            VStack {
                switch viewModel.type {
                case .exisitng:
                    OnboardingExpUserView {
                        viewModel.onConnectTap()
                    }
                case .new:
                    ScrollView(.horizontal, showsIndicators: false) {
                        LazyHStack(spacing: 0) {
                            ForEach(0...1, id: \.self) { page in
                                VStack {
                                    switch page {
                                    case 0:
                                        OnboardingNameView(
                                            productName: $viewModel.productName,
                                            description: $viewModel.description,
                                            country: $viewModel.country
                                        ) {
                                            isCountriesListShowing.toggle()
                                        }
                                        .padding(.horizontal, 20)
                                        
                                        
                                    case 1:
                                        if let analyticsState = viewModel.analyticsState {
                                            OnboardingAnalyticsView(analyticsState: analyticsState)
                                        } else {
                                            ProgressView()
                                                .padding(.horizontal, 20)
                                        }
                                    default:
                                        EmptyView()
                                            .padding(.horizontal, 20)
                                    }
                                }
                                .containerRelativeFrame(.horizontal)
                                .scrollTransition(.animated, axis: .horizontal) { content, phase in
                                    content
                                        .opacity(phase.isIdentity ? 1.0 : 0.6)
                                        .scaleEffect(phase.isIdentity ? 1.0 : 0.6)
                                        .blur(radius: phase.isIdentity ? 0 : 10)
                                        .rotationEffect(phase.isIdentity ? .zero : .init(degrees: 5))
                                }
                            }
                        }
                        .scrollTargetLayout()
                    }//: ScrollView
                    .scrollPosition(id: $viewModel.selectedTab)
                    .scrollTargetBehavior(.paging)
                    .ignoresSafeArea(.keyboard, edges: .bottom)
                    .scrollDisabled(true)
                }
            }
            .background(.background.secondary)
            .countriesList(
                isShowing: $isCountriesListShowing,
                countryName: $viewModel.country
            )
        }
        .safeAreaInset(edge: .bottom) {
            
            Button("Next") {
                withAnimation {
                    viewModel.onNextTapped()
                }
            }
            .mainButtonStyle()
            .padding(.horizontal, 20)
            .padding(.vertical)
            .opacity(viewModel.type == .exisitng ? 0 : 1)
            .disabled(!viewModel.isEnabledNextButton || viewModel.isLoadingAnalytics)
        }
        .loader(isPresented: viewModel.isLoadingAnalytics)
        .alert("Error", isPresented: Binding(
            get: { viewModel.analyticsError != nil },
            set: { if !$0 { viewModel.analyticsError = nil } }
        )) {
            Button("OK") {
                viewModel.analyticsError = nil
            }
        } message: {
            if let errorMessage = viewModel.analyticsError {
                Text(errorMessage)
            }
        }
        .dottedBackground(spacing: 20, dotSize: 3)
        .ignoresSafeArea(.keyboard, edges: .bottom)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button {
                    withAnimation {
                        viewModel.onBackTapped()
                    }
                } label: {
                    Image(systemName: "chevron.backward.circle.fill")
                        .symbolRenderingMode(.hierarchical)
                        .frame(width: 24)
                }
            }
        }
    }
}
