# Rejestr decyzji architektonicznych (ADR)

ADR (*Architecture Decision Record*) to krótki zapis jednej decyzji technicznej: jaki był problem, jakie opcje rozważono, co wybrano i z jakimi konsekwencjami. Rejestr zachowuje uzasadnienie wyborów, nie tylko ich wynik. Jest źródłem materiału do rozdziału 4 (projekt i realizacja potoku) i do podrozdziału 5.3 (ograniczenia).

## Zasady

1. **Jedna decyzja na plik.** Jeśli w jednym ADR pojawia się „i”, na przykład „GitHub Actions i AWS”, zwykle są to dwie decyzje.
2. **Nazwa pliku:** `NNNN-krotki-tytul.md`, gdzie numer jest czterocyfrowy i nadawany kolejno (`0001`, `0002`, …). Tytuł pisz małymi literami, bez polskich znaków, z myślnikami.
3. **Kopiuj [`_szablon.md`](_szablon.md).** Sekcje: kontekst, czynniki decyzyjne, rozważane opcje, decyzja, konsekwencje.
4. **Statusy:** `proponowany` → `przyjęty`; później ewentualnie `zastąpiony przez NNNN` albo `wycofany`.
5. **Nie edytuj treści przyjętego ADR.** Gdy decyzja się zmienia, napisz nowy ADR, a w starym zmień tylko status na `zastąpiony przez NNNN`. Historia zmian zdania jest materiałem do pracy.
6. **Uzasadnienia muszą być prawdziwe.** Nie dopisuj powodów, których nie było, ani źródeł z pamięci. Czego nie wiadomo, oznacz `TODO: zweryfikować`. Źródła cytuj kluczem z rejestru źródeł (`[@KLUCZ]`).
7. **Wpis w dzienniku** ([`../log/`](../log/)) z dnia decyzji zawiera link do ADR.

## Indeks

| Nr | Decyzja | Status | Data |
|---|---|---|---|
| [0001](0001-platforma-ci-cd-github-actions.md) | Platforma CI/CD: GitHub Actions | przyjęty | 2026-10-01 |
| [0002](0002-konteneryzacja-docker.md) | Konteneryzacja aplikacji: Docker | przyjęty | 2026-10-01 |
| [0003](0003-dostawca-chmury-aws.md) | Dostawca chmury: AWS | przyjęty | 2026-10-01 |
| [0004](0004-publiczne-repozytorium.md) | Publiczne repozytorium | przyjęty | 2026-10-01 |
