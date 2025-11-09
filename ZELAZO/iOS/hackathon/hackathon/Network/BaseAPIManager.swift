//
//  BaseAPIManager.swift
//  hackathon
//
//  Created by Viacheslav Starovoitov on 08/11/2025.
//

import Foundation

/// Base API Manager for handling network requests
class BaseAPIManager {
    
    // MARK: - Properties
    
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    
    // MARK: - Initialization
    
    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
        self.encoder = JSONEncoder()
        
        // Configure decoder/encoder if needed
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        encoder.keyEncodingStrategy = .convertToSnakeCase
    }
    
    // MARK: - Public Methods
    
    /// Performs a GET request
    /// - Parameters:
    ///   - endpoint: The API endpoint path
    ///   - headers: Optional custom headers
    /// - Returns: Decoded response of type T
    func get<T: Decodable>(
        endpoint: String,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = try buildRequest(
            endpoint: endpoint,
            method: "GET",
            headers: headers
        )
        return try await performRequest(request)
    }
    
    /// Performs a POST request
    /// - Parameters:
    ///   - endpoint: The API endpoint path
    ///   - body: Encodable body object
    ///   - headers: Optional custom headers
    /// - Returns: Decoded response of type T
    func post<T: Decodable, U: Encodable>(
        endpoint: String,
        body: U,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = try buildRequest(
            endpoint: endpoint,
            method: "POST",
            body: body,
            headers: headers
        )
        return try await performRequest(request)
    }
    
    /// Performs a PUT request
    /// - Parameters:
    ///   - endpoint: The API endpoint path
    ///   - body: Encodable body object
    ///   - headers: Optional custom headers
    /// - Returns: Decoded response of type T
    func put<T: Decodable, U: Encodable>(
        endpoint: String,
        body: U,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = try buildRequest(
            endpoint: endpoint,
            method: "PUT",
            body: body,
            headers: headers
        )
        return try await performRequest(request)
    }
    
    /// Performs a DELETE request
    /// - Parameters:
    ///   - endpoint: The API endpoint path
    ///   - headers: Optional custom headers
    /// - Returns: Decoded response of type T
    func delete<T: Decodable>(
        endpoint: String,
        headers: [String: String]? = nil
    ) async throws -> T {
        let request = try buildRequest(
            endpoint: endpoint,
            method: "DELETE",
            headers: headers
        )
        return try await performRequest(request)
    }
    
    // MARK: - Private Methods
    
    private func buildRequest(
        endpoint: String,
        method: String,
        headers: [String: String]? = nil
    ) throws -> URLRequest {
        guard let baseURL = APIConstants.baseURL else {
            throw APIError.invalidURL
        }
        
        let url = baseURL.appendingPathComponent(endpoint)
        var request = URLRequest(url: url)
        request.httpMethod = method
        
        // Set default headers
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // Add custom headers
        headers?.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        // Add authorization header if needed (can be extended)
        if let token = getAuthToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        return request
    }
    
    private func buildRequest<U: Encodable>(
        endpoint: String,
        method: String,
        body: U,
        headers: [String: String]? = nil
    ) throws -> URLRequest {
        var request = try buildRequest(
            endpoint: endpoint,
            method: method,
            headers: headers
        )
        
        // Encode body
        request.httpBody = try encoder.encode(body)
        
        return request
    }
    
    private func performRequest<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(statusCode: httpResponse.statusCode, data: data)
        }
        
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingError(error)
        }
    }
    
    /// Override this method in subclasses to provide authentication token
    /// - Returns: Optional authentication token string
    func getAuthToken() -> String? {
        // Implement token retrieval logic here
        // e.g., from Keychain, UserDefaults, etc.
        return nil
    }
}

// MARK: - API Errors

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpError(statusCode: Int, data: Data?)
    case decodingError(Error)
    case encodingError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response"
        case .httpError(let statusCode, _):
            return "HTTP error with status code: \(statusCode)"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Encoding error: \(error.localizedDescription)"
        }
    }
}

