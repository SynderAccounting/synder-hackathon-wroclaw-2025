import { extractShopifyId } from '../utils/shopify';

const parseAmount = (value) => {
  if (typeof value === 'number') return value;
  if (value == null) return 0;
  const parsed = Number.parseFloat(value);
  return Number.isNaN(parsed) ? 0 : parsed;
};

const normalizeStoreDomain = (value) => {
  if (!value) return '';
  let domain = String(value).trim();
  domain = domain.replace(/^https?:\/\//, '').replace(/\/.*/, '');
  const dotIndex = domain.indexOf('.');
  if (dotIndex === -1) {
    return domain;
  }
  return domain.substring(0, dotIndex);
};

export const adaptBackendOrder = (backendOrder = {}) => {
  const totalPrice = backendOrder?.totalPriceSet?.shopMoney ?? {
    amount: backendOrder?.total_price ?? backendOrder?.totalPrice,
    currencyCode: backendOrder?.currency,
  };
  const subtotalPrice = backendOrder?.subtotalPriceSet?.shopMoney ?? totalPrice;
  const fulfillmentStatus =
    backendOrder?.displayFulfillmentStatus ??
    backendOrder?.fulfillment_status ??
    backendOrder?.fulfillmentStatus ??
    backendOrder?.status;
  const financialStatus =
    backendOrder?.displayFinancialStatus ??
    backendOrder?.financial_status ??
    backendOrder?.financialStatus;
  const customerName =
    backendOrder?.customerName ??
    backendOrder?.customer?.displayName ??
    backendOrder?.customer?.email ??
    backendOrder?.email;
  const storeDomain =
    backendOrder?.store_domain ??
    backendOrder?.storeDomain ??
    backendOrder?.shopDomain ??
    backendOrder?.shop?.permanentDomain ??
    backendOrder?.shop?.myshopifyDomain ??
    backendOrder?.shop?.domain ??
    backendOrder?.raw?.shopDomain ??
    backendOrder?.raw?.shop?.permanentDomain ??
    backendOrder?.raw?.shop?.myshopifyDomain ??
    backendOrder?.raw?.shop?.domain;
  const normalizedStoreDomain = normalizeStoreDomain(storeDomain);
  const rawId = backendOrder.id ?? backendOrder.name;
  return {
    id: extractShopifyId(rawId) || rawId,
    gid: backendOrder.id,
    orderNumber: backendOrder.name ?? backendOrder.id ?? 'N/A',
    customerName: customerName ?? 'Unknown customer',
    total: parseAmount(totalPrice?.amount ?? subtotalPrice?.amount ?? 0),
    currency: totalPrice?.currencyCode ?? subtotalPrice?.currencyCode ?? 'USD',
    createdAt: backendOrder.createdAt ?? null,
    fulfillmentStatus: fulfillmentStatus ?? 'UNKNOWN',
    financialStatus: financialStatus ?? 'UNKNOWN',
    shop: backendOrder.shop,
    shopDomain: normalizedStoreDomain || undefined,
    raw: backendOrder,
  };
};

export const adaptBackendOrders = (response = {}) => {
  const list = response.orders ?? response.items ?? response.data ?? [];
  if (!Array.isArray(list)) {
    return [];
  }
  return list.map(adaptBackendOrder);
};
