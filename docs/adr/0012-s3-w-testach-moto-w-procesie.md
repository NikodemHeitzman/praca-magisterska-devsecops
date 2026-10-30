# 0012. S3 w testach: moto w procesie (`mock_aws`)

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0006](0006-przechowywanie-zalacznikow-s3.md), [0009](0009-lokalna-usluga-s3-moto.md), zadanie E04-03, [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Upload, pobieranie i usuwanie załączników korzystają z S3 przez boto3 (0006). Testy muszą działać bez AWS. Lokalnie aplikacja łączy się z kontenerem moto z `compose.yaml` przez `S3_ENDPOINT_URL` (0009). Pakiet moto ma też tryb w procesie: dekorator lub menedżer kontekstu `mock_aws` przechwytuje wywołania boto3 bez sieci.

## Czynniki decyzyjne

- izolacja testów,
- prostota konfiguracji joba testowego w CI.

## Rozważane opcje

1. moto w procesie (`mock_aws`), pakiet `moto` w zależnościach deweloperskich
2. usługa moto z `compose.yaml` przez `S3_ENDPOINT_URL`

## Decyzja

Wybrano **moto w procesie**, ponieważ każdy test dostaje czysty S3 bez stanu dzielonego z innymi testami, a job testowy w CI nie potrzebuje dodatkowej usługi (powody autora).

## Konsekwencje

- (+) Fixture tworzy kubełek w `mock_aws` na czas jednego testu; nie trzeba sprzątać kubełka.
- (−) Testy nie sprawdzają połączenia z usługą przez `S3_ENDPOINT_URL`. Sprawdza je test dymny na `compose.yaml` (E04-03) i skan DAST (E07).
- (−) Pakiet `moto[s3]` jest zależnością deweloperską w `uv.lock` i dokłada do niego pakiety pośrednie (m.in. `cryptography`, `werkzeug`, `requests`). Eksport `requirements.txt` dla pip-audit pomija grupę dev (`--no-dev`). Czy Trivy, czytając `uv.lock`, zgłasza też zależności deweloperskie: TODO: zweryfikować w E07.
- W E04-02 instalacja moto nie powiodła się w środowisku o bardzo długiej ścieżce na Windows (limit długości ścieżek). W `app/.venv` instaluje się bez problemu (sprawdzone 2026-10-30).

## Źródła

- Repozytorium moto: https://github.com/getmoto/moto (wydanie 5.2.5 na PyPI, sprawdzone 2026-10-30).
- Źródła spoza rejestru `Zrodla/`: TODO: zweryfikować, czy rejestrować.
