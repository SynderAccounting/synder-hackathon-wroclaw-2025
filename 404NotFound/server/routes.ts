import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertPlatformSchema, platformSettingsSchema } from "@shared/schema";
import { checkShopifyAlerts, getShopifyProductsWithFullInfo, getDailySalesData } from "./shopifyClient";
import { checkSquareAlerts, getDailySalesDataSquare } from "./squareClient";
import { generateSalesSummary } from "./groqClient";
import { sendTelegramAlert } from "./telegramBot";

export async function registerRoutes(app: Express): Promise<Server> {
  app.get("/api/platforms", async (_req, res) => {
    const platforms = await storage.getPlatformsPublic();
    res.json(platforms);
  });

  app.post("/api/platforms", async (req, res) => {
    try {
      const validatedData = insertPlatformSchema.parse(req.body);
      const platform = await storage.createPlatform(validatedData);
      const { credentials, ...publicPlatform } = platform;
      res.status(201).json({ ...publicPlatform, hasCredentials: !!credentials });
    } catch (error: any) {
      const message = error.errors ? error.errors.map((e: any) => e.message).join(", ") : "Invalid platform data";
      res.status(400).json({ error: message });
    }
  });

  app.post("/api/platforms/:id/settings", async (req, res) => {
    try {
      const { id } = req.params;
      const validatedSettings = platformSettingsSchema.parse(req.body);
      const platform = await storage.updatePlatformSettings(id, validatedSettings);
      
      if (!platform) {
        return res.status(404).json({ error: "Platform not found" });
      }
      
      const { credentials, ...publicPlatform } = platform;
      res.json({ ...publicPlatform, hasCredentials: !!credentials });
    } catch (error) {
      res.status(400).json({ error: "Invalid settings data" });
    }
  });

  app.delete("/api/platforms/:id", async (req, res) => {
    const { id } = req.params;
    const deleted = await storage.deletePlatform(id);

    if (!deleted) {
      return res.status(404).json({ error: "Platform not found" });
    }

    res.status(204).send();
  });

  app.get("/api/platforms/:id/shopify/products", async (req, res) => {
    try {
      const { id } = req.params;
      const { limit = '50', status, since_id } = req.query;

      // Get platform from storage
      const platforms = await storage.getPlatforms();
      const platform = platforms.find(p => p.id === id);

      if (!platform) {
        return res.status(404).json({ error: "Platform not found" });
      }

      if (platform.type !== 'Shopify') {
        return res.status(400).json({ error: "Platform is not a Shopify store" });
      }

      const params = {
        limit: limit as string,
        ...(status && { status: status as string }),
        ...(since_id && { since_id: since_id as string })
      };

      const result = await getShopifyProductsWithFullInfo(platform, params);

      res.json({
        success: true,
        data: result,
        message: 'Products with full information successfully retrieved'
      });
    } catch (error: any) {
      console.error("Error fetching Shopify products:", error);
      res.status(500).json({
        error: "Failed to fetch products",
        details: error.message
      });
    }
  });

  app.get("/api/telegram/status", async (_req, res) => {
    const hasToken = !!process.env.TELEGRAM_BOT_TOKEN;
    const hasChatId = !!process.env.TELEGRAM_CHAT_ID;
    const connected = hasToken && hasChatId;

    res.json({
      connected,
      hasToken,
      hasChatId,
      tokenLength: process.env.TELEGRAM_BOT_TOKEN?.length || 0,
      chatIdValue: process.env.TELEGRAM_CHAT_ID ? `${process.env.TELEGRAM_CHAT_ID.substring(0, 3)}...` : 'not set'
    });
  });

  app.post("/api/test/telegram", async (_req, res) => {
    try {
      // Check if credentials are configured first
      if (!process.env.TELEGRAM_BOT_TOKEN || !process.env.TELEGRAM_CHAT_ID) {
        return res.status(400).json({
          error: "Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment variables."
        });
      }

      const testMessage =
        `🔔 Test Message\n\n` +
        `Notification system is working correctly!\n` +
        `Time: ${new Date().toLocaleString('en-US')}`;

      const { sendTelegramAlert } = await import("./telegramBot");
      await sendTelegramAlert(testMessage);

      res.json({
        success: true,
        message: "Test message sent successfully"
      });
    } catch (error: any) {
      console.error("Error sending test message:", error);
      res.status(500).json({
        error: "Failed to send test message",
        details: error.message
      });
    }
  });

  app.post("/api/check/run", async (_req, res) => {
    console.log("Running manual alert check...");
    res.json({ message: "Check started. Alerts will appear on Telegram." });

    (async () => {
      let totalAlerts = 0;
      const platforms = await storage.getPlatforms();
      for (const platform of platforms) {
        if (platform.type === 'Shopify') {
          try {
            const alerts = await checkShopifyAlerts(platform);
            totalAlerts += alerts;
          } catch (error: any) {
            console.error(`Error checking platform ${platform.name}:`, error.message);
          }
        } else if (platform.type === 'Square') {
          try {
            const alerts = await checkSquareAlerts(platform);
            totalAlerts += alerts;
          } catch (error: any) {
            console.error(`Error checking platform ${platform.name}:`, error.message);
          }
        }
      }
      console.log(`Check completed. Found ${totalAlerts} alerts.`);
    })();
  });

  // Analytics endpoint
  app.get("/api/analytics", async (req, res) => {
    try {
      const period = req.query.period || '30d';
      const platforms = await storage.getPlatforms();

      // Generate mock analytics data
      // In production, this would query actual sales data from platforms or database
      const analyticsData = await generateAnalyticsData(platforms, period as string);

      res.json(analyticsData);
    } catch (error: any) {
      console.error("Error generating analytics:", error);
      res.status(500).json({ error: "Failed to generate analytics data" });
    }
  });

  // Returns & Refunds endpoint
  app.get("/api/analytics/returns", async (req, res) => {
    try {
      const period = req.query.period || '30d';
      const platforms = await storage.getPlatforms();

      // Generate mock returns/refunds data
      // In production, this would query actual returns data from platforms
      const returnsData = await generateReturnsData(platforms, period as string);

      res.json(returnsData);
    } catch (error: any) {
      console.error("Error generating returns data:", error);
      res.status(500).json({ error: "Failed to generate returns data" });
    }
  });

  app.post("/api/generate-summary/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const platforms = await storage.getPlatforms();
      const platform = platforms.find(p => p.id === id);

      if (!platform) {
        return res.status(404).json({ message: "Platform not found" });
      }

      if (platform.type !== 'Shopify') {
        return res.status(400).json({ message: "This function is available only for Shopify" });
      }

      console.log(`Generating AI summary for ${platform.name}...`);

      // 1. Fetch data from Shopify
      console.log("Step 1: Fetching data from Shopify...");
      const salesData = await getDailySalesData(platform);
      console.log("Sales data:", salesData);

      let summary = "";
      if (salesData.orderCount === 0) {
        console.log("No orders - using default message");
        summary = "No orders today. Quiet day!";
      } else {
        // 2. Send data to Groq for analysis
        console.log("Step 2: Sending to Groq...");
        summary = await generateSalesSummary(salesData, platform.type);
        console.log("Generated summary:", summary);
      }

      // 3. Send AI summary to Telegram
      console.log("Step 3: Sending to Telegram...");
      const telegramMessage = `📊 Daily AI Summary (Groq) 📊\n\n${summary}`;
      await sendTelegramAlert(telegramMessage);
      console.log("Telegram message sent");

      // 4. Return response to frontend
      res.json({ success: true, summary });

    } catch (error: any) {
      console.error("❌ Error in endpoint /api/generate-summary:", error.message);
      console.error("Full error:", error);
      res.status(500).json({ message: error.message || "Unknown error" });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}

// Helper function to generate analytics data
async function generateAnalyticsData(platforms: any[], period: string) {
  const days = period === '7d' ? 7 : period === '30d' ? 30 : 90;
  const now = new Date();

  // Mock data generation - replace with actual data from platforms in production
  const totalSales = Math.floor(Math.random() * 500000) + 100000;
  const totalOrders = Math.floor(Math.random() * 1000) + 200;
  const totalVisitors = Math.floor(Math.random() * 10000) + 2000;

  // Generate sales trend
  const salesTrend = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    salesTrend.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      sales: Math.floor(Math.random() * (totalSales / days)) + (totalSales / days / 2)
    });
  }

  // Generate conversion trend
  const conversionTrend = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    conversionTrend.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      rate: Math.random() * 5 + 2
    });
  }

  // Generate sales by platform
  const salesByPlatform = platforms.map(platform => ({
    platform: platform.name,
    sales: Math.floor(Math.random() * 100000) + 10000,
    orders: Math.floor(Math.random() * 200) + 50
  }));

  // Generate AOV trend by platform
  const aovTrend = platforms.map(platform => ({
    platform: platform.name,
    aov: Math.floor(Math.random() * 200) + 50
  }));

  // Get low stock products from real data
  const lowStockProducts: any[] = [];

  // Process each Shopify platform to get real products
  for (const platform of platforms) {
    if (platform.type === 'Shopify') {
      try {
        const productsData = await getShopifyProductsWithFullInfo(platform, { limit: '50' });

        if (productsData && productsData.products) {
          for (const product of productsData.products) {
            const threshold = platform.settings?.low_stock_threshold || 10;
            const totalStock = product._meta?.total_inventory || 0;

            // Include all products, but especially those with low stock
            if (totalStock <= threshold) {
              product.variants.forEach((variant: any) => {
                const totalVariantStock = variant.inventory_details?.reduce(
                  (sum: number, inv: any) => sum + (inv.available || 0),
                  0
                ) || 0;

                lowStockProducts.push({
                  id: variant.id.toString(),
                  name: `${product.title}${variant.title !== 'Default Title' ? ` - ${variant.title}` : ''}`,
                  sku: variant.sku || 'N/A',
                  platform: platform.name,
                  stock: totalVariantStock,
                  threshold,
                  image: variant.image_url || product.image?.src || undefined,
                  productUrl: `https://${platform.name}.myshopify.com/admin/products/${product.id}`
                });
              });
            }
          }
        }
      } catch (error: any) {
        console.error(`Error fetching real products for ${platform.name}:`, error.message);
        // Fallback to mock data if real data fails
      }
    }
  }

  // If we don't have enough real products, add some mock ones for Square platforms
  if (lowStockProducts.length < 5) {
    for (let i = lowStockProducts.length; i < Math.min(10, platforms.length * 3); i++) {
      const platform = platforms[Math.floor(Math.random() * platforms.length)];
      const stock = Math.floor(Math.random() * 10);
      const threshold = platform.settings?.low_stock_threshold || 10;

      lowStockProducts.push({
        id: `product-${i}`,
        name: `${platform.type === 'Square' ? 'Square ' : ''}Product ${i + 1}`,
        sku: `SKU-${1000 + i}`,
        platform: platform.name,
        stock,
        threshold,
        image: `https://picsum.photos/seed/${i}/100/100`,
        productUrl: platform.type === 'Shopify'
          ? `https://${platform.name}.myshopify.com/admin/products/${i}`
          : '#'
      });
    }
  }

  return {
    totalSales,
    salesGrowth: Math.random() * 20 + 5,
    averageOrder: totalSales / totalOrders,
    totalOrders,
    conversionRate: (totalOrders / totalVisitors) * 100,
    totalVisitors,
    lowStockCount: lowStockProducts.length,
    lowStockProducts: lowStockProducts.slice(0, 10).sort((a, b) => a.stock - b.stock),
    salesByPlatform,
    salesTrend,
    conversionTrend,
    aovTrend
  };
}

// Helper function to generate returns/refunds data
async function generateReturnsData(platforms: any[], period: string) {
  const days = period === '7d' ? 7 : period === '30d' ? 30 : 90;
  const now = new Date();

  // Mock data generation - replace with actual data from platforms in production
  const totalReturns = Math.floor(Math.random() * 50) + 10;
  const totalRefundAmount = Math.floor(Math.random() * 10000) + 2000;
  const totalReturnedItems = Math.floor(Math.random() * 100) + 20;

  // Calculate return rate (typically 2-5% of orders)
  const returnRate = (Math.random() * 3 + 2).toFixed(2);

  // Generate returns trend over time
  const returnsTrend = [];
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    returnsTrend.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      returns: Math.floor(Math.random() * 5) + 1,
      refundAmount: Math.floor(Math.random() * 500) + 100
    });
  }

  // Generate returns by platform
  // Use default platforms if none are configured
  const platformsForReturns = platforms.length > 0 ? platforms : [
    { name: 'Shopify Store', type: 'Shopify' },
    { name: 'Square POS', type: 'Square' }
  ];

  const returnsByPlatform = platformsForReturns.map(platform => {
    const platformReturns = Math.floor(Math.random() * 20) + 2;
    const platformRefunds = Math.floor(Math.random() * 3000) + 500;
    return {
      platform: platform.name,
      returns: platformReturns,
      refundAmount: platformRefunds,
      returnRate: ((platformReturns / (Math.random() * 100 + 50)) * 100).toFixed(2)
    };
  });

  // Generate return reasons distribution
  const returnReasons = [
    { reason: 'Wrong Size/Fit', count: Math.floor(Math.random() * 15) + 5, percentage: 0 },
    { reason: 'Defective/Damaged', count: Math.floor(Math.random() * 10) + 3, percentage: 0 },
    { reason: 'Not as Described', count: Math.floor(Math.random() * 8) + 2, percentage: 0 },
    { reason: 'Changed Mind', count: Math.floor(Math.random() * 12) + 4, percentage: 0 },
    { reason: 'Better Price Found', count: Math.floor(Math.random() * 5) + 1, percentage: 0 },
    { reason: 'Other', count: Math.floor(Math.random() * 6) + 2, percentage: 0 }
  ];

  const totalReasonCount = returnReasons.reduce((sum, r) => sum + r.count, 0);
  returnReasons.forEach(r => {
    r.percentage = parseFloat(((r.count / totalReasonCount) * 100).toFixed(1));
  });

  // Generate detailed returns list
  const recentReturns = [];
  const statuses = ['Pending', 'Approved', 'Refunded', 'Rejected', 'Processing'];
  const products = [
    'Wireless Headphones Pro',
    'Smart Watch Series 5',
    'USB-C Cable 2m',
    'Laptop Stand Aluminum',
    'Mechanical Keyboard RGB',
    'Webcam HD 1080p',
    'Phone Case Premium',
    'Bluetooth Speaker',
    'Gaming Mouse',
    'Screen Protector'
  ];

  // Default platforms if none exist
  const defaultPlatforms = platforms.length > 0 ? platforms : [
    { name: 'Shopify Store', type: 'Shopify' },
    { name: 'Square POS', type: 'Square' }
  ];

  for (let i = 0; i < Math.min(15, totalReturns); i++) {
    const platform = defaultPlatforms[Math.floor(Math.random() * defaultPlatforms.length)];
    const returnDate = new Date(now);
    returnDate.setDate(returnDate.getDate() - Math.floor(Math.random() * days));
    const refundAmount = Math.floor(Math.random() * 300) + 20;
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const reason = returnReasons[Math.floor(Math.random() * returnReasons.length)].reason;

    recentReturns.push({
      id: `RET-${1000 + i}`,
      orderId: `ORD-${2000 + Math.floor(Math.random() * 1000)}`,
      productName: products[Math.floor(Math.random() * products.length)],
      platform: platform.name,
      reason,
      status,
      refundAmount,
      returnDate: returnDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      customerName: `Customer ${i + 1}`,
      sku: `SKU-${Math.floor(Math.random() * 9000) + 1000}`
    });
  }

  // Sort by most recent first
  recentReturns.sort((a, b) => new Date(b.returnDate).getTime() - new Date(a.returnDate).getTime());

  // Calculate average refund amount
  const avgRefundAmount = totalRefundAmount / totalReturns;

  // Generate refund status breakdown
  const refundStatusBreakdown = {
    pending: Math.floor(totalReturns * 0.2),
    approved: Math.floor(totalReturns * 0.15),
    refunded: Math.floor(totalReturns * 0.55),
    rejected: Math.floor(totalReturns * 0.05),
    processing: Math.floor(totalReturns * 0.05)
  };

  return {
    totalReturns,
    totalRefundAmount,
    totalReturnedItems,
    returnRate: parseFloat(returnRate),
    avgRefundAmount,
    returnsTrend,
    returnsByPlatform,
    returnReasons,
    recentReturns,
    refundStatusBreakdown,
    // Comparison with previous period
    returnsGrowth: (Math.random() * 20 - 10).toFixed(2), // Can be negative
    refundAmountGrowth: (Math.random() * 25 - 12).toFixed(2)
  };
}
