import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import orderService from '../../api/services/orderService';
import { adaptBackendOrder, adaptBackendOrders } from '../../adapters/orderAdapter';
import { QUERY_KEYS } from '../../constants';

const adaptOrdersResponse = (data) => ({
  orders: adaptBackendOrders(data),
  total: data?.total ?? data?.count ?? data?.items?.length ?? 0,
  syncedAt: data?.synced_at ?? data?.syncedAt ?? null,
  pageInfo: data?.page_info ?? data?.pageInfo ?? null,
  raw: data,
});

export const useOrders = (params = {}, options = {}) => {
  const { enabled, ...queryOptions } = options;
  return useQuery({
  queryKey: [QUERY_KEYS.ORDERS, params],
  queryFn: () => orderService.getShopifyOrders(params),
    select: adaptOrdersResponse,
    staleTime: 5 * 60 * 1000,
    placeholderData: (previousData) => previousData,
    enabled: enabled ?? true,
    ...queryOptions,
  });
};

export const useOrder = (orderId, options = {}) => {
  const { enabled, ...queryOptions } = options;
  return useQuery({
  queryKey: [QUERY_KEYS.ORDER, orderId],
    queryFn: async () => {
      const raw = await orderService.getOrderById(orderId);
      return raw ? adaptBackendOrder(raw) : null;
    },
    enabled: Boolean(orderId) && (enabled !== false),
    placeholderData: (previousData) => previousData,
    ...queryOptions,
  });
};

export const useUpdateOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, updates }) => orderService.updateOrder(orderId, updates),
    onSuccess: (data, variables) => {
  queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ORDERS] });
  queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ORDER, variables.orderId] });
      return data;
    },
  });
};

export const useCreateOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload) => orderService.createOrder(payload),
    onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.ORDERS] });
    },
  });
};
