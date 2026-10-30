# 0014. Linting i formatowanie kodu aplikacji: ruff bez reguł bezpieczeństwa

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0008](0008-menedzer-zaleznosci-uv.md), zadania E04-05, E04-04, E06-01, [`experiment/PROTOCOL.md`](../../experiment/PROTOCOL.md) (P3), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Kod aplikacji potrzebuje lintera i formattera, uruchamianych lokalnie i w CI. Job „lint i testy” (E06-01) będzie w obu wariantach potoku. Wariant A to z definicji CI/CD bez kontroli bezpieczeństwa (`experiment/PROTOCOL.md`). Gdyby linter zgłaszał podatności, wariant A zatrzymywałby niektóre pozycje katalogu, a porównanie wariantów (M1, M3) przestałoby mierzyć wpływ narzędzi bezpieczeństwa. Wybór dotyczy więc i narzędzia, i zestawu reguł.

## Czynniki decyzyjne

- liczba narzędzi do zainstalowania, skonfigurowania i opisania,
- czas jobu lint w CI (czas potoku jest mierzony w eksperymencie, H2a),
- trafność eksperymentu: lint nie może wykrywać pozycji katalogu,
- spójność z resztą narzędzi projektu (uv, [ADR-0008](0008-menedzer-zaleznosci-uv.md)).

## Rozważane opcje

Narzędzie:

1. ruff (lint, sortowanie importów i formatter w jednym pakiecie)
2. flake8 + black + isort
3. pylint (+ black)

Zestaw reguł:

1. reguły stylu i poprawności, bez reguł bezpieczeństwa (`S`, przeniesione z Bandita)
2. reguły stylu i poprawności razem z `S`

Dodatki z definicji zadania: mypy, hook pre-commit.

## Decyzja

Wybrano **ruff z regułami `E`, `W`, `F`, `I`, `B`, `UP`, `SIM`, bez reguł `S`**, bez mypy i bez hooka pre-commit. Powody autora:

- **Jedno narzędzie:** ruff zastępuje linter, sortowanie importów i formatter jedną konfiguracją w `pyproject.toml`.
- **Szybkość w CI:** krótszy job lint to krótszy mierzony czas potoku. Wielkość zysku względem flake8 + black + isort: TODO: zweryfikować (nie mierzono).
- **Popularność:** ruff jest dziś częstym wyborem w nowych projektach Pythona. TODO: zweryfikować (brak źródła).
- **Spójność z uv:** ten sam producent (Astral) co uv. Ruff instaluje się jako zależność grupy `dev`, a wersję blokuje `uv.lock`.
- **Bez reguł `S` — trafność eksperymentu:** lint działa w obu wariantach. Reguły `S` wykrywałyby część pozycji katalogu (np. zakodowany sekret w GT-02, `eval()` w GT-04). Wariant A miałby wtedy kontrolę bezpieczeństwa, a nie powinien jej mieć.
- **Bez hooka pre-commit:** hooka nie da się traktować jak kontroli, bo programista pominie go opcją `--no-verify`, a autorytatywną warstwą jest CI ([`docs/notes/owasp-devsecops.md`](../notes/owasp-devsecops.md), p. 6). Do tego prostota: w projekcie jednoosobowym lint i tak działa w CI i ręcznie.
- **Bez mypy:** przyjęte razem z rekomendacją agenta; autor nie podał osobnego powodu. Rekomendacja agenta: każda z 20 łatek musiałaby przechodzić też mypy, co dokłada bramkę mogącą zatrzymać pozycję w wariancie A z powodu typów, a definicja zadania traktuje mypy jako opcjonalne.

Decyzje agenta w konfiguracji, zaakceptowane przez autora 2026-10-30 bez osobnego powodu:

- `line-length = 100`. Kod był pisany pod linie około 100 znaków. Przy 100 formatter zmienił 9 plików, a przy domyślnych 88 zmieniłby 18.
- `target-version = "py313"`, mimo `requires-python = ">=3.14"`. Przy `py314` formatter ruff 0.17.3 zamienia `except (A, B):` na składnię z PEP 758 (`except A, B:`), a pyupgrade (UP037) usuwa cudzysłowy z odwołań w przód w modelach SQLAlchemy. Czy parsery skanerów SAST (Semgrep, Bandit) obsługują już składnię z PEP 758: TODO: zweryfikować. Niższy cel to środek ostrożności, który kosztuje tyle, że ruff nie proponuje składni dostępnej dopiero od 3.14.

## Konsekwencje

- (+) Jedna konfiguracja (`[tool.ruff]` w `app/pyproject.toml`) i jedna zależność `ruff` w grupie `dev`, zablokowana w `uv.lock` (0.17.3 na dzień decyzji). Eksport `requirements.txt` jej nie obejmuje, więc nie trafia do skanów SCA aplikacji.
- (+) Wariant A nie dostaje ukrytej kontroli bezpieczeństwa przez lint.
- (−) Każda łatka katalogu musi przechodzić `ruff check` i `ruff format --check`. Nie może zostawiać nieużywanych importów (F401, np. `require_admin` po GT-19), nieużywanych zmiennych (F841) ani niesformatowanego kodu. Wymóg dopisano do `experiment/PROTOCOL.md`, P3. Sprawdza go E04-04 i pilotaż P5.
- (−) Ruff nie dubluje Bandita w wariancie B. Analizę bezpieczeństwa kodu robią skanery SAST z wariantu B.
- Job lint w CI (E06-01): `uv run ruff check .` i `uv run ruff format --check .` w `app/`.

## Źródła

- Konfiguracja i wyniki uruchomienia ruff 0.17.3 na kodzie aplikacji, 2026-10-30 (dziennik).
- PyPI JSON API, `https://pypi.org/pypi/ruff/json` (wersja 0.17.3 z 2026-10-27, sprawdzone 2026-10-30).
- Źródła spoza rejestru `Zrodla/`: TODO: zweryfikować, czy rejestrować.
