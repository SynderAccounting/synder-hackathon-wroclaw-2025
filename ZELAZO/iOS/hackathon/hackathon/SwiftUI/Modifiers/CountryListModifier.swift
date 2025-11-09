//
//  CountryListModifier.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

struct CountryListModifier: ViewModifier {
    @Binding var isShowing: Bool
    @Binding var countryName: String?
    
    private let countries = Country.allCountries
    @State private var searchText = ""
    
    var searchResults: [Country] {
        if searchText.isEmpty {
            return countries
        } else {
            return countries.filter {
                $0.name.lowercased().contains(searchText.lowercased())
            }
        }
    }
    
    func body(content: Content) -> some View {
        content
            .sheet(isPresented: $isShowing) {
                NavigationStack {
                    List {
                        ForEach(searchResults) { country in
                            HStack(spacing: 16) {
                                Text(country.flag)
                                    .font(.callout)
                                    .fontDesign(.monospaced)
                                
                                Text(country.name)
                                    .fontWeight(.medium)
                                    .font(.callout)
                                    .fontDesign(.rounded)
                                    .foregroundColor(.black)
                                    .multilineTextAlignment(.leading)
                                
                                Spacer()
                                
                                if let countryName, country.name == countryName {
                                    Image(systemName: "checkmark")
                                        .foregroundStyle(.blue)
                                }
                            }
                            .contentShape(Rectangle())
                            .onTapGesture {
                                countryName = country.name
                                isShowing.toggle()
                            }
                        }
                    }
                    .navigationTitle("Pick country")
                    .navigationBarTitleDisplayMode(.large)
                    .onDisappear {
                        searchText = ""
                    }
                }
                .searchable(text: $searchText)
            }
    }
}

extension View {
    func countriesList(
        isShowing: Binding<Bool>,
        countryName: Binding<String?>
    ) -> some View {
        modifier(CountryListModifier(isShowing: isShowing, countryName: countryName))
    }
}
