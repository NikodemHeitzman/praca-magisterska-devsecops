# 0011. Baza danych testów: PostgreSQL z compose

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0005](0005-baza-danych-postgresql.md), zadanie E04-03, [`docs/app-spec.md`](../app-spec.md) (p. 7, testy), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Testy pytest (jednostkowe i API przez `TestClient`) wchodzą do obu wariantów potoku i muszą dawać pokrycie co najmniej 70%. Aplikacja używa PostgreSQL (0005), a usługa `db` jest już w `app/compose.yaml`. Część kodu zależy od silnika: wyszukiwanie (miejsce GT-01) to surowe zapytanie `text()`, a statusy, priorytety i role to natywne typy enum PostgreSQL w migracji `0001`.

## Czynniki decyzyjne

- zgodność środowiska testów ze środowiskiem docelowym,
- koszt uruchomienia lokalnie i w CI.

## Rozważane opcje

1. PostgreSQL z `app/compose.yaml` (lokalnie), usługa `postgres` w jobie CI
2. SQLite w pamięci
3. Testcontainers (PostgreSQL uruchamiany przez pytest na sesję testów)

## Decyzja

Wybrano **PostgreSQL z compose**, ponieważ testy działają na tym samym silniku co aplikacja w AWS, a usługa `db` już istnieje w `compose.yaml`, więc nie trzeba dodawać kolejnej zależności, jak Testcontainers (powody autora).

## Konsekwencje

- (+) Zapytanie `text()` i typy enum są testowane na silniku docelowym.
- (−) Uruchomienie testów wymaga Dockera i `docker compose up -d db`; w CI job testowy potrzebuje usługi `postgres` (E06/E07).
- (−) Testy są wolniejsze niż na SQLite w pamięci. Izolację między testami trzeba zapewnić w fixtures (np. transakcja wycofywana po teście albo czyszczenie tabel).

## Źródła

- Brak źródeł zewnętrznych. Materiał wewnętrzny: `app/compose.yaml`, `app/migrations/versions/0001_initial_schema.py`.
