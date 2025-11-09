import apiClient from '../client';
import { API_ENDPOINTS } from '../../constants';

const ORDERS_BASE = API_ENDPOINTS.ORDERS;
const ORDERS_SYNC = API_ENDPOINTS.ORDERS_SYNC;
const SHOPIFY_ORDERS = API_ENDPOINTS.SHOPIFY_ORDERS;
const SHOPIFY_ORDERS_EXPORT = API_ENDPOINTS.SHOPIFY_ORDERS_EXPORT;

const orderService = {
  async getOrders(params = {}) {
    const response = await apiClient.get(ORDERS_BASE, { params });
    return response.data;
  },

  async getShopifyOrders(params = {}) {
    const response = await apiClient.get(SHOPIFY_ORDERS, { params });
    return response.data;
  },

  async exportShopifyOrders(params = {}) {
    const response = await apiClient.get(SHOPIFY_ORDERS_EXPORT, {
      params,
      responseType: 'blob',
    });
    return response;
  },

  async getOrderById(orderId) {
    const response = await apiClient.get(`${ORDERS_BASE}/${encodeURIComponent(orderId)}`);
    return response.data;
  },

  async syncOrders(payload = {}) {
    const response = await apiClient.post(ORDERS_SYNC, payload);
    return response.data;
  },

  async updateOrder(orderId, updates) {
    const response = await apiClient.patch(`${ORDERS_BASE}/${orderId}`, updates);
    return response.data;
  },

  async createOrder(payload) {
    const response = await apiClient.post(ORDERS_BASE, payload);
    return response.data;
  },
};

export default orderService;
