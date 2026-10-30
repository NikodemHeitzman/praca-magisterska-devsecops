# Aplikacja badawcza: system zgłoszeń

Specyfikacja: [`docs/app-spec.md`](../docs/app-spec.md). Decyzje: ADR-0005…0013 w [`docs/adr/`](../docs/adr/).

## Stos

- Python 3.14, FastAPI, Pydantic, SQLAlchemy 2, Alembic, Jinja2,
- PostgreSQL i moto (atrapa S3) w [`compose.yaml`](compose.yaml),
- zależności: uv 0.13.6, `uv.lock`, eksport [`requirements.txt`](requirements.txt) z sumami kontrolnymi dla pip-audit.

## Uruchomienie lokalne

Wymagane: uv 0.13.6 i Docker. Polecenia uruchamiaj w katalogu `app/`.

1. Skopiuj `.env.example` do `.env` i uzupełnij `POSTGRES_PASSWORD` (to samo hasło w `DATABASE_URL`), `JWT_SECRET` oraz hasła kont startowych `SEED_*_PASSWORD`.
2. Uruchom bazę i atrapę S3: `docker compose up -d`.
3. Zainstaluj zależności: `uv sync --frozen`.
4. Utwórz schemat bazy: `uv run --env-file .env alembic upgrade head`.
5. Wgraj dane startowe (konta `alice`, `bob`, `admin`, zgłoszenia, załącznik; kubełek w moto): `uv run --env-file .env python -m ticketing.seed`. Skrypt można uruchamiać wielokrotnie; po restarcie kontenera `s3` trzeba go powtórzyć, bo moto trzyma dane w pamięci.
6. Uruchom aplikację: `uv run --env-file .env uvicorn ticketing.main:app --reload`.

Aplikacja działa pod http://localhost:8000. Dokumentacja API jest pod `/docs`, a stan aplikacji i bazy pod `/health`.

`--env-file` jest potrzebne, bo boto3 czyta `AWS_*` ze zmiennych środowiskowych procesu, a nie z pliku `.env`.

## Testy

Wymagane: uruchomiona baza z compose (`docker compose up -d db`).

```
uv run pytest
```

- Testy działają na PostgreSQL ([ADR-0011](../docs/adr/0011-baza-danych-testow-postgresql.md)) w osobnej bazie: `TEST_DATABASE_URL` albo `DATABASE_URL` z `.env` z przyrostkiem `_test` w nazwie bazy. Baza jest usuwana i tworzona od nowa na początku każdego przebiegu, a schemat buduje migracja Alembic. Nazwa bazy musi kończyć się na `_test`.
- S3 zastępuje moto w procesie (`mock_aws`), osobno dla każdego testu ([ADR-0012](../docs/adr/0012-s3-w-testach-moto-w-procesie.md)). Kontener `s3` z compose nie jest potrzebny.
- Klient testowy to `TestClient` z httpx2 ([ADR-0013](../docs/adr/0013-klient-http-testow-httpx2.md)). Ostrzeżenia są traktowane jak błędy (`filterwarnings = ["error"]`).
- Raport pokrycia wyświetla się po testach. Przebieg kończy się błędem, gdy pokrycie spadnie poniżej 70%.

## Zmiana zależności

Po każdej zmianie w `pyproject.toml`:

```
uv lock
uv export --format requirements-txt --no-dev --frozen -o requirements.txt
```

Oba pliki trafiają do tego samego commita. Łatka GT-07 zmienia `jinja2` w `pyproject.toml`, `uv.lock` i `requirements.txt` naraz.

## Struktura

- `ticketing/main.py`: aplikacja, CORS, nagłówki bezpieczeństwa,
- `ticketing/config.py`: ustawienia ze zmiennych środowiskowych,
- `ticketing/db.py`, `ticketing/models.py`: baza i modele,
- `ticketing/routers/`: endpointy (`auth`, `users`, `tickets`, `attachments`, `admin`, `health`, strony HTML),
- `ticketing/schemas.py`: modele żądań i odpowiedzi,
- `ticketing/security.py`: skróty haseł (Argon2), tokeny JWT, zależności `get_current_user` i `require_admin`,
- `ticketing/storage.py`: obiekty załączników w S3,
- `ticketing/seed.py`: dane startowe (`docs/app-spec.md`, p. 6),
- `ticketing/templates/`: szablony Jinja2,
- `ticketing/static/`: arkusz stylów stron HTML, podawany pod `/static` (plik z tej samej domeny, więc zgodny z CSP `default-src 'self'`),
- `migrations/`: migracje Alembic,
- `tests/`: testy pytest i fixtures (`conftest.py`). Testy sprawdzają działanie, a nie właściwości zmieniane przez łatki katalogu, bo każda łatka musi je przechodzić (`experiment/PROTOCOL.md`).
