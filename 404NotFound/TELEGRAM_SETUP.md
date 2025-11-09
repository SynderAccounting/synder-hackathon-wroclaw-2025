# Telegram Bot Configuration - Guide

## Step 1: Create a new Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send the command `/newbot`
3. Provide a name for your bot (e.g., "Synder Alert Bot")
4. Provide a username for the bot (must end with "bot", e.g., "synder_alert_bot")
5. **BotFather** will send you a token - **COPY IT!**
   - It looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - This is your `TELEGRAM_BOT_TOKEN`

## Step 2: Obtain the Chat ID

### Option A: For a private message (DM)

1. Open a chat with **@userinfobot** or **@RawDataBot**
2. Send any message
3. The bot will return your information, including `Id` — that is your `TELEGRAM_CHAT_ID`

### Option B: For a group

1. Add your bot to the group
2. Send any message in the group (e.g., "/start")
3. Open in the browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
   Replace `<YOUR_TOKEN>` with the token from Step 1
4. Find the field `"chat":{"id": -1001234567890}` — that is your `TELEGRAM_CHAT_ID`
   - IMPORTANT: Group chat IDs start with `-` (minus)

### Option C: For a channel

1. Add your bot as an administrator of the channel
2. Send a message to the channel
3. Open in the browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
4. Find the field `"chat":{"id": -1001234567890}` — that is your `TELEGRAM_CHAT_ID`

## Step 3: Configure environment variables

### Windows (PowerShell)
```powershell
$env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID="123456789"
```

### Windows (CMD)
```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
set TELEGRAM_CHAT_ID=123456789
```

### Linux/macOS
```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="123456789"
```

### .env file (persistent configuration)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your values:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

3. Install `dotenv` if you don't have it:
   ```bash
   npm install dotenv
   ```

4. Add at the top of `server/index.ts`:
   ```typescript
   import 'dotenv/config';
   ```

## Step 4: Testing

1. Start the application:
   ```bash
   npm run dev
   ```

2. Open the dashboard in your browser (default: http://localhost:3000)

3. Click the **"Test Telegram"** button in the top-right corner

4. Verify that the test message arrived in Telegram

## Troubleshooting

### Problem: "Telegram is not configured"
- Fix: Check that the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` variables are set
- Run the `/api/telegram/status` endpoint to see configuration details

### Problem: "Unauthorized" (401)
- Fix: The bot token is invalid
- Check the token in BotFather — send `/mybots` -> choose your bot -> API Token

### Problem: "Bad Request: chat not found" (400)
- Fix: The chat ID is incorrect
- Make sure group/channel Chat IDs start with `-` (minus)
- Ensure the bot is added to the group/channel

### Problem: "Forbidden: bot was blocked by the user" (403)
- Fix: The user blocked the bot
- Unblock the bot or send `/start` to the bot

### Problem: MarkdownV2 parsing error
- Fix: The code automatically falls back to plain text if MarkdownV2 fails
- If the issue persists, check server logs for details

## Debugging

Enable verbose logging in `server/telegramBot.ts`. The project already includes:

- ✅ Detailed logs of message send attempts
- ✅ Automatic fallback from MarkdownV2 to plain text
- ✅ Clear Telegram API error output
- ✅ Configuration validation before sending

Check the server console logs for precise error messages.

## Useful links

- Telegram Bot API Documentation: https://core.telegram.org/bots/api
- BotFather Commands: https://core.telegram.org/bots#botfather
- MarkdownV2 Formatting: https://core.telegram.org/bots/api#markdownv2-style
