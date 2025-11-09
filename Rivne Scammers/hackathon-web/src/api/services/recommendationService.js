import apiClient from '../client';
import { API_ENDPOINTS } from '../../constants';

const RECOMMENDATIONS_BASE = API_ENDPOINTS.RECOMMENDATIONS;

const recommendationService = {
  async getRecommendations(params = {}) {
    const response = await apiClient.get(RECOMMENDATIONS_BASE, { params });
    return response.data;
  },

  async actionRecommendation(recommendationId, actionData) {
    const response = await apiClient.post(
      `${RECOMMENDATIONS_BASE}/${recommendationId}/action`,
      actionData,
    );
    return response.data;
  },

  async generateRecommendations() {
    const response = await apiClient.post(`${RECOMMENDATIONS_BASE}/generate`);
    return response.data;
  },

  async deleteRecommendation(recommendationId) {
    const response = await apiClient.delete(`${RECOMMENDATIONS_BASE}/${recommendationId}`);
    return response.data;
  },
};

export default recommendationService;
