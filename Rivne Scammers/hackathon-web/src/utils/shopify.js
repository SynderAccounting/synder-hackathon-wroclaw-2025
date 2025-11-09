/**
 * Shopify utility functions for handling product URLs and IDs
 */

const normalizeStoreDomain = (value) => {
  if (!value) return '';
  let domain = String(value).trim();
  if (!domain) return '';
  domain = domain.replace(/^https?:\/\//, '').replace(/\/.*/, '');
  domain = domain.toLowerCase();
  if (domain.endsWith('.myshopify.com')) {
    domain = domain.replace('.myshopify.com', '');
  }
  const dotIndex = domain.indexOf('.');
  if (dotIndex !== -1) {
    domain = domain.substring(0, dotIndex);
  }
  return domain;
};

const persistStoreSlug = (slug) => {
  if (!slug) return '';
  const normalized = slug.toLowerCase();
  if (!/^[a-z0-9][a-z0-9-]*$/.test(normalized)) {
    return '';
  }
  try {
    sessionStorage.setItem('shopify_store_name', normalized);
  } catch (error) {
    // Ignore storage write errors (e.g., unavailable in test environments)
  }
  return normalized;
};

const readCachedStoreSlug = () => {
  try {
    return sessionStorage.getItem('shopify_store_name') || '';
  } catch (error) {
    return '';
  }
};

/**
 * Extract the numeric ID from a Shopify GID
 * @param {string} gid - Shopify GID (e.g., "gid://shopify/Product/7993198575670")
 * @returns {string} - Numeric ID
 */
export const extractShopifyId = (gid) => {
  if (!gid) return '';

  // If already numeric, return as is
  if (/^\d+$/.test(gid)) {
    return gid;
  }

  // Extract from GID format: gid://shopify/Product/ID
  const match = gid.match(/\/(\d+)$/);
  return match ? match[1] : gid;
};

/**
 * Get the Shopify store name from entity data or cached settings
 * @param {object} entity - Product or order object (optional)
 * @returns {string} - Store slug used in Shopify admin URLs
 */
export const getShopifyStoreName = (entity = {}) => {
  const directDomainSources = [
    entity.shopDomain,
    entity.store_domain,
    entity.storeDomain,
    entity.storeSlug,
    entity.shop?.storeDomain,
    entity.shop?.permanentDomain,
    entity.shop?.myshopifyDomain,
    entity.shop?.domain,
    entity.raw?.shopDomain,
    entity.raw?.store_domain,
    entity.raw?.storeDomain,
    entity.raw?.storeSlug,
    entity.raw?.shop?.storeDomain,
    entity.raw?.shop?.permanentDomain,
    entity.raw?.shop?.myshopifyDomain,
    entity.raw?.shop?.domain,
  ];

  for (const candidate of directDomainSources) {
    const slug = persistStoreSlug(normalizeStoreDomain(candidate));
    if (slug) {
      return slug;
    }
  }

  if (entity.store_name) {
    const slug = persistStoreSlug(normalizeStoreDomain(entity.store_name));
    if (slug) {
      return slug;
    }
  }

  try {
    const settingsValue = localStorage.getItem('shopify_settings');
    if (settingsValue) {
      const settings = JSON.parse(settingsValue);
      const slug = persistStoreSlug(
        normalizeStoreDomain(settings.shop_url || settings.shopUrl)
      );
      if (slug) {
        return slug;
      }
    }
  } catch (error) {
    console.error('Error parsing Shopify settings:', error);
  }

  const cachedSlug = readCachedStoreSlug();
  if (cachedSlug) {
    return cachedSlug;
  }

  fetch('/api/v1/shopify/config')
    .then((res) => res.json())
    .then((data) => {
      const slug = persistStoreSlug(normalizeStoreDomain(data?.shop_url));
      if (slug) {
        try {
          localStorage.setItem('shopify_settings', JSON.stringify(data));
        } catch (error) {
          console.warn('Could not cache Shopify settings:', error);
        }
      }
    })
    .catch((err) => console.warn('Could not fetch Shopify settings:', err));

  return 'admin';
};

/**
 * Save Shopify store name to cache for quick access
 * @param {string} shopUrl - Shopify shop URL
 */
export const cacheShopifyStoreName = (shopUrl) => {
  persistStoreSlug(normalizeStoreDomain(shopUrl));
};

/**
 * Generate Shopify admin URL for a product
 * @param {object} product - Product object with id or gid
 * @returns {string} - Shopify admin product URL
 */
export const getProductAdminUrl = (product = {}) => {
  const storeName = getShopifyStoreName(product);
  const rawIdentifier = product.id || product.gid || product.sku;
  const productId = extractShopifyId(rawIdentifier);

  if (productId && /^\d+$/.test(productId)) {
    return `https://admin.shopify.com/store/${storeName}/products/${productId}`;
  }

  const searchTerm = encodeURIComponent(product.sku || productId || rawIdentifier || '');
  if (!searchTerm) {
    return `https://admin.shopify.com/store/${storeName}/products`;
  }
  return `https://admin.shopify.com/store/${storeName}/products?query=${searchTerm}`;
};

/**
 * Generate Shopify admin URL for an order
 * @param {object} order - Order object with id or gid
 * @returns {string} - Shopify admin order URL
 */
export const getOrderAdminUrl = (order = {}) => {
  const storeName = getShopifyStoreName(order);
  const orderId = extractShopifyId(order.id || order.gid);
  return `https://admin.shopify.com/store/${storeName}/orders/${orderId}`;
};

/**
 * Open Shopify admin product page in a new tab
 * @param {object} product - Product object
 */
export const openShopifyProduct = (product) => {
  const url = getProductAdminUrl(product);
  window.open(url, '_blank', 'noopener,noreferrer');
};

