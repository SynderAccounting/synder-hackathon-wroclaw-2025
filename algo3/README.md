# Smart Product Optimization Manager

**An AI-powered e-commerce optimization platform that helps online retailers maximize revenue through intelligent pricing, promotion, and bundling suggestions.**

![Platform](https://img.shields.io/badge/Platform-Docker-blue)
![Backend](https://img.shields.io/badge/Backend-Flask-green)
![Frontend](https://img.shields.io/badge/Frontend-React-cyan)
![Database](https://img.shields.io/badge/Database-SQLite-orange)

---

## Table of Contents

- [The Problem](#the-problem)
- [Our Solution](#our-solution)
- [How It Works](#how-it-works)
- [Technical Architecture](#technical-architecture)

---

## The Problem

E-commerce retailers face three critical challenges that directly impact their bottom line:

### 1. **Pricing Optimization**
Determining optimal product prices requires constant market analysis and competitor monitoring. Questions arise daily:
- Is this product priced too high, leaving money on the table?
- Is it priced too low, eroding profit margins?
- Should prices be adjusted based on current inventory levels?

### 2. **Promotion Timing**
Knowing when and how to discount products to maximize sales without eroding margins is an art and science:
- Which products should be promoted to move slow-moving inventory?
- What discount percentage will drive sales without training customers to wait for deals?
- How do seasonal trends affect promotion effectiveness?

### 3. **Product Bundling**
Identifying which products should be bundled together to increase average order value:
- Which product combinations make logical sense to customers?
- How should bundles be priced to be attractive while maintaining margins?
- Which bundles will actually sell vs. just cluttering the catalog?


### The Reality for SMB Retailers

Manual management of these tasks is:
- **Time-consuming**: Hours spent analyzing spreadsheets and market data
- **Error-prone**: Human judgment can miss patterns in sales data
- **Reactive**: Decisions made after problems occur, not proactively
- **Resource-intensive**: Small to medium-sized retailers lack dedicated pricing analysts or data science teams

**The result?** Missed revenue opportunities, stagnant inventory, and sub-optimal profit margins.

---

## Our Solution

**Smart Product Optimization Manager** is an intelligent platform that acts as your virtual pricing analyst and e-commerce strategist. It continuously monitors your product catalog and automatically generates actionable recommendations.

### What Makes It Different?

Unlike traditional analytics dashboards that just show you data, our platform:
1. **Analyzes** your product performance metrics
2. **Generates** specific, actionable suggestions
3. **Applies** changes with one click
4. **Tracks** the results of each optimization

### Core Capabilities

#### **Dynamic Pricing**
AI-driven price adjustments based on:
- **Inventory levels**: Suggest price increases for low-stock high-demand items
- **Sales velocity**: Identify products that can support higher prices
- **Stock clearance**: Recommend strategic discounts to move excess inventory
- **Competitive positioning**: Optimize prices for market competitiveness

**Example**: "Product X has only 5 units left but sold 20 in the past week. Suggestion: Increase price by 15% to maximize revenue on remaining stock."

#### **Smart Promotions**
Targeted discount suggestions that:
- **Move slow inventory**: Identify products sitting in warehouse for 60+ days
- **Capitalize on trends**: Suggest promotions for products with increasing search interest
- **Prevent stockouts**: Recommend discounts when overstocked
- **Seasonal optimization**: Time promotions to align with buying patterns

**Example**: "Product Y hasn't sold in 45 days and has 30 units in stock. Suggestion: Run a 20% off promotion for 2 weeks to clear inventory."

#### **Bundle Creation**
Automated detection of product synergies:
- **Complementary products**: Find items frequently viewed together
- **Margin optimization**: Bundle slow-moving items with bestsellers
- **Value perception**: Create bundles that feel like a deal while maintaining profits
- **Cross-category bundling**: Combine products to increase basket size

**Example**: "Gaming Mouse + Mouse Pad are often purchased together. Suggestion: Create 'Gaming Combo' bundle at $45 (individual total: $52) to increase AOV."

### Key Features
- **One-Click Application**: Apply optimization suggestions instantly without manual data entry
- **Real-Time Analytics**: Track the impact of applied suggestions through comprehensive event history
- **Demo Mode**: Test the platform with realistic data without connecting real stores
- **Non-Destructive**: All changes are tracked and can be monitored through detailed audit logs
- **Platform Agnostic**: Works with any WooCommerce or Shopify store out of the box

---

## How It Works

### The Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. CONNECT YOUR STORE                        │
│  Securely link WooCommerce/Shopify via API (credentials encrypted)│
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. SYNC PRODUCTS                             │
│  Platform imports all products, prices, stock levels, metadata  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  3. AI ANALYSIS ENGINE                          │
│  • Analyzes product performance metrics                         │
│  • Identifies optimization opportunities                        │
│  • Generates specific, actionable suggestions                   │
│  • Categorizes by type: Price / Promo / Bundle                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. REVIEW SUGGESTIONS                          │
│  Dashboard shows all suggestions with:                          │
│  • Clear description of the recommendation                      │
│  • Expected impact on revenue/inventory                         │
│  • One-click "Apply" button                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  5. APPLY OPTIMIZATION                          │
│  Single click triggers:                                         │
│  • Price updates pushed to e-commerce platform                  │
│  • Promotion campaigns created                                  │
│  • Bundle products generated with SKUs                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  6. TRACK RESULTS                               │
│  • Complete audit trail of all changes                          │
│  • Event history with timestamps                                │
│  • Before/after comparison                                      │
│  • Active promotions displayed on dashboard                     │
└─────────────────────────────────────────────────────────────────┘
```

### Technical Flow

For technical evaluators, here's how the system processes a suggestion:

1. **Product Sync** (`POST /api/connections/:id/sync`)
   ```
   Platform API → Flask Backend → SQLite Database
   • Fetches products from WooCommerce/Shopify
   • Normalizes data across platforms
   • Stores in local database for analysis
   ```

2. **Suggestion Generation** (Automatic)
   ```
   Algorithm analyzes:
   • Stock levels (high/low thresholds)
   • Price points (below/above category average)
   • Sales velocity indicators
   • Product relationships (frequently viewed together)

   Generates suggestions with:
   • Type classification (price/promo/bundle)
   • Specific recommendation text
   • Expected new values
   ```

3. **Suggestion Application** (`POST /api/suggestions/:id/apply`)
   ```
   Frontend → Backend → Decision Logic:

   IF type == "price":
     • Parse new price from description (regex)
     • Update local database
     • Push to e-commerce platform API
     • Create event log entry

   IF type == "promo":
     • Mark product as "on promotion"
     • Store discount details
     • Display in "Active Promotions" section
     • Create event log entry

   IF type == "bundle":
     • Create new bundle product
     • Link component products (many-to-many)
     • Calculate bundle pricing
     • Generate unique SKU
     • Create event log entry
   ```

---

## Technical Architecture

### System Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   React Frontend│ ◄─────► │   Flask Backend  │ ◄─────► │ E-commerce APIs │
│   (Port 5173)   │   REST  │   (Port 5001)    │   REST  │  WooCommerce    │
└─────────────────┘         └──────────────────┘         │    Shopify      │
                                     │                     └─────────────────┘
                                     ▼
                            ┌──────────────────┐
                            │  SQLite Database │
                            │   (Persistent)   │
                            └──────────────────┘
```

### Technology Stack

#### Backend (Python/Flask)
- **Framework**: Flask 3.0 with RESTful API design
- **Database**: SQLite with transaction-safe operations
- **Security**:
  - AES-256 encryption for credentials (PBKDF2HMAC key derivation)
  - CORS protection
  - Input validation and sanitization
- **External Integrations**:
  - Shopify Admin API 2024-01
  - Mock integration for testing without real stores

#### Frontend (React/Vite)
- **Framework**: React 18 with modern hooks (useState, useEffect)
- **Build Tool**: Vite 5 for fast development and optimized production builds
- **Styling**: Vanilla CSS with responsive design (no external UI libraries)
- **State Management**: Component-level state with callback-based updates
- **API Client**: Fetch API with error handling and retry logic

#### Infrastructure
- **Containerization**: Docker & Docker Compose for one-command deployment
- **Data Persistence**: Named volume for SQLite database
- **Networking**: Internal Docker network with exposed ports


## Quick Start

### Prerequisites
- Docker
- Docker Compose

### One-Command Setup

```bash
docker-compose up
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/health

### Demo Mode (No Real Store Required)

1. Open http://localhost:5173
2. Navigate to **"Store Connections"** tab
3. Click **"Quick Demo"** button
4. Click **"Sync"** for each demo store
5. Test all features with sample products!

### Production Setup with Real Stores

See [STORE_API_SETUP.md](STORE_API_SETUP.md) for detailed instructions on connecting WooCommerce or Shopify stores.

---

## Project Structure

```
.
├── Backend/
│   ├── app/
│   │   ├── main.py                      # Flask application & API endpoints
│   │   ├── database.py                  # Schema definition & seed data
│   │   ├── crypto.py                    # Credential encryption
│   │   ├── suggestions_generator.py     # AI suggestion logic
│   │   └── integrations/
│   │       ├── base.py                  # Integration interface
│   │       ├── woocommerce.py          # WooCommerce API client
│   │       ├── shopify.py              # Shopify API client
│   │       └── mock.py                 # Demo mode integration
│   ├── Dockerfile
│   └── requirements.txt
│
├── Frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductsTable.jsx       # Product list view
│   │   │   ├── SuggestionsPanel.jsx    # Suggestion sidebar
│   │   │   ├── EventHistory.jsx        # Action audit trail
│   │   │   ├── StoreConnections.jsx    # Store management
│   │   │   ├── ProductModal.jsx        # Product details popup
│   │   │   ├── Notification.jsx        # Toast notifications
│   │   │   └── Tabs.jsx                # Tab navigation
│   │   ├── services/
│   │   │   └── api.js                  # API client wrapper
│   │   ├── App.jsx                     # Main application component
│   │   ├── main.jsx                    # React entry point
│   │   └── index.css                   # Global styles
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml                   # Service orchestration
├── README.md                           # This file
├── QUICKSTART.md                       # Quick reference guide
├── DEMO_MODE.md                        # Demo mode instructions
├── STORE_API_SETUP.md                 # Production setup guide
└── CLAUDE_CONTEXT.md                  # Development context
```

---


## Testing

### Manual Testing (Demo Mode)
```bash
# Start services
docker-compose up

# Access frontend
http://localhost:5173

# Create demo stores
Click "Quick Demo" → Sync each store

# Test workflow
1. Select a product
2. View suggestions
3. Apply suggestion
4. Verify in event history
```

### API Testing
```bash
# Health check
curl http://localhost:5001/health

# Get products
curl http://localhost:5001/api/products

# Get suggestions for product ID 1
curl http://localhost:5001/api/suggestions?product_id=1
```


## Team

Developed during SynderHacks Wrocław 2025

**Built with**: Python, React, Docker, SQLite, and lots of coffee

---

**Last Updated**: November 2025
**Status**: MVP Complete, Bundle System in Development
**Version**: 1.0.0
