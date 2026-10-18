# Mapa książek na podrozdziały pracy

- **Źródła:** posiadane książki z rejestru (`Zrodla/` w vaulcie): rdzeń [@Suehring2024], [@Laster2023], [@Brikman2022]; zastępca [@Hoffman2024]; pomocnicze [@Lubanovic2023], [@Meijer2022], [@Gift2019], [@Skoulikari2023].
- **Zadanie:** E02-09 (tablica zadań). Mapa wskazuje, który rozdział której książki czytać przy pisaniu danego podrozdziału. Pełna lektura rozdziałów odbywa się dopiero przy pisaniu (`Zrodla/_Rdzen.md`, kolejność lektur, p. 6).
- **Zakres:** mapa, nie lektura. Pole `zweryfikowane` w rejestrze zostaje `nie`, dopóki autor nie przeczyta danego rozdziału.
- **Konspekt pracy:** według szkieletu `thesis/praca-magisterska-szkielet.docx` w vaulcie (stan z 2026-10-18).
- **Skąd tekst:** spisy treści i strony redakcyjne z egzemplarzy PDF autora (wydania O'Reilly, pobrane 2026-10-18). Pliki leżą w vaulcie w `Zrodla/pdf/<KLUCZ>-<tytuł>.pdf`, poza repozytorium ze względu na prawa autorskie. Agent (Claude Code) wyciągnął spisy treści narzędziem `pdftotext`. Tematy przekrojowe (np. OIDC, tfsec/Checkov, przypinanie akcji) zlokalizował wyszukiwaniem w pełnym tekście, nie z pamięci.
- **Numeracja stron:** numery wydrukowane w książce. **W przeglądarce PDF dodaj przesunięcie** z tabeli w sekcji 0.
- **Stan:** przypisania rozdziałów do podrozdziałów pracy zaproponował agent na podstawie spisów treści. Autor je zaakceptował 2026-10-18.

## Jak czytać ten plik

1. Sekcja 0 zawiera wydania i przesunięcia stron PDF.
2. Sekcja 1 to widok od strony pracy: podrozdział → książki i rozdziały.
3. Sekcja 2 to widok od strony książek: rozdział książki → strony → podrozdział pracy (kryterium ukończenia E02-09).
4. Sekcja 3 wymienia książki, których świadomie nie mapujemy.
5. Sekcja 4 zbiera ustalenia i otwarte kwestie do decyzji autora.

**Priorytet** w tabelach sekcji 2:
- **A:** przeczytać przed pisaniem podrozdziału,
- **B:** przejrzeć albo przeczytać wskazane strony,
- **C:** tylko warsztat albo odwołanie, raczej bez cytowania,
- **—:** poza zakresem.

---

## 0. Wydania i przesunięcia stron

Dane ze stron redakcyjnych egzemplarzy (2026-10-18).

| Klucz | Wydanie (strona redakcyjna) | ISBN | Strona książki → strona PDF |
|---|---|---|---|
| [@Suehring2024] | First Edition, maj 2024 (First Release 2024-05-15) | 978-1-098-14486-9 | +14 |
| [@Laster2023] | First Edition, sierpień 2023 (First Release 2023-08-16) | 978-1-098-13107-4 | +22 |
| [@Brikman2022] | Third Edition, wrzesień 2022 (First Release 2022-09-19); opisuje Terraform do wersji 1.2 | 978-1-098-11674-3 | +26 |
| [@Hoffman2024] | Second Edition, styczeń 2024 (First Release 2024-01-17) | 978-1-098-14393-0 | +36 |
| [@Lubanovic2023] | First Edition, listopad 2023 (First Release 2023-11-06); copyright 2024 | 978-1-098-13550-8 | +18 |
| [@Meijer2022] | Third Edition, lipiec 2022 (First Release 2022-07-12) | 978-1-098-10915-8 | +22 |
| [@Gift2019] | First Edition, grudzień 2019 (First Release 2019-12-11); copyright 2020 | 978-1-492-05769-7 | +22 |
| [@Skoulikari2023] | First Edition, maj 2023 (First Release 2023-05-16) | 978-1-098-13391-7 | +22 |

Przykład: s. 204 u Brikmana to strona 230 w przeglądarce PDF.

## 1. Podrozdział pracy → książki

| Podrozdział pracy | Książki i rozdziały (priorytet A/B) |
|---|---|
| 1.1. Uzasadnienie i motywacja | Suehring rozdz. 1 (s. 8–10: bezpieczeństwo „na końcu”); Hoffman rozdz. 1 (tło historyczne, C) |
| 2.1. Ewolucja od DevOps do DevSecOps | **Suehring rozdz. 1, 8**, rozdz. 2 (s. 31–33, triada CIA), rozdz. 3; Brikman rozdz. 1 (s. 1–3, czym jest DevOps), rozdz. 10 |
| 2.2. Architektura i zagrożenia w potokach CI/CD | **Laster rozdz. 2, 9**, rozdz. 3, 5; Brikman rozdz. 6; Hoffman rozdz. 6, 24; Suehring rozdz. 6 |
| 2.3. DevSecOps w środowiskach chmurowych | słabe pokrycie: Brikman rozdz. 1 (IaC); Gift rozdz. 9 (modele usług chmurowych). Oparcie raczej w artykułach i dokumentacji AWS (sekcja 4, p. 3) |
| 2.4. Przegląd narzędzi DevSecOps | **Suehring rozdz. 3, 5**, rozdz. 6; **Brikman rozdz. 9** (s. 364–370); **Hoffman rozdz. 20, 26**; Laster rozdz. 9 (s. 201–205) |
| 2.5. Krytyczna analiza literatury | — (prace naukowe, `docs/literature-matrix.md`) |
| 3.1–3.5. Standardy i wytyczne | — (dokumenty źródłowe). Pomocniczo: Suehring rozdz. 5 (SBOM, s. 97–101), Laster rozdz. 9 (s. 199–201, zależności od akcji) |
| 4.1. Aplikacja badawcza | **Lubanovic rozdz. 11**, rozdz. 3, 5, 7, 8–10; **Hoffman rozdz. 10–18** i 28–36 (dobór i opis podatności) |
| 4.2. Architektura Docker i AWS | **Brikman rozdz. 1, 3, 6**, rozdz. 4, 8; Suehring rozdz. 5 (Docker, s. 101–112); Lubanovic rozdz. 13; Gift rozdz. 9, 11; Meijer (jeśli Ansible zostaje w zakresie) |
| 4.3. Projekt potoku CI/CD | **Laster rozdz. 2, 6, 9**, rozdz. 1, 3, 5, 12; **Brikman rozdz. 6** (s. 204–206, GitHub Actions + OIDC), **rozdz. 10**; **Skoulikari rozdz. 12**; Suehring rozdz. 4 |
| 4.4. Integracja testów bezpieczeństwa | **Suehring rozdz. 3** (s. 59–74: analiza statyczna, OWASP ZAP); **Brikman rozdz. 9** (s. 364–370); **Hoffman rozdz. 26, 27**; Laster rozdz. 9 (s. 201–205); Lubanovic rozdz. 12 |
| 4.5. Logowanie, audyt i artefakty | Laster rozdz. 7 (artefakty), 10 (logi, podsumowania jobów); Suehring rozdz. 5 (SBOM), 6 (monitoring) |
| 5.1. Metryki oceny | **Hoffman rozdz. 27** (CVSS, progi istotności). Metryki DORA i skuteczności skanerów w innych źródłach (E02-11, E02-13) |
| 5.3. Dyskusja i ograniczenia | Suehring rozdz. 8; Brikman rozdz. 9 (s. 364–370: mocne i słabe strony analizy statycznej) |
| 6.2. Rekomendacje praktyczne | Suehring rozdz. 8; Brikman rozdz. 8 (checklista produkcyjna) |
| Załącznik B. Katalog podatności | **Hoffman rozdz. 10–18** (atak) i **28–36** (obrona); Lubanovic rozdz. 11 |
| `experiment/` (skrypty metryk) | Gift rozdz. 2, 8 (warsztat) |

## 2. Książka → rozdział → podrozdział pracy

Rozdziały bez związku z pracą pomijamy albo oznaczamy „—”.

### 2.1. Suehring, *Learning DevSecOps* (2024): rdzeń

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 1. The Need for DevSecOps | 1–15 | 2.1, 1.1 | Od zwinnego wytwarzania do DevSecOps (s. 2–7). Bezpieczeństwo jako dodatek na końcu (s. 8). Kultura i procesy przed narzędziami (s. 9–10). DevSecOps jako proces i cykl DevSecOps SDLC (s. 11–15) | A |
| 2. Foundational Knowledge… (tylko „Data Security: CIA”) | 31–33 | 2.1 | Triada poufność–integralność–dostępność jako punkt wyjścia definicji | B |
| 3. Integrating Security | 41–75 | 2.1, 2.4, 4.3, 4.4 | Najmniejsze uprawnienia (s. 42–44, uprawnienia w potoku). Poufność danych (s. 44–50). Integralność i sumy kontrolne (s. 50–52). Identyfikowalność kodu i analiza statyczna (s. 59–61, SAST). OWASP ZAP, skan ręczny (s. 63–74, DAST) | A |
| 4. Managing Code and Testing | 77–94 | 4.3 | Git, Gitflow a trunk-based (s. 87–90, model gałęzi). Automatyzacja testów (s. 90–94) | B |
| 5. Moving Toward Deployment | 97–113 | 2.4, 3.5, 4.2, 4.5 | Konfiguracja jako kod i SBOM (s. 97–101). Docker: kontenery, obrazy, pozyskiwanie obrazów (s. 101–112). Wdrożenie blue-green (s. 112) | A |
| 6. Deploy, Operate, and Monitor | 115–134 | 2.2, 2.4, 4.5 | CI/CD (s. 115–116). Potok w Jenkinsie jako punkt odniesienia dla GitHub Actions (s. 117–131). Monitorowanie (s. 131–134) | B |
| 7. Plan and Expand | 137–154 | — | Kubernetes, Helm, mikroserwisy: poza zakresem pracy | — |
| 8. Beyond DevSecOps | 155–157 | 2.1, 5.3, 6.2 | Wzorce DevSecOps: shift left, zintegrowane i automatyczne bezpieczeństwo, wiele chmur | A |

### 2.2. Laster, *Learning GitHub Actions* (2023): rdzeń

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 1. The Basics | 3–14 | 4.3 | Czym jest GitHub Actions, model kosztów (s. 10–13), kiedy warto przejść na Actions | B |
| 2. How Does Actions Work? | 15–24 | 2.2, 4.3 | Wyzwalacze, kroki, runnery, joby, workflow: słownik do opisu architektury potoku | A |
| 3. What's in an action? | 25–36 | 2.2, 4.3 | Struktura akcji. Akcje publiczne i Marketplace (s. 32–36): zależność od kodu osób trzecich | B |
| 4. Working with Workflows | 37–65 | — | Warsztat: pierwszy workflow, rozszerzenie VS Code | C |
| 5. Runners | 67–87 | 2.2, 4.3 | Runnery GitHub-hosted i self-hosted. Ryzyka self-hosted (s. 74–75): uzasadnienie wyboru runnera | B |
| 6. Managing Your Workflow Environments | 91–115 | 4.3 | Sekrety i zmienne konfiguracyjne (s. 97–103). Uprawnienia workflow (s. 103–105). Środowiska wdrożeniowe z regułami ochrony (s. 105–115) | A |
| 7. Managing Data Within Workflows | 117–145 | 4.5 | Artefakty: wysyłanie i pobieranie (s. 122–127). Cache (s. 135–145) | B |
| 8. Managing Workflow Execution | 147–163 | 4.3 | Wyzwalacze i filtry, współbieżność, macierze | C |
| 9. Actions and Security | 167–220 | 2.2, 2.4, 4.3, 4.4 | **Najważniejszy rozdział.** Uprawnienia, CODEOWNERS, chronione gałęzie i tagi, rulesety (s. 168–181). Sekrety i tokeny (s. 181–191). Niezaufane dane wejściowe, wstrzykiwanie (s. 191–199). Zabezpieczanie zależności i wybór referencji akcji: gałąź, tag, SHA (s. 199–201). Skanowanie (s. 201–205). Bezpieczna obsługa PR, `pull_request_target` (s. 205–220) | A |
| 10. Monitoring, Logging, and Debugging | 223–256 | 4.5 | Historia uruchomień, logi debugowania, własne podsumowanie joba (s. 253–256): raportowanie wyników skanów | B |
| 11. Creating Custom actions | 259–291 | — | Własne akcje: poza zakresem | — |
| 12. Advanced Workflows | 293–315 | 4.3 | Reusable workflows (s. 300–307), required workflows (s. 308–315). Por. notatki SLSA (E02-05) | B |
| 13. Advanced Workflow Techniques | 317–335 | 4.3 | Kontenery jako środowisko joba i usługi (s. 330–335), np. skanery w obrazach | C |
| 14. Migrating to GitHub Actions | 337–373 | — | Migracja z innych systemów CI. Ewentualnie tło do porównania platform | — |

### 2.3. Brikman, *Terraform: Up and Running*, wyd. 3 (2022): rdzeń

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 1. Why Terraform | 1–36 | 2.1, 2.3, 4.2 | Czym jest DevOps (s. 1–3). IaC i jego rodzaje (s. 3–16). Korzyści IaC (s. 16–17). Infrastruktura zmienna i niezmienna (s. 21). Porównanie Terraform z innymi narzędziami IaC (s. 20–36): materiał do ADR | A |
| 2. Getting Started with Terraform | 39–80 | 4.2 | Konto AWS i pierwsze zasoby. Uwaga: książka zakłada klucze dostępu IAM (s. 40–43), a projekt używa OIDC | C |
| 3. How to Manage Terraform State | 81–113 | 4.2 | Zdalny stan we współdzielonym magazynie (s. 83–93). Izolacja stanu (s. 93–105) | A (s. 81–105) |
| 4. Reusable Infrastructure with Modules | 115–139 | 4.2 | Moduły. Wersjonowanie modułów (s. 133–139) a przypinanie wersji | B |
| 5. Tips and Tricks | 141–189 | — | Pętle, warunki, wdrożenie bez przestoju: warsztat | C |
| 6. Managing Secrets with Terraform | 191–219 | 2.2, 4.2, 4.3 | Podstawy i narzędzia zarządzania sekretami (s. 192–196). **GitHub Actions jako serwer CI z OIDC do AWS (s. 204–206).** Sekrety w plikach stanu i planu (s. 217–219) | A |
| 7. Working with Multiple Providers | 221–272 | 4.2 | Szybki kurs Dockera (s. 249–252) jako tło. EKS poza zakresem | C |
| 8. Production-Grade Terraform Code | 275–313 | 4.2, 6.2 | Lista kontrolna infrastruktury produkcyjnej (s. 279–280) | B |
| 9. How to Test Terraform Code | 315–372 | 2.4, 4.4, 5.3 | **Analiza statyczna IaC (s. 364–370):** porównanie `terraform validate`, tfsec, tflint, Terrascan (tab. 9-1) oraz Terratest, OPA, Sentinel, Checkov; mocne i słabe strony | A (s. 364–372) |
| 10. How to Use Terraform as a Team | 375–414 | 4.3, 2.1 | Workflow wdrażania kodu aplikacji (s. 382–390) i infrastruktury (s. 390–414): kontrola wersji, review, testy automatyczne, merge, wdrożenie | A |

### 2.4. Hoffman, *Web Application Security*, wyd. 2 (2024): pierwszy zastępca

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 1. The History of Software Security | 1–18 | 1.1 | Tło historyczne | C |
| 3. The Structure of a Modern Web Application | 27–56 | 4.1 | M.in. uwierzytelnianie i autoryzacja (s. 46–47) | C |
| 6. Identifying Third-Party Dependencies | 87–98 | 2.2 | Zależności jako powierzchnia ataku | B |
| 10. Cross-Site Scripting | 117–134 | Zał. B | Kandydat do katalogu podatności (E03-03) | A, jeśli klasa w katalogu |
| 11. Cross-Site Request Forgery | 135–146 | Zał. B | j.w. | A, jeśli w katalogu |
| 12. XML External Entity | 147–158 | Zał. B | j.w. | A, jeśli w katalogu |
| 13. Injection | 159–174 | Zał. B, 4.1 | SQL injection (s. 159), code injection (s. 163), command injection (s. 167) | A |
| 15. Attacking Data and Objects | 187–192 | Zał. B | Mass assignment, IDOR, deserializacja | A, jeśli w katalogu |
| 17. Exploiting Third-Party Dependencies | 205–216 | Zał. B, 2.2 | Podatne zależności: cel dla SCA | A |
| 18. Business Logic Vulnerabilities | 217–226 | 5.3 | Klasa, której skanery zwykle nie wykrywają: ograniczenia | B |
| 20. Securing Modern Web Applications | 231–236 | 2.4, 4.4 | Przegląd: code review, wykrywanie, analiza i zarządzanie podatnościami, testy regresji | A |
| 24. Threat Modeling Applications | 277–288 | 2.2 | Modelowanie zagrożeń | B |
| 25. Reviewing Code for Security | 289–298 | 2.4 | Ręczny przegląd kodu | C |
| 26. Vulnerability Discovery | 299–307 | 2.4, 4.4 | Automatyzacja bezpieczeństwa: analiza statyczna (s. 300), dynamiczna (s. 301), testy regresji podatności (s. 302) | A |
| 27. Vulnerability Management | 309–317 | 4.4, 5.1 | CVSS: ocena bazowa, czasowa, środowiskowa (s. 310–316): progi blokowania potoku | A |
| 28–36. Defending Against … | 319–382 | 4.1, Zał. B | Obrona przed XSS (s. 319), CSRF (s. 331), XXE (s. 339), injection (s. 343), dane i obiekty (s. 359), zależności (s. 371): opis poprawki w katalogu | B |

### 2.5. Lubanovic, *FastAPI* (2023): pomocnicza

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 1. The Modern Web | 3–14 | 4.1 | Tło | C |
| 3. FastAPI Tour | 27–48 | 4.1 | Charakterystyka frameworka | B |
| 5. Pydantic, Type Hints, and Models Tour | 61–76 | 4.1 | Walidacja danych wejściowych | B |
| 6. Dependencies | 77–82 | 4.1 | Wstrzykiwanie zależności (np. kontrola dostępu) | C |
| 7. Framework Comparisons | 83–92 | 4.1 | FastAPI wobec innych frameworków: materiał do ADR | B |
| 8–10. Web, Service, Data Layer | 93–142 | 4.1 | Warstwowa architektura aplikacji badawczej | B |
| 11. Authentication and Authorization | 143–164 | 4.1, Zał. B | Metody uwierzytelniania, OAuth2 (s. 150), OIDC (s. 159), autoryzacja (s. 160): miejsca na celowe podatności | A |
| 12. Testing | 165–184 | 4.3, 4.4 | Testy jednostkowe, integracyjne, pełne. Testy bezpieczeństwa (s. 182) | B |
| 13. Production | 185–194 | 4.2 | Wdrożenie, Docker (s. 187), usługi chmurowe (s. 188) | B |

### 2.6. Meijer, Hochstein, Moser, *Ansible: Up and Running*, wyd. 3 (2022): pomocnicza, warunkowo

Mapa obowiązuje tylko wtedy, gdy Ansible zostanie w zakresie (pierwszy kandydat do cięcia według harmonogramu).

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 1. Introduction | 1–14 | 4.2 | Jak działa Ansible, architektura bezagentowa, bezpieczeństwo (s. 11–13): materiał do ADR | B |
| 2–5, 7, 9. Instalacja, playbooki, inwentarz, zmienne, role | 15–176 | 4.2 | Warsztat | C |
| 13. Ansible and Containers | 243–258 | 4.2 | Budowa obrazu i wdrożenie kontenera Dockera z Ansible (s. 246–257) | B |
| 17. Cloud Infrastructure | 293–319 | 4.2 | EC2: poświadczenia (s. 298–300), security groups (s. 308–310), VPC (s. 316–319) | B |
| 21. Networking and Security (część „Security”) | 375–381 | 2.3 | Zgodność a bezpieczeństwo, zero trust | C |
| 22. CI/CD and Ansible | 383–398 | 4.3 | Ansible w systemie CI | B |
| 24. Best Practices | 419–424 | 4.2 | Dobre praktyki, w tym bezpieczeństwo (s. 422) | B |

### 2.7. Gift i in., *Python for DevOps* (2019): pomocnicza

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 2. Automating Files and the Filesystem | 35–56 | `experiment/` | Odczyt plików JSON i YAML (raporty skanerów) | C |
| 6. Continuous Integration and Continuous Deployment | 145–162 | — | Studia przypadków CI/CD (AWS CodePipeline, Google Cloud Build) | C |
| 7. Monitoring and Logging | 163–192 | 4.5 | Logowanie w Pythonie (s. 177–184) | C |
| 8. Pytest for DevOps | 193–217 | 4.3, `experiment/` | pytest, fixtures, testy infrastruktury (Testinfra) | B |
| 9. Cloud Computing | 219–246 | 2.3 | Modele usług chmurowych IaaS, PaaS, serverless, SaaS (s. 220–232) | B |
| 10. Infrastructure as Code | 247–273 | 4.2 | Terraform w AWS (s. 251–260): uzupełnienie Brikmana | C |
| 11. Container Technologies: Docker and Docker Compose | 275–298 | 4.2 | Obrazy, rejestr, Compose | B |

### 2.8. Skoulikari, *Learning Git* (2023): pomocnicza

| Rozdział książki | Strony | Podrozdział pracy | Do czego | Priorytet |
|---|---|---|---|---|
| 4. Branches | 43–62 | 4.3 | Gałęzie | C |
| 8. Cloning and Fetching (część „Git Collaboration and Branches”) | 125–132 | 4.3 | Współpraca na gałęziach | C |
| 12. Pull Requests (Merge Requests) | 231–258 | 4.3 | Po co PR (s. 235), sposoby scalania (s. 237), review i zatwierdzenie (s. 246–248): model pracy z PR i ochrona gałęzi | A |

## 3. Książki poza mapą

| Książka | Powód |
|---|---|
| [@Barrett2022], *Efficient Linux at the Command Line* | Pomoc warsztatowa, raczej nie do cytowania (rejestr, E02-01). Definicja E02-09 jej nie obejmuje. |
| [@Oswalt2023], *Network Programmability and Automation* | Poza zakresem pracy. Definicja E02-09 jej nie obejmuje. |
| *Docker: Up & Running*, wyd. 3 (O'Reilly) | Decyzja autora (2026-10-18): dodać do rejestru jako źródło pomocnicze do 4.2. Notatka w rejestrze i mapa powstaną po przekazaniu PDF-a (sekcja 4, p. 4). |
| *Kubernetes: Up and Running*, książki o Linuksie | Poza zakresem pracy (Kubernetes wyłączony) albo czysto warsztatowe. |

## 4. Ustalenia i otwarte kwestie

1. **Suehring nie obejmuje standardów.** W tekście książki nie ma odwołań do NIST, SSDF ani SLSA, a łańcuch dostaw pojawia się tylko przy SBOM (s. 101). Przypisanie „Suehring → rozdz. 3” z definicji zadania nie potwierdza się dla rozdziału 3 pracy. **Rozstrzygnięte 2026-10-18:** Suehring nie jest źródłem do rozdziału 3 pracy. Rozdział 3 opiera się na dokumentach źródłowych (NIST, OWASP, SLSA). Rozdz. 3 książki („Integrating Security”) jest zmapowany do 2.1, 2.4 i 4.4. Decyzję podjął agent, bo autor ją agentowi przekazał. Zmiana jest też w `Zrodla/_Rdzen.md` w vaulcie.
2. **Laster nie opisuje OIDC** (wydanie z 2023; brak trafień w pełnym tekście). Uwierzytelnianie GitHub Actions w AWS przez OIDC opisuje Brikman (s. 204–206), a szczegóły trzeba sprawdzić w aktualnej dokumentacji GitHub i AWS (E02-10).
3. **2.3 (chmura) ma słabe pokrycie w książkach:** tylko Brikman rozdz. 1 i Gift rozdz. 9. Oparcie w pracach z rdzenia (Alghawli2024, Janczewski2025) i w dokumentacji AWS (model współdzielonej odpowiedzialności, E02-10).
4. **Docker: Up & Running.** Żadna książka z rdzenia nie opisuje Dockera w całości (Suehring s. 101–112, Gift rozdz. 11, Brikman s. 249–252 to krótkie wprowadzenia). **Decyzja autora (2026-10-18): dodać.** TODO: autor przekazuje PDF. Potem agent zakłada notatkę w rejestrze z metadanymi ze strony redakcyjnej i dopisuje książkę do sekcji 0–2.
5. **Ansible warunkowo.** Mapa Meijer2022 ma sens tylko wtedy, gdy Ansible zostanie w zakresie (harmonogram, ADR).
6. **Metadane potwierdzone na stronach redakcyjnych** (otwarte kwestie z E02-01):
   - ISBN Meijer2022 to 978-1-098-10915-8,
   - rok Skoulikari2023 to 2023 (First Edition, maj 2023),
   - Lubanovic2023 i Gift2019 mają copyright o rok późniejszy niż pierwsze wydanie (2024 i 2020). W opisie bibliograficznym zostaje rok wydania (2023 i 2019).
7. **Wersje narzędzi w książkach są starsze niż w projekcie** (Terraform 1.2, tfsec jako osobne narzędzie, a dziś jego reguły są w Trivy). Fakty o narzędziach sprawdzać w aktualnej dokumentacji (`docs/narzedzia.md`, E02-10).
