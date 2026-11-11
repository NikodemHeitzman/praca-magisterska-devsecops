# 0022. Obraz kontenera aplikacji: python:3.14-slim bez pip, uv w etapie budowania, migracje poza obrazem

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0002](0002-konteneryzacja-docker.md), [0007](0007-wersja-pythona-aplikacji.md), [0008](0008-menedzer-zaleznosci-uv.md), zadanie E05-01, `app/Dockerfile`, `experiment/ground-truth.yaml` (GT-08, GT-09), [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Aplikacja ma działać w kontenerze lokalnie, w CI (skan DAST) i w AWS (ADR-0002). Dockerfile wersji czystej jest też punktem wyjścia dla dwóch pozycji katalogu: GT-08 (starszy digest tego samego obrazu bazowego) i GT-09 (brak instrukcji `USER`). Trzeba było wybrać obraz bazowy, sposób instalacji zależności w obrazie i to, czy kontener sam uruchamia migracje bazy.

## Czynniki decyzyjne

- utrzymanie i przewidywalność obrazu bazowego,
- łatwość diagnozowania i napisania `HEALTHCHECK`,
- zgodność wersji zależności między komputerem autora, CI i obrazem,
- czas budowania w CI (czas potoku jest mierzony w eksperymencie),
- zakres odpowiedzialności i uprawnień kontenera aplikacji.

## Rozważane opcje

Obraz bazowy:

1. `python:3.14-slim` (Debian)
2. distroless
3. `python:3.14-alpine`
4. Chainguard / Wolfi

Instalacja zależności:

1. uv skopiowany z obrazu `ghcr.io/astral-sh/uv` (przypiętego digestem), `uv sync --frozen --no-dev`
2. `pip install --require-hashes -r requirements.txt`
3. uv instalowany z PyPI w etapie budowania

Migracje Alembic:

1. osobne polecenie (`docker compose run --rm app alembic upgrade head`)
2. skrypt startowy obrazu (`alembic upgrade head`, potem `uvicorn`)

pip z obrazu bazowego w etapie końcowym (pytanie powstało po pierwszym skanie Trivy, zob. Kontekst skanu niżej):

1. usunąć pip w etapie końcowym
2. zostawić i opisać zgłoszenia jako znany szum spoza katalogu
3. wyjątki w konfiguracji Trivy (`.trivyignore`) w wariancie B

Starszy digest do łatki GT-08 (tag `python:3.14-slim` w kolejnych wydaniach 3.14.x):

1. 3.14.6 (2026-08-05, Debian 13.6)
2. 3.14.7 (2026-09-25, Debian 13.7)
3. 3.14.5 (2026-05-22, Debian 13.5)
4. 3.14.8 albo 3.14.9 (październik 2026)

## Decyzja

Wybrano **`python:3.14-slim`, uv z obrazu Astral i migracje osobnym poleceniem**. Powody autora:

- **`python:3.14-slim`:**
  - oficjalny obraz,
  - prostota i debugowanie: obraz ma powłokę, więc łatwiej diagnozować kontener i napisać `HEALTHCHECK` niż w distroless.
- **uv z obrazu Astral:**
  - jeden lockfile: obraz instaluje ten sam `uv.lock` co komputer autora i CI (ciągłość z ADR-0008),
  - szybkość budowania w CI. Wielkość zysku względem `pip`: TODO: zweryfikować (nie mierzono).
- **Migracje osobnym poleceniem:**
  - prostszy obraz, który tylko uruchamia aplikację,
  - mniej uprawnień: aplikacja nie musi startować z prawem do zmiany schematu bazy.
- **Usunięcie pip:** czysta wersja bazowa, czyli wersja czysta bez zgłoszeń spoza katalogu, więc pomiar wykryć nie jest zaszumiony.
- **GT-08: digest 3.14.6:**
  - realizm: obraz nieaktualizowany od około trzech miesięcy,
  - wyraźny sygnał: nowe CVE o ważności HIGH i CRITICAL w kilku pakietach, więc wykrycie nie zależy od jednego zgłoszenia.

Kontekst skanu (Trivy 0.76.0, baza podatności z 2026-11-11, linux/amd64; liczby to identyfikatory CVE w pakietach systemowych, których nie ma w wersji czystej): 3.14.9 i 3.14.8 po 1 (HIGH), 3.14.7 18 (3 HIGH), 3.14.6 62 (3 CRITICAL, 18 HIGH), 3.14.5 78 (3 CRITICAL, 19 HIGH). Pierwszy skan obrazu aplikacji pokazał 8 zgłoszeń w pakietach Pythona (5 HIGH, wszystkie z poprawką). Pochodziły z bibliotek dołączonych do pip z obrazu bazowego (`pip/_vendor`: urllib3 2.7.0, msgpack 1.1.2, setuptools 70.3.0), a nie z `uv.lock`, w którym jest urllib3 2.8.0.

Postać Dockerfile (decyzje agenta przy implementacji, zgodne z wymaganiami zadania E05-01 i katalogu):

- pip usuwany w etapie końcowym (`python -m pip uninstall`); bez `apt-get upgrade`, bo zaktualizowałby też starszy digest i zniósł łatkę GT-08,
- trzy etapy: `uv` (tylko źródło pliku binarnego), `build` (środowisko `/opt/venv` z `uv.lock`) i `runtime`; obraz bazowy wpisany raz, w etapie `base`, więc łatka GT-08 zmienia jedną linię,
- `USER 10001:10001` tylko w etapie końcowym (warunek GT-09: Checkov CKV_DOCKER_3 i Trivy DS-0002 patrzą na cały plik),
- kod i środowisko należą do roota i są tylko do odczytu dla użytkownika `app`; aplikacja zapisuje tylko w `/tmp` (katalog podręczny załączników),
- `HEALTHCHECK` przez `python -c` i `urllib` na `/health`, bo obraz slim nie ma `curl`,
- `.dockerignore` jako lista dozwolonych plików (`pyproject.toml`, `uv.lock`, `alembic.ini`, `migrations/`, `ticketing/`), więc `.env`, `.venv` i testy nie trafiają do kontekstu budowania.

## Konsekwencje

- (+) Obraz końcowy nie zawiera uv ani zależności deweloperskich.
- (+) Łatki GT-08 i GT-09 zmieniają po jednym miejscu w Dockerfile. Sprawdzone 2026-11-11 na kopiach Dockerfile (bez commitów łatek): po zmianie digestu Trivy zgłasza 62 nowe CVE, a po usunięciu `USER` Trivy `config` zgłasza DS-0002 (HIGH); wersja czysta ma 0 błędów konfiguracji. Checkov nie był uruchamiany: TODO: zweryfikować w E04-04.
- (−) Obraz slim ma powłokę i menedżer pakietów, więc większą powierzchnię ataku niż distroless. Wersja czysta ma według Trivy (2026-11-11) 204 zgłoszenia w pakietach systemowych (92 identyfikatory CVE; 49 zgłoszeń HIGH, 0 CRITICAL), z czego tylko 3 mają dostępną poprawkę. Zgłoszeń w pakietach Pythona: 0.
- Bramka wariantu B z progiem HIGH zablokuje wersję czystą, jeśli liczy też podatności bez poprawki. Czy bramka ma pomijać podatności bez poprawki (`--ignore-unfixed`) i jak to opisać w `experiment/PROTOCOL.md`: TODO: zweryfikować w E07. Liczba zgłoszeń wersji czystej zmienia się z bazą podatności, więc w eksperymencie trzeba zapisywać datę bazy.
- (−) Korzyść „mniej uprawnień” wymaga osobnego użytkownika bazy dla aplikacji bez prawa DDL. Dziś aplikacja i migracje używają tego samego użytkownika `ticketing` (`compose.yaml`), więc korzyść jest na razie tylko możliwa. Czy rozdzielać użytkowników w AWS (E05-04, E05-07): TODO: zweryfikować.
- Wdrożenie (E05-07) i potok z DAST (E07) muszą uruchamiać migracje jako osobny krok przed startem aplikacji.
- Dwa obrazy do aktualizowania digestem: `python:3.14-slim` i `ghcr.io/astral-sh/uv:0.13.6`.

## Źródła

- Obrazy i digesty: Docker Hub (`library/python`, tag `3.14-slim`) i GitHub Container Registry (`astral-sh/uv`, tag `0.13.6`), sprawdzone 2026-11-11.
- Źródła spoza rejestru `Zrodla/`: TODO: zweryfikować, czy rejestrować.
