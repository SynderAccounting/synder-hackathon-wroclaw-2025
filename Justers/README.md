# AI Adviser - Intelligent Inventory Management System

An AI-powered inventory management application that helps businesses make data-driven decisions about stock levels, reordering, and supply chain optimization using real-time analytics and Claude AI recommendations.

## Problem Statement

E-commerce businesses face significant challenges in inventory management:

- **Overstocking** leads to increased carrying costs and tied-up capital
- **Understocking** results in lost sales and dissatisfied customers
- **Manual analysis** of sales data is time-consuming and error-prone
- **Lack of actionable insights** from disparate data sources (sales platforms, warehouses, suppliers)
- **Uncertainty** about optimal reorder quantities and timing

**AI Adviser solves these problems** by automatically aggregating data from multiple sources (Shopify, Baselinker), analyzing historical trends, and providing AI-driven recommendations with detailed financial forecasts.

## Key Features

### 📊 Real-Time Product Analytics
- **Stock Monitoring**: Live inventory levels across all warehouses
- **Sales Tracking**: 30-day sales history and velocity calculations
- **Profit Analysis**: Automatic calculation of monthly net profit (revenue - COGS)
- **Color-Coded Indicators**: Visual alerts for low stock and profitability issues

### 🤖 AI-Powered Recommendations
- **Intelligent Reordering**: Claude AI analyzes your data and suggests optimal order quantities
- **Financial Forecasts**: 5 key metrics for each recommendation:
  - Expected Revenue
  - Expected Profit
  - Carrying Cost (inventory holding costs)
  - Stockout Loss (potential lost sales)
  - Opportunity Cost (capital tied in excess inventory)
- **Dynamic TTL**: Recommendations expire based on product velocity (2-72 hours)

### 💬 Interactive AI Chat
- **Multi-Turn Conversations**: Ask follow-up questions and get detailed explanations
- **Context Awareness**: AI remembers your conversation per product
- **Persistent Sessions**: Chat history saved and restored automatically
- **Scheduled Cleanup**: Expired sessions automatically removed hourly

### 🔄 Automated Data Synchronization
- **Startup Sync**: Automatic product data sync when application starts
- **Multi-Source Integration**: Combines data from Shopify (sales) and Baselinker (inventory)
- **Dynamic Lead Times**: Calculated based on current stock levels

### 🎨 User-Friendly Interface
- **Responsive Design**: Clean, modern UI with gradient backgrounds
- **Accessibility**: Full ARIA support, keyboard navigation, tooltips
- **Help System**: Contextual hints (ⓘ) explain every metric

## Technology Stack

- **Backend**: Spring Boot 3.2.0 (Java 21)
- **Database**: H2 (in-memory, demo mode) / PostgreSQL-ready
- **AI**: Anthropic Claude API (claude-3-5-sonnet-20241022)
- **APIs**: RESTful architecture
- **Frontend**: Vanilla HTML/CSS/JavaScript (SPA)
- **Mock Server**: MockServer for demo data generation
- **Build Tool**: Maven 3.9.9

## Code Structure

```
src/main/java/com/aiadviser/
│
├── AiAdviserApplication.java          # Main Spring Boot application entry point
│
├── client/                            # External API clients
│   ├── BaselinkerClient.java          # Warehouse/inventory API integration
│   └── ShopifyClient.java             # E-commerce sales API integration
│
├── config/                            # Application configuration
│   ├── BaselinkerConfig.java          # Baselinker API settings
│   ├── ClaudeConfig.java              # Claude AI API configuration
│   ├── ShopifyConfig.java             # Shopify API settings
│   ├── MockServerConfig.java          # Mock server configuration beans
│   └── MockServerConfiguration.java   # Mock data generation for demo mode
│
├── controller/                        # REST API endpoints
│   └── AdvisorController.java         # All HTTP endpoints:
│                                       # - GET /api/products (list with analytics)
│                                       # - POST /api/advise/{sku} (AI recommendation)
│                                       # - POST /api/chat/{sku} (chat with AI)
│                                       # - GET/POST/DELETE /api/chat/session/{sku}
│
├── model/                             # Data models
│   ├── baselinker/                    # Baselinker API models
│   │   ├── BaselinkerProduct.java     # Product inventory data
│   │   └── BaselinkerProductsResponse.java
│   ├── shopify/                       # Shopify API models
│   │   ├── ShopifyOrder.java          # Order and sales data
│   │   ├── ShopifyLineItem.java       # Individual order items
│   │   └── ShopifyOrdersResponse.java
│   ├── AdviceResponse.java            # AI recommendation response
│   ├── ChatMessage.java               # Single chat message
│   ├── ChatRequest.java               # Chat API request
│   ├── ChatResponse.java              # Chat API response
│   ├── ChatSession.java               # Persistent chat session entity
│   ├── ClaudeRequest.java             # Claude API request format
│   ├── ClaudeResponse.java            # Claude API response format
│   ├── FinancialMetrics.java          # Forecast calculations result
│   ├── LLMInputData.java              # Data sent to Claude for analysis
│   ├── ProductData.java               # Core product entity (DB)
│   ├── ProductSummary.java            # Enhanced product with analytics
│   ├── SaleData.java                  # Sales history aggregation
│   └── StockData.java                 # Current inventory levels
│
├── repository/                        # Database layer
│   ├── ChatSessionRepository.java     # Chat persistence (JDBC)
│   └── ProductRepository.java         # Product data storage (JDBC)
│
├── service/                           # Business logic
│   ├── ClaudeService.java             # Claude AI integration
│   ├── DataAggregatorService.java     # Combines Shopify + Baselinker data
│   ├── DataSyncService.java           # Syncs products from external APIs
│   ├── FinancialForecastService.java  # Calculates financial metrics
│   └── ProductSummaryService.java     # Enriches products with analytics
│
├── scheduled/                         # Background tasks
│   └── ChatSessionCleanupTask.java    # Hourly cleanup of expired chats
│
└── startup/                           # Initialization
    └── StartupDataSyncRunner.java     # Auto-sync products on startup
```

### Frontend Structure
```
src/main/resources/
├── static/
│   └── index.html                     # Single-page application with:
│                                      # - Product cards with analytics
│                                      # - AI recommendation modal
│                                      # - Interactive chat interface
│                                      # - Financial forecast display
└── application.yaml                   # Spring Boot configuration
```

## How It Works

### 1. Data Flow
```
External APIs → Clients → Services → Aggregator → AI Analysis → User
     ↓              ↓          ↓
Baselinker    Shopify    Database
(inventory)   (sales)    (products, chat)
```

### 2. Recommendation Pipeline
1. User requests recommendation for a product (SKU)
2. `DataAggregatorService` fetches:
   - Product details from database
   - Current stock from Baselinker API
   - 30-day sales history from Shopify API
3. `FinancialForecastService` pre-calculates baseline metrics
4. `ClaudeService` sends data to AI with structured prompts
5. AI responds with:
   - Reorder recommendation
   - Reasoning explanation
   - Days until stockout prediction
   - Recommended chat TTL
6. Financial metrics recalculated with AI predictions
7. Results displayed with color-coded indicators

### 3. Chat System
- Each product (SKU) has an independent chat session
- Messages stored as JSON in database
- Sessions expire based on AI-determined TTL
- Automatic restoration when modal reopened
- Scheduled task cleans expired sessions hourly

## Setup and Running

### Prerequisites
- Java 21 or higher
- Maven 3.9+
- (Optional) Claude API key for production mode

### Demo Mode (Default)
```bash
# Clone the repository
git clone <repository-url>

# Run the application
mvn spring-boot:run
```

The application starts with:
- **Main app**: http://localhost:5000
- **MockServer**: http://localhost:9090
- **H2 Console**: http://localhost:5000/h2-console

MockServer generates realistic random data for demonstration purposes.

### Production Mode
1. Set Spring profile to `prod`:
   ```yaml
   spring:
     profiles:
       active: prod
   ```

2. Configure real API keys in `application.yaml`:
   ```yaml
   baselinker:
     api-token: your-baselinker-token
     base-url: https://api.baselinker.com/connector.php
   
   shopify:
     api-key: your-shopify-key
     base-url: https://your-store.myshopify.com
   
   claude:
     api-key: your-claude-api-key
     base-url: https://api.anthropic.com
   ```

3. Configure PostgreSQL database:
   ```yaml
   spring:
     datasource:
       url: jdbc:postgresql://localhost:5432/aiadviser
       username: your-username
       password: your-password
   ```

## API Endpoints

### Product Management
- `GET /api/products` - List all products with analytics
  - Returns: stock quantity, monthly sales, monthly profit, COGS, lead time

### AI Recommendations
- `POST /api/advise/{sku}` - Get AI recommendation for a product
  - Returns: advice text, reasoning, financial metrics, TTL

### Interactive Chat
- `POST /api/chat/{sku}` - Send a message to AI
  - Body: `{ "message": "your question" }`
  - Returns: AI response with context awareness

### Chat Session Management
- `GET /api/chat/session/{sku}` - Retrieve chat history
- `POST /api/chat/session/{sku}` - Create/update session
  - Body: `{ "messages": [...], "ttlHours": 24 }`
- `DELETE /api/chat/session/{sku}` - Clear chat history

## Financial Metrics Explained

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Expected Revenue** | Sales velocity × forecast days × avg unit price | Projected income |
| **Expected Profit** | Expected revenue - (units sold × COGS) | Net profit forecast |
| **Carrying Cost** | Current stock × COGS × 20% annual rate × days/365 | Storage costs |
| **Stockout Loss** | Lost sales × unit price × 15% penalty | Revenue at risk |
| **Opportunity Cost** | Excess stock × COGS × 20% annual rate × days/365 | Capital opportunity |

**Color Coding:**
- 🟢 Green: Positive/good metric
- 🟡 Yellow: Neutral
- 🔴 Red: Negative/warning

## Configuration

Key settings in `application.yaml`:

```yaml
# Server configuration
server:
  port: 5000
  address: 0.0.0.0  # Required for Replit/cloud deployments

# Financial calculation parameters
forecast:
  carrying-cost-rate: 0.20      # 20% annual holding cost
  stockout-penalty-rate: 0.15   # 15% lost sale penalty
  forecast-horizon-days: 30     # Default forecast period

# Chat session cleanup
chat:
  cleanup:
    cron: "0 0 * * * *"          # Every hour
    enabled: true
```

## Development Notes

- **Demo Mode**: Uses MockServer to simulate external APIs with random realistic data
- **Database**: H2 in-memory database (demo) / PostgreSQL (production)
- **AI Model**: Claude 3.5 Sonnet (latest version)
- **Data Sync**: Automatic on startup, manual sync available via service methods
- **Error Handling**: Graceful fallbacks, detailed logging
- **Accessibility**: WCAG 2.1 compliant UI with ARIA labels

## Future Enhancements

- Real-time inventory updates via webhooks
- Multi-warehouse routing optimization
- Seasonal trend analysis
- Automated purchase order generation
- Email/SMS alerts for critical stock levels
- Advanced analytics dashboard
- Export reports (PDF/Excel)

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please contact the development team.

---

**Built with ❤️ using Spring Boot and Claude AI**
