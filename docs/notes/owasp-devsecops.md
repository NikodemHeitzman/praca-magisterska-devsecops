# OWASP DevSecOps Guideline i OWASP Top 10 CI/CD Security Risks: notatki z lektury

- **Źródła:** [@OWASP-DevSecOps-Guideline], [@OWASP-Top10-CICD].
- **Zadanie:** E02-04 (tablica zadań). Używane w 2.2 (model zagrożeń potoku), 3.3 (projekty OWASP), 4.3 (projekt potoku i bramek) i 5.3 (dyskusja i ograniczenia). Lista ryzyk z przykładami dla potoku (sekcja 3) i tabela rekomendacji (sekcja 4) zasilają listę kontrolną celu C1 (`docs/metodyka.md`, p. 1.5).
- **Skąd tekst:** notatki przygotował agent (Claude Code) 2026-10-20 na podstawie tekstu źródeł pobranego z oficjalnych repozytoriów OWASP, nie z pamięci:

  | Źródło | Repozytorium | Wersja (ref) | Pliki |
  |---|---|---|---|
  | DevSecOps Guideline | `OWASP/DevSecOpsGuideline` | `master`, commit `a2cd4f9` (2026-10-16) | `current-version/**/*.md` |
  | Top 10 CI/CD, PDF | `OWASP/www-project-top-10-ci-cd-security-risks` | `assets/OWASP_Top_10_CICD_Risks.pdf`, dodany 2022-11-15 (commit `3204d6d`) | 39 stron PDF, 37 numerowanych |
  | Top 10 CI/CD, strony webowe | ten sam, commit `74b2c79` (2025-11-03) | `index.md`, `CICD-SEC-*.md` | porównane z PDF |

- **Numery stron:**
  - Top 10 CI/CD cytujemy według PDF: `dok. s.` to numer w stopce dokumentu, a strona w przeglądarce PDF jest o 1 większa (np. dok. s. 14 = PDF s. 15). Strony webowe różnią się od PDF drobiazgami (sekcja 2.1).
  - Guideline to dokument webowy bez stron i bez wydań. Miejsce w źródle podajemy jako ścieżkę rozdziału, np. `2-3-5 Security Gates`. W bibliografii podajemy datę dostępu i commit.
- **Stan lektury:** autor czyta opracowanie z pytaniami kontrolnymi ([`owasp-devsecops-pytania.md`](owasp-devsecops-pytania.md)). Oryginałów nie czytał (decyzja autora z 2026-10-20). Autor przeczytał opracowanie 2026-10-28, więc źródła mają `zweryfikowane: opracowanie`.

## Jak czytać ten plik

1. Sekcja 1: Guideline, czyli czym jest, główne tezy i zestawienie z projektowanym potokiem.
2. Sekcja 2: Top 10 CI/CD, czyli czym jest i notatki do każdego ryzyka.
3. Sekcja 3: **lista ryzyk CICD-SEC z przykładem dla mojego potoku** (kryterium ukończenia E02-04).
4. Sekcja 4: rekomendacje Top 10 CI/CD jako kandydaci do listy kontrolnej (C1), z oceną stosowalności i pokryciem przez SP 800-204D.
5. Sekcja 5: przypisanie pozycji katalogu podatności (`experiment/ground-truth.yaml`, pole `owasp_cicd`) do ryzyk.
6. Sekcje 6–7: porównanie obu dokumentów z SP 800-204D i uwagi krytyczne do 5.3.
7. Sekcja 8: decyzje do podjęcia przez autora i otwarte kwestie.

Oceny stosowalności, przykłady i przypisania w sekcjach 1.4, 3, 4 i 5 to **propozycje agenta**, nie decyzje.

---

## 1. OWASP DevSecOps Guideline

### 1.1. Czym jest

- Przewodnik praktyk i narzędzi do budowy bezpiecznego potoku dostarczania oprogramowania, „dla organizacji każdej wielkości” (`0-1 Intro`). Nie jest standardem ani listą wymagań: nie ma identyfikatorów wymagań, mocy (MUST/SHOULD) ani procedury oceny.
- Cel dokumentu w jednym zdaniu (`0-1 Intro`): wykrywać problemy bezpieczeństwa (projektowe i implementacyjne) jak najwcześniej i najtaniej, a potem wykrywać je dalej w sposób ciągły. Dokument mówi o *shift-left* i coraz częściej o *shift-everywhere* (`0-2 Overview`).
- **Status:** projekt OWASP w fazie Incubator, lider A. Yazdani. Nie ma numerowanych wydań ani tagów. Treść zmienia się co kilka dni: między 2026-09-24 a 2026-10-16 weszło kilkanaście commitów, m.in. przykłady bramek dla GitLaba i dopisanie generowania provenance.
- **Wersje:**
  - 2026-06-28 (commit `a4f4793`) przebudowano całość („restructure guideline and expand content for 2025/2026”).
  - Starsze wydania V0.1–V0.3 leżą w `old-versions/`.
  - Strona owasp.org odsyła do `current-version`, ale repozytorium strony projektu ma jeszcze w `latest/` stary układ V0.1 (stan 2026-10-20). W pracy cytujemy `current-version` z commitem.

### 1.2. Budowa

Trzy filary (`0-1 Intro`):

| Filar | Zawartość | Znaczenie dla pracy |
|---|---|---|
| People | security champions, role, szkolenia (w tym szkolenie z bezpieczeństwa CI/CD) | małe: projekt jednoosobowy |
| Process | 7 etapów: Design, Develop, Build, Test, Release, Deploy, Operate, z kontrolami przypisanymi do etapów | **główne:** podstawa doboru etapów i narzędzi (C2) |
| Governance | zgodność, policy as code, raportowanie, ASPM, zarządzanie AI | tło: zgodność jako dowody z potoku |

Kontrole w etapie Process (`0-1 Intro`, „How this guideline is organized”):

- **Design:** modelowanie zagrożeń, bezpieczny projekt, wymagania bezpieczeństwa.
- **Develop:** hooki pre-commit, zarządzanie sekretami, linting, utwardzenie repozytorium, bezpieczeństwo pracy z asystentami AI.
- **Build:** SAST, SCA, bezpieczeństwo kontenerów, skan IaC, bramki bezpieczeństwa, łańcuch dostaw (SBOM, podpisy i provenance, bezpieczeństwo potoku).
- **Test:** IAST, DAST, testy aplikacji mobilnych, bezpieczeństwo API, kontrola błędnej konfiguracji.
- **Release:** końcowa akceptacja, podpisane i atestowane artefakty.
- **Deploy:** kontrola dopuszczania (*admission control*), GitOps, wdrażanie stopniowe.
- **Operate:** bezpieczeństwo w czasie działania, logowanie i monitoring, testy penetracyjne, zarządzanie podatnościami, programy zgłaszania podatności, symulacja ataków (BAS).

Rozdziały mają ten sam układ: opis, przykłady konfiguracji (głównie GitHub Actions), typowe błędy (*pitfalls*), stopnie dojrzałości, metryki i listy narzędzi (otwarte i komercyjne, alfabetycznie).

### 1.3. Główne tezy

1. **DevSecOps to nie zakup narzędzi.** Rozdział `0-1 Intro` wylicza, czym DevSecOps nie jest: zespołem bezpieczeństwa wstawionym do potoku, zakupem narzędzi, jednorazowym projektem, zgodnością z przepisami ani „tylko CI/CD”. Narzędzia bez procesu segregacji zgłoszeń (*triage*), właściciela i terminów naprawy dają zmęczenie alertami i fałszywe poczucie bezpieczeństwa.
2. **Potok to też powierzchnia ataku.** Narzędzia budowania i automatyzacji same są celem ataku, więc zabezpieczenie potoku dokument traktuje na równi z zabezpieczeniem aplikacji (`0-1 Intro`, „A note on the pipeline itself”). Przykłady: SolarWinds, Codecov, xz-utils, tj-actions/changed-files (2025) i akcje Trivy (2026).
3. **Kolejność wprowadzania kontroli** (`0-2 Overview`, „A recommended introduction order”). Uzasadnienie: największa redukcja ryzyka na jednostkę wysiłku. Dokument radzi zacząć od pozycji 1–3.

   | Priorytet | Kontrola | Uzasadnienie według dokumentu |
   |---|---|---|
   | 1 | Skan sekretów (pre-commit i CI) | najczęstszy i najbardziej szkodliwy wyciek w potoku, prawie zero fałszywych alarmów |
   | 2 | SCA w CI | znane CVE w zależnościach, mało fałszywych alarmów |
   | 3 | Ochrona gałęzi i SAST w PR | bramka dla nowego kodu |
   | 4 | Skan IaC | błędna konfiguracja chmury przed jej utworzeniem |
   | 5 | Skan kontenerów | podatne obrazy bazowe |
   | 6 | DAST / IAST | wymaga środowiska testowego |
   | 7 | SBOM i podpisy | zaufanie w łańcuchu dostaw, wymagania regulacyjne |

4. **Bramki bez niszczenia przepływu pracy** (`2-3-5 Security Gates`):
   - blokować według ryzyka (ważność, wykorzystywalność, osiągalność), a nie według liczby zgłoszeń,
   - rozliczać tylko z *nowych* zgłoszeń względem stanu bazowego (*baseline*),
   - jasno mówić, co i gdzie naprawić,
   - mieć udokumentowany proces wyjątków ograniczonych w czasie,
   - stroić reguły, bo fałszywe alarmy to błąd bramki, a nie programisty.
5. **Bramka ma działać w trybie „fail closed”** (`2-3-5 Security Gates`):
   - brak raportu skanera oznacza błąd, a nie wynik „czysto”,
   - stan ERROR (skaner się nie wykonał) trzeba odróżnić od FAILED,
   - kody wyjścia narzędzi znaczą co innego: OSV-Scanner zwraca 1 przy znalezionych podatnościach, a Trivy domyślnie zwraca 0 niezależnie od wyników.
6. **Hooki pre-commit nie są kontrolą bezpieczeństwa.** Programista pominie je opcją `--no-verify`. Te same kontrole muszą działać w CI, które jest warstwą „autorytatywną” (`2-2-1-1 Pre-commit`).
7. **Utwardzenie potoku** (`0-2 Overview`, `2-2-1-4 Repository Hardening`, `2-3-6-3 CI/CD Pipeline Security`):
   - OIDC zamiast długoterminowych kluczy chmurowych,
   - przypinanie akcji i obrazów do niezmiennych SHA/digestów,
   - minimalne `permissions:` w każdym jobie,
   - efemeryczne runnery z kontrolą ruchu wychodzącego,
   - bez `pull_request_target` z kodem z forka,
   - przegląd zmian w plikach workflow (CODEOWNERS),
   - skanowanie workflow zizmorem.

   Wprost: przypinanie do SHA chroni przed przejęciem tagów jak w tj-actions (2025) i trivy-action (2026). GitHub pozwala ten wymóg wymusić w ustawieniach Actions.
8. **Podpis bez weryfikacji to „teatr bezpieczeństwa”** (`2-3-6-2 Artifact Signing and Provenance`, `2-5-1 Release`, `2-6-1 Deploy`):
   - weryfikację wykonuje się przy promocji artefaktu i przy wdrożeniu,
   - podpisuje się digest, nie tag,
   - weryfikacja działa w trybie „fail closed”.
9. **Artefakt buduje się raz i ten sam promuje przez kolejne środowiska** (`2-5-1 Release`). Przebudowa na produkcję unieważnia wyniki testów z wcześniejszych etapów.
10. **SLSA na GitHub Actions** (`0-3 Frameworks`, `2-3-6-2`):
    - same artifact attestations dają Build L2,
    - L3 wymaga budowania w reusable workflow albo generatora SLSA,
    - L2 jest „osiągalny dla większości zespołów”.

    Sprawdzone w E02-05 (2026-10-28, `slsa.md`, sekcje 3.2–3.3 i 5) według specyfikacji [@SLSA-1.2] i dokumentacji GitHuba:
    - L2: potwierdzone.
    - L3 przez reusable workflow: tak twierdzi GitHub, ale atestacja w jednym jobie z buildem nie spełnia litery wymagania „Unforgeable”.
    - Generator SLSA nie jest już aktywnie utrzymywany.

    Decyzja autora (wariant A): próg H3b ≥ L2, L3 jako cel rozszerzony w E07-09.
11. **Mapa ram** (`0-3 Frameworks and Standards`):
    - SSDF to bazowy poziom zgodności,
    - SAMM mierzy dojrzałość strategiczną,
    - DSOMM wspiera wdrażanie praktyk przez inżynierów,
    - SLSA dotyczy integralności łańcucha dostaw,
    - Top 10 CI/CD opisuje ryzyka samego potoku.

    Guideline sytuuje się „pośrodku” i przekłada te ramy na kontrole przypisane do etapów. To gotowa rama do 3.3.

### 1.4. Zestawienie z projektowanym potokiem (wariant B)

Etapy i kontrole Guideline zestawione z planem potoku. Narzędzia według `docs/narzedzia.md`, identyfikatory SP 800-204D według [`nist-800-204d.md`](nist-800-204d.md). Status:

- **plan:** jest w obecnym planie (E02-10, `experiment/PROTOCOL.md`),
- **nowe:** Guideline podsuwa coś, czego plan nie zawiera, do decyzji w E07-01,
- **poza:** poza zakresem pracy, z uzasadnieniem.

| Etap Guideline | Kontrola | W projekcie | Status | SP 800-204D |
|---|---|---|---|---|
| Design | Modelowanie zagrożeń | Model zagrożeń potoku według Top 10 CI/CD (sekcja 3, 2.2 pracy). Dla aplikacji osobnego modelu nie planujemy, bo jej podatności wyznacza katalog | plan (potok) / do decyzji (aplikacja) | — |
| Develop | Pre-commit | Gitleaks i Semgrep jako hook lokalny. Guideline: hook to wygoda, nie kontrola, a kontrola działa w CI | nowe (opcjonalne, poza pomiarem) | — |
| Develop | Sekrety | Gitleaks w CI (PR i pełna historia), secret scanning i push protection GitHuba, OIDC do AWS | plan | COMMIT-REQ-1, COMMIT-REQ-2, DEPLOY-REQ-1 |
| Develop | Utwardzenie repozytorium | Rulesety lub ochrona gałęzi, wymagane *status checks*, blokada force push, podpisane commity, przypinanie akcji do SHA, minimalne `permissions:`, zatwierdzanie workflow z forków. CODEOWNERS ma ograniczony sens przy jednym autorze | plan / Cz | PP-AUTH*, PP-INT*, PULL-PUSH-REQ-2, PULL-PUSH-REQ-3 |
| Develop | Pomiar postawy | OpenSSF Scorecard jako miara w ewaluacji | plan (miara) | PULL-PUSH-REQ-4, BASE-6* |
| Build | SAST | Semgrep (z regułami własnymi dla GT-06 i GT-14), Bandit; seria porównawcza CodeQL | plan | TEST-1* |
| Build | SCA | pip-audit, Trivy, `dependency-review-action` | plan | TEST-2*, DEPLOY-REQ-2 |
| Build | Zarządzanie zależnościami | Lockfile z hashami (`pip install --require-hashes`), dokładne wersje (P2 w protokole). Okres karencji (*cooldown*) dla Dependabota | plan (lockfile) / nowe (cooldown) | BASE-4* |
| Build | Kontener: skan i utwardzenie | Trivy (obraz), hadolint, nieuprzywilejowany `USER`, obraz bazowy przypięty digestem | plan | DEPLOY-REQ-4, DEPLOY-REQ-5 |
| Build | IaC | Checkov, Trivy config | plan | PRE-5* |
| Build | Bramki | Joby-bramki jako wymagane *status checks*, progi zapisane przed serią (P1), pełne raporty także poniżej progu. Z Guideline: tryb „fail closed” przy braku raportu i jawny kod wyjścia Trivy | plan / nowe (fail closed) | BUILD-2* |
| Build | SBOM | Syft: SPDX (atestowany) i CycloneDX (artefakt) | plan | ATT-1*, TEST-2* |
| Build | Podpis i provenance | `actions/attest` (następca `attest-build-provenance`), weryfikacja `gh attestation verify` przed deployem. SLSA Build L2 jako próg, L3 (osobny job atestacji) jako cel rozszerzony (E02-05, `slsa.md`) | plan | BUILD-3*, ATT-1*–ATT-4* |
| Build | Bezpieczeństwo potoku | zizmor, actionlint, `step-security/harden-runner` (otwarte), OIDC z rolą na środowisko | plan / otwarte | PRE-1*, PRE-3*, DEPLOY-REQ-5 |
| Test | DAST | ZAP baseline na kontenerze w runnerze na każdym PR. Zgodne z Guideline: skan pasywny w efemerycznym środowisku | plan | TEST-1* |
| Test | API | ZAP API scan z `openapi.json` z FastAPI. Rozszerzenie zasięgu DAST | nowe (do decyzji, wpływa na pułap H1) | TEST-1* |
| Test | IAST | — | poza (`AGENTS.md`) | — |
| Release | Niezmienność i identyfikowalność | Ten sam digest w teście i na produkcji (protokół, zasada 4), niezmienne tagi w ECR, tag obrazu = SHA commita | plan / do ADR (usługa AWS) | GitOps-REQ-2, ATT-3* |
| Deploy | Weryfikacja przed wdrożeniem | `gh attestation verify` dla digestu przed wdrożeniem, „fail closed” | plan | DEPLOY-REQ-3, ATT-4* |
| Deploy | Tożsamość wdrożenia | OIDC, rola IAM tylko dla środowiska docelowego | plan | PRE-3*, BASE-7* |
| Deploy | Admission control, GitOps | — | poza (brak Kubernetes) | GitOps-REQ-1 (Cz) |
| Operate | Logowanie | CloudTrail. Logi przebiegów zapisywane jako artefakty eksperymentu | plan (Cz) | BASE-8* |
| Operate | Zarządzanie podatnościami, ASPM, BAS, pentest | — | poza (zakres lekkiego potoku) | — |

Wniosek do 4.3: Etapy Build i Test Guideline pokrywają się z planem wariantu B prawie w całości. Różnice:

- **Nowe propozycje:** karencja aktualizacji, „fail closed”, skan API.
- **Elementy poza zakresem:** Kubernetes, IAST, ASPM, które definicja lekkiego potoku wyklucza (`docs/metodyka.md`, p. 1.1).

### 1.5. Wskazówki do projektu bramek (E07-01)

Z `2-3-5 Security Gates`, `2-3-1-1 SAST` i `2-4-2 DAST`:

1. **Gdzie blokować:**

   | Etap | Co blokuje |
   |---|---|
   | PR | nowe high/critical z SAST, SCA i IaC |
   | Build | wypromowania artefaktu |
   | Release | publikacji bez podpisu i provenance |
   | Deploy | uruchomienia niezweryfikowanego artefaktu |

   Pre-commit tylko doradczo.
2. **Progi wyjściowe:** critical i high blokują, medium ostrzega (z akceptacją), low tylko się liczy. Guideline podaje je jako „typowy punkt wyjścia”, nie normę.
3. **Wdrażanie stopniowe** (najpierw ostrzeżenia, potem blokada critical, potem high) dotyczy organizacji. W eksperymencie progi są stałe przez całą serię (P1 w protokole), więc ta rada nie dotyczy pomiaru. Opisujemy ją jako rekomendację w 6.
4. **Stan bazowy** („tylko nowe zgłoszenia”): czysta wersja aplikacji nie ma zgłoszeń z katalogu, więc w eksperymencie bramka „nowe zgłoszenia” i „wszystkie zgłoszenia” daje ten sam wynik, o ile czysta wersja przechodzi bramki. TODO: zweryfikować na czystej wersji (E04, seria próbna).
5. **Wyjątki:** każdy z uzasadnieniem, właścicielem i datą wygaśnięcia. W serii eksperymentu wyjątków nie ma, bo wyjątek byłby zmianą bramki po obejrzeniu wyników (TW2).
6. **Tryb „fail closed”:**
   - brak pliku raportu → job kończy się błędem,
   - Trivy z jawnym `exit-code: 1`,
   - kod wyjścia każdego narzędzia sprawdzony w dokumentacji.

   Do tabeli bramek w E07-01.
7. **Przypinanie narzędzi bramek.** Skaner w potoku ma dostęp do sekretów joba. Przykład z Guideline to trivy-action w 2026 r.: incydent GHSA-69fq-xp46-6x23 / CVE-2026-33634 z 21.03.2026.
   - **Co dotknęło:** `trivy-action` (tagi sprzed 0.35.0), `setup-trivy` (v0.2.0–v0.2.5) i binarkę Trivy v0.69.4.
   - **Co robił złośliwy kod:** odczytywał sekrety z pamięci procesu runnera i wysyłał je na zewnątrz.
   - **Nasze wersje:** wersje w `docs/narzedzia.md` (trivy-action v0.36.0 z 2026-04-22, setup-trivy v0.3.1, Trivy v0.76.0) są późniejsze od naprawionych.
   - **Skąd dane:** porada odczytana w oryginale przez API GitHuba 2026-10-28. Incydent jest piątym studium w `incydenty.md` (3.5), klucz [@Incydent-Trivy].

---

## 2. OWASP Top 10 CI/CD Security Risks

### 2.1. Czym jest

- Lista dziesięciu ryzyk bezpieczeństwa środowisk CI/CD, przeznaczona dla obrońców. Ma pomóc wskazać obszary, na których trzeba się skupić (dok. s. 2). To model zagrożeń, a nie standard: nie ma wymagań z mocą ani procedury oceny.
- **Autorzy:** D. Krivelevich (CTO) i O. Gil (Director of Research), obaj z Cider Security. 15 recenzentów z branży (dok. s. 2).
- **Metoda** (dok. s. 3), deklarowana bez danych:
  - analiza architektury i zabezpieczeń „setek” środowisk CI/CD,
  - rozmowy z ekspertami,
  - publikacje o incydentach i lukach.
- **Układ każdego ryzyka** (dok. s. 3): definicja, opis, skutki (*impact*), rekomendacje, odniesienia do realnych przypadków.
- **Kolejność:** dokument nie twierdzi, że numeracja to ranking częstości albo wagi (dok. s. 3–4). W tekście nie traktujemy CICD-SEC-1 jako „najważniejszego”.
- **Status:** projekt OWASP w fazie Lab. Repozytorium OWASP od 2022-07, PDF z 2022-11. Później zmieniano tylko literówki i odniesienia (np. in-toto i SLSA w CICD-SEC-9, 2022-12).
- **Kontekst powstania** (dok. s. 1): rośnie liczba ataków na CI/CD (SolarWinds, Codecov, włamanie do repozytorium PHP, dependency confusion, przejęcia pakietów npm). Obrońcy są na wczesnym etapie, a zespoły szukają kontroli, które nie spowolnią inżynierii.

### 2.2. Ryzyka (notatki)

Strony według numeracji dokumentu (PDF = dok. + 1).

**CICD-SEC-1 Insufficient Flow Control Mechanisms** (dok. s. 5–7)

- **Definicja:** atakujący z uprawnieniami w jednym systemie CI/CD (SCM, CI, repozytorium artefaktów) może *samodzielnie* przepchnąć złośliwy kod lub artefakt przez potok, bo nic nie wymusza dodatkowej akceptacji lub przeglądu.
- **Przykłady skutków:**
  - push na gałąź wdrażaną automatycznie,
  - ręczne uruchomienie potoku produkcyjnego,
  - nadużycie reguły auto-merge,
  - wyłączenia z ochrony gałęzi,
  - artefakt wgrany do rejestru „pod przykrywką” artefaktu z CI,
  - zmiana bezpośrednio na produkcji (np. funkcja AWS Lambda).
- **Rekomendacje (5):**
  - ochrona gałęzi bez wyjątków,
  - ograniczone reguły auto-merge,
  - akceptacja przed uruchomieniem potoku produkcyjnego,
  - przez potok przechodzą tylko artefakty z zaufanego konta CI,
  - wykrywanie dryfu między produkcją a źródłem w CI/CD.

**CICD-SEC-2 Inadequate Identity and Access Management** (dok. s. 8–10)

- **Źródło ryzyka:** ogromna liczba tożsamości ludzkich i programowych w wielu systemach, każda z własnym sposobem nadawania, polityką i modelem uprawnień.
- **Problemy:** tożsamości nadmiernie uprzywilejowane, nieaktywne, lokalne (bez centralnego IdP), zewnętrzne (prywatne adresy e-mail, współpracownicy spoza organizacji), samorejestrowane i współdzielone.
- **Skutek:** przejęcie prawie dowolnego konta może dać przejście do produkcji.
- **Rekomendacje (9):** mapowanie tożsamości i porównanie uprawnień nadanych z używanymi, odbieranie zbędnych uprawnień, wyłączanie kont nieaktywnych, centralny IdP, uprawnienia z datą wygaśnięcia, zakaz adresów spoza domeny, zakaz samorejestracji, brak uprawnień bazowych dla wszystkich, zakaz kont współdzielonych.

**CICD-SEC-3 Dependency Chain Abuse** (dok. s. 11–13)

- **Definicja:** nadużycie sposobu, w jaki stacje robocze i środowiska buildu *pobierają* zależności. Złośliwy pakiet zostaje pobrany i uruchomiony lokalnie, często od razu przez skrypty instalacyjne.
- **Ważne rozróżnienie** (dok. s. 11): dokument oddziela to ryzyko od wykrywania pakietów ze *znanymi podatnościami*. Ryzyko dotyczy zabezpieczenia *procesu pobierania*, a nie zawartości zależności. Ma to znaczenie dla katalogu (sekcja 5).
- **Wektory:**
  - *dependency confusion* (publiczny pakiet o nazwie wewnętrznego),
  - *dependency hijacking* (przejęcie konta opiekuna i nowa złośliwa wersja),
  - *typosquatting*,
  - *brandjacking*.
- **Rekomendacje (8):**
  - pobieranie przez wewnętrzny serwer pośredniczący (*proxy*), bez bezpośredniego dostępu do internetu,
  - weryfikacja sum kontrolnych i podpisów,
  - przypięte wersje zamiast „latest”,
  - zakresy nazw (*scopes*) dla pakietów prywatnych,
  - skrypty instalacyjne w osobnym kontekście bez sekretów,
  - pliki konfiguracji menedżera pakietów w repozytorium,
  - nieujawnianie nazw projektów wewnętrznych,
  - nacisk na wykrywanie i ograniczanie szkód, bo pełne zapobieganie jest „dalekie od trywialnego”.

**CICD-SEC-4 Poisoned Pipeline Execution (PPE)** (dok. s. 14–20)

- **Definicja:** atakujący z dostępem do SCM, ale *bez* dostępu do środowiska buildu, wstrzykuje polecenia do konfiguracji potoku lub do plików, z których potok korzysta. Kod wykonuje się w kontekście tożsamości potoku.
- **Trzy odmiany** (dok. s. 14–15):
  - **D-PPE (bezpośrednia):** zmiana pliku konfiguracji CI na niechronionej gałęzi albo w PR.
  - **I-PPE (pośrednia):** konfiguracja CI jest chroniona, więc atakujący zmienia pliki, które ona wywołuje: Makefile, skrypty, testy, pliki konfiguracji linterów i skanerów.
  - **3PE (publiczna):** w repozytoriach publicznych PR może złożyć każdy, więc atak nie wymaga uprawnień w organizacji.
- **Przykład 1 dotyczy GitHub Actions i AWS** (dok. s. 16–17): nowa gałąź ze zmienionym workflow wysyła sekrety AWS na serwer atakującego. Przykład 2 to I-PPE w Jenkinsie przez Makefile (dok. s. 17–18).
- **Skutki:** dostęp do wszystkich sekretów joba, do zasobów hosta i chmury, możliwość wypuszczenia artefaktu „jako legalnego”, ruch boczny w sieci.
- **Rekomendacje (6):**
  - kod bez przeglądu na izolowanych węzłach bez sekretów,
  - ograniczenie potoków z forków albo ręczna akceptacja,
  - ochrona gałęzi dla każdej gałęzi uruchamiającej wrażliwy potok,
  - przegląd pliku CI przed uruchomieniem albo trzymanie go na chronionej gałęzi,
  - odebranie zbędnych uprawnień w SCM,
  - minimalne poświadczenia potoku.

**CICD-SEC-5 Insufficient PBAC (Pipeline-Based Access Controls)** (dok. s. 21–23)

- **Definicja:** złośliwy kod w potoku nadużywa uprawnień nadanych potokowi, żeby poruszać się w CI/CD i poza nim.
- **PBAC obejmuje** kontekst każdego potoku i kroku: dostęp do kodu, sekretów, zmiennych i innych potoków, uprawnienia do hosta i węzłów, filtry ruchu do i z internetu.
- **Skala szkód** zależy od szczegółowości PBAC (dok. s. 22).
- **Rekomendacje (8):**
  - osobne węzły dla potoków o różnej wrażliwości,
  - sekrety przypisane do potoku i kroku,
  - przywracanie czystego stanu węzła po każdym przebiegu,
  - minimalne uprawnienia użytkownika systemu,
  - ograniczone uprawnienia jobów na kontrolerze,
  - łatanie węzłów,
  - segmentacja sieci i ograniczony dostęp do internetu,
  - skrypty instalacyjne bez sekretów.

**CICD-SEC-6 Insufficient Credential Hygiene** (dok. s. 24–26)

- **Definicja:** atakujący zdobywa sekrety rozproszone w potoku przez słabą kontrolę dostępu, złe zarządzanie i nadmierne uprawnienia.
- **Typowe błędy:**
  - sekret w kodzie wypchniętym do SCM (zostaje w historii nawet po usunięciu),
  - poświadczenia w buildzie dostępne dla kodu bez przeglądu,
  - poświadczenia w warstwach obrazu,
  - poświadczenia wypisane w logach,
  - brak rotacji.
- **Rekomendacje (8):**
  - mapowanie poświadczeń i najmniejsze uprawnienia,
  - brak współdzielenia między kontekstami,
  - poświadczenia tymczasowe zamiast statycznych,
  - ograniczenie użycia do warunków (adres źródłowy, tożsamość),
  - wykrywanie sekretów w repozytorium (IDE, przy pushu, okresowo w historii),
  - sekrety przypisane do kroku,
  - blokowanie wypisywania do logów,
  - usuwanie sekretów z artefaktów.

**CICD-SEC-7 Insecure System Configuration** (dok. s. 27–29)

- **Definicja:** słabości w ustawieniach, konfiguracji i utwardzeniu systemów potoku (SCM, CI, repozytorium artefaktów).
- **Przykłady:**
  - przestarzałe wersje,
  - zbyt szeroki dostęp sieciowy,
  - system z uprawnieniami administratora do systemu operacyjnego,
  - niebezpieczne ustawienia domyślne,
  - domyślne hasła.
- **Usługi SaaS** usuwają część ryzyka (utwardzanie hostów, ruch boczny), ale nie zwalniają z konfiguracji samej usługi (dok. s. 28).
- **Rekomendacje (4):**
  - inwentarz systemów i wersji z właścicielem,
  - dostęp sieciowy według zasady najmniejszego dostępu,
  - okresowy przegląd konfiguracji,
  - najmniejsze uprawnienia do węzłów wykonawczych.

  Osobna uwaga o uprawnieniach debugowania: kto debuguje węzeł, ten widzi sekrety w pamięci.

**CICD-SEC-8 Ungoverned Usage of 3rd Party Services** (dok. s. 30–32)

- **Definicja:** dostęp usług firm trzecich do zasobów CI/CD da się nadać bardzo łatwo, co poszerza powierzchnię ataku.
- **W GitHubie** jest 5 sposobów podłączenia (dok. s. 30): GitHub App, OAuth App, token, klucz SSH, webhook.
- **W systemach buildu** wystarczą 1–2 linie konfiguracji albo wtyczka z marketplace. Przykład dokumentu: **akcje w GitHub Actions** (dok. s. 31). Kod firmy trzeciej wykonuje się z pełnym dostępem do zasobów etapu.
- **Skutek:** organizacja jest tak bezpieczna, jak firmy trzecie, które podłącza.
- **Rekomendacje (4)**, według cyklu życia integracji:
  - zatwierdzenie przed nadaniem dostępu,
  - widoczność integracji (sposób podłączenia, uprawnienia nadane i używane),
  - ograniczenie zakresu: firmy trzecie w buildzie działają w kontekście z ograniczonym dostępem do sekretów i kodu oraz z filtrami ruchu,
  - okresowe usuwanie nieużywanych.

**CICD-SEC-9 Improper Artifact Integrity Validation** (dok. s. 33–34)

- **Definicja:** atakujący z dostępem do jednego z systemów CI/CD wypycha złośliwy (pozornie nieszkodliwy) kod lub artefakt, bo brakuje mechanizmów sprawdzania integralności.
- **Rekomendacje (2):**
  1. Walidacja integralności od deweloperki do produkcji. Zasób podpisuje się przy wytworzeniu, a weryfikuje przed użyciem. Przykłady:
     - podpisy commitów,
     - oprogramowanie do podpisu i weryfikacji (Sigstore; w wersji webowej także in-toto i SLSA),
     - wykrywanie dryfu konfiguracji.
  2. Zasoby firm trzecich pobierane w potoku (np. skrypty): przed użyciem porównać hash z hashem opublikowanym przez dostawcę.
- **Odniesienie Codecov** (dok. s. 34): atak wykrył klient, który porównał hash skryptu.

**CICD-SEC-10 Insufficient Logging and Visibility** (dok. s. 35–36)

- **Definicja:** atakujący działa niewykryty na każdym etapie ataku, a po incydencie nie da się odtworzyć jego technik.
- **Logi:** potrzebne są oba rodzaje, logi audytowe systemów (dostęp, tworzenie kont, zmiany uprawnień) i logi aplikacyjne (push, buildy, wgrane artefakty).
- **Rekomendacje (4):**
  - inwentarz systemów,
  - włączenie właściwych źródeł logów (domyślnie zwykle wyłączone),
  - centralizacja (SIEM),
  - alerty o anomaliach w poszczególnych systemach i w całym procesie dostarczania.
- **Rodzaj ryzyka:** to ryzyko przekrojowe, bez listy odniesień, bo dotyczy każdego incydentu (dok. s. 36).

---

## 3. Lista ryzyk CICD-SEC z przykładem dla mojego potoku

Potok: GitHub Actions na runnerach hostowanych przez GitHub, obraz Docker w rejestrze, wdrożenie do AWS przez OIDC, repozytorium publiczne, jeden autor.

- **Pozycje katalogu:** z `experiment/ground-truth.yaml`.
- **Incydenty:** z [`incydenty.md`](incydenty.md).
- **Przypisanie incydentu do ryzyka:** według odniesień w samym Top 10 CI/CD tam, gdzie dokument je podaje. W innych przypadkach według `incydenty.md`.

Zabezpieczenia to plan wariantu B. W wariancie A ich nie ma, z wyjątkiem ustawień platformy wspólnych dla obu wariantów.

| Ryzyko | Przykład w moim potoku (scenariusz) | Zabezpieczenie w wariancie B | Katalog / incydent | SP 800-204D | Co zostaje |
|---|---|---|---|---|---|
| **CICD-SEC-1** Flow control | Ktoś z przejętym kontem autora (albo sam autor, przez pomyłkę) pushuje na `main` z pominięciem PR. Workflow wdrożeniowy wypycha zmianę do AWS bez skanów | Ruleset na `main` i `exp/variant-b`: PR wymagany, joby-bramki jako wymagane *status checks*, blokada force push, bez obejść dla administratora. Wdrożenie tylko po scaleniu i tylko obrazu z potoku | brak pozycji (w wariancie A brak bramek z założenia) | PP-AUTH*, PP-INT*, BUILD-2*, DEPLOY-REQ-3 | Brak drugiego recenzenta (projekt jednoosobowy, `docs/metodyka.md`, p. 1.5) |
| **CICD-SEC-2** IAM | Wyciek tokenu PAT autora z zakresem `repo` i `workflow`. Polityka zaufania roli IAM dla OIDC zbyt szeroka (np. dowolne repozytorium albo gałąź), więc każdy workflow może przyjąć rolę wdrożeniową | 2FA na koncie GitHub, brak długoterminowych PAT w potoku, warunek `sub` w polityce zaufania ograniczony do repozytorium i środowiska, osobna rola na środowisko, brak użytkowników IAM z kluczami | brak pozycji (kandydat rezerwowy: szeroka polityka zaufania OIDC) | PRE-2*, PRE-3*, BASE-7* | Konto autora pozostaje pojedynczym punktem awarii |
| **CICD-SEC-3** Dependency chain | Literówka w nazwie pakietu w `requirements` (typosquatting), nieprzypięta wersja pobiera świeżo przejęte wydanie, `--extra-index-url` umożliwia dependency confusion (Guideline `2-3-2-2`) | Lockfile z hashami i `--require-hashes`, dokładne wersje (P2), `dependency-review-action` na PR. Z Guideline: karencja nowych wersji w Dependabocie | xz-utils | TEST-2*, BASE-1*, BASE-4*, DEPLOY-REQ-2 | Złośliwy pakiet bez CVE przejdzie przez pip-audit i Trivy. Bez wewnętrznego proxy (lekki potok) |
| **CICD-SEC-4** PPE | **GT-17:** tytuł PR wstawiony wyrażeniem `${{ }}` do `run:` wykonuje polecenia w runnerze. D-PPE: PR zmienia workflow, żeby wysłać sekrety. I-PPE: PR zmienia testy albo konfigurację skanera (np. reguły Semgrep, `.gitleaks.toml`) i tak „wycisza” bramkę. 3PE: repozytorium jest publiczne | Workflow PR bez sekretów i bez `id-token: write`, bez `pull_request_target`, zatwierdzanie workflow od zewnętrznych współpracowników, wdrożenie tylko z chronionej gałęzi, zizmor i actionlint. Konfiguracja skanerów w ścieżkach objętych przeglądem | GT-17 | PULL-PUSH-REQ-3, PRE-5*, DEPLOY-REQ-5 | Zmiana konfiguracji skanera w PR autora nie przechodzi przeglądu przez drugą osobę |
| **CICD-SEC-5** PBAC | **GT-15:** `permissions: write-all`, więc skompromitowany krok (np. akcja zewnętrzna) może pushować do repozytorium i zmieniać wydania. `id-token: write` w jobie, który nie wdraża, pozwala każdemu krokowi uzyskać poświadczenia AWS | `permissions:` puste lub `contents: read` na poziomie workflow, uprawnienia nadawane per job, `id-token: write` tylko w jobie wdrożeniowym, sekrety środowiska `production`, efemeryczne VM, kontrola ruchu wychodzącego (harden-runner, otwarte) | GT-15; Codecov (dok. s. 23) | PRE-1*, PRE-3* | Uprawnień użytkownika systemu na runnerze hostowanym nie da się zawęzić (TODO: zweryfikować) |
| **CICD-SEC-6** Credential hygiene | **GT-02:** zakodowany klucz JWT w module konfiguracji. Sekret w `ARG`/`ENV` Dockerfile zostaje w warstwie obrazu. Sekret wypisany do logu publicznego repozytorium (jak w tj-actions). Długoterminowe klucze AWS w GitHub Secrets | Gitleaks (PR i pełna historia), secret scanning i push protection GitHuba, skan sekretów w obrazie (Trivy), OIDC zamiast kluczy (`AGENTS.md`, zasada 4), brak sekretów w argumentach buildu | GT-02; Codecov, tj-actions | COMMIT-REQ-1, COMMIT-REQ-2, DEPLOY-REQ-1 | Maskowanie sekretów w logach GitHuba da się obejść kodowaniem (tj-actions: base64) |
| **CICD-SEC-7** System config | Ustawienia repozytorium: domyślne uprawnienia `GITHUB_TOKEN` zapis i odczyt, zgoda na tworzenie i akceptowanie PR przez Actions, brak listy dozwolonych akcji. Repozytorium ECR bez niezmiennych tagów. Akcja do debugowania przez SSH w runnerze (dok. s. 28) | Spisana konfiguracja repozytorium (do E07), OpenSSF Scorecard jako miara, niezmienne tagi w rejestrze, zakaz akcji debugujących. Runnery hostowane eliminują utwardzanie własnych hostów | brak pozycji (kandydat rezerwowy: domyślne uprawnienia repozytorium); SolarWinds (dok. s. 29) | PRE-1*, BUILD-1*, PULL-PUSH-REQ-4, BASE-6* | Konfiguracja usługi SaaS jest poza kontrolą wersji w repozytorium (chyba że opiszemy ją w dokumentacji) |
| **CICD-SEC-8** 3rd party | **GT-16:** akcja zewnętrzna przez zmienny tag. Tag przestawiony na złośliwy commit wykrada sekrety (tj-actions 2025, trivy-action 2026). Skrypt pobierany `curl … \| bash` w workflow (jak Codecov). GitHub App z szerokim dostępem do repozytorium | Przypinanie do pełnego SHA (`AGENTS.md`, zasada 5), lista akcji w `docs/narzedzia.md` (p. 2) jako lista zatwierdzonych, ustawienie wymuszające SHA i lista dozwolonych akcji (TODO: zweryfikować dostępność dla konta osobistego), Dependabot dla akcji, zizmor | GT-16; tj-actions, Codecov | PULL-PUSH-REQ-2, BASE-2* | Zależności przechodnie akcji złożonych (`incydenty.md`, tj-actions) |
| **CICD-SEC-9** Artifact integrity | Obraz wypchnięty do rejestru spoza potoku (ręcznie albo z innego procesu) pod tym samym tagiem zostaje wdrożony. Wdrożenie po tagu, który ktoś przestawił | Build raz, wdrożenie po digeście (protokół, zasada 4), `attest-build-provenance` i weryfikacja atestacji przed wdrożeniem, niezmienne tagi, podpisane commity, wykrywanie dryfu (`terraform plan`) | SolarWinds, Codecov (dok. s. 34) | BUILD-3*, ATT-1*–ATT-4*, DEPLOY-REQ-3, GitOps-REQ-4 | Provenance nie wykryje złośliwego kodu dodanego w zaufanym buildzie (`incydenty.md`, SolarWinds) |
| **CICD-SEC-10** Logging | Workflow z przejętą rolą OIDC zmienia zasoby AWS. Bez CloudTrail nie ma śladu, a logi przebiegów GitHub znikają po okresie retencji | CloudTrail, logi i raporty przebiegów zapisywane jako artefakty (dane eksperymentu), alerty bezpieczeństwa GitHuba | brak pozycji | BASE-8*, ATT-3* | Bez SIEM i korelacji (lekki potok). Retencja logów GitHuba: TODO: zweryfikować |

**Wnioski do 2.2 i 4.3:**

- **Ryzyka ze scenariuszem w katalogu:** cztery (CICD-SEC-4, -5, -6, -8) mają pozycje GT, więc eksperyment zmierzy, czy wariant B je zatrzymuje.
- **Ryzyka bez pozycji w katalogu:** CICD-SEC-1, -2, -7, -9 i -10 to ryzyka konfiguracji platformy i procesu. Ocenia je lista kontrolna (C5), a nie seria skuteczności.
- **CICD-SEC-3:** w ścisłym sensie dokumentu (sposób pobierania) nie ma pozycji w katalogu (sekcja 5).

---

## 4. Rekomendacje Top 10 CI/CD jako kandydaci do listy kontrolnej (C1)

`docs/metodyka.md` (p. 1.5) przyjmuje Top 10 CI/CD jako źródło pozycji listy kontrolnej, ale wstępnie, do lektury w E02-04. Dokument ma 58 rekomendacji bez numerów. Nadajemy im własne identyfikatory `CICDn.m*`, gdzie gwiazdka oznacza identyfikator nadany w tej pracy, jak w `nist-800-204d.md`.

**Legenda:**

- **Stos.:**
  - `T`: dotyczy projektu,
  - `Cz`: dotyczy częściowo,
  - `N`: nie dotyczy, z uzasadnieniem.

  Ocena wstępna agenta.
- **SP 800-204D:**
  - `=`: ta sama treść w tabeli A lub B (pozycja nie powinna liczyć się drugi raz),
  - `≈`: częściowe pokrycie,
  - `—`: brak odpowiednika.
- **Dup.:** rekomendacja powtórzona w Top 10 CI/CD przy innym ryzyku.

| ID | Rekomendacja (streszczenie) | Dok. s. | Stos. | Realizacja (propozycja) | SP 800-204D |
|---|---|---|---|---|---|
| CICD1.1* | Ochrona gałęzi produkcyjnych bez wyłączeń. Konta z prawem pushu bez przeglądu nie uruchamiają wdrożeń | 6 | Cz | Ruleset bez obejść. Przegląd przez drugą osobę niemożliwy | = PP-AUTH*, PP-INT* |
| CICD1.2* | Ograniczyć reguły auto-merge, przejrzeć ich kod | 6 | N | Bez auto-merge w projekcie | — |
| CICD1.3* | Uruchomienie potoku produkcyjnego wymaga dodatkowej akceptacji | 6 | Cz | Środowisko `production` z wymaganym recenzentem. Recenzentem jest sam autor | ≈ BUILD-1* (c) |
| CICD1.4* | Przez potok przechodzą tylko artefakty z zaufanego konta CI | 6 | T | Weryfikacja atestacji pochodzenia przed wdrożeniem | = DEPLOY-REQ-3 |
| CICD1.5* | Wykrywać dryf między produkcją a źródłem | 6 | Cz | `terraform plan -detailed-exitcode` cyklicznie | = GitOps-REQ-4 |
| CICD2.1* | Mapować tożsamości: IdP, uprawnienia nadane i używane, dostęp programowy | 9 | T | Krótki spis tożsamości (konto autora, `GITHUB_TOKEN`, role IAM, Dependabot) w dokumentacji potoku | — |
| CICD2.2* | Odebrać zbędne uprawnienia | 9 | T | Minimalne `permissions:`, role IAM z minimalną polityką | = PRE-3* |
| CICD2.3* | Wyłączać konta nieaktywne po ustalonym okresie | 9 | N | Brak innych kont | — |
| CICD2.4* | Bez kont lokalnych, tożsamości z centralnego IdP | 10 | T | W AWS bez użytkowników IAM dla potoku, tylko rola przez OIDC | — |
| CICD2.5* | Współpracownicy zewnętrzni: najmniejsze uprawnienia, data wygaśnięcia | 10 | N | Brak współpracowników | — |
| CICD2.6* | Zakaz adresów spoza domeny organizacji | 10 | N | Projekt prywatny, brak domeny organizacji | — |
| CICD2.7* | Zakaz samorejestracji | 10 | N | GitHub SaaS, repozytorium bez członków | — |
| CICD2.8* | Bez uprawnień bazowych dla wszystkich i dużych grup | 10 | N | Brak organizacji i grup | — |
| CICD2.9* | Bez kont współdzielonych, osobne konta na kontekst | 10 | T | Osobna rola IAM na środowisko i zadanie | ≈ PRE-3* |
| CICD3.1* | Pakiety tylko przez wewnętrzny proxy, bez bezpośredniego dostępu do rejestrów publicznych | 12 | N | Sprzeczne z definicją lekkiego potoku (bez własnej infrastruktury). Do 5.3 | ≈ BASE-1* |
| CICD3.2* | Weryfikacja sum kontrolnych i podpisów pobieranych pakietów | 12 | T | `pip install --require-hashes`, obrazy po digeście | ≈ BASE-4* |
| CICD3.3* | Bez „latest”, przypięte wersje, blokada wersji | 12 | T | Lockfile, dokładne wersje (P2) | — |
| CICD3.4* | Zakresy nazw (*scopes*) dla pakietów prywatnych | 13 | N | Brak pakietów prywatnych | — |
| CICD3.5* | Skrypty instalacyjne w kontekście bez sekretów | 13 | T | Instalacja zależności w jobach bez sekretów i bez OIDC | — (Dup. CICD5.8*) |
| CICD3.6* | Konfiguracja menedżera pakietów w repozytorium | 13 | N | Tylko PyPI, bez indeksów prywatnych | — |
| CICD3.7* | Nie publikować nazw projektów wewnętrznych | 13 | N | Repozytorium publiczne z założenia | — |
| CICD3.8* | Nacisk na wykrywanie i ograniczanie szkód, utwardzenie według CICD-SEC-7 | 13 | Cz | Alerty Dependabota, SCA, kontrola ruchu wychodzącego | ≈ BASE-8* |
| CICD4.1* | Kod bez przeglądu na izolowanych węzłach bez sekretów | 19 | T | Workflow PR na efemerycznych VM, bez sekretów i OIDC | = PULL-PUSH-REQ-3 |
| CICD4.2* | Ograniczyć potoki z forków, ręczna akceptacja | 19 | T | „Require approval for all outside collaborators” | = PULL-PUSH-REQ-3 |
| CICD4.3* | Każda gałąź uruchamiająca wrażliwy potok ma ochronę | 19 | T | Wdrożenie tylko z chronionej gałęzi (warunek w workflow i w środowisku) | — |
| CICD4.4* | Przegląd pliku CI przed uruchomieniem albo plik na chronionej gałęzi | 19 | Cz | zizmor i actionlint w PR. Przegląd przez drugą osobę niemożliwy | — |
| CICD4.5* | Odebrać zbędne uprawnienia w SCM | 19 | N | Jeden użytkownik | ≈ PRE-3* |
| CICD4.6* | Potok ma tylko potrzebne poświadczenia o minimalnych uprawnieniach | 19 | T | Jak CICD5.2* | = PRE-3* |
| CICD5.1* | Bez wspólnych węzłów dla potoków o różnej wrażliwości | 22 | T | Każdy job na nowej VM | ≈ PRE-1* |
| CICD5.2* | Sekrety przypisane do potoku i kroku | 22 | T | Sekrety środowiska, uprawnienia per job (GT-15) | = PRE-3* (Dup. CICD6.6*) |
| CICD5.3* | Czysty stan węzła po każdym przebiegu | 22 | T | Runnery hostowane są efemeryczne | ≈ PRE-1* |
| CICD5.4* | Minimalne uprawnienia użytkownika systemu na węźle | 22 | Cz | Na runnerze hostowanym nie do zmiany (TODO: zweryfikować) | ≈ PRE-1* |
| CICD5.5* | Ograniczone uprawnienia jobów na kontrolerze | 22 | N | Brak własnego kontrolera (SaaS) | — |
| CICD5.6* | Łatane węzły | 22 | T | Obowiązek GitHuba (obrazy runnerów); etykieta `ubuntu-24.04` | ≈ PRE-1* |
| CICD5.7* | Segmentacja sieci, ograniczony dostęp do internetu | 22 | Cz | harden-runner w trybie audit/block (otwarte) | ≈ PRE-1*, BASE-8* |
| CICD5.8* | Skrypty instalacyjne w kontekście bez sekretów | 22 | T | Duplikat CICD3.5* | — |
| CICD6.1* | Mapować poświadczenia, najmniejsze uprawnienia | 25 | T | Spis sekretów potoku (powinien być prawie pusty dzięki OIDC) | — |
| CICD6.2* | Bez współdzielenia poświadczeń między kontekstami | 25 | T | Osobne role i środowiska | — |
| CICD6.3* | Poświadczenia tymczasowe zamiast statycznych, rotacja statycznych | 25 | T | OIDC (`AGENTS.md`, zasada 4) | — |
| CICD6.4* | Użycie poświadczeń ograniczone warunkami (adres źródłowy, tożsamość) | 25 | T | Warunki `sub` i `aud` w polityce zaufania roli | — |
| CICD6.5* | Wykrywać sekrety w repozytorium: IDE, push, okresowo z historią | 26 | T | Gitleaks w CI z pełną historią, secret scanning, push protection | = COMMIT-REQ-1, DEPLOY-REQ-1, COMMIT-REQ-2 |
| CICD6.6* | Sekrety przypisane do potoku i kroku | 26 | T | Duplikat CICD5.2* | = PRE-3* |
| CICD6.7* | Nie wypisywać sekretów do logów, sprawdzić istniejące logi | 26 | Cz | Maskowanie GitHuba, brak `echo` sekretów, przegląd logów serii próbnej | — |
| CICD6.8* | Usuwać sekrety z artefaktów (warstwy obrazu, binaria) | 26 | T | Skan sekretów obrazu (Trivy), brak sekretów w `ARG`/`ENV` | ≈ DEPLOY-REQ-4 |
| CICD7.1* | Inwentarz systemów i wersji z właścicielem, łatanie | 28 | Cz | `docs/narzedzia.md` (narzędzia i akcje). Wersji usług SaaS nie kontrolujemy | — |
| CICD7.2* | Dostęp sieciowy do systemów według zasady najmniejszego dostępu | 28 | N | Systemy potoku to SaaS | — |
| CICD7.3* | Okresowy przegląd konfiguracji systemów | 28 | T | Spisana konfiguracja repozytorium, Scorecard | = BASE-6*, ≈ PULL-PUSH-REQ-4 |
| CICD7.4* | Najmniejsze uprawnienia do węzłów, ostrożnie z debugowaniem | 28 | T | Zakaz akcji debugowania przez SSH | — |
| CICD8.1* | Zatwierdzać firmy trzecie przed nadaniem dostępu | 31 | T | Lista akcji w `docs/narzedzia.md`, p. 2. Nowa akcja wymaga wpisu i ADR albo notatki | = PULL-PUSH-REQ-2, BASE-2* |
| CICD8.2* | Widoczność integracji: sposób, uprawnienia nadane i używane | 31–32 | T | Spis akcji i GitHub Apps z uprawnieniami | — |
| CICD8.3* | Firmy trzecie w buildzie w kontekście ograniczonym (sekrety, kod, ruch sieciowy) | 32 | Cz | Akcje w jobach z minimalnymi `permissions:`, harden-runner | ≈ PRE-1*, PRE-3* |
| CICD8.4* | Okresowo usuwać nieużywane integracje | 32 | T | Przegląd listy akcji przy E07 i po eksperymencie | — |
| CICD9.1* | Podpis i weryfikacja zasobów od deweloperki do produkcji (podpisy commitów, Sigstore, wykrywanie dryfu) | 33–34 | T | Podpisane commity, atestacje, weryfikacja przed wdrożeniem, `terraform plan` | = BUILD-3*, ATT-1*–ATT-4*, DEPLOY-REQ-3, COMMIT-REQ-2, GitOps-REQ-4 |
| CICD9.2* | Zasoby firm trzecich w potoku: porównać hash z opublikowanym | 34 | T | Akcje po SHA, binaria narzędzi z weryfikacją sumy lub podpisu (TODO: sprawdzić, jak instalują je wybrane akcje) | ≈ PULL-PUSH-REQ-2 |
| CICD10.1* | Inwentarz systemów potoku | 36 | T | Spis: GitHub, rejestr obrazów, AWS | — |
| CICD10.2* | Włączyć logi audytowe i aplikacyjne, ludzi i dostępu programowego | 36 | Cz | CloudTrail, dziennik bezpieczeństwa konta GitHub (zakres dla konta osobistego: TODO: zweryfikować) | — |
| CICD10.3* | Logi w centralnym miejscu (SIEM) | 36 | N | Poza lekkim potokiem. Do 5.3 | — |
| CICD10.4* | Alerty o anomaliach | 36 | Cz | Alerty bezpieczeństwa GitHuba. Alarmy CloudTrail opcjonalnie | ≈ BASE-8* |

**Bilans:** 58 rekomendacji.

| Stosowalność | Liczba |
|---|---|
| T | 32 |
| Cz | 12 |
| N | 14 |

| Pokrycie w SP 800-204D | Liczba |
|---|---|
| `=` (ta sama treść) | 13 |
| `≈` (częściowe) | 15 |
| `—` (brak odpowiednika) | 30 |

Rekomendacji stosowalnych (T lub Cz) **bez** odpowiednika w SP 800-204D (`—`) jest 18. Po odjęciu duplikatu CICD5.8* zostaje **17 nowych pozycji listy**:

- CICD2.1*, CICD2.4*,
- CICD3.3*, CICD3.5*,
- CICD4.3*, CICD4.4*,
- CICD6.1*, CICD6.2*, CICD6.3*, CICD6.4*, CICD6.7*,
- CICD7.1*, CICD7.4*,
- CICD8.2*, CICD8.4*,
- CICD10.1*, CICD10.2*.

Liczby policzono skryptem z tabeli (2026-10-20).

**Propozycja agenta (do decyzji autora, sekcja 8):** do listy kontrolnej wchodzą rekomendacje stosowalne bez odpowiednika (`—`). Przy pozycjach SP 800-204D z oznaczeniem `=` albo `≈` dodajemy kolumnę „CICD-SEC” z identyfikatorem rekomendacji. Ta sama zasada co przy SSDF (`docs/metodyka.md`, p. 1.5): bez liczenia tego samego wymagania dwa razy. Rekomendacje N trafiają do listy z uzasadnieniem, bo kryterium C1 wymaga uzasadnienia każdej pozycji niestosowalnej. Dodatkowo w 4.3 i 5.x podajemy pokrycie według ryzyk (10 wierszy).

---

## 5. Pozycje katalogu podatności a ryzyka CICD-SEC

Pole `owasp_cicd` w `experiment/ground-truth.yaml` jest wstępne „do weryfikacji w E02-04”. Propozycje agenta po lekturze:

| Pozycja | Obecnie | Propozycja | Uzasadnienie |
|---|---|---|---|
| GT-02 zakodowany klucz JWT | CICD-SEC-6 | **bez zmian** | Pierwszy z typowych błędów: kod z poświadczeniem wypchnięty do SCM, zostaje w historii (dok. s. 24) |
| GT-07 Jinja2 ze znanymi CVE | CICD-SEC-3 | **`null`** | Dokument wprost oddziela wykrywanie pakietów ze znanymi podatnościami od nadużycia łańcucha zależności, które dotyczy *procesu pobierania* (dok. s. 11). Pozycję klasyfikuje już A03:2025 Software Supply Chain Failures |
| GT-08 nieutrzymywany obraz bazowy | CICD-SEC-3 | **`null`** | Jak GT-07: przestarzały komponent ze znanymi podatnościami, a nie złośliwa zależność ani wada pobierania. CICD-SEC-7 dotyczy systemów CI/CD, nie obrazu aplikacji |
| GT-15 `permissions: write-all` | CICD-SEC-5 | **bez zmian** | PBAC to uprawnienia nadane potokowi i krokom (dok. s. 21). Guideline (`2-3-6-3`) przypisuje „joby z większym dostępem niż potrzebny” do CICD-SEC-5. Drugorzędnie CICD-SEC-2 (nadmiernie uprzywilejowana tożsamość programowa) |
| GT-16 akcja niepinowana do SHA | CICD-SEC-3 (TODO) | **CICD-SEC-8** | Dokument podaje akcje GitHub Actions jako przykład integracji firm trzecich w buildzie (dok. s. 31). Guideline przypisuje „niezweryfikowane akcje GitHub” do CICD-SEC-8 (`2-3-6-3`) i łączy przypinanie z CICD-SEC-8 (`2-2-1-4`, „Further reading”). Drugorzędnie CICD-SEC-9, rekomendacja o hashu zasobów firm trzecich (dok. s. 34). CICD-SEC-3 opisuje menedżery pakietów i rejestry, choć wektor „dependency hijacking” jest analogiczny |
| GT-17 wstrzyknięcie przez kontekst zdarzenia | CICD-SEC-4 | **bez zmian, z uwagą** | Guideline (`2-3-6-3`) wymienia wstawianie niezaufanych wartości do `run:` jako zagrożenie PPE. W ścisłej definicji Top 10 PPE to zmiana pliku konfiguracji albo plików, z których korzysta (dok. s. 14–15). Wstrzyknięcie przez tytuł PR jest odmianą, w której atakujący kontroluje *dane*, a nie plik. Napisać to w 2.2 |
| GT-09 kontener jako root, GT-10, GT-11, rezerwowa IMDSv1 | `null` | **bez zmian** | Top 10 CI/CD dotyczy systemów i procesów CI/CD, a nie infrastruktury uruchomieniowej aplikacji. Propozycja z E02-06 (drugie pole klasyfikacji według CICD-SEC dla pozycji bez CWE na listach Top 10:2025) się nie sprawdza: dla GT-09 nie ma pasującego ryzyka |

Uzasadnienie GT-16 w katalogu odwołuje się dziś do `AGENTS.md` i [@NIST-SP800-204D]. Guideline daje bezpośrednie źródło zalecenia przypinania do SHA (`2-2-1-4`, `2-3-6-3`). SP 800-204D mówi o tym tylko pośrednio (PULL-PUSH-REQ-2, por. otwarte kwestie w `nist-800-204d.md`).

---

## 6. Porównanie dokumentów (materiał do 2.2 i 3.3)

| Cecha | DevSecOps Guideline | Top 10 CI/CD | SP 800-204D |
|---|---|---|---|
| Rodzaj | przewodnik praktyk i narzędzi | model zagrożeń (lista ryzyk) | wytyczne (rekomendacje z mocą) |
| Pytanie, na które odpowiada | co i w jakiej kolejności włączyć do potoku | co może pójść źle w samym potoku | co potok musi zapewnić, żeby łańcuch dostaw był bezpieczny |
| Przedmiot | aplikacja i potok, cały cykl życia | systemy i procesy CI/CD | łańcuch dostaw w potokach CI/CD (cloud-native) |
| Wersjonowanie | brak wydań, ciągłe zmiany | 2022, praktycznie bez zmian | wydanie final 2024 |
| Identyfikatory | brak | CICD-SEC-1…10, rekomendacje bez numerów | część rekomendacji numerowana |
| Autorzy | społeczność OWASP (Incubator) | 2 osoby z firmy dostawcy (Cider Security), 15 recenzentów | NIST |
| Rola w pracy | dobór etapów i narzędzi (C2) | model zagrożeń (2.2), pozycje listy kontrolnej (C1) | główna lista kontrolna (C1, C5) |

Dokumenty się uzupełniają:

- **Top 10 CI/CD** nazywa ryzyka, ale nie mówi, jakim narzędziem je ograniczyć.
- **Guideline** daje konkretne konfiguracje (GitHub Actions), ale bez mocy wymagań i bez listy do oceny.
- **SP 800-204D** stawia wymagania z mocą, ale bez modelu zagrożeń w postaci listy.

W 3.3 dobrze to pokazać tabelą „ryzyko → rekomendacja SP 800-204D → praktyka z Guideline”. Sekcja 3 tej notatki to jej szkic.

---

## 7. Uwagi krytyczne (materiał do 5.3)

**DevSecOps Guideline:**

1. **Brak wersji.** Treść zmienia się co kilka dni, a projekt nie publikuje wydań. Cytowanie wymaga daty dostępu i commita, a czytelnik pracy może zobaczyć inny tekst niż autor.
2. **Listy narzędzi nie są niezależnym wyborem.** Wpisy dodają kontrybutorzy, także producenci, np. commit z 2026-10-15 „add EyalSec es-python to IAST and RASP commercial tools”. Guideline nie uzasadnia doboru narzędzi w pracy, ten dobór uzasadnia E02-10.
3. **Część liczb to deklaracje producentów,** np. redukcja zgłoszeń SCA przez analizę osiągalności o „60–85%” według tego, co „producenci często podają” (`2-3-2-1 SCA`). Dokument sam zastrzega, że często cytowane proporcje kosztów naprawy przypisywane IBM mają nieweryfikowalne źródło (`0-1 Intro`). Takich liczb nie cytujemy jako faktów.
4. **Poziomy dojrzałości są ad hoc** (Starting / Developing / Maturing / Advanced, różne nazwy w różnych rozdziałach). Nie są formalnie powiązane z DSOMM ani SAMM. Nie nadają się na miarę w ewaluacji.
5. **Zakres jest szerszy niż lekki potok** (Kubernetes, ASPM, BAS, CNAPP). Praca bierze tylko część, według definicji z `docs/metodyka.md`, p. 1.1. Wybór trzeba opisać jawnie.

**Top 10 CI/CD:**

1. **Autorstwo dostawcy.** Autorzy są z firmy sprzedającej produkt do bezpieczeństwa CI/CD (dok. s. 2). Możliwy wpływ na dobór i opis ryzyk. TODO: zweryfikować dalsze losy Cider Security (przejęcie) przed wzmianką w tekście.
2. **Metoda bez danych.** Analiza „setek środowisk” jest zadeklarowana, ale niepublikowana i nieodtwarzalna (dok. s. 3). Numeracja nie jest rankingiem.
3. **Wiek.** Lista pochodzi z 2022 r. i opisuje incydenty do 2021 r. Nowsze ataki (tj-actions 2025, trivy-action 2026) mieszczą się w niej (CICD-SEC-8, -6), co przemawia za trwałością modelu. Nowszych mechanizmów, np. atestacji GitHuba, dokument nie omawia (wspomina tylko Sigstore, in-toto i SLSA).
4. **Rekomendacje pisane dla dużych organizacji:** IdP, SIEM, wewnętrzne proxy pakietów, przeglądy wielu kont. W projekcie jednoosobowym 14 z 58 jest niestosowalnych, a kilka sprzecznych z definicją lekkiego potoku (CICD3.1*, CICD10.3*). To argument za luką badawczą: brak wzorców dla małych zespołów (E02-08).
5. **Ryzyka się nakładają.** Te same rekomendacje stoją przy kilku ryzykach (skrypty instalacyjne w CICD-SEC-3 i -5, zakres sekretów w CICD-SEC-5 i -6), a jeden incydent pasuje do kilku ryzyk (Codecov: CICD-SEC-5, -6, -8, -9). Przypisanie pozycji do ryzyka bywa niejednoznaczne (GT-16), więc wybieramy ryzyko główne i to opisujemy.

---

## 8. Decyzje do podjęcia i otwarte kwestie

**Rozstrzygnięcia z 2026-10-28** (autor po lekturze opracowania, `docs/log/2026-10-28.md`):

1. Lista kontrolna: wariant (c), czyli 17 nowych pozycji. Wpisane do `docs/metodyka.md`, p. 1.5.
2. `owasp_cicd`: GT-16 → CICD-SEC-8, GT-07 i GT-08 → `null`. Wpisane do `experiment/ground-truth.yaml` (katalog v0, walidator bez błędów).
3. Do E07-01 przechodzą:
   - „fail closed” przy braku raportu i jawne kody wyjścia,
   - karencja aktualizacji w Dependabocie,
   - hook pre-commit (poza pomiarem).

   ZAP API scan z `openapi.json` **nie** przechodzi teraz (zmieniałby zasięg DAST i pułap H1). Zostaje jako możliwe rozszerzenie.
4. Incydent Trivy 2026 dodany jako piąte studium w `incydenty.md` (sekcje 1, 2 i 3.5) i w notatce źródła `Zrodla/Incydent-Trivy.md`. Porada GHSA-69fq-xp46-6x23 odczytana w oryginale (API GitHuba). Wersje zgadzają się z p. 7 w sekcji 1.5. Data 21.03.2026 w p. 7 to publikacja porady, a sam atak był 19.03.2026.

Opcje rozważane przed decyzją:

1. **Skład listy kontrolnej z Top 10 CI/CD** (sekcja 4). Opcje:
   - (a) 10 ryzyk jako pozycje,
   - (b) wszystkie 58 rekomendacji,
   - (c) **propozycja agenta:** 17 rekomendacji stosowalnych bez odpowiednika w SP 800-204D jako nowe pozycje, pozostałe jako kolumna mapowania, N z uzasadnieniem.

   Wynik wpisać do `docs/metodyka.md`, p. 1.5, bo tam ta część jest wstępna.
2. **Pole `owasp_cicd` w katalogu** (sekcja 5): GT-16 → CICD-SEC-8; GT-07 i GT-08 → `null`. Zmiana katalogu v0 przed zamrożeniem (E03-07), zapis w dzienniku.
3. **Propozycje z Guideline do projektu potoku (E07-01):**
   - karencja aktualizacji w Dependabocie,
   - „fail closed” przy braku raportu i jawne kody wyjścia,
   - ZAP API scan z `openapi.json` (zmienia zasięg DAST, więc może zmienić pułap H1; decyzja przed zamrożeniem metodyki),
   - hook pre-commit (poza pomiarem).
4. **Incydent trivy-action 2026 jako piąte studium w `incydenty.md`?**
   - **Za:** dotyczy narzędzia z własnego potoku i pokazuje, że skaner bezpieczeństwa sam jest wektorem ataku.
   - **Przeciw:** E02-12 jest zamknięte z czterema incydentami.

Otwarte kwestie:

- ~~TODO: zweryfikować w oryginale GHSA-69fq-xp46-6x23 (daty, wersje) przed cytowaniem.~~ Zrobione 2026-10-28: atak 19.03.2026, Trivy v0.69.4, `trivy-action` < 0.35.0, `setup-trivy` < 0.2.6, CVE-2026-33634 (KEV od 26.03.2026). Cytować kluczem [@Incydent-Trivy].
- TODO: zweryfikować ustawienia GitHuba wymienione w sekcjach 3–4 dla repozytorium na koncie osobistym:
  - wymuszanie przypinania do SHA i lista dozwolonych akcji,
  - zakaz samoakceptacji w środowiskach,
  - dziennik bezpieczeństwa konta,
  - retencja logów,
  - dostęp do sekretów w PR z gałęzi tego samego repozytorium.
- `AGENTS.md`, zasada 5, przypisuje przypinanie do SHA wprost SP 800-204D. Lepiej dopisać [@OWASP-DevSecOps-Guideline] jako bezpośrednie źródło, a SP 800-204D zostawić jako interpretację PULL-PUSH-REQ-2.
- `incydenty.md`, sekcja 1: Top 10 CI/CD przypisuje Codecov także do CICD-SEC-5 (dok. s. 23). Można dopisać, autor przyjął mapowanie bez tego.
- Guideline cytujemy z commitem `a2cd4f9`. Przed oddaniem pracy sprawdzić, czy cytowane rozdziały nie zmieniły się istotnie.
