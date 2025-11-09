import apiClient from '../client';
import { API_ENDPOINTS } from '../../constants';

const PRODUCTS_BASE = API_ENDPOINTS.PRODUCTS;
const PRODUCTS_SYNC = API_ENDPOINTS.PRODUCTS_SYNC;
const SHOPIFY_PRODUCTS = API_ENDPOINTS.SHOPIFY_PRODUCTS;

const productService = {
  async getProducts(params = {}) {
    const response = await apiClient.get(PRODUCTS_BASE, { params });
    return response.data;
  },

  async getShopifyProducts(params = {}) {
    const response = await apiClient.get(SHOPIFY_PRODUCTS, { params });
    return response.data;
  },

  async getProductById(productId) {
    const response = await apiClient.get(`${PRODUCTS_BASE}/${encodeURIComponent(productId)}`);
    return response.data;
  },

  async syncProducts(payload = {}) {
    const response = await apiClient.post(PRODUCTS_SYNC, payload);
    return response.data;
  },
};

export default productService;
