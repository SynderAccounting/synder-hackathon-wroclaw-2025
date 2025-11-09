# Konfiguracja API dla Sklepów

Przewodnik krok po kroku jak uzyskać klucze API dla WooCommerce i Shopify.

## WooCommerce

### Wymagania
- Sklep WooCommerce na WordPress (wersja 3.5+)
- Dostęp administratora do panelu WP Admin

### Kroki konfiguracji

#### 1. Zaloguj się do panelu WordPress

Przejdź do swojego sklepu i zaloguj się jako administrator.

#### 2. Włącz REST API

1. Przejdź do: **WooCommerce → Ustawienia**
2. Kliknij zakładkę: **Zaawansowane**
3. Kliknij: **REST API**
4. Kliknij: **Dodaj klucz**

#### 3. Wypełnij formularz

- **Opis**: `Product Suggestions Manager` (lub dowolna nazwa)
- **Użytkownik**: Wybierz swojego użytkownika administratora
- **Uprawnienia**: Wybierz **Odczyt/Zapis** (Read/Write)
- Kliknij: **Generuj klucz API**

#### 4. Skopiuj klucze

Po wygenerowaniu zobaczysz:
- **Consumer Key** (np. `ck_1234567890abcdef...`)
- **Consumer Secret** (np. `cs_1234567890abcdef...`)

⚠️ **WAŻNE**: Skopiuj oba klucze teraz - nie będziesz mógł ich później ponownie zobaczyć!

#### 5. Dodaj połączenie w aplikacji

W aplikacji Product Suggestions Manager:
1. Przejdź do zakładki **"Połączenia ze sklepami"**
2. Kliknij **"+ Dodaj połączenie"**
3. Wypełnij formularz:
   - **Nazwa**: Dowolna nazwa (np. "Mój sklep WooCommerce")
   - **Platforma**: `WooCommerce`
   - **URL sklepu**: Pełny URL (np. `https://mojsklep.pl`)
   - **Consumer Key**: Wklej skopiowany `ck_...`
   - **Consumer Secret**: Wklej skopiowany `cs_...`
4. Kliknij **"Dodaj i przetestuj połączenie"**

Jeśli wszystko jest OK, zobaczysz komunikat o sukcesie!

---

## Shopify

### Wymagania
- Sklep Shopify (dowolny plan)
- Dostęp właściciela sklepu lub uprawnienia do zarządzania aplikacjami

### Kroki konfiguracji

#### Opcja A: Custom App (Zalecane)

##### 1. Włącz Custom Apps

1. Zaloguj się do panelu Shopify Admin
2. Przejdź do: **Settings → Apps and sales channels**
3. Kliknij: **Develop apps**
4. Jeśli widzisz komunikat o włączeniu custom apps, kliknij **Allow custom app development**

##### 2. Utwórz Custom App

1. Kliknij: **Create an app**
2. **App name**: `Product Suggestions Manager`
3. **App developer**: Wybierz siebie
4. Kliknij: **Create app**

##### 3. Skonfiguruj uprawnienia (Scopes)

1. Kliknij: **Configure Admin API scopes**
2. Zaznacz następujące uprawnienia:
   - `read_products` - Odczyt produktów
   - `write_products` - Zapis produktów
   - `read_price_rules` - Odczyt reguł cenowych
   - `write_price_rules` - Zapis reguł cenowych
   - `read_discounts` - Odczyt rabatów
   - `write_discounts` - Zapis rabatów
3. Kliknij: **Save**

##### 4. Instaluj App

1. Kliknij zakładkę: **API credentials**
2. Kliknij: **Install app**
3. Potwierdź instalację

##### 5. Skopiuj Access Token

Po instalacji zobaczysz:
- **Admin API access token**: `shpat_1234567890abcdef...`

⚠️ **WAŻNE**: Skopiuj token teraz - nie będziesz mógł go później ponownie zobaczyć!

##### 6. Znajdź nazwę sklepu

Twoja nazwa sklepu to część przed `.myshopify.com` w URLu:
- Jeśli URL to `https://mojesklep.myshopify.com` → Nazwa to: `mojesklep.myshopify.com`

#### Opcja B: Private App (Starsze sklepy)

Jeśli masz starszy sklep Shopify:

1. Przejdź do: **Apps → Manage private apps**
2. Kliknij: **Create new private app**
3. Wypełnij nazwę i email
4. W sekcji **Admin API** zaznacz uprawnienia jak w opcji A
5. Kliknij: **Save**
6. Skopiuj **Password** (to jest Twój access token)

#### 7. Dodaj połączenie w aplikacji

W aplikacji Product Suggestions Manager:
1. Przejdź do zakładki **"Połączenia ze sklepami"**
2. Kliknij **"+ Dodaj połączenie"**
3. Wypełnij formularz:
   - **Nazwa**: Dowolna nazwa (np. "Mój sklep Shopify")
   - **Platforma**: `Shopify`
   - **URL sklepu**: Format `mojesklep.myshopify.com` (bez `https://`)
   - **Access Token**: Wklej skopiowany `shpat_...`
4. Kliknij **"Dodaj i przetestuj połączenie"**

---

## Testowanie połączenia

Po dodaniu połączenia:

1. Jeśli test się powiedzie, zobaczysz połączenie na liście ze statusem **"Aktywne"**
2. Kliknij **"Synchronizuj"** aby pobrać produkty ze sklepu
3. Przejdź do zakładki **"Produkty i Sugestie"** aby zobaczyć zsynchronizowane produkty

---

## Rozwiązywanie problemów

### WooCommerce

**Problem**: "Connection test failed"

Możliwe przyczyny:
- ❌ Nieprawidłowy URL sklepu - upewnij się że używasz pełnego `https://`
- ❌ Błędnie skopiowane klucze - sprawdź czy nie ma spacji na początku/końcu
- ❌ REST API jest wyłączone - sprawdź ustawienia permalinków WordPress
- ❌ Problem z SSL - niektóre serwery wymagają prawidłowego certyfikatu SSL

**Rozwiązanie**:
1. Sprawdź czy możesz otworzyć `https://mojsklep.pl/wp-json/wc/v3` w przeglądarce
2. Upewnij się że permalinki są włączone (nie "Plain")
3. Zregeneruj klucze API i spróbuj ponownie

### Shopify

**Problem**: "Connection test failed"

Możliwe przyczyny:
- ❌ Nieprawidłowy format URL - użyj `mojesklep.myshopify.com` (bez https://)
- ❌ Błędnie skopiowany token
- ❌ Brak wymaganych uprawnień (scopes)
- ❌ App został odinstalowany

**Rozwiązanie**:
1. Sprawdź format URL - tylko nazwa sklepu z `.myshopify.com`
2. Upewnij się że app jest zainstalowany i aktywny
3. Sprawdź czy zaznaczone są wszystkie wymagane uprawnienia
4. Zregeneruj access token jeśli to możliwe

---

## Bezpieczeństwo

### ✅ Dobre praktyki

- Klucze API są **automatycznie szyfrowane** w bazie danych
- Używaj silnego hasła do szyfrowania (zmienna `ENCRYPTION_KEY`)
- Nie udostępniaj kluczy API nikomu
- Regularnie rotuj klucze API (co 3-6 miesięcy)
- Używaj odrębnych kluczy dla środowisk testowych i produkcyjnych

### ⚠️ Ostrzeżenia

- Nigdy nie commituj kluczy API do repozytorium Git
- Nie udostępniaj screenshotów z widocznymi kluczami
- Jeśli klucz wycieknie - natychmiast go zregeneruj

---

## Sklepy testowe

Jeśli nie masz jeszcze sklepu, możesz utworzyć testowy:

### WooCommerce (Darmowy)
1. Załóż darmowe konto na [InstaWP](https://instawp.com/) lub [TasteWP](https://tastewp.com/)
2. Wybierz szablon z WooCommerce
3. Postępuj zgodnie z instrukcjami powyżej

### Shopify (14 dni trial)
1. Przejdź na [shopify.com/free-trial](https://www.shopify.com/free-trial)
2. Załóż konto (nie potrzebujesz karty kredytowej przez pierwsze 3 dni)
3. Postępuj zgodnie z instrukcjami powyżej

---

## Dalsze kroki

Po skonfigurowaniu połączeń:

1. **Synchronizuj produkty** - Kliknij "Synchronizuj" dla każdego połączenia
2. **Sprawdź produkty** - Przejdź do zakładki "Produkty i Sugestie"
3. **Zastosuj sugestie** - Wybierz produkt i przetestuj sugestie optymalizacyjne

Miłego użytkowania!
