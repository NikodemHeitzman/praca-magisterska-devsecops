# 0046. SCA: pip-audit z bazą OSV na zależnościach runtime, kontrola zgodności lockfile'a, Dependabot

- **Status:** przyjęty
- **Data:** 2026-11-24
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0008](0008-menedzer-zaleznosci-uv.md) (`uv.lock` i eksport `requirements.txt`), [0012](0012-s3-w-testach-moto-w-procesie.md) (`--no-dev`), [0041](0041-zamrozenie-wariantu-a.md) (kontrola zgodności w B), [0042](0042-projekt-potoku-wariantu-b.md) (kroki B10, B11, B12; D5, D6, D7, D9, D11), [0043](0043-utwardzenie-workflowow.md) (H3, H6), [0045](0045-sast-semgrep-i-bandit.md) (T8), [`docs/projekt-potoku.md`](../projekt-potoku.md), [`docs/narzedzia.md`](../narzedzia.md), [`.github/workflows/devsecops-gates.yml`](../../.github/workflows/devsecops-gates.yml), [`.github/scripts/sca_gate.py`](../../.github/scripts/sca_gate.py), [`.github/gate-exceptions.yaml`](../../.github/gate-exceptions.yaml), [`.github/tools/sca.in`](../../.github/tools/sca.in), zadanie E07-05, `experiment/ground-truth.yaml` (GT-07), [dziennik 2026-11-24](../log/2026-11-24.md)

## Kontekst

ADR-0042 przewidział job `sca` z dwoma krokami:
- B10: pip-audit na `app/requirements.txt`, blokuje GT-07 (`jinja2==3.1.2`),
- B11: kontrola, że `requirements.txt` jest eksportem `uv.lock`. pip-audit czyta inny plik niż ten, z którego powstaje obraz (ADR-0008, ADR-0041).

`dependency-review-action` (B12) jest poza wariantem B (D7). Narzędzia bez skali ważności blokują każde zgłoszenie (D5), instalujemy je z PyPI w dokładnej wersji (D9). Dependabot (alerty i security updates) włączono w E07-02 (ADR-0043, H6). Aktualizacje wersji dla Pythona wyłączono, bo Dependabot zmieniał `requirements.txt` bez `uv.lock`.

Rozpoznanie agenta (2026-11-24, kontener `python:3.14-slim`, czysty eksport `HEAD`):

- **Wersja:** pip-audit 2.10.1 (2026-06-10) jest najnowszy i przeszedł karencję 7 dni (H6). Wymaga Pythona `>=3.10`.
- **Formaty wyjścia:** `columns`, `json`, `cyclonedx-json`, `cyclonedx-xml` i `markdown`. **Bez SARIF.**
- **Bazy podatności:** `pypi` (domyślna, Python Packaging Advisory Database przez PyPI JSON API), `osv` (`https://api.osv.dev/v1/query`) i `esms`.
- **Ważność:** pip-audit nie ma filtra ważności, a raport JSON nie zawiera poziomu ważności.
- **Kody wyjścia:** 0 to brak znanych podatności, 1 to znalezione podatności (README `pypa/pip-audit`). Lokalnie sprawdzono, że kod 1 pojawia się też przy błędzie narzędzia: brak pliku wymagań, pakiet nieznany w PyPI przy `--strict`, niedostępna baza. W takim wypadku raport nie powstaje. Kod wyjścia nie odróżnia więc zgłoszeń od awarii.
- **Czysta wersja:** obie bazy dają 0 podatności w 38 pakietach. 39. pakiet, `tzdata` z markerem `sys_platform == 'win32'`, nie dotyczy Linuksa. Czas skanu: PyPI około 1 s, OSV około 11 s.
- **Łatka próbna GT-07** (`jinja2==3.1.2` w `pyproject.toml`, `uv lock`, eksport): obie bazy zgłaszają te same 5 podatności (CVE-2024-22195, CVE-2024-34064, CVE-2024-56201, CVE-2024-56326 i CVE-2025-27516; ID PYSEC-2026-1471…1475 z aliasami GHSA). Raport JSON zawiera każdą z nich dwa razy (10 wpisów przy jednym pakiecie). Przyczyna: TODO: zweryfikować.
- **Zgodność lockfile'a:** eksport tym samym poleceniem co w nagłówku `requirements.txt` daje identyczny plik. Inna ścieżka `-o` zmienia tylko nagłówek. Zmieniony `uv.lock` przy starym `requirements.txt` wykrywa porównanie eksportu. Zmieniony `pyproject.toml` bez `uv lock` wykrywa tylko `uv lock --check`, bo `uv export --frozen` czyta `uv.lock` bez sprawdzania.
- **Dependabot:** API GitHuba 2026-11-24 zwraca dla `vulnerability-alerts` 204 (włączone), dla `automated-security-fixes` `{"enabled":true,"paused":false}`, a otwartych alertów jest 0.

## Czynniki decyzyjne

- skuteczność wobec GT-07 (M1, H1) i brak fałszywych alarmów na czystej wersji (M6),
- trafność eksperymentu: odtwarzalność (K5, zasada 6 z `AGENTS.md`), stały czas joba (H2a), jedno źródło danych w serii,
- zgodność z SP 800-204D (TEST-2*, BASE-4*) [@NIST-SP800-204D] i SSDF (PW.4.4, PW.4.1) [@NIST-SP800-218], polityka bramek ADR-0042 [@OWASP-DevSecOps-Guideline],
- lekki potok: mało narzędzi, kodu własnego i akcji firm trzecich.

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| Z1. Baza podatności | OSV; PyPI (domyślna); obie |
| Z2. Zakładka Security | tylko raport JSON; własna konwersja JSON → SARIF; JSON + CycloneDX z podatnościami |
| Z3. Python dla pip-audit | kontener `python:3.14-slim` po digeście; Python 3.14 przez `uv python install`; Python 3.12 runnera |
| Z4. Zakres zależności | tylko runtime (`--no-dev`); runtime i grupa dev |
| Z5. Skąd uv do kontroli zgodności | PyPI z hashami w tym samym kontenerze; akcja `astral-sh/setup-uv` jak w A; obraz `ghcr.io/astral-sh/uv` po digeście |
| Z6. OSV-Scanner i Safety CLI | tylko opis jako alternatywy; OSV-Scanner jako druga bramka; OSV-Scanner jako seria porównawcza poza bramką |
| Z7. Nowa CVE w czystej wersji w trakcie serii | wyjątek z datą i odchylenie w dzienniku; nowa czysta wersja i seria od nowa; bramka blokuje, analiza odfiltrowuje |
| Z8. API OSV niedostępne | do 3 prób, potem blokada; od razu blokada; zapasowo baza PyPI |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-24. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta.

| # | Decyzja | Powody autora |
|---|---|---|
| Z1 | pip-audit z bazą OSV (`--vulnerability-service osv`) | spójność z katalogiem (GT-07 sprawdzono w OSV, `experiment/ground-truth.yaml`), koszt pomijalny |
| Z2 | Tylko raport JSON w artefakcie `sca-reports`, bez SARIF | podatne zależności pokazuje w zakładce Security Dependabot, brak własnego kodu |
| Z3 | pip-audit w kontenerze `python:3.14-slim` przypiętym digestem | ten sam Python co aplikacja (markery rozstrzygane jak w obrazie), odporność na zmiany runnera |
| Z4 | Tylko zależności runtime: `app/requirements.txt`, czyli eksport `--no-dev` | grupa dev nie trafia do obrazu, mniej wyjątków |
| Z5 | uv 0.13.6 z PyPI z hashami, w tym samym kontenerze co pip-audit | jedno środowisko |
| Z6 | OSV-Scanner i Safety CLI poza wariantem B, opisane jako alternatywy | ta sama baza (OSV-Scanner korzysta z bazy OSV.dev, README `google/osv-scanner`) |
| Z7 | Nowa podatność w czystej wersji w trakcie serii: wpis w `.github/gate-exceptions.yaml` z datą i uzasadnieniem, odchylenie w dzienniku badawczym, seria trwa | realizm (tak postępuje mały zespół: akceptuje ryzyko z datą i planuje aktualizację) |
| Z8 | Gdy pip-audit nie zapisze raportu, job ponawia skan do 3 razy (przerwa 15 s), potem blokuje | mniej fałszywych blokad |

Decyzje agenta (techniczne, w ramach decyzji autora i ADR-0042):

- **pip-audit 2.10.1** z `--disable-pip --strict`: pip-audit nie rozwiązuje zależności, bo `requirements.txt` ma wszystkie pakiety z hashami. Pakiet, którego nie da się sprawdzić, przerywa audyt. Do tego `--aliases on --desc on`, bo bramka dopasowuje wyjątki także po aliasach, a opis zostaje w danych.
- **Instalacja:** `.github/tools/sca.txt` wygenerowany przez `uv pip compile --generate-hashes` dla Pythona 3.14 i Linuksa, z `--exclude-newer` 7 dni wstecz. Zawiera pip-audit, uv i PyYAML dla skryptu bramki. Instalacja `pip install --no-deps --require-hashes` do środowiska wirtualnego w `$RUNNER_TEMP/sca`, które kolejne kontenery tego samego obrazu montują ponownie.
- **Kontrola zgodności (B11)** działa na kopii `app/`, więc katalog roboczy zostaje tylko do odczytu:
  - `uv lock --check` (wykrywa `pyproject.toml` niezgodny z `uv.lock`),
  - eksport tym samym poleceniem co w nagłówku i `diff -u` z `app/requirements.txt`. Diff trafia do artefaktu (`requirements-export.diff`; pusty plik oznacza zgodność).
  - `UV_PYTHON_DOWNLOADS=never`, żeby uv użył Pythona z obrazu.
- **Bramka nie opiera się na kodzie wyjścia pip-audit**, tylko na raporcie (fail closed). `.github/scripts/sca_gate.py` zwraca 2 (nieczytelne wejście), gdy raportu nie ma, nie jest poprawnym JSON-em, ma pustą listę zależności albo pakiet z `skip_reason`. Zwraca 1, gdy jest podatność spoza listy wyjątków, a 0 w pozostałych przypadkach.
- **Duplikaty:** bramka liczy unikatowe trójki (pakiet, wersja, ID), a w podsumowaniu przebiegu podaje też surową liczbę wpisów raportu.
- **Wyjątek pip-audit** w `.github/gate-exceptions.yaml`: `tool: pip-audit`, `rule` = ID podatności albo dowolny alias (PYSEC, GHSA, CVE), `path: app/requirements.txt`. Nieużyty wyjątek daje ostrzeżenie.
- **Krok pip-audit działa też po nieudanej kontroli zgodności** (`!cancelled()`), więc dane o podatnościach zostają w artefakcie.

## Konsekwencje

- (+) Kroki B10 i B11 z `docs/projekt-potoku.md` są zrealizowane. Zamknięte TODO z ADR-0042: filtr ważności w pip-audit (nie istnieje, blokuje każde zgłoszenie) i kody wyjścia pip-audit (0 i 1, kod 1 także przy błędzie, stąd bramka oparta na raporcie).
- (+) Test lokalny (2026-11-24, kroki joba wyciągnięte z workflow i uruchomione w kontenerze `python:3.14-slim` po digeście z workflow):

  | Scenariusz | Zgodność lockfile'a | pip-audit | Bramka |
  |---|---|---|---|
  | czysta wersja | przechodzi | raport, 38 pakietów | przechodzi, 0 podatności |
  | GT-07 (`pyproject.toml`, `uv.lock`, eksport) | przechodzi | raport | blokuje: 5 unikatowych podatności (10 wpisów) |
  | GT-07, `requirements.txt` nieaktualny | blokuje (diff eksportu) | raport, 0 podatności | przechodzi |
  | `pyproject.toml` bez `uv lock` | blokuje (`uv lock --check`) | raport, 0 podatności | przechodzi |
  | GT-07 z wyjątkiem po aliasie GHSA i jednym nieużytym | przechodzi | raport | blokuje 4, 1 wyjątek, ostrzeżenie o nieużytym wyjątku |
  | brak raportu po 3 próbach | — | kod 1 | — |
  | raport brakujący, nieczytelny, pusty, z `skip_reason` | — | — | kod 2 |

- (+) Scenariusz „`requirements.txt` nieaktualny” pokazuje, czemu B11 jest potrzebne. Gdy łatka zmienia `uv.lock`, a nie eksport, pip-audit nie widzi podatnej wersji, a obraz ją instaluje.
- (+) Czysta wersja przechodzi bez wyjątków SCA.
- (−) Baza OSV zmienia się w czasie i nie da się jej zamrozić. Podatność opublikowana w trakcie serii zmieni wynik czystej wersji (Z7). Ślad zostaje w raportach JSON w artefaktach przebiegów. Materiał do 5.3 (odtwarzalność).
- (−) Job zależy od dostępności `api.osv.dev` i PyPI (instalacja narzędzi). Trwała awaria blokuje (fail closed), a ponowienia (Z8) wydłużają job najwyżej o około 30 s przerw.
- (−) pip-audit nie ma SARIF, więc wynik bramki SCA nie trafia do zakładki Security (Z2). Widać tam tylko alerty Dependabota, które działają niezależnie od potoku.
- (−) pip-audit nie wykryje złośliwego pakietu bez opublikowanej podatności (CICD-SEC-3, `docs/projekt-potoku.md`, 3.1).
- (−) DEPLOY-REQ-2 nadal bez bezpośredniego pokrycia (D7). pip-audit na PR pokazuje podatne wersje przed scaleniem, ale nie przegląda zmian zależności.
- (−) Lista wyjątków i skrypt bramki są w repozytorium, więc PR może je zmienić. To ryzyko resztkowe z `docs/projekt-potoku.md` (4.6), jak w ADR-0044 i ADR-0045.
- (−) Format wyjątku nie ma jeszcze daty wygaśnięcia, której wymaga Z7. Pole i proces doda E07-11.
- Dependabot (kryterium E07-05): alerty i security updates włączone w E07-02 (ADR-0043, H6), stan potwierdzony 2026-11-24 (Kontekst). To kontrola platformy (B04), poza pomiarem (ADR-0042, sekcja 4.4).
- Kolejne kroki:
  - **po scaleniu:** `sca` jako wymagany check, `settings.sh apply` za zgodą autora,
  - **E07-12:** zbiorczy raport musi usuwać duplikaty z raportu pip-audit,
  - **E07-14:** zamrożenie wersji z `variant-b.yaml`.

## Źródła

- [@NIST-SP800-204D]: TEST-2*, BASE-4*; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PW.4.1, PW.4.4; notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-Top10-CICD]: CICD-SEC-3; notatki `docs/notes/owasp-devsecops.md`.
- [@OWASP-DevSecOps-Guideline]: SCA w CI, „fail closed”; notatki `docs/notes/owasp-devsecops.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-24):
  - pomoc `pip-audit --help` w 2.10.1 i README https://github.com/pypa/pip-audit (bazy podatności, kody wyjścia),
  - PyPI, historia wydań `pip-audit`: https://pypi.org/project/pip-audit/#history
  - OSV-Scanner, README https://github.com/google/osv-scanner (baza OSV.dev; ostatnie wydanie v2.7.1),
  - Safety CLI: https://pypi.org/project/safety/ (bez uwierzytelnienia narzędzie prosi o utworzenie konta albo logowanie; plan Free dla jednego użytkownika, niezalecany do zastosowań komercyjnych),
  - REST API GitHuba: `vulnerability-alerts`, `automated-security-fixes`, `dependabot/alerts`.
