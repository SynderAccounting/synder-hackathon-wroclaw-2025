/**
 * Orders API
 * Provides access to orders data
 */
import { API_URL } from '../config.js';

export interface OrdersDTO {
  id: number;
  shoesId: number;
  shoesType: string;
  shoesSize: number;
  shoesPrice: number;
  shoesProductionPrice: number;
  status: string;
  description: string;
  date: string;
  quantity: number;
}

export interface OrdersResponse {
  message: string;
  orders: OrdersDTO[];
}

/**
 * Fetch all orders from the backend
 * @returns Promise with list of all orders
 */
export const getAllOrders = async (): Promise<OrdersResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v1/orders/all`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch orders: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
};
