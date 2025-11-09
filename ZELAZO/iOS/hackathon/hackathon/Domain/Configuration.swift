//
//  Configuration.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import SwiftUI

enum Configuration {
    static var isOnboardingWatched = AppStorage(wrappedValue: false, "isOnboardingWatched")
}
