# 0023. Uruchamianie aplikacji z zależnościami: Docker Compose z jednorazowymi usługami migrate i seed, `.env` w CI generowany przez workflow

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0002](0002-konteneryzacja-docker.md), [0005](0005-baza-danych-postgresql.md), [0009](0009-lokalna-usluga-s3-moto.md), [0022](0022-obraz-kontenera-aplikacji.md), zadanie E05-02, `app/compose.yaml`, `app/scripts/ci-env.sh`, [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Aplikacja działa w trzech kontenerach: aplikacja (ADR-0022), PostgreSQL (ADR-0005) i moto jako atrapa S3 (ADR-0009). ADR-0002 zapowiedział osobną decyzję o tym, jak je łączyć i uruchamiać razem. Ten sam stos ma działać lokalnie i w potoku, gdzie skan DAST (E07) potrzebuje aplikacji z danymi startowymi. Do tej pory `app/compose.yaml` uruchamiał kontenery, ale migracje i dane startowe były osobnymi poleceniami (`docker compose run --rm app …`, ADR-0022), a compose wymagał pliku `app/.env`, którego w CI nie ma, bo nie trafia do repozytorium.

## Czynniki decyzyjne

- jeden opis środowiska dla komputera autora i potoku,
- prostota i deklaratywny opis zależności między kontenerami,
- skala projektu: trzy kontenery na jednej maszynie,
- brak sekretów w publicznym repozytorium (AGENTS.md, zasada 4),
- liczba kroków potrzebnych do gotowej aplikacji.

## Rozważane opcje

Sposób uruchamiania kontenerów:

1. Docker Compose (`app/compose.yaml`)
2. kontenery usług GitHub Actions (`services:` w jobie)
3. Kubernetes lokalnie (kind albo minikube)

Migracje i dane startowe:

1. jednorazowe usługi `migrate` i `seed` w compose, uruchamiane przez `docker compose up`
2. tylko migracje jako usługa w compose, dane startowe osobnym poleceniem
3. bez zmian: oba kroki osobnymi poleceniami (`docker compose run --rm app …`)

Zmienne środowiskowe w CI:

1. workflow tworzy `app/.env` z `.env.example` przed `docker compose up`
2. nakładka `compose.ci.yaml` z jawnymi wartościami testowymi w repozytorium
3. `.env` opcjonalny i wartości domyślne w `compose.yaml`, nadpisywane zmiennymi środowiska

Źródło wartości w `.env` w CI:

1. losowe przy każdym przebiegu, generowane w jobie
2. stałe wartości w GitHub Secrets

## Decyzja

Wybrano **Docker Compose z jednorazowymi usługami `migrate` i `seed` oraz `.env` tworzony w CI przez workflow z losowymi wartościami**. Powody autora:

- **Docker Compose:**
  - jedno źródło lokalnie i w CI: ten sam plik uruchamia stos na komputerze autora i w potoku przed skanem DAST,
  - deklaratywność i prostota: kolejność startu, healthchecki, sieć i wolumeny są opisane w jednym pliku YAML,
  - skala projektu: trzy kontenery na jednej maszynie, a orkiestrator jest poza zakresem pracy.
- **Odrzucone:**
  - `services:` w GitHub Actions działa tylko w CI, więc lokalnie trzeba by opisać środowisko drugi raz,
  - Kubernetes (kind, minikube) jest poza zakresem pracy (AGENTS.md) i nadmiarowy przy trzech kontenerach.
- **Jednorazowe usługi `migrate` i `seed`:** jedno polecenie do gotowej aplikacji. `docker compose up` daje aplikację z danymi bez pamiętania kolejności kroków.
- **`.env` tworzony przez workflow:** żadnych sekretów w repozytorium, także testowych haseł i klucza JWT.
- **Wartości losowe przy każdym przebiegu:** wybór autora. Powód: TODO: zweryfikować z autorem.

Decyzja nie zmienia ADR-0022: migracje nadal nie należą do obrazu ani do procesu aplikacji. Zmienia się tylko sposób ich wywołania lokalnie i w CI, z ręcznego `docker compose run` na usługę w compose.

Postać `compose.yaml` i skryptu (decyzje agenta przy implementacji):

- usługi `app`, `migrate` i `seed` dzielą jeden fragment konfiguracji (`x-ticketing`): obraz `ticketing:local`, `build`, `env_file` i adresy bazy oraz S3 dla kontenera. Każda z nich ma `build`, więc `up --build` nie próbuje pobierać `ticketing:local` z rejestru,
- kolejność startu: `db` (healthcheck `pg_isready`) → `migrate` → `seed` (czeka też na zdrowy `s3`) → `app`. Warunki to `service_healthy` i `service_completed_successfully`, a `migrate` i `seed` mają `restart: "no"`,
- nowy healthcheck usługi `s3`: `curl` na `/moto-api/` (obraz moto ma `curl`), żeby `seed` nie tworzył kubełka przed startem moto,
- `seed` działa przy każdym `up`. Skrypt jest idempotentny (`ticketing/seed.py`), więc odtwarza też kubełek i załącznik, które moto traci po restarcie,
- `app/scripts/ci-env.sh` tworzy `app/.env` z `.env.example`:
  - wartości z `openssl rand -hex`,
  - w GitHub Actions maskuje je w logu (`::add-mask::`),
  - nie nadpisuje istniejącego `.env`,
  - kończy się błędem, gdy któryś sekret zostałby pusty.

## Konsekwencje

- (+) `docker compose up -d --build` od pustej bazy daje działającą aplikację z kontami `alice`, `bob`, `admin`, zgłoszeniami i załącznikiem. Lokalnie zajęło to 15,3 s (2026-11-11, Docker 29.9.2, Compose 5.6.1, warstwy obrazu w pamięci podręcznej budowania). `docker compose up -d --wait` kończy się kodem 0, gdy `app` jest zdrowa, co nada się do kroku potoku przed skanem DAST.
- (+) Bez `app/.env` compose kończy się czytelnym błędem (`required variable POSTGRES_PASSWORD is missing a value`), a nie startem z przewidywalnym sekretem.
- (+) Każdy przebieg CI ma inne hasła i klucz JWT. Skaner sekretów nie ma w repozytorium testowych wartości do zgłoszenia.
- (−) Hasła kont startowych są znane tylko w jobie. Skan DAST (E07) musi je czytać z wygenerowanego `app/.env` w tym samym jobie.
- (−) `seed` przy każdym `up` ustawia hasła kont startowych na wartości z `.env`. Lokalnie to zamierzone. Czy compose z `seed` będzie też wdrożeniem na EC2 (E05-03, E05-07), czy w AWS konta startowe mają powstawać inaczej: TODO: zweryfikować.
- (−) `docker compose ps -a` pokazuje zakończone kontenery `migrate` i `seed`. To stan oczekiwany, nie błąd.
- Bez zmian zostaje uwaga z ADR-0022: `migrate` używa tego samego użytkownika bazy co aplikacja.
- Workflow E06 i E07: przed `docker compose up` krok `sh scripts/ci-env.sh` w katalogu `app/`.

## Źródła

- Dokumentacja Docker Compose (`depends_on`, `condition: service_completed_successfully`, `--wait`, fragmenty `x-`): źródło spoza rejestru `Zrodla/`, TODO: zweryfikować, czy rejestrować.
- Rozdział o Docker Compose i pliku `.env` w notatkach z książek (`docs/notes/ksiazki.md`): do ewentualnego cytowania w 4.2, TODO: zweryfikować.
