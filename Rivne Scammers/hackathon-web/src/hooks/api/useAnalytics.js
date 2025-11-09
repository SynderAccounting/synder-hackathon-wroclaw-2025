import { useQuery } from '@tanstack/react-query';
import analyticsService from '../../api/services/analyticsService';
import { QUERY_KEYS } from '../../constants';

const toNumber = (value) => {
  if (typeof value === 'number') return value;
  if (value == null) return 0;
  const parsed = Number.parseFloat(value);
  return Number.isNaN(parsed) ? 0 : parsed;
};

export const useSalesAnalytics = (days = 30, options = {}) => {
  return useQuery({
  queryKey: [QUERY_KEYS.ANALYTICS, 'sales', days],
    queryFn: () => analyticsService.getSalesAnalytics(days),
    select: (data) => ({
      totalRevenue: toNumber(data?.total_revenue),
      orderCount: data?.order_count ?? 0,
      averageOrderValue: toNumber(data?.average_order_value),
      raw: data,
    }),
    staleTime: 5 * 60 * 1000,
    placeholderData: (previousData) => previousData,
    ...options,
  });
};

export const useTrendingProducts = ({ limit = 10, days = 30 } = {}, options = {}) => {
  return useQuery({
  queryKey: [QUERY_KEYS.ANALYTICS, 'trending-products', { limit, days }],
    queryFn: () => analyticsService.getTrendingProducts(limit, days),
    select: (data) => ({
      products: data?.products ?? [],
      raw: data,
    }),
    staleTime: 10 * 60 * 1000,
    placeholderData: (previousData) => previousData,
    ...options,
  });
};

export const useSalesTrend = (days = 30, options = {}) => {
  return useQuery({
  queryKey: [QUERY_KEYS.ANALYTICS, 'sales-trend', days],
    queryFn: () => analyticsService.getSalesTrend(days),
    select: (data) => ({
      trend: data?.trend ?? data ?? [],
      raw: data,
    }),
    staleTime: 10 * 60 * 1000,
    placeholderData: (previousData) => previousData,
    ...options,
  });
};
