# AGENTS.md: kontekst dla asystentów AI

Ten plik opisuje projekt dla asystentów AI (Claude Code, Copilot, Codex i innych). `CLAUDE.md` wskazuje na ten plik.

## Projekt

- **Tytuł pracy:** Projekt i ewaluacja lekkiego potoku DevSecOps dla aplikacji webowej w chmurze AWS z wykorzystaniem GitHub Actions, Dockera i skanerów bezpieczeństwa zgodnego z wytycznymi OWASP i NIST SP 800-204D
- **Rodzaj:** praca magisterska; studium przypadku i eksperyment porównawczy (potok bazowy kontra potok DevSecOps).
- **Cel repozytorium:** odtwarzalna część praktyczna, czyli aplikacja, infrastruktura, potoki CI/CD, eksperyment i dokumentacja decyzji.
- **Poza zakresem:** Kubernetes, IAST, architektura mikroserwisowa.

## Struktura

- `app/`: aplikacja webowa i `Dockerfile`
- `infra/terraform/`: infrastruktura AWS (region domyślny: TODO, np. `eu-central-1`)
- `infra/ansible/`: konfiguracja i wdrożenie
- `.github/workflows/`: potok bazowy i potok DevSecOps
- `experiment/`: skrypty pomiarowe, surowe dane (`experiment/data/`), analiza
- `docs/adr/`: decyzje architektoniczne, `NNNN-tytul.md`
- `docs/meetings/`: notatki ze spotkań, `RRRR-MM-DD-promotor.md`
- `docs/log/`: dziennik badawczy, `RRRR-MM-DD.md` (zasady w `docs/log/README.md`)

## Konwencje

1. **Język:** dokumentacja i ADR po polsku; kod, identyfikatory, nazwy jobów i komunikaty commitów po angielsku.
2. **Commity:** Conventional Commits (`feat:`, `fix:`, `ci:`, `infra:`, `docs:`, `exp:`, `chore:`).
3. **Decyzje:** każdy wybór techniczny (narzędzie, usługa AWS, sposób wdrożenia) dostaje ADR w `docs/adr/`: kontekst, rozważane opcje, decyzja, konsekwencje.
4. **Sekrety:** nigdy w repozytorium. Sekrety trzymamy w GitHub Secrets, a do AWS uwierzytelniamy się przez OIDC, bez długoterminowych kluczy. Repozytorium jest publiczne.
5. **Akcje GitHub** przypinamy do pełnego SHA commita (wymóg łańcucha dostaw, NIST SP 800-204D).
6. **Odtwarzalność:** wersje narzędzi i obrazów bazowych przypięte; wyniki eksperymentu zapisujemy jako surowe dane, nie tylko wykresy.
7. **Nie wymyślaj** wyników pomiarów, numerów CVE, źródeł ani cytatów. Czego nie wiadomo, oznacz `TODO: zweryfikować`.
8. **Dziennik badawczy:** na koniec każdej sesji pracy dopisz wpis do `docs/log/RRRR-MM-DD.md` według `docs/log/_szablon.md`: autor (nazwa narzędzia), czas, co zrobiono, decyzje, problemy, następne kroki. Czasu, którego nie znasz, nie szacuj, tylko wpisz `TODO: zweryfikować`.

## Powiązane miejsca

- Planowanie zadań i statusy: tablica zadań na claude.ai oraz vault Obsidiana `Magisterka-Vault` (kontrakt w jego `CLAUDE.md`, notatki zadań w `Zadania/`).
- Tekst pracy jest pisany poza repozytorium (Claude Docs). Repozytorium dostarcza do niego materiał: ADR-y, dane, opisy potoków.
