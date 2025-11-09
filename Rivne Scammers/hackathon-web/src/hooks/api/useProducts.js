import { useQuery } from '@tanstack/react-query';
import productService from '../../api/services/productService';
import { adaptBackendProduct, adaptBackendProducts } from '../../adapters/productAdapter';
import { QUERY_KEYS } from '../../constants';

const adaptProductsResponse = (data) => ({
  products: adaptBackendProducts(data),
  total: data?.total ?? data?.count ?? data?.items?.length ?? 0,
  syncedAt: data?.synced_at ?? data?.syncedAt ?? null,
  pageInfo: data?.page_info ?? data?.pageInfo ?? null,
  raw: data,
});

export const useProducts = (params = {}, options = {}) => {
  const { enabled, ...queryOptions } = options;
  return useQuery({
  queryKey: [QUERY_KEYS.PRODUCTS, params],
  queryFn: () => productService.getShopifyProducts(params),
    select: adaptProductsResponse,
    staleTime: 2 * 60 * 1000,
    placeholderData: (previousData) => previousData,
    enabled: enabled ?? true,
    ...queryOptions,
  });
};

export const useProduct = (productId, options = {}) => {
  const { enabled, ...queryOptions } = options;
  return useQuery({
  queryKey: [QUERY_KEYS.PRODUCT, productId],
    queryFn: async () => {
      const raw = await productService.getProductById(productId);
      return raw ? adaptBackendProduct(raw) : null;
    },
    enabled: Boolean(productId) && (enabled !== false),
    placeholderData: (previousData) => previousData,
    ...queryOptions,
  });
};
