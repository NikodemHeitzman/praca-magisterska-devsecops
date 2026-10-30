# Specyfikacja funkcjonalna aplikacji badawczej

Zadanie E04-01. Specyfikacja opisuje wersję czystą aplikacji (gałąź `main`) i wskazuje w niej miejsca, w które łatki z katalogu (`experiment/ground-truth.yaml`) wprowadzają podatności. Samych łatek i gałęzi `seed/*` dotyczy E04-04.

Wersja: v0 (2026-10-30). Przed pierwszą próbą serii właściwej specyfikacja musi być zgodna z zamrożonym katalogiem v1 (`experiment/PROTOCOL.md`, P1).

## 1. Decyzje

Wszystkie podjął autor 2026-10-30. Agent przedstawiał opcje.

| Decyzja | Wybór | Powód autora | Odrzucone |
|---|---|---|---|
| Domena | system zgłoszeń (ticketów) zespołu | domena naturalnie mieści cały katalog: właściciel zasobu, role, wyszukiwanie, załączniki | notatki zespołu (rola administratora i sortowanie mniej naturalne); biblioteka dokumentów (pasuje głównie do GT-05) |
| Baza danych | PostgreSQL, w `compose.yaml` jako osobny kontener | realizm wdrożenia: aplikacje webowe w chmurze zwykle korzystają z serwera bazy | SQLite (rzadko na produkcji); SQLite lokalnie i PostgreSQL w AWS (różne środowiska osłabiają kontrolę zmiennych) |
| Załączniki | obiekty w S3, pobieranie przez lokalny katalog podręczny na dysku kontenera | S3 to typowy wzorzec chmurowy (kontener bezstanowy, pliki w usłudze zarządzanej); katalog lokalny zostawia GT-05 bez zmian w katalogu | sam S3 (path traversal w kluczu S3 to inna postać błędu, reguły SAST na ścieżkach plików by jej nie objęły); zmiana GT-05 przed zamrożeniem v1; dysk zamiast S3 |
| Wyjątek dla GT-14 | naturalny błąd w logice zmiany statusu zgłoszenia (p. 5) | TODO: zweryfikować, powód do uzupełnienia przez autora | osobny endpoint diagnostyczny (sztuczny, a pająk ZAP mógłby na niego trafić) |

Kontener z bazą to rozdzielenie komponentów uruchomieniowych, a nie architektura mikroserwisowa (ADR-0002). Czy w AWS baza będzie kontenerem, czy usługą zarządzaną (RDS), rozstrzyga E05. TODO: ADR dla bazy danych i przechowywania załączników.

## 2. Domena i role

Zespół zgłasza i obsługuje problemy (zgłoszenia). Zgłoszenie ma autora, priorytet, status i opcjonalne załączniki.

| Rola | Uprawnienia |
|---|---|
| `user` | zakłada zgłoszenia; widzi, edytuje i usuwa tylko własne; dodaje i pobiera załączniki własnych zgłoszeń; edytuje własny profil bez zmiany roli |
| `admin` | wszystko, co `user`, dla wszystkich zgłoszeń; lista użytkowników i zmiana ich ról |

Rejestracja zawsze tworzy konto z rolą `user`. Konto administratora powstaje tylko w skrypcie danych startowych (p. 6).

## 3. Model danych

Klucze główne są liczbami całkowitymi z autoinkrementacją. Kolejne identyfikatory łatwo zgadnąć, co jest typowe dla małych aplikacji i daje GT-18 realistyczną postać.

**`users`**

| Pole | Typ | Uwagi |
|---|---|---|
| `id` | integer, PK | |
| `username` | varchar, unikalne | login w formularzu OAuth2 |
| `email` | varchar, unikalne | |
| `full_name` | varchar, null | |
| `password_hash` | varchar | Argon2 (p. 7) |
| `role` | enum `user`/`admin` | domyślnie `user` |
| `created_at` | timestamp | |

**`tickets`**

| Pole | Typ | Uwagi |
|---|---|---|
| `id` | integer, PK | |
| `title` | varchar | przeszukiwane (GT-01) |
| `description` | text | przeszukiwane (GT-01) |
| `status` | enum `open`/`in_progress`/`resolved`/`closed` | zmiana tylko przez endpoint statusu (p. 5) |
| `priority` | enum `low`/`medium`/`high` | |
| `owner_id` | integer, FK → `users.id` | właściciel (GT-18) |
| `created_at`, `updated_at` | timestamp | |

**`attachments`**

| Pole | Typ | Uwagi |
|---|---|---|
| `id` | integer, PK | |
| `ticket_id` | integer, FK → `tickets.id` | |
| `filename` | varchar | nazwa pliku po oczyszczeniu, unikalna w obrębie zgłoszenia |
| `s3_key` | varchar | `tickets/<ticket_id>/<filename>` |
| `content_type` | varchar | |
| `size` | integer | bajty |
| `uploaded_by` | integer, FK → `users.id` | |
| `created_at` | timestamp | |

Schemat tworzą migracje (narzędzie: E04-02, np. Alembic).

## 4. Endpointy

API zwraca JSON pod prefiksem `/api`. Uwierzytelnianie: token JWT (HS256) w nagłówku `Authorization: Bearer`. Aplikacja nie używa ciasteczek sesyjnych, więc CORS działa z `allow_credentials=False` (wymóg GT-12).

### 4.1. Uwierzytelnianie i profil

| Metoda i ścieżka | Dostęp | Opis | Pozycje |
|---|---|---|---|
| `POST /api/auth/register` | publiczny | JSON: `username`, `email`, `password`, `full_name`. Tworzy konto z rolą `user`, hasło jako skrót Argon2. 201 albo 409 przy zajętym loginie lub e-mailu. | GT-03 |
| `POST /api/auth/login` | publiczny | Formularz `OAuth2PasswordRequestForm` (pola `username`, `password`). Zwraca `access_token`. Przy nieudanym logowaniu handler trasy zapisuje ostrzeżenie z nazwą użytkownika po neutralizacji znaków nowej linii. 401 przy błędnych danych. | GT-02, GT-03, GT-06 |
| `GET /api/users/me` | zalogowany | Profil bieżącego użytkownika (bez skrótu hasła). | |
| `PATCH /api/users/me` | zalogowany | Model wejściowy `UserProfileUpdate` z polami `full_name` i `email`. Handler przypisuje pola z `model_dump(exclude_unset=True)` w pętli. | GT-20 |

### 4.2. Zgłoszenia

| Metoda i ścieżka | Dostęp | Opis | Pozycje |
|---|---|---|---|
| `POST /api/tickets` | zalogowany | Tworzy zgłoszenie (`title`, `description`, `priority`) ze statusem `open`; właścicielem jest bieżący użytkownik. | |
| `GET /api/tickets` | zalogowany | Lista zgłoszeń: `user` widzi własne, `admin` wszystkie. Parametry: `status`, `sort` (nazwa pola z listy dozwolonych: `created_at`, `priority`, `status`, `title`), `order` (`asc`/`desc`), `limit`, `offset`. | GT-04 |
| `GET /api/tickets/search?q=` | zalogowany | Wyszukiwanie fragmentu tekstu w `title` i `description` (bez rozróżniania wielkości liter) wśród zgłoszeń widocznych dla użytkownika. Zapytanie SQL przez `text()` z parametrem wiązanym. | GT-01 |
| `GET /api/tickets/{id}` | właściciel albo `admin` | Szczegóły zgłoszenia z listą załączników. 404, gdy zgłoszenie nie istnieje albo nie należy do użytkownika. | GT-18 |
| `PATCH /api/tickets/{id}` | właściciel albo `admin` | Zmiana `title`, `description`, `priority`. | |
| `POST /api/tickets/{id}/status` | właściciel albo `admin` | JSON: `status`. Zmiana statusu według tabeli przejść (p. 5). 409 przy niedozwolonym przejściu. | GT-14 (wywołanie wyjątku) |
| `DELETE /api/tickets/{id}` | właściciel albo `admin` | Usuwa zgłoszenie z załącznikami (rekordy i obiekty S3). | |

Wersja czysta odpowiada 404, a nie 403, na zgłoszenie innego użytkownika, żeby nie ujawniać, że zasób istnieje.

### 4.3. Załączniki

| Metoda i ścieżka | Dostęp | Opis | Pozycje |
|---|---|---|---|
| `POST /api/tickets/{id}/attachments` | właściciel albo `admin` | Upload `multipart/form-data`. Nazwa pliku oczyszczona (tylko nazwa bez katalogów, dozwolony zestaw znaków). Limit rozmiaru i lista typów w konfiguracji. Zapis do S3 pod `s3_key`. | |
| `GET /api/tickets/{id}/attachments` | właściciel albo `admin` | Lista załączników zgłoszenia. | |
| `GET /api/tickets/{id}/attachments/{filename}` | właściciel albo `admin` | Pobranie pliku. Ścieżka w katalogu podręcznym: `ATTACHMENT_CACHE_DIR/<id>/<filename>`. Wersja czysta normalizuje ścieżkę (`resolve()`) i sprawdza, czy leży w katalogu podręcznym; inaczej 404. Gdy pliku nie ma lokalnie, aplikacja pobiera obiekt z S3 do katalogu podręcznego, a potem zwraca go przez `FileResponse`. | GT-05 |

### 4.4. Administracja

| Metoda i ścieżka | Dostęp | Opis | Pozycje |
|---|---|---|---|
| `GET /api/admin/users` | `admin` | Lista użytkowników z rolami. Zależność `require_admin` sprawdza rolę. | GT-19 |
| `PATCH /api/admin/users/{id}/role` | `admin` | Zmiana roli użytkownika. | |

### 4.5. Strony HTML i endpointy systemowe

| Metoda i ścieżka | Dostęp | Opis | Pozycje |
|---|---|---|---|
| `GET /` | publiczny | Strona startowa (szablon Jinja2) z opisem aplikacji i odnośnikami do `/login` i `/docs`. | GT-07, GT-13 |
| `GET /login` | publiczny | Strona z formularzem logowania (Jinja2), wysyłanym do `POST /api/auth/login`. | GT-07, GT-13 |
| `GET /health` | publiczny | `{"status": "ok"}` i stan połączenia z bazą. Używany w `HEALTHCHECK` (E05-01) i w potoku przed skanem DAST. | |
| `GET /docs`, `GET /openapi.json` | publiczny | Dokumentacja OpenAPI generowana przez FastAPI. | |

Strony `/` i `/login` są celem pająka ZAP: przy domyślnym progu reguła `10020` sprawdza tylko odpowiedzi HTML (`docs/narzedzia.md`, GT-13). Obie są osiągalne bez logowania z adresu głównego. Czy ZAP w potoku działa bez uwierzytelnienia: TODO: zweryfikować w E07.

## 5. Zmiana statusu i wyjątek dla GT-14

Tabela dozwolonych przejść w wersji czystej:

| Z | Do |
|---|---|
| `open` | `in_progress`, `closed` |
| `in_progress` | `open`, `resolved` |
| `resolved` | `open`, `closed` |

Tabela jest słownikiem, a handler odczytuje `ALLOWED_TRANSITIONS[current]`. Stan `closed` nie ma w słowniku klucza, więc każda próba zmiany statusu zamkniętego zgłoszenia kończy się nieobsłużonym `KeyError` i odpowiedzią 500. To celowo pozostawiony błąd logiki, a nie pozycja katalogu:

- w wersji czystej (`debug=False`) klient dostaje tylko `Internal Server Error`,
- po łatce GT-14 (`FastAPI(debug=True)`) ten sam ciąg żądań zwraca stack trace, co sprawdza audyt (`PROTOCOL.md`, p. 4.4),
- wywołanie wymaga zalogowania i żądań POST (utworzenie i zamknięcie zgłoszenia, potem zmiana statusu), więc pająk ZAP baseline nie trafi na nie przypadkiem i nie wywoła w wersji czystej zgłoszenia `90022`,
- błąd opisujemy w kodzie komentarzem i testem, który sprawdza odpowiedź 500 (E04-03), żeby nikt go nie naprawił przypadkiem.

Powtarzalny scenariusz: zaloguj się kontem testowym, `POST /api/tickets`, `POST /api/tickets/{id}/status` z `closed`, ponownie `POST /api/tickets/{id}/status` z dowolnym statusem.

## 6. Konta testowe i dane startowe

Wymóg z `PROTOCOL.md`, p. 4.6. Skrypt danych startowych (E04-02/E04-03) tworzy:

| Login | Rola | Dane |
|---|---|---|
| `alice` | `user` | co najmniej jedno zgłoszenie z załącznikiem |
| `bob` | `user` | co najmniej jedno zgłoszenie |
| `admin` | `admin` | brak |

Dane są fikcyjne. Hasła pochodzą ze zmiennych środowiskowych skryptu (lokalnie z `.env`, w AWS z GitHub Secrets), nigdy z repozytorium. Konta `alice` i `bob` służą audytowi GT-18–20: odczyt zgłoszenia drugiego użytkownika, wywołanie `GET /api/admin/users` przez zwykłego użytkownika i próba nadania sobie roli przez `PATCH /api/users/me`.

## 7. Konfiguracja i wymagania niefunkcjonalne

Konfiguracja przez zmienne środowiskowe (klasa ustawień `pydantic-settings`):

| Zmienna | Znaczenie |
|---|---|
| `DATABASE_URL` | połączenie z PostgreSQL |
| `JWT_SECRET` | klucz podpisywania tokenów, bez wartości domyślnej (GT-02) |
| `JWT_EXPIRE_MINUTES` | ważność tokenu |
| `CORS_ORIGINS` | lista dozwolonych źródeł (GT-12) |
| `S3_BUCKET` | kubełek na załączniki |
| `S3_ENDPOINT_URL` | opcjonalny adres zgodnej z S3 usługi lokalnie i w CI (TODO: zweryfikować wybór w E04-02/E05, np. MinIO w `compose.yaml`) |
| `ATTACHMENT_CACHE_DIR` | katalog podręczny załączników (GT-05) |
| `MAX_UPLOAD_BYTES`, `ALLOWED_CONTENT_TYPES` | limity uploadu (wartości: E04-02) |
| `LOG_LEVEL` | poziom logowania |

W AWS aplikacja korzysta z S3 przez rolę IAM, bez kluczy dostępowych (zasada 4 w `AGENTS.md`).

Wymagania:

- **Hasła:** Argon2 (biblioteka: E04-02).
- **Nagłówki bezpieczeństwa:** middleware dodaje do każdej odpowiedzi `Content-Security-Policy` z `frame-ancestors 'none'` i `X-Frame-Options: DENY` (GT-13). Zestaw pozostałych nagłówków: E04-02.
- **CORS:** `app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, ...)`. Konfiguracja w konstruktorze `FastAPI(middleware=[...])` jest wykluczona, bo reguła Semgrep jej nie obejmuje (decyzja autora z 2026-10-20).
- **Tryb debug:** `FastAPI()` bez argumentu `debug` i bez odczytu trybu z konfiguracji. Łatka GT-14 dopisuje dosłownie `debug=True` (decyzja autora z 2026-10-28).
- **Logi:** na standardowe wyjście. Zdarzenia uwierzytelniania (nieudane logowanie) loguje bezpośrednio handler trasy, a nie funkcja pomocnicza, bo reguła własna GT-06 analizuje jedną funkcję (`semgrep-rules/README.md`).
- **Zgodność z Pythonem 3.9:** kod działa na Pythonie 3.9 (warunek GT-08): bez `match` i bez unii `X | Y` w adnotacjach, które Pydantic i FastAPI wyliczają w czasie działania (`Optional[...]`, `Union[...]`). Czy wersje zależności z lockfile instalują się na 3.9 i działają z jinja2 3.1.2 (GT-07): TODO: zweryfikować w E04-02.
- **Testy:** pytest z `TestClient`, pokrycie co najmniej 70% (E04-03).

## 8. Miejsca pod pozycje katalogu

„Wersja czysta” opisuje stan na `main`. „Łatka” to skrót opisu z katalogu. Dokładną postać łatek ustala E04-04.

| ID | Miejsce | Wersja czysta | Łatka |
|---|---|---|---|
| GT-01 | `GET /api/tickets/search` | `text()` z parametrem wiązanym `:q` | zapytanie składane f-stringiem z `q` |
| GT-02 | moduł konfiguracji | `jwt_secret` z `JWT_SECRET` przez klasę ustawień | stała `JWT_SECRET = "<fikcyjna wartość>"` w module konfiguracji |
| GT-03 | rejestracja i logowanie | Argon2 | `hashlib.md5(...)` |
| GT-04 | `GET /api/tickets`, parametr `sort` | nazwa pola z listy dozwolonych | wyrażenie z `sort` przekazane do `eval()` |
| GT-05 | `GET /api/tickets/{id}/attachments/{filename}` | normalizacja i sprawdzenie katalogu podręcznego | ścieżka bez normalizacji i sprawdzenia |
| GT-06 | `POST /api/auth/login`, nieudane logowanie | nazwa użytkownika po `.replace()` znaków `\n` i `\r` | nazwa użytkownika bez neutralizacji |
| GT-07 | lockfile (E04-02) | aktualna wersja `jinja2` | `jinja2==3.1.2` |
| GT-08 | `Dockerfile`, `FROM` (E05-01) | aktualny obraz Pythona przypięty digestem | `python:3.9-slim-bullseye` przypięty digestem |
| GT-09 | `Dockerfile` (E05-01) | `USER` z nieuprzywilejowanym użytkownikiem tylko w etapie końcowym | brak `USER` |
| GT-10 | Terraform, grupa zabezpieczeń (E05) | brak reguły dla portu 22 | ingress tcp/22 z `0.0.0.0/0` |
| GT-11 | Terraform, kubełek S3 na załączniki albo wolumen (E05) | szyfrowanie w spoczynku | szyfrowanie wyłączone (TODO: zweryfikować, czy dla S3 da się je wyłączyć; katalog dopuszcza EBS) |
| GT-12 | `add_middleware(CORSMiddleware, ...)` | `allow_origins` z konfiguracji | `allow_origins=["*"]` |
| GT-13 | middleware nagłówków bezpieczeństwa | CSP `frame-ancestors 'none'` i `X-Frame-Options: DENY` | oba usunięte |
| GT-14 | konstruktor `FastAPI()` | bez `debug` | `debug=True`; stack trace widoczny przy wyjątku z p. 5 |
| GT-15 | workflow wdrożeniowy (E07) | minimalne uprawnienia per job | `permissions: write-all` |
| GT-16 | workflow (E07) | akcje przypięte do SHA | akcja przez tag |
| GT-17 | workflow wyzwalany przez PR (E07) | brak wyrażeń kontekstu zdarzenia w `run` (postać: E07) | tytuł PR wstawiony wyrażeniem do `run` |
| GT-18 | `GET /api/tickets/{id}` | sprawdzenie `owner_id` albo roli `admin` | brak sprawdzenia właściciela |
| GT-19 | `GET /api/admin/users` | zależność `require_admin` | zależność tylko od zalogowania |
| GT-20 | `UserProfileUpdate` w `PATCH /api/users/me` | model bez pola `role` | model z polem `role` |

Postać wersji czystej przy GT-01, GT-05, GT-06, GT-12, GT-14 i GT-20 wybrano tak, żeby łatka zmieniała jak najmniej kodu. Każda pozycja to wtedy jedna, czytelna zmiana w PR.

## 9. Poza zakresem

- interfejs użytkownika poza dwiema stronami HTML (bez SPA),
- komentarze do zgłoszeń, powiadomienia e-mail, przypisywanie zgłoszeń do innych osób,
- odświeżanie tokenów, wylogowanie po stronie serwera, ograniczanie liczby prób logowania.

Braki te mogą dać prawdziwe zgłoszenia spoza katalogu (np. ZAP o braku tokenów CSRF w formularzu `/login`). Klasyfikujemy je według metodyki (`docs/metodyka.md`, p. 3.3) i nie dopasowujemy pod nie kodu wersji czystej.

## 10. Otwarte kwestie

- Powód wyboru naturalnego błędu dla GT-14: do uzupełnienia przez autora.
- ADR dla bazy danych i przechowywania załączników.
- Usługa zgodna z S3 lokalnie i w CI (skan DAST na `compose.yaml`): E04-02/E05.
- Zgodność zależności z Pythonem 3.9 i jinja2 3.1.2: E04-02. Wymóg 3.9 może wymusić starsze wersje zależności, a te mogą mieć znane podatności spoza katalogu.
- Fałszywe alarmy reguły GT-06 na wersji czystej (aliasy zależności, pola liczbowe; `semgrep-rules/README.md`): sprawdzić po E04-03. Kodu nie dopasowujemy pod regułę.
- Czy wersja czysta przechodzi bramki wariantu B (`docs/notes/owasp-devsecops.md`, stan bazowy): seria próbna.
