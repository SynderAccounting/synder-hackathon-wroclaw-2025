import type { LoginCredentials, RegisterCredentials, AuthResponse, User, RegisterStatus } from '../types';
import { API_URL } from '@/config';


export const authApi = {
  /**
   * Register a new user
   */
  async register(credentials: RegisterCredentials): Promise<RegisterStatus> {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      // Check for 201 Created status
      if (response.status === 201) {
        return { success: true };
      }

      // Any other status is an error - try to parse JSON error response
      const errorText = await response.text();
      let errorMessage = errorText;

      try {
        const errorJson = JSON.parse(errorText);
        // Extract message from JSON response (e.g., {message: "...", error: 400})
        errorMessage = errorJson.message || errorJson.error || errorText;
      } catch {
        // If not JSON, use the text as-is
      }

      const error: any = new Error(errorMessage || `HTTP ${response.status}`);
      error.status = response.status;
      throw error;
    } catch (error) {
      // Re-throw network errors
      if (error instanceof TypeError) {
        const networkError: any = new Error('Network error');
        networkError.status = 0;
        throw networkError;
      }
      throw error;
    }
  },

  /**
   * Login user and get JWT token
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        // Try to parse JSON error response
        const errorText = await response.text();
        let errorMessage = errorText;

        try {
          const errorJson = JSON.parse(errorText);
          // Extract message from JSON response (e.g., {message: "...", error: 400})
          errorMessage = errorJson.message || errorJson.error || errorText;
        } catch {
          // If not JSON, use the text as-is
        }

        const error: any = new Error(errorMessage || `HTTP ${response.status}`);
        error.status = response.status;
        throw error;
      }

      return response.json();
    } catch (error) {
      // Re-throw network errors
      if (error instanceof TypeError) {
        const networkError: any = new Error('Network error');
        networkError.status = 0;
        throw networkError;
      }
      throw error;
    }
  },

  /**
   * Get current user info (requires authentication)
   */
  async getUser(token: string): Promise<User> {
    const response = await fetch(`${API_URL}/api/v1/authorized/user`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Unauthorized - Please login again');
      }
      const error = await response.text();
      throw new Error(error || 'Failed to fetch user');
    }

    return response.json();
  },
};

/**
 * Token management utilities
 */
export const tokenStorage = {
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  setToken(token: string): void {
    localStorage.setItem('auth_token', token);
  },

  removeToken(): void {
    localStorage.removeItem('auth_token');
  },
};

/**
 * User data management utilities
 */
export const userStorage = {
  getUser(): User | null {
    const userJson = localStorage.getItem('user_data');
    if (!userJson) return null;
    try {
      return JSON.parse(userJson);
    } catch {
      return null;
    }
  },

  setUser(user: User): void {
    localStorage.setItem('user_data', JSON.stringify(user));
  },

  removeUser(): void {
    localStorage.removeItem('user_data');
  },
};
