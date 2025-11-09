# Quick Start Guide

## Uruchomienie aplikacji w 3 krokach

### 1. Uruchom Docker
```bash
docker-compose up
```

### 2. Otwórz przeglądarkę
Przejdź do: **http://localhost:5173**

### 3. Gotowe!

Aplikacja jest już gotowa do użycia z przykładowymi danymi.

---

## Co zobaczysz?

- **8 produktów** z różnych kanałów (WooCommerce, Shopify)
- **15+ sugestii** optymalizacyjnych
- **Historia zdarzeń** z przykładowymi akcjami

---

## Testowanie funkcjonalności

1. **Wybierz produkt** z tabeli (kliknij na wiersz)
2. **Zobacz sugestie** w panelu po prawej stronie
3. **Zastosuj sugestię** klikając przycisk "Zastosuj sugestię"
4. **Sprawdź historię** - nowe zdarzenie powinno pojawić się w panelu historii
5. **Powiadomienie** pojawi się w prawym górnym rogu

---

## API Endpoints (do testowania przez curl)

```bash
# Health check
curl http://localhost:5001/health

# Lista produktów
curl http://localhost:5001/api/products

# Sugestie dla produktu ID=1
curl "http://localhost:5001/api/suggestions?product_id=1"

# Zastosuj sugestię ID=1
curl -X POST http://localhost:5001/api/suggestions/1/apply

# Historia zdarzeń
curl http://localhost:5001/api/events
```

---

## Zatrzymanie aplikacji

```bash
docker-compose down
```

---

## Reset danych (czysty start)

```bash
docker-compose down -v
docker-compose up
```

---

## Porty

- Frontend: **5173**
- Backend: **5001**

---

## Problemy?

Jeśli port 5001 lub 5173 jest zajęty, zmień porty w pliku `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "NOWY_PORT:5000"  # Zmień NOWY_PORT na wolny port

  frontend:
    ports:
      - "NOWY_PORT:5173"  # Zmień NOWY_PORT na wolny port
    environment:
      - VITE_API_URL=http://localhost:BACKEND_PORT  # Użyj portu backendu
```

Następnie:
```bash
docker-compose down
docker-compose up --build
```
