import { useQuery } from '@tanstack/react-query';
import dashboardService from '../../api/services/dashboardService';
import { QUERY_KEYS } from '../../constants';

export const useDashboardStats = (options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.ANALYTICS, 'dashboard'],
    queryFn: () => dashboardService.getDashboardStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
};
