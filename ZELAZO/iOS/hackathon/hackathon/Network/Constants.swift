//
//  Constants.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation

enum APIConstants {
    /// Base host URL for API requests
    /// Change this value to switch between different environments
    static var baseHost: String = "https://susceptible-liv-issuably.ngrok-free.dev/api"
    
    /// Base URL for API endpoints
    static var baseURL: URL? {
        URL(string: baseHost)
    }
}

