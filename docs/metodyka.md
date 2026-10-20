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

- **„Zatrzymana” (H1).** Podatność jest zatrzymana, jeśli bramka blokująca wariantu B uniemożliwiła wdrożenie na produkcję artefaktu, który ją zawiera, a wśród zgłoszeń, które wywołały blokadę, jest trafienie tej podatności. Samo zgłoszenie bez zablokowania się nie liczy. Blokada wywołana wyłącznie innymi zgłoszeniami (np. fałszywym alarmem) też się nie liczy (decyzja autora z 2026-10-13; klasy wyniku próby: `experiment/PROTOCOL.md`, p. 3.3). Rozróżnienie „wykryta” i „zablokowana” to zagrożenie trafności konstruktu (p. 4.5, TK1).
- **Zakres czasu (H2a).** Próg dotyczy workflow wyzwalanego przez pull request, czyli pętli informacji zwrotnej dla programisty. Pełny potok na gałęzi głównej (z wdrożeniem do AWS) raportujemy opisowo, bo jego czas zależy też od AWS, a nie tylko od skanerów. Próg 10 minut to heurystyka praktyki ciągłej integracji: etap commit powinien trwać najlepiej poniżej 5 minut i nie dłużej niż 10 [@Humble2010, s. TODO]. TODO: zweryfikować po lekturze (rozdz. 7 „The Commit Stage”; źródło ma w rejestrze `zweryfikowane: nie`). Sposób pomiaru: p. 3.2, M4.
- **Precyzja (H2b).** Liczymy zgłoszenia unikalne (ta sama reguła w tym samym miejscu kodu w kolejnych przebiegach to jedno zgłoszenie). Klasy zgłoszeń: trafienie z katalogu, prawdziwy problem spoza katalogu, fałszywy alarm. Reguły klasyfikacji ustali E03-04.
- **Pokrycie (H3a).** Do progu liczymy wyłącznie oceny „spełniona”, więc wynik jest dolną granicą i nie zależy od wartości oceny „częściowo”, którą ustali E03-04. Wynik z oceną „częściowo” podajemy obok, opisowo.
- **SLSA (H3b).** Próg L2 to propozycja wstępna. TODO: zweryfikować po lekturze specyfikacji SLSA (E02-05), które wymagania poziomów Build da się spełnić na runnerach hostowanych GitHuba, i wtedy potwierdzić albo zmienić próg. Zmianę zapisujemy w dzienniku.

Progi są decyzją autora z 2026-10-09 (E03-02). Literatura z rdzenia nie podaje gotowych wartości progowych dla tych miar, więc progi ustalono przed eksperymentem, żeby wynik nie wpływał na kryterium oceny. Reguły rozstrzygania hipotez i sposób wnioskowania są w p. 4.3.

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
6. **Klasyfikator.** Klasyfikuje autor pracy. Brak drugiej osoby i miary zgodności klasyfikatorów to zagrożenie trafności; mitygacja w p. 4.5 (TN4).

### 3.4. Uzasadnienie metryk w literaturze

Metryki skuteczności (M1, M6) liczymy względem zbioru podatności o znanej lokalizacji, tak jak w porównaniach narzędzi SAST na benchmarkach ze znaną prawdą [@Li2023]. Ocena względem katalogu, a nie względem wyniku innego narzędzia, wynika z dużych rozbieżności między raportami narzędzi SCA uruchomionych na tej samej aplikacji [@Imtiaz2021]. Fałszywe alarmy należą do głównych barier używania narzędzi analizy statycznej przez programistów [@Johnson2013], dlatego koszt potoku obejmuje precyzję bramek (M6) i blokady wywołane wyłącznie fałszywymi alarmami (M9), a nie tylko czas. Czas potoku jest składnikiem czasu realizacji zmiany, jednej z metryk dostarczania oprogramowania DORA [@Forsgren2018]. Narzut czasowy kontroli bezpieczeństwa w potoku CI/CD mierzono empirycznie przy integracji testów dynamicznych [@Rangnau2020]. Pokrycie listy kontrolnej (M7) wynika z operacyjnej definicji zgodności z p. 1.1.

TODO: zweryfikować po lekturze. Wszystkie źródła tego akapitu mają w rejestrze `zweryfikowane: nie` (E02-11), a tezy opierają się na abstraktach. Lekturę Li2023, Imtiaz2021 i Johnson2013 obejmuje zadanie E02-13.

## 4. Analiza danych i zagrożenia trafności

Sekcja ustala, jak z surowych danych eksperymentu (`experiment/data/`) wyprowadzamy wyniki i rozstrzygnięcia hipotez (4.1–4.4) oraz co może te wnioski osłabić (4.5). Reguły zapisujemy przed eksperymentem, żeby wynik nie wpływał na sposób jego oceny. Decyzje autora z 2026-10-13 (E03-06).

### 4.1. Zasady ogólne

1. **Dwa rodzaje danych.**
   - **Dane deterministyczne:** wyniki prób na katalogu (M1–M3), zbiór zgłoszeń bramek (M6, M9), lista kontrolna (M7) i wymagania SLSA (M8). Katalog i lista kontrolna nie są losowymi próbami z większej populacji, tylko całym badanym zbiorem. Skaner uruchomiony na tym samym kodzie z tą samą bazą podatności daje ten sam wynik. Rozstrzygamy więc regułą na wartości punktowej, bez wnioskowania statystycznego. Ograniczenia uogólnienia opisujemy jako zagrożenia trafności zewnętrznej (4.5).
   - **Dane losowe:** czasy przebiegów (M4, M5). Czas zależy od kolejki, obciążenia runnerów i sieci, więc 20 przebiegów to próba z procesu losowego. Tu stosujemy przedziały ufności i testy.
2. **Metody nieparametryczne.** Przy 20 pomiarach nie zakładamy rozkładu normalnego czasów. Rozkład czasów potoku bywa prawostronnie skośny przez pojedyncze przebiegi z długą kolejką.
3. **Poziom istotności i przedziały.** α = 0,05, przedziały ufności 95%.
4. **Odtwarzalność analizy.** Wszystkie wyniki liczą skrypty w `experiment/scripts/` wprost z surowych danych, bez ręcznych kroków pośrednich (wyjątek: klasyfikacja zgłoszeń, p. 3.3, zapisana w pliku). Wersje bibliotek analizy przypinamy jak wersje narzędzi potoku. Język i biblioteki: TODO (E09).
5. **Stany rozstrzygnięcia.** Hipoteza jest **potwierdzona**, **odrzucona** albo, tam gdzie reguła to przewiduje (H2a, H2b), **nierozstrzygnięta**. Stan „nierozstrzygnięta” raportujemy z wartością punktową i przyczyną.

### 4.2. Plan analizy metryk

| Metryka | Statystyka opisowa | Prezentacja | Wnioskowanie |
|---|---|---|---|
| M1 | odsetek na \|K\| = 20, obok M1_z (17) i M1_g dla każdej grupy | tabela pozycja × wariant × klasa wyniku (Z1–Z4) z narzędziem, które trafiło; wykres słupkowy M1_g | brak (dane deterministyczne) |
| M2 | liczba pozycji na każdym etapie | tabela etap × grupa | brak |
| M3 | odsetek pozycji, które dotarły na produkcję, w A i w B; zgodność z audytem (PROTOCOL.md, p. 4.5) | tabela jak przy M1, kolumna wyniku audytu | reguła H1 (4.3) |
| M4 | mediana, p90, min, max; T_czek i T_wyk; kolejka pierwszego joba (T_czek − T_wyk) osobno | wykres pudełkowy dla każdej pary (wariant, wyzwalacz); wykres przebiegów w kolejności wykonania (pokazuje dryf, np. po zmianie obrazu runnera) | 95% CI mediany; reguła H2a (4.3) |
| M5 | różnica median Δ i Δ%; mediana czasu kroków każdego skanera | wykres skumulowany kroków wariantu B | 4.4 |
| M6 | odsetek na zbiorze Z, \|Z_FP\| ogółem i dla każdego narzędzia; zawsze z \|Z\| | tabela narzędzie × klasa zgłoszenia | reguła H2b (4.3) |
| M7 | M7(MUST), M7(SHOULD), obok M7' | tabela pokrycia z dowodem przy każdej pozycji | reguła H3a (4.3) |
| M8 | osiągnięty poziom i niespełnione wymagania wyższego poziomu | tabela wymagań SLSA Build | reguła H3b (4.3) |
| M9 | N_blok, N_FP, N_FP / N_blok | tabela | brak |

Przy małych liczbach (np. \|Z\| < 10) podajemy odsetek razem z licznikiem i mianownikiem, np. „7/9 (78%)”, bo sam odsetek sugeruje większą dokładność, niż mają dane.

### 4.3. Reguły rozstrzygania hipotez

| Hipoteza | Reguła | Stany |
|---|---|---|
| **H1** | potwierdzona, gdy wariant B zatrzymał co najmniej 16 z 20 pozycji (klasa Z1, PROTOCOL.md p. 3.3), czyli M3(B) ≤ 20%. Rozstrzyga wynik potoku z regułami własnymi. Obok podajemy opisowo wynik bez reguł własnych | potwierdzona / odrzucona |
| **H2a** | 95% przedział ufności mediany T_czek(B, PR) z 20 przebiegów, bez założeń o rozkładzie: (x₍₆₎, x₍₁₅₎), pokrycie 95,9%. Potwierdzona, gdy górna granica ≤ 10 min, czyli co najmniej 15 z 20 przebiegów trwa ≤ 10 min. Odrzucona, gdy dolna granica > 10 min, czyli co najmniej 15 z 20 przebiegów trwa > 10 min. | potwierdzona / odrzucona / nierozstrzygnięta |
| **H2b** | M6 z klasyfikacji podstawowej i M6 w wariancie pesymistycznym (wszystkie zgłoszenia „wątpliwe” jako Z_FP, p. 3.3 pkt 5). Potwierdzona, gdy oba ≥ 50%. Odrzucona, gdy M6 podstawowe < 50%. Nierozstrzygnięta (wrażliwa na klasyfikację), gdy podstawowe ≥ 50%, a pesymistyczne < 50%. | potwierdzona / odrzucona / nierozstrzygnięta |
| **H3a** | potwierdzona, gdy M7(MUST) ≥ 80% i M7(SHOULD) ≥ 50% (tylko oceny „spełniona”) | potwierdzona / odrzucona |
| **H3b** | potwierdzona, gdy M8 ≥ L2 | potwierdzona / odrzucona |

Uzasadnienia:

- **H1 bez przedziału ufności** (decyzja autora z 2026-10-13). Katalog to cały badany zbiór, a nie losowa próba podatności (4.1), więc wynik jest dokładny dla tego katalogu. Rozstrzyganie dolną granicą przedziału Clopper-Pearsona byłoby też niewykonalne. Przy n = 20 dolna granica dwustronnego 95% CI wynosi 62,1% dla 17/20 i 83,2% dla 20/20, więc próg 80% wymagałby wyniku 20/20, a pułap to 17/20 (3 pozycje poza zasięgiem narzędzi). H1 przegrałaby wtedy z samej konstrukcji eksperymentu, tak samo w teście dwumianowym. Granice wyliczone przez agenta 2026-10-13; TODO: zweryfikować skryptem analizy (E09).
- **H1 ma mały zapas.** Przy pułapie 17/20 i progu 16/20 jedna niewykryta pozycja w zasięgu narzędzi nie zmienia wyniku, a dwie go odwracają. Tabela pozycji (4.2, M1) pokazuje, które pozycje rozstrzygnęły wynik.
- **H1 z regułami własnymi i bez nich** (decyzja autora z 2026-10-20, E02-10). Rejestr Semgrep i Bandit nie mają reguł dla GT-06 (log injection) i GT-14 (tryb debug w FastAPI) (`docs/narzedzia.md`, p. 4). Wariant B ma więc reguły własne Semgrep, które blokują tak samo jak reguły z rejestru. Reguły pisane są pod klasę CWE, a nie pod postać łatki, i zamrażane razem z katalogiem v1. Rozstrzyga wynik z regułami własnymi. Wynik bez nich liczymy z tych samych logów: pozycja jest wtedy zatrzymana tylko wtedy, gdy wśród zgłoszeń wywołujących blokadę jest trafienie reguły innej niż własna. Bez reguł własnych pułap wynosi 16/20 według listy detektorów, a realnie 15/20, bo ZAP baseline nie odróżnia GT-14 od zwykłego błędu 500. Wynik bez reguł własnych pokazuje, ile daje sam rejestr narzędzi. Uzasadnienie (odpowiedzi autora z 2026-10-20):
  - **Zarzut doboru reguł pod katalog (TW1).** Reguła opisuje klasę słabości (CWE-117, tryb debug na produkcji), a nie konkretną łatkę, i jest testowana także na kodzie spoza katalogu. Rejestr nie pokrywa każdego frameworka, więc zespoły dopisują reguły dla własnego stosu (tu FastAPI). TODO: zweryfikować, źródło dla twierdzenia o praktyce.
  - **Czemu nie CodeQL.** Regułę własną dopisujemy w Semgrepie, który już jest w potoku, więc nie dochodzi kolejne narzędzie SAST obok Semgrepa i Bandita. CodeQL buduje bazę kodu, co może wydłużyć czas PR (H2a). TODO: zweryfikować pomiarem albo źródłem.
  - **Rola reguł własnych.** Są częścią proponowanego wzorca potoku: małemu zespołowi zalecamy dopisanie kilku reguł dla własnego frameworka. Opis w podrozdziale 4.3 pracy, razem z kosztem.
- **Koszt reguł własnych (RQ2)** (decyzja autora z 2026-10-20). Czas pisania i testowania reguł własnych zapisujemy w dzienniku badawczym i podajemy opisowo obok kosztu czasowego potoku. Nie wchodzi do H2a.
- **Porównanie z CodeQL** (decyzja autora z 2026-10-20). Poza wariantem B uruchamiamy CodeQL na pozycjach katalogu w kodzie aplikacji jako dodatkową serię porównawczą. CodeQL nie jest bramką i nie wpływa na H1 ani na H2a. Wynik porównujemy z wykryciami Semgrepa (z regułami własnymi i bez nich) w 5.3. TODO (E03-05/E07):
  - które pozycje obejmuje seria (np. grupa `kod` oraz GT-12 i GT-14),
  - zestaw zapytań (domyślny czy `security-extended`),
  - miejsce uruchomienia (osobny workflow na tych samych gałęziach prób),
  - czy wynik wchodzi do M1.
- **H2a z przedziałem** (decyzja autora z 2026-10-13). Hipoteza dotyczy typowego czasu procesu, a 20 przebiegów to próba. Przy medianie bliskiej 10 min sama wartość punktowa nie wystarcza do rozstrzygnięcia, więc reguła ma stan „nierozstrzygnięta”. Granice przedziału to statystyki pozycyjne wynikające z rozkładu dwumianowego Bin(20; 0,5). TODO: źródło metody (przedział ufności mediany bez założeń o rozkładzie).
- **H2b z analizą wrażliwości** (decyzja autora z 2026-10-13). Zbiór Z jest deterministyczny, ale jego klasyfikacja zależy od oceny jednej osoby. Wariant pesymistyczny zawsze daje M6 nie większe od podstawowego, dlatego reguła ma trzy, a nie cztery przypadki.
- **H3a i H3b** są deterministyczne. Zagrożenie leży w ocenie pozycji przez autora (4.5, trafność konstruktu), a nie w zmienności danych.

### 4.4. Porównanie czasów wariantów (M5)

M5 nie ma hipotezy, ale wielkość narzutu jest głównym wynikiem RQ2 obok H2a. Analizę wykonujemy osobno dla wyzwalaczy PR i main, na T_wyk (p. 3.2) (decyzja autora z 2026-10-13):

1. **Test Manna-Whitneya**, dwustronny, α = 0,05: czy rozkłady T_wyk(A, w) i T_wyk(B, w) się różnią. Przebiegi traktujemy jako niezależne. Przeplatanie A/B (PROTOCOL.md, p. 2.3) służy wyrównaniu warunków, a nie parowaniu.
2. **Estymator Hodgesa-Lehmanna** przesunięcia (mediana wszystkich różnic b − a) z 95% CI: „o ile minut wariant B jest wolniejszy”. To główna liczba wyniku. Sam test przy spodziewanej wyraźnej różnicy niesie niewiele informacji.
3. **Miara efektu Vargha-Delaney A12**: prawdopodobieństwo, że losowy przebieg B trwa dłużej niż losowy przebieg A. Wartość 0,5 oznacza brak różnicy. Progi interpretacji: TODO, według źródła.
4. Obok: różnica median Δ i Δ% (p. 3.2) oraz rozbicie na kroki skanerów.

Dwa porównania (PR, main) nie testują hipotezy, więc nie stosujemy korekty na wielokrotne porównania.

TODO: źródła metod. Kandydaci do sprawdzenia i dopisania do rejestru: przewodnik po testach statystycznych w inżynierii oprogramowania (Arcuri, Briand) i oryginalna praca o A12 (Vargha, Delaney). Metadanych nie wpisujemy z pamięci (`Zrodla/_Zrodla.md`).

### 4.5. Zagrożenia trafności

Zagrożenia grupujemy w cztery rodzaje: trafność wewnętrzną (czy wynik wynika z wariantu potoku, a nie z innych czynników), zewnętrzną (na ile wynik się uogólnia), konstruktu (czy metryki mierzą to, co deklarujemy) oraz niezawodność i trafność wniosków (czy pomiar jest powtarzalny, a wnioskowanie poprawne). TODO: źródło klasyfikacji zagrożeń trafności (kandydat: podręcznik eksperymentów w inżynierii oprogramowania, Wohlin i in.; do sprawdzenia i dopisania do rejestru).

Kolumna „Ryzyko szczątkowe” mówi, co mimo mitygacji opisujemy w rozdz. 5.3.

#### Trafność wewnętrzna

| # | Zagrożenie | Mitygacja | Ryzyko szczątkowe |
|---|---|---|---|
| TW1 | **Podatności dobrane pod narzędzia.** Katalog i potok projektuje ta sama osoba, więc może (świadomie albo nie) wybrać podatności, które skanery łatwo wykrywają. | Skład katalogu wynika z pokrycia OWASP Top 10:2025 i grup artefaktów, a nie z reguł narzędzi (E03-03); 3 z 20 pozycji celowo poza zasięgiem narzędzi; oczekiwany detektor i pewność detekcji zapisane przed eksperymentem (`ground-truth.yaml`); skład ustalony przed decyzją o miejscu DAST; katalog zamrożony w v1 (K6); zamiana na pozycję rezerwową tylko przy niewykonalności, z wpisem w dzienniku. Reguły własne Semgrep dla GT-06 i GT-14 (oznaczone `regula_wlasna` w `ground-truth.yaml`) są pisane pod klasę CWE, zamrażane razem z katalogiem v1 przed akceptacją promotora i testowane także na kodzie spoza katalogu. Wynik H1 podajemy z nimi i bez nich (4.3). | Postać łatki (sposób zapisania podatności w kodzie) może ułatwiać albo utrudniać wykrycie. Opisujemy ją przy każdej pozycji. Reguła własna powstaje ze znajomością katalogu, więc pisanie jej pod klasę CWE ogranicza to ryzyko, ale go nie usuwa. |
| TW2 | **Progi bramek dostrojone do wyniku.** | Progi i konfiguracja bramek zamrożone przed serią (P1, K5); zmiana po obejrzeniu wyników wymaga powtórzenia serii i wpisu w dzienniku. | brak |
| TW3 | **Fałszywe alarmy poprawiają H1.** Blokada wywołana zgłoszeniem niezwiązanym z pozycją wyglądałaby jak zatrzymanie. | Klasa Z3 nie liczy się jako zatrzymanie (PROTOCOL.md, p. 3.3); próby Z3 raportowane osobno z przyczyną. | brak |
| TW4 | **Warianty różnią się czymś więcej niż kontrolami bezpieczeństwa.** | Workflow A powstaje z workflow B przez usunięcie kroków bezpieczeństwa, kontrola diffem w pilotażu (K2); zmienne K1–K12 (PROTOCOL.md, sekcja 5). | brak |
| TW5 | **Warunki zmieniają się między próbami** (nowe CVE w bazach, aktualizacja obrazu runnera). | Próby parami dla każdej pozycji, jedna seria w krótkim oknie (K10, K11); zapis wersji baz i obrazu przy każdym przebiegu; nowe CVE jako zgłoszenia spoza katalogu (Z_poza). | Nowe CVE może wywołać blokadę Z3 w części prób. Raportujemy liczbę takich prób. |
| TW6 | **Wiedza o katalogu wpływa na ocenę trafień.** Eksperymentator zna prawdę, więc może „dopasować” zgłoszenie do pozycji. | Reguła trafienia zapisana przed eksperymentem (`experiment/README.md`); audyt rozdzielony na R1 (potwierdzenie, z wiedzą o katalogu) i R2 (wykrycie, bez niej), do M2 liczy się tylko R2. | Przypadki graniczne reguły trafienia opisujemy przy pozycji. |

#### Trafność zewnętrzna

| # | Zagrożenie | Mitygacja | Ryzyko szczątkowe |
|---|---|---|---|
| TZ1 | **Jedna mała aplikacja i jeden stos** (FastAPI, Docker, AWS, GitHub Actions). | Opis kontekstu (rozdz. 4); rekomendacje (C6) formułowane warunkowo, z zakresem stosowalności. | Wyniki nie przenoszą się wprost na inne języki, frameworki i platformy CI. |
| TZ2 | **Katalog celowy, nie losowy, 20 pozycji.** | Wynik podajemy jako dokładny dla katalogu, bez wnioskowania o populacji podatności (4.1); M1_g dla każdej grupy pozwala czytelnikowi ocenić przenośność na własny profil ryzyka. | Odsetek wykrytych zależy od składu katalogu. |
| TZ3 | **Jedna podatność na próbę.** | Świadoma decyzja (PROTOCOL.md, sekcja 0): blokadę da się przypisać jednej pozycji. | Nie badamy interakcji między podatnościami; wersje zbiorcze są konstrukcją pomiarową, a nie realnym przebiegiem rozwoju. |
| TZ4 | **Projekt jednoosobowy.** | Wymagania przeglądu przez drugą osobę ocenione jako ograniczenie (p. 1.5). | Nie badamy, jak zespół obsługuje alarmy w codziennej pracy. |
| TZ5 | **Stan narzędzi i baz z dnia eksperymentu.** | Przypięte wersje (K4); zapis wersji baz podatności. | Wynik opisuje stan narzędzi na datę serii. |
| TZ6 | **Runnery hostowane GitHuba.** | Etykieta i typ maszyny stałe (K3). | Czasy na innych runnerach (np. własnych) mogą się różnić. |

#### Trafność konstruktu

| # | Zagrożenie | Mitygacja | Ryzyko szczątkowe |
|---|---|---|---|
| TK1 | **„Wykryta” to nie „zablokowana”.** | Dwie osobne miary: M1 (wykrycie) i M3/H1 (zatrzymanie); klasy Z1–Z4 (PROTOCOL.md, p. 3.3); definicja „zatrzymanej” w p. 2.2. | brak |
| TK2 | **„Dotarła na produkcję” dla pozycji workflow** (GT-15–17) znaczy co innego niż dla pozycji aplikacji. | Definicja: scalenie do gałęzi bazowej, która wdraża produkcję (p. 3.2, uwagi). | Opisujemy różnicę znaczeń w 5.3. |
| TK3 | **Czas potoku to tylko część kosztu.** | Osobne miary kosztu obsługi alarmów: M6 i M9. | Nie mierzymy czasu pracy człowieka nad alarmami. |
| TK4 | **T_czek zależy od znaczenia pola `created_at` joba.** | Weryfikacja na pierwszych przebiegach przez porównanie z interfejsem GitHuba (p. 3.2, uwagi; E09). | Do czasu weryfikacji: TODO. |
| TK5 | **Próg 10 min to heurystyka praktyki, nie norma.** | Źródło progu [@Humble2010] (TODO: zweryfikować po lekturze); obok progu raportujemy cały rozkład czasów. | Inny próg zmieniłby rozstrzygnięcie H2a; czytelnik ma rozkład, żeby to ocenić. |
| TK6 | **„Zgodność” to ocena autora, a nie certyfikacja.** | Operacyjna definicja zgodności (p. 1.1); dowód przy każdej pozycji listy kontrolnej; H3a liczona tylko na ocenach „spełniona” (dolna granica). | Ocena stosowalności i spełnienia zależy od interpretacji wytycznych przez autora. |
| TK7 | **Reguła trafienia może uznać przypadkowe zgłoszenie za trafienie** (np. inna reguła w tym samym pliku). | Reguła trafienia zapisana przed eksperymentem (`experiment/README.md`); w tabeli wyników podajemy regułę narzędzia przy każdym trafieniu. | Przypadki graniczne opisujemy przy pozycji. |

#### Niezawodność i trafność wniosków

| # | Zagrożenie | Mitygacja | Ryzyko szczątkowe |
|---|---|---|---|
| TN1 | **Zmienność infrastruktury GitHub** (kolejka, obciążenie runnerów). | Jeden przebieg naraz, przeplatanie A/B (PROTOCOL.md, p. 2.3); mediana i p90 zamiast średniej; 95% CI mediany; kolejka pierwszego joba raportowana osobno. | Systematyczne zmiany obciążenia w skali dni nie są kontrolowane. |
| TN2 | **Aktualizacja obrazu runnera w trakcie serii.** | Zapis wersji obrazu przy każdym przebiegu. Jeśli obraz zmieni się w trakcie serii czasowej, wyniki M4 i M5 podajemy łącznie oraz osobno przed i po zmianie. | Przy małej liczbie przebiegów po jednej stronie zmiany porównanie jest tylko orientacyjne. |
| TN3 | **Mała liczba pomiarów** (20 na parę wariant–wyzwalacz). | Metody nieparametryczne i przedziały (4.1, 4.4); stan „nierozstrzygnięta” w H2a. | Szerokie przedziały przy dużej zmienności czasów. |
| TN4 | **Jeden klasyfikator zgłoszeń** (M6, M9; p. 3.3 pkt 6). | Uzasadnienie każdej klasyfikacji w publicznym repozytorium (p. 3.3 pkt 4). Ponowna, ślepa klasyfikacja wszystkich zgłoszeń przez autora po co najmniej 2 tygodniach, bez wglądu w pierwszą; zgodność wewnątrz klasyfikatora mierzona współczynnikiem kappa Cohena. Rozbieżności rozstrzygamy ponowną analizą z zapisem uzasadnienia; do wyników wchodzi klasyfikacja po rozstrzygnięciu. Decyzja autora z 2026-10-13. | Brak drugiej osoby: zgodność wewnątrz jednego klasyfikatora nie wyklucza jego systematycznego błędu. TODO: źródło dla kappa Cohena i jej interpretacji. |
| TN5 | **Niepowtarzalność wyników skanerów.** Reguła H1 zakłada, że próba daje ten sam wynik przy powtórzeniu (4.1). Skaner dynamiczny (ZAP) może dawać różne zgłoszenia zależnie od przebiegu przeszukiwania aplikacji i limitu czasu. | W pilotażu (P5) powtarzamy próbę wariantu B dla wybranych pozycji, zwłaszcza GT-12–14 wykrywanych przez ZAP, i porównujemy zgłoszenia. | Jeśli wynik okaże się niepowtarzalny, opisujemy to w 5.3 i rozważamy powtórzenia prób dla pozycji DAST (zmiana protokołu z wpisem w dzienniku). |
| TN6 | **Mały zapas H1** (pułap 17/20, próg 16/20). | Tabela wyników pozycja po pozycji (4.2), z której widać, które pozycje rozstrzygnęły wynik. | Analiza reguł (E02-10, `docs/narzedzia.md`, p. 4): GT-12 wykrywa Semgrep na etapie PR. GT-13 wykrywa ZAP, jeśli pająk dotrze do strony HTML. GT-06 i GT-14 wymagają reguł własnych (4.3). Bez nich pułap wynosi realnie 15/20, poniżej progu. Wyniki analizy potwierdzamy w pilotażu (P5). |
| TN7 | **Odtwarzalność.** | Przypięte wersje (K4), surowe dane w repozytorium, analiza skryptami z danych surowych (4.1 pkt 4), instrukcja odtworzenia (C3). | Runnery hostowane i bazy podatności zmieniają się w czasie, więc dokładne powtórzenie liczb nie jest możliwe; możliwe jest powtórzenie procedury. |
