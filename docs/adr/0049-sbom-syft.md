# 0049. SBOM obrazu: Syft na archiwum z `image-scan`, SPDX i CycloneDX

- **Status:** przyjęty
- **Data:** 2026-11-25
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0036](0036-build-i-publikacja-obrazu.md) (job `build`), [0042](0042-projekt-potoku-wariantu-b.md) (krok B22; D1, D2, D3, D9), [0043](0043-utwardzenie-workflowow.md) (H6, H8), [0044](0044-skanowanie-sekretow.md) (S4, wspólny plik bramek), [0048](0048-skanowanie-obrazu-trivy.md) (job `image-scan`, M1, M5), [`docs/projekt-potoku.md`](../projekt-potoku.md), [`docs/narzedzia.md`](../narzedzia.md) p. 4.4, zadanie E07-08, [dziennik 2026-11-25](../log/2026-11-25.md)

## Kontekst

ADR-0042 przewidział krok B22: job `sbom` po publikacji obrazu, tylko na pushu, w trybie fail closed (brak SBOM to błąd joba). Format ustalił autor 2026-10-20 (`docs/narzedzia.md`, p. 4.4): Syft zapisuje w jednym przebiegu SPDX JSON i CycloneDX JSON. Atestowany będzie SPDX (E07-09), a CycloneDX zostaje artefaktem przebiegu. Kryterium zadania E07-08 brzmi jednak „SBOM dla każdego builda”, a to obejmuje też PR.

SP 800-204D nie określa formatu SBOM (1.2), ale wymaga wyliczenia zależności łącznie z przechodnimi (TEST-2*) i SBOM od pierwszego commitu (BASE-4*) [@NIST-SP800-204D]. Według SLSA SBOM opisuje, z czego artefakt się składa, i uzupełnia provenance, ale nie podnosi poziomu Build [@SLSA-1.2] (`docs/notes/slsa.md`, FAQ).

Workflow wariantu B z jobem `build` powstaje dopiero w E07-14. Do tego czasu obraz dla bramek buduje tymczasowy job `image-scan` w `devsecops-gates.yml`, bez pushu (ADR-0048, M1).

Rozpoznanie agenta (2026-11-25, czysta wersja `5ba61f0`, lokalnie w Dockerze):

- **Wersja:** najnowsze wydanie Syft to 1.57.2 z 2026-11-16, więc karencja 7 dni (ADR-0043, H6) minęła. Obraz `anchore/syft:v1.57.2` ma digest indeksu `sha256:e97e20b6…`. W `docs/narzedzia.md` zapisana była wersja 1.54.1.
- **Wejście:** Syft czyta archiwum `docker save` (`docker-archive:`) bez dostępu do demona Dockera. Jeden przebieg zapisuje kilka formatów (`--output` wiele razy). Czas około 4 s.
- **Wersje schematu w wyniku:**
  - SPDX 2.3 (`spdxVersion: SPDX-2.3`, licencja danych CC0-1.0, lista licencji 3.29),
  - CycloneDX 1.7 (`specVersion: 1.7`, `bom-1.7.schema.json`).
- **Zawartość:**
  - 87 pakietów Debiana 13.7, 38 pakietów Pythona z `/opt/venv` i interpreter CPython 3.14.10 (wykryty po pliku binarnym, bo obraz bazowy instaluje go ze źródeł),
  - każdy pakiet ma purl, a przy 8 z 127 nie ma zadeklarowanej licencji,
  - SPDX ma 2,6 MB, a CycloneDX 1,1 MB. Limit atestacji GitHuba to 16 MB (`docs/narzedzia.md`, p. 4.4).
- **Kompletność:** pakiety Pythona w SBOM porównano z `uv export --no-dev` (uv 0.13.6). Brakuje tylko `tzdata`, zależności `psycopg` wyłącznie na Windows (`sys_platform == 'win32'`), której nie ma w obrazie.
- **Identyfikacja obrazu:**
  - SPDX (suma kontrolna pakietu głównego i purl `pkg:oci`) i CycloneDX (wersja komponentu w `metadata`) podają digest manifestu, który Syft liczy z archiwum,
  - ID obrazu (digest konfiguracji), czyli wartość `ImageID` z raportu Trivy, jest tylko w formacie syft-json,
  - opcja `--source-version` zastępuje digest w CycloneDX podaną wartością,
  - etykieta `org.opencontainers.image.revision` (SHA commita, nadawana w `build` i `image-scan`) jest w CycloneDX jako właściwość `syft:image:labels:…`, a w SPDX jej nie ma.

## Czynniki decyzyjne

- kryterium zadania („SBOM dla każdego builda”) i wymagania TEST-2*, BASE-4* [@NIST-SP800-204D], PS.3.2 [@NIST-SP800-218],
- spójność z `image-scan`: SBOM i skan podatności mają opisywać ten sam obraz,
- K2: wariant A bez zmian; obraz publikuje jeden workflow (H8, S4),
- fail closed bez progu ważności (ADR-0042, B22) i jawne wersje formatów (odtwarzalność, zasada 6 w `AGENTS.md`),
- czas przebiegu PR (H2a).

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| S1. Miejsce SBOM do E07-14 | tymczasowy job `sbom` w `devsecops-gates.yml` na archiwum `docker save`; obraz z GHCR po digeście na pushu (zależność od `build` w `baseline-ci.yml`); krok po `docker push` w `build` wariantu A |
| S2. Kiedy | na PR i pushu; tylko na pushu (jak B22) |
| S3. Co sprawdza fail closed | kod wyjścia Syft i kontrola treści; tylko kod wyjścia i obecność plików; pełna walidacja JSON Schema SPDX 2.3 i CycloneDX 1.7 |
| S4. Wymagany check | tak, w rulesetach `main` i `exp-variant-b`; nie, tryb doradczy |
| S5. Skąd job `sbom` bierze obraz | archiwum z `image-scan` jako artefakt (`needs: image-scan`); krok Syft w jobie `image-scan`; osobny build w jobie `sbom` |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-25. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta. Pytanie S5 doszło w trakcie wywiadu: powód autora przy S1 („ten sam obraz co image-scan”) wyklucza osobny build w jobie `sbom`.

| # | Decyzja | Powody autora |
|---|---|---|
| S1 | Tymczasowy job `sbom` w `devsecops-gates.yml`; SBOM z archiwum `docker save`. W E07-14 SBOM przechodzi do workflow B razem z krokami skanu (D1) | ten sam obraz co `image-scan`, bez zależności między workflowami, wariant A bez zmian (K2) |
| S2 | SBOM na PR i na pushu | mały koszt, dane do eksperymentu (SBOM z każdego przebiegu, także dla łatek GT) |
| S3 | Fail closed: błąd Syft i kontrola treści skryptem (pliki, JSON, wersje schematu, pakiety systemowe i Pythona, zgodność obu dokumentów, commit) | pusty SBOM nie przejdzie, wersja schematu jawna, spójne z innymi bramkami (skrypt, kody wyjścia, Job Summary) |
| S4 | `sbom` jest wymaganym checkiem w rulesetach `main` i `exp-variant-b` | fail closed ma sens tylko wtedy, jak pozostałe bramki |
| S5 | `image-scan` wysyła archiwum jako artefakt `image-archive` zaraz po `docker save`, a `sbom` (`needs: image-scan`) je pobiera | dokładnie ten sam obraz, osobny check `sbom`, prostota |

Decyzje agenta (techniczne, w ramach decyzji autora i ADR-0042):

- **Syft 1.57.2** z obrazu `anchore/syft:v1.57.2@sha256:e97e20b6e6d1699c60296b66ab337941724f9bd06ac279d893eda89601fc4b2a` (D9), z `SYFT_CHECK_FOR_APP_UPDATE=false`, z domyślnymi katalogerami dla obrazu.
- **Nazwa obrazu:** `--source-name ghcr.io/<repozytorium>` zamiast ścieżki archiwum. Bez `--source-version`, bo ta opcja usuwa digest obrazu z CycloneDX. Commit sprawdza się po etykiecie obrazu.
- **Pliki:** `sbom.spdx.json` i `sbom.cdx.json` w artefakcie `sbom` (retencja 90 dni, jak raporty). Bez formatu syft-json, zgodnie z decyzją z 2026-10-20 (dwa formaty).
- **Archiwum obrazu:** artefakt `image-archive` z retencją 1 dnia. To dane pośrednie przebiegu, a nie dane eksperymentu. Upload jest przed skanem i bramką Trivy, więc SBOM powstaje także wtedy, gdy `image-scan` blokuje obraz (`sbom` ma `if: !cancelled()`). Brak archiwum kończy job błędem (fail closed). Ten sam artefakt przyda się w E07-10 (DAST, D2).
- **`actions/download-artifact` v8.0.2** (`9000827c…`, wydanie z 2026-10-07), przypięta po SHA. ADR-0042 (D9) dopuszcza akcje artefaktów.
- **Kontrola `.github/scripts/sbom_check.py`** (tylko biblioteka standardowa, bez instalacji, w `PYTHON_IMAGE`):
  - kod 1: wersja inna niż SPDX-2.3 albo CycloneDX 1.7, dokument nie opisuje obrazu kontenera, brak pakietów `pkg:deb` albo `pkg:pypi`, różne digesty obrazu albo różne zbiory purl w SPDX i CycloneDX, etykieta `revision` inna niż commit przebiegu,
  - kod 2: brak albo nieczytelny plik, archiwum bez `manifest.json` z dokładnie jednym obrazem,
  - Job Summary: liczba pakietów i plików w obu formatach, pakiety według typu purl, wynik każdej kontroli, digest konfiguracji obrazu z archiwum (to `ImageID` z raportu Trivy w `image-scan`).

## Konsekwencje

- (+) Kryterium „SBOM dla każdego builda” jest spełnione: SBOM powstaje dla każdego obrazu, który buduje i skanuje `image-scan`, na PR i na pushu.
- (+) Wersje formatów są jawne i sprawdzane. Aktualizacja Syft, która zmieni domyślną wersję schematu, zatrzyma job, zamiast po cichu zmienić dane eksperymentu.
- (+) Test lokalny (2026-11-25): kroki joba odtworzone w Dockerze, z Syft i Pythonem z obrazów po digeście z workflow. Syft potrzebuje około 4 s.

  | Scenariusz | Wynik kontroli |
  |---|---|
  | czysta wersja | przechodzi (kod 0) |
  | etykieta `revision` z innego commita | kod 1 |
  | SPDX 2.2 (`spdx-json@2.2`) zamiast 2.3 | kod 1 |
  | SPDX i CycloneDX bez pakietów Pythona | kod 1 |
  | SPDX bez pakietów Pythona, CycloneDX pełny (różne zbiory purl) | kod 1 |
  | ucięty plik SPDX, brak pliku CycloneDX, archiwum, które nie jest plikiem tar | kod 2 |
  | Syft na nieistniejącym archiwum | krok Syft kończy się kodem 1 |

  actionlint 1.7.12 i zizmor 1.32.0 (`regular`) bez uwag.
- (+) Test w CI (2026-11-25), PR #34, dwa przebiegi `devsecops-gates`: 45629532620 (`5b1a025`) i 45629608294 (`c412081`). Wszystkie checki są zielone.
  - Job `sbom` trwa 21 s i 19 s:
    - pobranie archiwum około 4 s,
    - pobranie obrazów Syft i Pythona około 5 s,
    - Syft około 2 s,
    - wysyłka SBOM około 1 s,
    - kontrola około 1 s.
  - Wynik kontroli jak lokalnie:
    - SPDX-2.3 ma 126 pakietów i 2852 pliki, CycloneDX 1.7 ma 127 komponentów poza plikami (różnica to komponent systemu operacyjnego),
    - według typu purl: 87 `deb`, 38 `pypi`, 1 `generic`,
    - zbiory purl w obu dokumentach są identyczne, wynik PASS.
  - Artefakty `sbom` (590 kB po kompresji) i `image-archive` (85,5 MB, wygasa po 1 dniu).
  - Digest konfiguracji obrazu z archiwum (`sha256:0fdb5b6e…`) jest równy `ImageID` w `trivy-image.json` z artefaktu `image-scan-reports` tego samego przebiegu. SBOM i skan dotyczą więc tego samego obrazu (S5).
  - Na PR `GITHUB_SHA` to commit scalenia testowego (`refs/pull/34/merge`, `58d7931`), a nie głowa gałęzi. Etykieta `revision` w obrazie i kontrola używają tej samej wartości, więc są zgodne.
- (−) `sbom` czeka na `image-scan`, więc nie biegnie równolegle z bramkami. W CI zakończył się:
  - w przebiegu `c412081` sekundę przed `sast` (`image-scan` 49 s, `sbom` 19 s, `sast` 71 s), więc najdłuższa ścieżka się nie zmieniła,
  - w przebiegu `5b1a025` 48 s po `sast` i `iac` (`image-scan` 90 s, bo pobranie obrazów narzędzi trwało 21 s, a build 25 s).

  Przy obecnych czasach ścieżka `image-scan` → `sbom` jest zbliżona do najdłuższej i w zależności od przebiegu może ją wydłużyć. To materiał do H2a. Pojedyncze przebiegi, bez statystyki.
- (−) Wysyłka archiwum (85,5 MB) wydłuża `image-scan` o 6–7 s (dwa przebiegi), a pobranie wydłuża `sbom` o około 4 s.
- (−) Do E07-14 SBOM opisuje obraz z `image-scan`, a nie obraz opublikowany przez `build` w wariancie A. To dwa buildy tego samego kodu z różnymi digestami i tymi samymi pakietami (ADR-0048, konsekwencje). Atestacja SBOM w E07-09 wymaga jednego obrazu, czyli stanu po E07-14.
- (−) Digest w SBOM to digest manifestu policzony przez Syft z archiwum. Digest obrazu w GHCR po `docker push` jest prawdopodobnie inny (TODO: zweryfikować). Wspólny dla SBOM i raportu Trivy jest tylko digest konfiguracji, a ten trafia do Job Summary, nie do SBOM. Dla E07-09 obraz wskazuje podmiot atestacji (digest z rejestru), a nie pole w SBOM.
- (−) SBOM pokazuje stan obrazu, nie podatności. Według SP 800-204D sam SBOM nie wystarcza do zarządzania podatnościami (2.1, `docs/notes/nist-800-204d.md`), dlatego podatności ocenia `image-scan`.
- (−) Konfiguracja kontroli jest w repozytorium, więc PR może ją zmienić (ryzyko resztkowe, `docs/projekt-potoku.md` 4.6).
- Kolejne kroki:
  - **po scaleniu:** `sbom` jako wymagany check w rulesetach `main` i `exp-variant-b` (`settings.sh apply` za zgodą autora),
  - **E07-09:** atestacja SPDX razem z provenance, po digeście z rejestru,
  - **E07-10:** artefakt `image-archive` jako wejście DAST (D2),
  - **E07-14:** Syft w workflow B na obrazie, który publikuje `build`; usunięcie tymczasowego przekazania archiwum, jeśli skan i SBOM trafią do jednego joba.

## Źródła

- [@NIST-SP800-204D]: 1.2 (bez specyfikacji SBOM), 2.1, TEST-2*, BASE-4*, ATT-1*; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PS.3.2; notatki `docs/notes/nist-ssdf.md`.
- [@SLSA-1.2]: FAQ o SBOM i provenance; notatki `docs/notes/slsa.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-25):
  - pomoc `syft scan --help` w 1.57.2,
  - wydania Syft: https://github.com/anchore/syft/releases
  - wydania `actions/download-artifact`: https://github.com/actions/download-artifact/releases
