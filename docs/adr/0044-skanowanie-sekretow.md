# 0044. Skanowanie sekretów: Gitleaks na commitach PR i pushu, domyślne reguły, wspólny plik bramek, hook pre-commit

- **Status:** przyjęty
- **Data:** 2026-11-24
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0042](0042-projekt-potoku-wariantu-b.md) (kroki B01, B03, B07; D5, D6, D9, D10, D13), [0043](0043-utwardzenie-workflowow.md) (H3, H6, H8), [`docs/projekt-potoku.md`](../projekt-potoku.md), [`docs/narzedzia.md`](../narzedzia.md) (GT-02, p. 4.1), [`.github/workflows/devsecops-gates.yml`](../../.github/workflows/devsecops-gates.yml), [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml), [`infra/github/settings.sh`](../../infra/github/settings.sh), zadanie E07-03, `experiment/ground-truth.yaml` (GT-02), `experiment/PROTOCOL.md` (P3, 2.3), [dziennik 2026-11-24](../log/2026-11-24.md)

## Kontekst

ADR-0042 przewidział trzy kontrole sekretów: doradczy hook pre-commit (B01), secret scanning z push protection na platformie (B03) i blokujący job `secrets` z Gitleaksem na PR i pushu (B07). Gitleaks nie ma poziomów ważności, więc blokuje każde zgłoszenie (ADR-0042). Narzędzie działa z oficjalnego obrazu przypiętego digestem (D9). Pozycja katalogu, której dotyczy kontrola, to GT-02: zakodowany klucz JWT w postaci `JWT_SECRET = "<losowa wartość>"`, wykrywalny regułą `generic-api-key` (decyzja autora z 2026-10-20, `docs/narzedzia.md`, p. 4.1).

Stan przed zadaniem (2026-11-24):

- secret scanning i push protection włączone (E07-02), wzorce spoza dostawców (*non-provider patterns*) wyłączone,
- brak joba `secrets`, brak hooka pre-commit,
- Gitleaks 8.30.1 (2026-03-21) to najnowsze wydanie; obraz `ghcr.io/gitleaks/gitleaks:v8.30.1` ma ten sam digest na GHCR i Docker Hub (`sha256:c00b6bd0…bbb7f`, sprawdzone 2026-11-24),
- kody wyjścia Gitleaks 8.30.1: `0` brak wycieków, `1` wyciek albo błąd, `126` nieznana flaga (README v8.30.1, sekcja „Exit Codes”, dostęp 2026-11-24).

Wersja zbiorcza wszystkich łatek, w tym GT-02, zostanie scalona do `exp/variant-b` (`experiment/PROTOCOL.md`, wersja zbiorcza). Czysta wersja musi przejść wszystkie bramki (PROTOCOL 2.3).

## Czynniki decyzyjne

- skuteczność wobec GT-02 i wobec sekretu, który zostaje w historii publicznego repozytorium (CICD-SEC-6) [@OWASP-Top10-CICD],
- trafność eksperymentu: reguły niedopasowane do katalogu (TW1), stały czas joba (M4/M5), K8 (te same ustawienia platformy dla A i B),
- zgodność z SP 800-204D (COMMIT-REQ-1, COMMIT-REQ-2, DEPLOY-REQ-1) [@NIST-SP800-204D] i SSDF (PS.1.1, interpretacja D10) [@NIST-SP800-218],
- lekki potok: mało plików i mało kodu firm trzecich.

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| S1. Co skanuje Gitleaks | commity z PR (`base..head`) i pushu (`before..after`); stan plików (`gitleaks dir`); cała historia przy każdym przebiegu |
| S2. Reguły | domyślne, wyjątki tylko według D6; domyślne bez pliku konfiguracji; domyślne z własną regułą na `JWT_SECRET` |
| S3. Raport | JSON w artefaktach i SARIF do code scanning; tylko JSON w artefaktach |
| S4. Plik workflow do E07-14 | wspólny plik bramek; osobny plik na bramkę; job w `workflow-lint.yml` |
| S5. Hook pre-commit (B01) | w repozytorium jako doradczy; tylko opis w rekomendacjach |
| S6. Wzorce spoza dostawców w secret scanningu | włączyć; zostawić wyłączone |
| S7. Push protection blokuje próbę GT-02 | push z jawnym obejściem i powodem; zmiana postaci łatki; uznanie za zatrzymanie przez platformę |
| S8. Zapis decyzji | nowy ADR; uzupełnienie ADR-0042 |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-24. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta.

| # | Decyzja | Powody autora |
|---|---|---|
| S1 | `gitleaks git` skanuje tylko commity zdarzenia: na PR `base..head`, na pushu `before..after` | historia jest publiczna (sekret usunięty w kolejnym commicie nadal wycieka), stały czas skanu, zgodne z praktyką |
| S2 | Domyślny zestaw reguł Gitleaksa. Plik `.gitleaks.toml` powstaje tylko wtedy, gdy czysta wersja da fałszywe alarmy, i zawiera wyjątki według D6 | obrona przed TW1, realistyczny potok |
| S3 | Pełny raport JSON w artefaktach i SARIF wysyłany do GitHub code scanning (`upload-sarif`) | dane do M1, spójność z SAST (E07-04), mały koszt (akcja dopuszczona w D9) |
| S4 | Nowy plik `devsecops-gates.yml` dla bramek wariantu B, które nie potrzebują obrazu. Zadania E07-04…E07-06 dopisują do niego swoje joby, a E07-14 scala go z `lint`, `test`, `build` | prostsze E07-14, mniej plików, bez podwójnego buildu (jak H8) |
| S5 | `.pre-commit-config.yaml` z hookiem `gitleaks` w tej samej wersji co w CI, doradczo i poza pomiarem | zatrzymuje sekret wcześniej niż PR, mały koszt |
| S6 | Włączyć wzorce spoza dostawców w secret scanningu | bezpłatne |
| S7 | Jeśli push protection zablokuje push łatki GT-02, próba idzie przez jawne obejście z powodem „used in tests”, zapisane w dzienniku; blokadę platformy zapisujemy osobno w danych jako wynik B03 | eksperyment mierzy potoki, ślad w logu platformy i dzienniku, realistyczny scenariusz (programista może obejść push protection) |
| S8 | Nowy ADR (ten), ADR-0042 bez zmian | — |

**Uwaga do S6.** Pytanie w wywiadzie zakładało, że wzorce spoza dostawców dają tylko alerty. Dokumentacja GitHuba mówi, że push protection obejmuje też tę kategorię (tabela „Capabilities by category” na stronie „Supported secret scanning patterns”, dostęp 2026-11-24), więc mogą blokować push. Wzorce tej kategorii to klucze prywatne, connection stringi (MongoDB, MySQL, PostgreSQL) i nagłówki HTTP Basic i Bearer. Żadna pozycja katalogu nie ma takiej postaci, więc na pomiar to nie wpływa. Dostępność tej funkcji dla publicznego repozytorium na koncie osobistym: TODO: zweryfikować przy `settings.sh apply`.

**Uzasadnienie „zgodne z praktyką” (S1).** Oficjalna akcja `gitleaks/gitleaks-action` (wersja przypięta w `docs/narzedzia.md`, commit `e0c47f4`) na PR i pushu skanuje zakres commitów przez `--log-opts` (`src/gitleaks.js`, dostęp 2026-11-24).

Decyzje agenta (techniczne, w ramach decyzji autora):

- **zakres przy nowej gałęzi:** push nowej gałęzi nie ma „before”, więc skanowane są commity spoza gałęzi domyślnej (`origin/main..after`); zakres, którego końców nie ma w klonie (np. po force push), zatrzymuje job przed skanem (fail closed),
- **`--exit-code 2`:** oddziela wyciek (`2`) od błędu narzędzia (`1`); krok raportu akceptuje `0` i `2`, a próg stosuje osobny krok na raporcie JSON (zasada z ADR-0042), tak jak oficjalna akcja,
- **`--redact`:** wartości nie trafiają do raportów, bo artefakty publicznego repozytorium może pobrać każdy zalogowany użytkownik; do M1 wystarczą reguła, plik, linia i commit,
- **`--ignore-gitleaks-allow`:** komentarze `gitleaks:allow` nie wyłączają bramki (analogia do D13),
- **repozytorium montowane w kontenerze tylko do odczytu,** raporty w osobnym katalogu,
- **`upload-sarif` w wersji v4.39.3** (2026-11-04), a nie v4.39.4 (2026-11-20), bo nowsza nie przeszła 7-dniowej karencji z H6,
- **hook `gitleaks`** (budowany przez pre-commit z Go), a nie `gitleaks-docker`, żeby działał bez Dockera; `rev` przypięty do commita tagu v8.30.1 (`83d9cd68`).

## Konsekwencje

- (+) Kroki B01 i B07 z `docs/projekt-potoku.md` są zrealizowane; B03 było włączone w E07-02.
- (+) Sekret dodany i usunięty w kolejnym commicie tego samego PR zostaje wykryty (test lokalny 2026-11-24: skan zakresu 1 zgłoszenie, `gitleaks dir` 0).
- (+) Czysta wersja przechodzi bez wyjątków D6: pełna historia (88 commitów, wszystkie gałęzie lokalne, 2026-11-24) nie ma zgłoszeń, więc `.gitleaks.toml` nie powstał.
- (−) Gitleaks uruchamia się dwa razy (JSON i SARIF), bo wersja 8.30.1 zapisuje jeden format na przebieg. Przy zakresie kilku commitów to niewielki koszt; czas joba `secrets` zmierzy seria (M4/M5).
- (−) Plik `.gitleaksignore` albo `.gitleaks.toml` dodany w PR zmieniłby działanie bramki. To ryzyko resztkowe z `docs/projekt-potoku.md` (4.6), materiał do 5.3.
- (−) Check code scanningu `gitleaks` nie blokuje: zgłoszenie Gitleaksa ma w SARIF poziom `warning`, a domyślny próg checku code scanningu go nie zatrzymuje (PR #19). Blokuje job `secrets`.
- Wyniki testów:
  - **PR #18** (2026-11-24): `secrets` przechodzi, 1 commit, 0 zgłoszeń; `workflow-lint`, `lint`, `test`, `build` przechodzą.
  - **Push protection** (2026-11-24, wzorce spoza dostawców wyłączone): push commita z łatką GT-02 na gałąź `test/e07-03-gt02-negative` **nie został zablokowany**. Potwierdza to przypuszczenie z `docs/projekt-potoku.md` (4.6): losowa wartość bez prefiksu dostawcy nie pasuje do wzorców platformy. S7 nie było potrzebne.
  - **PR #19** (test negatywny, draft, zamknięty bez scalania): `secrets` blokuje z 1 zgłoszeniem `generic-api-key` w `app/ticketing/config.py` (commit `a297a60`). Łatka testowa ma postać GT-02 z decyzji z 2026-10-20, ale nie jest docelową łatką z E04.
- Kolejne zadania:
  - **E07-03 (po scaleniu):** dopisać `secrets` do `required_status_checks` w `infra/github/rulesets/main.json` i `variant-b.json`, włączyć wzorce spoza dostawców w `infra/github/settings.sh` (S6) i uruchomić `settings.sh apply`; powtórzyć sprawdzenie push protection z GT-02 po włączeniu,
  - **E07-04…E07-06:** joby `sast`, `sca`, `iac` w `devsecops-gates.yml`,
  - **E07-14:** scalić `devsecops-gates.yml` z `lint`, `test`, `build` w workflow wariantu B.
- TODO: zweryfikować: dostępność wzorców spoza dostawców dla repozytorium na koncie osobistym; czy wzorce spoza dostawców blokują push łatki GT-02 (oczekiwanie: nie).

## Źródła

- [@NIST-SP800-204D]: COMMIT-REQ-1, COMMIT-REQ-2, DEPLOY-REQ-1; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PS.1.1 (interpretacja autora, D10), PW.7.2; notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-Top10-CICD]: CICD-SEC-6; notatki `docs/notes/owasp-devsecops.md`, sekcja 3.
- [@OWASP-DevSecOps-Guideline]: skan sekretów w pre-commit i CI, „fail closed”; notatki `docs/notes/owasp-devsecops.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-24):
  - Gitleaks README v8.30.1: https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md
  - `gitleaks-action`, `src/gitleaks.js`: https://github.com/gitleaks/gitleaks-action/blob/e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e/src/gitleaks.js
  - GitHub Docs, „Supported secret scanning patterns”: https://docs.github.com/en/code-security/reference/secret-security/supported-secret-scanning-patterns
  - GitHub Docs, „Enabling secret scanning for generic patterns”: https://docs.github.com/en/code-security/secret-scanning/using-advanced-secret-scanning-and-push-protection-features/non-provider-patterns
