import apiClient from '../client';

const analyticsService = {
  async getSalesAnalytics(days = 30) {
    const response = await apiClient.get('/api/v1/shopify/analytics/sales', {
      params: { days },
    });
    return response.data;
  },

  async getTrendingProducts(limit = 10, days = 30) {
    const response = await apiClient.get('/api/v1/shopify/analytics/top-products', {
      params: { limit, days },
    });
    return response.data;
  },

  async getSalesTrend(days = 30) {
    const response = await apiClient.get('/api/v1/shopify/analytics/sales-trend', {
      params: { days },
    });
    return response.data;
  },
};

export default analyticsService;
