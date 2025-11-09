# 🎮 Tryb Demo - Testowanie bez prawdziwych sklepów

Jeśli nie masz jeszcze sklepu WooCommerce lub Shopify, możesz przetestować całą aplikację w trybie demo!

## Jak uruchomić Demo Mode?

### Metoda 1: Szybkie Demo (Zalecane) ⚡

1. **Uruchom aplikację**
   ```bash
   docker-compose up
   ```

2. **Otwórz aplikację** w przeglądarce
   - Przejdź do: http://localhost:5173

3. **Przejdź do zakładki "Połączenia ze sklepami"**
   - Kliknij na drugą zakładkę na górze strony

4. **Kliknij przycisk "🎮 Szybkie Demo"**
   - Znajdziesz go w prawym górnym rogu
   - Potwierdź utworzenie demo sklepów

5. **Gotowe!**
   - Zostanie utworzone 2 demo sklepy:
     - Demo WooCommerce Store
     - Demo Shopify Store

6. **Zsynchronizuj produkty**
   - Dla każdego sklepu kliknij przycisk **"Synchronizuj"**
   - Produkty zostaną automatycznie wygenerowane (8-20 losowych produktów)

7. **Testuj funkcjonalności**
   - Przejdź do zakładki **"Produkty i Sugestie"**
   - Zobacz zsynchronizowane produkty
   - Testuj sugestie i ich zastosowanie
   - Sprawdź historię zdarzeń

### Metoda 2: Ręczne dodawanie demo połączenia

1. Przejdź do zakładki **"Połączenia ze sklepami"**

2. Kliknij **"+ Dodaj połączenie"**

3. Wypełnij formularz:
   - **Nazwa**: `Mój Demo Sklep`
   - **Platforma**: `WooCommerce` lub `Shopify`
   - **URL sklepu**: `https://demo.example.com` (dowolny URL)
   - **API Key**: `demo` (wpisz słowo "demo")
   - **API Secret** (tylko WooCommerce): `demo` (wpisz słowo "demo")

4. Kliknij **"Dodaj i przetestuj połączenie"**

5. Sklep zostanie dodany jako demo - możesz zsynchronizować produkty!

---

## Co robi Demo Mode?

✅ **Generuje losowe produkty** - każda synchronizacja zwraca 8-20 losowych produktów
✅ **Symuluje prawdziwe sklepy** - produkty mają realistyczne nazwy, ceny i statusy
✅ **Działa bez internetu** - wszystko działa lokalnie
✅ **Różnorodność produktów** - za każdym razem inne produkty (losowe)
✅ **Pełna funkcjonalność** - wszystkie feature działają jak w prawdziwym sklepie

---

## Przykładowe produkty demo

Demo mode losowo generuje produkty z kategorii:

**Electronics:**
- Smartwatch Fitness Pro
- Wireless Earbuds Elite
- Portable Power Bank 20000mAh
- Webcam HD 1080p
- External SSD 1TB

**Gaming:**
- Gaming Mouse RGB
- Mechanical Keyboard

**Accessories:**
- Phone Stand Adjustable
- Laptop Sleeve 15 inch
- Phone Case Premium
- Wireless Charger Pad

**Smart Home:**
- Smart Light Bulb RGB
- Security Camera WiFi
- Smart Plug Mini

**Fitness:**
- Fitness Tracker Band
- Yoga Mat Premium
- Resistance Bands Set

I wiele więcej!

---

## Testowanie funkcji

### 1. Synchronizacja produktów
- Kliknij "Synchronizuj" dla demo sklepu
- Produkty pojawią się w zakładce "Produkty i Sugestie"
- Każda synchronizacja może zwrócić inne produkty

### 2. Sugestie optymalizacyjne
- Wybierz produkt z listy
- Zobacz sugestie w panelu po prawej:
  - **Cena** - optymalizacja cenowa
  - **Promo** - propozycje promocji
  - **Bundle** - pakiety produktowe

### 3. Zastosowanie sugestii
- Kliknij "Zastosuj sugestię" dla wybranej sugestii
- Pojawi się powiadomienie o sukcesie
- Sugestia zmieni status na "Zastosowana"
- Zdarzenie pojawi się w historii

### 4. Historia zdarzeń
- Panel "Historia zdarzeń" pokazuje wszystkie akcje
- Real-time aktualizacja po każdej akcji
- Timestampy wszystkich zdarzeń

---

## Różnice między Demo a Prawdziwym sklepem

| Funkcja | Demo Mode | Prawdziwy sklep |
|---------|-----------|-----------------|
| Pobieranie produktów | ✅ Losowe produkty | ✅ Prawdziwe produkty ze sklepu |
| Synchronizacja | ✅ Instant | ✅ Wymaga połączenia z API |
| Tworzenie kuponów | ✅ Symulowane | ✅ Tworzy prawdziwe kupony |
| Aktualizacja cen | ✅ Symulowane | ✅ Aktualizuje prawdziwe ceny |
| Wymagane klucze API | ❌ Nie potrzebne | ✅ Wymagane |
| Połączenie z internetem | ❌ Nie potrzebne | ✅ Wymagane |

---

## Migracja z Demo do Prawdziwego sklepu

Gdy będziesz gotowy podłączyć prawdziwy sklep:

1. **Usuń demo sklepy**
   - Kliknij "Usuń" przy demo sklepach

2. **Dodaj prawdziwe połączenie**
   - Postępuj według instrukcji w `STORE_API_SETUP.md`
   - Dodaj prawdziwe klucze API

3. **Zsynchronizuj prawdziwe produkty**
   - Kliknij "Synchronizuj" dla prawdziwego sklepu
   - Produkty zastąpią demo produkty

---

## Wskazówki

💡 **Wielokrotne testowanie** - Możesz synchronizować demo sklepy wielokrotnie, za każdym razem otrzymując inne produkty

💡 **Testuj wszystko** - Demo mode obsługuje wszystkie funkcje aplikacji

💡 **Czysty start** - Aby zacząć od nowa:
```bash
docker-compose down -v
docker-compose up
```

💡 **Równoległe testowanie** - Możesz mieć jednocześnie demo sklepy i prawdziwe połączenia

---

## FAQ

**Q: Czy produkty demo są zapisywane?**
A: Tak! Produkty z demo mode są zapisywane w bazie jak prawdziwe produkty.

**Q: Czy mogę mieć demo i prawdziwe sklepy jednocześnie?**
A: Tak! Demo i prawdziwe połączenia mogą współistnieć.

**Q: Czy demo mode wymaga internetu?**
A: Nie! Wszystko działa lokalnie w Dockerze.

**Q: Jak często mogę synchronizować demo sklepy?**
A: Bez limitu! Każda synchronizacja generuje nowe losowe produkty.

**Q: Czy sugestie w demo mode są automatyczne?**
A: Nie, sugestie musisz dodać ręcznie lub użyć istniejących seed data.

---

## Problemy?

Jeśli coś nie działa:

1. Sprawdź logi:
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. Zrestartuj aplikację:
   ```bash
   docker-compose restart
   ```

3. Czysty restart:
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

---

**Miłego testowania!** 🚀
