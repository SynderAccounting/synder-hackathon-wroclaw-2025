# Struktura Danych Produktów

## TL;DR - To musisz wiedzieć

**KAŻDY produkt w systemie ma dokładnie te pola:**

```javascript
{
  sku: "SKU-001",                    // Kod produktu
  name: "Smartwatch Fitness Pro",    // Nazwa produktu
  price: 299.99,                     // Cena
  stock: 50,                         // Nakład (ilość)
  status: "active",                  // Status
  channel: "woocommerce",            // Kanał (shopify lub woocommerce)
  active_promotion: "20% rabatu"     // Aktywna promocja (lub null)
}
```

## Pełna struktura

### ProductRecord (główna struktura)

| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `sku` | string | Kod produktu (SKU) | ✅ |
| `name` | string | Nazwa produktu | ✅ |
| `price` | number | Cena produktu | ✅ |
| `stock` | number | Nakład/ilość na stanie | ✅ |
| `status` | string | Status produktu | ✅ |
| `channel` | string | Kanał sprzedaży | ✅ |
| `active_promotion` | string \| null | Opis aktywnej promocji | ✅ |
| `id` | number | ID w bazie (tylko internal) | ❌ |
| `active_promotions` | array | Lista promocji (tylko internal) | ❌ |
| `created_at` | string | Data utworzenia (tylko internal) | ❌ |

### Dozwolone wartości

**Status** (`status`):
- `active` - Produkt aktywny
- `low_stock` - Niski stan magazynowy
- `out_of_stock` - Brak w magazynie
- `inactive` - Produkt nieaktywny

**Kanał** (`channel`):
- `shopify` - Shopify
- `woocommerce` - WooCommerce

**Typ promocji** (w `active_promotions[].type`):
- `price` - Promocja cenowa
- `bundle` - Bundle/pakiet
- `promo` - Inna promocja

## Przykłady

### Produkt z promocją

```json
{
  "sku": "SKU-001",
  "name": "Smartwatch Fitness Pro",
  "price": 299.99,
  "stock": 50,
  "status": "active",
  "channel": "woocommerce",
  "active_promotion": "Black Friday - 20% rabatu"
}
```

### Produkt bez promocji

```json
{
  "sku": "SKU-002",
  "name": "Wireless Earbuds Elite",
  "price": 149.99,
  "stock": 120,
  "status": "active",
  "channel": "shopify",
  "active_promotion": null
}
```

### Produkt z niskim stanem

```json
{
  "sku": "SKU-004",
  "name": "USB-C Charging Cable 2m",
  "price": 19.99,
  "stock": 8,
  "status": "low_stock",
  "channel": "shopify",
  "active_promotion": null
}
```

## Jak używać

### Backend (Python)

```python
from models import ProductRecord, db_row_to_product

# Konwersja z bazy danych
product = db_row_to_product(db_row, promotions)
product_dict = product.dict()  # Do JSON

# Konwersja z Shopify/WooCommerce
from models import transform_external_product

product_data = transform_external_product(shopify_product, 'shopify')
# product_data jest gotowe do wrzucenia do bazy
```

### Frontend (JavaScript)

```javascript
import { getStatusLabel, getChannelLabel, formatPrice } from './types.js';

// Pobierz produkty
const response = await fetch('/api/products');
const products = await response.json();

// Wyświetl w tabeli
products.forEach(product => {
  console.log(`
    SKU: ${product.sku}
    Nazwa: ${product.name}
    Cena: ${formatPrice(product.price)}
    Nakład: ${product.stock}
    Status: ${getStatusLabel(product.status)}
    Kanał: ${getChannelLabel(product.channel)}
    Promocja: ${product.active_promotion || 'Brak'}
  `);
});
```

## Integracje z platformami

### Shopify → Nasza struktura

```python
# backend/app/models.py
from models import transform_external_product

shopify_product = {
  "id": 12345,
  "title": "Smartwatch Pro",
  "variants": [{
    "sku": "SKU-001",
    "price": "299.99",
    "inventory_quantity": 50
  }]
}

our_format = transform_external_product(shopify_product, 'shopify')
# Zwraca: {sku, name, price, stock, status, channel, external_id}
```

### WooCommerce → Nasza struktura

```python
woo_product = {
  "id": 789,
  "name": "Smartwatch Pro",
  "sku": "SKU-001",
  "price": "299.99",
  "stock_quantity": 50,
  "stock_status": "instock"
}

our_format = transform_external_product(woo_product, 'woocommerce')
# Zwraca: {sku, name, price, stock, status, channel, external_id}
```

## Zasady

1. **Zawsze używaj modelu ProductRecord** - nie twórz własnych struktur
2. **Zawsze używaj funkcji transformacji** - `db_row_to_product()` dla bazy, `transform_external_product()` dla platform
3. **Nie modyfikuj struktury** - jeśli potrzebujesz więcej pól, dodaj je do modelu w `models.py`
4. **Walidacja automatyczna** - Pydantic sprawdza typy i wartości
5. **Konsystencja** - wszędzie ta sama struktura, zero wyjątków

## Pliki

- **Backend**: `/backend/app/models.py` - definicje modeli i funkcje transformacji
- **Frontend**: `/frontend/src/types.js` - typy i helpery
- **API endpoint**: `/backend/app/main.py` - endpoint `/api/products` zwraca listę ProductRecord
