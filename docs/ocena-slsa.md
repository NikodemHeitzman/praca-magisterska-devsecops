# Ocena poziomu SLSA Build wariantu B (E07-09)

Wstępna ocena metryki M8 (`docs/metodyka.md`): najwyższy poziom SLSA Build, którego wszystkie wymagania ścieżki Build są spełnione, i niespełnione wymagania poziomu wyższego. Lista wymagań pochodzi z tabeli w `docs/notes/slsa.md`, sekcja 2 [@SLSA-1.2]. Decyzje dotyczące potoku opisuje [ADR-0050](adr/0050-atestacje-i-weryfikacja-przed-wdrozeniem.md).

- **Stan oceniany:** `main` w commicie `71ec119` (2026-11-27), workflow `devsecops-ci.yml` i `attest.yml`, agent wdrożenia z `infra/terraform/work/`.
- **Ocena:** wstępna, sporządzona przez agenta AI. Autor ją czyta i redaguje. Ostateczną wartość M8 ustala się dla zamrożonego wariantu B (tag `pipeline-b-v1`, zadanie zamrożenia B), bo potok może się do tego czasu zmienić.

## Wynik

**Build L2: spełniony**, pod warunkiem potwierdzenia SLSA-0 w liście kontrolnej M7. Próg hipotezy H3b (M8 ≥ L2) jest więc osiągnięty na tym etapie.

**Build L3: spełniony według interpretacji GitHuba** (atestacja w reusable workflow i weryfikacja z `--signer-workflow`), z zastrzeżeniami opisanymi niżej. Zgodnie z decyzją autora z 2026-10-28 (E02-05, wariant A) L3 jest wynikiem ponad próg i w pracy podaje się go razem z tymi zastrzeżeniami.

## Dowody wspólne

Provenance obrazu `main` z przebiegu push [45999735380](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/45999735380). Bundle pobrano anonimowo z GHCR (indeks pod tagiem `sha256-<hex>`) 2026-11-27:

| Pole | Wartość |
|---|---|
| podmiot | `ghcr.io/nikodemheitzman/praca-magisterska-devsecops@sha256:7a6454a2…6d7995` |
| `predicateType` | `https://slsa.dev/provenance/v1` |
| `buildType` | `https://actions.github.io/buildtypes/workflow/v1` |
| `externalParameters.workflow` | `path: .github/workflows/devsecops-ci.yml`, `ref: refs/heads/main`, repozytorium `NikodemHeitzman/praca-magisterska-devsecops` |
| `internalParameters.github` | `event_name: push`, `runner_environment: github-hosted` |
| `resolvedDependencies` | commit `71ec119…` |
| `runDetails.builder.id` | `…/.github/workflows/attest.yml@refs/heads/main` |
| `invocationId` | `…/actions/runs/45999735380/attempts/1` |
| wpis w logu przejrzystości | Rekor `logIndex` 4148574388 (provenance), 4148576256 (SBOM) |

Certyfikat podpisu obrazu `sha256:9e764a94…` z przebiegu 45992258765 ma `buildSignerURI` = `attest.yml` i `buildConfigURI` = `devsecops-ci.yml` (ADR-0050, wyniki CI).

Weryfikacja przez konsumenta (ADR-0050):

- **Job `verify`** w każdym przebiegu push uruchamia cztery przypadki bez logowania. Ostatnio przeszły w przebiegach 45994110024, 45995528608 i 45999735380.
- **Agent na instancji AWS** (test z 2026-11-27):
  - obraz z atestacją: wdrożony,
  - obraz bez atestacji: agent czeka,
  - atestacja z innego refu: odrzucona.

## Tabela wymagań

Stan: ✓ spełnione, ◐ spełnione z zastrzeżeniem, ✗ niespełnione. Kolumna „Poziom” podaje najniższy poziom, który wymaga danej pozycji.

| ID | Wymaganie (skrót) | Poziom | Stan | Dowód w projekcie |
|---|---|---|---|---|
| SLSA-0 | najlepsze praktyki bezpieczeństwa | L1 | ◐ | pośrednio: utwardzenie workflowów (ADR-0043), sekrety (ADR-0044), rulesety. Pełne potwierdzenie w liście kontrolnej M7 (TODO: zweryfikować przy ocenie M7) |
| SLSA-P1 | platforma zdolna do docelowego poziomu | L1 | ✓ | GitHub Actions, runnery hostowane (ADR-0001, ADR-0042) |
| SLSA-P2 | spójny proces buildu | L1 | ✓ | jeden workflow `devsecops-ci.yml` wyzwalany pushem na `main` i `exp/variant-*`; w provenance `externalParameters.workflow` |
| SLSA-P3 | dystrybucja provenance | L1 | ✓ | atestacje w API atestacji repozytorium, w GHCR obok obrazu (`push-to-registry`, tag `sha256-<hex>`) i w publicznym Rekorze |
| SLSA-B1 | provenance istnieje i wskazuje artefakt digestem | L1 | ✓ | `subject` = digest obrazu z wyjścia joba `build`; `gh` wymaga predykatu SLSA v1 |
| SLSA-B2 | provenance autentyczne (podpis, dane z platformy) | L2 | ✓ | podpis Sigstore, certyfikat Fulcio z tożsamością workflow z tokenu OIDC GitHuba, predykat z claimów OIDC (`actions/attest`, `docs/notes/slsa.md` 3.1); `gh` sprawdza podpis i wpis w logu |
| SLSA-B3 | provenance niepodrabialne | L3 | ◐ | `id-token: write` ma tylko job `attest` (reusable `attest.yml`); `build` i pozostałe joby go nie mają. Workflow bez `workflow_dispatch`, `inputs` i `vars`. `builder.id` i podpisujący = `attest.yml`, weryfikacja z `--signer-workflow`. Zastrzeżenia Z1–Z3 |
| SLSA-B4 | platforma hostowana | L2 | ✓ | `runner_environment: github-hosted`; `--deny-self-hosted-runners` w weryfikacji |
| SLSA-B5a | build bez dostępu do sekretu podpisu | L3 | ◐ | jak SLSA-B3: sekret OIDC dostępny tylko w jobie `attest`, który ma jedynie kroki `download-artifact`, logowanie do GHCR i `actions/attest`. Zastrzeżenie Z1 |
| SLSA-B5b | buildy równoległe nie wpływają na siebie | L3 | ✓ | wszystkie joby na `ubuntu-24.04` (osobna VM), bez etykiet jednoprocesorowych |
| SLSA-B5c | efemeryczne środowisko | L3 | ✓ | nowa VM na każdy job (runnery hostowane GitHuba) |
| SLSA-B5d | brak zatrucia cache | L3 | ✓ | bez `actions/cache` i cache BuildKit; `setup-uv` z `enable-cache: false` (ADR-0038); w Dockerfile `uv sync --no-cache`; obraz budowany na świeżej VM |
| SLSA-B5e | brak zdalnego wpływu na build | L3 | ✓ | brak akcji zdalnego dostępu do runnera; actionlint i zizmor bez uwag (ADR-0043) |
| SLSA-K1 | konsument sprawdza autentyczność | L2 | ✓ | agent wdrożenia (egzekwowanie) i job `verify` (`verify-attestation.sh`, `gh attestation verify --bundle`); test negatywny na instancji i w CI |
| SLSA-K2 | konsument sprawdza oczekiwania | L1 (SHOULD) | ◐ | sprawdzane: repozytorium (`--repo`), podpisujący (`--signer-workflow`), ref źródłowy (`--source-ref`), runner hostowany, typ predykatu. Nie sprawdza się wprost `buildType` ani nierozpoznanych parametrów zewnętrznych (`gh` tego nie robi). Pozycja ma stopień SHOULD |

## Zastrzeżenia do L3

- **Z1. Podział na najemcę i platformę jest umowny.** L3 zakłada, że płaszczyzna sterowania jest poza kontrolą najemcy (`terminology#build-model`). Tutaj autor pisze zarówno `devsecops-ci.yml`, jak i `attest.yml`, w tym samym repozytorium. Zmianę `attest.yml` ogranicza tylko ruleset `main`: wymagany PR, 0 zatwierdzeń, bez obejść. W projekcie jednoosobowym nie ma drugiej osoby, która recenzuje zmianę. Uzasadnienie GitHuba (reusable workflow jako sprawdzone instrukcje buildu) ma tu słabsze oparcie (`docs/notes/slsa.md`, 3.3).
- **Z2. Digest przychodzi z joba `build`.** `attest` dostaje digest przez wyjście joba (`needs.build.outputs.digest`). To kanał kontrolowany przez platformę, jak w `slsa-github-generator`. Wartość ustala jednak krok użytkownika w `build`. Provenance poświadcza, że ten workflow wskazał ten digest, a nie że obraz zbudowano bit po bicie w opisany sposób. Specyfikacja dopuszcza ten model (`build-requirements`), ale to granica tego, co L3 gwarantuje.
- **Z3. Kompletność parametrów zewnętrznych.** Provenance z `actions/attest` zawiera tylko `workflow` (ścieżka, ref, repozytorium) i nie zapisuje `inputs` ani `vars` (`docs/notes/slsa.md`, 3.1). Wymaganie jest spełnione dlatego, że workflow nie ma `inputs` ani nie czyta `vars`. Dodanie ich później po cichu złamałoby SLSA-B3. Warto to sprawdzać przy zamrożeniu B.
- **Z4. Weryfikacja w CI nie jest egzekwowaniem.** Job `verify` może usunąć ktoś, kto zmienia definicję potoku (`docs/notes/slsa.md`, 3.4). Wdrożenie blokuje agent na instancji, którego konfigurację ustala Terraform, a nie potok (ADR-0050).

## Niespełnione albo niepotwierdzone wymagania (do M8)

- SLSA-0: do potwierdzenia w liście kontrolnej M7.
- SLSA-K2 (SHOULD): brak sprawdzenia `buildType` i odrzucania nierozpoznanych parametrów zewnętrznych. Można to dodać jako kontrolę JSON wyniku `gh --format json`. Decyzja należy do autora: TODO: zweryfikować, czy warto.
- L3: zastrzeżenia Z1–Z3. Formalnie spełnione według deklaracji GitHuba, a w ocenie autora pracy tylko z zastrzeżeniem interpretacyjnym (materiał do 5.3).

## Źródła

- [@SLSA-1.2]: `build-track-basics`, `build-requirements`, `verifying-artifacts`, `terminology#build-model`; notatki `docs/notes/slsa.md`.
- [@NIST-SP800-204D]: BUILD-3*, ATT-1*, ATT-4*; notatki `docs/notes/nist-800-204d.md`.
- Dokumentacja GitHuba o artifact attestations i poziomie L3 z reusable workflow: odnośniki w `docs/notes/slsa.md`, „Źródła użyte w notatce”.
- Dane: przebiegi `devsecops-ci` 45992258765, 45994110024, 45995528608, 45999735380; test AWS w ADR-0050.
