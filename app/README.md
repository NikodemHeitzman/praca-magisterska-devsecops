# Aplikacja badawcza: system zgłoszeń

Specyfikacja: [`docs/app-spec.md`](../docs/app-spec.md). Decyzje: ADR-0005…0010 w [`docs/adr/`](../docs/adr/).

## Stos

- Python 3.14, FastAPI, Pydantic, SQLAlchemy 2, Alembic, Jinja2,
- PostgreSQL i moto (atrapa S3) w [`compose.yaml`](compose.yaml),
- zależności: uv 0.13.6, `uv.lock`, eksport [`requirements.txt`](requirements.txt) z sumami kontrolnymi dla pip-audit.

## Uruchomienie lokalne

Wymagane: uv 0.13.6 i Docker. Polecenia uruchamiaj w katalogu `app/`.

1. Skopiuj `.env.example` do `.env` i uzupełnij `POSTGRES_PASSWORD` (to samo hasło w `DATABASE_URL`) oraz `JWT_SECRET`.
2. Uruchom bazę i atrapę S3: `docker compose up -d`.
3. Zainstaluj zależności: `uv sync --frozen`.
4. Utwórz schemat bazy: `uv run --env-file .env alembic upgrade head`.
5. Uruchom aplikację: `uv run --env-file .env uvicorn ticketing.main:app --reload`.

Aplikacja działa pod http://localhost:8000. Dokumentacja API jest pod `/docs`, a stan aplikacji i bazy pod `/health`.

`--env-file` jest potrzebne, bo boto3 czyta `AWS_*` ze zmiennych środowiskowych procesu, a nie z pliku `.env`.

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
- `ticketing/routers/`: endpointy (`health`, strony HTML; API: E04-03),
- `ticketing/templates/`: szablony Jinja2,
- `migrations/`: migracje Alembic.
