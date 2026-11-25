# 0048. Skanowanie obrazu kontenera: Trivy image z przypiętą bazą podatności

- **Status:** przyjęty
- **Data:** 2026-11-25
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0022](0022-obraz-kontenera-aplikacji.md) (obraz bazowy po digeście), [0036](0036-build-i-publikacja-obrazu.md) (job `build`), [0042](0042-projekt-potoku-wariantu-b.md) (krok B19; D1, D2, D5a, D6, D9, D13), [0043](0043-utwardzenie-workflowow.md) (H8), [0044](0044-skanowanie-sekretow.md) (S4, wspólny plik bramek), [0047](0047-skanowanie-iac-checkov-trivy-hadolint.md) (ten sam obraz Trivy), [`docs/projekt-potoku.md`](../projekt-potoku.md), zadanie E07-07, `experiment/ground-truth.yaml` (GT-08), [dziennik 2026-11-25](../log/2026-11-25.md)

## Kontekst

ADR-0042 przewidział krok B19: Trivy skanuje obraz aplikacji w jobie `build` między `docker build` a `docker push` (D1, DEPLOY-REQ-5 [@NIST-SP800-204D]) i blokuje podatności `MEDIUM` i wyższe z dostępną poprawką (D5a). Jedyną pozycją katalogu z oczekiwanym detektorem „skaner obrazu” jest GT-08: starszy digest `python:3.14-slim` w `FROM` (E05-01).

Job `build` jest jednak w `baseline-ci.yml`, czyli w wariancie A. Krok bezpieczeństwa w tym jobie złamałby K2, a kopia `build` w workflow bramek publikowałaby obraz drugi raz (ADR-0043 H8, ADR-0044 S4). Workflow wariantu B, w którym `build` dostanie krok skanu, powstaje dopiero w E07-14.

Rozpoznanie agenta (2026-11-25, kod z `main` po `349d42a`, Trivy 0.76.2 z obrazu przypiętego w ADR-0047):

- **Opcje Trivy dla obrazu:**
  - domyślne skanery to `vuln,secret`; `--image-config-scanners` dodaje skan konfiguracji obrazu (`misconfig`, `secret`),
  - `--input` czyta archiwum z `docker save`, bez dostępu do demona Dockera,
  - kod wyjścia przy zgłoszeniach ustawia `--exit-code` (domyślnie 0); błąd narzędzia, np. brak pliku wejściowego albo nieistniejący digest bazy, daje 1,
  - `trivy convert` zamienia raport JSON na SARIF, więc jeden skan daje oba formaty,
  - pliki czytane automatycznie: `trivy.yaml`, `.trivyignore` i `trivy-secret.yaml` (wyłączane pustą wartością `--config`, `--ignorefile` i `--secret-config`).
- **Baza podatności** to artefakt OCI (`mirror.gcr.io/aquasec/trivy-db:2`, `ghcr.io/aquasecurity/trivy-db:2`) pobierany przy każdym skanie. Tag przesuwa się kilka razy na dobę: digest `sha256:78c9bebc…` (`UpdatedAt` 2026-11-25 07:11 UTC) był aktualny o 13:15 UTC, a kilka minut później tag wskazywał już inny digest. `--db-repository ghcr.io/aquasecurity/trivy-db@sha256:…` pobiera bazę po digeście. Jak długo GHCR przechowuje stare digesty bazy, nie wiadomo (TODO: zweryfikować).
- **Czysta wersja (obraz bazowy `9aaa4740…`, Debian 13.7)** z bazą z 2026-11-25: 254 podatności w pakietach systemowych, 0 w pakietach Pythona, 0 sekretów. Ponad progiem D5a jest 29 wpisów pakietów, czyli 16 CVE w trzech pakietach źródłowych: glibc (13 CVE w `libc6` i `libc-bin`), zlib (2) i libzstd (1, HIGH). E05-01 podawał 3 zgłoszenia z poprawką (stan 2026-11-08). Różnica wynika wyłącznie ze zmiany bazy, bo obraz jest ten sam.
- **GT-08 (obraz bazowy `7bec7ddc…`, Debian 13.6)** z tą samą bazą: 65 CVE ponad progiem, w tym 49 spoza czystej wersji (3 CRITICAL, 18 HIGH, 28 MEDIUM). Warunek z referencji GT-08 jest spełniony.
- **Najnowszy `python:3.14-slim`** (`22eafb37…`, Debian 13.8, ten sam digest co `PYTHON_IMAGE` w potoku): ponad progiem zostaje w pakietach systemowych tylko libzstd.

## Czynniki decyzyjne

- skuteczność wobec GT-08 (M1, H1) bez blokowania czystej wersji (M6),
- zgodność z polityką bramek ADR-0042 (D1, D5a, D6, D9) [@OWASP-DevSecOps-Guideline] i z DEPLOY-REQ-4, DEPLOY-REQ-5 [@NIST-SP800-204D],
- K2: wariant A bez kontroli bezpieczeństwa; obraz publikuje jeden workflow (H8, S4),
- odtwarzalność wyniku w serii (K5, zasada 6 w `AGENTS.md`).

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| M1. Miejsce skanu do E07-14 | tymczasowy job `image-scan` w `devsecops-gates.yml` (build bez pushu); szkielet workflow B już teraz; krok w `build` w `baseline-ci.yml` |
| M2. 16 CVE czystej wersji | lista wyjątków (D6); nowszy digest obrazu bazowego; próg tylko HIGH i wyżej |
| M3. Baza podatności | przypięta po digeście; najnowsza w każdym przebiegu z zapisem metadanych; przypięta tylko na czas serii |
| M3a. Brak przypiętej bazy w rejestrze | błąd bramki i świadoma zmiana digestu; kopia bazy w rejestrze projektu; awaryjnie najnowsza baza |
| M4. Skanery | `vuln,secret` i sekrety konfiguracji obrazu; dodatkowo misconfig konfiguracji; tylko `vuln` |
| M5. Wejście skanu | archiwum z `docker save` (`--input`); gniazdo Dockera |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-25. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta.

| # | Decyzja | Powody autora |
|---|---|---|
| M1 | Tymczasowy job `image-scan` w `devsecops-gates.yml`: buduje obraz tym samym poleceniem co `build`, bez logowania i pushu, i skanuje go. W E07-14 kroki skanu przechodzą do `build` przed `docker push` (D1) | bez podwójnej publikacji, prostsze E07-14, tymczasowy koszt (drugi build w przebiegu) akceptowalny |
| M2 | 16 CVE czystej wersji idzie na listę wyjątków `trivy-image`; obraz bazowy bez zmian | zgodne z D6 i I2, katalog bez zmian (referencje GT-08 i ADR-0022 zostają ważne), jawnie widoczne |
| M2a | Uzasadnienie wyjątków: pakiety obrazu bazowego przypiętego w ADR-0022; poprawka wymaga nowego digestu, czego D6 nie dopuszcza przed serią; aktualizacja obrazu bazowego po serii | zatwierdzone przez autora |
| M3 | Baza podatności przypięta po digeście w zmiennej `TRIVY_DB_REPOSITORY`, zmieniana tylko świadomie, razem z przeglądem wyjątków | odtwarzalność, czysty pomiar (różnice w serii wynikają z łatek GT, a nie z dryfu bazy) |
| M3a | Gdy przypiętej bazy nie da się pobrać, job kończy się błędem (fail closed); nowy digest wpisuje się razem z przeglądem wyjątków | zgodne z fail closed, przegląd wyjątków przy każdej zmianie bazy, ryzyko zniknięcia digestu w czasie serii małe (TODO: zweryfikować retencję) |
| M4 | `--scanners vuln,secret --image-config-scanners secret` | zgodne z B19 (podatności i sekrety w warstwach), mały koszt |
| M5 | Trivy czyta archiwum z `docker save` (`--input`), bez gniazda Dockera | bez dostępu narzędzia do demona Dockera, wspólne z DAST (D2), prostota |

Decyzje agenta (techniczne, w ramach decyzji autora i ADR-0042):

- **Digest bazy:** `ghcr.io/aquasecurity/trivy-db@sha256:78c9bebc838106b10b9ad320b9d7976319ca7516740dd0fe01a5b5036b6049e1` (`UpdatedAt` 2026-11-25T07:11:44Z), czyli baza, z którą policzono 16 CVE czystej wersji. Osobny krok pobiera ją do katalogu cache (`--download-db-only`), a skan działa z `--skip-db-update`. Metadane bazy z repozytorium (`reports/trivy-db.json`) trafiają do artefaktu i podsumowania przebiegu.
- **Jeden skan JSON, SARIF z `trivy convert`.** Pełny raport bez filtra ważności i bez `--ignore-unfixed` (M1 eksperymentu), próg stosuje skrypt. Opcje `--config ""`, `--ignorefile ""` i `--secret-config ""` jak I4 oraz `--disable-telemetry`.
- **Bramka `.github/scripts/image_gate.py`** (wzór `sca_gate.py`):
  - podatność `MEDIUM`, `HIGH` lub `CRITICAL` ze statusem `fixed` blokuje; bez statusu decyduje pole `FixedVersion`,
  - każdy sekret blokuje, jak w jobie `secrets` (Gitleaks nie ma poziomów),
  - wyjątek: narzędzie `trivy-image`, reguła = identyfikator podatności albo reguły sekretu, ścieżka = `<typ pakietu>/<pakiet źródłowy>` (np. `debian/glibc`), plik w obrazie albo `image-config` dla konfiguracji obrazu. Pakiet źródłowy zamiast binarnego, bo `libc6` i `libc-bin` mają te same poprawki glibc: 16 wpisów zamiast 29,
  - kod 2 (fail closed): brak albo nieczytelny raport, raport innego typu niż `container_image`, raport bez wykrytego systemu (pakiety systemowe niezeskanowane), brak metadanych bazy, niekompletny wpis wyjątku,
  - nieużyty wyjątek daje ostrzeżenie; tabela w podsumowaniu przebiegu.
- **PyPI dla bramki:** `.github/tools/image.in` i `image.txt` (PyYAML 6.0.3 z hashami, `--exclude-newer 2026-11-18`), instalowane w `PYTHON_IMAGE`, jak w `sca`.
- **Artefakt `image-scan-reports`** (`trivy-image.json`, `trivy-image.sarif`, `trivy-db.json`, retencja 90 dni) i SARIF w zakładce Security (kategoria `trivy-image`), jak I5. Archiwum obrazu nie jest jeszcze artefaktem: potrzebuje go dopiero DAST (E07-10, D2).

## Konsekwencje

- (+) Krok B19 z `docs/projekt-potoku.md` jest zrealizowany, do E07-14 jako osobny job. Zamknięte pytanie z E05-01 o `--ignore-unfixed`: próg stosuje bramka na pełnym raporcie.
- (+) Test lokalny (2026-11-25): kroki joba odtworzone w Dockerze, z przypiętą bazą, Trivy i Pythonem z obrazów po digeście z workflow. Skan z konwersją do SARIF trwa około 22–41 s.

  | Scenariusz | Ponad progiem (CVE, pakiet źródłowy) | Sekrety | Bramka |
  |---|---|---|---|
  | czysta wersja | 16 (wszystkie na liście wyjątków) | 0 | przechodzi (kod 0) |
  | GT-08 (`FROM python:3.14-slim@sha256:7bec7ddc…`) | 65, w tym 49 blokujących | 0 | blokuje (kod 1) |
  | klucz AWS w pliku w obrazie i token GitHub w `ENV` | 16 (wyjątki) | 4 wpisy, 3 unikatowe (plik w warstwie, polecenie `RUN` w historii, `ENV`) | blokuje (kod 1) |
  | jak wyżej z wyjątkiem dla `github-pat` w `image-config` | 16 (wyjątki) | 2 blokujące | blokuje (kod 1) |
  | brak raportu, brak metadanych bazy, raport bez systemu, raport typu `filesystem`, wpis wyjątku bez `reason` | — | — | kod 2 |
  | nieistniejący digest bazy | — | — | krok pobierania kończy się kodem 1 |

  actionlint i zizmor (`regular`, od `low`) bez uwag.
- (+) Test w CI (2026-11-25):
  - **PR #31** (czysta wersja, `d4c0795`, przebieg `devsecops-gates` 45624517614): wszystkie checki zielone. `image-scan` przechodzi w około 49 s: build obrazu około 10 s, pobranie bazy około 5 s, skan i konwersja około 8 s, wysyłka SARIF około 8 s, bramka około 3 s. Wynik jak lokalnie: 16 CVE ponad progiem, wszystkie na liście wyjątków, baza z `UpdatedAt` 2026-11-25T07:11:44Z,
  - **PR #32** (szkic, łatka GT-08; zamknięty bez scalania, przebieg 45624539051): `image-scan` blokuje 49 CVE (65 ponad progiem, 16 z wyjątkami), pozostałe joby zielone,
  - artefakt `image-scan-reports` jest w obu przebiegach. Code scanning przyjął SARIF (kategoria `trivy-image`, 254 wyniki, 116 reguł).
- (+) Sekrety w konfiguracji obrazu Trivy wykrywa także w historii warstw: polecenie `RUN` z kluczem daje zgłoszenie w konfiguracji i w pliku.
- (−) Do E07-14 obraz skanowany w `image-scan` i obraz publikowany przez `build` to dwa buildy tego samego kodu. Build nie jest powtarzalny bit po bicie, więc digesty się różnią, a zawartość pakietów jest ta sama (te same digesty bazowe i `uv.lock`). W E07-14 skan i publikacja dotyczą jednego obrazu (D1).
- (−) Przypięta baza nie widzi podatności opublikowanych po `UpdatedAt`. Między aktualizacjami bazy bramka może przepuścić obraz z nową CVE. Ryzyko łagodzi audyt R2 (B25, DEPLOY-REQ-4), który używa bieżącej bazy. Opis do 5.3.
- (−) Wynik skanu obrazu zależy od daty bazy bardziej niż od kodu: ta sama czysta wersja dała 3 zgłoszenia 2026-11-08 i 16 CVE 2026-11-25. Bez przypięcia lista wyjątków psułaby się w trakcie serii. To materiał do 4.4 i 5.3.
- (−) Wyjątki dotyczą CVE z dostępną poprawką. Pakiety mają nowsze wersje w Debianie 13.8, ale D6 wyklucza zmianę czystej wersji przed serią.
- (−) Code scanning dostaje alerty czystej wersji (także z listy wyjątków), jak w ADR-0047. Lokalizacją alertu jest archiwum obrazu (`/image.tar`), a nie plik repozytorium (sprawdzone w PR #31), więc alerty nie wskazują linii w `app/Dockerfile`.
- (−) Konfiguracja bramki jest w repozytorium, więc PR może ją zmienić (ryzyko resztkowe, `docs/projekt-potoku.md` 4.6).
- Kolejne kroki:
  - **po scaleniu:** `image-scan` jako wymagany check w rulesetach `main` i `exp-variant-b` (`settings.sh apply` za zgodą autora),
  - **E07-08:** SBOM z tego samego obrazu (archiwum z `docker save`),
  - **E07-10:** archiwum obrazu jako artefakt dla DAST (D2),
  - **E07-12:** zbiorczy raport czyta `trivy-image.json` z artefaktu `image-scan-reports`,
  - **E07-14:** kroki skanu do `build` przed `docker push`, usunięcie joba `image-scan`, zamrożenie digestu bazy z wersjami (K5),
  - **po serii:** nowy digest obrazu bazowego i bazy podatności, przegląd wyjątków `trivy-image`.

## Źródła

- [@NIST-SP800-204D]: DEPLOY-REQ-4, DEPLOY-REQ-5, TEST-2*; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PW.4.4; notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-DevSecOps-Guideline]: skan obrazu w CI, „fail closed”; notatki `docs/notes/owasp-devsecops.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-25):
  - pomoc `trivy image --help` i `trivy convert --help` w 0.76.2,
  - wydania Trivy: https://github.com/aquasecurity/trivy/releases
