import { extractShopifyId } from '../utils/shopify';

const parseInventory = (product = {}) => {
  const inventory =
    product.totalInventory ??
    product.total_inventory ??
    product.current_stock ??
    product.stock ??
    0;
  if (typeof inventory === 'number') return inventory;
  const parsed = Number.parseInt(inventory, 10);
  return Number.isNaN(parsed) ? 0 : parsed;
};

const parsePrice = (variant = {}) => {
  const price = variant.price ?? variant.amount;
  if (typeof price === 'number') return price;
  const parsed = Number.parseFloat(price ?? 0);
  return Number.isNaN(parsed) ? 0 : parsed;
};

const extractVariants = (backendProduct = {}) => {
  if (Array.isArray(backendProduct.variants)) {
    return backendProduct.variants;
  }
  const edges = backendProduct.variants?.edges;
  if (Array.isArray(edges)) {
    return edges.map((edge) => edge?.node ?? edge).filter(Boolean);
  }
  return [];
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

export const adaptBackendProduct = (backendProduct = {}) => {
  const variants = extractVariants(backendProduct);
  const primaryVariant = variants[0] ?? null;
  const fallbackVariant = {
    sku: backendProduct.sku,
    price: backendProduct.selling_price ?? backendProduct.price,
  };
  const chosenVariant = primaryVariant ?? fallbackVariant;
  const storeDomain =
    backendProduct?.store_domain ??
    backendProduct?.storeDomain ??
    backendProduct?.shopDomain ??
    backendProduct?.shop?.permanentDomain ??
    backendProduct?.shop?.myshopifyDomain ??
    backendProduct?.shop?.domain;
  const normalizedStoreDomain = normalizeStoreDomain(storeDomain);
  const rawId = backendProduct.id ?? backendProduct.gid ?? backendProduct.sku ?? 'N/A';
  return {
    id: extractShopifyId(rawId) || rawId,
    gid: backendProduct.id ?? backendProduct.gid,
    sku: chosenVariant?.sku ?? backendProduct.sku ?? 'N/A',
    name: backendProduct.title ?? backendProduct.name ?? 'Unnamed product',
    category: backendProduct.productType ?? backendProduct.category ?? 'Uncategorized',
    stock: parseInventory(backendProduct),
    price: parsePrice(chosenVariant ?? {}),
    shop: backendProduct.shop,
    shopDomain: normalizedStoreDomain || undefined,
    raw: backendProduct,
  };
};

export const adaptBackendProducts = (response = {}) => {
  const list = response.products ?? response.items ?? [];
  if (!Array.isArray(list)) {
    return [];
  }
  return list.map(adaptBackendProduct);
};
