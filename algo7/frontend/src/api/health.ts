/**
 * Health Check API
 * Provides health status monitoring for the backend service
 */
import { API_URL } from '../config.js';
console.log('API URL:', API_URL)

export interface HealthResponse {
  status: string;
  timestamp?: string;
  details?: Record<string, unknown>;
}

/**
 * Check the health status of the backend API
 * @returns Promise with health status response
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v1/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};
