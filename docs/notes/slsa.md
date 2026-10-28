# SLSA v1.2: notatki z lektury i ocena poziomu Build

- **Źródło:** [@SLSA-1.2], *SLSA specification, Version 1.2*, OpenSSF, listopad 2025, https://slsa.dev/spec/v1.2/ (dostęp 2026-10-28).
- **Zadanie:** E02-05 (tablica zadań). Używane w rozdz. 3 i 4.3, w hipotezie H3b i metryce M8 (`docs/metodyka.md`).
- **Wersja i status:** v1.2 ma status *Approved*, czyli stabilny (strona slsa.dev/spec/v1.2/, `spec-stages`). Ogłoszono ją 2025-11-24. Według ogłoszenia jest wstecznie zgodna z v1.1. Notatki oparto na tekście z gałęzi `releases/v1.2` repozytorium `slsa-framework/slsa` (commit `ae7fc76`, 2026-04-14, poprawki redakcyjne po wydaniu; tag `v1.2` to `19e4e2f`). Gałąź `main` zawiera już *Working Draft* następnej wersji. Ten szkic opisuje m.in. ścieżki Build Environment i Dependency i nie jest tu cytowany.
- **Jak wskazywać miejsca:** specyfikacja jest serwisem HTML bez numerów stron. Miejsca podaję jako `strona#kotwica`, np. `build-requirements#isolated` oznacza https://slsa.dev/spec/v1.2/build-requirements#isolated.
- **Stan lektury:** TODO: autor potwierdza. Notatki przygotował agent (Claude Code) na podstawie tekstu specyfikacji. Pytania kontrolne są w `docs/notes/slsa-pytania.md`.

## Jak czytać ten plik

1. Sekcja 1 zawiera notatki z części specyfikacji potrzebnych w pracy.
2. Sekcja 2 to tabela wymagań ścieżki Build L1–L3 z propozycją dowodu dla M8.
3. Sekcja 3 przenosi wymagania na GitHub Actions.
4. Sekcja 4 to wstępna ocena docelowego poziomu, czyli kryterium 2 zadania.
5. Sekcje 5–7 zawierają powiązania z SP 800-204D, SSDF i OWASP, uwagi krytyczne i otwarte kwestie.

Kolumny „Realizacja” i „Dowód” to **propozycje agenta**, nie decyzje. Docelowy poziom wybiera autor (sekcja 4).

---

## 1. Notatki z części specyfikacji

### Czym jest SLSA (`about`, `principles`)

- SLSA (*Supply-chain Levels for Software Artifacts*, wym. „salsa”) to zbiór wytycznych bezpieczeństwa łańcucha dostaw, które można wdrażać stopniowo. Specyfikacja określa je jako „ustalone konsensusem branżowym” (`about#what-is-slsa`). Jest projektem OpenSSF (README repozytorium).
- Specyfikacja deklaruje cztery zastosowania: wspólne słownictwo, ocenę artefaktów, które się konsumuje, listę kontrolną dla własnego oprogramowania i sposób mierzenia zgodności z SSDF (`about#what-is-slsa`). Ostatnie łączy SLSA z [@NIST-SP800-218].
- **Uzasadnienie (`about#why-slsa-is-needed`):** jako przykłady podano SolarWinds i Codecov. Teza: skanowanie kodu źródłowego nie wystarcza, bo kod może się zmienić między skanem a binarium. SLSA ma zwiększyć pewność, że analiza kodu źródłowego „nadal dotyczy” binarium po buildzie i dystrybucji. To dobry argument do rozdz. 1 i 2.2: skanery z potoku B mają sens tylko wtedy, gdy wdrożony artefakt pochodzi z przeskanowanego kodu.
- **Czego SLSA nie obejmuje (`about#what-slsa-doesnt-cover`):**
  - jakości kodu i bezpiecznego programowania (to zadanie SAST/SCA),
  - zaufania do producenta,
  - zależności przechodnich, bo poziom artefaktu nie zależy od poziomu jego zależności (`faq#q-why-is-slsa-not-transitive`).
- **Zasady (`principles`):**
  - „ufaj platformom, weryfikuj artefakty”: zaufanie ogranicza się do małej liczby utwardzonych platform, a weryfikację artefaktów się automatyzuje,
  - minimalizacja liczby zaufanych platform,
  - „ufaj kodowi, nie ludziom”: wszystko ma być śledzalne do kodu źródłowego,
  - atestacje zamiast wnioskowania.

### Ścieżki i poziomy (`tracks`, `build-track-basics`)

- W v1.2 są dwie ścieżki (*tracks*): **Build** (L0–L3) i **Source** (L1–L4, nowość v1.2). Każda ma własne poziomy, wymagania i zagrożenia.
- Ścieżka Build opisuje rosnącą wiarygodność i kompletność **provenance** (pochodzenia) artefaktu. Jej celem jest umożliwienie **weryfikacji**, że artefakt zbudowano zgodnie z oczekiwaniami (`tracks#build-track`).
- Poziomy Build (`build-track-basics`):

| Poziom | Wymaganie (skrót) | Przed czym chroni | Dla kogo według specyfikacji |
|---|---|---|---|
| L0 | brak | — | buildy deweloperskie i testowe na tej samej maszynie |
| L1 | provenance istnieje | pomyłki, dokumentacja; provenance „trywialna do obejścia lub sfałszowania” | szybki start bez zmiany procesu buildu |
| L2 | podpisane provenance z **hostowanej** platformy budowania | manipulacja **po** buildzie | umiarkowana ochrona przez przejście na platformę hostowaną |
| L3 | **utwardzona** platforma budowania | manipulacja **w trakcie** buildu | „większość wydań oprogramowania”; zwykle wymaga istotnych zmian platformy |

- Przy L2 fałszerstwo wymaga jawnego „ataku”, choć może być łatwe. Odstrasza przeciwników, którzy ponoszą ryzyko prawne lub finansowe, np. pracowników. Przy L3 wymaga wykorzystania podatności, która przekracza możliwości większości przeciwników (`build-track-basics#build-l2`, `#build-l3`).
- Poprzednia numeracja SLSA 1–4 (v0.1) obejmowała źródło i build razem. W v1.0 usunięto część dotyczącą źródła, a v1.2 przywraca ją jako osobną ścieżkę Source (`build-track-basics`, uwaga pod tabelą). W literaturze i blogach spotyka się jeszcze dawne „SLSA 4”, które nie odpowiada „Build L4”.

### Model buildu i role (`terminology#build-model`, `terminology#roles`)

- **Role:** producent (*producer*), weryfikator (*verifier*), konsument (*consumer*) i dostawca infrastruktury. Jedna osoba może pełnić kilka ról. W tym projekcie autor jest producentem i weryfikatorem (job wdrożeniowy).
- **Model:**
  1. Najemca (*tenant*) wywołuje build, podając **parametry zewnętrzne** (*external parameters*).
  2. **Płaszczyzna sterowania** (*control plane*) platformy interpretuje parametry, pobiera zależności, tworzy **środowisko buildu** i uruchamia kroki.
  3. Kroki buildu kontroluje najemca, a platforma izoluje od siebie środowiska. Stopień tej izolacji mierzy poziom Build.
  4. Od L2 płaszczyzna sterowania wydaje provenance.
- Model nie ma osobnego pojęcia „źródła”. Odwołanie do repozytorium jest parametrem zewnętrznym, a samo repozytorium jest zależnością.
- Pojęcia, które trzeba rozróżniać w tekście pracy:
  - *platforma* (cała zaufana całość: oprogramowanie, sprzęt, ludzie, organizacje),
  - *administrator*,
  - *najemca* (traktowany jako niezaufany),
  - *płaszczyzna sterowania*,
  - *środowisko buildu*,
  - *cache buildu*.
- Terminu *builder* specyfikacja unika jako niejednoznacznego. Wyjątkiem jest pole `builder.id` w provenance.

### Wymagania (`build-requirements`)

- Odpowiedzialność jest podzielona: **platforma** wzmacnia zabezpieczenia, a **producent** wybiera platformę zdolną do osiągnięcia danego poziomu i stosuje zabezpieczenia, które ta platforma zaleca (`build-requirements#build-levels`).
- Wszystkie implementacje MUSZĄ stosować „najlepsze praktyki branżowe”: kontrolę dostępu, bezpieczną komunikację, zarządzanie sekretami kryptograficznymi, aktualizacje i łatanie. Przykładem odniesienia są CIS Controls (`#security-best-practices`). Wymaganie jest ogólne i nie da się go sprawdzić wprost.
- Wymagania wobec producenta są celowo skromne. Te z v0.1 (np. *scripted build*) usunięto w v1.0 i mogą wrócić (`#producer`).
- Integralność provenance ma trzy wymiary: **kompletność**, **autentyczność** i **dokładność** (`#provenance-generation`).
- Pełna lista wymagań jest w sekcji 2.
- **Uwaga do dokumentacji GitHuba:** GitHub odwołuje się do SLSA v1.0. Agent porównał linie normatywne (MUST/SHOULD/MAY) sekcji „Build Platform” w v1.0 i v1.2 i są identyczne. Według stron „What's new” zmiany v1.1 dotyczą VSA i modelu zagrożeń, a v1.2 ścieżki Source. Twierdzenia GitHuba o poziomach można więc odnosić do v1.2.

### Format provenance (`build-provenance`, `attestation-model`)

- Zalecany format to predykat SLSA Provenance (`predicateType: https://slsa.dev/provenance/v1`) w ramach in-toto attestation. Inny format MUSI zawierać równoważne informacje (`build-requirements#provenance-exists`).
- Struktura (`build-provenance#model`):
  - `buildDefinition`:
    - `buildType`: szablon procesu,
    - `externalParameters`: niezaufane, MUSZĄ być w provenance i MUSZĄ być weryfikowane,
    - `internalParameters`: ustawia platforma, są opcjonalne i zaufane,
    - `resolvedDependencies`: kompletność „best effort”,
  - `runDetails`:
    - `builder.id`: tożsamość platformy jako przechodniego domknięcia zaufanych podmiotów,
    - `metadata`,
  - `subject`: artefakty identyfikowane digestem.
- Dla GitHub Actions istnieje typ buildu `github-actions-buildtypes/workflow/v1`, utrzymywany przez społeczność (`build-provenance#index-of-build-types`). Akcja `actions/attest` używa typu `https://actions.github.io/buildtypes/workflow/v1` (sekcja 3.1).

### Dystrybucja provenance (`distributing-provenance`)

- Producent MUSI opublikować atestacje w co najmniej jednym miejscu i POWINIEN w kilku (`#where-attestations-are-published`). Możliwe miejsca:
  - przy wydaniu w repozytorium źródłowym,
  - obok artefaktu w rejestrze pakietów (*sidecar*),
  - gdziekolwiek indziej, z wpisem w logu przejrzystości (np. Rekor).
- Docelowo rejestry POWINNY przechowywać provenance obok artefaktu: klient i tak ufa rejestrowi i i tak jest od niego zależny.
- Atestacje POWINNY być niezmienne. Nowe provenance oznacza nowe wydanie (`#immutability-of-attestations`).

### Weryfikacja (`verifying-artifacts`)

- Provenance „nic nie daje, dopóki ktoś jej nie sprawdzi” (wstęp strony). To ta sama teza co „teatr bezpieczeństwa” w OWASP DevSecOps Guideline (`owasp-devsecops.md`, pkt 8).
- **Krok 1: poziom Build.** Weryfikator ma skonfigurowane korzenie zaufania (*roots of trust*), czyli mapę: tożsamość klucza i `builder.id` → maksymalny poziom, do którego ufa danemu builderowi. Następnie:
  1. sprawdza podpis koperty,
  2. sprawdza, czy `subject` odpowiada digestowi artefaktu,
  3. sprawdza, czy `predicateType` to `https://slsa.dev/provenance/v1`,
  4. odczytuje poziom z mapy, domyślnie L1.
- **Krok 2: oczekiwania.** Weryfikator POWINIEN porównać z wartościami oczekiwanymi co najmniej:
  - tożsamość buildera,
  - kanoniczne repozytorium źródłowe,
  - `buildType`,
  - `externalParameters`.

  Nierozpoznane parametry zewnętrzne POWINNY powodować odrzucenie.
- **Krok 3 (opcjonalny):** rekurencyjne sprawdzenie zależności, np. przez VSA.
- **Gdzie weryfikować:** w ekosystemie pakietów przy publikacji (RECOMMENDED), u konsumenta przy instalacji lub wdrożeniu albo w monitorze. Co najmniej jedno z tych miejsc POWINNO być użyte. W projekcie weryfikuje konsument, czyli job wdrożeniowy przed deployem (E07-09).
- **Zastrzeżenie:** L3 **nie** chroni przed kompromitacją samej platformy budowania, np. przez złośliwego pracownika dostawcy. Wybór platform zaufanych to decyzja weryfikatora (`verifying-artifacts#step-1-check-slsa-build-level`, `assessing-build-platforms`).

### Zagrożenia (`threats`)

- Model zagrożeń dzieli łańcuch na etapy (A)–(I):
  - **źródło:** (A) producent, (B) modyfikacja źródła, (C) system kontroli wersji,
  - **build:** (D) parametry zewnętrzne, (E) proces buildu, (F) publikacja artefaktu, (G) kanał dystrybucji,
  - **użycie:** (H) wybór pakietu, (I) użycie,
  - osobno zagrożenia zależności, dostępności i weryfikacji.
- Zagrożenia buildu ważne dla projektu:
  - **(D) parametry zewnętrzne:** build z nieoficjalnego forka, gałęzi, kroków albo parametrów, np. z innego workflow (`debug.yml` zamiast `release.yml`) albo z `github.event.inputs`. Środek zaradczy: porównanie provenance z oczekiwaniami. Wystarcza do tego L1.
  - **(E) proces buildu:**
    - fałszowanie provenance (L2+),
    - kompromitacja właściciela projektu (L2+),
    - wpływ jednego buildu na inny (L3),
    - kradzież sekretów kryptograficznych (L3),
    - **zatrucie cache buildu** (L3),
    - kompromitacja administratora platformy (tylko przez wybór zaufanej platformy).

    Specyfikacja nie uważa za problem fałszywego digestu wyjścia (`threats#forged-digest`): weryfikator i tak odrzuci artefakt, jeśli nie zgadza się źródło.
  - **(F) publikacja:**
    - build w niezaufanym CI/CD (oczekiwania),
    - artefakt bez provenance (L1),
    - modyfikacja artefaktu po CI/CD (L1, porównanie `subject` z hashem),
    - modyfikacja provenance (L2, podpis).

    Ten ostatni przykład w specyfikacji dotyczy wprost GitHub Actions: build z `evil/my-package` z przerobionym provenance (`threats#f-artifact-publication`).
  - **(G) kanał dystrybucji:** środki jak przy (F), ale weryfikację wykonuje konsument.

### FAQ: SBOM i runnery samohostowane (`faq`)

- **SBOM a provenance** (`faq#q-how-does-slsa-and-slsa-provenance-relate-to-sbom`):
  - SBOM opisuje drobnoziarniście, z czego artefakt się składa (podatności, licencje),
  - provenance opisuje gruboziarniście, jak go zbudowano,
  - obecne formaty SBOM uznano za nieodpowiednie dla ścieżki Build,
  - provenance może zwiększyć wiarygodność SBOM, bo opisuje, jak SBOM powstał.

  Uzasadnia to w pracy obecność obu mechanizmów (E07-08 i E07-09) i odpowiada luce z SP 800-204D (1.2, 6).
- **Runnery samohostowane** (`faq#q-how-to-slsa-with-a-self-hosted-runner`): wymagania poziomu dotyczą przechodniego domknięcia systemów, które wpływają na provenance. Jeśli runner współtworzy provenance, wymagania obejmują też runner. Projekt używa tylko runnerów hostowanych przez GitHub.

### Kierunki rozwoju (`future-directions`)

- Ewentualny Build L4 może obejmować przypięte zależności, buildy hermetyczne, pełną listę zależności w provenance i buildy odtwarzalne. Specyfikacja zastrzega, że te wymagania „mogą, ale nie muszą” się w nim znaleźć.
- Przypinanie wersji (AGENTS.md, konwencja 6) wykracza więc poza wymagania L3. Można je opisać jako krok w stronę przyszłego L4. W pracy trzeba to podać ostrożnie, bo L4 nie istnieje.

### Ścieżka Source (`source-requirements`), tylko tło

- Poziomy:
  - L1: system kontroli wersji,
  - L2: ciągła, niezmienna historia i *Source Provenance* dla każdej rewizji,
  - L3: ciągłe egzekwowanie kontroli technicznych na chronionych referencjach,
  - L4: przegląd przez dwie zaufane osoby.
- Już od L1 system kontroli wersji MUSI wydawać *Source VSA* (`source-requirements#source-summary`). Bez VSA rewizja ma Source L0. GitHub nie wydaje VSA natywnie. Specyfikacja jako przykład podaje narzędzie `slsa-source-poc` (`verifying-source`). Czy GitHub ma dziś natywne wsparcie: TODO: zweryfikować.
- **Wniosek:** ścieżka Source jest poza zakresem oceny (M8 dotyczy tylko Build). Source L4 jest nieosiągalny w projekcie jednoosobowym, bo wymaga dwóch recenzentów. Do pracy (3.x) wystarczy wzmianka, że ścieżka istnieje, i uzasadnienie, dlaczego jej nie oceniamy.

---

## 2. Tabela wymagań ścieżki Build (lista do M8)

Oznaczenia: P = producent, PB = platforma budowania, K = konsument (weryfikator). „Hostowane GH” mówi, czy wymaganie spełniają same runnery hostowane i `actions/attest` bez dodatkowej konfiguracji.

| ID | Wymaganie | Kto | Stopień | L1 | L2 | L3 | Miejsce w specyfikacji | Hostowane GH | Realizacja w projekcie (propozycja) | Dowód do M8 (propozycja) |
|---|---|---|---|---|---|---|---|---|---|---|
| SLSA-0 | Najlepsze praktyki bezpieczeństwa (dostęp, komunikacja, sekrety, aktualizacje) | P, PB | MUST | ✓ | ✓ | ✓ | `build-requirements#security-best-practices` | n/d | Sprawdza się pośrednio przez listę kontrolną M7 (800-204D, CICD-SEC) | odsyłacz do M7 |
| SLSA-P1 | Wybór platformy zdolnej do docelowego poziomu | P | MUST | ✓ | ✓ | ✓ | `#choose-an-appropriate-build-platform` | tak (L2 według GitHuba, L3 z reusable workflow) | GitHub Actions, runnery hostowane | ADR potoku, dokumentacja GitHuba |
| SLSA-P2 | Spójny proces buildu, na podstawie którego weryfikator może ustalić oczekiwania | P | MUST | ✓ | ✓ | ✓ | `#follow-a-consistent-build-process` | nie (zależy od producenta) | Jeden workflow wydania, wyzwalany z `main` lub tagu | plik workflow, `externalParameters.workflow` w provenance |
| SLSA-P3 | Dystrybucja provenance do konsumentów | P | MUST | ✓ | ✓ | ✓ | `#distribute-provenance`, `distributing-provenance` | częściowo (API atestacji GitHuba, Rekor dla repozytoriów publicznych) | Dodatkowo `push-to-registry: true` (atestacja w rejestrze OCI obok obrazu) | wpis w API atestacji, wpis w Rekorze, referrer w rejestrze (ECR: TODO: zweryfikować) |
| SLSA-B1 | Provenance istnieje, identyfikuje artefakt digestem i opisuje proces | PB | MUST | ✓ | ✓ | ✓ | `#provenance-exists` | tak | `actions/attest` z `subject-digest` obrazu | `gh attestation verify` (domyślnie wymaga predykatu SLSA v1) |
| SLSA-B2 | Provenance autentyczne: podpis, generowane przez płaszczyznę sterowania, dane z platformy | PB | MUST (podpis: SHOULD) | | ✓ | ✓ | `#provenance-authentic` | tak (Sigstore, certyfikat Fulcio z tożsamością workflow z tokenu OIDC; dane predykatu z podpisanych claimów OIDC) | bez zmian | weryfikacja podpisu i certyfikatu przez `gh attestation verify` |
| SLSA-B3 | Provenance niepodrabialne: sekret podpisujący niedostępny dla kroków użytkownika; każde pole generowane lub sprawdzane przez platformę; parametry zewnętrzne w pełni wyliczone | PB | MUST | | | ✓ | `#provenance-unforgeable` | **nie w jednym jobie** (sekcja 3.3) | Osobny job (i najlepiej reusable workflow) do atestacji, bez `id-token: write` w jobie buildu; wydanie bez `inputs` i `vars` | struktura workflow, `builder.id` = reusable workflow, test negatywny |
| SLSA-B4 | Platforma hostowana (nie stacja robocza) | PB | MUST | | ✓ | ✓ | `#hosted` | tak (GitHub Actions jako przykład w specyfikacji) | runnery hostowane | `internalParameters.github.runner_environment` = `github-hosted`, flaga `--deny-self-hosted-runners` |
| SLSA-B5a | Build nie ma dostępu do sekretów platformy (klucz podpisu provenance) | PB | MUST | | | ✓ | `#isolated` | jak SLSA-B3 | jak SLSA-B3 | jak SLSA-B3 |
| SLSA-B5b | Buildy równoległe nie wpływają na siebie | PB | MUST | | | ✓ | `#isolated` | tak, z wyjątkiem runnerów jednoprocesorowych (kontener na współdzielonej VM) | etykieta runnera z osobną VM | etykieta `runs-on` w workflow |
| SLSA-B5c | Efemeryczne środowisko dla każdego buildu | PB | MUST | | | ✓ | `#isolated` | tak (nowa VM na każdy job, z tym samym wyjątkiem) | jak wyżej | dokumentacja GitHuba, `runs-on` |
| SLSA-B5d | Brak zatrucia cache: wynik identyczny z cache i bez niego | PB | MUST | | | ✓ | `#isolated`, `threats#e-build-process` | niepewne, zależy od użycia `actions/cache` i cache BuildKit `type=gha` (TODO: zweryfikować zasady zakresu cache) | build wydania bez cache albo uzasadnienie zakresu cache | workflow bez `cache-from`/`actions/cache` w jobie wydania |
| SLSA-B5e | Brak usług pozwalających na zdalny wpływ, chyba że ujęte w `externalParameters` | PB | MUST | | | ✓ | `#isolated` | tak, przy braku narzędzi debugowania typu SSH w jobie | żadnych akcji zdalnego dostępu do runnera | przegląd workflow (zizmor/actionlint) |
| SLSA-K1 | Konsument sprawdza autentyczność provenance | K | wymóg L2 (`build-track-basics`) | | ✓ | ✓ | `build-track-basics#build-l2` | nie (trzeba wywołać) | `gh attestation verify oci://…@sha256:…` w jobie deploy, *fail closed* | log joba, test negatywny (E07-09) |
| SLSA-K2 | Sprawdzenie oczekiwań: builder, repozytorium, `buildType`, `externalParameters`; odrzucanie nierozpoznanych parametrów | K | SHOULD | ✓ | ✓ | ✓ | `verifying-artifacts#step-2-check-expectations` | częściowo (`--repo`, `--signer-workflow`, `--source-ref`; `gh` nie odrzuca nierozpoznanych parametrów) | flagi `--repo`, `--signer-workflow`, `--source-ref refs/heads/main`; ewentualnie kontrola JSON z `--format json` | polecenie weryfikacji i jego wynik |

---

## 3. Przeniesienie na GitHub Actions

### 3.1. Co zapisuje `actions/attest`

Źródło: `packages/attest/src/provenance.ts` w `actions/toolkit` (gałąź `main`, odczyt 2026-10-28).

- **Treść predykatu:** cały predykat powstaje z claimów tokenu OIDC wydanego przez GitHub:
  - `buildType` = `https://actions.github.io/buildtypes/workflow/v1`,
  - `externalParameters.workflow` = `{ref, repository, path}`,
  - `internalParameters.github` = `{event_name, repository_id, repository_owner_id, runner_environment}`,
  - `resolvedDependencies` = tylko commit repozytorium,
  - `builder.id` = `github.server_url` + `job_workflow_ref`, czyli **ścieżka workflow, który wykonał atestację**; przy reusable workflow jest to reusable workflow,
  - `invocationId` = identyfikator przebiegu i próby.
- **Konsekwencje:**
  - **L2 (autentyczność, dokładność):** dane provenance pochodzą od platformy (claimy OIDC podpisane przez GitHub), a nie od kroków użytkownika. Spełnia to warunek „generator czyta dane bezpośrednio z platformy” (`build-requirements#provenance-authentic`).
  - **L3 (kompletność):** `externalParameters` **nie zawiera** `inputs` ani `vars`, choć typ buildu społeczności je przewiduje. Jeśli workflow wydania przyjmuje `workflow_dispatch.inputs` albo czyta `vars`, parametry zewnętrzne nie są „w pełni wyliczone” (`#provenance-unforgeable`). To także zagrożenie (D), przykład 2. **Wniosek (agent):** workflow wydania bez `inputs` i bez `vars` wpływających na build.
  - `resolvedDependencies` nie wylicza zależności aplikacji ani obrazu bazowego. Według SLSA jest to dopuszczalne (best effort), a zależności dokumentuje SBOM (sekcja 1, FAQ).
- **Akcje:** od v4 `actions/attest-build-provenance` jest tylko nakładką na `actions/attest`. README zaleca `actions/attest` w nowych wdrożeniach. Dokumentacja GitHuba używa w przykładach `actions/attest@v4`. W `docs/narzedzia.md` obie akcje są przypięte w v4.2.2.
- **Podpis:** krótkotrwały certyfikat Sigstore (Fulcio) wiąże klucz efemeryczny z tożsamością workflow. Repozytoria publiczne używają instancji Public Good z wpisem w publicznym logu przejrzystości, a prywatne instancji GitHuba bez logu (dokumentacja GitHuba „Artifact attestations”). Repozytorium jest publiczne (ADR 0004), więc atestacje trafiają do Rekora.

### 3.2. Build L2 na runnerach hostowanych

- GitHub deklaruje: same artifact attestations dają „SLSA v1.0 Build Level 2” (dokumentacja „Artifact attestations”, sekcja „SLSA levels for artifact attestations”).
- Według tabeli z sekcji 2:
  - SLSA-B1, -B2 i -B4 spełniają runnery hostowane i `actions/attest`,
  - SLSA-P2 i -P3 zależą od konfiguracji producenta, ale są proste,
  - SLSA-K1 wymaga kroku weryfikacji przed deployem (zaplanowany w E07-09).
- **Ocena (agent):** L2 jest osiągalny małym kosztem. Wymaga trzech uprawnień (`id-token: write`, `attestations: write`, `contents: read`; do rejestru także `packages: write`), jednego kroku atestacji i jednego kroku weryfikacji.

### 3.3. Build L3: co trzeba zmienić i gdzie jest problem

- GitHub deklaruje L3 przy atestacji z **reusable workflow** i weryfikacji przez `--signer-workflow` albo `--signer-repo` (dokumentacja „Using artifact attestations and reusable workflows to achieve SLSA v1 Build Level 3”). Uzasadnienie GitHuba: reusable workflow to „znane, sprawdzone instrukcje buildu” i zapewnia izolację od workflow wywołującego.
- **Problem w jednym jobie (analiza agenta, do weryfikacji):** uprawnienie `id-token: write` dotyczy całego joba. Każdy krok joba, także krok buildu albo akcja zewnętrzna, może pobrać token OIDC i podpisać przez Fulcio dowolne provenance z tą samą tożsamością workflow. Narusza to SLSA-B3 i -B5a: sekret uwierzytelniający provenance jest dostępny dla kroków użytkownika. Dlatego `slsa-github-generator` dzieli reusable workflow na osobne joby (osobne VM): build i generowanie provenance. Digest przekazuje między nimi przez wyjścia jobów, czyli zaufany kanał (SPECIFICATIONS.md generatora, „Trusted builder and provenance generator”).
- **Problem zaufania w projekcie jednoosobowym (analiza agenta):**
  - L3 zakłada, że płaszczyzna sterowania jest poza kontrolą najemcy (`terminology#build-model`).
  - W `slsa-github-generator` rolę zaufanego buildera pełni reusable workflow utrzymywany przez osobny projekt.
  - Tutaj autor pisze i workflow wywołujący, i reusable workflow, więc rozdział „najemca – platforma” jest umowny. Argument GitHuba („współdzielony przez wiele repozytoriów organizacji, sprawdzony”) ma tu słabsze oparcie.
  - Twierdzenie „L3” będzie więc twierdzeniem „L3 według interpretacji GitHuba, z zastrzeżeniem”. TODO: zweryfikować, czy w literaturze lub dyskusjach SLSA (issues `slsa-framework/slsa`) jest stanowisko w tej sprawie.
- **`slsa-github-generator`:** według README (stan 2026-10-28) projekt „nie jest już aktywnie utrzymywany”. Ostatnie wydanie to v2.1.0 z lutego 2025. Projekt sam zaleca artifact attestations GitHuba. Generator odpada więc jako ścieżka do L3 (wymóg aktualności narzędzi, AGENTS.md).
- **Minimalny projekt L3 (propozycja do E07-09):**
  1. Build obrazu w osobnym jobie **bez** `id-token: write`, wynik to digest (wyjście joba).
  2. Atestacja w osobnym jobie reusable workflow (np. `.github/workflows/attest.yml`, `on: workflow_call`) z `id-token: write` i `attestations: write`. Przyjmuje tylko nazwę i digest obrazu.
  3. Workflow wydania bez `workflow_dispatch.inputs` i bez `vars` wpływających na build (SLSA-B3, kompletność).
  4. Brak cache w jobie wydania albo udokumentowany zakres cache (SLSA-B5d).
  5. Runnery z osobną VM, bez etykiet jednoprocesorowych (SLSA-B5b, -B5c; TODO: zweryfikować etykiety w „GitHub-hosted runners reference”).
  6. Weryfikacja przed deployem:

     `gh attestation verify oci://<rejestr>/<obraz>@sha256:<digest> --repo <właściciel>/praca-magisterska-devsecops --signer-workflow <właściciel>/praca-magisterska-devsecops/.github/workflows/attest.yml --source-ref refs/heads/main --deny-self-hosted-runners`

     Flagi według `gh` v2.103.3. Uwaga: przy `--bundle-from-oci` `gh` porównuje `--repo` tylko z nazwą repozytorium i właściciela (pomoc polecenia).
  7. Test negatywny: obraz bez atestacji albo z atestacją z innego workflow jest odrzucany (kryterium E07-09).

### 3.4. Gdzie weryfikować

- Projekt weryfikuje w jobie wdrożeniowym tego samego potoku. Według SLSA weryfikacja przez konsumenta jest dozwolona (`verifying-artifacts#consumer`).
- **Ograniczenie (agent):** ktoś, kto kontroluje definicję potoku, może też usunąć krok weryfikacji. Silniejsze warianty wykraczają poza zakres:
  - weryfikacja po stronie AWS przed uruchomieniem obrazu (np. kontrola dopuszczenia),
  - weryfikacja w osobnym, chronionym workflow wdrożeniowym ze środowiskiem GitHub i wymaganymi recenzentami.

  Warto to opisać w 5.3 jako ograniczenie. Odpowiada to ATT-4* z SP 800-204D (brak podpisanej polityki, `nist-800-204d.md`).

---

## 4. Wstępna ocena docelowego poziomu (kryterium 2)

**Stan wiedzy:** L1 i L2 są osiągalne na runnerach hostowanych małym kosztem. L3 jest osiągalny w recepturze GitHuba, ale wymaga zmiany struktury potoku (sekcja 3.3, kroki 1–5). Zgodność z literą SLSA-B3 opiera się wtedy na interpretacji, którą trzeba opisać jako ograniczenie.

| Wariant | Próg H3b | Co robi E07-09 | Zalety | Wady |
|---|---|---|---|---|
| **A. L2 jako próg, L3 jako rozszerzenie** | M8 ≥ L2 (bez zmiany) | L2 zawsze. L3 (osobny job i reusable workflow) jeśli wystarczy czasu. M8 raportuje osiągnięty poziom i niespełnione wymagania wyższego | Hipoteza realna, ocena uczciwa, L3 można dodać bez zmiany metodyki | Słabsza teza, jeśli L3 się nie uda |
| **B. L3 jako próg** | M8 ≥ L3 | Pełna receptura z sekcji 3.3 obowiązkowo | Mocniejszy wynik. BUILD-3* z 800-204D („proces o wyższym zaufaniu niż build”) pokrywa się z separacją z L3 | Twierdzenie zależne od interpretacji GitHuba. Większe ryzyko dla harmonogramu |
| **C. L2, L3 tylko opisowo** | M8 ≥ L2 | Bez prób L3; w pracy opis, czego brakuje do L3 | Najmniej pracy. Zgodne z rezerwą zakresu (E01-03, poz. 3 „E07-09 SLSA tylko opisowo”) | BUILD-3* zostaje spełnione tylko częściowo |

**Decyzja autora z 2026-10-28: wariant A** (zgodnie z rekomendacją agenta).

- Próg H3b ≥ L2 zostaje i jest teraz uzasadniony specyfikacją (sekcja 3.2), a nie tylko wstępny.
- Sekcja 3.3 (osobny job atestacji) to mały koszt, który poprawia też BUILD-3*. Warto ją zaplanować w E07-09 jako cel rozszerzony.
- Przy pomiarze M8 tabela z sekcji 2 służy jako lista wymagań. Dla każdego wymagania wpisuje się dowód i ocenę.

**Wprowadzone zmiany (2026-10-28):**

- `docs/metodyka.md`, p. 2.2 „SLSA (H3b)”: próg L2 potwierdzony z uzasadnieniem, L3 jako cel rozszerzony z zastrzeżeniem,
- tabela metryk, M8: tabela wymagań z sekcji 2 jako lista, sposób weryfikacji (`gh attestation verify` z flagami z 3.3) i źródło `[@SLSA-1.2]`,
- odsyłacze w `nist-800-204d.md` (BUILD-3*, ATT-1*, luka formatów atestacji), `owasp-devsecops.md` (pkt 10 i tabela etapów) i `Zrodla/_Rdzen.md`,
- wpis w dzienniku badawczym `docs/log/2026-10-28.md`.

---

## 5. Powiązania z innymi ramami

| Rama | Pozycja | Związek z SLSA |
|---|---|---|
| SP 800-204D | BUILD-3* (MUST): dowody do atestacji generowane w procesie o wyższym zaufaniu niż build | Odpowiada SLSA-B2 (płaszczyzna sterowania) i w pełni SLSA-B3 (separacja). W jednym jobie spełnione częściowo, osobny job atestacji daje pełne spełnienie (analiza agenta) |
| SP 800-204D | ATT-1* (atestacje środowiska, procesu, materiałów, artefaktów) | Provenance GitHuba pokrywa środowisko (`builder.id`, `runner_environment`) i proces (`buildType`, `workflow`). Materiały tylko jako commit źródła, zależności przez SBOM. Rozstrzyga to „do sprawdzenia w E02-05” w `nist-800-204d.md`: **częściowo** |
| SP 800-204D | ATT-2*, ATT-3* | Podpis keyless (Sigstore) i log przejrzystości (repozytorium publiczne) odpowiadają SLSA-B2 i `distributing-provenance` |
| SP 800-204D | ATT-4* | SLSA-K1 i -K2. Podpisanej polityki brak, oczekiwania zapisane w poleceniu weryfikacji |
| SP 800-204D | rozdz. 1.2, 6 (nie specyfikuje formatów atestacji) | SLSA dostarcza format (SLSA Provenance, in-toto) i poziomy |
| SSDF | PS.2.1, PS.3.2 | Provenance i jego weryfikacja (PS.2.1), dane o pochodzeniu razem z SBOM (PS.3.2). SLSA deklaruje się jako sposób mierzenia zgodności z SSDF (`about`) |
| OWASP Top 10 CI/CD | CICD-SEC-9 Improper Artifact Integrity Validation | Bezpośrednio: build raz, atestacja, weryfikacja po digeście. Także CICD-SEC-4 (PPE) przez zagrożenie (D) |
| OWASP DevSecOps Guideline | pkt 10 w `owasp-devsecops.md` | „Same atestacje dają L2” potwierdza dokumentacja GitHuba i analiza wymagań. „L3 wymaga reusable workflow albo generatora” jest zgodne z GitHubem, ale generator jest nieutrzymywany, a samo przeniesienie do reusable workflow bez osobnego joba nie spełnia litery SLSA-B3 (sekcja 3.3). „L2 osiągalny dla większości zespołów” zgadza się z analizą |

---

## 6. Uwagi krytyczne i pytania na obronę

1. **Kto utrzymuje SLSA?** Projekt OpenSSF, specyfikacja według licencji Community Specification. Status „Approved” nadaje proces specyfikacji projektu, a nie organ normalizacyjny. W przeciwieństwie do NIST nie jest to dokument instytucji publicznej. W tekście pracy: „specyfikacja branżowa”.
2. **Czy poziom SLSA to ocena bezpieczeństwa aplikacji?** Nie. Dotyczy integralności buildu i pochodzenia artefaktu, a nie podatności (`about#what-slsa-doesnt-cover`). Ostrzega przed tym także dokumentacja GitHuba: atestacja nie gwarantuje, że artefakt jest bezpieczny.
3. **Dlaczego próg to L2, a nie L3, skoro GitHub deklaruje L3?** Patrz sekcja 3.3 i wariant A w sekcji 4: L3 to cel rozszerzony, który podajemy z zastrzeżeniem interpretacyjnym.
4. **Czy przypięte zależności i SBOM podnoszą poziom?** Nie. W v1.2 nie są wymaganiami ścieżki Build. Przypinanie jest w kierunkach rozwoju jako możliwe L4 (`future-directions`).
5. **Czy weryfikacja w tym samym potoku ma sens?** Tak jako weryfikacja konsumenta (`verifying-artifacts#consumer`), ale z ograniczeniem opisanym w sekcji 3.4.
6. **Wiek i zmienność:** ścieżka Build nie zmieniła wymagań od v1.0 (2023). Nowe ścieżki (Build Environment, Dependency) są w przygotowaniu (ogłoszenie v1.2). Ocena dotyczy v1.2.

---

## 7. Otwarte kwestie

- [x] Decyzja autora: wariant A (2026-10-28). H3b i M8 w `metodyka.md` zaktualizowane.
- [ ] TODO: zweryfikować zasady zakresu cache GitHub Actions i cache BuildKit `type=gha` pod kątem SLSA-B5d.
- [ ] TODO: zweryfikować etykiety runnerów jednoprocesorowych w „GitHub-hosted runners reference”.
- [ ] TODO: zweryfikować, czy ECR obsługuje atestacje jako artefakty OCI powiązane z obrazem (`push-to-registry`). Zależy od wyboru rejestru.
- [ ] TODO: zweryfikować, czy jest publiczne stanowisko SLSA w sprawie L3 przy reusable workflow pisanym przez samego producenta.
- [ ] Wybór między `actions/attest-build-provenance` a `actions/attest` w potoku (E07-09). Dokumentacja zaleca `actions/attest`.
- [ ] Ścieżka Source: tylko wzmianka w rozdz. 3. Natywne wsparcie GitHuba: TODO: zweryfikować.

## Źródła użyte w notatce

- [@SLSA-1.2]: strony `about`, `principles`, `tracks`, `terminology`, `build-track-basics`, `build-requirements`, `build-provenance`, `distributing-provenance`, `verifying-artifacts`, `threats`, `faq`, `future-directions`, `source-requirements`, `whats-new`.
- GitHub Docs: „Artifact attestations” (https://docs.github.com/en/actions/concepts/security/artifact-attestations), „Using artifact attestations and reusable workflows to achieve SLSA v1 Build Level 3” (https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/increase-security-rating), „Using artifact attestations to establish provenance for builds” (link w `docs/narzedzia.md`), „GitHub-hosted runners” (https://docs.github.com/en/actions/concepts/runners/github-hosted-runners). Dostęp 2026-10-28.
- `actions/attest-build-provenance` README, `actions/toolkit` `packages/attest/src/provenance.ts`, `cli/cli` `pkg/cmd/attestation/verify/verify.go` (gałęzie główne, dostęp 2026-10-28).
- `slsa-framework/slsa-github-generator`: README i SPECIFICATIONS.md (dostęp 2026-10-28).
- `slsa-framework/github-actions-buildtypes`: `workflow/v1` (dostęp 2026-10-28).
