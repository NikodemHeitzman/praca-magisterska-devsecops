# 0043. Utwardzenie workflowów i platformy GitHub: rulesety, polityka akcji, Dependabot, lint workflowów

- **Status:** przyjęty
- **Data:** 2026-11-23
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0042](0042-projekt-potoku-wariantu-b.md) (kroki B02–B05, B16, B17; D5, D9, D11), [0041](0041-zamrozenie-wariantu-a.md), [`docs/projekt-potoku.md`](../projekt-potoku.md), [`docs/ustawienia-github.md`](../ustawienia-github.md), [`infra/github/`](../../infra/github/), [`.github/workflows/workflow-lint.yml`](../../.github/workflows/workflow-lint.yml), [`.github/dependabot.yml`](../../.github/dependabot.yml), [`.github/CODEOWNERS`](../../.github/CODEOWNERS), zadanie E07-02, `experiment/PROTOCOL.md` (P1, 2.2, zasada 4), [dziennik 2026-11-23](../log/2026-11-23.md)

## Kontekst

ADR-0042 umieścił część kontroli wariantu B na platformie GitHub (etap 1: kroki B02–B05) i w jobie `workflow-lint` (B16, B17). Na PR bramki egzekwuje ruleset, a nie `needs:`. Stan repozytorium przed zadaniem (odczyt przez API, 2026-11-23):

- `main` bez rulesetu i bez klasycznej ochrony gałęzi,
- Dependabot wyłączony (alerty, security updates), brak `.github/dependabot.yml`,
- dozwolone wszystkie akcje, przypinanie do SHA niewymuszone (pilnowała go tylko konwencja z `AGENTS.md`, zasada 5),
- zgoda na workflow z forków tylko przy pierwszym wkładzie,
- domyślny `GITHUB_TOKEN` tylko do odczytu, secret scanning i push protection włączone,
- actionlint i zizmor uruchamiane tylko lokalnie (E05, E06-05).

Konfiguracja platformy nie jest pod kontrolą wersji (CICD-SEC-7) [@OWASP-Top10-CICD]. Wariant B ma być jednym workflow (D3, D4), ale powstanie dopiero w E07-03…E07-14. Seria czasowa „main” wypycha puste commity bezpośrednio na `exp/variant-b` (`experiment/PROTOCOL.md`, 2.2).

## Czynniki decyzyjne

- zgodność z SP 800-204D i SSDF: PP-AUTH*, PP-INT*, BUILD-2*, PULL-PUSH-REQ-2, PRE-2*, PRE-3*, PO.2.1, PO.3.2, PS.1.1 [@NIST-SP800-204D; @NIST-SP800-218],
- trafność eksperymentu: K2 (A/B różnią się tylko kontrolami bezpieczeństwa), P1 (ochrona `exp/variant-b` zamrożona), zgodność z protokołem serii,
- projekt jednoosobowy: brak drugiego recenzenta,
- prostota i odtwarzalność ustawień.

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| H1. Zakres rulesetu | `main` + `exp/variant-b`; `main` + wszystkie `exp/*`; tylko `main` |
| H2. Obejścia | nikt, także właściciel; właściciel tylko przez PR; właściciel zawsze |
| H3. Wymagane checki | lista rosnąca z zadaniami E07; pełna lista w E07-14; pełna lista od razu |
| H4. harden-runner i podpisane commity (D11) | oba poza B; tylko podpisane commity; tylko harden-runner; oba |
| H5. CODEOWNERS | plik jako ślad, bez wymogu przeglądu; bez pliku; plik z wymogiem przeglądu |
| H6. Dependabot | `github-actions`, `uv`, `docker`; tylko `github-actions`; dodatkowo Terraform |
| H7. Polityka akcji | wymuszenie SHA i lista dozwolonych; tylko wymuszenie SHA; bez zmian (zizmor i przegląd) |
| H8. Miejsce `workflow-lint` | osobny workflow teraz; szkielet workflow B teraz; dopiero w E07-14 |
| H9. Workflow z forków | zgoda dla wszystkich zewnętrznych kontrybutorów; bez zmian |
| H10. Profil zizmora | domyślny (`regular`); `pedantic`; `auditor` |
| H11. Dodatkowe reguły | blokada force push i usunięcia; ochrona tagów; gałąź aktualna przed scaleniem (strict); liniowa historia |
| H12. Ustawienia jako kod | JSON w repozytorium i skrypt; tylko spis w dokumentacji; Terraform (provider `github`) |
| H13. Bezpośredni push w serii „main” a ruleset bez obejść | obejście dla właściciela tylko na `exp/variant-b`; seria „main” przez scalanie PR; wyłączenie rulesetu na czas serii |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-23. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta. H13 wynikło z konfliktu, który agent znalazł po wywiadzie: H2 (bez obejść) blokowałoby serię „main” z PROTOCOL 2.2.

| # | Decyzja | Powody autora |
|---|---|---|
| H1 | Rulesety na `main` i `exp/variant-b`; gałąź `exp/variant-a` bez rulesetu | nie zmieniać zamrożonego wariantu A, czysty pomiar |
| H2 | Na `main` nikt nie może obejść rulesetu, także właściciel (wyjątek dla `exp/variant-b`: H13); awaryjnie można wyłączyć ruleset, co zostaje w logu audytu | zgodne z B02 i SP 800-204D, ślad w logu audytu |
| H3 | Wymagane checki: teraz `lint`, `test`, `build`, `workflow-lint`; każde z zadań E07-03…E07-10 dopisuje swój job do rulesetu (JSON w repozytorium) | praca nie stoi, każde zadanie może od razu sprawdzić swoją bramkę na PR |
| H4 | D11 bez zmian: harden-runner i podpisane commity poza wariantem B | jeden autor, czysty pomiar |
| H5 | `CODEOWNERS` jako ślad odpowiedzialności, ruleset nie wymaga przeglądu właściciela kodu | jeden autor, gotowe na drugiego recenzenta |
| H6 | Dependabot: alerty i security updates włączone; aktualizacje wersji dla `github-actions`, `uv` (`app/`) i `docker` (`app/Dockerfile`), co tydzień, karencja 7 dni, jeden zgrupowany PR na ekosystem | pokrywa artefakt, karencja przeciw złośliwym wersjom, Terraform poza artefaktem, mniej PR-ów do przeglądu |
| H7 | Platforma wymusza przypinanie akcji do pełnego SHA (`sha_pinning_required`) i dopuszcza tylko akcje GitHuba oraz jawną listę (dziś `astral-sh/setup-uv`) | egzekwowanie zamiast konwencji |
| H8 | actionlint i zizmor w osobnym workflow `workflow-lint.yml`; w E07-14 job przechodzi do workflow wariantu B | bez podwójnego buildu, prosto |
| H9 | Zgoda na uruchomienie workflow dla wszystkich zewnętrznych kontrybutorów (`all_external_contributors`) | zgodne z protokołem (zasada 4), brak kosztów |
| H10 | zizmor w profilu domyślnym (`regular`); bramka od poziomu `low` (D5) | bezpieczeństwo, nie styl |
| H11 | Blokada force push i usunięcia na chronionych gałęziach; osobny ruleset tagów (zakaz usunięcia i przesunięcia); bez trybu strict i bez liniowej historii | odtwarzalność tagów |
| H12 | Rulesety jako JSON w `infra/github/rulesets/`, pozostałe ustawienia w skrypcie `infra/github/settings.sh` (`show`, `apply`), spis w `docs/ustawienia-github.md` | zmiany w historii repozytorium, prosto |
| H13 | Na `exp/variant-b` rola admina repozytorium może obejść ruleset (`bypass_mode: always`), więc skrypt serii może pushować bezpośrednio; PR-y do `exp/variant-b` nadal wymagają checków | ślad w logu reguł, porównywalne przebiegi |

Decyzje agenta (techniczne, w ramach decyzji autora):

- wymagane checki przypięte do aplikacji GitHub Actions (`integration_id` 15368), żeby status o tej samej nazwie z innego źródła nie spełniał wymogu,
- na `exp/variant-b` `do_not_enforce_on_create: true`, żeby dało się utworzyć gałąź z tagu czystej wersji (E09),
- `workflow-lint` bez filtra ścieżek, bo pominięty wymagany check blokowałby PR,
- zizmor w trybie online z tokenem joba tylko do odczytu (sprawdza m.in., czy przypięty SHA istnieje w repozytorium akcji i czy wersja akcji nie ma znanych podatności),
- najpierw pełne raporty obu narzędzi (artefakt `workflow-lint-reports`, dane do M1), potem osobne kroki bramek (zasada z ADR-0042),
- zizmor sprawdza też `.github/dependabot.yml` (reguła `dependabot-cooldown` wymaga co najmniej 7 dni karencji).

## Konsekwencje

- (+) Kroki B02–B05, B16 i B17 z `docs/projekt-potoku.md` są zrealizowane, a ustawienia platformy mają wersję w repozytorium (CICD-SEC-7).
- (+) Akcja przypięta do tagu albo spoza listy nie uruchomi się, nawet jeśli przejdzie przez przegląd i zizmora.
- (+) Zamrożone tagi (`pipeline-a-v1`, `methodology-v1`) nie mogą zostać przesunięte ani usunięte.
- (−) Każda nowa akcja firmy trzeciej wymaga dopisania do `allowed_patterns` w `infra/github/settings.sh` i ponownego `apply`.
- (−) Obejście na `exp/variant-b` (H13) pozwala właścicielowi pushować bez checków. Na pushu bramek pilnuje atestacja (D3), ale samo obejście to ryzyko resztkowe (materiał do 5.3, razem z brakiem drugiego recenzenta).
- (−) Dependabot nie utrzymuje razem `uv.lock` i `requirements.txt` (eksport z `uv.lock`). Pierwsza security update (PR #13, `dnspython` 2.9.2, 2026-11-23) zmieniła tylko `requirements.txt`, bo alert dotyczył też tego pliku jako manifestu pip. Takie PR-y zamykamy i robimy aktualizację ręcznie: `uv lock --upgrade-package` i nowy eksport (decyzja autora z 2026-11-24).
- (−) Ekosystem `docker` proponuje też nowy obraz uv (PR #14, 0.13.9), a wersja uv musi być ta sama w `app/Dockerfile` i w `UV_VERSION` workflowów, przy zamrożonym wariancie A. Decyzja autora z 2026-11-24: reguła `ignore` dla obrazu uv w `.github/dependabot.yml`; uv aktualizujemy ręcznie we wszystkich miejscach naraz, w A tylko przez nowy tag zamrożenia (ADR-0041).
- Kolejne zadania:
  - **E07-03…E07-10:** każde zadanie dopisuje swój job do `required_status_checks` w `infra/github/rulesets/main.json` i `variant-b.json` i uruchamia `infra/github/settings.sh apply`,
  - **E07-14:** przenieść job `workflow-lint` do workflow wariantu B i usunąć `workflow-lint.yml`,
  - **E09:** sprawdzić przy tworzeniu `exp/variant-b`, że obejście (H13) działa dla pushy skryptu serii.
- Sprawdzone po pierwszym `apply` (2026-11-23):
  - `actor_id: 5` to rola admina: API zwraca `current_user_can_bypass` = `always` dla `exp-variant-b` i `never` dla `main` i `tags`,
  - `patterns_allowed` zapisane (repozytorium jest publiczne),
  - API dopisuje do reguły `pull_request` domyślny parametr `require_extra_approval_for_unattributed_changes: true`, a z reguły `update` dla tagów usuwa `update_allows_fetch_and_merge`. Pliki JSON zapisują stan zwrócony przez API. Parametr dotyczy PR-ów otwieranych przez Copilota bez przypisanej osoby i według dokumentacji nie działa przy zerowej liczbie wymaganych zatwierdzeń (strona „Available rules for rulesets”, dostęp 2026-11-24), więc w tym repozytorium nie ma skutku.
- Test negatywny (PR #12, 2026-11-23, szczegóły w dzienniku): akcję przypiętą do tagu zatrzymały trzy warstwy: zizmor w `workflow-lint` (high), polityka platformy (`startup_failure` z adnotacją o SHA i liście) i ruleset (PR `BLOCKED`). Akcja przypięta do SHA, ale spoza listy, przeszła przez zizmora i zatrzymała ją tylko platforma (`startup_failure`).
- TODO: zweryfikować: przyczynę `startup_failure` akcji spoza listy (brak adnotacji); czy reguła `update` nie blokuje tworzenia nowych tagów (według dokumentacji tworzenie to osobna reguła `creation`; sprawdzić przy następnym tagu, np. zamrożeniu B).

## Źródła

- [@NIST-SP800-204D]: PP-AUTH*, PP-INT*, BUILD-2*, PULL-PUSH-REQ-2, PRE-2*, PRE-3*, PRE-5*, DEPLOY-REQ-5; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PO.2.1, PO.3.2, PO.5.1, PS.1.1; notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-Top10-CICD]: CICD-SEC-1, -4, -5, -7, -8; notatki `docs/notes/owasp-devsecops.md`, sekcja 3.
- [@OWASP-DevSecOps-Guideline]: utwardzenie repozytorium i potoku; notatki `docs/notes/owasp-devsecops.md`.
- [@Laster2023], rozdz. 9: uprawnienia, CODEOWNERS, rulesety, przypinanie akcji, `pull_request_target` (mapa w `docs/notes/ksiazki.md`; strony TODO: zweryfikować przy lekturze).
- [@Incydent-tj-actions], [@Incydent-Trivy]: uzasadnienie wymuszenia SHA, listy akcji i karencji Dependabota.
- Dokumentacja GitHub (REST: rulesets, uprawnienia Actions; Dependabot options reference) i zizmor (`docs.zizmor.sh`, dostęp 2026-11-23); poza rejestrem źródeł, TODO: zweryfikować, czy dodać do `Zrodla/`.
