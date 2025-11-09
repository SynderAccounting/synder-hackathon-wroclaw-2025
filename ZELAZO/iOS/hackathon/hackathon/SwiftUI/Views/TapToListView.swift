//
//  TapToListView.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

struct TapToListView: View {
    let title: String
    var placeholder: String?
    var value: String?
    
    var body: some View {
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .foregroundColor(.tfTitle)
                    .font(.footnote)
                    .fontWeight(.medium)
                
                ZStack {
                    HStack {
                        if let placeholder, value == nil {
                            Text(placeholder)
                                .fontWeight(.semibold)
                                .font(.callout)
                                .fontDesign(.rounded)
                                .foregroundColor(.tfPlaceholder)
                        } else {
                            Text(value ?? title)
                                .fontWeight(.semibold)
                                .font(.callout)
                                .fontDesign(.rounded)
                                .foregroundColor(.black)
                        }
                        
                        Spacer()
                        
                        Image(systemName: "arrow.down.circle.fill")
                            .resizable()
                            .frame(width: 24, height: 24)
                            .symbolRenderingMode(.hierarchical)
                            .foregroundStyle(.gray500)
                    }
                    .padding(.horizontal, 20)
                }
                .frame(height: 50)
                .background(.tfBG)
                .cornerRadius(14)
                .contentShape(Rectangle())
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

#Preview {
    TapToListView(title: "Currency", placeholder: "", value: "USD")
}
