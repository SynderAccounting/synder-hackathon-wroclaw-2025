# Claude Context - Product Suggestions Manager

> **Dla osób pracujących z Claude**: Ten plik zawiera pełny kontekst projektu, kluczowe decyzje architektoniczne i aktualny stan implementacji.

## 🎯 Cel Projektu

System zarządzania produktami e-commerce z **automatycznymi sugestiami AI** do optymalizacji (cena, promocje, bundle). Integracja z Shopify, analiza rynku przez DummyJSON API, generowanie sugestii przez OpenAI GPT-4o-mini.

## 🏗️ Architektura

### Backend (Python/Flask)
- **Port**: 5001
- **Baza danych**: SQLite z volume Docker `/data/db.sqlite`
- **AI Engine**: OpenAI GPT-4o-mini
- **Market Data**: DummyJSON API (tylko do analizy, NIE do rekomendacji)
- **Bezpieczeństwo**: Credentials szyfrowane AES (cryptography + PBKDF2HMAC)

### Frontend (React/Vite)
- **Port**: 3000
- **Styling**: Tailwind CSS / Vanilla CSS
- **State**: React hooks (useState, useEffect)

### Integracje
- **Shopify Admin API 2024-01** (główna integracja)
- **OpenAI API** (GPT-4o-mini dla sugestii)
- **DummyJSON API** (dane rynkowe do analizy)

## 📊 Schema Bazy Danych

### Główne Tabele

```sql
products (
  id, sku, name, price, stock, status, channel,
  connection_id, external_id,
  vendor TEXT,                    -- Shopify vendor
  product_type TEXT,              -- NULL | 'bundle' | 'promotion'
  created_at, updated_at
)

suggestions (
  id, product_id,
  type TEXT,                      -- 'price' | 'promo' | 'bundle'
  description TEXT,
  status TEXT,                    -- 'new' | 'applied'
  related_product_ids TEXT,       -- JSON array [29, 30, 31]
  created_at, applied_at
)

events (
  id, product_id, suggestion_id, event_type,
  description, created_at
)

store_connections (
  id, name, platform, store_url,
  api_key_encrypted, api_secret_encrypted,
  is_active, last_sync
)
```

## 🔑 Kluczowe Rozwiązania

### 1. **Database Reset on Startup**
**Założenie**: Każde uruchomienie kontenera = czysty start (dla demo).

**Implementacja**: `backend/app/database.py::seed_data()`
```python
def seed_data():
    """Clear products and suggestions on startup - fresh start every time"""
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM suggestions')
    cursor.execute('DELETE FROM events WHERE product_id IS NOT NULL')
```

### 2. **AI Agent - Workflow Generowania Sugestii**

#### Zasady AI:
1. **Maksymalna liczba sugestii** = `total_products / 2`
2. **DummyJSON** używany TYLKO do analizy rynku (porównanie cen)
3. **Sugestie dotyczą TYLKO** produktów z Shopify (NIE z DummyJSON)
4. **Produkty wykluczane z analizy**: `product_type` in `['bundle', 'promotion', 'Zestaw', 'Promocja']`

#### Implementacja:
```python
# backend/app/services/ai_agent_service.py:248-257

# Get all products (exclude bundles and promos)
cursor.execute('''
    SELECT id, name FROM products
    WHERE (product_type IS NULL OR product_type NOT IN ('bundle', 'promotion', 'Zestaw', 'Promocja'))
''')
products = cursor.fetchall()

# Limit to half of products
total_products = len(products)
max_products_to_analyze = max(1, total_products // 2)
```

#### Prompt Structure:
AI otrzymuje:
1. **Produkt do analizy** (z naszego Shopify)
2. **WSZYSTKIE inne produkty** z naszego sklepu (do bundle/promo)
3. **Dane rynkowe** z DummyJSON (TYLKO do porównania cen)

```python
prompt = f"""
PRODUKT DO ANALIZY (NASZ SKLEP SHOPIFY):
- ID: {product['id']}
- Nazwa: {product['name']}
- Cena: {product['price']} PLN

POZOSTAŁE PRODUKTY W NASZYM SKLEPIE SHOPIFY:
{shop_products_text}

DANE RYNKOWE DO ANALIZY (DummyJSON - tylko do porównania, NIE nasze produkty):
{json.dumps(market_data[:5])}

KRYTYCZNIE WAŻNE:
- WSZYSTKIE sugestie dotyczą TYLKO produktów z naszego sklepu Shopify!
- W bundle/promo używaj TYLKO ID produktów z sekcji "POZOSTAŁE PRODUKTY W NASZYM SKLEPIE"
- NIE używaj produktów z DummyJSON - to tylko dane do analizy rynku!
"""
```

### 3. **Bundle & Promo Creation**

#### Bundle (2-3 produkty):
**Workflow**:
1. Pobiera produkty z `related_product_ids` (JSON: `[29, 30, 31]`)
2. **Walidacja**: sprawdza czy żaden produkt nie ma `product_type` in `['bundle', 'promotion', 'Zestaw', 'Promocja']`
3. Tworzy nowy produkt w Shopify:
   - `name`: "BUNDLE: Product1 + Product2 + Product3"
   - `price`: suma cen * 0.9 (10% zniżki)
   - `stock`: min(stock z wszystkich produktów)
   - `vendor`: "AI Bundle"
   - **`product_type`: "bundle"**
4. Ustawia stock oryginalnych produktów na 0 (Shopify + DB)
5. Zmienia status oryginalnych produktów na `'bundled'`

**Implementacja**: `backend/app/services/suggestion_service.py:194-244`

```python
# Validate: cannot create bundle from bundles or promos
invalid_products = [p for p in products_to_bundle
                   if p.get('product_type') in ['bundle', 'promotion', 'Zestaw', 'Promocja']]
if invalid_products:
    return error("Nie można tworzyć bundla z bundli lub promek")

# Create new bundle product
new_product = integration.create_product({
    'name': bundle_name[:100],
    'price': bundle_price,
    'stock': min(p['stock'] for p in products_to_bundle),
    'vendor': 'AI Bundle',
    'product_type': 'bundle'  # <-- KLUCZOWE!
})

# Reduce stock to 0
for prod in products_to_bundle:
    integration.update_product_stock(prod['external_id'], 0)
    cursor.execute('UPDATE products SET stock = 0, status = ? WHERE id = ?',
                 ('bundled', prod['id']))
```

#### Promo (1+1):
**Workflow**:
1. Pobiera main product + 1 related product
2. **Walidacja**: sprawdza czy żaden nie jest bundle/promo
3. Tworzy nowy produkt w Shopify:
   - `name`: "PROMO 1+1: Product1 + Product2"
   - `price`: price1 + price2 * 0.5 (drugi produkt 50% taniej)
   - `vendor`: "AI Promo"
   - **`product_type`: "promotion"**
4. Ustawia stock oryginalnych na 0
5. Zmienia status na `'promo_used'`

**Implementacja**: `backend/app/services/suggestion_service.py:139-192`

### 4. **Product Type Filtering**

**KRYTYCZNE**: Wszystkie filtry muszą obsługiwać zarówno nowe jak i legacy nazwy:
- **Nowe**: `'bundle'`, `'promotion'`
- **Legacy**: `'Zestaw'`, `'Promocja'` (stare polskie nazwy)

```python
# Poprawny filtr:
if product.get('product_type') in ['bundle', 'promotion', 'Zestaw', 'Promocja']:
    # Skip from analysis
```

**Lokalizacje**:
- `backend/app/services/ai_agent_service.py:163-169` (skip analysis)
- `backend/app/services/ai_agent_service.py:175-176` (get products for AI)
- `backend/app/services/ai_agent_service.py:251` (get all products)
- `backend/app/services/suggestion_service.py:154` (promo validation)
- `backend/app/services/suggestion_service.py:209` (bundle validation)

### 5. **Related Product IDs Storage**

Bundle i promo sugestie przechowują powiązane produkty jako JSON string:

```python
# Zapisywanie (AI agent)
product_ids_json = json.dumps(suggestion['product_ids'])  # [29, 30, 31]
cursor.execute('''
    INSERT INTO suggestions (product_id, type, description, related_product_ids)
    VALUES (?, ?, ?, ?)
''', (product_id, 'bundle', description, product_ids_json))

# Odczytywanie (apply suggestion)
related_ids = json.loads(suggestion['related_product_ids'])  # [29, 30, 31]
```

### 6. **Shopify Integration - Product Type**

Podczas tworzenia/synchronizacji produktów, `product_type` jest przekazywane do/z Shopify:

```python
# backend/app/integrations/shopify.py:70-72
products.append({
    'vendor': product.get('vendor', ''),
    'product_type': product.get('product_type', '')  # <-- Synchronizacja
})

# backend/app/integrations/shopify.py:193
payload = {
    'product': {
        'vendor': product_data.get('vendor', ''),
        'product_type': product_data.get('product_type', ''),  # <-- Ustawienie
    }
}
```

## 🎮 API Endpoints

### Products
- `GET /api/products` - Get all products
- `GET /api/products/<id>` - Get product details

### Suggestions
- `GET /api/suggestions?product_id=<id>` - Get suggestions for product
- `POST /api/suggestions/<id>/apply` - **Apply suggestion** (creates bundle/promo in Shopify)

### AI Agent
- `POST /api/ai/analyze-all` - Generate suggestions for max(1, total_products/2) products
- `POST /api/ai/analyze/<product_id>` - Generate suggestions for specific product

### Sync
- `POST /api/connections/<id>/sync` - Sync products from Shopify

## 🔧 Environment Variables

```bash
# Backend (.env)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxx
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4o-mini
ENCRYPTION_KEY=your-32-byte-key
```

## 🐛 Znane Problemy/Fixe

### Fix #1: httpx Dependency
**Problem**: OpenAI SDK wymaga `httpx` ale nie było w requirements.txt

**Rozwiązanie**:
```bash
# backend/requirements.txt
httpx==0.27.0
```

### Fix #2: Logger Import w database.py
**Problem**: `NameError: name 'logger' is not defined`

**Rozwiązanie**:
```python
# backend/app/database.py
from utils.logger import get_logger
logger = get_logger(__name__)
```

### Fix #3: Code Changes Not Reflected
**Problem**: Docker nie ma volume mount dla kodu, zmiany wymagają rebuild

**Rozwiązanie**:
```bash
docker-compose build backend
docker-compose up -d backend
```

## 🚀 Testing Workflow

### 1. Sync Products
```bash
curl -X POST http://localhost:5001/api/connections/1/sync
# Response: {"success": true, "products_synced": 4}
```

### 2. Generate AI Suggestions
```bash
curl -X POST http://localhost:5001/api/ai/analyze-all
# Response: {"total_products": 4, "max_analyzed": 2, "total_suggestions_created": 6}
```

### 3. View Suggestions
```bash
curl "http://localhost:5001/api/suggestions?product_id=57"
# Returns: [{id: 74, type: 'price', ...}, {id: 75, type: 'promo', ...}, {id: 76, type: 'bundle', ...}]
```

### 4. Apply Bundle Suggestion
```bash
curl -X POST http://localhost:5001/api/suggestions/76/apply
# Creates new bundle in Shopify, sets original products stock to 0
```

### 5. Sync to See New Bundle
```bash
curl -X POST http://localhost:5001/api/connections/1/sync
# Response: {"products_synced": 5}  <- now includes the bundle
```

### 6. Verify Bundle Excluded from AI
```bash
curl -X POST http://localhost:5001/api/ai/analyze-all
# Response: {"total_products": 3, ...}  <- bundles/promos excluded!
```

## 📦 Deployment

### Development
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:5001
# Health: http://localhost:5001/health
```

### Restart After Code Changes
```bash
docker-compose build backend
docker-compose up -d backend
```

### View Logs
```bash
docker logs -f product-suggestions-backend
```

### Clean Reset
```bash
docker-compose down -v  # Removes database volume
docker-compose up -d
```

## 📝 File Structure

```
backend/app/
├── main.py                      # Flask app, API routes
├── database.py                  # Schema, seed_data(), migrations
├── models.py                    # Pydantic models
├── crypto.py                    # AES encryption
├── services/
│   ├── ai_agent_service.py     # ⭐ AI suggestion generation (OpenAI)
│   ├── suggestion_service.py   # ⭐ Apply suggestions (bundle/promo creation)
│   ├── product_service.py      # Product CRUD
│   ├── sync_service.py         # Shopify sync
│   ├── connection_service.py   # Store connections
│   └── dummyjson_service.py    # Market data API
├── integrations/
│   ├── base.py                 # Base integration interface
│   └── shopify.py              # ⭐ Shopify Admin API (product_type handling)
└── utils/
    └── logger.py               # Logging setup
```

## 🔮 Kluczowe Założenia Biznesowe

### Workflow Sugestii:
```
1. User syncs products from Shopify
   ↓
2. AI analyzes products (max total/2, excludes bundles/promos)
   ↓
3. AI generates suggestions (price/promo/bundle) using:
   - DummyJSON for market price analysis
   - Shopify products for bundle/promo combinations
   ↓
4. Suggestions saved with status='new'
   ↓
5. User reviews and applies suggestions
   ↓
6. For bundle/promo: create new product in Shopify, reduce original stock to 0
   ↓
7. Next sync: new bundles/promos appear, but are excluded from AI analysis
```

### Bundle Rules:
- 2-3 produkty
- 10% zniżki od sumy cen
- Stock = min(stock wszystkich produktów)
- Oryginalne produkty: stock → 0, status → 'bundled'
- **NIE można** tworzyć bundla z bundla ani promki z promki

### Promo Rules:
- 2 produkty (1+1)
- Drugi produkt 50% taniej
- Stock = min(stock obu produktów)
- Oryginalne produkty: stock → 0, status → 'promo_used'

## 🆘 Troubleshooting

### Bundle dostaje sugestie AI
**Problem**: Bundle ma `product_type='Zestaw'` (stara polska nazwa)

**Rozwiązanie**: Filtry muszą zawierać zarówno `'bundle'` jak i `'Zestaw'`

### AI sugeruje produkty z DummyJSON
**Problem**: Prompt nie był wystarczająco jasny

**Rozwiązanie**: Prompt zawiera teraz sekcję "KRYTYCZNIE WAŻNE" z explicit instrukcjami

### Code changes not working
**Problem**: Docker nie ma volume mount

**Rozwiązanie**:
```bash
docker-compose build backend && docker-compose up -d backend
```

## 🤝 Praca Zespołowa z Claude

### Dla Nowej Osoby
1. **Przeczytaj**: `CLAUDE_CONTEXT.md` (ten plik)
2. **Przeczytaj**: `ARCHITECTURE.md` (szczegóły techniczne)
3. **Setup**: `docker-compose up -d`
4. **Test**: Wykonaj workflow z sekcji "Testing Workflow"
5. **Git**: `git log` - sprawdź ostatnie zmiany

### Przed Zadaniem Pytania Claude
Podaj kontekst:
```
Pracuję nad Product Suggestions Manager.
Przeczytałem CLAUDE_CONTEXT.md i ARCHITECTURE.md.
Aktualny branch: backend/api-structure

[Twoje pytanie...]
```

### Commitowanie
```bash
git add .
git commit -m "feat(ai-agent): implement bundle/promo exclusion from analysis

- Added product_type filtering in AI agent
- Bundles and promos now excluded from AI analysis
- Validation prevents nested bundles/promos
- Updated Shopify integration to sync product_type
- Added related_product_ids to suggestions table
- Tested workflow: sync → analyze → apply → verify exclusion
"
```

## 📊 Metryki Projektu

- **Backend endpoints**: 15+
- **React components**: 10+
- **Database tables**: 8
- **AI Integration**: OpenAI GPT-4o-mini
- **Lines of code**: ~3000 (backend) + ~1500 (frontend)
- **Docker containers**: 2

---

**Ostatnia aktualizacja**: 2025-11-09
**Status**: AI Agent ukończony, Bundle/Promo system ukończony
**Branch**: `backend/api-structure`
**Autorzy**: Andrii Nikonchuk + Claude
