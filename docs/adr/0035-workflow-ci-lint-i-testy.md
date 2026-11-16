# 0035. Workflow CI wariantu A: dwa joby (lint, testy), uv z setup-uv bez cache, baza z compose

- **Status:** przyjęty
- **Data:** 2026-11-16
- **Decydujący:** autor pracy
- **Powiązane:** [0008](0008-menedzer-zaleznosci-uv.md), [0011](0011-baza-danych-testow-postgresql.md), [0014](0014-linting-i-formatowanie-ruff.md), [0023](0023-uruchamianie-stosu-docker-compose.md), zadanie E06-01, `.github/workflows/baseline-ci.yml`, `experiment/PROTOCOL.md` (K2, K12), [dziennik 2026-11-16](../log/2026-11-16.md)

## Kontekst

Potok bazowy (wariant A) zaczyna się od sprawdzenia kodu: ruff (ADR-0014) i pytest na PostgreSQL (ADR-0011). Ten sam rdzeń trafi do wariantu B, bo workflow A powstaje z workflow B przez usunięcie kroków bezpieczeństwa, a build, testy, publikacja i wdrożenie są identyczne (`PROTOCOL.md`, K2). Czas potoku jest metryką eksperymentu (E06-04, E09-04), więc sposób instalacji zależności i podział na joby wpływają na dane. Trzeba ustalić: jak job dostaje uv i Pythona, czy używa pamięci podręcznej zależności, skąd bierze bazę danych, jak dzieli kroki na joby i na jakich gałęziach się uruchamia.

## Czynniki decyzyjne

- porównywalność czasów potoku między przebiegami i wariantami,
- jedna wersja narzędzi lokalnie, w CI i w obrazie (`uv.lock`, AGENTS.md, zasada 6),
- liczba akcji zewnętrznych do przypięcia i aktualizowania (łańcuch dostaw, AGENTS.md, zasada 5),
- czytelność wyniku w pull requeście,
- zgodność z wcześniejszymi decyzjami (ADR-0023: jeden opis środowiska lokalnie i w CI).

## Rozważane opcje

Instalacja uv i Pythona:

1. akcja `astral-sh/setup-uv` (Python według `app/.python-version`)
2. `actions/setup-python`, potem `pip install uv`
3. job w kontenerze `ghcr.io/astral-sh/uv`

Pamięć podręczna zależności:

1. bez cache: każdy przebieg instaluje zależności od zera
2. cache uv w GitHub Actions (klucz z `uv.lock`)

Baza danych dla testów:

1. `docker compose up -d --wait db` z `app/compose.yaml` i `.env` z `scripts/ci-env.sh`
2. kontener usługi GitHub Actions (`services: postgres`), jak zapowiadał ADR-0011

Podział na joby:

1. dwa joby równolegle: `lint` i `test`
2. jeden job: lint, potem testy

Wyzwalacze:

1. `pull_request` i `push` na `main` oraz `exp/variant-*`
2. tylko `main`, a `exp/variant-*` dopisane przy tworzeniu gałęzi wariantów
3. `push` na każdej gałęzi i `pull_request`

## Decyzja

Wybrano **dwa joby (`lint`, `test`), uv z `astral-sh/setup-uv` bez cache, PostgreSQL z `compose.yaml` i wyzwalacze na `main` oraz `exp/variant-*`**. Powody autora:

- **`setup-uv`:** jedna akcja instaluje uv i Pythona.
- **Bez cache:** porównywalne czasy. Czas potoku jest metryką eksperymentu, a cache wprowadza zmienność zależną od tego, czy klucz trafił.
- **Baza z compose:** powody z ADR-0023 (jedno źródło lokalnie i w CI; `services:` działa tylko w CI, więc środowisko trzeba by opisać drugi raz). Ta decyzja zastępuje zapowiedź usługi `postgres` z ADR-0011.
- **Dwa joby:**
  - osobne czasy lintu i testów w danych z GitHub API (E06-04),
  - czytelny wynik: w pull requeście widać od razu, czy zawiódł lint, czy testy.
- **Wyzwalacze `main` i `exp/variant-*`:** zgodność z protokołem. Wyzwalacz „main” w metodyce oznacza push na gałąź bazową wariantu (`PROTOCOL.md`).

Postać workflow (decyzje agenta przy implementacji):

- uv 0.13.6, ta sama wersja co w `app/Dockerfile`; akcja sprawdza sumę SHA-256 pobranego archiwum uv (wejście `checksum`),
- `enable-cache: "false"` jawnie, bo domyślne `auto` włącza cache na runnerach GitHub,
- `uv sync --locked` (błąd, gdy `uv.lock` nie zgadza się z `pyproject.toml`), potem `uv run --no-sync`,
- `ruff check --output-format=github`, żeby zgłoszenia pojawiały się przy liniach w pull requeście,
- `permissions: {}` na poziomie workflow, `contents: read` w jobach, `persist-credentials: false` w checkout,
- `concurrency` na gałąź bez anulowania: przebiegi czekają w kolejce, więc żaden nie znika z danych czasowych,
- `timeout-minutes`: 10 dla `lint`, 15 dla `test`; `docker compose down --volumes` na końcu joba `test`,
- akcje przypięte do SHA: `actions/checkout` v7.0.1 (`3d3c42e…`), `astral-sh/setup-uv` v10.3.3 (`68559e9…`).

## Konsekwencje

- (+) Wariant B dostaje te same dwa joby bez zmian, a joby bezpieczeństwa dochodzą obok nich; diff A/B w pilotażu (K2) pokaże tylko kroki bezpieczeństwa.
- (+) Każdy przebieg CI ma nowe sekrety w `app/.env` (ADR-0023), a w repozytorium nie ma wartości testowych.
- (+) Brak zapisu do repozytorium i do rejestru: job ma tylko prawo odczytu kodu.
- (−) Bez cache każdy przebieg pobiera Pythona 3.14 i wszystkie zależności. Ile to kosztuje czasu: TODO: zweryfikować w danych z E06-04.
- (−) Obie akcje instalują zależności osobno, więc pobieranie jest podwójne.
- (−) Przebiegi z `push` i `pull_request` na tej samej gałęzi PR liczą się osobno. Które przebiegi wchodzą do pomiaru, ustala E06-04 i `PROTOCOL.md`.
- Spójności `requirements.txt` z `uv.lock` (ADR-0008) ten workflow nie sprawdza: TODO: zweryfikować, czy to krok wspólny wariantów (E06) czy część E07.
- Job `build` (E06-02) i `deploy` (E06-03) dochodzą do tego samego pliku.

## Źródła

- `astral-sh/setup-uv`, `action.yml` w commicie `68559e99cc807c1eb7e9238fd43a15bba460eec2` (wejścia `version`, `checksum`, `enable-cache`, sprawdzone 2026-11-16): źródło spoza rejestru `Zrodla/`, TODO: zweryfikować, czy rejestrować.
- Wydanie `astral-sh/uv` 0.13.6, plik `uv-x86_64-unknown-linux-gnu.tar.gz.sha256` (sprawdzone 2026-11-16).
