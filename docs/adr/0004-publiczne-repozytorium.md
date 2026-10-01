# 0004. Publiczne repozytorium

- **Status:** przyjęty
- **Data:** 2026-10-01
- **Decydujący:** autor pracy
- **Powiązane:** [0001](0001-platforma-ci-cd-github-actions.md), zadania E01-06 i E01-09, [dziennik 2026-10-01](../log/2026-10-01.md)

## Kontekst

Repozytorium projektu powstało na GitHubie w zadaniu E01-06. Potok DevSecOps ma uruchamiać skanery bezpieczeństwa w GitHub Actions, a eksperyment wymaga wielokrotnych przebiegów obu potoków. Liczba minut runnerów i dostępność funkcji bezpieczeństwa GitHuba zależą od widoczności repozytorium. Projekt nie ma budżetu.

## Czynniki decyzyjne

- koszt minut GitHub Actions przy wielu przebiegach eksperymentu,
- dostęp do funkcji bezpieczeństwa GitHuba (code scanning, przesyłanie wyników SARIF),
- odtwarzalność badania dla promotora i recenzenta,
- poufność zawartości repozytorium.

## Rozważane opcje

1. Repozytorium publiczne
2. Repozytorium prywatne na darmowym planie
3. Repozytorium prywatne na płatnym planie

## Decyzja

Wybrano **repozytorium publiczne**, ponieważ daje więcej czasu runnerów na skany i jest tańsze. Dla repozytoriów publicznych minuty standardowych runnerów GitHub Actions i code scanning są bezpłatne, a w repozytoriach prywatnych obowiązują limity lub płatny plan. <!-- TODO: zweryfikować aktualne limity i ceny w dokumentacji GitHuba -->

Autor potwierdził, że w repozytorium nie będzie danych poufnych.

## Konsekwencje

- (+) Brak kosztów minut CI i dostęp do code scanning bez płatnego planu.
- (+) Kod, infrastruktura, potoki i surowe dane eksperymentu są jawne, co ułatwia weryfikację i odtworzenie badania.
- (−) Wszystko, co trafi do repozytorium lub do logów potoku, jest publiczne. Obowiązuje zakaz sekretów, identyfikatorów kont AWS i danych osobowych w repozytorium i dzienniku.
- (−) Uwierzytelnianie do AWS tylko przez OIDC, bez długoterminowych kluczy. Sekrety wyłącznie w GitHub Secrets.
- (−) Publiczne repozytorium może być celem automatycznych skanów i zgłoszeń z zewnątrz. Workflowy uruchamiane z forków trzeba konfigurować ostrożnie. <!-- TODO: zweryfikować zalecenia GitHuba dla pull_request_target -->

## Źródła

- TODO: zweryfikować; dokumentacja GitHuba o rozliczaniu GitHub Actions i dostępności code scanning dla repozytoriów publicznych i prywatnych; dodać do rejestru źródeł.
