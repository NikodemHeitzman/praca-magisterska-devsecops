# 0047. Skanowanie IaC: Checkov, Trivy config i hadolint na obu warstwach Terraformu i Dockerfile

- **Status:** przyjęty
- **Data:** 2026-11-24
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0025](0025-narzedzie-iac-terraform.md) (Terraform), [0026](0026-stan-terraform-i-warstwy.md) (warstwy `shared/` i `work/`), [0042](0042-projekt-potoku-wariantu-b.md) (kroki B13, B14, B15; D5, D5a, D6, D7, D9, D13), [0043](0043-utwardzenie-workflowow.md) (H6, karencja 7 dni), [0045](0045-sast-semgrep-i-bandit.md) (T8, wspólna lista wyjątków), [`docs/projekt-potoku.md`](../projekt-potoku.md), [`docs/narzedzia.md`](../narzedzia.md), [`infra/terraform/README.md`](../../infra/terraform/README.md) (8 trafień Trivy z E05-04), zadanie E07-06, `experiment/ground-truth.yaml` (GT-09, GT-10, GT-11), [dziennik 2026-11-24](../log/2026-11-24.md)

## Kontekst

ADR-0042 przewidział job `iac` z trzema narzędziami:
- B13: Checkov na `infra/terraform` i `app/Dockerfile` (GT-09, GT-10, GT-11), blokuje każdą nieudaną kontrolę, bo bez platformy nie podaje ważności (D5),
- B14: Trivy config na tych samych plikach, blokuje od `LOW` (D5a),
- B15: hadolint na `app/Dockerfile`, blokuje poziom `error` (D7). Nie jest detektorem GT-09 (`docs/narzedzia.md`, sekcja 5).

Narzędzia działają z obrazów po digeście albo z PyPI w dokładnej wersji (D9). Trafienia czystej wersji idą na listę wyjątków (D6), a bramki ignorują wyciszenia w kodzie (D13). E05-04 zostawił 8 trafień Trivy config w czystej wersji do rozstrzygnięcia w tym zadaniu.

Rozpoznanie agenta (2026-11-24, kod z `main` po `47fe399`):

- **Wersje** (najnowsze wydania, które przeszły karencję 7 dni, H6):
  - Checkov 3.4.5 (PyPI, 2026-11-12, `requires_python >=3.10`, Apache-2.0). Wydania 3.4.6–3.4.10 (2026-11-19 do 2026-11-24) są za nowe. `docs/narzedzia.md` podaje jeszcze 3.3.29,
  - Trivy v0.76.2 (2026-11-05), obraz `ghcr.io/aquasecurity/trivy` z indeksem `sha256:8f6bb947dbc528902e11f2f5be52f7b519f6a39d5d148f41166f2040499768fb` (ten sam digest w Docker Hub). v0.76.1 i v0.76.2 to wydania poprawkowe z aktualizacjami bezpieczeństwa obrazu i zależności,
  - hadolint v2.15.1 (2026-07-31), obraz `ghcr.io/hadolint/hadolint` z indeksem `sha256:32dac94127fd60b7b7e3fbfc65e1383b9b5e25c9bfd7b8536de7a539fe68a12d`.
- **Instalacja Checkova:** `uv pip compile` z `checkov==3.4.5` i PyYAML (dla skryptu bramki), Python 3.12, Linux, `--exclude-newer 2026-11-17` daje 96 pakietów z hashami. Instalacja `--no-deps --require-hashes` w kontenerze `python:3.12-slim` przechodzi, `pip check` bez błędów.
- **Formaty i kody wyjścia:**
  - Checkov zapisuje kilka formatów w jednym przebiegu (`-o json -o sarif --output-file-path`). Kod wyjścia 1 przy nieudanych kontrolach, 0 bez nich. Pole `severity` jest `null`. Z `--quiet` raport JSON nie zawiera kontroli zaliczonych ani pominiętych,
  - Checkov wywołany z `-d infra/terraform -f app/Dockerfile` skanuje tylko Terraform. Działa za to `-d infra/terraform -d app --framework terraform dockerfile`: jeden raport z oboma typami. Kod 2 oznacza awarię narzędzia (np. wyjątek przy zapisie SARIF z `--compact` w tym wywołaniu),
  - Trivy config ma formaty `json` i `sarif`, przyjmuje jeden cel na wywołanie, a kod wyjścia przy zgłoszeniach ustawia `--exit-code` (domyślnie 0). Ścieżki w raporcie są względne wobec celu,
  - Trivy na `infra/terraform` w kopii roboczej autora podał trafienia z `work/` dwa razy (14 zamiast 8). Przyczyną były lokalne katalogi `.terraform/` (w `.gitignore`): w czystym checkoucie (`git archive`) ten sam skan daje 8 unikatowych trafień,
  - hadolint ma poziomy `error`, `warning`, `info`, `style`, opcję `--failure-threshold` (domyślnie `info`) i format `sarif`. To zamyka TODO z ADR-0042 o poziomach hadolint.
- **Czysta wersja:**

  | Narzędzie | `work/` | `shared/` | `app/Dockerfile` |
  |---|---|---|---|
  | Trivy config | 6 (AWS-0178, AWS-0104 ×2, AWS-0089, AWS-0090, AWS-0132) | 2 (AWS-0089, AWS-0132) | 0 |
  | Checkov | 9 | 6 | 0 (53 zaliczone) |
  | hadolint | — | — | 0 |

  Trafienia Checkova: CKV_AWS_145 i CKV_AWS_18, CKV_AWS_144, CKV2_AWS_62 (po dwa: kubełek stanu i kubełek załączników), CKV_AWS_21, CKV2_AWS_61, CKV2_AWS_11, CKV_AWS_88, CKV_AWS_126, CKV_AWS_260, CKV_AWS_297.
- **Wyciszenia w kodzie:**
  - Checkov: `#checkov:skip=<ID>` przenosi zgłoszenie z `failed_checks` do `skipped_checks` z polem `suppress_comment`. Opcji wyłączającej nie ma, ale ślad zostaje w raporcie JSON (bez `--quiet`),
  - Trivy: `#trivy:ignore:<ID>` usuwa zgłoszenie z raportu bez śladu, także z `--include-non-failures`. Opcji wyłączającej nie ma,
  - hadolint: `--disable-ignore-pragma` wyłącza komentarze `# hadolint ignore=`.
- **Pliki konfiguracyjne czytane automatycznie:** Trivy `trivy.yaml` i `.trivyignore` (wyłączane przez `--config ""` i `--ignorefile ""`), Checkov `.checkov.yaml`, hadolint `.hadolint.yaml`. W repozytorium nie ma żadnego z nich.

## Czynniki decyzyjne

- skuteczność wobec GT-09, GT-10 i GT-11 (M1, H1) i obsługa trafień czystej wersji bez fałszywych blokad (M6),
- spójność z polityką bramek ADR-0042 (D5, D6, D13) [@OWASP-DevSecOps-Guideline],
- zgodność z SP 800-204D (PRE-5*) [@NIST-SP800-204D] i SSDF (PW.9.2, PW.6.2) [@NIST-SP800-218],
- odtwarzalność (K5) i lekki potok: mało kodu własnego, niski koszt.

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| I1. Zakres skanu Terraformu | `work/` i `shared/`; tylko `work/` (tam trafią łatki GT); `shared/` tylko doradczo |
| I2. 15 trafień Checkova w czystej wersji | wszystkie na listę wyjątków; tanie poprawić w Terraformie, resztę na listę; wyłączyć nieadekwatne reguły (`--skip-check`) |
| I3. `#trivy:ignore` (D13) | bramka traktuje komentarz jak zgłoszenie; ryzyko opisane w 5.3 |
| I4. Pliki konfiguracyjne skanerów | bramka blokuje ich obecność; tylko opcje wyłączające (Trivy); pominąć, ryzyko w 5.3 |
| I5. Zakładka Security | JSON i SARIF w artefaktach i SARIF trzech narzędzi do code scanning; tylko artefakty |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-24. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta.

| # | Decyzja | Powody autora |
|---|---|---|
| I1 | Checkov i Trivy config skanują obie warstwy Terraformu (`infra/terraform/work`, `infra/terraform/shared`) i `app/Dockerfile`; hadolint `app/Dockerfile` | całe IaC pod kontrolą (warstwa stała to też kod w repozytorium), stan Terraformu jest wrażliwy, mały koszt |
| I2 | Wszystkie trafienia Checkova czystej wersji idą na listę wyjątków `.github/gate-exceptions.yaml` z uzasadnieniem; kod czystej wersji bez zmian | zgodnie z D6, bez zmian infrastruktury (poprawka zmieniłaby czystą wersję i wymagała nowego `apply`/`destroy`) |
| I3 | Bramka traktuje komentarz `trivy:ignore` w skanowanych plikach jak zgłoszenie blokujące | mały koszt. Na pytanie, czy przy wyższym koszcie luka zostałaby otwarta, autor odpowiedział, że decyduje koszt |
| I4 | Obecność `.checkov.yaml`/`.checkov.yml`, `.hadolint.yaml`/`.hadolint.yml`, `trivy.yaml` i `.trivyignore` w repozytorium blokuje job `iac`; Trivy dodatkowo z `--config ""` i `--ignorefile ""` | konfiguracja skanerów tylko w workflow, odtwarzalność (wynik nie zależy od plików spoza manifestu wersji), mały koszt |
| I5 | Raporty JSON i SARIF w artefakcie `iac-reports`, SARIF Checkova, Trivy i hadolint do zakładki Security | spójność z jobami `secrets` i `sast`, historia alertów (GitHub śledzi alert w czasie, artefakty wygasają) |

Decyzje agenta (techniczne, w ramach decyzji autora i ADR-0042):

- **Checkov 3.4.5 z PyPI** w Pythonie runnera, jak Semgrep i Bandit w `sast`. `.github/tools/iac.txt` wygenerowany przez `uv pip compile --generate-hashes` dla Pythona 3.12 i Linuksa z `--exclude-newer` 7 dni wstecz (96 pakietów, razem z PyYAML dla skryptu bramki). Jedno wywołanie `-d infra/terraform -d app --framework terraform dockerfile` z `--skip-download --skip-results-upload` (bez połączeń z platformą Prisma Cloud), bez `--quiet` (pełny raport, M1). Kod 1 (nieudane kontrole) jest oczekiwany, inny niezerowy kod przerywa job.
- **Trivy config na kopii śledzonych plików** (`git ls-files infra/terraform app/Dockerfile`) ułożonej według ścieżek repozytorium. Jeden cel daje jeden raport ze ścieżkami względem korzenia repozytorium (także w SARIF dla zakładki Security), a lokalne `.terraform/` nie wpływa na wynik. Trivy działa z `--skip-check-update` (reguły wbudowane w binarkę), `--config ""` i `--ignorefile ""`.
- **hadolint** z `--disable-ignore-pragma --no-fail`: raport powstaje przy każdym zgłoszeniu, więc niezerowy kod to awaria.
- **Bramka `.github/scripts/iac_gate.py`** (wzór `sast_gate.py`):
  - Checkov: nieudane kontrole i kontrole wyciszone `#checkov:skip` (`skipped_checks`) blokują (D5, D13). Ścieżka z pola `repo_file_path`,
  - Trivy config: `Status: FAIL` od `LOW` blokuje, `UNKNOWN` tylko w danych (D5a),
  - hadolint: poziom `error` blokuje (D7),
  - komentarz `trivy:ignore` w plikach spod `--scan-path` (I3) i plik konfiguracyjny skanera w dowolnym miejscu repozytorium (I4) blokują i nie podlegają wyjątkom,
  - wyjątki z `.github/gate-exceptions.yaml` po narzędziu (`checkov`, `trivy-config`, `hadolint`), regule i ścieżce. Nieużyty wyjątek daje ostrzeżenie,
  - kod 2 (fail closed): brak albo nieczytelny raport, raport bez wyników typu `terraform` albo `dockerfile` (nic nie zeskanowano), plik, którego Checkov nie sparsował, nieistniejąca ścieżka skanu. W `sast` błędy częściowe tylko ostrzegają (T5), ale w IaC nieparsowalny plik oznacza zasób bez żadnej kontroli,
  - kod 1 przy zgłoszeniu blokującym, 0 w pozostałych przypadkach. Tabela w podsumowaniu przebiegu (Job Summary).
- **Wyjątki czystej wersji (I2):** 22 wpisy dla 23 trafień (dwa trafienia AWS-0104 w jednym pliku pokrywa jeden wpis). Uzasadnienia zatwierdził autor 2026-11-24: 18 trafień ma podstawę w istniejących decyzjach (ADR-0024, README Terraformu, E08-01), a dla pięciu reguł Checkova bez wcześniejszej decyzji autor wskazał powody w wywiadzie:
  - CKV_AWS_144 (replikacja między regionami): SCP konta dopuszcza w UE tylko `eu-north-1` (ADR-0030), koszt, dane efemeryczne (stan jest wersjonowany),
  - CKV2_AWS_62 (powiadomienia o zdarzeniach S3): koszt odbiorcy powiadomień, dane fikcyjne i efemeryczne,
  - CKV2_AWS_61 (cykl życia kubełka załączników): kubełek istnieje tylko w czasie sesji,
  - CKV_AWS_126 (szczegółowy monitoring EC2): funkcja płatna, logi i alarmy rozstrzyga E08-02,
  - CKV_AWS_297 (harmonogram sprzątania bez klucza KMS klienta): brak danych wrażliwych, koszt i prostota.

## Konsekwencje

- (+) Kroki B13, B14 i B15 z `docs/projekt-potoku.md` są zrealizowane. Zamknięte TODO z ADR-0042: nazwy poziomów i opcja progu hadolint 2.15.1, kody wyjścia Checkova, Trivy config i hadolint, digesty obrazów Trivy i hadolint. Otwarte pytanie z E05-04 (sposób liczenia 8 trafień Trivy) rozstrzyga D6 z I2.
- (+) Test lokalny (2026-11-24): kroki joba odtworzone na kopii kopii roboczej (`git ls-files`), Checkov w kontenerze `python:3.12-slim` z tymi samymi pakietami, Trivy i hadolint z obrazów po digeście z workflow. Czas wszystkich kroków skanu i bramki około 11–17 s.

  | Scenariusz | Checkov | Trivy config | hadolint | Bramka |
  |---|---|---|---|---|
  | czysta wersja | 15 (wyjątki) | 8 (wyjątki) | 0 | przechodzi |
  | GT-09 (usunięte `USER`) | CKV_DOCKER_3 | DS-0002 (HIGH) | 0 | blokuje |
  | GT-10 (ingress tcp/22 z `0.0.0.0/0`) | CKV_AWS_24, CKV_AWS_23 | AWS-0107 (HIGH), AWS-0124 (LOW) | — | blokuje |
  | GT-11 (`encrypted = false` na wolumenie głównym) | CKV_AWS_8 | AWS-0131 (HIGH) | — | blokuje |
  | GT-11 i `#checkov:skip=CKV_AWS_8` | CKV_AWS_8 (wyciszona w kodzie) | AWS-0131 | — | blokuje |
  | `#trivy:ignore:AWS-0178` | 15 (wyjątki) | 7 (trafienie znika z raportu) | 0 | blokuje (I3), ostrzeżenie o nieużytym wyjątku |
  | `.checkov.yaml` w korzeniu | — | — | — | blokuje (I4) |
  | `ADD` w Dockerfile | CKV_DOCKER_4 | DS-0005 (LOW) | DL3020 (`error`) | blokuje |
  | brak raportu, raport bez Dockerfile, nieistniejąca ścieżka skanu | — | — | — | kod 2 |

  AWS-0124 (brak opisu reguły SG) i CKV_AWS_23 to skutki uboczne łatki próbnej bez pola `description`. Docelowa łatka GT-10 powstaje w E04.
- (+) Test w CI (2026-11-24):
  - **PR #28** (czysta wersja, `9e5585f`): wszystkie checki zielone. `iac` przechodzi w około 62 s (przebieg 45481039030): instalacja Checkova 21 s, trzy skany razem około 5 s, wysyłka trzech SARIF około 22 s. Python runnera 3.12.3. Liczby zgłoszeń jak lokalnie: Checkov 15, Trivy config 8, hadolint 0, wszystkie trafienia Checkova i Trivy na liście wyjątków,
  - **PR #29** (szkic, łatki GT-09, GT-10 i GT-11 razem; do zamknięcia bez scalania): `iac` blokuje 6 zgłoszeń, czyli CKV_DOCKER_3, CKV_AWS_8, CKV_AWS_24, DS-0002, AWS-0131 i AWS-0107 (łatka z polem `description`, więc bez AWS-0124 i CKV_AWS_23). Artefakt `iac-reports` jest w obu przebiegach.
- (+) Każda pozycja GT-09, GT-10 i GT-11 ma po dwa blokujące detektory IaC, jak przewiduje katalog. Żaden wyjątek czystej wersji nie dotyczy reguł tych pozycji.
- Obserwacja z PR #29: GT-09 blokuje także job `sast`. Zestaw `p/default` Semgrepa zawiera regułę `dockerfile.security.missing-user.missing-user` (ważność ERROR), a `sast` skanuje `app/`, więc także `app/Dockerfile` (ADR-0045, T3). Katalog (`experiment/ground-truth.yaml`) wymienia dla GT-09 tylko Checkov i Trivy. Czy dopisać Semgrep jako detektor GT-09, rozstrzyga autor przed zamrożeniem katalogu (TODO: decyzja autora). Do analizy w E09: wykrycie GT-09 przez SAST w liczbie detektorów i klasie narzędzi.
- (−) Wyjątek dopasowany po narzędziu, regule i ścieżce ukrywa też nowe trafienie tej samej reguły w tym samym pliku, np. kolejną regułę wyjścia do `0.0.0.0/0` w `security.tf` (AWS-0104). Żadna pozycja katalogu tego nie wymaga.
- (−) Trivy, Checkov i hadolint wbudowują reguły w wersję, więc zmiana wersji zmienia zestaw kontroli i liczbę trafień czystej wersji. Wersje zamarzają w E07-14 (K5).
- (−) Konfiguracja bramki (workflow, skrypt, lista wyjątków) jest w repozytorium, więc PR może ją zmienić. To ryzyko resztkowe z `docs/projekt-potoku.md` (4.6), jak w ADR-0044–ADR-0046. I4 zamyka tylko jedną drogę: pliki konfiguracyjne skanerów.
- (−) Code scanning dostaje 23 alerty czystej wersji z Checkova i Trivy, bo SARIF zawiera także trafienia z listy wyjątków (I5). Lista wyjątków działa tylko w bramce.
- Kolejne kroki:
  - ~~**po scaleniu:** `iac` jako wymagany check w rulesetach `main` i `exp-variant-b` (`settings.sh apply` za zgodą autora)~~ wykonane 2026-11-24: PR #28 scalony (`fd2247e`), `apply` zaktualizował rulesety `main`, `tags` i `exp-variant-b`; API potwierdza `iac` jako wymagany check w `main` i `exp-variant-b`. PR #29 zamknięty bez scalania. Przebieg na pushu do `main` (`devsecops-gates` 45482045342, `fd2247e`): `secrets`, `sast`, `sca` i `iac` przechodzą; `baseline-ci` i `workflow-lint` też,
  - **E07-11:** data wygaśnięcia w formacie wyjątku,
  - **E07-12:** zbiorczy raport czyta `checkov.json`, `trivy-config.json` i `hadolint.json` z artefaktu `iac-reports`,
  - **E07-14:** zamrożenie wersji z `variant-b.yaml`.

## Źródła

- [@NIST-SP800-204D]: PRE-5*; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PW.9.2, PW.6.2; notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-DevSecOps-Guideline]: skanowanie IaC w CI, „fail closed”; notatki `docs/notes/owasp-devsecops.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-24):
  - pomoc `checkov --help` w 3.4.5 i PyPI, historia wydań: https://pypi.org/project/checkov/#history
  - pomoc `trivy config --help` w 0.76.2 i informacje o wydaniach: https://github.com/aquasecurity/trivy/releases
  - pomoc `hadolint --help` w 2.15.1: https://github.com/hadolint/hadolint/releases/tag/v2.15.1
