# 🔔 Backoffice Notification Assistant

An application for monitoring e-commerce platforms (Shopify) with Telegram notifications.

---

## 🎯 Features

- ✅ Low stock monitoring
- ✅ Chargeback (payment dispute) alerts
- ✅ Real-time Telegram notifications
- ✅ Per-platform thresholds configuration
- ✅ Manual run of checks
- ✅ Material Design UI (Vuetify 3)

---

## 🛠️ Technology Stack

### Frontend
- Vue 3.5.13 — UI framework
- Vuetify 3.7.5 — Material Design components
- TypeScript 5.6.3 — static typing
- Vite 5.4.20 — build tool
- Vue Router 4.5.0 — routing
- TanStack Query (Vue) — server state management

### Backend
- Node.js — runtime
- Express 4.21.2 — web framework
- TypeScript — server typing
- Axios — HTTP client for Shopify and Telegram
- Drizzle ORM 0.39.1 — database ORM (Postgres-ready)
- Zod 3.24.2 — schema validation

### External APIs
- Shopify Admin API — e-commerce integration
- Telegram Bot API — sending notifications

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd synder_hackaton
```

### 2. Install dependencies

```bash
npm install
```

### 3. Telegram configuration

Create an `.env` file in the project root:

```bash
cp .env.example .env
```

Fill in your values in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id
```

Detailed instructions: see `TELEGRAM_SETUP.md` or `TELEGRAM_SETUP_EN.md`.

---

## 🚀 Running

### Development mode

```bash
npm run dev
```

The app is available at: http://localhost:3000

### Production build

```bash
npm run build
npm start
```

### TypeScript checks

```bash
npm run check
```

---

## 📖 Documentation

- `TELEGRAM_SETUP.md` / `TELEGRAM_SETUP_EN.md` — Telegram bot setup (step-by-step)
- `FIXES_TELEGRAM.md` — Telegram bot fixes report
- `MIGRATION_VUE.md` — Migration details from React to Vue 3
- `replit.md` — System architecture and technical notes

---

## 🎨 User Interface

### Main sections

1. Header
   - Telegram connection status
   - Test Telegram button

2. Available platforms
   - Shopify card with option to add a store

3. Connected platforms
   - List of connected stores
   - Alert configuration per store
   - Remove platform option

4. Actions
   - Manual run of alert checks

---

## ⚙️ Shopify platform configuration

1. Click **"Add platform"** on the Shopify card
2. Fill the form:
   - **Store name** (without `.myshopify.com`)
   - **Admin API Access Token** (from Shopify admin)
   - **API Version** (format: `2024-01`)
3. Click **"Add platform"**

### Alert settings

For each platform you can configure:

- Low stock monitoring:
  - Enable/disable
  - Set threshold (default: 10 units)

- Chargeback monitoring:
  - Enable/disable
  - Automatic alerts for new disputes

---

## 🔔 Telegram notifications

### Message format

Low stock:
```
📦 Low Stock Alert

Store: store-name
Product: Product Name - Variant
SKU: SKU123
Remaining: 5 units (Threshold: 10)
```

Chargeback:
```
🔴 NEW CHARGEBACK 🔴

Store: store-name
Order: 123456
Amount: 99.99 USD
Status: Action required
```

---

## 🧪 Testing

### Telegram connection test

1. Ensure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set
2. Click **"Test Telegram"** in the top-right corner
3. Verify the test message arrives in Telegram

### Alert check test

1. Add a Shopify platform with valid credentials
2. Enable low stock or chargeback monitoring
3. Click **"Run check"**
4. Check server logs and Telegram

---

## 🗂️ Project structure

```
synder_hackaton/
├── client/                 # Frontend (Vue 3)
│   ├── src/
│   │   ├── App.vue        # Main component
│   │   ├── main.ts        # Entry point
│   │   ├── plugins/       # Vuetify, Router
│   │   ├── pages/         # Pages (Dashboard, NotFound)
│   │   ├── components/    # Vue components
│   │   └── lib/           # Helpers (API client)
│   └── index.html
├── server/                 # Backend (Express)
│   ├── index.ts           # Server entry point
│   ├── routes.ts          # API endpoints
│   ├── telegramBot.ts     # Telegram integration
│   ├── shopifyClient.ts   # Shopify API client
│   └── storage.ts         # In-memory storage
├── shared/                 # Shared code
│   └── schema.ts          # Zod schemas + TypeScript types
├── .env.example           # Config template
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## 🔐 Security

- ✅ Credentials are never returned by the API — only `hasCredentials: boolean`
- ✅ Strict Zod validation — all inputs are validated
- ✅ MarkdownV2 escaping — protects Telegram from injection
- ✅ HTTPS for Shopify and Telegram APIs
- ✅ Environment variables for secrets (not stored in repo)

---

## 📊 API Endpoints

### Platforms

- `GET /api/platforms` — Get all platforms (without credentials)
- `POST /api/platforms` — Add a new platform
- `POST /api/platforms/:id/settings` — Update platform settings
- `DELETE /api/platforms/:id` — Remove a platform

### Telegram

- `GET /api/telegram/status` — Check Telegram connection status
- `POST /api/test/telegram` — Send a test message

### Checks

- `POST /api/check/run` — Manually run alert checks

---

## 🐛 Troubleshooting

### Telegram not sending messages

1. Check environment variables:
   ```bash
   echo $TELEGRAM_BOT_TOKEN
   echo $TELEGRAM_CHAT_ID
   ```

2. Check the status endpoint:
   ```bash
   curl http://localhost:3000/api/telegram/status
   ```

3. Check server logs

More details: `FIXES_TELEGRAM.md`

### TypeScript errors

```bash
npm run check
```

### Installation problems

```bash
rm -rf node_modules package-lock.json
npm install
```

---

## 📈 Future improvements

- [ ] Migrate to PostgreSQL (Drizzle ORM ready)
- [ ] Scheduled periodic checks every X minutes
- [ ] Support for more platforms (WooCommerce, Magento)
- [ ] Dashboard with charts and analytics
- [ ] Webhooks instead of polling
- [ ] Export reports to CSV/PDF
- [ ] User roles and authentication

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

MIT

---

## 👨‍💻 Author

Synder Hackathon 2025

---

## 🙏 Thanks

- Vue.js Team — Framework
- Vuetify Team — Material components
- Telegram — Bot API
- Shopify — Admin API

---

**Version:** 1.0.0 (Vue 3 Migration)
**Date:** 2025-11-09
