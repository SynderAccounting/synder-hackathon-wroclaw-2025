/**
 * Refunds API
 * Uses existing orders endpoint and filters refunds on the client side
 */
import { getAllOrders, type OrdersDTO } from './orders.js';

export interface RefundDTO {
  id: number;
  shoesId: number;
  shoesType: string;
  shoesSize: number;
  shoesPrice: number;
  description: string;
  date: string;
  quantity: number;
}

export interface RefundsBySizeDTO {
  size: number;
  count: number;
}

export interface RefundsResponse {
  message: string;
  refunds: RefundDTO[];
}

export interface RefundsBySizeResponse {
  message: string;
  refundsBySize: RefundsBySizeDTO[];
}

/**
 * Filter orders to get only refunds (status RETURNED)
 */
const filterRefunds = (orders: OrdersDTO[]): RefundDTO[] => {
  return orders
    .filter((order) => order.status === 'RETURNED')
    .map((order) => ({
      id: order.id,
      shoesId: order.shoesId,
      shoesType: order.shoesType,
      shoesSize: order.shoesSize,
      shoesPrice: order.shoesPrice,
      description: order.description,
      date: order.date,
      quantity: order.quantity,
    }));
};

/**
 * Fetch all refunds from the backend
 * Uses /api/v1/orders/all and filters for RETURNED status
 * @returns Promise with list of all refunds
 */
export const getAllRefunds = async (): Promise<RefundsResponse> => {
  try {
    const ordersResponse = await getAllOrders();
    const refunds = filterRefunds(ordersResponse.orders);

    return {
      message: 'REFUNDS WERE FILTERED SUCCESSFULLY',
      refunds,
    };
  } catch (error) {
    console.error('Error fetching refunds:', error);
    throw error;
  }
};

/**
 * Fetch refunds grouped by shoe size
 * Uses /api/v1/orders/all and aggregates on the client side
 * @returns Promise with refunds count by size
 */
export const getRefundsBySize = async (): Promise<RefundsBySizeResponse> => {
  try {
    const ordersResponse = await getAllOrders();
    const refunds = filterRefunds(ordersResponse.orders);

    // Group refunds by size
    const sizeMap = new Map<number, number>();
    refunds.forEach((refund) => {
      const currentCount = sizeMap.get(refund.shoesSize) || 0;
      sizeMap.set(refund.shoesSize, currentCount + 1);
    });

    // Convert to array and sort by size
    const refundsBySize = Array.from(sizeMap.entries())
      .map(([size, count]) => ({ size, count }))
      .sort((a, b) => a.size - b.size);

    return {
      message: 'REFUNDS BY SIZE WERE CALCULATED SUCCESSFULLY',
      refundsBySize,
    };
  } catch (error) {
    console.error('Error fetching refunds by size:', error);
    throw error;
  }
};
