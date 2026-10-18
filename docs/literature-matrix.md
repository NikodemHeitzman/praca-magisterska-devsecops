# Macierz literatury

- **Zadanie:** E02-08 (tablica zadań). Używane w podrozdziale 2.5 (luka badawcza) i w dyskusji wyników (5.3).
- **Zakres:** 5 prac naukowych z rdzenia literatury (`Zrodla/_Rdzen.md` w vaulcie). Decyzja autora z 2026-10-14: zamiast „min. 10 artykułów” z definicji zadania, zgodnie z zestawem literatury zaakceptowanym przez promotora (mail z 2026-10-05, por. E02-07). Literatura zostanie uzupełniona po napisaniu części teoretycznej.
- **Pytania badawcze:** RQ1 (skuteczność), RQ2 (koszt), RQ3 (zgodność), pełne brzmienie w [`metodyka.md`](metodyka.md), p. 2.1.
- **Skąd tekst:** pełne teksty w vaulcie, `Zrodla/pdf/` (poza repozytorium, ze względu na prawa autorskie). Wersje:

  | Praca | Wersja użyta w macierzy | Numeracja stron |
  |---|---|---|
  | [@Rajapakse2022] | preprint arXiv:2103.08266v2 (29.07.2021, „Submitted to the Journal of Information and Software Technology”) | strony preprintu (numer na stronie = numer w PDF); TODO: wersja w czasopiśmie ma inną numerację |
  | [@Cheenepalli2025] | preprint arXiv:2503.22612v1 (28.03.2025) | strony według przeglądarki PDF (preprint bez numeracji); TODO: wersja IEEE ma inną numerację |
  | [@Alghawli2024] | arXiv:2412.16190, rękopis autorski (wgrany po publikacji, journal_ref: AEJ 107, s. 136–149) | własna numeracja rękopisu „N of 23” = numer w PDF; TODO: wersja w AEJ ma s. 136–149 i inny układ |
  | [@Janczewski2025] | wersja opublikowana (strona czasopisma WSB), s. 77–90 | według wersji opublikowanej (numer w PDF + 76) |
  | [@Biswas2025] | **tylko abstrakt** (Semantic Scholar) i metadane Crossref; brak dostępu do IEEE Xplore | — |

- **Stan lektury (2026-10-18):** autor przeczytał opracowania z pytaniami dla Rajapakse2022, Cheenepalli2025, Alghawli2024 i Janczewski2025, więc w rejestrze mają `zweryfikowane: opracowanie`. Oryginałów nie czytał: szczegóły z numerem strony sprawdza w źródle. Biswas2025: `nie` (tylko abstrakt).

## 1. Tabela zbiorcza

| Źródło | Jakość źródła | Problem | Metoda | Główne wyniki | Związek z RQ | Ograniczenia | Rozdział pracy |
|---|---|---|---|---|---|---|---|
| [@Rajapakse2022] | Czasopismo (IST, Elsevier), recenzowane; preprint | Wyzwania i rozwiązania przy wdrażaniu DevSecOps | Przegląd systematyczny (SLR), 54 prace, analiza tematyczna | 21 wyzwań, 31 rozwiązań, 9 luk; najwięcej problemów dotyczy narzędzi (fałszywe alarmy i czas SAST); kompromis szybkość–bezpieczeństwo | RQ1 (podatności w CI/CD, kontenerach), RQ2 (czas, fałszywe alarmy), RQ3 (brak zgody, co i gdzie przesunąć w lewo) | Literatura do 06.2020; brak łańcucha dostaw, SBOM, SLSA, GitHub Actions; brak pomiarów, sama synteza | 2.1, 2.5, 5.3 |
| [@Cheenepalli2025] | Konferencja IEEE (ISDFS 2025), 6 s.; preprint | Wyzwania i dobre praktyki DevSecOps w MŚP | Ankieta, 405 respondentów z panelu, odsetki; ramy TAM i DOI | 68% deklaruje pełne wdrożenie; bariery: złożoność 41%, zasoby 35%, kultura 38%; skan przy każdym commicie tylko 12%; bezpieczeństwo kontenerów 34%; 11 zaleceń | RQ1 (rzadkie skany per commit, kontenery), RQ2 (złożoność i koszt jako bariera; brak pomiaru), RQ3 (zalecenia ogólne, bez standardów) | Dane deklaratywne, brak testów statystycznych; MŚP = 1–5000 pracowników; brak łańcucha dostaw i standardów | 2.5, 5.3 |
| [@Alghawli2024] | Czasopismo (AEJ, Elsevier, open access), recenzowane; rękopis autorski z arXiv | Klaster AWS z potokiem DevSecOps i automatyczną oceną ryzyka | Projekt i wdrożenie (Terraform, Jenkins, SonarQube, AWS); wybór dostawcy metodą AHP; model ryzyka oparty na FAIR | Architektura AWS z zaleceniami (szyfrowanie, VPC, WAF, GuardDuty); AWS wybrany z wagą 50,9%; liczby ryzyka bez danych wejściowych | RQ1 (tylko SAST, bez pomiaru wykryć), RQ2 (mierzy czas Terraform, nie potoku), RQ3 (brak standardów potoku) | Wyniki nieodtwarzalne; jeden skaner; klucze admina IAM; błędy rzeczowe; brak łańcucha dostaw | 2.3, 4.2, 5.3, 6.3 |
| [@Janczewski2025] | Zeszyty Naukowe WSB w Poznaniu (polskie czasopismo uczelniane), 14 s. | DevSecOps w chmurze dla infrastruktury krytycznej | Przegląd literatury bez protokołu + ankieta wśród ekspertów, bez liczebności i liczb | Deklaracje: shift-left i automatyzacja SAST/DAST/SCA zmniejszają podatności na produkcji; bariera: systemy legacy/SCADA; rola NIS2, ISO 27001, NIST; przykłady SonarQube i Checkov | RQ1 (deklaracje bez pomiaru), RQ2 (kompromis tylko wspomniany), RQ3 (regulacje i standardy, bez SP 800-204D) | Brak danych ankiety i protokołu przeglądu; część źródeł branżowych; wątpliwe przypisanie tezy do Rajapakse2022 | 2.2, 2.3 |
| [@Biswas2025] | Konferencja IEEE (ICRITO 2025), 4 s., autor praktyk; **tylko abstrakt** | Zarządzanie wyjątkami od podatności w obrazach kontenerów | Propozycja ramy (frameworku) dla CI/CD; metoda ewaluacji nieznana z abstraktu | Automatyczne, audytowalne polityki wyjątków dla obrazów Docker w Google Artifact Registry, bez zakłócania potoku | RQ2 (obsługa zgłoszeń, narzut operacyjny), RQ1 (wyjątki jako droga przepuszczenia podatności) | Bez pełnego tekstu; inny dostawca chmury (GCP); krótka praca | 5.3 |

Kolumna „Rozdział pracy” wstępnie według `Zrodla/_Rdzen.md`; do korekty po lekturze.

## 2. Karty prac

Każde twierdzenie ma numer strony według numeracji użytej wersji (patrz tabela wersji wyżej).

### 2.1. [@Rajapakse2022]

Strony według preprintu arXiv:2103.08266v2 (numer na dole strony = numer w przeglądarce PDF). Opracowanie: [`notes/rajapakse2022-pytania.md`](notes/rajapakse2022-pytania.md).

- **Jakość źródła:** przegląd systematyczny w czasopiśmie *Information and Software Technology* (Elsevier), recenzowany. Autorzy z University of Adelaide (CREST) i Australian Catholic University (s. 1). Korzystam z preprintu przesłanego do czasopisma (s. 1); wersja opublikowana może się różnić redakcyjnie. TODO: sprawdzić numery stron w wersji wydawcy przed cytowaniem stron.
- **Problem:** jakie wyzwania napotykają praktycy przy wdrażaniu DevSecOps, jakie rozwiązania proponuje literatura i gdzie są luki badawcze. Trzy pytania badawcze autorów: wyzwania, rozwiązania, luki (Tabela 2, s. 5).
- **Metoda:** SLR według wytycznych Kitchenham i Chartersa (s. 4). Źródła: Scopus, IEEE Xplore, ACM DL, wyszukiwanie w czerwcu 2020 (s. 5). Lejek: 460 → 283 po usunięciu duplikatów → 62 po kryteriach → 48 po ocenie jakości → 54 po snowballingu (s. 5–6, rys. 3 s. 7). Wykluczono literaturę szarą, przeglądy i prace do 5 stron (s. 5). Analiza tematyczna (Braun i Clarke) w NVivo (s. 6).
- **Główne wyniki:**
  - 21 wyzwań i 31 rozwiązań w czterech tematach: ludzie, praktyki, narzędzia, infrastruktura (s. 7; tabele 3 i 4, s. 9 i 14–15). Najczęściej opisywane są wyzwania i rozwiązania dotyczące narzędzi (abstrakt, s. 1).
  - Ch4: SAST generuje dużo fałszywych alarmów, których ręczna ocena opóźnia wydania, a pełne skany trwają długo i zużywają zasoby (s. 10). W jednej z prac dodanie skanera bezpieczeństwa wielokrotnie wydłużyło cykl integracji [P28] (s. 8).
  - Ch6, Ch7, Ch9: podatności obrazów kontenerów, systemów CI (najemcy uruchamiają własny kod) i samego potoku CD, który otwiera dodatkowe powierzchnie ataku (s. 10–11).
  - Ch13: brak zgody (ustandaryzowanej metodyki), jak włączać środki bezpieczeństwa do potoku [P16] (s. 12).
  - Ch14: kompromis między szybkością wydań a bezpieczeństwem; część organizacji uważa je za niezgodne (s. 12).
  - Rozwiązania bliskie mojemu projektowi: S3 dobre praktyki konfiguracji skanerów i równoległe potoki do długich skanów (s. 15), S6 ciągła ocena podatności i łączenie wielu narzędzi, żeby ograniczyć fałszywe alarmy (s. 15), S9 analiza statyczna skryptów IaC (s. 16), S16 przesunięcie w lewo (s. 17), S17 ciągła ocena bezpieczeństwa (s. 17), S20 dostęp według potrzeb i automatyczne zmiany na produkcji (s. 17).
  - Luki (p. 4.6, s. 21–22): narzędzia dopasowane do szybkich cykli CI/CD, mało empirycznie zweryfikowanych rozwiązań do ciągłej oceny podatności (s. 21); potrzeba praktycznych wskazówek, jak wyważyć szybkość i bezpieczeństwo (s. 21); brak zgody, co i do którego miejsca potoku przesunąć w lewo (s. 21); brak empirycznie zweryfikowanych metryk bezpieczeństwa dla DevSecOps (s. 22).
- **Związek z RQ1–RQ3:**
  - RQ1 (skuteczność): praca opisuje, jakie klasy problemów potok powinien wychwytywać (SAST, kontenery, IaC, sam potok), ale nie mierzy, ile podatności dociera na produkcję. Moja praca daje taki pomiar dla jednego potoku.
  - RQ2 (koszt): Ch4 i Ch14 to bezpośrednie uzasadnienie, dlaczego mierzę narzut czasu i udział fałszywych alarmów. Luka z s. 21 o wyważeniu szybkości i bezpieczeństwa.
  - RQ3 (zgodność): luka z s. 21 (brak zgody, co i gdzie umieścić w potoku). Moja odpowiedź to lista kontrolna oparta na SP 800-204D i OWASP Top 10 CI/CD.
- **Ograniczenia:**
  - Literatura do czerwca 2020 (s. 5). W tekście nie występują łańcuch dostaw oprogramowania, SBOM, SLSA ani GitHub Actions (sprawdzone wyszukiwaniem w tekście preprintu). Pomija więc temat, który jest w tytule mojej pracy (SP 800-204D).
  - To synteza bez własnych pomiarów. Autorzy sami wskazują, że wiele rozwiązań nie zostało empirycznie zweryfikowanych (s. 21–22).
  - Wykluczenie literatury szarej i krótkich prac (s. 5). Selekcję i ekstrakcję prowadził głównie pierwszy autor, pod nadzorem pozostałych (s. 4, 6).
- **Gdzie użyję:** 2.1 (definicje CI, CDE, CD, DevSecOps, s. 2–3), 2.5 (luka badawcza: brak empirycznej oceny, kompromis szybkość–bezpieczeństwo, brak metryk), 5.3 (porównanie moich wyników narzutu i fałszywych alarmów z Ch4 i Ch14).

### 2.2. [@Cheenepalli2025]

Strony według przeglądarki PDF preprintu arXiv:2503.22612v1 (preprint nie ma numerów na stronach). Opracowanie: [`notes/cheenepalli2025-pytania.md`](notes/cheenepalli2025-pytania.md).

- **Jakość źródła:** krótka praca konferencyjna IEEE (ISDFS 2025, 6 stron, Dakota State University, USA; s. 1). Recenzowana jako artykuł konferencyjny. Korzystam z preprintu v1 z 28.03.2025 (s. 1). TODO: sprawdzić numery stron w wersji IEEE przed cytowaniem stron.
- **Problem:** jakie wyzwania napotykają małe i średnie przedsiębiorstwa (MŚP) przy wdrażaniu DevSecOps i jakie praktyki im pomagają. Trzy pytania badawcze: wyzwania, strategie, dobre praktyki (s. 1).
- **Metoda:** „metody mieszane” oparte na ankiecie; pytania zaprojektowano według modelu akceptacji technologii (TAM) i teorii dyfuzji innowacji (DOI), Tabela I (s. 1–2). Respondentów dostarczył komercyjny panel Centiment; warunek udziału: praca w MŚP i doświadczenie z DevSecOps (s. 2). 405 ważnych odpowiedzi (s. 2). Wyniki podane jako odsetki, bez testów statystycznych (sprawdzone w tekście).
- **Główne wyniki:**
  - Wdrożenie: 68% w pełni, 22% w trakcie, 10% nie zaczęło (Tabela II, s. 2).
  - Narzędzia w CI/CD: bezpieczeństwo API 63%, SCA 62%, IaC 61%, SAST 60%; bezpieczeństwo kontenerów tylko 34% (s. 3).
  - Bariery: złożoność techniczna 41%, ograniczone zasoby 35% (s. 3), opór kulturowy 38% (Tabela IV, s. 3); 31% zgłasza umiarkowaną trudność integracji bezpieczeństwa z CI/CD (s. 3), w innym miejscu 33% (s. 4).
  - Częstotliwość skanów: co tydzień 37%, codziennie 24%, przy każdym commicie tylko 12% (s. 4).
  - Metryki skuteczności używane w firmach: częstotliwość skanów 53%, liczba wykrytych podatności 46%, czas naprawy 45%, mniej incydentów 44% (Tabela III, s. 3).
  - 11 zaleceń, m.in. automatyczne skany w IDE, repozytorium i CI/CD (zal. 2), kontrole zgodności w przepływie pracy (zal. 6), wdrażanie etapami z naciskiem na tanie i otwartoźródłowe narzędzia (zal. 7), audyt IaC (zal. 9), KPI takie jak częstotliwość skanów i tempo naprawy podatności (zal. 10) (s. 5).
- **Związek z RQ1–RQ3:**
  - RQ1 (skuteczność): tylko 12% skanuje przy każdym commicie, a 34% zabezpiecza kontenery (s. 3–4). Mój potok skanuje każdy pull request i obraz kontenera. Praca mierzy jednak tylko *deklarowaną* skuteczność (67% uważa DevSecOps za bardzo skuteczny, s. 3), a nie liczbę zatrzymanych podatności.
  - RQ2 (koszt): złożoność i brak zasobów to główne bariery w MŚP (s. 3). Praca nie mierzy narzutu czasu ani fałszywych alarmów. To uzasadnia, dlaczego mierzę koszt na rzeczywistym potoku.
  - RQ3 (zgodność): zalecenie kontroli zgodności (s. 5) jest ogólne. Praca nie odwołuje się do NIST ani OWASP (sprawdzone wyszukiwaniem w tekście).
- **Ograniczenia:**
  - Dane deklaratywne. Autorzy sami piszą, że mogą zawyżać albo zaniżać poziom wdrożenia i skuteczności, i zalecają walidację empiryczną: studia przypadków, obserwację (s. 6).
  - Ocena agenta: dobór z panelu wyłącznie osób z doświadczeniem w DevSecOps (s. 2) sprzyja zawyżeniu odsetka wdrożeń. Brak stopy odpowiedzi mimo nagłówka „Response Rate” (s. 2). Zapowiedziana część jakościowa nie jest opisana. Brak testów statystycznych, choć tekst mówi o „istotnie lepszej” integracji przy zaangażowaniu kierownictwa (s. 4).
  - MŚP zdefiniowano szeroko, jako 1–5000 pracowników (s. 5); w definicji UE MŚP to mniej niż 250 osób. TODO: zweryfikować definicję UE ze źródłem, jeśli ją przytoczę.
  - W tekście nie występują łańcuch dostaw, SBOM, SLSA, GitHub ani fałszywe alarmy (sprawdzone wyszukiwaniem).
- **Gdzie użyję:** 2.5 (motywacja: MŚP potrzebują prostszych, tańszych rozwiązań, a skanowanie przy każdej zmianie jest rzadkie), 5.3 (moje pomiary kosztu na tle barier „złożoność i zasoby” z ankiety), ewentualnie 1 (motywacja „lekkiego” potoku).

### 2.3. [@Alghawli2024]

Strony według rękopisu z arXiv (numeracja „N of 23” = numer w przeglądarce PDF). Opracowanie: [`notes/alghawli2024-pytania.md`](notes/alghawli2024-pytania.md).

- **Jakość źródła:** artykuł w *Alexandria Engineering Journal* (Elsevier, otwarty dostęp, licencja CC BY-NC-ND), recenzowany. Autorzy z Prince Sattam Bin Abdulaziz University (Arabia Saudyjska) i Charkowskiego Narodowego Uniwersytetu Radioelektroniki (Ukraina) (s. 1). Korzystam z rękopisu autorskiego z arXiv, który ma inny układ i numerację niż wersja w AEJ (s. 136–149). TODO: sprawdzić strony w wersji wydawcy przed cytowaniem stron.
- **Problem:** jak zbudować w chmurze klaster do bezpiecznego wytwarzania aplikacji webowej, który łączy automatyzację DevSecOps, wykrywanie podatności w kodzie i ilościową ocenę ryzyka organizacji (s. 2). Autorzy twierdzą, że dotychczasowe podejścia rozwiązują te trzy zadania osobno (s. 2) i że modele ryzyka w chmurze nie są jednocześnie zautomatyzowane i ilościowe (s. 4).
- **Metoda:** praca projektowo-wdrożeniowa, w czterech częściach:
  1. Algorytm automatycznej oceny ryzyka w 8 krokach oparty na triadzie poufność–integralność–dostępność (CIA) (s. 6–7) i na zmodyfikowanej metodyce FAIR, ze wzorami (1)–(3) na prawdopodobieństwo i stratę (s. 7–9).
  2. Wybór dostawcy chmury metodą AHP Saaty’ego według 5 kryteriów (s. 9–13). Czas wdrożenia infrastruktury przez Terraform v0.12 zmierzono w eksperymencie trwającym 10 dni (s. 10).
  3. Architektura klastra w AWS z zaleceniami dla poszczególnych usług (s. 13–18).
  4. Potok Jenkins (Groovy) z SonarQube i wdrożeniem blue-green (s. 18).
- **Główne wyniki:**
  - Średni czas wdrożenia infrastruktury: AWS 6,3 min, Azure 6,5 min, GCP 7 min (s. 10). Koszt klastra w AWS 350,37 USD/mies., dane z 2023 r. (Tabela 1, s. 11).
  - Wagi AHP: AWS 50,9%, Azure 33,6%, GCP 15,5% (Tabela 3, s. 12). Autorzy zaznaczają, że ocena była ekspercka i oparta na wymaganiach, które sami przyjęli (s. 13).
  - Zalecenia dla usług AWS (s. 15–17):
    - szyfrowanie EBS, RDS i S3,
    - VPC z prywatną podsiecią dla bazy, grupy bezpieczeństwa z minimum otwartych portów,
    - TLS 1.2/1.3 na load balancerze, WAF z regułami na XSS, SQLi i limit żądań,
    - GuardDuty, CloudWatch i SNS,
    - stan Terraform w S3 zamiast lokalnie (s. 14).
  - Potok: push do GitHub, webhook, Jenkins, skan SonarQube z obliczeniem ryzyka CIA, budowa obrazu Docker, wysłanie do ECR, wdrożenie blue-green przez AWS CodePipeline (s. 18).
  - Wynik eksperymentu z ryzykiem: prawdopodobieństwa naruszenia 0,77, 0,68 i 0,81 oraz ryzyko 4184,6, 3819,3 i 4475,5 „jednostek umownych” odpowiednio dla poufności, integralności i dostępności (Tabela 4, s. 18).
- **Związek z RQ1–RQ3:**
  - RQ1 (skuteczność): potok ma jeden skaner, SonarQube (s. 18). Praca nie podaje, ile podatności wykryto ani zatrzymano. Mój potok łączy kilka klas skanerów (SAST, SCA, sekrety, IaC, obraz kontenera) i mierzy, co dociera na produkcję.
  - RQ2 (koszt): mierzony jest tylko czas wdrożenia infrastruktury przez Terraform (s. 10), a nie narzut skanów w potoku ani fałszywe alarmy.
  - RQ3 (zgodność): brak odniesienia do NIST SP 800-204D, OWASP czy SLSA. NIST pojawia się tylko w bibliografii, przy NIST CSF i FAIR (sprawdzone wyszukiwaniem w tekście).
- **Ograniczenia** (ocena agenta, z podstawą w tekście):
  - Wyniki ryzyka są nieodtwarzalne. Tabela 4 nie podaje danych wejściowych (zdarzeń, hipotez, kwot strat), a zgodność z metodą standardową opisano bez liczb (s. 9, 18).
  - Jeden skaner SAST. Brak SCA, skanowania obrazów, IaC i sekretów (s. 18).
  - Praktyki sprzeczne z najmniejszymi uprawnieniami: użytkownik IAM z prawami administratora i dostępem programowym dla Terraform, przykład polityki AmazonS3FullAccess (s. 17). Zmiana portu SSH jako środek bezpieczeństwa (s. 15). Mój projekt używa OIDC bez długoterminowych kluczy.
  - Błędy rzeczowe i niespójności:
    - zdanie, że Kubernetes i Azure to projekty Google (s. 13), podczas gdy Azure to usługa Microsoft,
    - port SSH 37337 (s. 15) i 37377 (s. 17).
  - Brak łańcucha dostaw, SBOM i SLSA. Terraform v0.12 (s. 10) jest dziś przestarzały.
- **Gdzie użyję:**
  - 2.3, praca pokrewna: DevSecOps dla aplikacji webowej w AWS z Terraform i Dockerem, czyli najbliższy mojemu projektowi zestaw technologii.
  - 4.2, punkt odniesienia dla architektury AWS. Zalecenia dla usług mogę porównać ze swoimi, np. stan Terraform w S3, szyfrowanie, WAF.
  - 5.3, kontrast: brak pomiaru skuteczności i kosztu oraz jeden skaner, wobec moich pomiarów.
  - 6.3, kierunki dalszych badań: ciągła, ilościowa ocena ryzyka w potoku (przypisanie z rejestru `Zrodla/`).

### 2.4. [@Janczewski2025]

Strony według wersji opublikowanej, s. 77–90 (numer w PDF + 76). Opracowanie: [`notes/janczewski2025-pytania.md`](notes/janczewski2025-pytania.md).

- **Jakość źródła:** artykuł w *Zeszytach Naukowych Wyższej Szkoły Bankowej w Poznaniu* (2025, t. 108, nr 1), jeden autor, WSB w Warszawie (s. 77). Polska publikacja, jedyna polska w rdzeniu. TODO: zweryfikować, czy czasopismo jest recenzowane i ile ma punktów na liście ministerialnej, jeśli to będzie potrzebne w pracy. Tytuł w bibliografii według PDF („…Analiza bezpieczeństwa procesów CI/CD”, s. 77), a nie według Crossref, który podaje „…Analiza integracji bezpieczeństwa z procesami CI/CD” (decyzja autora, 2026-10-14).
- **Problem:** jak wdrażać praktyki DevSecOps w środowiskach chmurowych infrastruktury krytycznej i jak skuteczne są narzędzia SAST, DAST, SCA i IAST w CI/CD (streszczenie, s. 77; s. 79).
- **Metoda:** „podejście mieszane” (s. 83):
  1. Przegląd literatury naukowej i branżowej. Autor nazywa go systematycznym, ale podaje tylko ogólne kryteria doboru: prace recenzowane, raporty branżowe i dokumentacja, po angielsku lub polsku, z ostatnich kilku lat. Brak baz, zapytań i liczby prac (s. 83).
  2. Ankieta internetowa z pytaniami otwartymi i zamkniętymi wśród ekspertów z sektorów infrastruktury krytycznej (s. 83–84). Nie podano liczby respondentów, terminu, pytań ani liczbowych wyników (sprawdzone w tekście).
- **Główne wyniki** (deklaracje respondentów, bez liczb):
  - DevSecOps ogranicza liczbę krytycznych podatności wykrywanych na produkcji. Dominuje trend shift-left (s. 84, rys. 1 s. 85).
  - Ciągłe skanowanie w CI/CD skraca czas identyfikacji i usunięcia luk (s. 84).
  - Cenione narzędzia: CSPM i skanery kontenerów (Aqua, Snyk) (s. 85). Przykłady konfiguracji: SonarQube w potoku i Checkov dla Terraform (s. 85–86).
  - Główna bariera to integracja z systemami legacy i SCADA, rozwiązywana przez warstwy adaptacyjne (s. 86).
  - Znaczenie mają kultura i zespoły interdyscyplinarne (s. 86), monitoring SIEM/SOAR (s. 86–87) oraz regulacje: NIS2, RODO, ISO/IEC 27001, NIST (s. 87, Tabela 1).
  - Część przeglądowa: SBOM i zalecenie CISA (s. 83), łańcuch dostaw na przykładzie SolarWinds i Equifax (s. 78), NIS2 i jej sankcje (s. 80–81).
- **Związek z RQ1–RQ3:**
  - RQ1 (skuteczność): teza, że DevSecOps zmniejsza liczbę podatności na produkcji (s. 77, 84), to dokładnie to, co mierzę w RQ1. U Janczewskiego jest to jednak deklaracja ekspertów bez liczb. Mój eksperyment daje pomiar.
  - RQ2 (koszt): kompromis między bezpieczeństwem a szybkością dostarczania wymieniony jako wyzwanie (s. 77), bez analizy.
  - RQ3 (zgodność): rola regulacji i standardów (NIS2, ISO 27001, NIST SP 800-53, CSF, OWASP Top 10, s. 80–81). Nie ma SP 800-204D ani SLSA (sprawdzone wyszukiwaniem w tekście).
- **Ograniczenia** (ocena agenta, z podstawą w tekście):
  - Brak danych z ankiety: liczebności, opisu próby, pytań i wyników liczbowych (s. 83–87). Wnioski nie dają się zweryfikować.
  - Przegląd nazwany systematycznym bez protokołu (s. 83).
  - Część źródeł to materiały branżowe: blog AmberTeam, Forward Security, Gartner, a także czasopismo IJDO (wydawca IAEME) (s. 89).
  - Teza „70–80% kodu zewnętrznego” bez źródła (s. 82).
  - Teza przypisana Rajapakse i in. (2022), że DevSecOps „znacząco przyspiesza wykrywanie i eliminację podatności” (s. 80), nie odpowiada głównym wynikom tego przeglądu, który opisuje wyzwania, rozwiązania i luki. Agent nie znalazł takiego stwierdzenia w tekście preprintu [@Rajapakse2022].
  - Przykład konfiguracji potoku (s. 85) ma składnię GitLab CI, nie GitHub Actions.
- **Gdzie użyję:**
  - 2.2 i 2.3: kontekst regulacyjny UE (NIS2) i infrastruktura krytyczna, motywacja z łańcucha dostaw (SolarWinds), SBOM. Polska perspektywa.
  - 2.5: przykład, że teza o mniejszej liczbie podatności na produkcji opiera się w literaturze na deklaracjach, a nie na pomiarach.
  - Nie cytować jako dowodu skuteczności.

### 2.5. [@Biswas2025]

Opis wyłącznie na podstawie abstraktu (Semantic Scholar, pobrany 2026-10-14) i metadanych Crossref. Pełnego tekstu brak: Collegium Da Vinci nie ma dostępu do IEEE Xplore, OpenAlex i Semantic Scholar podają status „closed”. Bez numerów stron. TODO: zweryfikować po uzyskaniu pełnego tekstu. Opracowania z pytaniami nie przygotowano, bo nie ma tekstu, na którym można by je oprzeć.

- **Jakość źródła:** praca konferencyjna IEEE (ICRITO 2025, 12th International Conference on Reliability, Infocom Technologies and Optimization), s. 1–4, opublikowana 18.09.2025 (Crossref). Jeden autor, według Crossref „DevOps Engineer, Deutsche Bank, Pune, India”, czyli praktyk, nie pracownik naukowy. Krótka praca: według kryterium z [@Rajapakse2022] (wykluczenie prac do 5 stron) nie weszłaby do tamtego przeglądu.
- **Problem** (abstrakt): zarządzanie podatnościami w obrazach kontenerów w chmurze, a zwłaszcza wyjątkami dla znanych podatności. Abstrakt wymienia nieautoryzowane zatwierdzanie wyjątków, nieefektywne procesy ręczne i brak audytowalności. Źle zarządzane wyjątki mogą narazić aplikację na naruszenia bezpieczeństwa.
- **Metoda** (abstrakt): propozycja skalowalnej, zautomatyzowanej ramy (frameworku) DevSecOps dla obrazów Docker w Google Cloud Artifact Registry. Sposób ewaluacji: TODO, z abstraktu nie wynika, czy rama była mierzona.
- **Główne wyniki** (abstrakt, deklaracje): rama tworzy i utrzymuje dynamiczne polityki wyjątków, automatyzuje przepływy CI/CD i daje rozbudowany audyt. Według autora poprawia bezpieczeństwo bez zakłócania potoku i przy minimalnym narzucie operacyjnym.
- **Związek z RQ1–RQ3:**
  - RQ1 (skuteczność): wyjątek od podatności to świadoma decyzja, żeby przepuścić podatność przez bramkę. W moim eksperymencie trzeba określić, czy i jak wariant B pozwala na wyjątki, bo wpływa to na to, co dociera na produkcję. TODO: decyzja autora przy projekcie bramek wariantu B (E07).
  - RQ2 (koszt): ręczna obsługa zgłoszeń i wyjątków to część kosztu bramek blokujących, obok fałszywych alarmów.
  - RQ3: z abstraktu nie wynika odniesienie do standardów.
- **Ograniczenia:**
  - Brak pełnego tekstu, więc wszystko powyżej to deklaracje z abstraktu.
  - Inny dostawca chmury (GCP Artifact Registry, a nie AWS ECR).
  - Bardzo krótka praca. W `_Rdzen.md` oznaczona jako pierwsza do wymiany.
- **Gdzie użyję:** 5.3 (dyskusja: obsługa wyjątków i akceptacja ryzyka jako koszt bramek; ograniczenie mojego eksperymentu, jeśli wyjątków nie modeluję). Tylko jako źródło uzupełniające, z oznaczeniem, że znam abstrakt.

## 3. Luka badawcza

Analiza prac naukowych z rdzenia literatury wskazuje, że korzyści z automatyzacji bezpieczeństwa w potokach CI/CD są w literaturze częściej deklarowane niż mierzone. Dwie prace opierają się na ankietach bez pomiarów [@Cheenepalli2025; @Janczewski2025], praca projektowo-wdrożeniowa nie ocenia skuteczności zastosowanego potoku [@Alghawli2024], a przegląd systematyczny wprost wskazuje na niedobór empirycznie zweryfikowanych rozwiązań i metryk bezpieczeństwa dla DevSecOps [@Rajapakse2022]. Żadna z prac dostępnych w pełnym tekście nie podaje, jaka część podatności zostaje zatrzymana przed wdrożeniem na produkcję ani jakim kosztem, mimo że wydłużenie czasu potoku i fałszywe alarmy skanerów są opisywane jako istotne przeszkody we wdrażaniu DevSecOps [@Rajapakse2022]. Prace te nie odnoszą się też do bezpieczeństwa łańcucha dostaw oprogramowania w ujęciu NIST SP 800-204D ani do poziomów SLSA; temat pojawia się wyłącznie jako ogólna wzmianka o SBOM [@Janczewski2025]. Jednocześnie małe i średnie organizacje wskazują złożoność techniczną i ograniczone zasoby jako główne bariery [@Cheenepalli2025], a jedyna z analizowanych prac opisująca kompletną architekturę potoku w AWS opiera się na pojedynczym skanerze i nie dostarcza danych pozwalających odtworzyć wyniki [@Alghawli2024], co pozostawia lukę w postaci lekkiego, odtwarzalnego i empirycznie ocenionego wzorca potoku DevSecOps dla małych zespołów, uwzględniającego wytyczne bezpieczeństwa łańcucha dostaw.

**Jak praca odpowiada na lukę:** pomiar skuteczności (RQ1), kosztu (RQ2) i zgodności z SP 800-204D i OWASP Top 10 CI/CD (RQ3) dla potoku aplikacji webowej w AWS, z zapisem surowych danych (`metodyka.md`, p. 2.1).

**Zastrzeżenia:**
- Lukę sformułowano na podstawie 5 prac. [@Biswas2025] znany tylko z abstraktu, dlatego nie uwzględniono go w zdaniu o braku pomiarów. Po napisaniu części teoretycznej literatura zostanie uzupełniona przez deep research (zalecenie promotora, por. E02-07). Wtedy trzeba sprawdzić, czy luka nadal jest aktualna, zwłaszcza przy pracach o bezpieczeństwie GitHub Actions i skuteczności skanerów w CI/CD.
- Cztery cytowane źródła mają stan `opracowanie`, więc tezy ogólne z akapitu wolno przenieść do tekstu pracy. Zdania z numerem strony albo liczbą autor sprawdza w źródle (`Zrodla/_Rdzen.md`, zasada 3).
