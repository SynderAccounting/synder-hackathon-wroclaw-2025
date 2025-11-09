/**
 * STANDARDOWA STRUKTURA DANYCH DLA PRODUKTÓW
 *
 * To jest jedyna struktura którą używamy w całej aplikacji.
 * Wszystkie produkty z API mają dokładnie te pola.
 */

/**
 * @typedef {Object} ActivePromotion
 * @property {number} id - ID promocji
 * @property {string} type - Typ promocji: 'price', 'bundle', 'promo'
 * @property {string} description - Opis promocji
 */

/**
 * @typedef {Object} ProductRecord
 *
 * GŁÓWNA STRUKTURA PRODUKTU - to wyświetlamy w tabeli
 *
 * @property {string} sku - Kod produktu (SKU)
 * @property {string} name - Nazwa produktu
 * @property {number} price - Cena produktu
 * @property {number} stock - Nakład/ilość na stanie
 * @property {string} status - Status: 'active', 'low_stock', 'out_of_stock', 'inactive'
 * @property {string} channel - Kanał sprzedaży: 'shopify' lub 'woocommerce'
 * @property {string|null} active_promotion - Opis aktywnej promocji lub null
 *
 * Dodatkowe pola (opcjonalne):
 * @property {number} [id] - ID produktu w bazie
 * @property {ActivePromotion[]} [active_promotions] - Lista wszystkich aktywnych promocji
 * @property {string} [created_at] - Data utworzenia
 */

/**
 * Przykład użycia:
 *
 * const product = {
 *   sku: "SKU-001",
 *   name: "Smartwatch Fitness Pro",
 *   price: 299.99,
 *   stock: 50,
 *   status: "active",
 *   channel: "woocommerce",
 *   active_promotion: "Promocja Black Friday - 20% rabatu"
 * }
 */

// Status produktu
export const ProductStatus = {
  ACTIVE: 'active',
  LOW_STOCK: 'low_stock',
  OUT_OF_STOCK: 'out_of_stock',
  INACTIVE: 'inactive'
};

// Kanały sprzedaży
export const Channel = {
  SHOPIFY: 'shopify',
  WOOCOMMERCE: 'woocommerce'
};

// Typy promocji
export const PromotionType = {
  PRICE: 'price',
  BUNDLE: 'bundle',
  PROMO: 'promo'
};

/**
 * Helper do wyświetlania statusu produktu po polsku
 */
export const getStatusLabel = (status) => {
  const labels = {
    'active': 'Aktywny',
    'low_stock': 'Niski stan',
    'out_of_stock': 'Brak w magazynie',
    'inactive': 'Nieaktywny'
  };
  return labels[status] || status;
};

/**
 * Helper do wyświetlania kanału sprzedaży
 */
export const getChannelLabel = (channel) => {
  const labels = {
    'shopify': 'Shopify',
    'woocommerce': 'WooCommerce'
  };
  return labels[channel] || channel;
};

/**
 * Formatowanie ceny
 */
export const formatPrice = (price) => {
  return `${price.toFixed(2)} PLN`;
};
