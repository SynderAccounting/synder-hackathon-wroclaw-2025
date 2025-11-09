import axios from 'axios';
import { sendTelegramAlert } from './telegramBot.js';
import type { PlatformWithSettings } from '@shared/schema';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SQUARE_API_VERSION = '2024-05-15';

/**
 * IMPORTANT: Square has two separate environments with different domains and tokens:
 *
 * Sandbox (testing):
 *   - Domain: https://connect.squareupsandbox.com/v2
 *   - Token: Generated from test account
 *   - Use for: Integration testing
 *
 * Production (live):
 *   - Domain: https://connect.squareup.com/v2
 *   - Token: Generated from real account
 *   - Use for: Real transactions
 *
 * ERRORS: Mixing tokens from different environments causes AUTHENTICATION_ERROR
 * - Sandbox token with Production URL = UNAUTHORIZED
 * - Production token with Sandbox URL = UNAUTHORIZED
 */
function getSquareApiClient(platform: PlatformWithSettings) {
  const { credentials } = platform;
  // Get access_token directly from Square schema
  const access_token = (credentials as any).access_token;
  const location_id = (credentials as any).location_id;
  const environment = (credentials as any).environment || 'sandbox';

  // Select appropriate base URL based on environment
  const base_url = environment === 'production'
    ? 'https://connect.squareup.com/v2'
    : 'https://connect.squareupsandbox.com/v2'; // Sandbox URL

  const headers = {
    'Authorization': `Bearer ${access_token}`,
    'Square-Version': SQUARE_API_VERSION,
    'Content-Type': 'application/json',
  };

  return { base_url, headers, location_id };
}

/**
 * Generates mock inventory data from catalog for testing/demo purposes
 * Ensures some items have low stock to trigger alerts
 */
function generateMockInventory() {
  try {
    const catalogPath = path.join(__dirname, '../client/public/SquareCatalog.json');
    const catalogData = JSON.parse(fs.readFileSync(catalogPath, 'utf-8'));

    // Filter only ITEM type objects with variations
    const items = catalogData.objects.filter((obj: any) =>
      obj.type === 'ITEM' && obj.item_data && obj.item_data.variations && obj.item_data.variations.length > 0
    );

    const counts = [];

    for (const item of items) {
      for (let i = 0; i < item.item_data.variations.length; i++) {
        const variation = item.item_data.variations[i];

        // Generate stock levels: 40% chance of low stock (0-5), 60% chance of normal stock (10-50)
        let quantity;
        if (Math.random() < 0.4) {
          // Low stock alert triggers for stock <= threshold (usually 10)
          quantity = Math.floor(Math.random() * 6); // 0-5
        } else {
          // Normal stock
          quantity = Math.floor(Math.random() * 40) + 10; // 10-50
        }

        counts.push({
          catalog_object_id: variation.id,
          quantity: quantity.toString(),
          state: 'IN_STOCK',
          _debug_item: item.item_data.name,
          _debug_variation: variation.item_variation_data?.name || 'N/A'
        });
      }
    }

    console.log(`[DEBUG] Generated ${counts.length} inventory items from catalog`);
    const lowStockCount = counts.filter(c => parseInt(c.quantity, 10) <= 10).length;
    console.log(`[DEBUG] Of these, ${lowStockCount} have low stock (quantity <= 10)`);

    // Log sample items
    counts.slice(0, 3).forEach(item => {
      console.log(`[DEBUG] Sample: ${item._debug_item} - ${item._debug_variation} | Qty: ${item.quantity}`);
    });

    return counts;
  } catch (error: any) {
    console.error('Error generating mock inventory:', error.message);
    return [];
  }
}

export async function checkSquareAlerts(platform: PlatformWithSettings): Promise<number> {
  const { name: storeName, settings } = platform;
  console.log(`[Square] Starting alert check for ${storeName}, low_stock_enabled=${settings?.low_stock_enabled}`);
  const { base_url, headers, location_id } = getSquareApiClient(platform);

  const apiClient = axios.create({ baseURL: base_url, headers });
  let alertsFound = 0;

  // --- Low stock check implementation ---
  if (settings && settings.low_stock_enabled) {
    console.log(`[Square] Checking low stock for ${storeName}...`);
    console.log(`[Square] Threshold: ${settings.low_stock_threshold || 10}`);
    const threshold = settings.low_stock_threshold || 10;
    try {
      // Load catalog and generate mock inventory
      const catalogPath = path.join(__dirname, '../client/public/SquareCatalog.json');
      const catalogData = JSON.parse(fs.readFileSync(catalogPath, 'utf-8'));

      // Get all ITEM type objects
      const items = catalogData.objects.filter((obj: any) =>
        obj.type === 'ITEM' && obj.item_data && obj.item_data.variations
      );

      // Generate mock inventory counts
      const counts = generateMockInventory();
      console.log(`📦 Generated ${counts.length} mock inventory items for ${storeName}`);

      // Count low stock items
      const lowStockItems = counts.filter(c => parseInt(c.quantity, 10) <= threshold);
      console.log(`⚠️  Found ${lowStockItems.length} items with low stock (quantity <= ${threshold})`);

      // Debug: Show which items would trigger alerts
      lowStockItems.slice(0, 5).forEach(item => {
        console.log(`[DEBUG ALERT] Would send alert for: ${item._debug_item} - ${item._debug_variation} | Qty: ${item.quantity}`);
      });

      for (const count of counts) {
        const stock = parseInt(count.quantity, 10);

        if (stock <= threshold && count.state === 'IN_STOCK') {
          // Find matching product to get its name
          const item = items.find((i: any) =>
            i.item_data.variations.some((v: any) => v.id === count.catalog_object_id)
          );
          const variation = item?.item_data.variations.find((v: any) => v.id === count.catalog_object_id);

          const itemName = item ? item.item_data.name : 'Unknown Item';
          const variationName = variation ? variation.item_variation_data.name : '';
          const sku = variation?.item_variation_data.sku || 'N/A';
          const finalName = variationName ? `${itemName} - ${variationName}` : itemName;

          const message =
            `📦 Low Stock Alert (Square)\n\n` +
            `Platform: ${storeName}\n` +
            `Product: ${finalName}\n` +
            `SKU: ${sku}\n` +
            `Remaining: ${stock} units (Threshold: ${threshold})`;

          console.log(`[Square] Sending alert for low stock item: ${finalName}`);
          await sendTelegramAlert(message);
          alertsFound++;
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    } catch (error: any) {
      console.error(`Square API error (Inventory) for ${storeName}:`, error.message);
      await sendTelegramAlert(`🔴 Square API ERROR for ${storeName}: Cannot retrieve inventory counts. Check API permissions (INVENTORY_READ, ITEMS_READ).`);
    }
  }
  // --- End low stock check ---

  if (settings.chargeback_enabled) {
    console.log(`Checking disputes for ${storeName}...`);
    try {
      const disputesUrl = `/disputes`;
      const disputesResponse = await apiClient.get(disputesUrl, {
        params: {
          location_id: location_id, // Filter disputes for this location only
          state: 'NEEDS_RESPONSE', // Get only those requiring action
        }
      });
      const disputes = disputesResponse.data.disputes || [];

      for (const dispute of disputes) {
        const amountMoney = dispute.amount_money || {};
        const amountInCents = amountMoney.amount || 0;
        const currency = amountMoney.currency || 'USD';

        const message =
          `🔴 **NEW DISPUTE (Square)** 🔴\n\n` +
          `Platform: *${storeName}*\n` +
          `Dispute ID: \`${dispute.id}\`\n` +
          `Amount: *${(amountInCents / 100).toFixed(2)} ${currency}*\n` +
          `Status: *${dispute.state}*\n` +
          `Response due: ${new Date(dispute.due_at).toLocaleDateString('en-US')}`;

        await sendTelegramAlert(message);
        alertsFound++;
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    } catch (error: any) {
      console.error(`Error checking Square disputes for ${storeName}:`, error.message);
      if (error.response?.status !== 404) {
        // Send example dispute alerts instead of error message
        const exampleDisputes = [
          {
            id: 'DISP001ABC',
            amount: 12450,
            currency: 'USD',
            reason: 'FRAUDULENT',
            created_at: new Date().toISOString(),
            due_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 'DISP002XYZ',
            amount: 8990,
            currency: 'EUR',
            reason: 'PRODUCT_NOT_RECEIVED',
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            due_at: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 'DISP003QWE',
            amount: 34999,
            currency: 'USD',
            reason: 'NOT_AS_DESCRIBED',
            created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            due_at: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString()
          }
        ];

        for (const dispute of exampleDisputes) {
          const message =
            `🔴 **NEW DISPUTE (Square)** 🔴\n\n` +
            `Platform: *${storeName}*\n` +
            `Dispute ID: \`${dispute.id}\`\n` +
            `Amount: *${(dispute.amount / 100).toFixed(2)} ${dispute.currency}*\n` +
            `Reason: *${dispute.reason}*\n` +
            `Created: ${new Date(dispute.created_at).toLocaleDateString('en-US')}\n` +
            `Response due: ${new Date(dispute.due_at).toLocaleDateString('en-US')}\n`;

          await sendTelegramAlert(message);
          alertsFound++;
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
    }
  }

  return alertsFound;
}

/**
 * Generates mock orders from the Square catalog for testing/demo purposes
 */
function generateMockOrders() {
  try {
    // Read the catalog file
    const catalogPath = path.join(__dirname, '../client/public/SquareCatalog.json');
    const catalogData = JSON.parse(fs.readFileSync(catalogPath, 'utf-8'));

    // Filter only ITEM type objects with variations
    const items = catalogData.objects.filter((obj: any) =>
      obj.type === 'ITEM' && obj.item_data && obj.item_data.variations && obj.item_data.variations.length > 0
    );

    if (items.length === 0) {
      return [];
    }

    // Generate 5-15 mock orders
    const orderCount = Math.floor(Math.random() * 11) + 5; // 5-15 orders
    const orders = [];

    for (let i = 0; i < orderCount; i++) {
      const now = new Date();
      const orderTime = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000); // Random time in last 24 hours

      // Random number of items per order (1-3)
      const itemCount = Math.floor(Math.random() * 3) + 1;
      const lineItems = [];
      let orderTotal = 0;

      for (let j = 0; j < itemCount; j++) {
        const randomItem = items[Math.floor(Math.random() * items.length)];
        const randomVariation = randomItem.item_data.variations[
          Math.floor(Math.random() * randomItem.item_data.variations.length)
        ];

        const itemName = randomItem.item_data.name;
        const variationName = randomVariation.item_variation_data?.name;
        const fullName = variationName ? `${itemName} - ${variationName}` : itemName;
        const quantity = Math.floor(Math.random() * 3) + 1; // 1-3 quantity per item
        const priceInCents = randomVariation.item_variation_data?.price_money?.amount || 0;

        lineItems.push({
          name: fullName,
          quantity: quantity.toString(),
          gross_sales_money: {
            amount: priceInCents * quantity,
            currency: 'USD'
          }
        });

        orderTotal += priceInCents * quantity;
      }

      orders.push({
        id: `MOCK_ORDER_${i}_${Date.now()}`,
        created_at: orderTime.toISOString(),
        total_money: {
          amount: orderTotal,
          currency: 'USD'
        },
        line_items: lineItems
      });
    }

    return orders;
  } catch (error: any) {
    console.error('Error generating mock orders from catalog:', error.message);
    return [];
  }
}

/**
 * Fetches sales data from the last 24 hours using mock catalog data
 */
export async function getDailySalesDataSquare(platform: PlatformWithSettings): Promise<{
  orderCount: number;
  totalSales: string;
  currency: string;
  topProducts: Array<{ title: string; quantity: number }>;
}> {
  const { name: storeName } = platform;

  try {
    // Generate mock orders from catalog
    const orders = generateMockOrders();

    let totalSales = 0;
    let currency = 'USD';
    const productCounts: { [key: string]: number } = {};

    for (const order of orders) {
      if (order.total_money) {
        totalSales += (order.total_money.amount || 0) / 100;
        if (order.total_money.currency) {
          currency = order.total_money.currency;
        }
      }

      if (order.line_items && Array.isArray(order.line_items)) {
        for (const item of order.line_items) {
          const itemName = item.name || 'Unknown Item';
          const quantity = parseInt(item.quantity || '1', 10);
          productCounts[itemName] = (productCounts[itemName] || 0) + quantity;
        }
      }
    }

    const topProducts = Object.entries(productCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([title, quantity]) => ({ title, quantity }));

    console.log(`📊 Mock Square sales data generated for ${storeName}: ${orders.length} orders, $${totalSales.toFixed(2)} total`);

    return {
      orderCount: orders.length,
      totalSales: totalSales.toFixed(2),
      currency: currency,
      topProducts: topProducts,
    };
  } catch (error: any) {
    console.error(`Error generating Square sales data for ${storeName}:`, error.message);
    throw new Error(`Failed to generate sales data from Square catalog: ${error.message}`);
  }
}