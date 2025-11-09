import apiClient from '../client';
import { adaptBackendOrders } from '../../adapters/orderAdapter';

const dashboardService = {
  /**
   * Fetch comprehensive dashboard statistics from Shopify
   */
  async getDashboardStats() {
    try {
      // Fetch data in parallel from multiple endpoints
      const [ordersRes, productsRes, customersRes, analyticsRes] = await Promise.allSettled([
        apiClient.get('/api/v1/shopify/orders', { params: { limit: 250 } }),
        apiClient.get('/api/v1/shopify/products', { params: { limit: 250 } }),
        apiClient.get('/api/v1/shopify/customers', { params: { limit: 250 } }),
        apiClient.get('/api/v1/shopify/analytics/sales', { params: { days: 30 } }),
      ]);

      const stats = {
        revenue: 0,
        orders: 0,
        products: 0,
        customers: 0,
        recentOrders: [],
        inventoryItems: [],
        error: null,
      };

      // Process orders
      if (ordersRes.status === 'fulfilled' && ordersRes.value?.data) {
        const ordersData = ordersRes.value.data;
        const rawOrders = ordersData.orders || [];
        const allOrders = adaptBackendOrders({ orders: rawOrders });
        
        // Get only 6 most recent for display
        stats.recentOrders = allOrders.slice(0, 6);
        
        // Use total count from all fetched orders
        stats.orders = allOrders.length;
      }

      // Process products count and inventory
      if (productsRes.status === 'fulfilled' && productsRes.value?.data) {
        const productsData = productsRes.value.data;
        const products = productsData.products || [];
        stats.products = products.length;
        
        // Extract inventory from products
        stats.inventoryItems = products.map(product => {
          const variants = product.variants?.edges?.map(edge => edge.node) || product.variants || [];
          const totalInventory = product.totalInventory || 0;
          
          if (variants.length > 0) {
            return variants.map(variant => ({
              id: variant.id || product.id,
              sku: variant.sku || 'N/A',
              title: product.title || 'Unknown Product',
              totalAvailable: variant.inventoryQuantity || 0,
              variant: {
                title: variant.title || 'Default',
              },
            }));
          }
          
          return [{
            id: product.id,
            sku: product.sku || 'N/A',
            title: product.title || 'Unknown Product',
            totalAvailable: totalInventory,
            variant: {
              title: 'Default',
            },
          }];
        }).flat();
      }

      // Process customers count
      if (customersRes.status === 'fulfilled' && customersRes.value?.data) {
        const customersData = customersRes.value.data;
        const customers = customersData.customers || [];
        stats.customers = customers.length;
      }

      // Process analytics/revenue - Use API directly
      if (analyticsRes.status === 'fulfilled' && analyticsRes.value?.data) {
        const analyticsData = analyticsRes.value.data;
        // Extract revenue from API response
        stats.revenue = parseFloat(analyticsData.total_revenue || 0);
      }

      return stats;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },
};

export default dashboardService;