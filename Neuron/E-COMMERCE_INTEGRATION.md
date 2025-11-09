# E-commerce Platform Integration

This project includes full integration with multiple e-commerce platforms that synchronize your product catalog between your local panel and your online stores.

## Shopify Integration

This project includes full Shopify integration that synchronizes your product catalog between your local panel and your Shopify store.

## WooCommerce Integration

This project also includes full WooCommerce integration that synchronizes your product catalog between your local panel and your WooCommerce store.

## Configuration

The integration uses the following environment variables, which are already configured in your `.env` file:

```env
SHOPIFY_STORE_URL=https://neuron-sp-zoo.myshopify.com/
SHOPIFY_ACCESS_TOKEN=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
SHOPIFY_VENDOR=Synder
```

## How It Works

### Product Synchronization

The integration automatically synchronizes product changes between your local database and Shopify:

1. **Adding Products**:
   - When you create a new product in the local panel, it's automatically created in Shopify
   - Product details (name, description, price, stock, category, photos, technical details) are synchronized
   - The Shopify product ID is stored in the local database for future updates

2. **Updating Products**:
   - When you edit a product in the local panel, the changes are pushed to Shopify
   - All product attributes are updated: name, description, price, stock quantity, category
   - If the product doesn't exist in Shopify, it will be created

3. **Deleting Products**:
   - When you delete a product from the local panel, it's also deleted from Shopify
   - Confirmation is required before deletion

### Database Changes

The integration adds a `shopify_product_id` column to the products table to track the Shopify product ID for synchronization.

### Routes Added

- `/products/<int:product_id>/delete` - Delete product and sync with Shopify

### Template Changes

- Added delete buttons to both `products.html` and `product_form.html` templates
- Confirmation dialogs warn about Shopify synchronization before deletion

## Error Handling

The integration includes comprehensive error handling:

- If a Shopify sync fails, the local operation still completes
- Error messages are logged for troubleshooting
- Products can still be managed locally even if Shopify API is temporarily unavailable

## API Endpoints

The core Shopify integration is in `shopify_integration.py` with these main functions:

- `sync_product_to_shopify()` - Create or update products in Shopify
- `delete_product_from_shopify()` - Remove products from Shopify
- `ShopifyProductSync` class handles all Shopify API interactions

## Shopify Integration Requirements

Make sure your Shopify private app is configured with these permissions:
- Products, variants and collections: Read and write
- Inventory: Read and write
- Images: Read and write

## WooCommerce Integration

The project includes full WooCommerce integration that synchronizes your product catalog between your local panel and your WooCommerce store.

### Configuration

The WooCommerce integration uses these hardcoded credentials (for security, change these in production):

```python
WOOCOMMERCE_URL = "https://neuron-test.wasmer.app"
WOOCOMMERCE_CONSUMER_KEY = "ck_162044d5d1ef3f112204dcf96d3bed1b05ce912c"
WOOCOMMERCE_CONSUMER_SECRET = "cs_fefddc0fed7eb0d7e13af961f273ea447bebcfec"
```

### How WooCommerce Integration Works

The WooCommerce integration automatically synchronizes product changes between your local database and WooCommerce:

1. **Adding Products**:
   - When you create a new product in the local panel, it's automatically created in WooCommerce
   - Product details (name, description, price, stock, categories, images, technical details) are synchronized
   - The WooCommerce product ID is stored in the local database for future updates

2. **Updating Products**:
   - When you edit a product in the local panel, the changes are pushed to WooCommerce
   - All product attributes are updated: name, description, price, stock quantity, categories
   - If the product doesn't exist in WooCommerce, it will be created

3. **Deleting Products**:
   - When you delete a product from the local panel, it's also deleted from WooCommerce
   - Confirmation is required before deletion

### Database Changes

The integration adds a `woocommerce_product_id` column to the products table to track the WooCommerce product ID for synchronization.

### WooCommerce API Endpoints

The core WooCommerce integration is in `woocommerce_integration.py` with these main functions:

- `sync_product_to_woocommerce()` - Create or update products in WooCommerce
- `delete_product_from_woocommerce()` - Remove products from WooCommerce
- `get_woocommerce_product()` - Get product details from WooCommerce
- `WooCommerceProductSync` class handles all WooCommerce API interactions

## Testing Both Integrations

You can verify both integrations are working by:

1. Adding a new product in the local panel
2. Checking that it appears in both your Shopify and WooCommerce stores
3. Updating the product in the local panel
4. Confirming the changes appear in both Shopify and WooCommerce
5. Deleting the product and confirming it's removed from both platforms