# 0050. Atestacje provenance i SBOM w workflow B (`devsecops-ci.yml`) i weryfikacja na instancji przez `gh attestation verify`

- **Status:** przyjęty
- **Data:** 2026-11-27
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md) (potok bez poświadczeń AWS), [0033](0033-mechanizm-wdrozenia-pull.md) (agent wdrożenia, pochodzenie obrazu odroczone), [0036](0036-build-i-publikacja-obrazu.md) (job `build`), [0041](0041-zamrozenie-wariantu-a.md) (tag `pipeline-a-v1`, K2), [0042](0042-projekt-potoku-wariantu-b.md) (D1, D2, D3, D9; kroki B23, B24), [0043](0043-utwardzenie-workflowow.md) (H6, H8), [0048](0048-skanowanie-obrazu-trivy.md) (M1), [0049](0049-sbom-syft.md) (S1, S5), [`docs/notes/slsa.md`](../notes/slsa.md) (sekcje 3.2–3.4), [`docs/projekt-potoku.md`](../projekt-potoku.md), zadania E07-09 i E02-05, dziennik 2026-11-27 (TODO: zweryfikować, wpis powstaje na koniec sesji)

## Kontekst

ADR-0042 przewidział dwa kroki:

- B23: job `attest` wystawia atestację provenance i SBOM i czeka (`needs:`) na wszystkie bramki przebiegu (D3),
- B24: agent wdrożenia na instancji weryfikuje atestację przed `docker compose up`, a brak atestacji oznacza „czekaj”.

Weryfikacja musi działać na instancji. Potok nie ma dostępu do AWS (ADR-0032), więc tylko agent może odrzucić obraz przed uruchomieniem.

Próg hipotezy H3b to SLSA Build L2, a L3 jest celem rozszerzonym (decyzja autora z 2026-10-28, E02-05, `docs/metodyka.md`). Recepturę L3 opisuje `docs/notes/slsa.md`, sekcja 3.3:

- build bez `id-token: write`,
- atestacja w osobnym jobie reusable workflow,
- workflow bez `inputs` i `vars`,
- weryfikacja z `--signer-workflow`.

Atestowany ma być SPDX z ADR-0049.

Przeszkoda: wariant B nie ma jeszcze joba `build`, który publikuje obraz. Obraz w GHCR publikuje `baseline-ci.yml`. Bramki i SBOM działają na osobnym buildzie w tymczasowym jobie `image-scan` w `devsecops-gates.yml` (ADR-0048, M1; ADR-0049, S1). To dwa buildy i dwa różne digesty, a atestacja ma sens tylko dla obrazu, który przeszedł bramki i trafia do rejestru. Wariant A jest zamrożony tagiem `pipeline-a-v1` (ADR-0041), więc pliki workflow na `main` można zmieniać bez wpływu na A.

Rozpoznanie agenta (2026-11-27):

- **`gh` bez tokenu.** `gh` 2.102.0 bez żadnego logowania do GitHuba (pusty `GH_CONFIG_DIR`, bez `GH_TOKEN`) zweryfikował atestację provenance pliku `gh_2.102.0_linux_amd64.tar.gz` z repozytorium `cli/cli`. Bundle pobrano anonimowo z API atestacji. Wyniki:
  - poprawna atestacja z `--repo cli/cli --deny-self-hosted-runners`: kod 0,
  - zły `--signer-workflow`: kod 1,
  - atestacja innego pliku: kod 1,
  - pusty plik bundla: kod 1.

  `gh help exit-codes` podaje tylko kody 0, 1, 2 i 4. Po samym kodzie wyjścia nie da się więc odróżnić braku atestacji od atestacji nieważnej.
- **`actions/attest` v4.2.2** (najnowsze wydanie, 2026-08-04, README w tej wersji):
  - provenance i SBOM to dwa osobne wywołania. Typ atestacji wynika z wejść: `sbom-path` daje atestację SBOM, a brak `sbom-path` i predykatu daje provenance,
  - limit pliku SBOM to 16 MB, a SPDX czystej wersji ma 2,6 MB (ADR-0049),
  - `push-to-registry: true` wymaga `subject-name` bez tagu i `subject-digest`,
  - `create-storage-record` działa tylko w repozytoriach organizacji. To repozytorium należy do konta osobistego,
  - wymagane uprawnienia: `id-token: write` i `attestations: write`; `artifact-metadata: write` tylko dla rekordu składowania.
- **Zapis bundla w rejestrze.** Biblioteka `@sigstore/oci` (repozytorium `sigstore/sigstore-js`, `packages/oci/src/image.ts`) zapisuje bundle jako manifest z polem `subject`. Jeśli rejestr nie obsługuje referrers API, tworzy indeks pod tagiem według *Referrers Tag Schema* (`sha256-<hex>`). Którą ścieżkę wybiera GHCR: TODO: zweryfikować w pierwszym przebiegu CI.
- **Wersja `gh` do instalacji na hoście.** Najnowsza to v2.106.0 z 2026-11-25, czyli jeszcze w karencji 7 dni (ADR-0043, H6). Do użycia jest v2.105.0 z 2026-11-18. Tarball `linux_amd64` ma około 15 MB.
- **Digest dla atestacji.** `build` (ADR-0036) już oddaje digest z rejestru po `docker push` jako wyjście joba (`outputs.digest`).
- **Digest w SBOM a digest w GHCR** (TODO z ADR-0049): lokalnie niemiarodajne, bo Docker Desktop na Windows ma inny magazyn obrazów niż runner. Do sprawdzenia w pierwszym przebiegu workflow B.

## Czynniki decyzyjne

- kryteria zadania E07-09: obraz ma atestację provenance, wdrożenie odrzuca obraz bez ważnej atestacji (test negatywny), poziom SLSA uzasadniony,
- próg H3b ≥ L2 i cel rozszerzony L3 (E02-05); BUILD-3*, ATT-1*, ATT-2*, ATT-3*, DEPLOY-REQ-3, ATT-4* [@NIST-SP800-204D], PS.2.1, PS.3.1, PS.3.2 [@NIST-SP800-218],
- jeden obraz: skan, SBOM, atestacja i wdrożenie mają dotyczyć tego samego digestu,
- D3: tag gałęzi przesuwa się w `build`, zanim `attest` skończy,
- ADR-0032: instancja i potok bez wzajemnych poświadczeń, repozytorium publiczne,
- K2: wariant A bez zmian,
- prostota agenta wdrożenia i odporność na zmiany narzędzi.

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| A1. Skąd atestowany obraz | workflow B teraz (jeden workflow na `main`: `build` ze skanem przed pushem, bramki, `sbom` i `attest` w tym samym przebiegu); tymczasowy push obrazu z `image-scan` pod osobnym tagiem; atestacja obrazu A po fakcie (`workflow_run` po `baseline-ci`) |
| A2. Weryfikator na instancji | `gh attestation verify`; `cosign verify-attestation`; wybór po rozpoznaniu |
| A3. Poziom SLSA Build w zadaniu | L2 i próba L3 (reusable workflow); tylko L2, a L3 opisowo |
| A4. Reakcja agenta | brak atestacji: czekaj, atestacja nieważna: odrzuć; każdy błąd: czekaj; każdy błąd: odrzuć |
| B1. Plik workflow B | nowy `devsecops-ci.yml`; rozszerzenie `devsecops-gates.yml`; rozszerzenie `baseline-ci.yml` |
| B2. Atestacja SBOM | provenance i SBOM, agent sprawdza provenance; provenance i SBOM, agent sprawdza obie; tylko provenance |
| B3. Weryfikacja w CI | job `verify` bez logowania, z tą samą komendą co agent; tylko instancja |
| B4. Jak agent wykrywa brak atestacji | zapytanie do rejestru (referrers API, potem tag `sha256-<hex>`); własne pobranie bundla i `gh --bundle`; treść komunikatu błędu `gh` |
| B5. Przełącznik weryfikacji | wynika z `deploy_branch` (`exp/variant-b` włącza); osobna zmienna logiczna; zawsze włączona |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w dwóch rundach wywiadu z 2026-11-27. Runda 1 dotyczyła pytań A1–A4 przed rozpoznaniem, a runda 2 pytań B1–B5 po nim. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta.

| # | Decyzja | Powody autora |
|---|---|---|
| A1 | Workflow B powstaje teraz: jeden workflow na `main` z jobami `lint`, `test` i `build` jak w A (K2), skanem Trivy w `build` przed `docker push` (D1), bramkami, `sbom` i `attest` w tym samym przebiegu. `attest` ma `needs:` na wszystkie bramki (D3). Tymczasowe joby `image-scan` i `sbom` na osobnym buildzie znikają | jeden obraz, bez pracy do wyrzucenia, D3 wprost |
| A2 | Instancja weryfikuje przez `gh attestation verify`, a atestacja leży w GHCR obok obrazu (`push-to-registry`) | natywne dla atestacji GitHuba, mniej błędów konfiguracji |
| A3 | L2 i próba L3: `attest` jako reusable workflow (osobny plik, `on: workflow_call`), workflow bez `inputs` i `vars`, weryfikacja z `--signer-workflow`. L3 według interpretacji GitHuba, z zastrzeżeniem w 5.3 | mały koszt, BUILD-3* z SP 800-204D, decyzja z E02-05, mocniejszy wynik M8 |
| A4 | Brak atestacji: agent nic nie zapisuje i sprawdza ponownie w kolejnym cyklu. Atestacja jest, ale weryfikacja nie przechodzi: digest trafia do `failed` jak dziś i agent czeka na nowy tag | wymaga tego D3, jasny sygnał odrzucenia, spójne z agentem, mierzalny test negatywny |
| B1 | Nowy plik `devsecops-ci.yml` z całym wariantem B. Z `main` znikają `baseline-ci.yml` i `devsecops-gates.yml` (A zostaje w tagu `pipeline-a-v1`). `workflow-lint.yml` zostaje osobno do zamrożenia B (H8) | czytelne nazwy w pracy, diff A/B i tak jest (`experiment/versions/*.yaml`, tag `pipeline-a-v1`), czyste przejście |
| B2 | `attest` wystawia atestację provenance i atestację SBOM (SPDX), obie w GHCR. Instancja weryfikuje tylko provenance | mały koszt, prostszy agent |
| B3 | Job `verify` w CI po `attest`, bez logowania do GHCR ani GitHuba, z tymi samymi flagami `gh` co agent, w tym test negatywny. Egzekwowanie zostaje na instancji | test negatywny bez AWS, wcześniejsza informacja |
| B4 | Agent najpierw pyta GHCR anonimowo o obecność atestacji: referrers API, a gdy rejestr go nie obsługuje, tag `sha256-<hex>`. Brak oznacza „czekaj”. Gdy atestacja jest, agent uruchamia `gh attestation verify --bundle-from-oci`, a błąd oznacza „odrzuć” | weryfikacja zostaje w `gh` |
| B5 | Weryfikacja wynika z `deploy_branch`: `exp/variant-b` ją włącza, `exp/variant-a` nie. Bez nowej zmiennej Terraform | bez pomyłki, mniej konfiguracji |
| B6 | Wywołanie `uses: ./.github/workflows/attest.yml` zostaje, a zizmor dostaje wyjątek reguły `self-repository` dla `devsecops-ci.yml` w `.github/zizmor.yml`, z uzasadnieniem i terminem przeglądu (D6) | decyzja autora w trakcie implementacji: rekomendacja agenta przyjęta bez wskazania dodatkowych powodów |

Pytanie B6 doszło w trakcie implementacji, bo dwie bramki `workflow-lint` wykluczały się nawzajem:

- zizmor 1.32.0 (reguła `self-repository`, poziom low, więc blokuje) wymaga nowej składni `uses: $/...` (GitHub, lipiec 2026),
- przypięty actionlint 1.7.12, który jest najnowszym wydaniem (sprawdzone 2026-11-27), tej składni nie zna i zgłasza błąd.

Odrzucono opcję „składnia `$/` i wyjątek actionlinta (`-ignore`)”, bo zmienia konfigurację bramki i może ukryć inne błędy w tej linii. Według dokumentacji zizmora ryzyko reguły dotyczy akcji wczytanej z plików zmienionych wcześniej w jobie, czyli akcji w krokach, a nie reusable workflow wywołanego na poziomie joba (analiza agenta).

Decyzje agenta (techniczne, w ramach decyzji autora; potwierdzone w implementacji z 2026-11-27, wyniki CI do uzupełnienia):

- **Akcja:** `actions/attest` v4.2.2 (`1e69f48acb82d1966a394da916b4c1698aa569d6`, `docs/narzedzia.md`), dwa wywołania: provenance bez `sbom-path` i SBOM z `sbom-path`. Oba z `subject-name: ghcr.io/<repozytorium>`, `subject-digest` z wyjścia `build`, `push-to-registry: true` i `create-storage-record: false`.
- **Uprawnienia:**
  - reusable workflow `attest`: `id-token: write`, `attestations: write`, `packages: write`, `contents: read`,
  - `build`: bez `id-token` (SLSA-B3, BUILD-3*).
- **Kanał digestu:** `build` → `attest` przez `needs.build.outputs.digest`, a nie przez tag w rejestrze. Atestacja nie zależy więc od tagu, który może się przesunąć.
- **Komenda weryfikacji:** ta sama w `verify` i na instancji:

  `gh attestation verify oci://ghcr.io/<repozytorium>@<digest> --bundle-from-oci --repo <właściciel>/praca-magisterska-devsecops --signer-workflow <właściciel>/praca-magisterska-devsecops/.github/workflows/attest.yml --source-ref refs/heads/<gałąź> --deny-self-hosted-runners`

  Flagi według pomocy `gh` 2.102.0.
- **Wspólny skrypt:** `infra/terraform/work/verify-attestation.sh`, uruchamiany i przez agenta (na instancji jako `/usr/local/bin/ticketing-verify`), i przez job `verify`. Kody wyjścia:
  - 0: atestacja provenance zweryfikowana,
  - 10: brak atestacji provenance (agent czeka),
  - 11: atestacja jest, ale `gh` ją odrzucił (agent odrzuca digest),
  - 1: błąd rejestru albo danych wejściowych (agent ponawia w kolejnym cyklu).

  Obecność sprawdza po adnotacji `dev.sigstore.bundle.predicateType` = `https://slsa.dev/provenance/v1`, którą `actions/attest` v4.2.2 nadaje manifestowi bundla (`src/attest.ts`). Atestacja SBOM nie wystarczy więc do uznania, że provenance już jest. Skrypt czyta oba miejsca (referrers API i tag `sha256-<hex>`). Odpowiedź 400, 405 albo 501 z referrers API traktuje jak brak tego API. GHCR odpowiada 404 (`MANIFEST_UNKNOWN`) na referrers API dla obrazu bez atestacji (sprawdzone 2026-11-27).
- **Job `verify`:** cztery przypadki z oczekiwanym kodem:
  - obraz z przebiegu, oczekiwany podpisujący i ref: 0,
  - podpisujący `devsecops-ci.yml` zamiast `attest.yml`: 11,
  - inny ref źródłowy: 11,
  - obraz `main` z wariantu A sprzed E07-09 (`sha256:4b68b453…`, commit `060ea70`): 10.

  Każdy przypadek ma pusty `HOME` i nie ma tokenów (`env -i`), czyli warunki jak na instancji.
- **`gh` na instancji:** v2.105.0 z tarballa wydania, przypiętego sumą SHA-256 z pliku `checksums.txt` wydania, instalowanego w `user-data.sh` tylko dla wariantu B. Instancja nie ma tokenu GitHuba (ADR-0032).
- **Agent:** potrzebuje nazwy gałęzi (`--source-ref`), a nie tylko tagu GHCR (`exp-variant-b`). `ec2.tf` przekazuje `DEPLOY_BRANCH`, `VERIFY_ATTESTATION` (`true` tylko dla `exp/variant-b`) i skrypt weryfikacji (`VERIFY_GZ_B64`). „Czekaj” zapisuje się raz na digest w logu (plik stanu `waiting`).
- **Workflow:**
  - `devsecops-ci.yml`: joby `lint` i `test` skopiowane z `baseline-ci.yml` bez zmian (K2, porównane `diff`), bramki z `devsecops-gates.yml` bez zmian,
  - `build`: build z A, archiwum `docker save` (dla `sbom`), skan i bramka Trivy, potem login i push,
  - `sbom` pobiera archiwum z `build`, `attest` i `verify` biegną tylko na pushu,
  - z rulesetów znika wymagany check `image-scan`; `attest` i `verify` nie są wymagane, bo na PR są pomijane.

## Konsekwencje

- (+) Atestacja, SBOM, skan Trivy i wdrożenie dotyczą jednego digestu. Znikają dwa buildy z ADR-0048 i ADR-0049.
- (+) Atestacja leży w GHCR, więc instancja weryfikuje bez tokenu GitHuba. Repozytorium jest publiczne, więc wpisy trafiają też do publicznego logu przejrzystości Sigstore (`docs/notes/slsa.md`, 3.1).
- (+) Agent rozróżnia „czekaj” i „odrzuć” bez polegania na treści komunikatów `gh`. Odrzucenie zostawia jeden wpis w logu i `failed`, jak przy nieudanym wdrożeniu (ADR-0033).
- (+) Weryfikacja działa także wtedy, gdy tag gałęzi przesunie ktoś spoza potoku (z `packages: write`), bo obraz bez atestacji z `attest.yml` nie przejdzie (CICD-SEC-9).
- (+) Test negatywny da się powtarzać w CI bez AWS (B3). AWS służy tylko do potwierdzenia na instancji.
- (+) Testy lokalne (2026-11-27):
  - actionlint 1.7.12, zizmor 1.32.0 (`regular`, od `low`; 1 wyjątek z B6) i ShellCheck bez uwag, `terraform fmt` bez zmian,
  - `verify-attestation.sh` w kontenerze `PYTHON_IMAGE` z curl, z prawdziwym GHCR:
    - obraz `main` bez atestacji: kod 10,
    - nieznany digest: kod 10,
    - błędny digest: kod 1,
    - nieistniejące repozytorium (GHCR odmawia tokenu, HTTP 403): kod 1,
  - agent z atrapą weryfikatora i prawdziwym tagiem `main` w GHCR:
    - kod 10 dwa razy: czeka, log raz,
    - kod 1: ponowienie, bez `failed`,
    - kod 11: `failed` i wpis `result=failed` w `deployments.log`, kolejne uruchomienie nic nie robi,
    - bez `VERIFY_ATTESTATION` (wariant A): przechodzi od razu do `docker pull`.
- (−) Błąd sieci przy pobieraniu zaufanego korzenia przez `gh` też kończy się kodem 1 z `gh`, czyli kodem 11 skryptu. Agent odrzuci wtedy digest, chociaż atestacja może być ważna. Wyjście: nowy push albo przesunięcie tagu (rollback). To koszt decyzji B4: kody `gh` nie rozróżniają przyczyn.
- (−) Wyjątek zizmora (B6) ma termin przeglądu do 2027-01-31 albo do wydania actionlinta ze składnią `$/`.
- (−) E07-09 przejmuje integrację workflow B, którą notatki przypisywały zadaniu zamrożenia B (w notatkach „E07-14”, w katalogu zadań E07-13). Zadanie rośnie z M do L.
- (−) Zmieniają się nazwy workflowów na `main`: skrypty eksperymentu i dokumenty, które odwołują się do `baseline-ci.yml` albo `devsecops-gates.yml`, trzeba przejrzeć. Rulesety wymagają checków po nazwie joba, więc nazwy jobów zostają (`lint`, `test`, `build` i bramki). Job `image-scan` znika (skan w `build`), więc ruleset trzeba zaktualizować (`settings.sh apply` za zgodą autora).
- (−) Na PR obraz nie trafia do rejestru, więc `attest` i `verify` biegną tylko na pushu. Kryterium E07-09 sprawdza się na przebiegu push.
- (−) Na pushu wdrożenie B zaczyna się dopiero po najwolniejszej bramce, `attest` i kolejnym cyklu agenta. Nie zmienia to mierzonego czasu potoku (ADR-0037).
- (−) L3 to L3 według interpretacji GitHuba. Autor pisze zarówno workflow wywołujący, jak i reusable workflow, więc podział najemca–platforma jest umowny (`docs/notes/slsa.md`, 3.3). Weryfikację w CI może usunąć ktoś, kto zmienia definicję potoku (3.4), dlatego egzekwuje ją instancja. Materiał do 5.3.
- (−) Instancja instaluje dodatkowe narzędzie (`gh`, około 15 MB) i potrzebuje dostępu do serwerów TUF Sigstore i GitHuba (zaufany korzeń). TODO: zweryfikować na instancji.
- Do sprawdzenia w implementacji (TODO: zweryfikować):
  - czy GHCR obsługuje referrers API, czy biblioteka używa tagu `sha256-<hex>` (dla obrazu bez atestacji referrers API odpowiada 404),
  - czy polityka akcji platformy (ADR-0043, H7: wymuszenie SHA i lista dozwolonych) przepuszcza lokalny reusable workflow `./.github/workflows/attest.yml`,
  - czy `builder.id` i tożsamość podpisującego to `attest.yml`, a nie `devsecops-ci.yml` (warunek L3),
  - czy `gh attestation verify --bundle-from-oci` działa anonimowo na publicznym GHCR (job `verify`),
  - czy digest w SBOM różni się od digestu w GHCR (TODO z ADR-0049),
  - które wymagania z tabeli `docs/notes/slsa.md` (sekcja 2) spełnia gotowy potok: notatka o poziomie (kryterium 3, M8).

## Źródła

- [@SLSA-1.2]: `build-requirements`, `verifying-artifacts`, `terminology#build-model`; notatki `docs/notes/slsa.md` i `docs/notes/slsa-pytania.md`.
- [@NIST-SP800-204D]: BUILD-3*, ATT-1*–ATT-4*, DEPLOY-REQ-3; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PS.2.1, PS.3.1, PS.3.2; notatki `docs/notes/nist-ssdf.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-27):
  - README `actions/attest` v4.2.2: https://github.com/actions/attest
  - pomoc `gh attestation verify` i `gh help exit-codes` w `gh` 2.102.0,
  - wydania `gh`: https://github.com/cli/cli/releases
  - `sigstore/sigstore-js`, `packages/oci/src/image.ts`: https://github.com/sigstore/sigstore-js
