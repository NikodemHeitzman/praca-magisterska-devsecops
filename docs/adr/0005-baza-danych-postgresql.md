# 0005. Baza danych aplikacji: PostgreSQL

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0002](0002-konteneryzacja-docker.md), [0006](0006-przechowywanie-zalacznikow-s3.md), zadanie E04-01, [`docs/app-spec.md`](../app-spec.md), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Aplikacja badawcza (system zgłoszeń, `docs/app-spec.md`) przechowuje użytkowników, zgłoszenia i metadane załączników. Pozycja GT-01 z katalogu wymaga zapytania SQL, które łatka zamienia na składane f-stringiem. Potrzebny jest silnik bazy, który działa lokalnie, w potoku (skan DAST na aplikacji uruchomionej z `compose.yaml`) i w AWS.

## Czynniki decyzyjne

- realizm wdrożenia: podobieństwo do typowej aplikacji webowej w chmurze,
- prostota i koszt środowiska,
- jednakowe środowisko lokalnie, w CI i w AWS (kontrola zmiennych w eksperymencie).

## Rozważane opcje

1. PostgreSQL jako osobny kontener w `compose.yaml`
2. SQLite (plik bazy w wolumenie, jeden kontener)
3. SQLite lokalnie, PostgreSQL w AWS (przełączanie przez `DATABASE_URL`)

## Decyzja

Wybrano **PostgreSQL**, ponieważ aplikacje webowe wdrażane w chmurze zwykle korzystają z serwera bazy danych, a SQLite rzadko pracuje na produkcji. Realizm wdrożenia autor przedłożył nad prostotę jednego kontenera.

Opcję 3 odrzucono, bo różne silniki lokalnie i w AWS osłabiają kontrolę zmiennych.

Ten ADR dotyczy tylko silnika. Czy w AWS PostgreSQL działa jako kontener, czy jako usługa zarządzana (RDS), rozstrzyga E05 (decyzja autora z 2026-10-30).

## Konsekwencje

- (+) Ten sam silnik lokalnie, w potoku i w AWS.
- (−) Dwa kontenery zamiast jednego: lokalnie i w CI trzeba uruchamiać bazę razem z aplikacją (`compose.yaml`, E05-02), a potok czeka na jej gotowość przed testami i skanem DAST.
- (−) Obraz PostgreSQL to kolejny obraz bazowy z własnymi podatnościami; jego wersję trzeba przypiąć. Czy skaner obrazów w potoku obejmuje także ten obraz: TODO: zweryfikować w E07.
- Częściowo rozstrzyga podział na obrazy odłożony w [0002](0002-konteneryzacja-docker.md): aplikacja i baza to osobne komponenty uruchomieniowe, a nie mikroserwisy.
- Wymaga decyzji w E05: kontener czy RDS w AWS.

## Źródła

- Brak źródeł zewnętrznych; decyzja opiera się na ocenie autora.
