# Protokół eksperymentu

Wersja: szkic v0 (E03-05, w toku). Zamrożenie jako v1 razem z metodyką po akceptacji promotora (E03-07).

Protokół opisuje, jak porównujemy wariant A (CI/CD bez kontroli bezpieczeństwa) z wariantem B (potok DevSecOps). Pytania badawcze, hipotezy i metryki są w [`docs/metodyka.md`](../docs/metodyka.md), a katalog podatności referencyjnych w [`ground-truth.yaml`](ground-truth.yaml) i [`README.md`](README.md).

## 0. Zasady scenariusza

Decyzje autora z 2026-10-13 (uzasadnienia i odrzucone opcje: [`docs/log/2026-10-13.md`](../docs/log/2026-10-13.md)).

1. **Dwie serie.** Seria skuteczności wprowadza pozycje katalogu i mierzy, co potok zatrzymuje (M1–M3, M6). Seria czasowa mierzy czas potoku na czystym kodzie (M4, M5).
2. **Jedna pozycja = jedna próba.** Każda próba to pull request od czystej wersji aplikacji, który wprowadza dokładnie jedną pozycję katalogu. Daje to 20 prób na wariant, razem 40. Blokadę przypisujemy jednoznacznie jednej pozycji.
3. **Rozdzielenie wariantów.** Jedno repozytorium, dwie gałęzie bazowe `exp/variant-a` i `exp/variant-b`. Każda zawiera tę samą czystą aplikację i tylko workflow swojego wariantu.
4. **DAST jako bramka przed wdrożeniem.** W wariancie B OWASP ZAP w trybie baseline (pasywnym, z limitem czasu) skanuje kontener uruchomiony w runnerze GitHub Actions na każdym pull requeście. Na produkcję trafia ten sam obraz (ten sam digest).
5. **Decyzja „zatrzymana / przepuszczona” pochodzi z logów potoku.** Audyt po wdrożeniu jest lekkim pomiarem kontrolnym M3, poza potokiem: jedno wdrożenie zbiorcze na wariant i audyt tła czystej wersji (sekcja 4).

## 1. Przygotowanie

Kroki P1–P5 są wymaganiami dla zadań implementacyjnych (aplikacja E04, potoki, infrastruktura E05). Wszystkie muszą być spełnione przed pierwszą próbą serii właściwej.

### P1. Zamrożenie badanych elementów

- Katalog podatności referencyjnych w wersji v1 (po E03-07), razem z regułami własnymi Semgrep dla GT-06 i GT-14 (decyzja autora z 2026-10-20, `docs/metodyka.md`, p. 4.3).
- Konfiguracja serii porównawczej CodeQL: 14 pozycji, zestaw `security-extended`, osobny workflow uruchamiany ręcznie po serii właściwej (decyzje autora z 2026-10-20, `docs/metodyka.md`, p. 4.3).
- Czysta wersja aplikacji oznaczona tagiem git (roboczo `exp-clean-v1`).
- Workflow obu wariantów w wersji końcowej.
- Progi bramek wariantu B (np. minimalna ważność zgłoszenia, które blokuje) zapisane w konfiguracji i w dzienniku badawczym.
- Ochrona gałęzi `exp/variant-b` (branch protection): joby-bramki są wymaganymi status checks, więc nieudana bramka uniemożliwia scalenie, a tym samym wdrożenie.
- Narzędzia wariantu B zapisują pełne raporty, także zgłoszenia poniżej progu blokady (potrzebne do M1). Próg blokady stosuje osobny krok bramki.

Po rozpoczęciu serii właściwej nie zmieniamy żadnego z tych elementów. Zmiana progu po obejrzeniu wyników byłaby dopasowaniem potoku do wyniku (zagrożenie trafności wewnętrznej TW2, `docs/metodyka.md`, p. 4.5). Jeśli zmiana okaże się konieczna, zapisujemy ją w dzienniku z uzasadnieniem i powtarzamy całą serię.

### P2. Przypięcie wersji

- Runner: etykieta konkretnej wersji systemu (`ubuntu-24.04`), nie `ubuntu-latest`.
- Akcje GitHub przypięte do pełnego SHA commita, obrazy narzędzi (m.in. ZAP, Trivy) do digestu.
- Zależności aplikacji zapisane z dokładnymi wersjami.
- **Bazy podatności** (Trivy, skaner zależności) aktualizują się przy każdym uruchomieniu i nie są zamrażane. Serię skuteczności wykonujemy w krótkim oknie czasu (docelowo jeden dzień), a przy każdym przebiegu zapisujemy wersję lub datę bazy. Nowe CVE, które pojawią się w trakcie, klasyfikujemy jako zgłoszenia spoza katalogu ([`README.md`](README.md), „Jak liczymy trafienia”).

### P3. Gałęzie

- Z tagu czystej wersji powstają gałęzie bazowe `exp/variant-a` i `exp/variant-b`.
- Dla każdej pozycji katalogu przygotowujemy łatkę, która wprowadza tylko tę pozycję. Pozycje dotyczące workflow (GT-15, GT-16, GT-17) mają osobną łatkę dla każdego wariantu, bo pliki workflow wariantów się różnią.
- Skrypt nakłada każdą łatkę na obie gałęzie bazowe i tworzy 40 gałęzi prób. Szczegóły nazewnictwa i przygotowania gałęzi: E04-04.
- Każda łatka zachowuje działanie aplikacji: testy funkcjonalne przechodzą. Inaczej potok A zatrzymałby pozycję z powodu testów, a nie braku filtrów. Sprawdza to pilotaż (P5) na wariancie A.
- Każda łatka przechodzi też linting i formatowanie (`ruff check`, `ruff format --check` w `app/`), bo lint działa w obu wariantach. Ruff nie ma włączonych reguł bezpieczeństwa (`S`), więc sam nie wykrywa pozycji katalogu. Łatka nie może jednak zostawiać nieużywanych importów ani zmiennych (np. `require_admin` po GT-19) ani niesformatowanego kodu (decyzja autora z 2026-10-30, E04-05).

### P4. Zapis danych

Katalog `experiment/data/` przechowuje surowe dane:

- odpowiedzi GitHub REST API z czasami jobów i kroków (próba 1 przebiegu, `docs/metodyka.md`, p. 3.2),
- raporty narzędzi w formacie maszynowym (JSON lub SARIF), pobrane z artefaktów przebiegu,
- manifest wersji: SHA akcji, digesty obrazów, wersje narzędzi i baz podatności, etykieta runnera.

Struktura plików: TODO (E09).

### P5. Pilotaż

Przed serią właściwą wykonujemy 1–2 próby i kilka przebiegów czasowych, żeby sprawdzić:

- skrypty tworzenia gałęzi, pobierania danych i zapisu,
- znaczenie pola `created_at` joba jako chwili wejścia do kolejki (otwarta kwestia z E03-04), przez porównanie z czasami w interfejsie GitHub,
- czy łatki przechodzą testy funkcjonalne w wariancie A (P3),
- czy workflow A różni się od workflow B wyłącznie krokami bezpieczeństwa (diff plików, K2 w sekcji 5),
- czy wynik próby jest powtarzalny: próbę wariantu B dla wybranych pozycji, zwłaszcza GT-12–14 wykrywanych przez ZAP, wykonujemy dwukrotnie i porównujemy zgłoszenia (zagrożenie TN5, `docs/metodyka.md`, p. 4.5).

Dane pilotażu oznaczamy jako pilotażowe i nie wchodzą do wyników.

## 2. Seria czasowa

Seria czasowa dostarcza M4 i M5 (`docs/metodyka.md`, p. 3.2): ile wariant B wydłuża potok względem wariantu A. Decyzje autora z 2026-10-13.

### 2.1. Zakres

- Wyzwalacze:
  - **PR**: przebieg wywołany aktualizacją pull requesta (pętla informacji zwrotnej programisty, H2a),
  - **main**: push na gałąź bazową wariantu (`exp/variant-a` albo `exp/variant-b`), z prawdziwym wdrożeniem czystej wersji do AWS. W metodyce wyzwalacz nosi nazwę „main”.
- Dla każdej pary (wariant, wyzwalacz): 1 przebieg rozgrzewkowy, nieliczony, i 20 przebiegów pomiarowych. Razem 80 przebiegów pomiarowych.
- Wszystkie przebiegi działają na czystej wersji aplikacji, więc bramki przechodzą i każdy przebieg dochodzi do końca.

### 2.2. Wywołanie przebiegów

Liczymy tylko pierwszą próbę przebiegu, więc ponowne uruchomienie („Re-run”) jest niedozwolone. Każdy przebieg pomiarowy wywołuje nowy, pusty commit (`git commit --allow-empty`), który nie zmienia kodu:

- **PR:** dla każdego wariantu jeden pull request z gałęzi pomiarowej do gałęzi bazowej. Skrypt wypycha na gałąź pomiarową kolejne puste commity.
- **main:** skrypt wypycha puste commity bezpośrednio na gałąź bazową wariantu. Każdy push uruchamia pełny potok z wdrożeniem.

Skrypt wywołujący: TODO (E09).

### 2.3. Zasady pomiaru

1. **Jeden przebieg naraz.** Kolejny przebieg startuje dopiero po zakończeniu poprzedniego (wszystkich jobów, łącznie z wdrożeniem), żeby przebiegi nie konkurowały o runnery i środowisko.
2. **Przeplatanie wariantów.** W obrębie wyzwalacza przebiegi idą naprzemiennie: A, B, A, B… Zmienne obciążenie infrastruktury GitHub w ciągu dnia dotyka wtedy obu wariantów w podobnym stopniu.
3. **Cache jak w codziennej pracy.** Potoki używają cache tak, jak zaprojektowano je do normalnej pracy. Kroki wspólne obu wariantów (np. instalacja zależności, budowanie obrazu) mają identyczną konfigurację cache. Przebieg rozgrzewkowy wypełnia cache przed serią i nie wchodzi do wyników. Wynik odpowiada więc kosztowi codziennej pracy, nie pierwszego uruchomienia.
4. **Zapis warunków.** Przy każdym przebiegu zapisujemy: identyfikator przebiegu, wariant, wyzwalacz, numer kolejny, wersję obrazu runnera (z logu joba) i wersję bazy podatności. Zmiana obrazu runnera w trakcie serii jest odnotowywana w dzienniku badawczym.
5. **Przebiegi nieudane.** Przebieg przerwany z przyczyn infrastrukturalnych powtarzamy jako nowy i zapisujemy w dzienniku (`docs/metodyka.md`, p. 3.1). Przebieg, w którym bramka zablokowała czystą wersję, oznacza błąd przygotowania: przerywamy serię i wyjaśniamy przyczynę.

### 2.4. Wdrożenia w serii main

- Wdrażana jest wyłącznie czysta wersja, więc zabezpieczenia z sekcji 6 dotyczą jej w mniejszym stopniu. Środowisko istnieje tylko w oknie serii main.
- Czas wdrożenia zależy też od AWS. Ten składnik jest wspólny dla obu wariantów, więc nie zmienia narzutu M5 liczonego jako różnica median. Czas kroków skanerów pokazuje rozbicie M5.
- Czy oba warianty wdrażają do jednego środowiska, czy do dwóch identycznych: TODO (E05).

Czas trwania całej serii: TODO, po pilotażu (P5).

## 3. Seria skuteczności

Seria skuteczności dostarcza M1–M3, M6 i M9 (`docs/metodyka.md`, p. 3.2). Decyzje autora z 2026-10-13.

### 3.1. Przebieg jednej próby

Próba to para (wariant v, pozycja k katalogu).

1. Skrypt tworzy gałąź próby (roboczo `exp/trial-<v>-<GT-xx>`) od gałęzi bazowej wariantu v, nakłada łatkę pozycji k i otwiera pull request do gałęzi bazowej.
2. Uruchamia się potok PR wariantu v. Liczy się tylko pierwsza próba przebiegu.
3. Po zakończeniu przebiegu zapisujemy w `experiment/data/`:
   - identyfikator przebiegu, wariant, pozycję,
   - wynik każdego joba-bramki (przeszła / zablokowała),
   - pełne raporty narzędzi z artefaktów przebiegu, łącznie ze zgłoszeniami poniżej progu blokady,
   - wersję obrazu runnera i bazy podatności.
4. Pull request zamykamy bez scalania, a gałąź próby usuwamy. Gałąź bazowa pozostaje czysta dla kolejnych prób.

W wariancie A potok nie ma bramek. Próba potwierdza, że pozycja przeszłaby do wdrożenia (potok kończy się powodzeniem).

### 3.2. Kolejność i okno czasu

- Próby wykonujemy parami dla każdej pozycji: A-GT-01, B-GT-01, A-GT-02, B-GT-02… Obie próby pozycji widzą tę samą bazę podatności i podobne warunki.
- Jedna próba naraz. Cała seria (40 prób) w krótkim oknie czasu (P2).

### 3.3. Klasyfikacja wyniku próby w wariancie B

Każda próba w wariancie B dostaje jedną z czterech klas:

| Klasa | Warunek | M1 (wykryta) | H1 (zatrzymana) |
|---|---|---|---|
| **Z1. Zatrzymana z trafieniem** | co najmniej jedna bramka zablokowała, a wśród zgłoszeń blokujących jest trafienie pozycji k | tak | tak |
| **Z2. Wykryta, niezatrzymana** | jest trafienie pozycji k, ale tylko poniżej progu blokady lub w narzędziu niepełniącym roli bramki; potok przechodzi | tak | nie |
| **Z3. Zatrzymana bez trafienia** | bramka zablokowała, ale żadne zgłoszenie blokujące nie jest trafieniem pozycji k (np. fałszywy alarm wywołany kodem łatki, nowe CVE w trakcie serii) | zależnie od zgłoszeń poniżej progu | **nie** |
| **Z4. Niewykryta** | brak trafienia pozycji k; potok przechodzi | nie | nie |

Reguła trafienia: [`README.md`](README.md), „Jak liczymy trafienia”.

**Klasa Z3 nie liczy się jako zatrzymanie** (decyzja autora z 2026-10-13). Blokada przez fałszywy alarm albo zgłoszenie niezwiązane z pozycją nie oznacza, że potok wykrył tę podatność. Liczenie jej jako zatrzymania pozwalałoby fałszywym alarmom poprawiać wynik H1. Próby Z3 raportujemy osobno, z przyczyną blokady. Ponieważ czysta wersja przechodzi bramki (sekcja 2.3), klasa Z3 powinna występować rzadko.

### 3.4. Od prób do metryk

| Metryka | Wyliczenie z prób |
|---|---|
| M1 | pozycje z trafieniem w wariancie B (klasy Z1, Z2 oraz Z3 z trafieniem poniżej progu) / 20; obok M1_z i M1_g |
| M2 | etap najwcześniejszego trafienia: PR (próba) albo audyt po wdrożeniu (sekcja 4). Etap „main przed wdrożeniem” wystąpi tylko wtedy, gdy potok main ma kontrole, których nie ma potok PR |
| M3 | wariant B: pozycje spoza klasy Z1 / 20; wariant A: pozycje, których próba zakończyła się powodzeniem / 20. Potwierdzenie: audyt po wdrożeniu zbiorczym (sekcja 4) |
| M6 | zgłoszenia blokujące ze wszystkich prób wariantu B, unikalne i sklasyfikowane według p. 3.3 metodyki |
| M9 | N_blok = próby B z blokadą (Z1 + Z3); N_FP = próby, w których wszystkie zgłoszenia blokujące to fałszywe alarmy |

Przypadek próby A zakończonej niepowodzeniem oznacza błąd przygotowania łatki (P3): poprawiamy łatkę, zapisujemy to w dzienniku i powtarzamy obie próby tej pozycji.

## 4. Wdrożenie zbiorcze i audyt kontrolny

Decyzja „zatrzymana / przepuszczona” zapada w próbach (sekcja 3). Audyt po wdrożeniu niezależnie sprawdza, co jest na działającym środowisku. Audyt jest lekki: jeden skrypt, pasywne narzędzia i pojedyncze, nieszkodliwe żądania potwierdzające (decyzje autora z 2026-10-13).

### 4.1. Wersje zbiorcze

- **Wersja zbiorcza A:** czysta wersja z wszystkimi pozycjami, których próba A zakończyła się powodzeniem.
- **Wersja zbiorcza B:** czysta wersja z pozycjami, które w próbach B nie dostały klasy Z1 (sekcja 3.3).
- Wersję zbiorczą scalamy do gałęzi bazowej wariantu i przepuszczamy przez potok main tego wariantu. W wariancie B jest to dodatkowo kontrola spójności: wynik bramek powinien zgadzać się z próbami. Rozbieżność zapisujemy i wyjaśniamy.
- Scalenie łatek dotykających tego samego miejsca w kodzie (np. GT-12, GT-13, GT-14) wymaga ręcznego rozwiązania konfliktów: E04-04.

### 4.2. Okno audytu

Jedno okno w AWS, kolejno:

1. utworzenie środowiska,
2. wdrożenie czystej wersji i audyt (tło),
3. wdrożenie wersji zbiorczej A i audyt,
4. wdrożenie wersji zbiorczej B i audyt,
5. usunięcie środowiska.

Za każdym razem ten sam skrypt audytu, uruchamiany z komputera autora (sekcja 6, zabezpieczenie 2).

### 4.3. Dwie role audytu

| Rola | Pytanie | Techniki | Metryka |
|---|---|---|---|
| **R1. Potwierdzenie** | czy pozycja k jest obecna na środowisku produkcyjnym? | wszystkie sprawdzenia z p. 4.4; korzystają z wiedzy o katalogu | M3 |
| **R2. Wykrycie po wdrożeniu** | czy narzędzie uruchomione na produkcji samo zgłasza pozycję k? | tylko OWASP ZAP baseline (pasywny) i Trivy, bez wiedzy o katalogu; trafienie według reguły z [`README.md`](README.md) | M2 (etap „audyt po wdrożeniu”) |

Potwierdzenie przez celowane sprawdzenie (R1) nie jest wykryciem w sensie M2, bo korzysta z wiedzy o lokalizacji pozycji.

### 4.4. Sprawdzenia potwierdzające (R1)

Najpierw skrypt sprawdza, czy na środowisku działa obraz o digeście zbudowanym przez potok wdrażanej wersji. Przy niezgodności audyt przerywamy.

| Grupa | Pozycje | Sprawdzenie |
|---|---|---|
| kod widoczny z zewnątrz | GT-01, GT-04, GT-05 | jedno nieszkodliwe żądanie potwierdzające zachowanie podatności (np. dla GT-04 wyrażenie arytmetyczne i porównanie wyniku) |
| kod niewidoczny z zewnątrz | GT-02, GT-03, GT-06 | inspekcja wdrożonego obrazu pobranego po digeście: czy plik zawiera zmianę z łatki |
| zależności | GT-07 | wersja pakietu `jinja2` w obrazie; Trivy na obrazie (także R2) |
| kontener | GT-08, GT-09 | Trivy na obrazie: system bez wsparcia (także R2); `docker inspect`: użytkownik procesu |
| IaC | GT-10, GT-11 | odczyt konfiguracji przez AWS CLI (reguły grupy zabezpieczeń, szyfrowanie magazynu); próba połączenia TCP z portem 22 |
| konfiguracja web | GT-12, GT-13, GT-14 | żądanie z nagłówkiem `Origin` i odczyt `Access-Control-Allow-Origin`; nagłówki `X-Frame-Options` i CSP `frame-ancestors`; wywołanie nieobsłużonego wyjątku i sprawdzenie, czy odpowiedź zawiera stack trace |
| workflow | GT-15, GT-16, GT-17 | odczyt pliku workflow na gałęzi bazowej po scaleniu wersji zbiorczej |
| logika autoryzacji | GT-18, GT-19, GT-20 | scenariusz HTTP z dwoma kontami testowymi: odczyt zasobu drugiego użytkownika, wywołanie funkcji administracyjnej przez zwykłego użytkownika, próba nadania sobie roli w aktualizacji profilu |

**Pozycje workflow** nie istnieją na działającym serwerze. Dla nich „dotarła na produkcję” oznacza: została scalona do gałęzi bazowej, więc działa w potoku, który wdraża produkcję (decyzja autora z 2026-10-13). Dzięki temu M3 obejmuje wszystkie 20 pozycji, spójnie z H1 i M1.

### 4.5. Wynik i porównanie

- Każde sprawdzenie daje: **obecna**, **nieobecna** albo **nie da się potwierdzić** (z przyczyną).
- **Tło weryfikuje sprawdzenia.** Na czystej wersji każde sprawdzenie musi dać „nieobecna”. Sprawdzenie, które daje „obecna” na czystej wersji, poprawiamy przed audytem wersji zbiorczych.
- Wynik audytu porównujemy z oczekiwaniem z prób: w A obecne wszystkie pozycje, w B obecne pozycje spoza klasy Z1. Każdą niezgodność opisujemy w wynikach (np. nagłówek dodany przez usługę AWS, który usuwa GT-13 ze środowiska).
- Zgłoszenia ZAP i Trivy spoza katalogu klasyfikujemy jak w p. 3.3 metodyki, ale nie wchodzą do M6, które dotyczy bramek.

### 4.6. Wymagania dla innych zadań

- **E04-01:** dwa konta testowe z fikcyjnymi danymi i zasobem każdego z nich; powtarzalny sposób wywołania nieobsłużonego wyjątku (bez tego GT-14 dostaje wynik „nie da się potwierdzić”).
- **E05:** uprawnienia tylko do odczytu konfiguracji grupy zabezpieczeń i magazynu dla audytu; dostęp do rejestru obrazów w celu pobrania obrazu po digeście.
- **E09:** skrypt audytu i format zapisu wyników w `experiment/data/`.

## 5. Zmienne kontrolowane

Zmienną niezależną jest wariant potoku (A albo B), a zmiennymi zależnymi metryki M1–M9. Pozostałe czynniki, które mogą wpłynąć na wynik, trzymamy stałe (5.1) albo, jeśli się nie da, rejestrujemy (5.2). Lista przyjęta przez autora 2026-10-13.

### 5.1. Zmienne kontrolowane

| # | Zmienna | Jak trzymamy stałą | Gdzie opisano |
|---|---|---|---|
| K1 | kod aplikacji | ten sam tag czystej wersji; te same łatki w obu wariantach (GT-15–17 jako równoważne zmiany w pliku workflow danego wariantu) | P1, P3 |
| K2 | kroki wspólne potoków | workflow A powstaje z workflow B przez usunięcie jobów i kroków bezpieczeństwa; build, testy, publikacja obrazu i wdrożenie są identyczne. Kontrola: porównanie plików (diff) w pilotażu pokazuje wyłącznie kroki bezpieczeństwa | P5 |
| K3 | runner | runnery hostowane GitHub, etykieta `ubuntu-24.04`, ten sam typ maszyny | P2 |
| K4 | wersje | akcje przypięte do SHA, narzędzia do digestu, zależności z dokładnymi wersjami | P2 |
| K5 | konfiguracja bramek | progi blokady i konfiguracja ZAP (tryb baseline, limit czasu, zestaw reguł) zamrożone przed serią | P1, sekcja 0 |
| K6 | katalog | wersja v1 zamrożona | P1 |
| K7 | cache | identyczna konfiguracja cache dla kroków wspólnych; przebieg rozgrzewkowy przed serią czasową | 2.3 |
| K8 | repozytorium | jedno repozytorium z tymi samymi ustawieniami, rolą OIDC i ochroną gałęzi | sekcja 0, P1 |
| K9 | środowisko AWS | ten sam region i ta sama konfiguracja Terraform dla obu wariantów | 2.4, E05 |
| K10 | kolejność i równoczesność | jeden przebieg naraz; przeplatanie A/B w serii czasowej; próby parami dla każdej pozycji | 2.3, 3.2 |
| K11 | okno czasu | seria skuteczności w krótkim oknie (docelowo jeden dzień) | P2, 3.2 |
| K12 | sposób pomiaru | ten sam skrypt pobierania danych; tylko pierwsza próba przebiegu | P4, `docs/metodyka.md` p. 3.1 |

### 5.2. Zmienne niekontrolowane, rejestrowane

| Zmienna | Postępowanie |
|---|---|
| obciążenie infrastruktury GitHub (kolejka do runnera) | przeplatanie A/B; mediana i p90 zamiast średniej; kolejka pierwszego joba raportowana osobno (T_czek − T_wyk) |
| aktualizacje obrazu runnera | zapis wersji obrazu przy każdym przebiegu; zmiana w trakcie serii odnotowana w dzienniku badawczym |
| bazy podatności | zapis wersji lub daty bazy przy każdym przebiegu; nowe CVE klasyfikowane jako zgłoszenia spoza katalogu |
| czas operacji AWS i sieci | składnik wspólny obu wariantów; narzut liczony jako różnica median; czas skanerów z rozbicia na kroki (M5) |

## 6. Bezpieczeństwo eksperymentu

Wariant A celowo wdraża do AWS aplikację z podatnościami, które da się wykorzystać, a repozytorium jest publiczne. Obowiązują zabezpieczenia (decyzja autora z 2026-10-13, potwierdzają wymagania z [`README.md`](README.md)):

1. **Krótkie życie środowiska.** Środowisko istnieje tylko w oknie wdrożenia i audytu (utworzenie, wdrożenie, audyt, usunięcie). Konto ma alert budżetowy. Aplikacja nie zawiera prawdziwych danych, a sekrety w katalogu są fikcyjne.
2. **Dostęp tylko z adresu autora.** Port aplikacji jest dostępny wyłącznie z publicznego adresu IP autora. Audyt uruchamiamy z komputera autora, nie z runnera GitHub.
3. **Brak logowania na instancję.** Instancja nie ma klucza SSH ani logowania hasłem, więc otwarty port 22 (GT-10) jest mierzalny, ale nie daje dostępu.
4. **Workflow odporny na nadużycie.** Brak wyzwalacza `pull_request_target`. Pull requesty eksperymentu pochodzą tylko z gałęzi tego repozytorium. Uruchomienie workflow dla zewnętrznych kontrybutorów wymaga zgody (ustawienie repozytorium). Rola AWS (OIDC) pozwala wdrażać tylko z gałęzi `exp/variant-*`, nie z pull requestów.

TODO: zweryfikować politykę AWS dotyczącą testów bezpieczeństwa dla usług wybranych w E05 (przy pasywnym audycie sprawa drobna).
