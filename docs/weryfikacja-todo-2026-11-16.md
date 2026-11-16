# Weryfikacja TODO z notatek, 2026-11-16

Wyniki researchu agentów (Claude Code, 5 subagentów) do miejsc oznaczonych `TODO: zweryfikować` w repozytorium i w vaulcie `Magisterka-Vault`. Wszystkie źródła sprawdzono 2026-11-16. Pewność: **P** potwierdzone, **Cz** częściowo, **N** nie ustalono. Przed cytowaniem w tekście pracy autor czyta źródło sam (zasady `Zrodla/_Rdzen.md`).

Plik jest materiałem roboczym. Rozstrzygnięte TODO trzeba jeszcze przenieść do ADR-ów i notatek (osobny krok).

## 1. GitHub

| Nr | Dotyczy | Ustalenie | Źródło | Pewność |
|---|---|---|---|---|
| G1 | ADR-0001, ADR-0004 | Standardowe runnery GitHub są bezpłatne w repozytoriach publicznych. Plan Free konta osobistego (repo prywatne) daje przydział kwotowy 12 USD/mies. zamiast minut; Linux 2-core x64 0,006 USD/min. | https://docs.github.com/en/billing/concepts/product-billing/github-actions | P |
| G2 | ADR-0004 | Code scanning i secret scanning są bezpłatne i domyślnie włączone w repo publicznych; w prywatnych code scanning wymaga GitHub Code Security. | https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security | P |
| G3 | ADR-0004 | „Avoid using the `pull_request_target` workflow trigger if it's not necessary”; nie wolno checkoutować niezaufanego kodu z forków w workflow z sekretami. | https://docs.github.com/en/actions/reference/security/secure-use | P |
| G4 | ADR-0019 | `schedule` działa domyślnie w UTC (można podać strefę IANA), może być opóźniony przy obciążeniu, a część jobów może zostać pominięta. | https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows | P |
| G5 | ADR-0027, ADR-0033 | Pakiet GHCR przy pierwszej publikacji jest domyślnie prywatny; powiązany z repo dziedziczy uprawnienia, „but not the visibility”. Upublicznienie jest nieodwracalne. Limitów anonimowych zapytań dokumentacja nie podaje. **Sprzeczność z testem z ADR-0033** (anonimowy odczyt działał od razu): sprawdzić ustawienie pakietu w interfejsie. | https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility | P (limity: N) |
| G6 | owasp-devsecops (CICD-SEC-10) | Logi i artefakty: domyślnie 90 dni; repo publiczne 1–90 dni, prywatne 1–400 dni. | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository | P |
| G7 | owasp-devsecops (CICD10.2) | Security log konta osobistego: ostatnie 90 dni; zdarzenia konta, repozytoriów właściciela, 2FA, kluczy, PAT, OAuth i inne. | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log | P |
| G8 | owasp-devsecops (GT-16) | Od 2025-08-15 polityka Actions ma „Require actions to be pinned to a full-length commit SHA” i blokowanie akcji (`!`), także na poziomie repozytorium; lista „Allow select actions”. Konta osobiste nie są wymienione wprost. | https://github.blog/changelog/2025-08-15-github-actions-policy-now-supports-blocking-and-sha-pinning-actions/ | Cz |
| G9 | owasp-devsecops | Na planie Free środowiska (environments) i required reviewers tylko dla repo publicznych; „prevent self-review” bez osobnych ograniczeń planu. | https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments | Cz |
| G10 | owasp-devsecops | Sekrety nie trafiają do workflow z forka (poza `GITHUB_TOKEN` tylko do odczytu); dla gałęzi tego samego repo dokumentacja nie ma osobnego zdania. | jw. (events-that-trigger-workflows) | Cz |
| G11 | slsa.md (SLSA-B5b/c) | `ubuntu-slim`: 1 CPU, kontener na współdzielonej VM. Pozostałe standardowe runnery publicznych repo to osobne VM (4 CPU, 16 GB). | https://docs.github.com/en/actions/reference/runners/github-hosted-runners | P |
| G12 | slsa.md (SLSA-B5d) | Cache Actions: odczyt z własnej gałęzi, bazowej i domyślnej; zapis do zakresu gałęzi domyślnej tylko ze zdarzeń zaufanych. BuildKit `type=gha` podlega tym samym ograniczeniom. | https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching ; https://docs.docker.com/build/cache/backends/gha/ | P |
| G13 | slsa.md (Source) | Nie znaleziono natywnego wydawania Source VSA ani poziomów SLSA Source w GitHubie. | https://docs.github.com/en/actions/concepts/security/artifact-attestations | N |
| G14 | nist-800-204d (COMMIT-REQ-2) | Push protection bezpłatne w repo publicznych; push rulesets (ścieżki, rozszerzenia, rozmiar) dotyczą repozytoriów prywatnych i wewnętrznych, więc nie repo publicznego. | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets | Cz |
| G15 | narzedzia.md (CodeQL) | `py/log-injection` nie jest w zestawie domyślnym, tylko w `security-extended`. | https://docs.github.com/en/code-security/code-scanning/managing-your-code-scanning-configuration/python-built-in-queries | P |
| G16 | nist-800-204d (ATT-3*), slsa.md | Atestacje w repo publicznym: Sigstore Public Good, publiczny niezmienny log przejrzystości. `push-to-registry`: mechanizm (OCI referrer czy tag) nieopisany. | https://docs.github.com/en/actions/concepts/security/artifact-attestations ; https://github.com/actions/attest | Cz |
| G17 | metodyka.md (TK4) | Schemat API joba nie opisuje znaczenia `created_at`; endpoint `/timing` „is in the process of closing down”. TK4 zostaje do sprawdzenia na przebiegach. | https://docs.github.com/en/rest/actions/workflow-jobs | Cz |
| G18 | narzedzia.md | `gh-action-pip-audit` nie ma inputu wersji; instaluje `pip-audit ~= 2.0, >= 2.5.6` (najnowsze 2.x w chwili uruchomienia). Ostatnie wydanie v1.1.0 z 2024-08-08. | https://github.com/pypa/gh-action-pip-audit | P |
| G19 | narzedzia.md | `checkov-action` v12.3134.0: 2026-10-13. `codeql-action` v4.39.0: 2026-10-15. | https://github.com/bridgecrewio/checkov-action/releases/tag/v12.3134.0 | P |
| G20 | narzedzia.md | `GITLEAKS_LICENSE` wymagana dla organizacji, nie dla kont osobistych. | https://github.com/gitleaks/gitleaks-action | P |

## 2. AWS

| Nr | Dotyczy | Ustalenie | Źródło | Pewność |
|---|---|---|---|---|
| A1 | ADR-0003 | Synergy Research, Q3 2026 (30.10.2026): Amazon 26%, Microsoft 19%, Google 16% rynku infrastruktury chmurowej. | https://www.srgresearch.com/articles/cloud-market-growth-rate-rises-again-in-q3-biggest-ever-sequential-increase | P |
| A2 | ADR-0003, ADR-0020 | Od 15.07.2025: 100 USD kredytu + do 100 USD za zadania; plan Free 6 mies. albo do wyczerpania kredytów. Regulamin: kredyty tylko dla jednego konta; FAQ wyklucza osoby z wcześniejszym kontem AWS. FAQ sprzeczne co do ważności kredytów (6 vs 12 mies.). Azure: 200 USD na 30 dni + 12 mies. usług. | https://aws.amazon.com/free/terms/ ; https://aws.amazon.com/free/faqs/ | P (sprzeczność FAQ) |
| A3 | ADR-0017, ADR-0024 | Lista usług planu Free (nowa rejestracja) obejmuje ECS, ECR, EC2, EBS, ELB, EventBridge, KMS; Fargate bez osobnej pozycji. App Runner zamknięty dla nowych klientów (data 30.04.2026 tylko w źródłach wtórnych), daty wycofania brak. | https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html ; https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html | Cz |
| A4 | ADR-0018 | AWS EMEA SARL nalicza VAT 23% dla Polski. | https://aws.amazon.com/tax-help/emea-vat-tables/ | P |
| A5 | ADR-0019, aws-konto.md | Budgets odświeża dane „up to three times a day”; budżety dzienne nie obsługują alertów prognozowanych (blog 2020, zmiany nie znaleziono); budżety bez akcji bezpłatne. | https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html ; https://aws.amazon.com/blogs/aws-cost-management/launch-daily-cost-and-usage-budgets | P |
| A6 | koszty.md | Tag alokacji kosztów: do 24 h na pojawienie się i do 24 h na aktywację; domyślnie nie wstecz; backfill do 12 mies. (od 03.2024). | https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/activating-tags.html | P |
| A7 | ADR-0034 | Scheduler ponawia tylko błędy „retryable”; błędy trwałe trafiają do DLQ bez ponowień. Listy błędów brak. Dokładność 60 s. | https://docs.aws.amazon.com/scheduler/latest/UserGuide/configuring-schedule-dlq.html | Cz |
| A8 | ADR-0006, app-spec GT-11 | S3 od 05.01.2023 szyfruje każdy nowy obiekt SSE-S3; „You can no longer disable encryption for new object uploads.” | https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html | P |
| A9 | koszty.md | EBS z kluczem `aws/ebs` wywołuje KMS (GenerateDataKeyWithoutPlaintext, CreateGrant, Decrypt); żądania do kluczy AWS managed są płatne powyżej darmowych 20 000/mies. | https://docs.aws.amazon.com/ebs/latest/userguide/how-ebs-encryption-works.html ; https://aws.amazon.com/kms/pricing/ | P |
| A10 | ADR-0024 | ALB eu-north-1: 0,02394 USD/h, 0,0076 USD za LCU-godzinę. | Price List API AWSELB eu-north-1 | P |
| A11 | ADR-0024, koszty.md | eu-north-1: t3.small 0,0216 USD/h, gp3 0,0836 USD/GB-mies., publiczny IPv4 0,005 USD/h. | Price List API; https://aws.amazon.com/vpc/pricing/ | P |
| A12 | ADR-0024 | Let's Encrypt wydaje certyfikaty dla adresów IP od 15.01.2026 (GA), ważne 160 h, profil „shortlived”. | https://letsencrypt.org/2026/01/15/6day-and-ip-general-availability/ | P |
| A13 | ADR-0028 | Właściciel AMI Canonical: 099720109477 (partycja domyślna). | https://ubuntu.com/aws/docs/aws-how-to/instances/find-ubuntu-images/ | P |
| A14 | ADR-0031 | `unattended-upgrades` jest „installed by default” i aktualizacje bezpieczeństwa są włączone po instalacji (dokumentacja Ubuntu Server; obrazy chmurowe nie wymienione osobno). | https://ubuntu.com/server/docs/how-to/software/automatic-updates/ | Cz |
| A15 | PROTOCOL.md, log 2026-10-13 | Polityka testów penetracyjnych AWS: EC2 na liście usług bez zgody; skanowanie aplikacji webowych dozwolone (bez DoS). Pasywny DAST nie wymaga zgłoszenia (wniosek). | https://aws.amazon.com/security/penetration-testing/ | P |
| A16 | ADR-0021 | Nowa rejestracja (od 16.09.2026, stopniowo): konto bez roota, właściciel przez AWS Builder ID; użytkownicy i role IAM „can only be used for programmatic access, not console access”. | https://docs.aws.amazon.com/accounts/latest/reference/sign-up-for-aws.html | P |
| A17 | ADR-0015 | Plany wsparcia nie zależą od regionu. AWS podaje kryteria wyboru regionu (compliance, latency, cost, usługi), nie poleca konkretnego regionu. | https://aws.amazon.com/blogs/architecture/what-to-consider-when-selecting-a-region-for-your-workloads | P |
| A18 | slsa.md (SLSA-P3) | ECR obsługuje OCI 1.1 i referrers (podpisy, SBOM, atestacje). | https://aws.amazon.com/about-aws/whats-new/2024/06/amazon-ecr-oci-image-distribution-version-1-1 | P |
| A19 | ADR-0032 | `GetRequestAuthorizationDetails` (preview) przyjmuje authorization ID z komunikatu odmowy, przechowuje szczegóły 24 h, więc dla odmowy z 2026-11-11 jest już za późno. Komunikat zwykle zawiera „explicit deny in a service control policy”. | https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied-authorization-id.html | P |
| A20 | koszty.md | Pochodzenia 2 żądań Secrets Manager nie ustalono; sprawdzić w CloudTrail (eventSource `secretsmanager.amazonaws.com`, pola userIdentity, userAgent). | https://docs.aws.amazon.com/secretsmanager/latest/userguide/monitoring-cloudtrail.html | N |

## 3. Narzędzia i licencje

| Nr | Dotyczy | Ustalenie | Źródło | Pewność |
|---|---|---|---|---|
| T1 | ADR-0014 | Semgrep od 1.179.0 parsuje `except A, B:` jako krotkę (wcześniej gubił drugi typ bez ostrzeżenia). Otwarty błąd #12079: częściowe parsowanie w pliku z `match`. Bandit używa `ast` interpretera, więc na 3.14 działa. | https://github.com/semgrep/semgrep/releases/tag/v1.179.0 ; https://github.com/semgrep/semgrep/issues/12079 | P |
| T2 | narzedzia.md | Semgrep Rules License v1.0 nie jest otwarta: użycie „for your own internal business purposes”, bez rozpowszechniania. Uruchamianie w CI wygląda na dozwolone, kopiowanie reguł do publicznego repo nie. | https://semgrep.dev/legal/rules-license | Cz |
| T3 | ADR-0025 | HashiCorp przeszedł na BSL 1.1 10.08.2023 (od 1.6.0); użycie wewnętrzne i niekomercyjne nie jest „competitive offering”; każde wydanie wraca na MPL 2.0 po 4 latach. | https://www.hashicorp.com/en/blog/hashicorp-adopts-business-source-license ; https://www.hashicorp.com/en/bsl | P |
| T4 | ADR-0007 | 3.14.0 wydano 2025-10-07, wsparcie bezpieczeństwa do ok. X 2030 (PEP 745 bez dokładnego dnia). 3.9 EOL 2025-10-31 (PEP 596). | https://peps.python.org/pep-0745/ | P |
| T5 | ADR-0012 | Trivy domyślnie nie zgłasza zależności deweloperskich z `uv.lock`; flaga `--include-dev-deps`. | https://trivy.dev/latest/docs/coverage/language/python/ | P |
| T6 | narzedzia.md | pip-audit wymaga Pythona ≥3.10 i rozstrzyga markery środowiskowe dla interpretera, na którym działa, więc audyt aplikacji 3.14 trzeba robić na 3.14. | https://github.com/pypa/pip-audit | P / Cz |
| T7 | incydenty.md | zizmor nie analizuje przechodnio akcji zewnętrznych („does not analyze other files referenced”). | https://docs.zizmor.sh/usage/ | P |
| T8 | E04-04 (GT-07) | jinja2 3.1.2 działa ze Starlette `Jinja2Templates`, ale `fastapi[standard]` wymaga `jinja2>=3.1.5`. | https://github.com/Kludex/starlette/blob/main/starlette/templating.py | P |
| T9 | ADR-0014 | Ankieta PSF/JetBrains nie pyta o lintery. Pobrania ruff z PyPI: ok. 408,5 mln/mies. (odczyt 2026-11-16). | https://pypistats.org/packages/ruff | Cz |
| T10 | ADR-0008, ADR-0014, ADR-0022 | Deklaracje producenta: ruff „10-100x faster” niż Flake8/Black; uv „10-100x faster than pip”. Pomiaru niezależnego brak. | https://github.com/astral-sh/ruff ; https://github.com/astral-sh/uv | P (deklaracje) |
| T11 | owasp-devsecops | Palo Alto Networks przejął Cider Security (zakończenie 20.12.2022). | https://www.paloaltonetworks.com/company/press/2022/palo-alto-networks-completes-acquisition-of-cider-security | P |
| T12 | ADR-0010 | Domyślny `PasswordHasher`: Argon2id, t=3, m=64 MiB, p=4. OWASP minimum: m=19 MiB, t=2, p=1. Domyślne przekraczają minimum. | https://argon2-cffi.readthedocs.io/en/stable/api.html ; https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html | P |
| T13 | metodyka.md (CodeQL) | Dla Pythona CodeQL nie buduje kodu (`build-mode none`); typowego czasu dokumentacja nie podaje. | https://docs.github.com/en/code-security/codeql-cli/getting-started-with-the-codeql-cli/preparing-your-code-for-codeql-analysis | P / N |
| T14 | narzedzia.md (ZAP 10098) | Pająk ZAP nie wysyła `Origin`. Nagłówek można dodać regułą Replacer przez `-z "-config replacer.full_list(0)..."`. | https://www.zaproxy.org/docs/desktop/addons/replacer/ | P |
| T15 | narzedzia.md | Trivy pobiera paczkę reguł z pływającego tagu głównej wersji; `--skip-check-update` wyłącza pobieranie (wtedy reguły wbudowane w binarkę). ZAP: `zap.sh -suppinfo` pokazuje wersje dodatków. | https://trivy.dev/latest/docs/references/configuration/cli/trivy_config/ | P |
| T16 | narzedzia.md (JWT) | Semgrep CE propaguje stałe tylko w obrębie pliku, więc sekret JWT z innego modułu nie zostanie wykryty. | https://docs.semgrep.dev/writing-rules/data-flow/constant-propagation | P |
| T17 | narzedzia.md, ADR-0022 | `CKV_DOCKER_3` przechodzi przy dowolnym `USER` w pliku. Trivy DS-0002 patrzy na ostatni `USER` w całym pliku, nie tylko w ostatnim etapie. | https://github.com/bridgecrewio/checkov/blob/main/checkov/dockerfile/checks/UserExists.py ; https://github.com/aquasecurity/trivy-checks/blob/main/checks/docker/root_user.rego | P |

## 4. Bibliografia

| Nr | Dotyczy | Ustalenie | Pewność |
|---|---|---|---|
| B1 | Landis1977 | pp. 159–174; skala kappa na **s. 165** (<0 Poor; 0–0,20 Slight; 0,21–0,40 Fair; 0,41–0,60 Moderate; 0,61–0,80 Substantial; 0,81–1 Almost Perfect); autorzy nazywają podziały „clearly arbitrary”. | P |
| B2 | Vargha2000 | J. Educ. Behav. Stat. 25(2), pp. 101–132, doi 10.3102/10769986025002101 (JSTOR: 10.2307/1165329). Progi 0,56/0,64/0,71 tylko ze źródeł wtórnych, strony nie ustalono (paywall). | P / N |
| B3 | Humble2010, metodyka H2a | Upper Saddle River, NJ: Addison-Wesley, 2010 (LoC; strona redakcyjna: © 2011, first printing VIII 2010). **Heurystyka jest na s. 120, rozdz. 5 „Anatomy of the Deployment Pipeline”**, nie w rozdz. 7: „The commit stage should ideally take less than five minutes to run, and certainly no more than ten minutes.” | P |
| B4 | Forsgren2018 | Portland, OR: IT Revolution, 2018, ISBN 978-1942788331. | P |
| B5 | Hollander2013 | Hoboken, NJ: Wiley; LoC [2013], katalogi c2014. Przedział mediany z testu znaku: **3.6, s. 80–83**; HL dla sumy rang: **4.2, s. 136**; przedział przesunięcia (Moses): **4.3, s. 142–144**. | P (rok: Cz) |
| B6 | Wohlin2024 | 2nd ed., Springer 2024, doi 10.1007/978-3-662-69306-3; zagrożenia trafności w **rozdz. 9 „Planning”, s. 115–145**. | P |
| B7 | Johnson2013 | ICSE 2013, San Francisco, May 2013, pp. 672–681, doi 10.1109/ICSE.2013.6606613. | P |
| B8 | Arcuri2014 | STVR 24(3), pp. 219–250, May 2014, doi 10.1002/stvr.1486. | P |
| B9 | Abiona2024, Gupta2022 | Oba czasopisma poza wykazem MNiSW 2024. Wydawca IJCTT (Seventh Sense) na liście Bealla. Scopus: nie sprawdzono bezpośrednio. | P / N |
| B10 | Janczewski2025 | ZN WSB Poznań t. 108 nr 1, s. 77–90, doi 10.58683/dnswsb.2064; recenzja podwójnie ślepa; 20 pkt MNiSW (ekonomia i finanse); metoda: przegląd + ankieta ekspertów bez podanej liczby respondentów. | P |
| B11 | Cheenepalli (MŚP) | Zalecenie KE 2003/361/WE, Dz.U. L 124 z 20.05.2003, s. 36: < 250 pracowników, obrót ≤ 50 mln EUR lub bilans ≤ 43 mln EUR. | P |
| B12 | Rajapakse2022, Cheenepalli2025, Alghawli2024 | IST 141, art. 106700, doi 10.1016/j.infsof.2021.106700; ISDFS 2025 pp. 1–6, doi 10.1109/ISDFS65363.2025.11011960; AEJ 107 pp. 136–149, doi 10.1016/j.aej.2024.07.036. | P |
| B13 | Biswas2025 | ICRITO 2025, pp. 1–4, doi 10.1109/ICRITO66076.2025.11241906; brak wersji otwartej; abstrakt nie wspomina ewaluacji. | P / N |
| B14 | Rangnau2020 | EDOC 2020, pp. 145–154, doi 10.1109/EDOC49727.2020.00026; otwarta kopia w repozytorium RUG; narzędzia: ZAP, JMeter, SeleniumBase; wartości narzutu nie ustalono. | P / N |
| B15 | weryfikacja-zrodel | Learning Git: O'Reilly 2023 (V 2023), ISBN 978-1-098-13391-7. Ansible: Up and Running 3rd ed.: druk ISBN 978-1-098-10915-8. | P / Cz |
| B16 | Incydent-SolarWinds | Raport FireEye z 13.12.2020 na Google Cloud Blog: https://cloud.google.com/blog/topics/threat-intelligence/evasive-attacker-leverages-solarwinds-supply-chain-compromises-with-sunburst-backdoor | P |
| B17 | Incydent-xz-utils | Pierwsza łata Jia Tana 29.10.2021, pierwszy commit 07.02.2022 (R. Cox, https://research.swtch.com/xz-timeline). | P |

## 5. Standardy

| Nr | Dotyczy | Ustalenie | Pewność |
|---|---|---|---|
| N1 | nist-800-204d, nist-ssdf | Tabela 2 SP 800-204D przypisuje DEPLOY-REQ-5 tylko do **PO.1** (wiersz s. 26–27, sekcje 5.1.1 i 5.2). | P |
| N2 | ADR-0016, ADR-0029, ADR-0032, AGENTS.md zasada 5 | Brak osobnego REQ o sekretach potoku; najbliżej: COMMIT-REQ-1 (s. 20), DEPLOY-REQ-1 (s. 20), PULL-PUSH-REQ-3 (s. 18), sek. 5.3 pkt 4 (s. 22). Fraza „least privilege” nie pada (najbliżej sek. 5, s. 15: „granular authorizations”). **PULL-PUSH-REQ-2 nie dotyczy przypinania**, dokument nie wymaga wprost przypinania do SHA. | P |
| N3 | metodyka M2 | Kontrole na etapach potoku: sek. 4 (s. 13), 4.2 (s. 14), PULL-PUSH-REQ-1 (s. 18), DEPLOY-REQ-2 (s. 20), DEPLOY-REQ-5 (s. 21), DEPLOY-REQ-4 (s. 21). | P |
| N4 | nist-ssdf | SSDF 1.2 (SP 800-218r1) nadal Initial Public Draft z 17.12.2025; nowe praktyki PO.6 i PW.10. | P |
| N5 | OWASP-Top10-2025 | Oficjalnej daty brak; RC 06.11.2025, oznaczenie RC usunięte 24.12.2025. Z ankiety: A03 (Supply Chain) i A09 (Logging and Alerting). | P / Cz |
| N6 | owasp-asvs-samm | owaspsamm.org/model pokazuje v2.0; v2.2.0 wydano 06.07.2026. | P |
| N7 | owasp-asvs-samm | CWE-16: PROHIBITED; CWE-284 i CWE-668: DISCOURAGED; CWE-918 i CWE-1188: ALLOWED. MITRE nie wskazuje CWE dla IMDSv1 ani SG 0.0.0.0/0 (najbliżej CWE-918 i, przez analogię, CWE-1327). | P / N |
| N8 | slsa.md | SLSA nie zajęła oficjalnego stanowiska co do L3 przy reusable workflow producenta w tym samym repo; wypowiedzi maintainerów w issues #986, #1063; GitHub Docs: atestacje = L2, reusable workflow → L3. | N / P |
| N9 | SLSA-1.2 | Projekt nie podaje formy cytowania; stopka: © The Linux Foundation; README: „SLSA is an OpenSSF project”. | P |
| N10 | owasp-devsecops | Top 10 CI/CD: 2022, autorzy D. Krivelevich i O. Gil. DevSecOps Guideline nie przypisuje przypinania wprost; pośrednio CICD-SEC-8. | Cz |
| N11 | nist-ssdf | EO 14028 sek. 4(e): 10 punktów (bezpieczne środowiska buildu, skanowanie, SBOM, pochodzenie, atestacja zgodności i in.). | P |
| N12 | Incydent-Trivy | Źródła wtórne potwierdzone: Microsoft (24.03.2026), Wiz (20.03 i 24.03.2026), Aqua; LiteLLM 1.82.7 i 1.82.8 usunięte z PyPI. Źródła różnią się liczbą tagów (75/76 albo 76/77) i godzinami. | P |

## Rozbieżności do poprawienia

1. **AGENTS.md, zasada 5, i ADR-y 0016, 0029, 0032** przypisują przypinanie i ochronę poświadczeń rekomendacjom SP 800-204D, które tego nie mówią wprost (N2). Bezpośrednim źródłem przypinania jest OWASP (N10) i incydent Trivy (N12).
2. **metodyka.md, H2a i TK5**: heurystyka 10 minut to Humble2010 s. 120, rozdz. 5 (B3), nie rozdz. 7.
3. **ADR-0033 a GHCR**: dokumentacja mówi, że pakiet jest domyślnie prywatny (G5), a test pokazał anonimowy odczyt. Sprawdzić ustawienia pakietu.
4. **ADR-0032**: dekodowanie odmowy SCP przez `GetRequestAuthorizationDetails` jest już niemożliwe (24 h, A19). TODO zamknąć jako „niewykonalne”.
5. **Abiona2024, Gupta2022**: poza wykazem MNiSW, wydawca IJCTT na liście Bealla (B9).
6. **GT-07 (jinja2 3.1.2)**: konflikt z `fastapi[standard]` (T8).

## Decyzje autora z 2026-11-16

Odpowiedzi autora na pytania zadane po przeglądzie TODO. Przy każdej decyzji podano opcję wybraną przez autora; opcje rekomendowane zaproponował agent.

### Uczelnia i formalności
- **Draft badań (2027-01-10):** metodyka, katalog GT, hipotezy oraz wykresy i tabele z serii próbnej/pilotażu jako wyniki wstępne.
- **Styl cytowania:** zostaje IEEE.
- **Deklaracja AI:** oświadczenie według wzoru uczelni oraz akapit w rozdziale metodycznym (narzędzia, zakres, weryfikacja; dziennik w repozytorium jako dowód).
- **Licencja repozytorium:** MIT dla kodu, CC BY 4.0 dla dokumentacji i danych eksperymentu.

### Eksperyment i potok B
- **Bramka Trivy:** `--ignore-unfixed`; w `experiment/PROTOCOL.md` zapis daty bazy podatności przy każdej próbie (zamyka TODO w ADR-0007 i ADR-0022).
- **Wyjątki od bramek:** w pomiarze brak wyjątków (poza `--ignore-unfixed`); mechanizm wyjątków opisany w 5.3 (wątek Biswas2025, SAMM Secure Build).
- **Uruchamianie skanerów:** bezpośrednio (CLI z przypiętą wersją albo oficjalny obraz po digeście), nie przez akcje firm trzecich (zamyka TODO w `docs/narzedzia.md`).
- **Spójność `requirements.txt` z `uv.lock`:** krok wspólny wariantów A i B (zamyka TODO w ADR-0035).
- **Reguły Trivy:** `--skip-check-update`, czyli reguły wbudowane w przypiętą binarkę; wersję zapisujemy w danych próby.
- **GT-07:** `fastapi` bez extras `standard` i `jinja2==3.1.2`; sprawdzić w E04-04, czy wersja czysta używa extras.
- **ZAP:** reguła Replacer dodająca nagłówek `Origin` w konfiguracji ZAP, ta sama w obu wersjach aplikacji.
- **Analiza wyników:** Python + pandas + scipy, wersje przypięte w `experiment/`.

### Infrastruktura AWS
- **GT-11:** niezaszyfrowany wolumen EBS (katalog v1 dopuszcza EBS; S3 nie da się odszyfrować, A8).
- **Ryzyko szczątkowe polityki `terraform`:** opis w 5.3 jako ograniczenie, bez granicy uprawnień.
- **Użytkownik bazy:** rozdzielić role: migracje z DDL, aplikacja bez DDL (lokalnie i w AWS).
- **GHCR:** autor sprawdza ustawienia widoczności pakietu w interfejsie GitHub; agent dopisuje wynik i rozbieżność z dokumentacją do ADR-0033.
- **Środowisko wdrożenia:** jedno środowisko, serie A i B kolejno (zamyka TODO w `experiment/PROTOCOL.md`).
- **CWE dla IMDSv1:** CWE-1188.
- **CWE dla SG 0.0.0.0/0:** CWE-284 z adnotacją, że MITRE odradza mapowanie na Pillar, a lepszego Base dla reguły zapory nie ma.
- **ADR-0015:** zamknąć TODO adnotacją (AWS podaje kryteria, nie poleca regionu; A17).

### Źródła
- **Dokumentacja techniczna spoza `Zrodla/`:** notatka w rejestrze tylko dla źródeł cytowanych w tekście pracy; w ADR-ach URL z datą dostępu. Regułę dopisać do `docs/adr/README.md`, a TODO „czy rejestrować” usunąć.
- **Abiona2024, Gupta2022:** usunąć z tekstu, w vaulcie oznaczyć „nie cytować” z powodem (B9).
- **Preprinty (Rajapakse, Cheenepalli, Alghawli):** opis i strony z wersji wydawcy, sprawdzone w PDF wydawcy przed cytowaniem stron.
- **Pełne teksty:** Rangnau2020 z repozytorium RUG; Biswas2025 przez bibliotekę.
- **NIST SP 800-204D a przypinanie i poświadczenia:** głównym źródłem przypinania jest OWASP (DevSecOps Guideline, Top 10 CI/CD, CICD-SEC-8) z incydentem Trivy; NIST jako tło (sek. 3.2.1, s. 12; PULL-PUSH-REQ-3, s. 18; sek. 5.3 pkt 4, s. 22; sek. 5, s. 15). Poprawić AGENTS.md (zasada 5) i ADR-0016, 0029, 0032.
- **Humble2010:** rok 2010, s. 120, rozdz. 5; poprawić metodykę (H2a, TK5) i notatkę źródła.
- **SLSA:** autor korporacyjny OpenSSF.
- **OWASP Top 10:2025:** rok 2025 z datą dostępu; w notatce źródła usunięcie RC 24.12.2025 jako uzasadnienie.

### Fakty i działania autora
- **Czas pracy w dzienniku:** agent odtwarza przedziały z timestampów commitów i sesji, oznacza je jako „odtworzone, przybliżone”, a autor poprawia. Od teraz czas mierzony na bieżąco; ograniczenie w 5.3.
- **Powód losowych sekretów w CI (ADR-0023):** według autora: nic stałego do wycieku (brak długożyjących sekretów do ochrony i rotacji).
- **Zrobione przez autora:** lektura NIST SP 800-204D rozdz. 4–6 i dodatku A oraz lektura opracowania SLSA (`docs/notes/slsa-pytania.md`).
- **Niezrobione:** zapis `AccountMFAEnabled = 1`, aktywacja tagu `Project` w Cost allocation tags.
- **Hook pre-commit (E07-01):** tylko Gitleaks na zmianach w stagingu.

## Przeniesienie do dokumentów (2026-11-16)

Ustalenia i decyzje przeniesiono do: ADR-0001–0035 (bez zmiany decyzji, zob. nowe zasady 8 i 9 w `docs/adr/README.md`), `AGENTS.md` (zasada 5), `README.md`, `LICENSE`, `LICENSE-docs.md`, `docs/metodyka.md`, `experiment/PROTOCOL.md` (P2, ustawienia skanerów), `experiment/ground-truth.yaml` (GT-07, GT-11), `docs/app-spec.md`, `docs/narzedzia.md`, `docs/koszty.md`, `docs/aws-konto.md`, `docs/literature-matrix.md`, `docs/weryfikacja-zrodel.md`, notatek w `docs/notes/`, `semgrep-rules/README.md` oraz vaulta (`Zrodla/`, `docs/wymogi.md`, `CLAUDE.md`).

Poprawka względem pytań: ADR-0007 pytał, czy `PROTOCOL.md` wymaga zapisu daty bazy podatności. Protokół już to wymagał (P2, p. 2.3 pkt 4, p. 3.1).

**Nie przeniesiono (celowo):**
- notatek zadań w vaulcie (`Zadania/`): to zapis historyczny zamkniętych zadań, rozstrzygnięcia są w dokumentach repozytorium;
- TODO, które wymagają pomiaru albo pracy w kolejnych zadaniach (E04-04, E07, E09, pilotaż), odczytu kosztów za listopad, lektury przez autora albo działania autora (MFA, tag kosztów, widoczność GHCR, Biswas2025);
- czasów pracy w dzienniku: odtworzenie z commitów to osobny krok.
