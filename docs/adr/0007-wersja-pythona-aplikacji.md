# 0007. Wersja Pythona aplikacji: 3.14

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0008](0008-menedzer-zaleznosci-uv.md), zadania E04-02 i E03-07, [`docs/app-spec.md`](../app-spec.md) (p. 7), `experiment/ground-truth.yaml` (GT-07, GT-08), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Pozycja GT-08 w katalogu zakłada, że łatka zmienia tylko instrukcję `FROM` na `python:3.9-slim-bullseye`, więc kod i zależności wersji czystej muszą działać na Pythonie 3.9 (`app-spec.md`, p. 7). Sprawdzenie w PyPI 2026-10-30 pokazało, że większość stosu nie wspiera już Pythona 3.9 w najnowszych wersjach: fastapi od 0.129.0, starlette od 0.50.0, pydantic od 2.14.0, pydantic-settings od 2.12.0, sqlalchemy od 2.1.0, alembic od 1.17.0, psycopg od 3.3.0, uvicorn od 0.40.0, python-multipart od 0.0.21. Zapytanie do OSV dla ostatnich wersji zgodnych z 3.9 zwróciło 15 różnych CVE spoza katalogu (starlette 5, python-multipart 7, anyio 2, python-dotenv 1, pytest 1). We wszystkich przypadkach poprawka jest w wersji, która wymaga Pythona co najmniej 3.10. Dla najnowszych wersji tych samych pakietów OSV nie zwrócił żadnej podatności.

## Czynniki decyzyjne

- realizm aplikacji badawczej,
- dojrzałość wersji Pythona,
- sprawdzona zgodność stosu,
- okres wsparcia wersji w czasie pracy.

## Rozważane opcje

1. Python 3.9 z lockfile'em dobranym pod 3.9 (GT-08 bez zmian)
2. Python 3.14 z aktualnymi zależnościami
3. Python 3.15 z aktualnymi zależnościami

## Decyzja

Wybrano **Pythona 3.14**.

- Przeciw opcji 1: realizm. Nowa aplikacja w 2026 roku nie powstaje na Pythonie po końcu wsparcia.
- Przeciw opcji 3, z trzech powodów:
  - dojrzałość: Python 3.14 ma za sobą rok poprawek, a 3.15 wydano trzy tygodnie przed decyzją;
  - zgodność: stos aplikacji sprawdzono na 3.14;
  - wsparcie: 3.14 jest wspierany do 2030-10, czyli przez cały czas trwania pracy i eksperymentu.

Sprawdzenie zgodności (2026-10-30, Windows, Python 3.14.8): najnowsze fastapi, starlette, pydantic, sqlalchemy, psycopg, argon2-cffi, pyjwt, boto3 i python-multipart oraz jinja2 3.1.2 (wersja z łatki GT-07). W teście działały: render szablonu Jinja2 z autoescape i `url_for`, upload pliku, skrót Argon2 i token JWT. Paczki binarne pakietów z kodem natywnym są na PyPI dla 3.14 na `manylinux` x86_64.

## Konsekwencje

- (+) Lockfile wersji czystej nie ma znanych podatności według OSV na dzień decyzji. Nowe CVE mogą się pojawić w trakcie eksperymentu, bo wersje są zamrożone; datę bazy podatności skanera trzeba więc zapisywać przy każdej próbie (TODO: zweryfikować, czy `PROTOCOL.md` już to wymaga).
- (−) GT-08 w obecnej postaci nie zadziała: obraz z Pythonem 3.9 nie zainstaluje zależności wersji czystej. Decyzja autora z 2026-10-30: GT-08 przechodzi na zamiennik, który katalog już przewiduje, czyli starszy digest tego samego obrazu, z którego korzysta wersja czysta. Opis GT-08 w `experiment/ground-truth.yaml` trzeba zmienić przed zamrożeniem katalogu v1 (E03-07).
- (−) GT-08 przestaje dotyczyć interpretera po końcu wsparcia. Zostają przestarzałe pakiety systemowe obrazu bazowego.
- Kod może używać składni Pythona 3.10+ (np. `X | None`). Ograniczenie z `app-spec.md`, p. 7 („bez `match` i unii `X | Y`”) przestaje obowiązywać.
- Obraz bazowy wersji czystej: `python:3.14-slim` przypięty digestem (E05-01).

## Źródła

Źródła spoza rejestru (TODO: zweryfikować, czy zarejestrować w `Zrodla/`), sprawdzone 2026-10-30:

- PyPI JSON API (`https://pypi.org/pypi/<pakiet>/json`), pole `requires_python` poszczególnych wydań,
- OSV (`https://api.osv.dev/v1/querybatch`),
- daty wydań Pythona 3.14.0 (2025-10-07) i 3.15.0 (2026-10-09): `https://www.python.org/api/v2/downloads/release/`,
- koniec wsparcia: `https://endoflife.date/api/python.json` (3.9: 2025-10-31, 3.14: 2030-10-31). Przed cytowaniem w pracy zweryfikować w PEP 745 (harmonogram 3.14): TODO: zweryfikować.
