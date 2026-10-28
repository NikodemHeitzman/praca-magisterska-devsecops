# OWASP DevSecOps Guideline i OWASP Top 10 CI/CD Security Risks: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia [`owasp-devsecops.md`](owasp-devsecops.md), gdzie są notatki, lista ryzyk z przykładami dla potoku i propozycje do listy kontrolnej.

- Odpowiedzi opracował agent (Claude Code) 2026-10-20 na podstawie tekstu źródeł z oficjalnych repozytoriów OWASP (wersje w nagłówku notatek).
- **Top 10 CI/CD:** miejsce w źródle według numeracji dokumentu (`dok. s.`). W przeglądarce PDF strona jest o 1 większa (`PDF s.`).
- **Guideline:** dokument webowy bez stron, więc miejsce w źródle podano jako ścieżkę rozdziału, np. `2-3-5 Security Gates`.
- Po przeczytaniu tego pliku źródła dostają `zweryfikowane: opracowanie`. Szczegół z liczbą albo nazwą autor sprawdza w oryginale przed wpisaniem do tekstu pracy.

---

## 1. OWASP DevSecOps Guideline

**Czym Guideline jest, a czym nie jest?** (`0-1 Intro`)

Przewodnikiem praktyk i narzędzi do budowy bezpiecznego potoku, dla organizacji każdej wielkości. Nie jest standardem: nie ma numerowanych wymagań, mocy (MUST/SHOULD) ani procedury oceny. W pracy służy do doboru etapów i narzędzi (C2). Wymagań do listy kontrolnej nie dostarcza.

**Jaki cel stawia sobie dokument?** (`0-1 Intro`)

Wykrywać problemy bezpieczeństwa, zarówno błędy projektu, jak i podatności implementacji, jak najwcześniej i najtaniej, a potem wykrywać je dalej w sposób ciągły. Dlatego obok *shift-left* mówi o *shift-everywhere*: szybkie kontrole na początku i głębsza walidacja w buildzie, testach, wdrożeniu i działaniu (`0-2 Overview`).

**Jak dokument jest zbudowany?** (`0-1 Intro`)

Trzy filary: People (zespoły, role, szkolenia), Process (czynności bezpieczeństwa w 7 etapach: Design, Develop, Build, Test, Release, Deploy, Operate) i Governance (zgodność, policy as code, raportowanie, ASPM, zarządzanie AI). Rozdziały mają stały układ:

1. opis,
2. przykłady konfiguracji (głównie GitHub Actions),
3. typowe błędy,
4. stopnie dojrzałości,
5. metryki,
6. listy narzędzi.

**Czym DevSecOps nie jest według dokumentu?** (`0-1 Intro`, „What DevSecOps is NOT”)

Nie jest:

- zespołem bezpieczeństwa wstawionym do potoku, który zatwierdza każdy PR (to się nie skaluje),
- zakupem narzędzi (bez procesu segregacji zgłoszeń, właściciela i terminów daje to zmęczenie alertami),
- jednorazowym projektem,
- zgodnością z przepisami (audyt to „podłoga, nie sufit”),
- „tylko CI/CD”.

> Związek z pracą: argument w 2.1, że potok to tylko jedna warstwa, i ograniczenie w 5.3 (eksperyment mierzy potok, a nie cały program DevSecOps).

**Od czego dokument każe zacząć?** (`0-2 Overview`, „A recommended introduction order”)

Od trzech kontroli o największej redukcji ryzyka na jednostkę wysiłku:

1. skan sekretów w pre-commit i CI,
2. SCA w CI,
3. ochrona gałęzi i SAST w PR.

Dalej, w tej kolejności: skan IaC, skan kontenerów, DAST/IAST (wymaga środowiska testowego), SBOM i podpisy.

> Związek z pracą: punkt odniesienia dla rekomendacji z celu C6 (minimalny zestaw i kolejność). Wynik eksperymentu może tę kolejność potwierdzić albo podważyć dla małej aplikacji.

**Dlaczego hook pre-commit nie wystarcza?** (`2-2-1-1 Pre-commit`)

Bo każdy programista pominie go opcją `--no-verify`. Hook daje szybką informację zwrotną, ale kontrolą jest dopiero to samo sprawdzenie w CI, którego nie da się obejść. Dokument nazywa to modelem dwuwarstwowym.

**Jakie zasady bramek podaje dokument?** (`2-3-5 Security Gates`, „Principles for effective gates”)

1. Blokować według ryzyka (ważność, wykorzystywalność, osiągalność), a nie liczby zgłoszeń.
2. Rozliczać z nowych zgłoszeń względem stanu bazowego.
3. Mówić jasno, co i gdzie naprawić.
4. Mieć udokumentowane, ograniczone w czasie wyjątki z właścicielem.
5. Stroić reguły, bo fałszywe alarmy to błąd bramki.

Typowy punkt wyjścia: critical i high blokują, medium ostrzega, low tylko się liczy. Dokument podaje to jako przykład, nie normę.

**Co znaczy, że bramka ma działać w trybie „fail closed”?** (`2-3-5 Security Gates`, „Normalizing multi-scanner output”, „The exit code trap”)

Brak raportu skanera to błąd, a nie wynik „czysto”. Stan ERROR (skaner się nie wykonał) trzeba odróżnić od FAILED (są zgłoszenia ponad próg), bo bramka, która sprawdza tylko ważność zgłoszeń, przepuści przebieg, w którym skaner w ogóle nie zadziałał. Kody wyjścia narzędzi znaczą co innego:

- OSV-Scanner zwraca 1, gdy znajdzie podatności,
- Trivy domyślnie zwraca 0 niezależnie od wyników.

> Związek z pracą: wymaganie do projektu bramek w E07-01 (jawny `exit-code` Trivy, sprawdzenie, czy raport istnieje).

**Jak dokument każe obsługiwać wyjątki?** (`2-3-5 Security Gates`, „Exception and risk-acceptance process”)

Wniosek z uzasadnieniem i kontrolą kompensującą, zatwierdzenie przez właściciela ryzyka, termin wygaśnięcia (np. 30 lub 90 dni), centralny rejestr, przegląd cykliczny. Obejście awaryjne musi autoryzować platforma (chronione środowisko z wymaganymi recenzentami), a nie zmienna ustawiona przez osobę uruchamiającą job.

> Związek z pracą: w serii eksperymentu wyjątków nie ma, bo wyjątek zmieniałby bramkę po obejrzeniu wyników (zagrożenie TW2).

**Jak dokument każe zabezpieczyć sam potok?** (`2-3-6-3 CI/CD Pipeline Security`, `2-2-1-4 Repository Hardening`)

- OIDC zamiast długoterminowych kluczy chmurowych,
- przypinanie akcji do pełnego SHA commita,
- minimalne `permissions:` w każdym jobie,
- efemeryczne, izolowane runnery z kontrolą ruchu wychodzącego (StepSecurity Harden-Runner),
- zatwierdzanie workflow z forków,
- bez `pull_request_target` z kodem z forka,
- `persist-credentials: false` przy checkout,
- CODEOWNERS dla `.github/workflows/`,
- skan workflow zizmorem.

Niezaufane wartości z kontekstu zdarzenia (np. tytuł PR) przekazywać przez zmienne środowiskowe, a nie wstawiać do `run:`.

**Skąd wiadomo, że przypinanie do SHA ma znaczenie w praktyce?** (`2-3-6-3`, `2-3-3-1 Container Scanning`)

Dokument podaje dwa przypadki przestawienia tagów na złośliwy kod, który wykradał sekrety CI: `tj-actions/changed-files` (marzec 2025) i `aquasecurity/trivy-action` (marzec 2026). Drugi dotyczy skanera, którego używa nasz potok. Według GHSA-69fq-xp46-6x23 (21.03.2026) dotknął on tagów trivy-action sprzed 0.35.0, setup-trivy v0.2.0–v0.2.5 i binarki Trivy v0.69.4. Wersje w `docs/narzedzia.md` są późniejsze. Dane GHSA: TODO: zweryfikować w oryginale.

**Co dokument mówi o podpisach i provenance?** (`2-3-6-2`, `2-5-1 Release`, `2-6-1 Deploy`)

- **Podpis** wiąże artefakt z producentem.
- **Provenance** opisuje, jak artefakt zbudowano: commit, builder, kroki, parametry.
- **Weryfikacja:** podpis bez weryfikacji to „teatr bezpieczeństwa”. Weryfikować trzeba przy promocji i przy wdrożeniu, zawsze po digeście, w trybie „fail closed”.
- **Build raz, promocja wiele razy:** artefakt buduje się raz i ten sam promuje przez środowiska. Przebudowa na produkcję unieważnia testy.
- **SLSA na GitHub Actions:** same atestacje dają Build L2, L3 wymaga reusable workflow albo generatora SLSA. Sprawdzić w specyfikacji SLSA (E02-05).

**Jak dokument układa ramy NIST i OWASP względem siebie?** (`0-3 Frameworks and Standards`, „How they fit together”)

| Rama | Rola |
|---|---|
| SSDF | bazowy poziom zgodności |
| SAMM | dojrzałość strategiczna |
| DSOMM | wdrażanie praktyk przez inżynierów |
| SLSA | integralność łańcucha dostaw |
| Top 10 CI/CD | ryzyka samego potoku |
| ASVS, Proactive Controls, Top 10 | kontrole po stronie programisty |

Guideline sytuuje się „pośrodku” i przekłada ramy na kontrole przypisane do etapów.

> Związek z pracą: gotowa rama do 3.3.

**Co z Guideline praca bierze, a czego nie?** (notatki, p. 1.4)

Bierze etapy Develop, Build, Test, Release i Deploy w zakresie potoku na GitHub Actions z wdrożeniem do AWS. Nie bierze:

- Kubernetes i *admission control*,
- IAST,
- ASPM, BAS, CNAPP, programów zgłaszania podatności.

Powód: definicja lekkiego potoku (`docs/metodyka.md`, p. 1.1) i zakres pracy (`AGENTS.md`). Nowe propozycje do decyzji: karencja aktualizacji, „fail closed”, skan API ZAP z `openapi.json`.

---

## 2. OWASP Top 10 CI/CD Security Risks: część ogólna

**Kto i jak opracował listę?** (dok. s. 2–3)

D. Krivelevich i O. Gil z Cider Security, z 15 recenzentami z branży. Metoda według dokumentu:

- analiza architektury i zabezpieczeń „setek” środowisk CI/CD,
- rozmowy z ekspertami,
- publikacje o incydentach.

Danych nie opublikowano.

**Czy numeracja CICD-SEC-1…10 to ranking?** (dok. s. 3–4)

Dokument tego nie deklaruje. Podaje listę i stały układ opisu. W pracy nie piszemy, że CICD-SEC-1 jest „najważniejszy”.

**Jak opisane jest każde ryzyko?** (dok. s. 3)

Definicja, opis (kontekst i motywacja atakującego), skutki, rekomendacje, odniesienia do realnych przypadków.

**Dlaczego atakujący celują w CI/CD?** (dok. s. 1)

Bo usługi CI/CD to „wydajna ścieżka” do najcenniejszych zasobów organizacji. Do tego:

- rośnie liczba technologii i automatyzacji,
- podłączenie usługi firmy trzeciej wymaga 1–2 linii kodu,
- obrońcy są na wczesnym etapie.

Przykłady z dokumentu: SolarWinds, Codecov, włamanie do repozytorium PHP, dependency confusion, przejęte pakiety npm.

---

## 3. Ryzyka CICD-SEC-1…10

**CICD-SEC-1. Na czym polega brak kontroli przepływu?** (dok. s. 5–6)

Atakujący z dostępem do jednego systemu (SCM, CI, rejestru artefaktów) może sam przepchnąć kod lub artefakt aż do produkcji, bo nic nie wymusza dodatkowego przeglądu ani akceptacji. Przykłady:

- push na gałąź wdrażaną automatycznie,
- obejście reguły auto-merge,
- wyłączenia z ochrony gałęzi,
- artefakt wgrany do rejestru poza CI,
- zmiana wprost na produkcji.

Rekomendacje: ochrona gałęzi bez wyjątków, akceptacja przed potokiem produkcyjnym, tylko artefakty z zaufanego konta CI, wykrywanie dryfu.

> Mój potok: ruleset z wymaganymi *status checks* i bez obejść. Ograniczenie: brak drugiego recenzenta.

**CICD-SEC-2. Jakie problemy z tożsamościami wymienia dokument?** (dok. s. 8–9)

Tożsamości:

- nadmiernie uprzywilejowane,
- nieaktywne,
- lokalne (bez centralnego IdP),
- zewnętrzne (prywatne adresy, współpracownicy),
- samorejestrowane,
- współdzielone.

Przeciętne konto w SCM i CI jest bardzo uprzywilejowane, bo te systemy nie były dotąd w centrum uwagi zespołów bezpieczeństwa. Przejęcie prawie dowolnego konta może więc prowadzić do produkcji.

> Mój potok: większość rekomendacji (IdP, samorejestracja, domeny) nie dotyczy projektu jednoosobowego. Dotyczą: najmniejsze uprawnienia ról IAM, brak użytkowników IAM, brak kont współdzielonych.

**CICD-SEC-3. Czym nadużycie łańcucha zależności różni się od znanych podatności w zależnościach?** (dok. s. 11)

Dokument oddziela je wprost. Wykrywanie pakietów ze znanymi podatnościami to jedno. CICD-SEC-3 dotyczy *procesu pobierania*: konfiguracja klienta może sprawić, że programista albo build pobierze złośliwy pakiet zamiast zamierzonego, często od razu go uruchamiając przez skrypty instalacyjne.

> Związek z pracą: dlatego GT-07 (Jinja2 ze znanymi CVE) i GT-08 (stary obraz bazowy) nie pasują do CICD-SEC-3 w ścisłym sensie (notatki, p. 5).

**CICD-SEC-3. Jakie wektory wymienia dokument?** (dok. s. 11–12)

- *dependency confusion*: publiczny pakiet o nazwie pakietu wewnętrznego,
- *dependency hijacking*: przejęcie konta opiekuna i nowa złośliwa wersja,
- *typosquatting*,
- *brandjacking*: podszywanie się pod konwencję nazw znanej marki.

Rekomendacje:

- proxy wewnętrzne,
- weryfikacja sum i podpisów,
- przypięte wersje,
- zakresy nazw dla pakietów prywatnych,
- skrypty instalacyjne bez sekretów,
- konfiguracja menedżera pakietów w repozytorium.

Pełne zapobieganie jest „dalekie od trywialnego”, więc liczy się też wykrywanie (dok. s. 13).

**CICD-SEC-4. Czym jest Poisoned Pipeline Execution?** (dok. s. 14)

Atakujący z dostępem do SCM, ale bez dostępu do środowiska buildu, wstrzykuje polecenia do konfiguracji potoku albo do plików, z których potok korzysta. Kod wykonuje się z tożsamością i dostępem joba. Najbardziej narażone są potoki uruchamiane na kodzie bez przeglądu: na PR i na dowolnych gałęziach.

**CICD-SEC-4. Jakie są trzy odmiany PPE?** (dok. s. 14–15)

- **D-PPE:** zmiana pliku konfiguracji CI w gałęzi albo PR.
- **I-PPE:** konfiguracja CI jest chroniona (osobna gałąź, osobne repozytorium, definicja w systemie CI), więc atakujący zmienia pliki, które potok wywołuje: Makefile, skrypty, testy, konfigurację linterów i skanerów.
- **3PE:** w repozytorium publicznym PR może złożyć każdy z internetu.

> Mój potok: repozytorium jest publiczne, więc 3PE dotyczy go wprost. I-PPE przez konfigurację skanera mogłoby „wyciszyć” bramkę.

**CICD-SEC-4. Jak wygląda przykład z GitHub Actions?** (dok. s. 16–17)

Workflow buduje, testuje i wdraża do AWS. Atakujący tworzy gałąź, w której workflow odczytuje sekrety AWS repozytorium i wysyła je `curl` na swój serwer. Push uruchamia zmieniony workflow, a skradzione klucze dają dostęp do produkcji.

> Mój potok: OIDC zamiast kluczy w sekretach, workflow PR bez sekretów i bez `id-token: write`, wdrożenie tylko z chronionej gałęzi.

**CICD-SEC-4. Jakie rekomendacje podaje dokument?** (dok. s. 19)

- kod bez przeglądu na izolowanych węzłach bez sekretów,
- ograniczenie potoków z forków albo ręczna akceptacja,
- ochrona każdej gałęzi uruchamiającej wrażliwy potok,
- przegląd pliku CI przed uruchomieniem albo plik na chronionej gałęzi,
- odebranie zbędnych uprawnień w SCM,
- minimalne poświadczenia potoku.

**CICD-SEC-4. Czy GT-17 (wstrzyknięcie przez tytuł PR) to PPE?** (dok. s. 14–15; Guideline `2-3-6-3`)

Guideline tak to klasyfikuje i jako obronę przed PPE podaje niewstawianie niezaufanych wartości do `run:`. W ścisłej definicji Top 10 PPE polega na zmianie pliku. Przy GT-17 atakujący kontroluje *dane* (tytuł PR), które workflow wykonuje jako kod. To odmiana tego samego mechanizmu: niezaufana treść wykonana w zaufanym kontekście potoku.

**CICD-SEC-5. Co oznacza PBAC?** (dok. s. 21)

Kontekst, w którym działa każdy potok i każdy jego krok:

- dostęp do kodu, sekretów, zmiennych i innych potoków,
- uprawnienia do hosta i innych węzłów,
- filtry ruchu do i z internetu.

Skala szkód po wstrzyknięciu złośliwego kodu zależy od tego, jak szczegółowo ustawiono PBAC (dok. s. 22).

> Mój potok: GT-15 (`permissions: write-all`) jest przykładem braku PBAC.

**CICD-SEC-5. Jakie rekomendacje podaje dokument?** (dok. s. 22)

- osobne węzły dla potoków o różnej wrażliwości,
- sekrety przypisane do potoku i kroku,
- czysty stan węzła po każdym przebiegu,
- minimalne uprawnienia użytkownika systemu,
- ograniczone uprawnienia na kontrolerze,
- łatanie węzłów,
- segmentacja sieci i ograniczony dostęp do internetu,
- skrypty instalacyjne bez sekretów.

> Mój potok: runnery hostowane przez GitHub spełniają część rekomendacji z założenia (nowa VM na każdy job).

**CICD-SEC-6. Jakie błędy higieny poświadczeń wymienia dokument?** (dok. s. 24–25)

1. Sekret w kodzie wypchniętym do SCM. Zostaje w historii nawet po usunięciu z gałęzi.
2. Poświadczenia w buildzie dostępne dla kodu bez przeglądu.
3. Poświadczenia w warstwach obrazu kontenera.
4. Poświadczenia wypisane w logach.
5. Brak rotacji, zwłaszcza kluczy wdrożeniowych („jeśli nie jest zepsute, nie naprawiaj”).

> Mój potok: GT-02 to błąd 1. Incydent tj-actions to błąd 4.

**CICD-SEC-6. Jakie rekomendacje podaje dokument?** (dok. s. 25–26)

- mapowanie poświadczeń,
- najmniejsze uprawnienia,
- brak współdzielenia między kontekstami,
- poświadczenia tymczasowe zamiast statycznych,
- ograniczenie użycia do warunków (adres, tożsamość),
- wykrywanie sekretów w IDE, przy pushu i okresowo w historii,
- sekrety przypisane do kroku,
- blokowanie wypisywania do logów,
- usuwanie sekretów z artefaktów.

> Mój potok: OIDC z warunkiem na repozytorium i środowisko realizuje wprost rekomendację o poświadczeniach tymczasowych i warunkach użycia.

**CICD-SEC-7. Czy korzystanie z SaaS (GitHub Actions) usuwa to ryzyko?** (dok. s. 28)

Nie. SaaS usuwa część ryzyka: utwardzanie własnych hostów i ruch boczny w sieci. Organizacja nadal odpowiada za konfigurację samej usługi, a każda usługa ma własne ustawienia bezpieczeństwa. Rekomendacje:

- inwentarz systemów i wersji z właścicielem,
- dostęp sieciowy według zasady najmniejszego dostępu,
- okresowy przegląd konfiguracji,
- najmniejsze uprawnienia do węzłów.

Osobna uwaga o debugowaniu: dostęp do węzła w trybie debug ujawnia sekrety w pamięci.

**CICD-SEC-8. Dlaczego akcje GitHub to „usługi firm trzecich”?** (dok. s. 30–31)

Dokument podaje akcje GitHub Actions jako przykład integracji, którą dodaje się 1–2 liniami konfiguracji. Kod akcji wykonuje się w buildzie z pełnym dostępem do zasobów etapu. W GitHubie firmę trzecią podłącza się na 5 sposobów: GitHub App, OAuth App, token, klucz SSH, webhook. Organizacja jest tak bezpieczna, jak firmy trzecie, które podłącza (dok. s. 31).

> Związek z pracą: dlatego GT-16 (akcja przez zmienny tag) przypisujemy do CICD-SEC-8, a nie CICD-SEC-3 (notatki, p. 5).

**CICD-SEC-8. Jakie rekomendacje podaje dokument?** (dok. s. 31–32)

Kontrole na każdym etapie cyklu życia integracji:

1. **Zatwierdzenie:** weryfikacja przed nadaniem dostępu, najmniejsze uprawnienia.
2. **Integracja:** widoczność sposobu podłączenia oraz uprawnień nadanych i używanych.
3. **Bieżące użycie:** firmy trzecie w buildzie w kontekście z ograniczonym dostępem do sekretów i kodu oraz z filtrami ruchu.
4. **Wycofanie:** okresowe usuwanie nieużywanych.

**CICD-SEC-9. Na czym polega brak walidacji integralności artefaktów?** (dok. s. 33)

Na wejście każdego kroku potoku trafiają zasoby wewnętrzne i zewnętrzne od wielu dostawców, więc punktów, w których da się podmienić zasób, jest wiele. Podmieniony zasób, który nie trafi na bramkę, przejdzie potokiem aż do produkcji jako „legalny”.

**CICD-SEC-9. Jakie środki podaje dokument?** (dok. s. 33–34)

1. **Podpis i weryfikacja zasobów od deweloperki do produkcji.** Zasób podpisuje się przy wytworzeniu i weryfikuje przed użyciem. Przykłady:
   - podpisy commitów,
   - narzędzia podpisu i weryfikacji (Sigstore; w wersji webowej także in-toto i SLSA),
   - wykrywanie dryfu konfiguracji (np. zasoby chmury spoza podpisanego IaC).
2. **Zasoby firm trzecich pobierane w potoku:** porównać hash z hashem opublikowanym przez dostawcę.

Przykład Codecov (dok. s. 34): atak wykrył klient, który porównał hash skryptu.

> Mój potok: atestacja pochodzenia, weryfikacja przed wdrożeniem, wdrożenie po digeście.

**CICD-SEC-10. Jakie logi są potrzebne?** (dok. s. 35–36)

Oba rodzaje:

- logi audytowe systemów: dostęp użytkowników, tworzenie kont, zmiany uprawnień,
- logi aplikacyjne: push, wykonanie buildu, wgranie artefaktu.

Zarówno dla dostępu ludzi, jak i programowego. Rekomendacje:

- inwentarz systemów,
- włączenie źródeł logów (domyślnie zwykle wyłączone),
- centralizacja w SIEM,
- alerty o anomaliach w systemach i w całym procesie dostarczania.

To ryzyko przekrojowe, bez listy odniesień, bo każdy incydent wymaga widoczności (dok. s. 36).

> Mój potok: CloudTrail i logi przebiegów jako artefakty. Bez SIEM, czyli ograniczenie lekkiego potoku.

---

## 4. Pytania na obronę

**„Dlaczego model zagrożeń potoku opiera się na Top 10 CI/CD, a nie na STRIDE?”**

Top 10 CI/CD jest katalogiem zagrożeń dla tej klasy systemów: SCM, CI, rejestry, integracje firm trzecich. Każde ryzyko ma rekomendacje i przykłady incydentów. STRIDE jest metodą ogólną, którą trzeba by dopiero zastosować do potoku. Guideline umieszcza Top 10 CI/CD w swojej mapie ram jako źródło „ryzyk specyficznych dla potoku” (`0-3 Frameworks`).

**„Top 10 CI/CD napisali pracownicy firmy sprzedającej produkt. Czy to nie podważa źródła?”**

To ograniczenie, które praca odnotowuje (5.3). Dokument przeszedł jednak do OWASP i miał 15 recenzentów spoza firmy (dok. s. 2). Jego ryzyka pokrywają się z rekomendacjami NIST SP 800-204D: 28 z 58 rekomendacji ma w nim pełny albo częściowy odpowiednik (notatki, p. 4). Nowsze incydenty, które nastąpiły po publikacji, też mieszczą się w tym modelu: tj-actions w 2025 i trivy-action w 2026, oba w CICD-SEC-8 i -6.

**„Dlaczego Guideline nie jest źródłem pozycji listy kontrolnej?”**

Bo nie formułuje wymagań: nie ma identyfikatorów, mocy ani kryteriów spełnienia, a treść zmienia się bez wydań. Służy do doboru etapów i narzędzi (C2). Wymagania z mocą daje SP 800-204D, a ryzyka i rekomendacje Top 10 CI/CD.

**„Ile ryzyk CICD-SEC sprawdza eksperyment?”**

Seria skuteczności sprawdza cztery: CICD-SEC-4, -5, -6 i -8, przez pozycje GT-17, GT-15, GT-02 i GT-16. Pozostałe dotyczą konfiguracji platformy i procesu (ochrona gałęzi, tożsamości, ustawienia, integralność artefaktów, logowanie). Te ocenia lista kontrolna (C5) z dowodem w konfiguracji, a nie podatność wprowadzana pull requestem.

**„Czy przypinanie akcji do SHA rozwiązuje problem akcji firm trzecich?”**

Usuwa wektor przestawienia tagu dla akcji wołanych bezpośrednio. Nie obejmuje akcji złożonych, które wewnątrz wołają inne akcje przez tag (`incydenty.md`, tj-actions). Nie chroni też przed złośliwym kodem w commicie, który się przypina. Dlatego dochodzą: najmniejsze uprawnienia joba (CICD-SEC-5), kontrola ruchu wychodzącego i lista zatwierdzonych akcji (CICD-SEC-8).

**„Skoro repozytorium jest publiczne, czy każdy może zatruć potok?”**

To scenariusz 3PE (dok. s. 15). Obrona:

- workflow uruchamiane na PR nie mają sekretów ani `id-token: write`,
- nie używamy `pull_request_target`,
- workflow od zewnętrznych współpracowników wymagają zatwierdzenia,
- wdrożenie działa tylko z chronionej gałęzi.

Atakujący może wykonać kod w efemerycznej VM bez poświadczeń, ale nie dotrze do AWS. W eksperymencie PR-y pochodzą tylko z gałęzi własnych (`experiment/README.md`).
