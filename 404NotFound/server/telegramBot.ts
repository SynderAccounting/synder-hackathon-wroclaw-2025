import axios from 'axios';

/**
 * Escape special characters for MarkdownV2 format
 * See: https://core.telegram.org/bots/api#markdownv2-style
 */
function escapeMarkdownV2(text: string): string {
  // Characters that need to be escaped: _ * [ ] ( ) ~ ` > # + - = | { } . !
  return text.replace(/([_*\[\]()~`>#+=|{}.!-])/g, '\\$1');
}

/**
 * Send a message to Telegram using plain text (no formatting)
 * This is more reliable when markdown formatting causes issues
 */
export async function sendTelegramMessage(message: string, useMarkdown = false): Promise<void> {
  const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;

  if (!TELEGRAM_TOKEN || !TELEGRAM_CHAT_ID) {
    const errorMsg = "ERROR: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment variables.";
    console.error(errorMsg);
    console.error(`Token: ${TELEGRAM_TOKEN ? 'SET' : 'NOT SET'}, Chat ID: ${TELEGRAM_CHAT_ID ? 'SET' : 'NOT SET'}`);
    throw new Error("Telegram credentials not configured");
  }

  const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;

  // Prepare payload - use plain text by default, MarkdownV2 only if requested
  const payload: any = {
    chat_id: TELEGRAM_CHAT_ID,
    text: useMarkdown ? escapeMarkdownV2(message) : message,
  };

  // Only add parse_mode if using markdown
  if (useMarkdown) {
    payload.parse_mode = 'MarkdownV2';
  }

  try {
    console.log(`📤 Sending message to Telegram (format: ${useMarkdown ? 'MarkdownV2' : 'plain text'})...`);
    console.log(`📨 Chat ID: ${TELEGRAM_CHAT_ID}`);

    const response = await axios.post(url, payload, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
      validateStatus: (status) => status < 500, // Don't throw on 4xx errors
    });

    if (response.status === 200) {
      console.log("✓ Telegram message sent successfully!");
      console.log(`✓ Message ID: ${response.data.result?.message_id}`);
    } else {
      console.error("✗ Telegram API returned error:", response.status, response.data);
      throw new Error(`Telegram API error: ${JSON.stringify(response.data)}`);
    }
  } catch (error: any) {
    if (error.response) {
      // Telegram API returned an error
      const errorDetails = error.response.data;
      console.error("✗ Telegram API Error:", JSON.stringify(errorDetails, null, 2));
      console.error("✗ HTTP Status:", error.response.status);

      // If markdown parsing failed, try again with plain text
      if (useMarkdown && errorDetails?.description?.includes('parse')) {
        console.warn("⚠ Markdown parsing error, retrying without formatting...");
        return sendTelegramMessage(message, false);
      }

      throw new Error(`Telegram API error: ${errorDetails.description || JSON.stringify(errorDetails)}`);
    } else if (error.request) {
      // Request was made but no response received
      console.error("✗ No response from Telegram API");
      console.error("✗ Check internet connection and bot token");
      throw new Error("No response from Telegram API");
    } else {
      // Something else happened
      console.error("✗ Sending error:", error.message);
      throw error;
    }
  }
}

/**
 * Send alert with MarkdownV2 formatting (with fallback to plain text)
 * Legacy function - kept for backward compatibility
 */
export async function sendTelegramAlert(message: string): Promise<void> {
  // Try with plain text for better reliability
  return sendTelegramMessage(message, false);
}
