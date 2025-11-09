import { storage } from './storage';
import { checkShopifyAlerts } from './shopifyClient';
import { checkSquareAlerts, getDailySalesDataSquare } from './squareClient';
import { getDailySalesData } from './shopifyClient';
import { generateSalesSummary } from './groqClient';
import { sendTelegramAlert } from './telegramBot';

/**
 * Runs alert check every 15 minutes
 * - Low stock alerts
 * - Chargeback/Dispute alerts
 */
export function startAlertCheckScheduler() {
  console.log('📅 Alert check scheduler started (every 15 minutes)');

  // Run immediately on startup
  runAlertCheck();

  // Then run every 15 minutes
  setInterval(() => {
    runAlertCheck();
  }, 15 * 60 * 1000); // 15 minutes in milliseconds
}

async function runAlertCheck() {
  const now = new Date();
  console.log(`\n⏰ Running alert check at ${now.toLocaleTimeString()}`);

  try {
    const platforms = await storage.getPlatforms();
    let totalAlerts = 0;

    for (const platform of platforms) {
      try {
        let alerts = 0;

        if (platform.type === 'Shopify') {
          alerts = await checkShopifyAlerts(platform);
        } else if (platform.type === 'Square') {
          alerts = await checkSquareAlerts(platform);
        }

        totalAlerts += alerts;
        console.log(`✓ ${platform.name} (${platform.type}): ${alerts} alerts`);
      } catch (error: any) {
        console.error(`✗ Error checking platform ${platform.name}:`, error.message);
      }
    }

    console.log(`✅ Alert check completed. Total alerts: ${totalAlerts}`);
  } catch (error: any) {
    console.error('❌ Alert check scheduler error:', error.message);
  }
}

/**
 * Runs daily AI report generation
 * - Generates summary for all platforms
 * - Sends to Telegram at specified time
 */
export function startDailyReportScheduler() {
  console.log('📅 Daily report scheduler started (daily at 08:00)');

  // Calculate milliseconds until next 08:00
  const now = new Date();
  const next = new Date(now);
  next.setHours(8, 0, 0, 0);

  // If it's already past 08:00 today, schedule for tomorrow
  if (next <= now) {
    next.setDate(next.getDate() + 1);
  }

  const timeUntilNext = next.getTime() - now.getTime();
  console.log(`📍 Next daily report: ${next.toLocaleString()}`);

  // Schedule first report
  setTimeout(() => {
    runDailyReport();

    // Then run every 24 hours
    setInterval(() => {
      runDailyReport();
    }, 24 * 60 * 60 * 1000); // 24 hours in milliseconds
  }, timeUntilNext);
}

async function runDailyReport() {
  const now = new Date();
  console.log(`\n📊 Generating daily reports at ${now.toLocaleTimeString()}`);

  try {
    const platforms = await storage.getPlatforms();

    if (platforms.length === 0) {
      console.log('ℹ️  No platforms configured, skipping daily report');
      return;
    }

    let reportMessage = `📊 *DAILY REPORT - ${now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}* 📊\n\n`;
    let reportCount = 0;

    for (const platform of platforms) {
      try {
        console.log(`  Processing ${platform.name} (${platform.type})...`);

        let salesData;

        if (platform.type === 'Shopify') {
          salesData = await getDailySalesData(platform);
        } else if (platform.type === 'Square') {
          salesData = await getDailySalesDataSquare(platform);
        } else {
          continue;
        }

        // Generate AI summary if there are orders
        let summary = 'No orders today. Quiet day! 🤐';
        if (salesData.orderCount > 0) {
          try {
            summary = await generateSalesSummary(salesData);
            console.log(`  ✓ AI Summary generated for ${platform.name}`);
          } catch (error: any) {
            console.error(`  ✗ AI Summary error for ${platform.name}:`, error.message);
            summary = `Orders: ${salesData.orderCount}, Sales: ${salesData.totalSales} ${salesData.currency}`;
          }
        }

        reportMessage += `*${platform.name}* (${platform.type})\n`;
        reportMessage += `📦 Orders: ${salesData.orderCount}\n`;
        reportMessage += `💰 Sales: ${salesData.totalSales} ${salesData.currency}\n`;
        reportMessage += `${summary}\n\n`;
        reportCount++;

      } catch (error: any) {
        console.error(`  ✗ Error processing ${platform.name}:`, error.message);
        reportMessage += `*${platform.name}* - ❌ Error: ${error.message}\n\n`;
      }
    }

    if (reportCount > 0) {
      reportMessage += '---\n✅ Report generated automatically at ' + now.toLocaleTimeString();

      try {
        await sendTelegramAlert(reportMessage);
        console.log(`✅ Daily report sent to Telegram (${reportCount} platform(s))`);
      } catch (error: any) {
        console.error('✗ Error sending daily report:', error.message);
      }
    }
  } catch (error: any) {
    console.error('❌ Daily report scheduler error:', error.message);
  }
}

/**
 * Starts all schedulers
 */
export function startAllSchedulers() {
  console.log('\n🚀 Starting automated schedulers...\n');
  startAlertCheckScheduler();
  startDailyReportScheduler();
  console.log('\n✅ All schedulers started!\n');
}
