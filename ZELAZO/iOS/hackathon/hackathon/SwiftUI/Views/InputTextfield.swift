//
//  InputTextfield.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 8/11/25.
//
//

import SwiftUI

struct InputTextfield: View {
    var showKeyboardOnAppear: Bool = false
    let title: String?
    var currency: String?
    @Binding var error: String?
    let placeholder: String
    var keyboardType: UIKeyboardType = .default
    var contentType: UITextContentType?
    var isDatePicker = false
    var isDisabled = false
    var onEditingEnded: (() -> Void)? = nil
    var onFocus: (() -> Void)? = nil
    @Binding var inputText: String
    
    @FocusState private var isFocused: Bool
    @State private var isShowingDatePicker = false
    
    var body: some View {
        let titleColor: Color = {
            if error != nil {
                return .red
            } else if isFocused {
                return .blue
            } else {
                return .tfTitle
            }
        }()
        
        let foregroundColor: Color = {
            if error != nil {
                return .red.opacity(0.1)
            } else {
                return .tfBG
            }
        }()
        
        let strokeColor: Color = {
            if error != nil {
                return .red
            } else if isFocused {
                return .blue
            } else {
                return .clear
            }
        }()
        
        HStack(alignment: .center, spacing: 12) {
            VStack(alignment: .leading, spacing: 6) {
                if let title {
                    Text(title)
                        .foregroundColor(titleColor)
                        .font(.footnote)
                        .fontWeight(.medium)
                }
                
                HStack(alignment: .center, spacing: 12) {
                    ZStack(alignment: .leading) {
                        if inputText.isEmpty {
                            Text(placeholder)
                                .fontWeight(.semibold)
                                .font(.callout)
                                .fontDesign(.rounded)
                                .foregroundColor(.tfPlaceholder)
                                .padding(.leading, 20)
                        }
                        
                        HStack(alignment: .center, spacing: 12) {
                            TextField(
                                "",
                                text: $inputText,
                                onEditingChanged: { changed in
                                    if changed {
                                        onFocus?()
                                        error = nil
                                    } else {
                                        onEditingEnded?()
                                    }
                                }
                            )
                            .textContentType(contentType)
                            .keyboardType(keyboardType)
                            .fontWeight(.semibold)
                            .font(.callout)
                            .fontDesign(.rounded)
                            .foregroundColor(.black)
                            .padding(.leading, 20)
                            .frame(maxWidth: .infinity)
                            .focused($isFocused)
                            .disabled(isDisabled)
                            .textInputAutocapitalization(.sentences)
                            .autocorrectionDisabled(true)
                            .accentColor(.blue)
                            .toolbar {
                                ToolbarItemGroup(placement: .keyboard) {
                                    if isFocused {
                                        Spacer()
                                        Button {
                                            isFocused = false
                                        } label: {
                                            Text("Confirm")
                                                .fontWeight(.semibold)
                                                .font(.callout)
                                                .foregroundStyle(.blue)
                                        }
                                    }
                                }
                            }
                            
                            if isFocused && !inputText.isEmpty {
                                Button(action: {
                                    inputText = ""
                                }) {
                                    Image(systemName: "multiply.circle.fill")
                                        .resizable()
                                        .frame(width: 22, height: 22)
                                        .padding(.trailing, 20)
                                        .foregroundStyle(.blue)
                                }
                            } else {
                                Spacer(minLength: 16)
                            }
                        }
                    }
                    .frame(height: 50)
                    .background(foregroundColor)
                    .overlay(
                        RoundedRectangle(cornerRadius: 14)
                            .stroke(strokeColor, lineWidth: 4)
                            .background(.white.opacity(isDatePicker ? 0.01 : 0))
                            .frame(height: 50)
                            .onTapGesture {
                                if isDatePicker {
                                    isShowingDatePicker.toggle()
                                }
                            }
                    )
                    .cornerRadius(14)
                }
                
                if let error {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.footnote)
                        .fontWeight(.medium)
                        .padding(.bottom, 16)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .animation(.easeInOut(duration: 0.4), value: error)
        .onAppear {
            if showKeyboardOnAppear {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    isDatePicker ? isShowingDatePicker.toggle() : isFocused.toggle()
                }
            }
        }
    }
}
