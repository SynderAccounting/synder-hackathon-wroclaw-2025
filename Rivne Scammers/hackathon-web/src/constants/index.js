export const API_ENDPOINTS = {
  AUTH: '/api/v1/auth',
  SHOPIFY: '/api/v1/shopify',
  SHOPIFY_ORDERS: '/api/v1/shopify/orders',
  SHOPIFY_PRODUCTS: '/api/v1/shopify/products',
  SHOPIFY_ORDERS_EXPORT: '/api/v1/shopify/orders/export',
  ORDERS: '/api/v1/orders',
  ORDERS_SYNC: '/api/v1/orders/sync',
  PRODUCTS: '/api/v1/products',
  PRODUCTS_SYNC: '/api/v1/products/sync',
  INVENTORY_SYNC: '/api/v1/inventory/sync',
  CATALOG_SYNC: '/api/v1/catalog/sync',
  RECOMMENDATIONS: '/api/v1/recommendations',
};

export const QUERY_KEYS = {
  ORDERS: 'orders',
  ORDER: 'order',
  PRODUCTS: 'products',
  PRODUCT: 'product',
  ANALYTICS: 'analytics',
  RECOMMENDATIONS: 'recommendations',
};

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  PRODUCTS: '/products',
  ORDERS: '/orders',
  MANAGEMENT: '/management',
  EXPORT: '/export',
  ML_SUGGESTIONS: '/ml-suggestions',
  SETTINGS: '/settings',
  LOGIN: '/login',
  REGISTER: '/register',
};

export const STATUS_COLORS = {
  CRITICAL: 'border-rose-500/40 bg-rose-500/10 text-rose-200',
  HIGH: 'border-amber-500/40 bg-amber-500/10 text-amber-200',
  MEDIUM: 'border-indigo-500/40 bg-indigo-500/10 text-indigo-200',
  LOW: 'border-slate-500/40 bg-slate-500/10 text-slate-200',
};
