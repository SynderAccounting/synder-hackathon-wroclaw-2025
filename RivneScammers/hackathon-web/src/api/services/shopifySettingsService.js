import apiClient from '../client';
import { API_ENDPOINTS } from '../../constants';

const SHOPIFY_BASE = API_ENDPOINTS.SHOPIFY;

const shopifySettingsService = {
  async getConfig() {
    const response = await apiClient.get(`${SHOPIFY_BASE}/config`);
    return response.data;
  },

  async saveConfig(payload) {
    const response = await apiClient.post(`${SHOPIFY_BASE}/config`, payload);
    return response.data;
  },

  async testCredentials(payload) {
    const response = await apiClient.post(`${SHOPIFY_BASE}/test-credentials`, payload);
    return response.data;
  },
};

export default shopifySettingsService;
