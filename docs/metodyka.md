# Metodyka badania

> **Status:** szkic (v0). Wersja v1 powstanie po akceptacji promotora (kamień milowy M1, zadanie E03-07). Każdą późniejszą zmianę założeń zapisujemy w dzienniku badawczym (`docs/log/`) z uzasadnieniem.

Dokument definiuje eksperyment, zanim powstanie kod. Implementacja ma zbierać dokładnie te dane, których potrzebuje rozdział 5. Kolejne sekcje uzupełniają zadania E03-01…E03-06.

## 1. Cele

### 1.1. Pojęcia operacyjne

Cele odwołują się do dwóch pojęć z tytułu pracy, które trzeba zdefiniować tak, żeby dało się je zmierzyć.

- **Lekki potok.** Potok, który:
  - korzysta wyłącznie z narzędzi bezpłatnych lub otwartoźródłowych i z runnerów udostępnianych przez GitHub, bez własnej infrastruktury bezpieczeństwa (np. serwera analizy kodu),
  - jest definiowany w całości w repozytorium (workflow, polityki, konfiguracja narzędzi),
  - może go utrzymać zespół 1–3 osób,
  - daje szybką informację zwrotną: mediana czasu wykonania potoku uruchamianego dla pull requesta nie przekracza 10 minut (hipoteza H2a w sekcji 2). Narzut względem potoku bazowego (w minutach i procentach) raportujemy opisowo. Sprawdzi to pomiar w eksperymencie (C4).

  Pierwotnie próg miał być względny (narzut w % względem potoku bazowego). Zmiana na próg bezwzględny: spodziewamy się, że potok bazowy małej aplikacji będzie krótki, więc nawet kilka minut skanowania da duży narzut procentowy, który niewiele mówi o uciążliwości dla zespołu. Dla zespołu liczy się czas oczekiwania na wynik (decyzja autora z 2026-10-09, E03-02).

  Koszt AWS nie wchodzi do definicji. Infrastrukturę aplikacji uruchamiają oba warianty potoku, a skanery działają na runnerach GitHuba, więc koszt AWS prawie nie różnicuje wariantów. Do definicji warto wrócić, jeśli projekt potoku (E07-01) wprowadzi płatne usługi bezpieczeństwa AWS (decyzja autora z 2026-10-06).
- **Zgodność z wytycznymi.** NIST SP 800-204D to wytyczne, a nie norma, a SSDF wprost zastrzega, że nie jest listą kontrolną [@NIST-SP800-218, dok. s. 1–3]. Dlatego „zgodność” rozumiemy operacyjnie jako **pokrycie stosowalnych pozycji listy kontrolnej**: każda pozycja ma ocenę (spełniona / częściowo / niespełniona / nie dotyczy) i wskazany dowód (log, artefakt, konfiguracja, atestacja).
  - Wynik podajemy osobno dla pozycji o mocy MUST i SHOULD, bez wag. Ważenie wymagałoby arbitralnego wyboru wartości wag.
  - Wartość oceny „częściowo” w wyniku liczbowym ustali E03-04 (metryki).
  - Skład listy kontrolnej (które dokumenty i tabele) określa cel C1.

  Decyzja autora z 2026-10-06.

### 1.2. Cel główny

Celem głównym pracy jest zaprojektowanie, wdrożenie i eksperymentalna ocena lekkiego potoku DevSecOps dla aplikacji webowej uruchamianej w chmurze AWS, zbudowanego na GitHub Actions i Dockerze z wykorzystaniem skanerów bezpieczeństwa, pod względem skuteczności wykrywania podatności, kosztu czasowego oraz pokrycia wytycznych OWASP i NIST SP 800-204D.

### 1.3. Problem badawczy

W jakim stopniu lekki potok DevSecOps, zbudowany z ogólnodostępnych narzędzi i zaprojektowany według wytycznych OWASP i NIST SP 800-204D, ogranicza liczbę podatności docierających do środowiska produkcyjnego i jakim kosztem?

Cel mówi, co praca robi, a problem badawczy, czego praca chce się dowiedzieć. Pytania badawcze (sekcja 2) rozkładają problem na części mierzalne. Rozdzielenie celu i problemu wymagają wymogi formalne uczelni (decyzja autora z 2026-10-06).

### 1.4. Cele szczegółowe

| ID | Cel szczegółowy | Rodzaj | Kryterium osiągnięcia (dowód) | Rozdz. | Zadania |
|---|---|---|---|---|---|
| C1 | Przeanalizować wytyczne NIST SP 800-204D, NIST SP 800-218 (SSDF) i OWASP i wyprowadzić z nich listę kontrolną wymagań wobec potoku CI/CD z oceną stosowalności dla małego zespołu. Skład listy: p. 1.5. | analityczny | Lista kontrolna, w której każda pozycja ma ID, źródło, moc (MUST/SHOULD), praktykę SSDF i ocenę stosowalności. Każda pozycja niestosowalna ma uzasadnienie. | 3, 5.1 | E02-02…E02-04, E07-01 |
| C2 | Zaprojektować architekturę potoku DevSecOps (etapy, narzędzia, bramki bezpieczeństwa i ich polityka) wyprowadzoną z listy kontrolnej. | projektowy | Macierz śledzenia „pozycja listy → etap → narzędzie → bramka”. Każda stosowalna pozycja jest pokryta albo ma uzasadnione pominięcie. Decyzje zapisane w ADR. | 4.3 | E07-01, E02-10 |
| C3 | Zaimplementować w publicznym repozytorium aplikację badawczą z katalogiem podatności referencyjnych, infrastrukturę AWS jako kod oraz dwa warianty potoku: bazowy (A) i DevSecOps (B). | implementacyjny | Oba warianty wdrażają aplikację do AWS. Wersje narzędzi, akcji i obrazów są przypięte. Instrukcja odtworzenia pozwala powtórzyć eksperyment. | 4 | E04–E08 |
| C4 | Ocenić eksperymentalnie skuteczność wykrywania podatności oraz koszt czasowy (czas wykonania potoku) i koszt obsługi fałszywych alarmów wariantu B względem wariantu A. | ewaluacyjny | Surowe dane z eksperymentu (`experiment/data/`) oraz wyniki: wykrywalność podatności z katalogu, etap wykrycia, liczba podatności, które dotarły do środowiska produkcyjnego, liczba fałszywych alarmów, czas potoku i narzut. Odpowiedź na RQ1 i RQ2 (E03-02). | 5 | E03-03…E03-06, E09, E13 |
| C5 | Ocenić, w jakim stopniu wariant B realizuje wytyczne z listy kontrolnej, oraz określić osiągnięty poziom SLSA Build. | ewaluacyjny | Tabela pokrycia: ocena każdej pozycji w skali z p. 1.1, odnośnik do dowodu, odsetek pokrycia pozycji stosowalnych osobno dla MUST i SHOULD. Osiągnięty poziom SLSA Build z dowodem (np. atestacja provenance), a dla poziomów nieosiągniętych przyczyna. Odpowiedź na RQ3. | 5 | E02-05, E07, E08, E13 |
| C6 | Sformułować rekomendacje wdrożenia lekkiego potoku DevSecOps dla małych zespołów wraz z ograniczeniami podejścia. | syntetyczny | Lista rekomendacji: minimalny zestaw kontroli i kolejność wdrażania. Każda rekomendacja wskazuje wynik z C4 lub C5, na którym się opiera. Ograniczenia opisane w 5.3. | 5.3, 6 | E13, E14 |

Rodzaje celów odpowiadają kolejnym częściom pracy: analiza (rozdz. 3) → projekt i implementacja (rozdz. 4) → ewaluacja (rozdz. 5) → wnioski (rozdz. 6).

### 1.5. Zakres i założenia

- Jedna aplikacja webowa (FastAPI) w kontenerze Docker, wdrażana do AWS. Poza zakresem są Kubernetes, IAST i architektura mikroserwisowa.
- Projekt jest jednoosobowy. Wymagania zakładające przegląd zmian przez drugą osobę lub podział ról (SP 800-204D, 3.2.2 i 5.1.2; SSDF PO.2) są oceniane jako ograniczenie, a nie pomijane bez komentarza.
- **Skład listy kontrolnej (C1)** (decyzja autora z 2026-10-06):

  | Dokument | Rola w pracy |
  |---|---|
  | NIST SP 800-204D, rekomendacje z rozdz. 5 (tabela A w `docs/notes/nist-800-204d.md`, 34 pozycje) | pozycje listy |
  | NIST SP 800-204D, środki bazowe dla open source z 3.2.1 (tabela B, 8 pozycji) | pozycje listy |
  | OWASP Top 10 CI/CD Security Risks | pozycje listy |
  | NIST SP 800-218 (SSDF) | kolumna mapowania przy każdej pozycji, bez osobnych pozycji (SP 800-204D sam jest zmapowany na SSDF, osobne pozycje liczyłyby te same wymagania dwa razy) |
  | OWASP DevSecOps Guideline | podstawa doboru etapów i narzędzi w projekcie potoku (C2) |
  | OWASP ASVS 5.0 i OWASP Top 10:2025 | podstawa katalogu podatności referencyjnych (E03-03), bo dotyczą aplikacji, nie potoku |

  Część OWASP jest wstępna do czasu lektury w E02-04. Zmianę składu po lekturze zapisujemy w dzienniku z uzasadnieniem.
- Mapowanie narzędzi na praktyki SSDF przyjmujemy według definicji SSDF: SAST → PW.7, SCA → PW.4.4, DAST → PW.8. Rozbieżność z dodatkiem A SP 800-204D opisujemy w 3.1 albo 5.3 (decyzja z E02-03).

## 2. Pytania badawcze i hipotezy

Pytania badawcze rozkładają problem z p. 1.3 na trzy części: skuteczność, koszt i zgodność. RQ1 i RQ2 obsługuje cel C4, a RQ3 cel C5.

### 2.1. Pytania badawcze

- **RQ1 (skuteczność).** Jaki odsetek podatności z katalogu referencyjnego wariant B zatrzymuje przed wdrożeniem na produkcję, na którym etapie potoku je wykrywa i ile podatności mimo to dociera do środowiska produkcyjnego w porównaniu z wariantem A?
- **RQ2 (koszt).** O ile wariant B wydłuża czas wykonania potoku względem wariantu A i jaką część zgłoszeń na bramkach blokujących stanowią fałszywe alarmy, które zespół musi ręcznie obsłużyć?
- **RQ3 (zgodność).** W jakim stopniu wariant B realizuje stosowalne pozycje listy kontrolnej z celu C1 (SP 800-204D i OWASP Top 10 CI/CD, z mapowaniem na SSDF) i jaki poziom SLSA Build osiąga?

Samo porównanie wykryć w wariantach A i B byłoby trywialne, bo wariant A nie ma skanerów i niczego nie wykrywa. Dlatego RQ1 mierzy przede wszystkim, ile podatności **dociera na produkcję**. W wariancie A trafiają tam z założenia prawie wszystkie podatności z katalogu, więc jego wynik jest punktem odniesienia. Informację niesie to, ile podatności przepuszcza wariant B.

### 2.2. Hipotezy

| ID | Hipoteza | Próg | Pytanie |
|---|---|---|---|
| H1 | Wariant B zatrzymuje przed wdrożeniem na produkcję co najmniej 80% podatności z katalogu referencyjnego. | M3(B) ≤ 20%, czyli zatrzymanych ≥ 80% | RQ1 |
| H2a | Mediana czasu wykonania potoku wariantu B uruchamianego dla pull requesta nie przekracza 10 minut. | mediana M4(B, PR) ≤ 10 min | RQ2 |
| H2b | Co najmniej połowa unikalnych zgłoszeń na bramkach blokujących wariantu B to prawdziwe problemy bezpieczeństwa (z katalogu albo spoza niego). | M6 ≥ 50% | RQ2 |
| H3a | Wariant B spełnia co najmniej 80% stosowalnych pozycji MUST i co najmniej 50% stosowalnych pozycji SHOULD listy kontrolnej. | M7(MUST) ≥ 80%, M7(SHOULD) ≥ 50% | RQ3 |
| H3b | Wariant B osiąga poziom SLSA Build co najmniej L2. | M8 ≥ L2 | RQ3 |

Doprecyzowania:

- **„Zatrzymana” (H1).** Podatność jest zatrzymana, jeśli bramka blokująca wariantu B uniemożliwiła wdrożenie na produkcję artefaktu, który ją zawiera, a wśród zgłoszeń, które wywołały blokadę, jest trafienie tej podatności. Samo zgłoszenie bez zablokowania się nie liczy. Blokada wywołana wyłącznie innymi zgłoszeniami (np. fałszywym alarmem) też się nie liczy (decyzja autora z 2026-10-13; klasy wyniku próby: `experiment/PROTOCOL.md`, p. 3.3). Rozróżnienie „wykryta” i „zablokowana” to zagrożenie trafności konstruktu omawiane w sekcji 4 (E03-06).
- **Zakres czasu (H2a).** Próg dotyczy workflow wyzwalanego przez pull request, czyli pętli informacji zwrotnej dla programisty. Pełny potok na gałęzi głównej (z wdrożeniem do AWS) raportujemy opisowo, bo jego czas zależy też od AWS, a nie tylko od skanerów. Próg 10 minut to heurystyka praktyki ciągłej integracji: etap commit powinien trwać najlepiej poniżej 5 minut i nie dłużej niż 10 [@Humble2010, s. TODO]. TODO: zweryfikować po lekturze (rozdz. 7 „The Commit Stage”; źródło ma w rejestrze `zweryfikowane: nie`). Sposób pomiaru: p. 3.2, M4.
- **Precyzja (H2b).** Liczymy zgłoszenia unikalne (ta sama reguła w tym samym miejscu kodu w kolejnych przebiegach to jedno zgłoszenie). Klasy zgłoszeń: trafienie z katalogu, prawdziwy problem spoza katalogu, fałszywy alarm. Reguły klasyfikacji ustali E03-04.
- **Pokrycie (H3a).** Do progu liczymy wyłącznie oceny „spełniona”, więc wynik jest dolną granicą i nie zależy od wartości oceny „częściowo”, którą ustali E03-04. Wynik z oceną „częściowo” podajemy obok, opisowo.
- **SLSA (H3b).** Próg L2 to propozycja wstępna. TODO: zweryfikować po lekturze specyfikacji SLSA (E02-05), które wymagania poziomów Build da się spełnić na runnerach hostowanych GitHuba, i wtedy potwierdzić albo zmienić próg. Zmianę zapisujemy w dzienniku.

Progi są decyzją autora z 2026-10-09 (E03-02). Literatura z rdzenia nie podaje gotowych wartości progowych dla tych miar, więc progi ustalono przed eksperymentem, żeby wynik nie wpływał na kryterium oceny. Sposób wnioskowania (np. przedział ufności dla proporcji przy H1, test dla czasów przy H2a) określi sekcja 4 (E03-06).

### 2.3. Metryki przypisane do pytań

Wzory, jednostki, źródła danych i sposób pomiaru są w sekcji 3 (E03-04).

| ID | Metryka | Źródło danych | RQ | Hipoteza |
|---|---|---|---|---|
| M1 | Wykrywalność (recall): odsetek podatności z katalogu zgłoszonych przez potok, ogółem i w każdej kategorii katalogu | raporty skanerów (SARIF/JSON) zestawione z katalogiem | RQ1 | opisowo |
| M2 | Etap wykrycia: PR, gałąź główna przed wdrożeniem, audyt po wdrożeniu | logi workflow GitHub Actions | RQ1 | opisowo |
| M3 | Odsetek podatności z katalogu, które dotarły na produkcję (w każdym wariancie) | status bramek w logach workflow, potwierdzenie niezależnym audytem środowiska po wdrożeniu (scenariusz E03-05) | RQ1 | H1 |
| M4 | Czas wykonania potoku: mediana i p90, osobno dla PR i gałęzi głównej, w każdym wariancie | API GitHub Actions (czasy przebiegów i jobów) | RQ2 | H2a |
| M5 | Narzut czasu wariantu B względem A, w minutach i w % | wyliczany z M4 | RQ2 | opisowo |
| M6 | Precyzja zgłoszeń na bramkach blokujących wariantu B oraz liczba fałszywych alarmów | raporty skanerów i ręczna klasyfikacja zgłoszeń | RQ2 | H2b |
| M7 | Pokrycie stosowalnych pozycji listy kontrolnej, osobno MUST i SHOULD | lista kontrolna z ocenami i dowodami (C1, C5) | RQ3 | H3a |
| M8 | Osiągnięty poziom SLSA Build | atestacja provenance, konfiguracja potoku | RQ3 | H3b |
| M9 | Liczba zablokowanych przebiegów, w tym zablokowanych wyłącznie przez fałszywe alarmy | logi workflow i klasyfikacja z M6 | RQ2 | opisowo |

Każde pytanie ma co najmniej jedną metrykę ze zdefiniowanym progiem: RQ1 → M3, RQ2 → M4 i M6, RQ3 → M7 i M8.

## 3. Metryki

Sekcja podaje dla każdej metryki z p. 2.3 wzór, jednostkę, źródło danych i sposób pomiaru. Implementacja potoku (E07–E09) ma zbierać dokładnie te dane, a skrypty w `experiment/scripts/` mają z nich liczyć wyniki. Surowe dane trafiają do `experiment/data/`.

### 3.1. Oznaczenia i zbiory danych

- **K:** katalog podatności referencyjnych (`experiment/ground-truth.yaml`), |K| = 20 w wersji v0.
  - **K_z ⊂ K:** pozycje w zasięgu narzędzi (`w_zasiegu_narzedzi: true`), |K_z| = 17.
  - **K_g:** pozycje grupy g. Grupy: kod, zależności, kontener, IaC, konfiguracja web, workflow.
- **v ∈ {A, B}:** wariant potoku.
- **Przebiegi eksperymentalne:** przebiegi wywołane serią pull requestów, które wprowadzają podatności z katalogu (scenariusz E03-05). Służą do M1–M3, M6 i M9.
- **Przebiegi pomiarowe R(v, w):** 20 przebiegów wariantu v dla wyzwalacza w ∈ {PR, main} na czystym commicie, czyli bez podatności z katalogu, więc bramki przechodzą. Służą do M4 i M5.
  - Wyzwalacz „main” oznacza push na gałąź bazową wariantu (`exp/variant-a` albo `exp/variant-b`), bo warianty mają osobne gałęzie bazowe w jednym repozytorium (`experiment/PROTOCOL.md`, sekcja 0). Przebiegi main wdrażają czystą wersję do AWS.
  - Przebieg zatrzymany przez bramkę kończy się wcześniej i zaniżałby czas, dlatego czasu nie mierzymy na przebiegach eksperymentalnych.
  - Liczba 20 zamiast 10 z definicji E03-05: przy 10 pomiarach p90 to w praktyce drugi największy pomiar (decyzja autora z 2026-10-12).
- **Z:** zbiór unikalnych zgłoszeń na bramkach blokujących wariantu B ze wszystkich przebiegów eksperymentalnych (reguły w p. 3.3).
- **Próba przebiegu:** liczymy wyłącznie pierwszą próbę (`run_attempt = 1`). Przebieg przerwany z przyczyn infrastrukturalnych (awaria runnera, limit API) powtarzamy jako nowy przebieg i zapisujemy w dzienniku badawczym.

### 3.2. Definicje metryk

| ID | Metryka | Wzór | Jednostka | Źródło danych i pomiar | RQ / H | Uzasadnienie |
|---|---|---|---|---|---|---|
| M1 | Wykrywalność (recall) | M1 = \|{k ∈ K : trafienie(k)}\| / \|K\|; obok M1_z (mianownik \|K_z\|) i M1_g (dla każdej grupy, mianownik \|K_g\|) | % | Raporty narzędzi wariantu B (SARIF/JSON, artefakty workflow) zestawione z katalogiem. Reguła trafienia: `experiment/README.md`. | RQ1, opisowo | [@Li2023; @Imtiaz2021] |
| M2 | Etap wykrycia | etap(k) = najwcześniejszy etap z trafieniem, w porządku PR < main przed wdrożeniem < audyt po wdrożeniu; wynik: liczba pozycji na każdym etapie | liczba pozycji | Zdarzenie wyzwalające przebieg (`pull_request` / `push` na main) i raport audytu po wdrożeniu (E03-05) | RQ1, opisowo | TODO: zweryfikować (kandydat: [@NIST-SP800-204D], integracja kontroli na etapach potoku) |
| M3 | Dotarło na produkcję | M3(v) = \|{k ∈ K : artefakt zawierający k wdrożono na produkcję w wariancie v}\| / \|K\| | % | Wynik jobów-bramek i jobu wdrożenia w logach workflow, potwierdzony audytem działającego środowiska (E03-05) | RQ1, H1: M3(B) ≤ 20% | konstrukcja własna (p. 2.2, „zatrzymana”) |
| M4 | Czas potoku | T_czek(r) = max_j completed_at(j) − min_j created_at(j); T_wyk(r) = max_j completed_at(j) − min_j started_at(j), gdzie j przebiega joby próby 1 przebiegu r. Dla każdego (v, w): mediana, p90, min i max | min | REST API GitHub Actions: lista jobów próby przebiegu (`/actions/runs/{run_id}/attempts/1/jobs`), surowy JSON w `experiment/data/` | RQ2, H2a: mediana T_czek(B, PR) ≤ 10 min | [@Forsgren2018; @Humble2010] |
| M5 | Narzut czasu | Δ = med T_wyk(B, w) − med T_wyk(A, w); Δ% = Δ / med T_wyk(A, w) · 100%; rozbicie: mediana czasu kroków każdego skanera, d(s) = completed_at(s) − started_at(s) | min, % | Wyliczane z M4; czasy kroków z tego samego wywołania API | RQ2, opisowo | [@Rangnau2020] |
| M6 | Precyzja bramek | M6 = (\|Z_kat\| + \|Z_poza\|) / \|Z\|; obok liczba fałszywych alarmów \|Z_FP\|, ogółem i dla każdego narzędzia | %, liczba | Raporty narzędzi pełniących rolę bramki blokującej i ręczna klasyfikacja (p. 3.3) | RQ2, H2b: M6 ≥ 50% | [@Johnson2013; @Imtiaz2021] |
| M7 | Pokrycie listy kontrolnej | M7(m) = S(m) / N(m) dla mocy m ∈ {MUST, SHOULD}, gdzie S to pozycje „spełniona”, a N pozycje stosowalne; opisowo M7'(m) = (S(m) + 0,5 · C(m)) / N(m), gdzie C to pozycje „częściowo” | % | Lista kontrolna z celu C1 z oceną i dowodem przy każdej pozycji | RQ3, H3a: M7(MUST) ≥ 80%, M7(SHOULD) ≥ 50% | definicja operacyjna z p. 1.1 [@NIST-SP800-204D; @NIST-SP800-218] |
| M8 | Poziom SLSA Build | najwyższy poziom L ∈ {L0, L1, L2, L3}, którego wszystkie wymagania ścieżki Build są spełnione | poziom | Atestacja provenance i konfiguracja potoku; sposób weryfikacji atestacji: TODO (E02-05, E08) | RQ3, H3b: M8 ≥ L2 | specyfikacja SLSA: TODO (brak notatki źródła, E02-05) |
| M9 | Zablokowane przebiegi | N_blok = liczba przebiegów eksperymentalnych B z co najmniej jedną nieudaną bramką blokującą; N_FP = liczba takich przebiegów, w których wszystkie zgłoszenia blokujące to fałszywe alarmy; obok N_FP / N_blok | liczba, % | Wynik jobów-bramek w logach workflow i klasyfikacja z M6 | RQ2, opisowo | [@Johnson2013] |

Uwagi do wzorów:

- **M1 na dwóch mianownikach** (decyzja autora z 2026-10-12). Główny wynik liczymy na \|K\| = 20, spójnie z M3 i H1. M1_z na 17 pozycjach w zasięgu pokazuje, ile narzędzia wykrywają z tego, co w ogóle mogą wykryć. Bez rozdzielenia wynik mieszałby ocenę narzędzi z oceną składu katalogu.
- **M4 i M5 na różnych miarach czasu** (decyzja autora z 2026-10-12):
  - H2a dotyczy czasu oczekiwania programisty na wynik (p. 1.1), więc liczymy ją na T_czek, razem z kolejką do runnera.
  - Narzut M5 liczymy na T_wyk, bez kolejki pierwszego joba, żeby losowy czas kolejki GitHuba nie zawyżał kosztu skanerów.
  - Różnicę T_czek − T_wyk (kolejka pierwszego joba) raportujemy osobno.
  - Ograniczenie: kolejka jobów uruchamianych później w grafie zależności zostaje w T_wyk. Rozbicie na kroki (M5) pokazuje czas samych skanerów.
- **Pola czasu w API.** Obiekt przebiegu nie ma pola zakończenia (`updated_at` to czas ostatniej zmiany), dlatego czas liczymy z jobów. Endpoint `/actions/runs/{run_id}/timing` (`run_duration_ms`) jest wygaszany, więc go nie używamy. Znaczenie pola `created_at` joba jako chwili wejścia do kolejki nie jest opisane w dokumentacji. TODO: zweryfikować na pierwszych przebiegach (E09), porównując z czasami w interfejsie GitHuba.
- **M7 z oceną „częściowo” = 0,5** (decyzja autora z 2026-10-12). Hipoteza H3a używa tylko M7, czyli dolnej granicy. M7' podajemy obok, opisowo.
- **Miejsce DAST** (decyzja autora z 2026-10-13, E03-05): w wariancie B OWASP ZAP w trybie baseline jest bramką na każdym pull requeście, na kontenerze uruchomionym w runnerze. Pozycje wykrywane tylko przez DAST mogą więc zostać zatrzymane przed wdrożeniem, a pułap H1 wynosi 85% (`experiment/README.md`). Szczegóły: `experiment/PROTOCOL.md`.
- **M2, etap „audyt po wdrożeniu”** liczy tylko zgłoszenia narzędzi uruchomionych na produkcji (ZAP baseline, Trivy). Sprawdzenia potwierdzające, które korzystają z wiedzy o katalogu, służą do M3, a nie do M2 (`experiment/PROTOCOL.md`, p. 4.3).
- **M3 dla pozycji workflow** (GT-15–17): pozycja dotarła na produkcję, jeśli została scalona do gałęzi bazowej wariantu, więc działa w potoku, który wdraża produkcję (decyzja autora z 2026-10-13). M3 obejmuje dzięki temu wszystkie 20 pozycji.

### 3.3. Klasyfikacja zgłoszeń (M6, M9)

1. **Zakres.** Klasyfikujemy zgłoszenia narzędzi, które w wariancie B pełnią rolę bramki blokującej, i tylko te zgłoszenia, które przekraczają próg blokady danej bramki (próg ustala E07). Zgłoszenia informacyjne poniżej progu nie wchodzą do M6.
2. **Unikalność.** Kluczem zgłoszenia jest trójka: narzędzie, identyfikator reguły, lokalizacja znormalizowana. Lokalizacja to plik i funkcja (kod), zasób (IaC), pakiet i wersja (zależności) albo obraz i pakiet systemowy (kontener). Numer linii pomijamy, bo przesuwa się między pull requestami. To samo miejsce zgłoszone przez dwa narzędzia to dwa zgłoszenia, bo H2b ocenia precyzję bramek, a nie podatności.
3. **Klasy.**
   - **Z_kat, trafienie z katalogu:** zgłoszenie spełnia regułę trafienia pozycji katalogu (`experiment/README.md`).
   - **Z_poza, prawdziwy problem spoza katalogu:** zgłoszenie wskazuje rzeczywistą słabość, której nie ma w katalogu i którą da się opisać numerem CWE albo CVE. Należą tu także nowe CVE w zależnościach wersji czystej, które pojawią się w trakcie eksperymentu.
   - **Z_FP, fałszywy alarm:** zgłoszenie nie wskazuje rzeczywistej słabości w danym kontekście, np. wzorzec uznany za niebezpieczny, choć dane są stałe albo zwalidowane.
4. **Zapis.** Każde zgłoszenie unikalne dostaje wiersz w pliku klasyfikacji w `experiment/data/` z kluczem, klasą, identyfikatorem pozycji katalogu (dla Z_kat) i jednozdaniowym uzasadnieniem. Format pliku ustali E09.
5. **Przypadki wątpliwe** klasyfikujemy jako Z_poza albo Z_FP z dopiskiem „wątpliwe”. W wynikach podajemy, jak zmienia się M6, gdy wszystkie wątpliwe uznać za fałszywe alarmy.
6. **Klasyfikator.** Klasyfikuje autor pracy. Brak drugiej osoby i miary zgodności klasyfikatorów to zagrożenie trafności opisywane w sekcji 4 (E03-06).

### 3.4. Uzasadnienie metryk w literaturze

Metryki skuteczności (M1, M6) liczymy względem zbioru podatności o znanej lokalizacji, tak jak w porównaniach narzędzi SAST na benchmarkach ze znaną prawdą [@Li2023]. Ocena względem katalogu, a nie względem wyniku innego narzędzia, wynika z dużych rozbieżności między raportami narzędzi SCA uruchomionych na tej samej aplikacji [@Imtiaz2021]. Fałszywe alarmy należą do głównych barier używania narzędzi analizy statycznej przez programistów [@Johnson2013], dlatego koszt potoku obejmuje precyzję bramek (M6) i blokady wywołane wyłącznie fałszywymi alarmami (M9), a nie tylko czas. Czas potoku jest składnikiem czasu realizacji zmiany, jednej z metryk dostarczania oprogramowania DORA [@Forsgren2018]. Narzut czasowy kontroli bezpieczeństwa w potoku CI/CD mierzono empirycznie przy integracji testów dynamicznych [@Rangnau2020]. Pokrycie listy kontrolnej (M7) wynika z operacyjnej definicji zgodności z p. 1.1.

TODO: zweryfikować po lekturze. Wszystkie źródła tego akapitu mają w rejestrze `zweryfikowane: nie` (E02-11), a tezy opierają się na abstraktach. Lekturę Li2023, Imtiaz2021 i Johnson2013 obejmuje zadanie E02-13.

## 4. Analiza danych i zagrożenia trafności

TODO: E03-06.

Materiał z E03-05 do uwzględnienia (`experiment/PROTOCOL.md`):

- **Trafność wewnętrzna:**
  - progi bramek zamrożone przed serią; zmiana po obejrzeniu wyników wymaga powtórzenia serii (P1),
  - skład katalogu ustalony przed decyzją o miejscu DAST,
  - blokada bez trafienia pozycji (klasa Z3) nie jest zatrzymaniem, więc fałszywe alarmy nie poprawiają H1 (p. 3.3),
  - workflow A = workflow B bez kroków bezpieczeństwa (K2).
- **Trafność zewnętrzna:** jedna pozycja na próbę, więc nie badamy interakcji między podatnościami; wersje zbiorcze są konstrukcją pomiarową, a nie realnym przebiegiem rozwoju.
- **Trafność konstruktu:**
  - „zatrzymana” = blokada z trafieniem pozycji (p. 2.2),
  - dla pozycji workflow „dotarła na produkcję” = scalona do gałęzi bazowej,
  - potwierdzenie audytem (R1) korzysta z wiedzy o katalogu i nie jest wykryciem w sensie M2.
- **Niezawodność:** zmienność infrastruktury GitHub (przeplatanie A/B, mediana i p90, kolejka osobno), aktualizacje obrazu runnera i baz podatności w trakcie serii (zapis wersji), czas operacji AWS (składnik wspólny obu wariantów).
