# Reguły własne Semgrep

Reguły dla dwóch pozycji katalogu, dla których rejestr Semgrep i Bandit nie mają reguł (analiza: `docs/narzedzia.md`, p. 4). Decyzja autora z 2026-10-20 (`docs/metodyka.md`, p. 4.3):

- reguły opisują klasę słabości (CWE), a nie postać łatki,
- są zamrażane razem z katalogiem v1,
- w wariancie B blokują pull request tak samo jak reguły z rejestru.

| Reguła | Pozycja | CWE | Pliki |
|---|---|---|---|
| `python-log-injection` | GT-06 | CWE-117 | `python-log-injection.yaml`, testy w `python-log-injection.py` |
| `python-asgi-debug-enabled` | GT-14 | CWE-209, CWE-489 | `python-asgi-debug-enabled.yaml`, testy w `python-asgi-debug-enabled.py` |

Każda reguła ma w metadanych `custom_rule: true`. Dzięki temu wynik H1 bez reguł własnych da się policzyć z tych samych raportów.

## Co wykrywają

**`python-log-injection`** (tryb *taint*):

- **Źródła:**
  - parametry funkcji obsługujących trasy FastAPI i Starlette (`@app.get`, `@router.post` itd.),
  - dane z obiektu `Request`: `query_params`, `path_params`, `headers`, `cookies`, `url`, `json()`, `form()`, `body()`.
- **Pomijane źródła:**
  - parametry typu `int`, `float`, `bool`, `uuid.UUID` (FastAPI je waliduje, więc nie zawierają znaków nowej linii),
  - parametry z `Depends(...)`, podane wprost albo w `Annotated[..., Depends(...)]`.
- **Sanityzacja:**
  - `.replace()` dla `\n` i `\r`, `re.sub()`, `repr()`, `json.dumps()`, `.encode("unicode_escape")`,
  - `int()`, `float()`, `bool()`, `len()`.
- **Ujścia:** `logging.<poziom>(...)` i `<logger>.<poziom>(...)` dla poziomów `debug`, `info`, `warning`, `warn`, `error`, `exception`, `critical`, `fatal` i `log`.

**`python-asgi-debug-enabled`**:

- `FastAPI(..., debug=True)` i `Starlette(..., debug=True)`, także przez stałą (`DEBUG = True`, `FastAPI(debug=DEBUG)`),
- `app.debug = True` po utworzeniu aplikacji FastAPI albo Starlette.

Tryb debug czytany z konfiguracji (`debug=os.getenv(...)`) nie jest zgłaszany.

## Testy

Testy jednostkowe Semgrepa: komentarze `# ruleid:` i `# ok:` w plikach `.py`.

```bash
semgrep --test --metrics=off semgrep-rules/
```

Wynik z 2026-10-20 (Semgrep 1.181.0, Windows): 2/2 pliki testów przechodzą. Reguła GT-06 ma 8 przypadków `ruleid` i 10 `ok`, a reguła GT-14 ma 5 `ruleid` i 4 `ok`.

Katalog nie może mieć kropki na początku nazwy (np. `.semgrep/`). Semgrep 1.181.0 nie znajduje wtedy testów przy `--test <katalog>`.

## Test na kodzie spoza katalogu

Uruchomiono 2026-10-20 na dwóch publicznych projektach FastAPI (`semgrep scan --config semgrep-rules/…`, tylko pliki `*.py`). Ocena zgłoszeń jest ręczna (agent).

| Projekt (commit) | Plików | Zgłoszeń GT-06 | Trafne / fałszywe | Zgłoszeń GT-14 |
|---|---|---|---|---|
| `fastapi/full-stack-fastapi-template` (`b1125d88`) | 28 | 0 | — | 0 |
| `Netflix/dispatch` (`dd2837e8`) | 658 | 14 | 8 / 6 | 0 |

- **Trafne (8):**
  - surowe nagłówki `Authorization` i `x-amzn-oidc-data` w logu (2),
  - pola zdekodowane z nagłówka JWT (3),
  - dane z ciała żądania (3).
- **Fałszywe (6), trzy przyczyny:**
  - parametry zależności zapisane aliasem typu z innego modułu (np. `CurrentUser`), którego reguła nie rozwija;
  - pola modelu typu `int`: reguła nie zna typów pól modeli pydantic;
  - wynik funkcji wywołanej z danymi z żądania (np. odczyt z bazy), bo Semgrep domyślnie przenosi taint przez wywołania.

Na tej próbie precyzja reguły GT-06 wynosi 8/14. W eksperymencie liczą się fałszywe alarmy na wersji czystej aplikacji (H2b, M6), a styl jej kodu (aliasy zależności, logowanie pól liczbowych) wpływa na ten wynik. TODO: sprawdzić reguły na wersji czystej, gdy powstanie (E04).

## Uwagi dla potoku

- Pliki testów zawierają celowo podatny kod. Skanery w potoku (Semgrep, Bandit, CodeQL) uruchamiamy na `app/` albo wykluczamy z nich `semgrep-rules/`. W przeciwnym razie testy reguł staną się zgłoszeniami w eksperymencie.
- Wywołanie w wariancie B: `semgrep --config p/python --config semgrep-rules/ app/` (zestaw rejestru do ustalenia w E07).
- Czas pisania i testowania reguł (koszt, RQ2): TODO: zweryfikować, uzupełnia autor.
