# 0009. Usługa zgodna z S3 lokalnie i w CI: moto

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0006](0006-przechowywanie-zalacznikow-s3.md), zadania E04-02, E04-03, E05, [`docs/app-spec.md`](../app-spec.md) (p. 7, `S3_ENDPOINT_URL`), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Załączniki są przechowywane w S3 (0006). Lokalnie i w CI, w tym przy skanie DAST na `compose.yaml`, aplikacja działa bez AWS, więc potrzebuje usługi zgodnej z API S3. W AWS aplikacja korzysta z prawdziwego S3. Najczęściej używany zamiennik, MinIO, ma od 2026 zarchiwizowane repozytorium z informacją, że nie jest już utrzymywane. Repozytorium LocalStack na GitHubie też jest zarchiwizowane (oba sprawdzone 2026-10-30).

## Czynniki decyzyjne

- prostota uruchomienia i konfiguracji,
- aktywne utrzymanie projektu,
- licencja zgodna z publicznym repozytorium.

## Rozważane opcje

1. moto w trybie serwera (atrapa API AWS, Apache-2.0)
2. RustFS (magazyn obiektów zgodny z S3, Apache-2.0)
3. SeaweedFS (rozproszony magazyn z bramką S3, Apache-2.0)

MinIO i LocalStack odrzucono na starcie, bo ich repozytoria są zarchiwizowane.

## Decyzja

Wybrano **moto**, ponieważ jest najprostszy: jeden lekki kontener bez konfiguracji. Lokalny S3 jest tylko zastępstwem prawdziwego S3 z AWS (powód autora).

## Konsekwencje

- (+) Jeden kontener w `compose.yaml` (obraz `motoserver/moto`, przypięty digestem; na dzień decyzji wersja 5.2.5 z 2026-10-27).
- (−) moto trzyma dane w pamięci, więc po restarcie kontenera załączniki znikają. Skrypt danych startowych tworzy kubełek i wgrywa załączniki przy każdym uruchomieniu.
- (−) moto to atrapa, a nie magazyn. Zachowanie może się różnić od prawdziwego S3 (TODO: zweryfikować w E05 na S3 w AWS). Różnice nie dotyczą pozycji katalogu, bo GT-05 działa na lokalnym katalogu podręcznym (0006).
- Aplikacja przyjmuje opcjonalny `S3_ENDPOINT_URL`. W AWS zmienna jest pusta i boto3 łączy się z prawdziwym S3.

## Źródła

- Repozytoria: https://github.com/minio/minio (zarchiwizowane), https://github.com/localstack/localstack (zarchiwizowane), https://github.com/getmoto/moto (wydanie 5.2.5), sprawdzone 2026-10-30 przez API GitHuba.
- Źródła spoza rejestru `Zrodla/`: TODO: zweryfikować, czy rejestrować.
