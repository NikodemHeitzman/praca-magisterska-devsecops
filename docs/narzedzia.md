# Narzędzia potoku: dokumentacja i wersje

> **Status:** szkic (E02-10, sesja 2026-10-18). Sekcje 1–3 mają dane z oficjalnych źródeł. Sekcja 4 ma analizę reguł dla pozycji katalogu o niepewnej detekcji; jej skutki dla katalogu i H1 czekają na decyzję autora (4.2). Podział ról narzędzi zapada w ADR-ach i E07.

Plik zbiera w jednym miejscu narzędzia rozważane dla wariantu B potoku, ich dokumentację i wersje. Służy dwóm celom:

1. **Odtwarzalność (K4, TN7 w `docs/metodyka.md`).** Wersje z tego pliku są punktem wyjścia do przypięcia wersji przy zamrożeniu potoku (P1 w `experiment/PROTOCOL.md`).
2. **Źródła faktów o narzędziach.** Książki z rdzenia opisują starsze wersje narzędzi (`docs/notes/ksiazki.md`, uwaga 7), więc fakty o działaniu narzędzi opieramy na dokumentacji z tego pliku.

**Kandydaci, nie decyzje.** Kolumna „Rola” to propozycja z tabeli rekomendacji NIST SP 800-204D (`docs/notes/nist-800-204d.md`) i z katalogu podatności (`experiment/ground-truth.yaml`). Ostateczny wybór narzędzi i bramek zapada w ADR-ach i w E07.

## 0. Jak zebrano dane

- **Data pobrania:** 2026-10-18.
- **Wersja najnowsza** to wynik `gh api repos/<właściciel>/<repo>/releases/latest` (pole `tag_name` i `published_at`). Dla narzędzi z PyPI wersję potwierdzono w `https://pypi.org/pypi/<pakiet>/json` (pole `info.version`), skąd pochodzi też `requires_python`.
- **SHA akcji** to commit, na który wskazuje tag (`git/ref/tags/<tag>`; dla tagów opisanych rozwinięte przez `git/tags/<sha>`). Dla `bridgecrewio/checkov-action` i `github/codeql-action` tag wzięto z listy tagów (`repos/<repo>/tags`), bo pole „latest release” wskazuje tam co innego (sekcja 5).
- **Licencja** z pola `license.spdx_id` w API GitHuba.
- **Linki do dokumentacji** sprawdzono 2026-10-18 (`curl -L`, HTTP 200). Podajemy adres docelowy po przekierowaniach, bo dokumentacja GitHuba zmieniła strukturę adresów.

Wersja najnowsza na dzień pobrania **nie jest** wersją przypiętą. Wersję przypiętą, digest obrazu i SHA akcji zapisujemy przy zamrożeniu workflow (P1) i ponownie sprawdzamy w dniu serii pomiarowej.

## 1. Skanery i narzędzia bezpieczeństwa

| Narzędzie | Klasa | Rola (propozycja) | Wersja najnowsza | Data wydania | Licencja | Dokumentacja | Wydanie |
|---|---|---|---|---|---|---|---|
| Semgrep (CE) | SAST | Kod Pythona (GT-01, GT-03–06, GT-12, GT-14), TEST-1 | v1.181.0 | 2026-10-14 | LGPL-2.1 (silnik; licencja reguł: TODO: zweryfikować) | https://docs.semgrep.dev/ | https://github.com/semgrep/semgrep/releases/tag/v1.181.0 |
| Bandit | SAST (Python) | Kod Pythona (GT-01–04), TEST-1 | 1.9.4 | 2026-02-25 | Apache-2.0 | https://bandit.readthedocs.io/en/latest/ | https://github.com/PyCQA/bandit/releases/tag/1.9.4 |
| pip-audit | SCA | Zależności Pythona (GT-07), TEST-2 | v2.10.1 | 2026-06-10 | Apache-2.0 | https://github.com/pypa/pip-audit | https://github.com/pypa/pip-audit/releases/tag/v2.10.1 |
| Gitleaks | Sekrety | Sekrety w kodzie i historii (GT-02), COMMIT-REQ-1, DEPLOY-REQ-1 | v8.30.1 | 2026-03-21 | MIT | https://github.com/gitleaks/gitleaks | https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1 |
| Checkov | IaC | Terraform i Dockerfile (GT-09, GT-10, GT-11), PRE-5* | 3.3.29 | 2026-10-13 | Apache-2.0 | https://www.checkov.io/ | https://github.com/bridgecrewio/checkov/releases/tag/3.3.29 |
| Trivy | SCA obrazu, IaC, sekrety | Zależności (GT-07), obraz (GT-08), Dockerfile i Terraform (GT-09–11), DEPLOY-REQ-4, DEPLOY-REQ-5 | v0.76.0 | 2026-10-14 | Apache-2.0 | https://trivy.dev/docs/latest/guide/ | https://github.com/aquasecurity/trivy/releases/tag/v0.76.0 |
| hadolint | Lint Dockerfile | Dockerfile (GT-09), PRE-5* | v2.15.1 | 2026-07-31 | GPL-3.0 | https://github.com/hadolint/hadolint | https://github.com/hadolint/hadolint/releases/tag/v2.15.1 |
| Syft | SBOM | SBOM obrazu, TEST-2, BASE-4* | v1.54.1 | 2026-10-06 | Apache-2.0 | https://github.com/anchore/syft | https://github.com/anchore/syft/releases/tag/v1.54.1 |
| Cosign | Podpisy | Podpis obrazu (alternatywa albo uzupełnienie atestacji GitHuba), ATT-1* | v3.1.3 | 2026-08-06 | Apache-2.0 | https://docs.sigstore.dev/cosign/ | https://github.com/sigstore/cosign/releases/tag/v3.1.3 |
| OWASP ZAP | DAST | Baseline na kontenerze w runnerze (GT-01, GT-05, GT-12–14), TEST-1, audyt po wdrożeniu | v2.17.0 | 2025-12-15 | Apache-2.0 | https://www.zaproxy.org/docs/docker/baseline-scan/ | https://github.com/zaproxy/zaproxy/releases/tag/v2.17.0 |
| actionlint | Lint workflow | Workflow GitHub Actions (GT-17), PRE-5*, DEPLOY-REQ-5 | v1.7.12 | 2026-03-30 | MIT | https://github.com/rhysd/actionlint | https://github.com/rhysd/actionlint/releases/tag/v1.7.12 |
| zizmor | Audyt bezpieczeństwa workflow | Workflow (GT-15, GT-16, GT-17), PRE-5*, DEPLOY-REQ-5 | v1.31.1 | 2026-10-15 | MIT | https://docs.zizmor.sh/ | https://github.com/zizmorcore/zizmor/releases/tag/v1.31.1 |

Wymagana wersja Pythona dla narzędzi instalowanych z PyPI (`requires_python`): Semgrep, Bandit i pip-audit `>=3.10`, Checkov `>=3.9`.

## 2. Akcje GitHub (kandydaci)

Akcje przypinamy do pełnego SHA commita (`AGENTS.md`, konwencja 5). Tabela podaje tag i SHA na 2026-10-18. Przed użyciem w workflow SHA trzeba sprawdzić ponownie, bo tag można przesunąć.

| Akcja | Tag | SHA commita | Data wydania | Do czego |
|---|---|---|---|---|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` | 2026-07-20 | pobranie kodu |
| `actions/setup-python` | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` | 2026-07-20 | Python dla testów i skanerów |
| `actions/upload-artifact` | v7.0.2 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | 2026-10-07 | raporty skanerów jako artefakty (dane eksperymentu) |
| `docker/setup-buildx-action` | v4.4.1 | `f87e5991a6d7451dcb8d9637bfbc97413f497069` | 2026-09-16 | builder obrazu |
| `docker/build-push-action` | v7.4.0 | `c3c9e263c25d99ce0380d002d59b67737d91b0dc` | 2026-09-15 | build i push obrazu |
| `docker/login-action` | v4.6.0 | `dbcb813823bdd20940b903addbd779551569679f` | 2026-07-29 | logowanie do rejestru |
| `aws-actions/configure-aws-credentials` | v6.3.0 | `e1253824e5c10ff9df46874f81ed3ec929e19cfd` | 2026-09-15 | OIDC do AWS, bez długoterminowych kluczy |
| `aws-actions/amazon-ecr-login` | v2.1.7 | `03f1aad4c6c7ffd436567f42f9384779290529bd` | 2026-08-19 | logowanie do ECR (jeśli rejestrem będzie ECR) |
| `github/codeql-action` (`upload-sarif`) | v4.39.0 | `6f2ac81f5cd81fe351a197ba0b00d91d03cd2aee` | TODO: zweryfikować | wyniki SARIF w zakładce Security |
| `actions/dependency-review-action` | v5.0.0 | `a1d282b36b6f3519aa1f3fc636f609c47dddb294` | 2026-05-08 | DEPLOY-REQ-2 |
| `actions/attest-build-provenance` | v4.2.2 | `4d101475d8b20a2381f78447822ac1eab6504dd8` | 2026-08-06 | provenance (SLSA, E02-05) |
| `actions/attest-sbom` | v4.1.0 | `c604332985a26aa8cf1bdc465b92731239ec6b9e` | 2026-03-18 | atestacja SBOM |
| `actions/attest` | v4.2.2 | `1e69f48acb82d1966a394da916b4c1698aa569d6` | 2026-08-04 | ogólna akcja atestacji (relacja do dwóch powyższych: TODO: zweryfikować w dokumentacji) |
| `anchore/sbom-action` | v0.24.3 | `66cbf4bc1f1c0d2edc94016e65bc221b6bb0ad6c` | 2026-10-02 | SBOM przez Syft |
| `aquasecurity/trivy-action` | v0.36.0 | `ed142fd0673e97e23eac54620cfb913e5ce36c25` | 2026-04-22 | skan Trivy |
| `aquasecurity/setup-trivy` | v0.3.1 | `81e514348e19b6112ce2a7e3ecbafe19c1e1f567` | 2026-06-03 | instalacja Trivy w przypiętej wersji |
| `zaproxy/action-baseline` | v0.15.0 | `de8ad967d3548d44ef623df22cf95c3b0baf8b25` | 2025-10-24 | ZAP baseline |
| `zaproxy/action-full-scan` | v0.13.0 | `3c58388149901b9a03b7718852c5ba889646c27c` | 2025-10-24 | ZAP z aktywnym skanowaniem (jeśli potrzebne) |
| `gitleaks/gitleaks-action` | v3.0.0 | `e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e` | 2026-05-30 | Gitleaks (warunki licencji akcji: TODO: zweryfikować) |
| `bridgecrewio/checkov-action` | v12.3134.0 | `6f26dc90000b74feb589a906cdfae540f5119895` | TODO: zweryfikować | Checkov |
| `hadolint/hadolint-action` | v3.5.0 | `06be81baf89a55ffd0e24b8f04a4185738dd3387` | 2026-08-24 | hadolint |
| `sigstore/cosign-installer` | v4.1.2 | `6f9f17788090df1f26f669e9d70d6ae9567deba6` | 2026-05-07 | instalacja Cosign |
| `pypa/gh-action-pip-audit` | v1.1.0 | `1220774d901786e6f652ae159f7b6bc8fea6d266` | 2024-08-08 | pip-audit |
| `zizmorcore/zizmor-action` | v0.7.1 | `85b2b9fb8e3325e7a23d7d0a9d7ba5ae0f999e3e` | 2026-10-15 | zizmor |
| `hashicorp/setup-terraform` | v4.0.1 | `dfe3c3f87815947d99a8997f908cb6525fc44e9e` | 2026-05-12 | Terraform w potoku |
| `step-security/harden-runner` | v2.22.1 | `ccd8616d44fd3846e67624a50d5aad6d37bf2d25` | 2026-10-08 | kontrola ruchu wychodzącego z runnera (PRE-1*, otwarte w `nist-800-204d.md`) |

Każde narzędzie można też uruchomić bez akcji zewnętrznej (instalacja z PyPI albo oficjalny obraz z digestem). To zmniejsza liczbę akcji firm trzecich w łańcuchu dostaw. Wybór między akcją a bezpośrednim uruchomieniem: TODO (E07).

## 3. Dokumentacja platform

| Dokument | Wydawca | Adres (sprawdzony 2026-10-18) | Do czego w pracy |
|---|---|---|---|
| Secure use reference (dawniej „Security hardening for GitHub Actions”) | GitHub | https://docs.github.com/en/actions/reference/security/secure-use | utwardzenie workflow, 4.3; GT-15–17 |
| OpenID Connect in Amazon Web Services | GitHub | https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws | OIDC z GitHub Actions do AWS (otwarte w `ksiazki.md`, uwaga 2) |
| Use artifact attestations | GitHub | https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations | provenance i atestacje, ATT-1*, SLSA |
| Dependency review | GitHub | https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-review | DEPLOY-REQ-2 |
| Create an OpenID Connect (OIDC) identity provider in IAM | AWS | https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html | strona AWS konfiguracji OIDC |
| Shared Responsibility Model | AWS | https://aws.amazon.com/compliance/shared-responsibility-model/ | 2.3, podział odpowiedzialności w chmurze |
| AWS CloudTrail User Guide | AWS | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html | rejestrowanie działań w koncie AWS, 4.2 |

Tytuły dokumentów GitHuba trzeba potwierdzić na stronach przed cytowaniem. Dokumenty, które zacytujemy w tekście pracy, dostaną notatki w rejestrze źródeł w vaulcie (`Zrodla/`) i klucze `[@KLUCZ]`.

## 4. Reguły dla pozycji katalogu

Sprawdzono 2026-10-18 w kodzie źródłowym reguł, a nie w opisach: dla każdej pozycji o niepewnej detekcji, czy oczekiwany detektor z `experiment/ground-truth.yaml` ma regułę i kiedy ta reguła się uruchamia. To analiza statyczna reguł. Zachowanie narzędzi trzeba jeszcze potwierdzić uruchomieniem w pilotażu (P5).

### 4.0 Wersje, na których sprawdzono reguły

| Źródło | Wersja (commit) |
|---|---|
| `gitleaks/gitleaks`, `config/gitleaks.toml` | v8.30.1 (`83d9cd68`) |
| `PyCQA/bandit`, `bandit/plugins/general_hardcoded_password.py` | 1.9.4 (`92ae8b82`) |
| `semgrep/semgrep-rules` | gałąź główna (`17e31e11`) |
| Zestawy rejestru Semgrep `p/python`, `p/default`, `p/security-audit`, `p/fastapi`, `p/jwt` | pobrane z `https://semgrep.dev/c/p/<zestaw>` 2026-10-18 (odpowiednio 151, 1073, 225, 1, 16 reguł) |
| `bridgecrewio/checkov`, `checkov/dockerfile/checks/` | 3.3.29 (`e40023ab`) |
| `aquasecurity/trivy-checks`, `checks/docker/root_user.rego` | gałąź główna (`80a59294`) |
| `hadolint/hadolint`, `src/Hadolint/Rule/DL3002.hs` | v2.15.1 (`2eece559`) |
| `zaproxy/zap-extensions`, dodatek `pscanrules` | gałąź główna (`15fc3d10`) |
| `zaproxy/zaproxy`, `docker/zap-baseline.py` | v2.17.0 (`8a1bff31`) |
| `encode/starlette`, `middleware/cors.py`, `middleware/errors.py` | 1.9.0, gałąź główna (`1840c9dd`) |

Reguły z gałęzi głównej mogą się różnić od tych, które pobierze potok. Trivy pobiera paczkę reguł (`trivy-checks`) w czasie działania, a obraz ZAP ma własne wersje dodatków. TODO: zweryfikować wersje reguł w obrazie i paczce przy P1.

### 4.1 Wyniki dla pozycji

**GT-02, zakodowany klucz JWT.**

- **Gitleaks `generic-api-key`.** Reguła łapie przypisanie, w którym nazwa zawiera m.in. `key`, `secret` albo `token`, a wartość ma 10–150 znaków `[\w.=-]` i entropię co najmniej 3,5. Wynik odrzucają *stopwords*, jeśli wystąpią w samej wartości. Na liście są m.in. `demo`, `example`, `fake`, `sample` i `testing`. Fikcyjna wartość w rodzaju `fake-jwt-key-…` nie zostanie więc zgłoszona.
- **Bandit B105 (`hardcoded_password_string`).** Nazwa zmiennej musi zawierać człon `password`, `pass`, `pwd`, `token` albo `secret` (lub `secrete`), oddzielony podkreślnikiem albo na całą nazwę, np. `JWT_SECRET` albo `SECRET_KEY`. `JWT_KEY` nie pasuje. Reguła obsługuje tylko zwykłe przypisanie (`ast.Assign`). Przypisanie z adnotacją typu (`jwt_secret: str = "…"`, typowe dla klas ustawień pydantic) nie jest sprawdzane: w Bandit 1.9.4 nie ma obsługi `ast.AnnAssign`.
- **Semgrep `python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret`** (w `p/python` i `p/default`, nie było w katalogu) ma wzorzec `jwt.encode($_, "...", ...)`, czyli literał w wywołaniu. Czy obejmie stałą zdefiniowaną w innym module: TODO: zweryfikować w pilotażu.
- **Wniosek:** wykrywalne, jeśli łatka ma postać `JWT_SECRET = "<losowa wartość bez słów ze stopwords>"` (zwykłe przypisanie). Pewność można podnieść ze średniej do wysokiej, gdy postać łatki zostanie tak ustalona.

**GT-06, log injection (CWE-117).**

- W `semgrep-rules` nie ma reguły dla Pythona z CWE-117. Jedyna reguła z tym CWE jest dla C#. W `p/python` i `p/default` z logowaniem w Pythonie wiążą się tylko `python-logger-credential-disclosure` (wyciek poświadczeń do logu) i `listen-eval`. Pozostałe reguły log injection w `p/default` dotyczą Javy.
- Bandit nie ma wtyczki dla log injection (z logowaniem wiąże się tylko B612, `logging.config.listen`).
- **Wniosek:** reguły z rejestru i Bandit nie wykryją GT-06.

**GT-09, kontener bez instrukcji USER.**

- **Checkov `CKV_DOCKER_3`** („Ensure that a user for the container has been created”) zgłasza błąd, gdy w Dockerfile nie ma żadnej instrukcji `USER`. **`CKV_DOCKER_8`** sprawdza tylko jawne `USER root`.
- **Trivy `DS-0002`** (alias `DS002`, ważność HIGH) zgłasza zarówno brak instrukcji `USER`, jak i ostatnie `USER root` albo `USER 0`.
- **hadolint `DL3002`** reaguje tylko na jawne `USER root`, `USER 0` albo `root:`/`0:` w danym etapie. Brak instrukcji `USER` tej reguły nie uruchamia.
- **Wniosek:** wykrywalne przez Checkov i Trivy. hadolint nie wykryje łatki w obecnej postaci (usunięcie `USER`). Uwaga: `CKV_DOCKER_3` sprawdza cały plik, więc w Dockerfile wieloetapowym `USER` w dowolnym etapie wystarczy, żeby kontrola przeszła (TODO: zweryfikować w pilotażu).

**GT-12, CORS z `*`.**

- **Semgrep `python.fastapi.security.wildcard-cors.wildcard-cors`** (w `p/python`, `p/default` i `p/fastapi`) to reguła typu *taint*: lista z `"*"` trafia do `allow_origins` w wywołaniu `$APP.add_middleware(CORSMiddleware, allow_origins=..., ...)`. Inna postać, np. `FastAPI(middleware=[Middleware(CORSMiddleware, ...)])`, nie pasuje do wzorca.
- **ZAP `10098` (Cross-Domain Misconfiguration, pasywna)** zgłasza odpowiedź z `Access-Control-Allow-Origin: *`. Starlette dodaje nagłówki CORS **tylko wtedy, gdy żądanie ma nagłówek `Origin`**. Przy `allow_credentials=True` odsyła konkretne źródło zamiast `*`, więc reguła 10098 się nie uruchomi. Pająk ZAP zwykle nie wysyła nagłówka `Origin` (TODO: zweryfikować w pilotażu).
- **Wniosek:** wykrywalne na etapie PR przez Semgrep, jeśli łatka używa `app.add_middleware(CORSMiddleware, allow_origins=["*"])`. ZAP baseline prawdopodobnie tego nie zobaczy bez dodania nagłówka `Origin` do żądań (np. regułą *replacer* w konfiguracji ZAP, TODO: zweryfikować).

**GT-13, brak ochrony przed osadzaniem w ramkach.**

- **ZAP `10020` (Anti-clickjacking Header, pasywna)** zgłasza odpowiedź bez `X-Frame-Options` i bez `frame-ancestors` w CSP. Przy domyślnym progu (MEDIUM) sprawdza tylko odpowiedzi **HTML**, z niepustą treścią, bez błędów i przekierowań. Dopiero przy progu LOW obejmuje inne odpowiedzi.
- Skrypt `zap-baseline.py` domyślnie przez 1 minutę przeszukuje aplikację tradycyjnym pająkiem, potem czeka na skan pasywny (`-m`, `-j` dla pająka AJAX, `-a` dla reguł alfa).
- **Wniosek:** wykrywalne, jeśli pająk dotrze do strony HTML, a middleware nagłówków w wersji czystej obejmuje tę stronę. Odpowiedzi JSON przy progu MEDIUM nie dają zgłoszenia. Strony HTML w aplikacji: TODO, zależy od E04 (szablony jinja2 z GT-07, `/docs` FastAPI).

**GT-14, tryb debug ujawniający stack trace.**

- **Semgrep:** w rejestrze nie ma reguły dla `FastAPI(debug=True)`. `python.flask.security.audit.debug-enabled` sprawdza tylko `$APP.run(..., debug=True)` w kodzie, który importuje `flask`.
- **ZAP `90022` (Application Error Disclosure, pasywna)** zgłasza **każdą** odpowiedź 500, a **`10023`** (Information Disclosure - Debug Error Messages) szuka w treści m.in. napisu `Internal Server Error`. W pliku wzorców `application_errors.xml` nie ma wzorców Pythona (`Traceback`). Starlette przy `debug=True` zwraca traceback jako HTML (gdy `Accept` zawiera `text/html`) albo tekst. Przy `debug=False` zwraca `Internal Server Error`.
- ZAP baseline nie wysyła ataków, więc błąd 500 pojawi się tylko wtedy, gdy pająk trafi na adres, który go wywołuje przy zwykłym żądaniu.
- **Wniosek:** reguły z rejestru Semgrep nie wykryją GT-14. ZAP baseline zgłosi błąd 500 niezależnie od trybu debug, więc samo zgłoszenie nie odróżnia GT-14 od zwykłego błędu serwera. Reguła trafienia musiałaby sprawdzać treść odpowiedzi (traceback).

### 4.2 Skutki dla katalogu i H1

| Pozycja | Detektor z katalogu | Wynik analizy reguł | Proponowana zmiana (do decyzji autora) |
|---|---|---|---|
| GT-02 | Gitleaks, Bandit | wykrywalne przy ustalonej postaci łatki | Zapisać postać łatki: zwykłe przypisanie `JWT_SECRET = "…"`, wartość bez słów ze *stopwords*. Dopisać Semgrep jako detektor przy literale w `jwt.encode` |
| GT-06 | Semgrep | brak reguły w rejestrze | **Decyzja 2026-10-20:** reguła własna Semgrep (`regula_wlasna: true`) |
| GT-09 | Checkov, Trivy, hadolint | Checkov i Trivy tak, hadolint nie | Usunąć hadolint z detektorów albo zmienić łatkę na `USER root` |
| GT-12 | Semgrep, ZAP | Semgrep tak (przy `add_middleware`), ZAP raczej nie | Bez zmiany pewności; zapisać postać łatki; ZAP z nagłówkiem `Origin` opcjonalnie |
| GT-13 | ZAP | tak, jeśli są strony HTML | Zapisać w E04 wymóg strony HTML osiągalnej dla pająka |
| GT-14 | Semgrep, ZAP | brak reguły Semgrep; ZAP nie odróżnia debug od zwykłego 500 | **Decyzja 2026-10-20:** reguła własna Semgrep (`regula_wlasna: true`) |

**Ryzyko dla H1 (TN6).** Pułap 17/20 zakłada, że narzędzia wykryją wszystkie pozycje w zasięgu. Jeśli potok użyje tylko reguł z rejestru, GT-06 i GT-14 prawdopodobnie przejdą. Pułap spadnie wtedy do 15/20, poniżej progu 16/20, i H1 przegra z konstrukcji eksperymentu. Są dwie drogi wyjścia, każda z kosztem:

- **Reguły własne Semgrep** dla GT-06 i GT-14. Wzmacniają zagrożenie TW1 (podatności i reguły od tej samej osoby), bo reguła powstaje pod konkretną pozycję katalogu. Wymaga to opisu w 5.3 i najlepiej wyniku osobno z regułami własnymi i bez nich.
- **Przeniesienie GT-06 i GT-14 poza zasięg narzędzi** (`w_zasiegu_narzedzi: false`). Zmienia pułap i może wymagać zmiany progu H1 w metodyce przed eksperymentem, z wpisem w dzienniku.

**Decyzja autora (2026-10-20) dla GT-06 i GT-14: reguły własne Semgrep w repozytorium.**

- Reguły są pisane pod klasę CWE (GT-06: dane z żądania trafiające do loggera bez neutralizacji; GT-14: tryb debug w FastAPI i Starlette, w konstruktorze i jako atrybut), a nie pod postać łatki. Testujemy je także na kodzie spoza katalogu.
- Reguły powstają i są zamrażane razem z katalogiem v1, przed akceptacją promotora (E03-07).
- Blokują pull request tak samo jak reguły z rejestru, więc ich zgłoszenia wchodzą do H1 i do precyzji bramek (H2b, M6).
- H1 rozstrzyga wynik z regułami własnymi. Wynik bez nich podajemy opisowo (`docs/metodyka.md`, p. 4.3).
- W katalogu detektory oznaczono polem `regula_wlasna: true`.

Odrzucone: przeniesienie GT-06 i GT-14 poza zasięg narzędzi (pułap 15/20, poniżej progu); wynik bez reguł własnych jako rozstrzygający albo wymóg przejścia w obu wariantach (H1 przegrałaby z konstrukcji eksperymentu); obniżenie progu H1; reguły pod postać łatki (słaba obrona przed TW1); reguły tylko raportujące (nie podnoszą H1).

**CodeQL.** Ma zapytanie `py/log-injection` (CWE-117, `@precision medium`; `github/codeql`, `python/ql/src/Security/CWE-117/LogInjection.ql`, sprawdzone 2026-10-20). Dla trybu debug ma tylko `FlaskDebug.ql`. Czy `py/log-injection` jest w domyślnym zestawie zapytań code scanning: TODO: zweryfikować. Decyzja autora (2026-10-20): CodeQL nie wchodzi do wariantu B (bez kolejnego narzędzia SAST; możliwy dłuższy czas PR), ale jest uruchamiany jako dodatkowa seria porównawcza na pozycjach w kodzie aplikacji (`docs/metodyka.md`, p. 4.3). Uzasadnienie i rola reguł własnych we wzorcu potoku: tamże.

Decyzje dla GT-09 (hadolint) oraz postaci łatek GT-02 i GT-12 są otwarte.

### 4.3 Otwarte

- [ ] Format SBOM (SPDX albo CycloneDX), otwarte w `docs/notes/nist-800-204d.md`.
- [ ] Potwierdzenie wyników 4.1 uruchomieniem narzędzi na łatkach (pilotaż P5).

## 5. Uwagi

- **tfsec.** Repozytorium `aquasecurity/tfsec` nie jest zarchiwizowane, ale jego opis w API GitHuba brzmi „Tfsec is now part of Trivy” (stan 2026-10-18). Skan Terraform robimy więc Trivy albo Checkovem, a nie osobnym tfsec.
- **`github/codeql-action`.** Pole „latest release” wskazuje wydanie paczki CodeQL (`codeql-bundle-v2.27.2`), a nie wersję akcji. Wersję akcji wzięto z tagów (`v4.39.0`).
- **`bridgecrewio/checkov-action`.** Ostatnie wydanie na GitHubie to `v12.1347.0` z 2022-03-09, a tagi sięgają `v12.3134.0`. Tagi są nowsze niż wydania, więc wersję akcji wzięto z tagów. TODO: zweryfikować, czy lista tagów z API jest posortowana według daty.
- **`pypa/gh-action-pip-audit`.** Ostatnie wydanie jest z 2024-08-08. Akcja może instalować pip-audit w innej wersji niż najnowsza. TODO: zweryfikować w README akcji, jak wybiera wersję pip-audit.
- **Python narzędzi a Python aplikacji.** Semgrep, Bandit i pip-audit wymagają Pythona `>=3.10`. GT-08 zakłada aplikację na Pythonie 3.9 (`experiment/ground-truth.yaml`), więc narzędzia muszą działać w osobnym środowisku niż aplikacja. Sam pip-audit ocenia zależności z pliku wymagań, więc nie musi działać na Pythonie aplikacji (TODO: zweryfikować w dokumentacji pip-audit).

## 6. Odświeżenie danych

Polecenia z sekcji 0 można powtórzyć w dniu zamrożenia potoku. Różnice wobec tej tabeli zapisujemy w dzienniku badawczym.
