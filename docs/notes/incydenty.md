# Incydenty łańcucha dostaw: pięć studiów przypadków

- **Zadanie:** E02-12 (tablica zadań). Używane w rozdz. 1 (motywacja) i 2.2 (wektory ataku), pomocniczo w 4.3 i 5.3.
- **Źródła:** po jednej notatce na incydent w rejestrze vaulta: [@Incydent-SolarWinds], [@Incydent-Codecov], [@Incydent-xz-utils], [@Incydent-tj-actions], [@Incydent-Trivy]. Źródło główne i źródła uzupełniające są opisane w notatce (`Zrodla/Incydent-*.md`).
- **Stan lektury:** opisy przygotował agent (Claude Code) 2026-10-20 na podstawie źródeł pierwotnych otwartych tego dnia: komunikatów firm, CISA, NVD i GHSA. Wszystkie źródła to literatura szara. Autor przyjął opisy i mapowanie z sekcji 2 (2026-10-20). Piąty incydent (Trivy, 2026) dodano 2026-10-28 przy E02-04 (decyzja autora) na podstawie porady GHSA-69fq-xp46-6x23 odczytanej w oryginale przez API GitHuba.

Kolumny „Ryzyko” i „SP 800-204D” odwołują się do identyfikatorów z [@OWASP-Top10-CICD] i z listy kontrolnej w [`nist-800-204d.md`](nist-800-204d.md) (tabele A i B). Mapowanie zaproponował agent, a autor je przyjął (2026-10-20).

---

## 1. Zestawienie

| Incydent | Data | Wektor ataku | Ryzyko OWASP CI/CD | Źródło |
|---|---|---|---|---|
| SolarWinds Orion (SUNBURST) | Aktualizacje 03–06.2020, ujawnienie 13–14.12.2020 | Kompromitacja systemu budowania dostawcy. Złośliwy kod wstrzyknięty w czasie kompilacji do podpisanych aktualizacji, nieobecny w repozytorium kodu | CICD-SEC-7, CICD-SEC-9 | [@Incydent-SolarWinds] |
| Codecov Bash Uploader | 31.01–1.04.2021, ujawnienie 15.04.2021 | Zmodyfikowany skrypt firmy trzeciej pobierany i uruchamiany w CI klientów wysyłał ich zmienne środowiskowe (sekrety) na zewnętrzny serwer. Punkt wejścia: poświadczenie wydobyte z obrazu Dockera | CICD-SEC-8, CICD-SEC-6, CICD-SEC-9 | [@Incydent-Codecov] |
| xz-utils (CVE-2024-3094) | Wydania 5.6.0 i 5.6.1, ujawnienie 29.03.2024 | Złośliwy współopiekun projektu OSS. Backdoor w tarballach wydań, nieobecny w gicie, aktywowany w czasie budowania liblzma | CICD-SEC-3 | [@Incydent-xz-utils] |
| tj-actions/changed-files (CVE-2025-30066) | 14–15.03.2025 (GHSA); okno audytu CISA: 12.03 00:00 – 15.03 12:00 UTC | Przejęte poświadczenie bota opiekuna akcji, istniejące tagi przestawione na złośliwy commit, sekrety z pamięci runnera wypisywane do logów. Prawdopodobnie poprzedzone kompromitacją `reviewdog/action-setup@v1` (CVE-2025-30154) | CICD-SEC-3, CICD-SEC-8, CICD-SEC-6 | [@Incydent-tj-actions] |
| Trivy, trivy-action, setup-trivy (CVE-2026-33634) | 19–20.03.2026 (Trivy v0.69.4, akcje), 22–23.03.2026 (obrazy Docker Hub) | Przejęte poświadczenia opiekunów (niepełna rotacja po ataku z lutego 2026). Złośliwe wydanie przez własny potok wydań projektu, 76 z 77 tagów `trivy-action` i 7 tagów `setup-trivy` przestawionych na kod kradnący sekrety z runnerów użytkowników | CICD-SEC-8, CICD-SEC-6, CICD-SEC-9 | [@Incydent-Trivy] |

## 2. Co każdy incydent oznacza dla projektowanego potoku

Propozycje agenta przyjęte przez autora 2026-10-20. Kolumna „Mechanizm” wskazuje narzędzia i zasady z [`docs/narzedzia.md`](../narzedzia.md) i `AGENTS.md`. Nie twierdzi, że mechanizm zatrzymałby dany atak w całości.

| Incydent | SP 800-204D | Mechanizm w potoku | Czego mechanizm nie pokrywa |
|---|---|---|---|
| SolarWinds | BUILD-1*, BUILD-3*, ATT-1*, DEPLOY-REQ-3 | Efemeryczne runnery hostowane przez GitHub, atestacja pochodzenia (`actions/attest-build-provenance`), wdrożenie po digeście obrazu z weryfikacją atestacji | Provenance zaświadcza, *jak* i *gdzie* zbudowano artefakt, ale nie wykryje złośliwego kodu dodanego w zaufanym środowisku buildu. Tu pomogłyby buildy odtwarzalne, które są poza zakresem projektu |
| Codecov | PULL-PUSH-REQ-2, BASE-4*, BASE-8* | Narzędzia w przypiętych wersjach (akcje po SHA, obrazy po digeście), OIDC do AWS zamiast długoterminowych kluczy (zasada 4 w `AGENTS.md`), minimalne `permissions:`, kontrola ruchu wychodzącego (`step-security/harden-runner`) | Sekret, który musi być w jobie (np. `GITHUB_TOKEN`), da się wykraść w czasie trwania joba. OIDC skraca czas życia poświadczenia, ale go nie eliminuje |
| xz-utils | TEST-2*, BASE-1*, BASE-3*, BASE-4* | SCA (pip-audit, Trivy) i SBOM (Syft): po nadaniu CVE pozwalają szybko ustalić, czy zależność jest w obrazie. Przypięte wersje zależności z hashami | Do ujawnienia nie było CVE, więc skanery oparte na bazach znanych podatności nic by nie zgłosiły. SBOM pomaga w reakcji, nie w zapobieganiu |
| tj-actions | PULL-PUSH-REQ-2, PRE-1*, PRE-3* | Przypinanie akcji do pełnego SHA (zasada 5 w `AGENTS.md`; GT-16 w katalogu referencyjnym), audyt workflowów zizmorem, harden-runner (to on wykrył ten atak według GHSA), minimalne `permissions:` (GT-15) | Według Wiz workflowy przypięte do SHA nie ucierpiały, ale akcje złożone, które w środku wołały `reviewdog/action-setup@v1`, były zagrożone „regardless of version or pinning method” (NVD, CVE-2025-30154). Przypięcie z zewnątrz nie obejmuje nieprzypiętych zależności przechodnich |
| Trivy | PULL-PUSH-REQ-2, BASE-4*, PRE-1* | Przypięte SHA akcji `trivy-action` i `setup-trivy` oraz wersja Trivy (`docs/narzedzia.md`, wersje późniejsze od naprawionych), obrazy po digeście, OIDC zamiast długoterminowych kluczy, harden-runner | Według porady przypięcie `trivy-action` do SHA sprzed 9.04.2025 nie chroniło, bo ta wersja wołała nieprzypięte `setup-trivy`. Przypięty SHA trzeba aktualizować (Dependabot), a jego bezpieczeństwo zależy od tego, co akcja woła w środku. Narzędzie bezpieczeństwa zwiększa powierzchnię ataku potoku |

## 3. Opisy

### 3.1. SolarWinds Orion, 2020

Według raportu 8-K złożonego przez SolarWinds 14.12.2020 złośliwy kod był w aktualizacjach platformy Orion wydanych od marca do czerwca 2020. Dostał się tam przez kompromitację systemu budowania i nie było go w repozytorium kodu źródłowego. Firma powiadomiła ok. 33 000 klientów. Instalacji z podatną wersją miało być mniej niż 18 000. Dzień wcześniej CISA wydała dyrektywę ED 21-01 nakazującą agencjom federalnym odłączenie Orion w wersjach 2019.4–2020.2.1 HF1. Mechanizm opisał CrowdStrike: złośliwe oprogramowanie SUNSPOT działało na serwerze buildu, wykrywało proces MsBuild.exe budujący Orion i na czas kompilacji podmieniało jeden plik źródłowy na wersję z backdoorem SUNBURST, a potem przywracało oryginał.

**Wniosek dla pracy:** środowisko buildu jest osobnym ogniwem łańcucha dostaw. Kod w repozytorium może być czysty, a artefakt i tak skompromitowany.

### 3.2. Codecov, 2021

Od 31.01.2021 atakujący okresowo modyfikował skrypt Bash Uploader. Klienci pobierali go i uruchamiali w swoich potokach CI, także przez Codecov GitHub Action. Zmieniony skrypt wysyłał zmienne środowiskowe potoku i adres repozytorium na serwer spoza infrastruktury Codecov. Punktem wejścia był błąd w procesie tworzenia obrazu Dockera, który pozwolił wydobyć poświadczenie do zmiany skryptu. Modyfikację wykrył klient, który zauważył niezgodność sumy kontrolnej (1.04.2021). Codecov zalecił unieważnienie wszystkich poświadczeń dostępnych w zmiennych środowiskowych potoku. Daty potwierdziła CISA (alert z 22.04.2021).

**Wniosek dla pracy:** każde narzędzie firmy trzeciej uruchamiane w potoku ma dostęp do jego sekretów. Weryfikacja integralności narzędzia i krótkotrwałe poświadczenia ograniczają skutki takiego ataku.

### 3.3. xz-utils, 2024

29.03.2024 A. Freund opisał na liście oss-security backdoor w bibliotece liblzma z pakietu xz, wersje 5.6.0 i 5.6.1. Złośliwy kod był w tarballach wydań, a nie w repozytorium git: dodatkowa linia skryptu budowania wyciągała z repozytoryjnych „plików testowych” obiekt, który modyfikował bibliotekę. Przez zależność libsystemd od liblzma kod docierał do serwera sshd w dystrybucjach, które łatają sshd pod systemd. Podatność dostała CVE-2024-3094 z oceną CVSS 10.0. Według opiekuna projektu, L. Collina, tarballe utworzył i podpisał współopiekun występujący jako „Jia Tan”.

**Wniosek dla pracy:** zaufany opiekun zależności też może być atakującym. Skanery oparte na bazach znanych podatności reagują dopiero po ujawnieniu.

### 3.4. tj-actions/changed-files, 2025

W marcu 2025 atakujący przestawił istniejące tagi wersji akcji `tj-actions/changed-files`, używanej w ponad 23 000 repozytoriów, na złośliwy commit. Kod odczytywał sekrety z pamięci procesu runnera i wypisywał je do logów workflow zakodowane w base64. W repozytoriach publicznych logi może czytać każdy. Atak wykrył StepSecurity na podstawie nieautoryzowanego połączenia wychodzącego z runnera. Według CISA kompromitację mogła umożliwić wcześniejsza kompromitacja akcji `reviewdog/action-setup@v1` (CVE-2025-30154). Według Wiz źródłem był wyciek tokenu PAT bota z uprzywilejowanym dostępem do repozytorium akcji. Oba CVE są w katalogu KEV CISA.

**Wniosek dla pracy:** akcja GitHub to kod firmy trzeciej z dostępem do sekretów potoku, a tag git jest zmienny. Przypinanie do SHA usuwa ten wektor dla akcji wołanych bezpośrednio, ale nie dla akcji wołanych wewnątrz akcji złożonych.

### 3.5. Trivy, 2026

Według porady Aqua Security (GHSA-69fq-xp46-6x23) 19.03.2026 atakujący z przejętymi poświadczeniami opiekunów wydał złośliwą wersję skanera Trivy v0.69.4 i przestawił 76 z 77 tagów akcji `aquasecurity/trivy-action` oraz wszystkie 7 tagów `aquasecurity/setup-trivy` na złośliwe commity. Trzy dni później opublikował złośliwe obrazy na Docker Hub. Kod w akcjach uruchamiał się przed właściwym skanem, zrzucał pamięć procesu runnera, zbierał poświadczenia chmurowe i klucze, szyfrował je i wysyłał na serwer atakującego. Wydanie v0.69.4 powstało przez potok wydań samego projektu: atakujący podmienił odwołanie do `actions/checkout` na podszywający się commit i wyłączył walidację artefaktów. Przyczyną była niepełna rotacja poświadczeń po wcześniejszym ataku z lutego 2026. Nie zostali dotknięci m.in. użytkownicy obrazów przypiętych digestem i wydań chronionych funkcją „immutable releases”. Przypięcie `trivy-action` do starego SHA nie chroniło, bo ta wersja wołała nieprzypięte `setup-trivy`. Podatność dostała CVE-2026-33634 i trafiła do katalogu KEV CISA (26.03.2026).

**Wniosek dla pracy:** skaner bezpieczeństwa w potoku to też kod firmy trzeciej z dostępem do sekretów. Każde dodane narzędzie zwiększa powierzchnię ataku, a przypinanie do SHA i digestu chroni tylko wtedy, gdy obejmuje też zależności przechodnie.

## 4. Otwarte kwestie

- [x] Autor przyjął mapowanie w sekcji 2 (2026-10-20).
- [x] Artykuły naukowe o incydentach: nie dodajemy (decyzja autora z 2026-10-20). Opisy opierają się na źródłach pierwotnych od firm, CISA, NVD i GHSA.
- [ ] Raport FireEye/Mandiant o SUNBURST (13.12.2020): TODO: zweryfikować. Stary adres przekierowuje, a kopii nie udało się otworzyć.
- [ ] Jak długo „Jia Tan” współtworzył xz: TODO: zweryfikować. Strona L. Collina tego nie podaje.
- [ ] Zasada 5 w `AGENTS.md` i GT-16: czy opisać w 4.3 ograniczenie przypinania (akcje złożone, wątek reviewdog)? Wiąże się to z regułą zizmora dotyczącą niepinowanych `uses:`. TODO: sprawdzić, czy zizmor analizuje akcje złożone przechodnio. Incydent Trivy (3.5) to drugi przykład tego samego mechanizmu.
- [ ] Trivy: źródła wtórne wymienione w poradzie (Microsoft, Wiz, Aqua) nie są sprawdzone. Opis opiera się tylko na poradzie i NVD.
- [ ] Top 10 CI/CD przypisuje Codecov także do CICD-SEC-5 (dok. s. 23, por. `owasp-devsecops.md`, sekcja 8). Do decyzji autora, czy dopisać w sekcji 1.
