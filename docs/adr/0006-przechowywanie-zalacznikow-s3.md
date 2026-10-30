# 0006. Przechowywanie załączników: S3 z lokalnym katalogiem podręcznym

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0005](0005-baza-danych-postgresql.md), zadanie E04-01, [`docs/app-spec.md`](../app-spec.md), `experiment/ground-truth.yaml` (GT-05, GT-11), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Użytkownicy dodają do zgłoszeń załączniki. Pozycja GT-05 z katalogu to path traversal przy pobieraniu pliku: ścieżka składana z nazwy podanej przez użytkownika bez normalizacji i sprawdzenia katalogu. Jej oczekiwanym detektorem jest Semgrep z analizą przepływu danych do operacji na plikach. Katalog ma zostać zamrożony jako v1 (E03-07), więc miejsce na pliki nie powinno zmieniać opisu pozycji.

## Czynniki decyzyjne

- zgodność ze wzorcem typowym dla aplikacji w chmurze,
- zgodność z opisem GT-05 w katalogu bez jego zmiany,
- prostota.

## Rozważane opcje

1. Dysk kontenera albo wolumen (lokalnie wolumen, w AWS dysk EBS)
2. Tylko S3 (pobieranie obiektu bezpośrednio po kluczu)
3. S3 jako magazyn, pobieranie przez lokalny katalog podręczny na dysku kontenera
4. S3 dla załączników i osobna funkcja na plikach lokalnych tylko dla GT-05
5. S3 i zmiana opisu GT-05 na path traversal w kluczu S3

## Decyzja

Wybrano **opcję 3**, ponieważ S3 to typowy wzorzec chmurowy: kontener aplikacji jest bezstanowy, a pliki trzyma usługa zarządzana. Pobieranie przez lokalny katalog podręczny zostawia GT-05 w postaci opisanej w katalogu (operacja na ścieżce w systemie plików).

Odrzucone:

- opcja 2: path traversal w kluczu S3 to inna postać błędu, a reguły SAST dla ścieżek plików by jej nie objęły, więc trzeba by zmienić GT-05,
- opcja 4: dwa mechanizmy przechowywania w małej aplikacji,
- opcja 5: zmiana pozycji katalogu tuż przed zamrożeniem v1,
- opcja 1: brak wzorca chmurowego.

## Konsekwencje

- (+) Kontener aplikacji nie przechowuje danych trwale; dane są w bazie (0005) i w S3.
- (+) Kubełek S3 to naturalny zasób IaC dla GT-11 (nieszyfrowany magazyn). Czy szyfrowanie kubełka da się wyłączyć: TODO: zweryfikować w E05; katalog dopuszcza zamiast tego wolumen EBS.
- (−) Lokalnie i w CI potrzebna jest usługa zgodna z S3 (np. MinIO w `compose.yaml`), bo skan DAST uruchamia aplikację bez AWS. TODO: zweryfikować wybór w E04-02/E05.
- (−) Aplikacja w AWS potrzebuje uprawnień IAM do kubełka (rola, bez kluczy dostępowych), co poszerza infrastrukturę w E05.
- Katalog podręczny jest ulotny; przy restarcie kontenera pliki są ponownie pobierane z S3.

## Źródła

- Brak źródeł zewnętrznych; decyzja opiera się na ocenie autora.
