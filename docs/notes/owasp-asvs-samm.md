# OWASP Top 10:2025, ASVS 5.0.0 i SAMM 2.2.0: notatki przeglądowe

- **Źródła:** [@OWASP-Top10-2025], [@OWASP-ASVS-5.0], [@OWASP-SAMM-2.2].
- **Zadanie:** E02-06 (tablica zadań). Używane w podrozdziale 3.3 (tło), w 4.1 (aplikacja badawcza) i w katalogu podatności referencyjnych (E03-03).
- **Zakres:** przegląd, nie pełna lektura. Według definicji zadania „wystarczy poziom tła”.
- **Skąd tekst:** notatki przygotował agent (Claude Code) 2026-10-09 na podstawie tekstu źródeł pobranego z oficjalnych repozytoriów OWASP na GitHubie, nie z pamięci:

  | Źródło | Repozytorium | Wersja (ref) | Pliki |
  |---|---|---|---|
  | Top 10:2025 | `OWASP/Top10` | `master`, commit `3a31f35` (2026-09-24) | `2025/docs/en/*.md` |
  | ASVS 5.0.0 | `OWASP/ASVS` | tag `v5.0.0_release` (2025-05-30), commit `5cf9b03` | `5.0/en/*.md`, `5.0/docs_en/…_5.0.0_en.csv` |
  | SAMM 2.2.0 | `owaspsamm/core` | tag `v2.2.0` (2026-07-06), commit `21352e0` | `model/**/*.yml` |

- **Numery stron:** Top 10 i SAMM to dokumenty webowe bez numeracji stron. ASVS cytujemy identyfikatorem wymagania w formacie zalecanym przez sam standard, np. `v5.0.0-1.2.5` (rozdz. „How to Reference ASVS Requirements”). Strony PDF nie są potrzebne.
- **Stan lektury:** autor przeczytał opracowanie z pytaniami kontrolnymi ([`owasp-asvs-samm-pytania.md`](owasp-asvs-samm-pytania.md)); oryginałów nie czytał. W rejestrze `zweryfikowane: opracowanie` (2026-10-09).

## Jak czytać ten plik

1. Sekcje 1–3 zawierają notatki do każdego dokumentu.
2. Sekcja 4 porównuje trzy dokumenty. To materiał do 3.3.
3. Sekcja 5 zawiera **wybrane wymagania ASVS dla aplikacji badawczej** (kryterium ukończenia E02-06).
4. Sekcja 6 przypisuje kandydatów do katalogu podatności (E03-03) do CWE i kategorii Top 10:2025.
5. Sekcja 7 to decyzje do podjęcia przez autora i otwarte kwestie.

Wybory w sekcjach 5 i 6 to **propozycje agenta**, nie decyzje.

---

## 1. OWASP Top 10:2025

### 1.1. Czym jest

- Dokument świadomościowy (*awareness document*) o najważniejszych ryzykach aplikacji webowych, a nie standard weryfikacji. Nie daje kryteriów „spełnia / nie spełnia”. Do weryfikacji służy ASVS (sekcja 2).
- Ósma edycja. Poprzednia: 2021.
- **Status i data:** w repozytorium oznaczenie wersji kandydującej (RC) usunięto 2025-12-24 (commity „Remove RC notice” i „Removed RC”). TODO: zweryfikować oficjalną datę wydania na owasp.org, bo strona top10.owasp.org jej nie podaje (por. notatka źródła).
- **Autorzy wiodący** (*Lead Authors*): Andrew van der Stock, Brian Glas, Neil Smithline, Tanya Janca, Torsten Gigler. Notatka źródła ma jako autora „OWASP Foundation” (decyzja w sekcji 7).

### 1.2. Metodyka (rozdz. „Introduction”)

- Lista jest oparta na danych (*data-informed*), ale nie wyłącznie na nich (*not blindly data-driven*). 8 kategorii pochodzi z danych, a 2 z ankiety wśród praktyków. Uzasadnienie: dane z testów pokazują przeszłość, bo nowe klasy podatności trafiają do narzędzi z opóźnieniem.
  - Których dwóch kategorii dotyczy ankieta, dokument nie mówi wprost w jednym miejscu. Z opisów kategorii wynika, że chodzi o A03 (najwyżej w ankiecie, połowa respondentów dała ją na 1. miejsce) i A09 („ponownie wybrana” głosami ankiety). TODO: zweryfikować przed cytowaniem.
- Dane: ponad 2,8 mln aplikacji od kilkunastu dostawców (m.in. Semgrep, Sonar, Veracode, Contrast Security, Bugcrowd).
- Miarą jest **częstość występowania w populacji aplikacji** (*incidence rate*), czyli odsetek aplikacji z co najmniej jednym wystąpieniem danego CWE. Liczba wystąpień w aplikacji się nie liczy, bo testy automatyczne raportują każde wystąpienie osobno, a testerzy ręczni zwykle raz.
  - To ta sama logika co liczenie unikalnych zgłoszeń przy H2b w `docs/metodyka.md`, p. 2.2. Można się na to powołać w 5.1.
- Analizowano 589 CWE. Kategorie grupują CWE, z limitem 40 na kategorię. Autorzy wolą kategorie od listy 10 pojedynczych CWE z dwóch powodów: nie każde CWE dotyczy każdego języka, a ta sama podatność ma często kilka CWE.
- Kategorie mają w miarę możliwości opisywać **przyczynę** (np. błąd kryptograficzny), a nie objaw (np. ujawnienie danych).
- Druga połowa oceny ryzyka to średnie wskaźniki *Exploit* i *Impact* z CVSS v2/v3 dla CVE przypisanych do CWE w NVD (ok. 220 tys. CVE). CVSS v4 nie użyto, bo nie daje osobno tych dwóch składowych.

### 1.3. Kategorie

Liczby z tabel „Score table” w plikach kategorii. Zmiany względem 2021 według rozdz. „Introduction”.

| ID | Kategoria | CWE | Śr. częstość | Zmiana względem 2021 | Przykładowe CWE (z listy kategorii) |
|---|---|---|---|---|---|
| A01 | Broken Access Control | 40 | 3,74% | bez zmian (#1), dołączono SSRF | 22 path traversal, 639 IDOR, 862, 918 SSRF, 352 CSRF |
| A02 | Security Misconfiguration | 16 | 3,00% | z #5 na #2 | 489 aktywny kod debug, 942 zbyt szeroka polityka cross-domain, 16 |
| A03 | Software Supply Chain Failures | 6 | 5,72% | nowa nazwa i szerszy zakres dawnej A06:2021 | 1395 zależność z podatnością, 1104 nieutrzymywany komponent, 1357 |
| A04 | Cryptographic Failures | 32 | 3,80% | z #2 na #4 | 327 słaby algorytm, 916 słaby hash hasła, 321 zakodowany klucz, 338 słaby PRNG |
| A05 | Injection | 37 | 3,08% | z #3 na #5 | 89 SQL, 78 OS command, 79 XSS, 95 eval |
| A06 | Insecure Design | 39 | 1,86% | z #4 na #6 | 311 brak szyfrowania, 434 upload, 693, 841 |
| A07 | Authentication Failures | 36 | 2,92% | bez zmian (#7), skrócona nazwa | 798 zakodowane poświadczenia, 307 brute force, 1392 domyślne poświadczenia |
| A08 | Software or Data Integrity Failures | 14 | 2,75% | bez zmian (#8) | 502 deserializacja, 829, 494 pobieranie kodu bez kontroli integralności |
| A09 | Security Logging & Alerting Failures | 5 | 3,91% | bez zmian (#9), nacisk na alertowanie | 117 log injection, 532 dane wrażliwe w logu, 778 |
| A10 | Mishandling of Exceptional Conditions | 24 | 2,95% | nowa | 209 komunikat błędu z danymi wrażliwymi, 636 *failing open* |

Łącznie 249 CWE według tabel (rozdz. „Introduction” podaje 248).

### 1.4. Co z tego dotyczy potoku CI/CD

- **A03** dotyczy wprost łańcucha dostaw i potoku. Opis:
  - wymienia jako podatność m.in. brak regularnego skanowania zależności, brak rozdziału obowiązków (jedna osoba nie powinna sama doprowadzić kodu do produkcji) i potok CI/CD słabiej zabezpieczony niż systemy, które buduje i wdraża,
  - zaleca SBOM, inwentaryzację zależności przechodnich i narzędzia SCA,
  - zaleca też utwardzenie repozytorium, potoku i artefaktów: ochronę gałęzi, brak sekretów w repozytorium, podpisy, provenance, promowanie artefaktu zamiast przebudowy dla każdego środowiska, IaC przez PR.

  To bliskie SP 800-204D ([@NIST-SP800-204D]). Wymóg rozdziału obowiązków jest w tym projekcie ograniczeniem (projekt jednoosobowy, `docs/metodyka.md`, p. 1.5).
- **A08** obejmuje potok pobierający kod lub artefakty z niezaufanych źródeł bez weryfikacji (np. podpisu). Tu mieści się m.in. niepinowana akcja GitHub (CWE-829).
- **A02** obejmuje konfigurację usług chmurowych (przykład: uprawnienia kubełków S3) i nagłówki bezpieczeństwa. Zaleca też federację tożsamości i krótkotrwałe poświadczenia zamiast statycznych kluczy w kodzie, konfiguracji i potokach. Tak uwierzytelniamy się do AWS (OIDC, `AGENTS.md`).

### 1.5. Niespójności w źródle

Warto je znać, zanim zacytujemy liczby:

| Miejsce | Wartość A | Wartość B |
|---|---|---|
| A03: liczba CWE | „Introduction”: 5 | tabela i lista kategorii: 6 |
| A05: liczba CWE | „Introduction”: 38 | tabela i lista kategorii: 37 |
| Suma CWE w kategoriach | „Introduction”: 248 | suma z tabel: 249 |
| A01: średnia częstość | „Introduction”: 3,73% | tabela: 3,74% |
| A03: średnia częstość | „Background” A03: 5,19% | tabela: 5,72% |
| A03: przestarzała funkcja | „Background”: CWE-477 | lista CWE: CWE-447 (prawdopodobnie literówka, bo nazwa „Use of Obsolete Function” należy do CWE-477) |

W tekście pracy podawać liczby z tabel kategorii i zaznaczyć, skąd pochodzą.

---

## 2. OWASP ASVS 5.0.0

### 2.1. Czym jest

- Standard wymagań bezpieczeństwa dla aplikacji webowych i usług. Wersja 5.0.0 z maja 2025, licencja CC BY-SA 4.0.
- **Liderzy projektu** (rozdz. „Frontispiece”): Elar Lang, Josh C Grossman, Jim Manico, Daniel Cuthbert. Notatka źródła `OWASP-ASVS-5.0` wymienia trzech, bez Jima Manico (decyzja w sekcji 7).
- **Zakres:** wymagania dotyczą produktu, nie procesu wytwarzania. ASVS wprost nie określa, jak budować aplikację w potoku CI/CD, tylko jaki efekt bezpieczeństwa ma osiągnąć sama aplikacja. Jednocześnie zaznacza, że wymagania trzeba oceniać razem z wytycznymi dla innych części cyklu życia, w tym CI/CD.
  - Dlatego w tej pracy ASVS jest podstawą wymagań wobec **aplikacji** i katalogu podatności, a nie listy kontrolnej **potoku** (zgodnie z `docs/metodyka.md`, p. 1.5).
- Każde wymaganie musi mieć wpływ na bezpieczeństwo i dawać się zweryfikować z wynikiem „pass/fail”. ASVS zawiera tylko wymagania (*must*), bez zaleceń (*should*).
- **Wymagania dokumentacyjne:** pierwsze sekcje niektórych rozdziałów wymagają udokumentowania decyzji (np. reguł walidacji, reguł autoryzacji, terminów usuwania podatności w zależnościach). Każde ma powiązane wymaganie implementacyjne. Weryfikacja dokumentacji i weryfikacja implementacji to dwie osobne czynności.

### 2.2. Poziomy

| Poziom | Charakter | Liczba wymagań w 5.0.0 |
|---|---|---|
| L1 | minimum, pierwsza linia obrony przed częstymi atakami bez warunków wstępnych | 70 (20%) |
| L2 | poziom, do którego powinna dążyć większość aplikacji; rzadsze ataki albo bardziej złożone zabezpieczenia | 183 (spełnienie L2 = L1 + L2, ok. 70% wszystkich) |
| L3 | obrona w głąb i zabezpieczenia trudne we wdrożeniu | 92 |

Razem 345 wymagań w 17 rozdziałach (liczby policzone z pliku CSV standardu, zgodne z rozdz. „Changes Compared to v4.x”).

- Poziom wybiera organizacja według ryzyka i dojrzałości. ASVS nie przypisuje poziomów do typów aplikacji. Przykład z dokumentu: startup z niewielką ilością danych wrażliwych może zacząć od L1, a bank trudno uzasadni coś poniżej L3.
- O poziomie decyduje stosunek redukcji ryzyka do nakładu wdrożenia, a nie testowalność z zewnątrz (zmiana względem 4.x). W 4.0.3 było 128 wymagań L1 z 278, w 5.0.0 jest 70 z 345.

### 2.3. Zmiany względem 4.x ważne dla tej pracy

- **Brak mapowania na CWE.** Wersja 5.0 zrezygnowała z bezpośredniego mapowania wymagań na CWE (i na NIST SP 800-63). Powód: CWE kategorii, trudność przypisania wymagania do jednego CWE, nieprecyzyjne mapowania w 4.x.
  - **Konsekwencja dla E03-03:** CWE dla pozycji katalogu bierzemy z list CWE kategorii Top 10:2025 (sekcja 6), a nie z ASVS. ASVS daje wymaganie, które pozycja katalogu łamie.
  - Repozytorium ASVS ma plik `5.0/mappings/v5.0.be_cwe_mapping.json`, ale dotyczy wersji roboczej („bleeding edge”), nie 5.0.0. Nie używamy go jako źródła.
- Nowe rozdziały: V3 Web Frontend Security, V9 Self-contained Tokens, V10 OAuth and OIDC, V15 Secure Coding and Architecture, V17 WebRTC. Usunięto dawny rozdział V1 Architecture.
- ASVS zachęca do własnej, okrojonej wersji standardu: pomija się rozdziały niestosowalne (np. OAuth, WebRTC), byle zachować identyfikatory wymagań.

### 2.4. Rozdziały

| Rozdział | L1 | L2 | L3 | Stosowalność do aplikacji badawczej (propozycja) |
|---|---|---|---|---|
| V1 Encoding and Sanitization | 8 | 19 | 3 | tak |
| V2 Validation and Business Logic | 4 | 7 | 2 | tak |
| V3 Web Frontend Security | 8 | 11 | 12 | częściowo (nagłówki, CORS, ciasteczka; zależy od tego, czy aplikacja ma frontend, E04) |
| V4 API and Web Service | 2 | 8 | 6 | tak (REST), bez WebSocket i GraphQL |
| V5 File Handling | 4 | 5 | 4 | jeśli aplikacja przyjmuje pliki (E04) |
| V6 Authentication | 13 | 22 | 12 | tak, bez MFA na L1 |
| V7 Session Management | 6 | 12 | 1 | tak |
| V8 Authorization | 4 | 3 | 6 | tak |
| V9 Self-contained Tokens | 4 | 3 | 0 | jeśli JWT (E04) |
| V10 OAuth and OIDC | 5 | 24 | 7 | nie (brak OAuth) |
| V11 Cryptography | 3 | 11 | 10 | częściowo (hashowanie haseł, losowość) |
| V12 Secure Communication | 3 | 6 | 3 | tak (TLS na granicy AWS) |
| V13 Configuration | 1 | 12 | 8 | tak (sekrety, tryb debug) |
| V14 Data Protection | 2 | 7 | 4 | częściowo |
| V15 Secure Coding and Architecture | 3 | 10 | 8 | tak (zależności, SBOM) |
| V16 Security Logging and Error Handling | 0 | 16 | 1 | tak |
| V17 WebRTC | 0 | 7 | 5 | nie |

---

## 3. OWASP SAMM 2.2.0

### 3.1. Czym jest

- Model dojrzałości (*maturity model*) praktyk bezpieczeństwa oprogramowania w **organizacji**, a nie wymagania wobec aplikacji ani potoku.
- **Struktura:** 5 funkcji biznesowych, w każdej 3 praktyki (razem 15). Każda praktyka ma 2 strumienie (*streams*) i 3 poziomy dojrzałości, a na każdym poziomie jedną czynność (*activity*) w każdym strumieniu.

  | Funkcja | Praktyki |
  |---|---|
  | Governance | Strategy and Metrics, Policy and Compliance, Education and Guidance |
  | Design | Threat Assessment, Security Requirements, Secure Architecture |
  | Implementation | Secure Build, Secure Deployment, Defect Management |
  | Verification | Architecture Assessment, Requirements-driven Testing, Security Testing |
  | Operations | Incident Management, Environment Management, Operational Management |

- **Poziomy dojrzałości:**
  1. czynność wykonywana doraźnie, „najlepszym wysiłkiem”,
  2. spójny, powtarzalny proces, na którym można polegać,
  3. maksymalna skuteczność dzięki ciągłemu doskonaleniu na podstawie informacji zwrotnej.
- **Wersja 2.2.0 względem 2.1.0:** 18 commitów, 117 zmienionych plików, żaden plik nie doszedł ani nie zniknął. Zmiany są redakcyjne (gramatyka, ujednolicenie terminologii, zestawy odpowiedzi, zależności między czynnościami). Struktura modelu się nie zmieniła. Wydanie v2.2.0 nie ma opisu zmian. Strona owaspsamm.org/model mogła jeszcze opisywać v2.0 (notatka źródła). TODO: zweryfikować przed cytowaniem, którą wersję pokazuje strona.

### 3.2. Praktyki związane z potokiem

| Praktyka / strumień | Poziom 1 | Poziom 2 | Poziom 3 |
|---|---|---|---|
| Secure Build / Build Process | zdefiniowany, spójny proces budowania | automatyzacja budowania z wbudowanymi narzędziami bezpieczeństwa (np. SAST) | egzekwowanie progu bezpieczeństwa: przerwanie buildu po przekroczeniu kryteriów, wyjątki tylko zatwierdzone i z uzasadnieniem |
| Secure Build / Software Dependencies | spis zależności (BOM) i sprawdzanie znanych podatności | przegląd zależności pod kątem bezpieczeństwa | testowanie zależności jak własnego kodu |
| Secure Deployment / Deployment Process | powtarzalny proces wdrożenia | automatyzacja wdrożenia z kontrolami bezpieczeństwa | weryfikacja integralności (podpisów) artefaktów przed wdrożeniem |
| Secure Deployment / Secret Management | ochrona sekretów w konfiguracji i kodzie, brak sekretów produkcyjnych u programistów | dołączanie sekretów dopiero przy wdrożeniu | zarządzanie cyklem życia sekretów (rotacja, wykrywanie nadużyć) |
| Security Testing / Scalable Baseline | automatyczne testy bezpieczeństwa | przypadki testowe specyficzne dla aplikacji | narzędzia testujące wbudowane w potok, wyniki na bieżąco |
| Defect Management / Defect Tracking | centralne śledzenie defektów bezpieczeństwa | ocena i klasyfikacja defektów | SLA na usuwanie defektów |

- **Do 3.3 i 4.3:** czynność Secure Build na poziomie 3 opisuje to samo co bramki blokujące w wariancie B: zdefiniowane kryteria, przerwanie buildu, wyjątki zatwierdzane i logowane z uzasadnieniem. Wątek wyjątków łączy się z [@Biswas2025]. TODO: zweryfikować to powiązanie przy lekturze E02-08.
- **Do 5.3:** poziomy SAMM opisują organizację (proces, ludzi, metryki). Jednoosobowy projekt może zrealizować techniczną część czynności, ale nie część organizacyjną (np. SLA, raportowanie kierownictwu). Ocenę dojrzałości SAMM warto więc najwyżej opisać, a nie mierzyć. Nie jest to pytanie badawcze (RQ1–RQ3).

---

## 4. Porównanie trzech dokumentów (materiał do 3.3)

| | Top 10:2025 | ASVS 5.0.0 | SAMM 2.2.0 |
|---|---|---|---|
| Rodzaj | lista świadomościowa ryzyk | standard weryfikacji | model dojrzałości |
| Przedmiot | aplikacja webowa | aplikacja webowa i usługi | organizacja i jej proces wytwarzania |
| Jednostka | kategoria ryzyka (grupa CWE) | wymaganie (pass/fail) | praktyka → strumień → czynność na poziomie 1–3 |
| Poziomy | brak (ranking 1–10) | L1–L3 | dojrzałość 1–3 |
| Podstawa | dane z testów aplikacji i ankieta | konsensus ekspertów | konsensus ekspertów, benchmark |
| Rola w pracy | klasyfikacja pozycji katalogu i znalezisk skanerów (E03-03, rozdz. 5) | wymagania wobec aplikacji badawczej i odniesienie dla pozycji katalogu (4.1) | tło procesowe: gdzie potok mieści się w modelu dojrzałości (3.3, 5.3) |

Teza do 3.3: trzy dokumenty odpowiadają na różne pytania. Top 10 mówi, **czego się bać**, ASVS, **co sprawdzić w aplikacji**, a SAMM, **jak dojrzały jest proces**. Żaden nie jest listą kontrolną potoku CI/CD. Tę rolę w pracy pełnią SP 800-204D i OWASP Top 10 CI/CD Security Risks (`docs/metodyka.md`, p. 1.5).

---

## 5. Wybrane wymagania ASVS dla aplikacji badawczej (propozycja)

Kryteria wyboru:

1. Wymaganie dotyczy elementu, który aplikacja FastAPI na pewno będzie miała (REST API, uwierzytelnianie, baza danych, kontener, logi).
2. Pierwszeństwo mają L1. L2 dobrano wtedy, gdy wymaganie odpowiada pozycji planowanej w katalogu E03-03.
3. Kolumna „Rola” mówi, czy aplikacja ma wymaganie **spełniać** (bazowa), czy wymaganie jest celowo **łamane** przez pozycję katalogu (katalog). Pozycja katalogu łamie wymaganie tylko w kontrolowanym miejscu, reszta aplikacji je spełnia.
4. Kolumna „Kto może wykryć” to wstępna klasa narzędzia. Konkretny detektor przypisze E03-03 po wyborze narzędzi (E02-10).

Opisy wymagań to streszczenia, nie tłumaczenia. Cytować z identyfikatorem `v5.0.0-…`.

| ID (v5.0.0-) | Poz. | Wymaganie (streszczenie) | Rola | Kto może wykryć |
|---|---|---|---|---|
| 1.2.4 | L1 | zapytania do bazy parametryzowane albo przez ORM | katalog (SQL injection) | SAST, DAST |
| 1.2.5 | L1 | ochrona przed wstrzyknięciem poleceń systemu operacyjnego | katalog (opcjonalnie) | SAST |
| 1.3.2 | L1 | brak `eval()` i podobnego dynamicznego wykonania kodu | katalog (eval) | SAST |
| 1.3.6 | L2 | ochrona przed SSRF przez listę dozwolonych adresów | katalog (opcjonalnie) | SAST częściowo |
| 1.5.2 | L2 | bezpieczna deserializacja niezaufanych danych | katalog (pickle) | SAST |
| 2.2.1 | L1 | walidacja wejścia według oczekiwań biznesowych (lista dozwolonych wartości, zakresy) | bazowa (modele Pydantic) | przegląd ręczny |
| 3.4.1 | L1 | nagłówek HSTS na wszystkich odpowiedziach | bazowa albo katalog (nagłówki) | DAST |
| 3.4.2 | L1 | stała wartość `Access-Control-Allow-Origin` albo lista dozwolonych źródeł | katalog (CORS `*`) | DAST, SAST |
| 3.4.3 | L2 | nagłówek Content-Security-Policy | katalog (nagłówki) | DAST |
| 3.4.4 | L2 | `X-Content-Type-Options: nosniff` | katalog (nagłówki) | DAST |
| 3.4.6 | L2 | dyrektywa CSP `frame-ancestors` na każdej odpowiedzi | katalog (clickjacking, GT-13; dodane w E03-03) | DAST |
| 5.3.2 | L1 | ścieżki plików z danych zaufanych, nie z nazw podanych przez użytkownika | katalog (path traversal) | SAST, DAST częściowo |
| 6.2.1 | L1 | hasło co najmniej 8 znaków | bazowa | przegląd ręczny |
| 6.3.1 | L1 | ochrona przed credential stuffing i brute force według dokumentacji | bazowa | przegląd ręczny |
| 6.3.2 | L1 | brak domyślnych kont (`admin`, `root`) | katalog (opcjonalnie) | przegląd ręczny, skaner sekretów częściowo |
| 8.2.1 | L1 | dostęp do funkcji tylko z jawnym uprawnieniem | katalog (poza zasięgiem narzędzi) | przegląd ręczny |
| 8.2.2 | L1 | dostęp do danych tylko z jawnym uprawnieniem do konkretnego obiektu (IDOR/BOLA) | katalog (poza zasięgiem narzędzi) | przegląd ręczny |
| 9.1.1 | L1 | weryfikacja podpisu tokenu (JWT) przed użyciem jego treści | bazowa (jeśli JWT) | SAST częściowo |
| 9.1.2 | L1 | lista dozwolonych algorytmów tokenu (np. bez `none`) | bazowa albo katalog (jeśli JWT) | SAST częściowo |
| 11.4.1 | L1 | tylko zatwierdzone funkcje skrótu, bez MD5 | katalog (słaby hash) | SAST |
| 11.4.2 | L2 | hasła przechowywane z użyciem funkcji wyprowadzania klucza o dużym koszcie obliczeniowym | katalog (słaby hash haseł) | SAST częściowo |
| 11.5.1 | L2 | wartości nieprzewidywalne z CSPRNG, min. 128 bitów entropii | katalog (opcjonalnie: `random` zamiast `secrets`) | SAST |
| 13.3.1 | L2 | sekrety w rozwiązaniu do zarządzania sekretami, nie w kodzie | katalog (zakodowany sekret) | skaner sekretów, SAST |
| 13.4.1 | L1 | wdrożenie bez metadanych systemu kontroli wersji (`.git`) | katalog (opcjonalnie: `.git` w obrazie) | skaner obrazu, DAST |
| 13.4.2 | L2 | tryb debug wyłączony na produkcji | katalog (debug) | SAST, DAST |
| 14.2.1 | L1 | dane wrażliwe nie w URL ani query string | bazowa | przegląd ręczny |
| 15.1.1 | L1 | udokumentowane terminy usuwania podatności w komponentach zewnętrznych | bazowa (dokument, łączy się z polityką bramek SCA) | — |
| 15.1.2 | L2 | inwentarz komponentów (SBOM) | bazowa (realizuje potok) | generator SBOM |
| 15.2.1 | L1 | brak komponentów po terminie usunięcia podatności | katalog (zależność z CVE) | SCA, skaner obrazu |
| 15.3.1 | L1 | API zwraca tylko potrzebne pola obiektu | katalog (opcjonalnie: nadmiarowe dane) | przegląd ręczny |
| 15.3.3 | L2 | ochrona przed mass assignment (dozwolone pola per akcja) | katalog (GT-20, poza zasięgiem; dodane w E03-03) | przegląd ręczny |
| 16.3.1 | L2 | logowanie operacji uwierzytelniania, udanych i nieudanych | bazowa | przegląd ręczny |
| 16.4.1 | L2 | kodowanie danych w logach przeciw log injection | bazowa | SAST częściowo |
| 16.5.1 | L2 | ogólny komunikat przy błędzie, bez stack trace i danych wewnętrznych | katalog (opcjonalnie) | DAST |

Podsumowanie wyboru: 32 wymagania (20 L1, 12 L2): 21 do celowego złamania w katalogu, 9 bazowych i 2 w obu rolach (3.4.1, 9.1.2). Przy budowie katalogu (E03-03, 2026-10-09) dodano 2 wymagania L2 łamane przez nowe pozycje: 3.4.6 (GT-13) i 15.3.3 (GT-20). Razem 34 wymagania (20 L1, 14 L2). Ostateczny katalog: `experiment/ground-truth.yaml`; tabela w sekcji 6 to materiał wejściowy, częściowo zastąpiony przez katalog. Pozycje „opcjonalnie” to zapas na wypadek, gdyby katalog potrzebował więcej pozycji w danej kategorii.

Propozycja poziomu docelowego: aplikacja spełnia **L1 w stosowalnych rozdziałach** (z wyjątkiem miejsc celowo złamanych w katalogu) **i wybrane wymagania L2 z tabeli**. Pełne L2 wymagałoby m.in. całego rozdziału logowania (V16) i zarządzania kluczami (V11.1), co wykracza poza cel aplikacji badawczej. Decyzja w sekcji 7.

---

## 6. Materiał do E03-03: kandydaci do katalogu w kategoriach Top 10:2025

Kandydaci pochodzą z definicji E03-03 na tablicy. CWE sprawdzono na listach CWE kategorii Top 10:2025 (sekcja „List of Mapped CWEs” w każdym pliku kategorii). Ostateczny dobór pozycji, plików i detektorów to zadanie E03-03.

| Kandydat | Grupa katalogu | Proponowane CWE | Kategoria Top 10:2025 | Wymaganie ASVS | Uwagi |
|---|---|---|---|---|---|
| SQL injection | kod | CWE-89 | A05 | 1.2.4 | |
| Zakodowany sekret | kod | CWE-798 | A07 | 13.3.1 | alternatywnie CWE-540 (A01) dla sekretu w kodzie albo CWE-321 (A04) dla klucza kryptograficznego |
| Słaby hash haseł | kod | CWE-916 | A04 | 11.4.2 | MD5 jako skrót: CWE-328 (A04), ASVS 11.4.1 |
| `eval` | kod | CWE-95 | A05 | 1.3.2 | |
| `pickle` na danych użytkownika | kod | CWE-502 | A08 | 1.5.2 | |
| Path traversal | kod | CWE-22 | A01 | 5.3.2 | |
| Zależność z publicznym CVE | zależności | CWE-1395 | A03 | 15.2.1 | numer CVE wybrać i sprawdzić w NVD/OSV przy E03-03, nie z pamięci |
| Stary obraz bazowy | kontener | CWE-1395 albo CWE-1104 | A03 | 15.2.1 | |
| Kontener uruchamiany jako root | kontener | CWE-250 | **brak na listach Top 10:2025** | — | najbliżej CWE-269 (A06). Decyzja: CWE-250 bez kategorii albo CWE-269 z A06 |
| SG otwarty na 0.0.0.0/0, port 22 | IaC | CWE-284 | A01 | — | CWE-16 (A02) to CWE kategorii, MITRE odradza mapowanie na takie CWE. TODO: zweryfikować zalecenie MITRE |
| Nieszyfrowany EBS/S3 | IaC | CWE-311 | A06 | — | w 2025 CWE-311 jest w A06, nie w A04 |
| IMDSv1 | IaC | TODO | TODO | — | brak oczywistego CWE na listach. Kandydaci: CWE-1188 (spoza list), kontekst SSRF CWE-918 (A01). Do decyzji w E03-03 |
| CORS `*` | konfiguracja web | CWE-942 | A02 | 3.4.2 | |
| Brak nagłówków bezpieczeństwa | konfiguracja web | CWE-693 | A06 | 3.4.1, 3.4.3, 3.4.4 | dla braku `frame-ancestors` CWE-1021 (A06). Opis A02 też wymienia brak nagłówków |
| Tryb debug na produkcji | konfiguracja web | CWE-489 | A02 | 13.4.2 | |
| Stack trace w odpowiedzi | konfiguracja web | CWE-209 | A10 | 16.5.1 | |
| Nadmierne uprawnienia `GITHUB_TOKEN` | workflow | CWE-732 | A01 | — | alternatywnie CWE-250 (spoza list). Odpowiednik w OWASP Top 10 CI/CD (E02-04) |
| Niepinowana akcja | workflow | CWE-829 | A08 | — | alternatywnie CWE-1357 (A03) albo CWE-494 (A08). Odpowiednik w OWASP Top 10 CI/CD (E02-04) |
| Błąd logiki autoryzacji (IDOR) | poza zasięgiem narzędzi | CWE-639 | A01 | 8.2.2 | |
| Brak autoryzacji funkcji | poza zasięgiem narzędzi | CWE-862 | A01 | 8.2.1 | |
| Obejście kolejności kroków | poza zasięgiem narzędzi | CWE-841 | A06 | 2.3.1 | |

Wnioski dla E03-03:

- Każda grupa katalogu ma kandydatów w co najmniej jednej kategorii Top 10:2025. Pozycje dotyczą 9 z 10 kategorii, brakuje tylko A09. Log injection (CWE-117, A09, ASVS 16.4.1) może ją uzupełnić.
- Pozycje IaC i workflow nie zawsze mają naturalne miejsce w Top 10:2025, bo to lista ryzyk **aplikacji**. Dla nich lepszą klasyfikacją jest OWASP Top 10 CI/CD Security Risks (E02-04) albo pozycja listy kontrolnej SP 800-204D. Proponuję w `experiment/ground-truth.yaml` dwa pola klasyfikacji: `owasp_top10_2025` (może być puste) i `owasp_cicd_top10` (dla pozycji potoku).

---

## 7. Decyzje do podjęcia przez autora i otwarte kwestie

Rozstrzygnięte 2026-10-09 (decyzje autora):

1. **Poziom docelowy ASVS dla aplikacji badawczej:** L1 w stosowalnych rozdziałach i wybrane wymagania L2 z sekcji 5. Odrzucone: pełne L2 (zbyt duży nakład na aplikację badawczą, m.in. cały rozdział V16) i samo L1 (wymagania L2 z tabeli istniałyby tylko jako pozycje katalogu).
2. **Autorzy w rejestrze źródeł:** dla wszystkich trzech dokumentów autor korporacyjny „OWASP Foundation”. Imiona liderów projektu zostają w notatkach źródeł jako informacja. Odrzucone: imienne wymienianie liderów (4 przy ASVS, 5 przy Top 10).
3. **Stan lektury:** opracowanie z pytaniami kontrolnymi ([`owasp-asvs-samm-pytania.md`](owasp-asvs-samm-pytania.md)). Po jego przeczytaniu źródła dostają `zweryfikowane: opracowanie`. Odrzucone: lektura oryginałów; same notatki bez pytań.

4. **Lista wybranych wymagań ASVS** (sekcja 5): zaakceptowana przez autora przy zamknięciu E02-06.

Do decyzji:

5. **CWE dla pozycji spoza list Top 10** (kontener jako root, IMDSv1, uprawnienia tokenu): ustalić w E03-03.

Otwarte:

- [ ] Oficjalna data wydania Top 10:2025 (TODO: zweryfikować na owasp.org).
- [ ] Które dwie kategorie Top 10:2025 pochodzą z ankiety (z opisów wynika A03 i A09; TODO: zweryfikować).
- [ ] Czy owaspsamm.org opisuje już model 2.2 (TODO: zweryfikować przed cytowaniem SAMM ze strony).
- [ ] Zalecenie MITRE co do mapowania na CWE kategorii (np. CWE-16) (TODO: zweryfikować na cwe.mitre.org przy E03-03).
