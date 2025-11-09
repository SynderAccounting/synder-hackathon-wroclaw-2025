/**
 * Shoes API
 * Provides access to shoes inventory data
 */
import { API_URL } from '../config.js';

export interface ShoesDTO {
  id: number;
  type: string;
  size: number;
  price: number;
  productionPrice: number;
}

export interface ShoesResponse {
  message: string;
  shoes: ShoesDTO[];
}

/**
 * Fetch all shoes from the backend
 * @returns Promise with list of all shoes
 */
export const getAllShoes = async (): Promise<ShoesResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v1/shoes/all`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch shoes: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching shoes:', error);
    throw error;
  }
};
