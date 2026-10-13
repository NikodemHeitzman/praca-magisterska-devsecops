# NIST SP 800-218 (SSDF 1.1): notatki i lista zadań dla potoku

Notatki z lektury [@NIST-SP800-218] do zadania E02-03. Plik ma dwie części: notatki z grup praktyk PO, PS, PW i RV oraz listę zadań SSDF, które da się zrealizować w potoku CI/CD tego projektu. Łatwiejsza wersja do nauki, w formie pytań i odpowiedzi: [`nist-ssdf-pytania.md`](nist-ssdf-pytania.md).

- **Opracował:** agent (Claude Code), 2026-10-05, na podstawie tekstu PDF (`NIST.SP.800-218.pdf`, 36 stron).
- **Strony:** podawane dwojako. „dok.” to numer wydrukowany w dokumencie, „PDF” to numer strony w przeglądarce. W części głównej PDF = dok. + 9.
- **Wersja:** cytujemy SSDF 1.1 (luty 2022). Stan sprawdzony 2026-10-05 na csrc.nist.gov:
  - SP 800-218 (1.1) ma status „Final” i nie została zastąpiona,
  - SP 800-218 Rev. 1 (SSDF 1.2) to nadal wstępny projekt (*Initial Public Draft*) z 2025-12-17, a okres uwag skończył się 2026-01-30.

  Przed złożeniem pracy trzeba sprawdzić ponownie.

---

## 0. Jak zbudowany jest dokument i co czytać

| Część | dok. | PDF | Co zawiera | Jak czytać |
|---|---|---|---|---|
| Streszczenie (*Executive Summary*) | vi | 8 | Cztery zalecenia odpowiadające grupom praktyk | Przeczytać, 1 strona |
| 1. Wprowadzenie | 1–3 | 10–12 | Po co jest SSDF, *shift left*, dlaczego bez narzędzi, podejście oparte na ryzyku, model współodpowiedzialności | Przeczytać, 3 strony |
| 2. Ramy SSDF | 4 | 13 | Cztery grupy, budowa praktyki (praktyka → zadania → przykłady → odwołania) | Przeczytać, 1 strona |
| Tabela 1 | 5–19 | 14–28 | 19 praktyk i 42 zadania z przykładami. To rdzeń dokumentu | Czytać kolumny „Practices” i „Tasks”, przykłady wybiórczo, kolumnę „References” pominąć |
| Bibliografia | 20–23 | 29–32 | Źródła mapowań | Pominąć |
| Dodatek A | 24 | 33 | Mapowanie podpunktów 4e rozporządzenia EO 14028 na zadania SSDF | Przejrzeć |
| Dodatki B i C | 25–27 | 34–36 | Skróty, historia zmian | Pominąć |

Liczbę praktyk (19) i zadań (42) policzył agent na podstawie tabeli 1. Dokument nie podaje tych liczb wprost.

---

## 1. Notatki z sekcji

### Streszczenie i rozdz. 1. Wprowadzenie (dok. vi, 1–3; PDF 8, 10–12)

- **Problem:** niewiele modeli cyklu życia oprogramowania (SDLC) opisuje bezpieczeństwo szczegółowo, więc praktyki bezpiecznego wytwarzania trzeba do nich dodać (dok. 1). SSDF to zestaw takich praktyk wysokiego poziomu, które można wpiąć w dowolny model: kaskadowy, spiralny, zwinny, DevOps.
- **Trzy cele praktyk** (dok. 1):
  1. mniej podatności w wydanym oprogramowaniu,
  2. mniejszy skutek wykorzystania podatności niewykrytych lub nienaprawionych,
  3. usuwanie przyczyn źródłowych, żeby podatności nie wracały.
- **Szersze pojęcie podatności** (dok. 1): to nie tylko błędy w kodzie, ale też słabe ustawienia konfiguracji, błędne założenia o zaufaniu i nieaktualna analiza ryzyka.
- ***Shift left*** (dok. 1): im wcześniej w SDLC zajmiemy się bezpieczeństwem, tym mniejszym kosztem osiągniemy ten sam poziom. Dokument nazywa tę zasadę krytycznie ważną dla każdego modelu SDLC.
- **SSDF nie wprowadza nowych praktyk ani terminów** (dok. 1). Zbiera praktyki z istniejących standardów i wytycznych (BSIMM, OWASP SAMM, ASVS, Microsoft SDL, SAFECode, IEC 62443 i inne).
- **DevOps jako przyszła praca** (dok. 1): dokument zapowiada, że kiedyś mogą powstać wskazówki, jak stosować SSDF w konkretnych metodykach, takich jak DevOps. *Interpretacja agenta:* tę lukę wypełnia potem SP 800-204D, co uzasadnia czytanie obu dokumentów razem.
- **Wyniki, nie narzędzia** (dok. 1–2): SSDF mówi, *co* osiągnąć, a nie *jak*. Dzięki temu pasuje do każdej organizacji, platformy, języka i łańcucha narzędzi, a organizacji, które już mają dobre praktyki, nie powinien szkodzić.
- **Wspólny język** (dok. 2): SSDF ma ułatwić rozmowę wewnątrz organizacji (deweloperzy, bezpieczeństwo, operacje) i z dostawcami. Podobnie działa NIST Cybersecurity Framework, ale praktyki SSDF nie są na niego mapowane (przypis 2).
- **Podejście oparte na ryzyku, nie lista kontrolna** (dok. 3):
  - nie wszystkie praktyki dotyczą każdego przypadku, np. ustawienia kompilatora nie mają znaczenia, gdy nic się nie kompiluje,
  - o wyborze praktyk decydują ryzyko, koszt, wykonalność i stosowalność, a dodatkowo możliwość automatyzacji,
  - praktyki, zadania i przykłady nie mają priorytetów, a podane częstotliwości są tylko poglądowe,
  - dokument wprost zastrzega, że celem SSDF nie jest lista kontrolna, tylko podstawa do planowania. **Ważne dla ewaluacji:** jeśli praca użyje SSDF do oceny potoku, trzeba to uzasadnić (patrz sekcja 4).
- **Model współodpowiedzialności** (dok. 3): przy IaaS, PaaS, SaaS, kontenerach jako usłudze i *serverless* odpowiedzialność za praktyki dzieli się między dostawcę platformy i organizację-najemcę. Najemca powinien uzgodnić z dostawcą, kto realizuje które zadanie. W projekcie dotyczy to GitHuba (runnery hostowane, magazyn atestacji) i AWS.

### Rozdz. 2. Ramy SSDF (dok. 4, PDF 13)

- **Cztery grupy praktyk:**

  | Grupa | Nazwa | Cel w jednym zdaniu |
  |---|---|---|
  | PO | *Prepare the Organization* | Ludzie, procesy i technologia są gotowe do bezpiecznego wytwarzania |
  | PS | *Protect the Software* | Wszystkie składniki oprogramowania są chronione przed manipulacją i nieuprawnionym dostępem |
  | PW | *Produce Well-Secured Software* | Wydania mają jak najmniej podatności |
  | RV | *Respond to Vulnerabilities* | Podatności, które zostały w wydaniach, są wykrywane i obsługiwane, a podobne nie powstają w przyszłości |

- **To nie są fazy.** Propozycja tematu podawała fazy PLAN, DEVELOP, BUILD, DEPLOY, OPERATE, a SSDF ich nie ma. Dokument zastrzega też, że kolejność praktyk, zadań i przykładów w tabeli nie oznacza kolejności wdrażania ani ważności (dok. 4).
- **Budowa każdej praktyki:**
  1. praktyka: nazwa, identyfikator (np. PW.7) i krótkie uzasadnienie,
  2. zadania (*tasks*): czynności, np. PW.7.2,
  3. poglądowe przykłady wdrożenia (*notional implementation examples*): żaden nie jest obowiązkowy i nie są to jedyne możliwości,
  4. odwołania (*references*) do standardów źródłowych.
- **Terminy do zdefiniowania przez organizację** (dok. 4): „sensitive data”, „qualified person”, „well-secured” oraz nazwy środowisk (development, build, staging, test, production, distribution). Dokument podkreśla, że środowiska trzeba wyliczyć, żeby je chronić i zapobiec przemieszczaniu się atakującego między nimi. **Do zrobienia w pracy:** w projekcie potoku (E07-01) wymienić i nazwać środowiska.

### Grupa PO: przygotowanie organizacji (dok. 5–9, PDF 14–18)

| Praktyka | Zadania | Najważniejsze przykłady | dok./PDF |
|---|---|---|---|
| **PO.1 Wymagania bezpieczeństwa dla wytwarzania** | PO.1.1 wymagania dla infrastruktury i procesów wytwarzania; PO.1.2 wymagania dla samego oprogramowania; PO.1.3 przekazanie wymagań dostawcom komponentów komercyjnych | Polityki zabezpieczenia infrastruktury i procesów, także dla komponentów open source; zgodność weryfikowana w kluczowych punktach SDLC, np. **bramkami** sprawdzającymi klasy błędów; przegląd wymagań co najmniej raz w roku; **proces obsługi wyjątków od wymagań** z okresowym przeglądem; od dostawców dane o pochodzeniu (*provenance*) | 5–6 / 14–15 |
| **PO.2 Role i odpowiedzialności** | PO.2.1 role; PO.2.2 szkolenia według ról; PO.2.3 zaangażowanie kierownictwa | Role w zespole, *security champions*, wyznaczony **właściciel kodu** (*code owner*) dla projektu | 6–7 / 15–16 |
| **PO.3 Łańcuch narzędzi** | PO.3.1 jakie narzędzia w każdym łańcuchu i jak je zintegrować; PO.3.2 bezpieczne wdrożenie i utrzymanie narzędzi; PO.3.3 narzędzia generują artefakty (dowody) | Automatyzacja jako sposób na powtarzalność i dowody; **potok jako kod** (*pipelines-as-code*); **odtwarzalne buildy**; aktualizacja narzędzi; **weryfikacja integralności i pochodzenia każdego narzędzia**; ślad audytowy i polityka przechowywania danych z narzędzi | 7–8 / 16–17 |
| **PO.4 Kryteria kontroli bezpieczeństwa** | PO.4.1 zdefiniować kryteria i śledzić je w SDLC; PO.4.2 zbierać i chronić informacje potrzebne do oceny kryteriów | KPI, KRI, progi ważności podatności; kryteria w *Definition of Done*; rejestrowanie akceptacji, odrzuceń i wyjątków; **automatyzacja decyzji na podstawie kryteriów**; ochrona zebranych danych przed zmianą i usunięciem | 8 / 17 |
| **PO.5 Bezpieczne środowiska wytwarzania** | PO.5.1 rozdzielić i chronić każde środowisko; PO.5.2 utwardzić stacje robocze deweloperów | MFA i dostęp warunkowy; segmentacja i oddzielenie od produkcji; **minimalny dostęp ludzi do systemów łańcucha narzędzi** (np. serwerów buildu); ciągłe monitorowanie wdrożonego oprogramowania pod kątem nowych podatności; zero trust | 8–9 / 17–18 |

Uwagi:
- PO.5 to praktyka dodana w wersji 1.1 (historia zmian, dok. 27). Odpowiada na ataki na środowiska buildu.
- **Definicje w przypisach:**
  - *provenance*, za SP 800-53: chronologia pochodzenia, rozwoju, własności, lokalizacji i zmian komponentu (przypis 5, dok. 6),
  - *artifact*: „a piece of evidence”, czyli dowód (przypis 6, dok. 7).
- **Uwaga terminologiczna:** w SSDF artefakt oznacza dowód realizacji praktyki, np. raport skanu albo log. W CI/CD artefakt to zwykle produkt buildu, np. obraz. W pracy trzeba to rozróżnić.

### Grupa PS: ochrona oprogramowania (dok. 9–10, PDF 18–19)

| Praktyka | Zadania | Najważniejsze przykłady | dok./PDF |
|---|---|---|---|
| **PS.1 Ochrona kodu przed nieuprawnionym dostępem i manipulacją** | PS.1.1 przechowywać każdą postać kodu (źródłowy, wykonywalny, konfiguracja jako kod) według zasady najmniejszych uprawnień | Repozytorium z kontrolą dostępu; historia zmian przypisana do konta; **podpisywanie commitów**; **przegląd i zatwierdzanie zmian przez właściciela kodu**; podpisywanie kodu wykonywalnego; hashe kryptograficzne | 9 / 18 |
| **PS.2 Mechanizm weryfikacji integralności wydania** | PS.2.1 udostępnić odbiorcom informacje do weryfikacji integralności | Hashe plików wydania na zabezpieczonej stronie; podpis certyfikatem uznanego urzędu, żeby system odbiorcy mógł sprawdzić podpis; przegląd procesu podpisywania (odnowienie, rotacja, unieważnienie certyfikatów) | 10 / 19 |
| **PS.3 Archiwizacja i ochrona każdego wydania** | PS.3.1 zarchiwizować pliki i dane wydania; PS.3.2 zbierać, chronić i udostępniać dane o pochodzeniu wszystkich komponentów, **np. w SBOM** | Repozytoria wydań tylko do odczytu; dane do weryfikacji i pochodzenia przechowywane osobno albo podpisane; SBOM w formacie opartym na standardach; aktualizacja SBOM przy każdej zmianie komponentu | 10 / 19 |

Uwaga: grupa PS jest najbliższa tematowi łańcucha dostaw. SBOM pojawia się w SSDF tylko tutaj, jako przykład danych o pochodzeniu (PS.3.2), a nie jako osobny wymóg.

### Grupa PW: wytwarzanie bezpiecznego oprogramowania (dok. 11–16, PDF 20–25)

| Praktyka | Zadania | Najważniejsze przykłady | dok./PDF |
|---|---|---|---|
| **PW.1 Projektowanie zgodne z wymaganiami i ryzykiem** | PW.1.1 modelowanie ryzyka (modelowanie zagrożeń, ataków, mapowanie powierzchni ataku); PW.1.2 śledzić wymagania, ryzyka i decyzje projektowe; PW.1.3 używać standardowych mechanizmów bezpieczeństwa zamiast własnych | Dokładniejsza ocena obszarów wysokiego ryzyka (dane wrażliwe, uwierzytelnianie, poświadczenia); klasyfikacja danych; **zapis uzasadnień zatwierdzonych wyjątków** i ich okresowy przegląd | 11 / 20 |
| **PW.2 Przegląd projektu** | PW.2.1 przegląd projektu przez osobę niezaangażowaną w projekt **albo** zautomatyzowane procesy w łańcuchu narzędzi | Sprawdzić, czy projekt spełnia wymagania i odpowiada na ryzyka; zapisać wyniki przeglądu jako artefakty | 12 / 21 |
| PW.3 | Wycofana, przeniesiona do PW.4 i PO.1.3 | | 12 / 21 |
| **PW.4 Ponowne użycie sprawdzonego oprogramowania** | PW.4.1 pozyskiwać i utrzymywać bezpieczne komponenty zewnętrzne; PW.4.2 tworzyć wspólne komponenty wewnętrzne; PW.4.4 **weryfikować przez cały cykl życia, że komponenty zewnętrzne spełniają wymagania** | Ocena komponentów w kontekście użycia; **dane o pochodzeniu (SBOM, analiza składu kodu źródłowego i binariów)**; zatwierdzone repozytorium komponentów; aktualizacja do nowszych wersji; **automatyczne wykrywanie znanych podatności w komponentach w łańcuchu narzędzi**; sprawdzanie, czy komponent jest utrzymywany i czy nie minął jego koniec życia (EOL); potwierdzanie integralności podpisem | 12–13 / 21–22 |
| **PW.5 Bezpieczne praktyki kodowania** | PW.5.1 stosować praktyki odpowiednie dla języka i środowiska | Walidacja wejścia i kodowanie wyjścia; unikanie niebezpiecznych funkcji; obsługa błędów; logowanie; **lintery i formatery**; samodzielny przegląd kodu przez autora jako uzupełnienie, nie zamiennik | 13 / 22 |
| **PW.6 Konfiguracja kompilacji, interpretera i buildu** | PW.6.1 narzędzia z funkcjami poprawiającymi bezpieczeństwo; PW.6.2 ustalić i stosować zatwierdzone konfiguracje | Aktualne wersje narzędzi; kontrola zmian i weryfikacja integralności narzędzi; *clean build* (ostrzeżenia traktowane jak błędy); **buildy w dedykowanym, ściśle kontrolowanym środowisku**; konfiguracje jako kod | 14 / 23 |
| **PW.7 Przegląd lub analiza kodu czytelnego dla człowieka** | PW.7.1 zdecydować, czy przegląd (człowiek), czy analiza (narzędzia), czy oba; PW.7.2 wykonać i **zapisać oraz posortować (*triage*) wszystkie znaleziska** w systemie zgłoszeń | Przegląd przez współpracownika; eksperci szukający tylnych furtek; **narzędzie analizy statycznej, którego wyniki przegląda człowiek**; automatyczne wykrywanie niebezpiecznych praktyk przy każdym wprowadzeniu kodu do repozytorium; analiza przyczyn | 14–15 / 23–24 |
| **PW.8 Testowanie kodu wykonywalnego** | PW.8.1 zdecydować, czy i jakie testy wykonywalnego kodu; PW.8.2 zaplanować, wykonać i udokumentować testy, zapisać znaleziska | Testy funkcjonalne mechanizmów bezpieczeństwa; **dynamiczne testy podatności w zautomatyzowanym zestawie testów**; testy regresji dla zgłoszonych wcześniej podatności; uwzględnienie stosu produkcyjnego; fuzzing; testy penetracyjne, jeśli są zasoby | 15 / 24 |
| **PW.9 Bezpieczne ustawienia domyślne** | PW.9.1 zdefiniować bezpieczną linię bazową ustawień; PW.9.2 wdrożyć ustawienia domyślne i je udokumentować | Testy, czy ustawienia nie osłabiają bezpieczeństwa; **sprawdzanie, czy zatwierdzona konfiguracja jest na miejscu**; dokumentacja każdego ustawienia; **konfiguracja domyślna jako kod** pod kontrolą zmian | 16 / 25 |

Uwagi:
- **PW.7 i PW.8 różnią się rodzajem kodu, nie narzędziem.** PW.7 dotyczy kodu czytelnego dla człowieka (źródła, skrypty), co w praktyce oznacza SAST i przegląd kodu. PW.8 dotyczy kodu wykonywalnego (binaria, uruchamiany kod), czyli DAST, fuzzingu i testów. Definicje są w opisach praktyk (dok. 14–15).
- **SCA formalnie należy do PW.4.4**, w przykładzie o automatycznym wykrywaniu znanych podatności w komponentach (dok. 13). SSDF nie używa tam skrótu „SCA”, ale w PW.4.1 (przykład 3) wymienia jako źródło danych o pochodzeniu SBOM, *source composition analysis* i *binary software composition analysis* (dok. 12).

### Grupa RV: reagowanie na podatności (dok. 16–18, PDF 25–27)

| Praktyka | Zadania | Najważniejsze przykłady | dok./PDF |
|---|---|---|---|
| **RV.1 Ciągłe wykrywanie i potwierdzanie podatności** | RV.1.1 zbierać informacje o podatnościach od odbiorców, użytkowników i ze źródeł publicznych, badać wiarygodne zgłoszenia; RV.1.2 przeglądać, analizować i testować kod, żeby znaleźć niewykryte wcześniej podatności; RV.1.3 polityka ujawniania i usuwania podatności | Monitorowanie baz podatności (przykład: NVD), list mailingowych, *threat intelligence*; **automatyczny przegląd danych o pochodzeniu i składzie (SBOM) pod kątem nowych podatności**; **łańcuch narzędzi wykonuje analizę i testy regularnie lub ciągle dla wszystkich wspieranych wydań**; program ujawniania podatności; zespół PSIRT; scenariusze reagowania | 16–17 / 25–26 |
| **RV.2 Ocena, priorytety i usuwanie podatności** | RV.2.1 przeanalizować każdą podatność pod kątem ryzyka; RV.2.2 zaplanować i wdrożyć odpowiedź na ryzyko | Rejestr podatności w systemie zgłoszeń; ocena ryzyka (wykorzystywalność, skutek); decyzja: naprawa albo **akceptacja lub przeniesienie ryzyka**; tymczasowe obejścia; komunikaty bezpieczeństwa (*advisories*); **dostarczanie poprawek zautomatyzowanym, zaufanym mechanizmem** | 17–18 / 26–27 |
| **RV.3 Analiza przyczyn źródłowych** | RV.3.1 ustalić przyczyny; RV.3.2 szukać wzorców w czasie; RV.3.3 przejrzeć oprogramowanie pod kątem podobnych podatności i usunąć całą klasę; RV.3.4 poprawić proces SDLC | Zapis wniosków w wiki; **dodać do łańcucha narzędzi mechanizmy automatycznie wykrywające przyszłe wystąpienia przyczyny**; zmiany praktyk SDLC | 18 / 27 |

Uwaga: RV wychodzi poza moment wydania. Potok nie kończy się na wdrożeniu: RV.1.2 (przykład 1) wprost zakłada cykliczne skanowanie wspieranych wydań przez łańcuch narzędzi.

### Dodatek A. SSDF a rozporządzenie EO 14028 (dok. 24, PDF 33)

- Rozporządzenie prezydenta USA nr 14028 (12 maja 2021 r.) w sekcji 4 poleciło NIST opracować wytyczne dla bezpieczeństwa łańcucha dostaw oprogramowania. SSDF 1.1 jest jedną z odpowiedzi.
- Tabela 2 przypisuje podpunktom 4e(i)–4e(x) zadania SSDF. Przykłady:
  - 4e(vii) (SBOM) → PS.3.2,
  - 4e(viii) (ujawnianie podatności) → RV.1.1–RV.3.3,
  - 4e(ix) (ogólna zgodność) → wszystkie praktyki, przy podejściu opartym na ryzyku.
- **Dla pracy:** wystarczy jedno zdanie w 3.1 o kontekście powstania SSDF. Treści EO 14028 nie trzeba omawiać. Treść podpunktów 4e jest poza SSDF, więc nie opisujemy ich z pamięci (TODO: zweryfikować w tekście EO, jeśli będą potrzebne).

### Historia zmian (dok. 27, PDF 36)

- Wersja 1.1 (luty 2022) zastąpiła wersję 1.0 (białą księgę z kwietnia 2020 r.).
- Główne zmiany:
  - dodano PO.5,
  - PW.3 scalono z PW.4,
  - dodano zadania PO.1.2, PO.5.1, PO.5.2, PS.3.2 i PW.1.2,
  - dodano definicje „provenance”, „artifact” i „evidence”.
- **Dla pracy:** zadania o środowiskach buildu (PO.5) i SBOM (PS.3.2) weszły do SSDF dopiero w 1.1, po EO 14028. To argument, że łańcuch dostaw jest stosunkowo nowym obszarem w ramach NIST.

---

## 2. Lista zadań SSDF realizowalnych w potoku

**Legenda:**
- **Potok:**
  - `P`: potok realizuje zadanie w całości albo w przeważającej części (job, konfiguracja, ustawienie repozytorium jako kod),
  - `Cz`: częściowo; potok dostarcza narzędzie albo dowód, ale decyzja lub proces są poza nim,
  - `O`: zadanie organizacyjne, poza potokiem,
  - `N`: nie dotyczy projektu, z uzasadnieniem.
- **Etapy** jak w liście kontrolnej SP 800-204D (`nist-800-204d.md`, sekcja 2): Platforma, PR/commit, Build, Test, Rejestr, Wdrożenie, Eksploatacja.
- **Realizacja:** propozycje agenta. Wybór narzędzi należy do E02-10 i ADR-ów.
- **204D:** czy zadanie występuje w mapowaniu dodatku A SP 800-204D (na poziomie praktyki); „nie (dod. B)” oznacza, że SP 800-204D świadomie je pomija.
- Ocena w kolumnie „Potok” to propozycja agenta do przeglądu przez autora.

| Zadanie | Treść (streszczenie) | dok./PDF | Potok | Etap | Realizacja w GitHub Actions / AWS (propozycja) | 204D |
|---|---|---|---|---|---|---|
| PO.1.1 | Wymagania bezpieczeństwa dla infrastruktury i procesów wytwarzania | 5/14 | Cz | Platforma | Spisana polityka potoku (E07-01), reguły repozytorium (*rulesets*) jako kod; ADR-y | tak |
| PO.1.2 | Wymagania bezpieczeństwa dla oprogramowania | 5/14 | Cz | PR/commit, Test | Wybrane wymagania ASVS (E02-06); weryfikacja bramkami w potoku (przykład 2); **wyjątki z przeglądem** (przykład 7) | tak |
| PO.1.3 | Przekazanie wymagań dostawcom komponentów komercyjnych | 5/14 | N | — | Brak komponentów komercyjnych | tak |
| PO.2.1 | Role i odpowiedzialności w SDLC | 6/15 | O | Platforma | Ślad w `CODEOWNERS` (przykład 7) | tak |
| PO.2.2 | Szkolenia według ról | 6/15 | N | — | Projekt jednoosobowy | tak |
| PO.2.3 | Zaangażowanie kierownictwa | 7/16 | N | — | Projekt jednoosobowy | tak |
| PO.3.1 | Jakie narzędzia w łańcuchu i jak je zintegrować | 7/16 | P | Wszystkie | Definicja workflow (potok jako kod), tabela narzędzi (E02-10), wspólny format wyników (SARIF, przykład 3) | tak |
| PO.3.2 | Bezpieczne wdrożenie i utrzymanie narzędzi | 7/16 | P | Platforma | Przypięte wersje akcji i narzędzi, Dependabot dla akcji, weryfikacja integralności narzędzi (przykład 7), odtwarzalny build (przykład 4), lint workflow (actionlint, zizmor) | tak |
| PO.3.3 | Narzędzia generują artefakty (dowody) | 7–8/16–17 | P | Wszystkie | Raporty SARIF w zakładce Security, artefakty jobów z okresem przechowywania (przykład 3), atestacje | tak |
| PO.4.1 | Kryteria kontroli bezpieczeństwa | 8/17 | Cz | Test, Rejestr | Progi bramek (np. blokada przy CRITICAL/HIGH), metryki ewaluacji. Definicja w E07-01, egzekwowanie w potoku | tak |
| PO.4.2 | Zbieranie i ochrona informacji do kryteriów | 8/17 | P | Wszystkie | Automatyczne zbieranie wyników, decyzja bramki (przykład 3), dostęp tylko dla uprawnionych, ochrona przed zmianą (przykład 4) | tak |
| PO.5.1 | Rozdzielić i chronić środowiska | 8–9/17–18 | Cz | Platforma, Wdrożenie | Efemeryczne runnery hostowane (minimalny dostęp ludzi, przykład 4), środowiska GitHuba z regułami ochrony, OIDC z osobną rolą IAM na środowisko; separacja w AWS przez Terraform | tak |
| PO.5.2 | Utwardzić stacje robocze deweloperów | 9/18 | O | — | MFA na kontach GitHub i AWS (przykład 5) | tak |
| PS.1.1 | Kod przechowywany według najmniejszych uprawnień | 9/18 | P | Platforma, PR/commit | Ochrona gałęzi, podpisane commity (przykład 3), wymagany przegląd (przykład 4, ograniczenie: jeden autor), podpis obrazu (przykład 5) | tak |
| PS.2.1 | Informacje do weryfikacji integralności dla odbiorców | 10/19 | P | Rejestr | Digest obrazu, podpis i atestacja (Sigstore, GitHub artifact attestations), weryfikacja przed wdrożeniem | tak |
| PS.3.1 | Archiwizacja plików i danych każdego wydania | 10/19 | P | Rejestr | Rejestr obrazów z niezmiennymi tagami, dostęp tylko do odczytu, atestacje i SBOM przechowywane osobno lub podpisane (przykład 2) | tak |
| PS.3.2 | Dane o pochodzeniu wszystkich komponentów (SBOM) | 10/19 | P | Build, Rejestr | SBOM (np. Syft) przy każdym buildzie, atestacja SBOM, provenance (SLSA, E02-05) | tak |
| PW.1.1 | Modelowanie ryzyka i zagrożeń | 11/20 | O | — | Jednorazowo: model zagrożeń potoku z OWASP Top 10 CI/CD (E02-04), dla aplikacji ASVS i Top 10 | nie (dod. B) |
| PW.1.2 | Śledzenie wymagań, ryzyk i decyzji | 11/20 | Cz | PR/commit | ADR-y; **wyjątki od skanerów jako kod z uzasadnieniem i datą wygaśnięcia** (przykłady 1 i 3) | nie (dod. B) |
| PW.1.3 | Standardowe mechanizmy bezpieczeństwa zamiast własnych | 11/20 | O | — | Decyzja projektowa aplikacji (uwierzytelnianie, logowanie) | nie (dod. B) |
| PW.2.1 | Przegląd projektu (osoba albo zautomatyzowane procesy) | 12/21 | Cz | PR/commit | Skan IaC (Checkov albo Trivy config) sprawdza część decyzji architektonicznych infrastruktury. Interpretacja do dyskusji | nie (dod. B) |
| PW.4.1 | Pozyskiwanie i utrzymanie bezpiecznych komponentów zewnętrznych | 12/21 | P | PR/commit, Build | Przypięte wersje zależności i obrazu bazowego, Dependabot, SBOM i SCA (przykład 3), aktualizacje (przykład 7) | nie (dod. B) |
| PW.4.2 | Wspólne komponenty wewnętrzne | 12/21 | N | — | Brak wspólnych komponentów; ewentualnie *reusable workflows* | nie (dod. B) |
| PW.4.4 | Weryfikacja komponentów zewnętrznych przez cały cykl życia | 13/22 | P | PR/commit, Build, Eksploatacja | SCA (pip-audit, Trivy), `dependency-review-action` (przykład 2), wykrywanie EOL obrazu bazowego (przykład 4), hashe zależności i weryfikacja podpisów (przykład 6) | nie (dod. B) |
| PW.5.1 | Bezpieczne praktyki kodowania | 13/22 | Cz | PR/commit | Lintery i formatery (przykład 7), reguły bezpieczeństwa języka (przykład 8, np. Bandit). Samo pisanie kodu jest poza potokiem | tak |
| PW.6.1 | Narzędzia buildu z funkcjami bezpieczeństwa | 14/23 | Cz | Build | Aktualne, przypięte wersje Dockera, BuildKit i akcji; weryfikacja integralności narzędzi. Przykłady kompilatorowe nie dotyczą Pythona | tak |
| PW.6.2 | Zatwierdzone konfiguracje narzędzi buildu | 14/23 | P | Build | hadolint jako zatwierdzona konfiguracja, ostrzeżenia blokują build (*clean build*, przykład 2), dedykowane środowisko buildu (przykład 3), konfiguracja jako kod (przykład 7) | tak |
| PW.7.1 | Decyzja: przegląd, analiza czy oba | 14/23 | Cz | PR/commit | Polityka w E07-01: SAST przy każdym PR i samodzielny przegląd autora | nie (dod. B) |
| PW.7.2 | Przegląd lub analiza kodu, zapis i sortowanie znalezisk | 14–15/23–24 | P | PR/commit | SAST (Semgrep, Bandit), skan IaC, lint workflow; wyniki w SARIF w zakładce Security (przykłady 4 i 6). Przegląd przez drugą osobę niemożliwy (jeden autor) | nie (dod. B) |
| PW.8.1 | Decyzja: czy i jakie testy kodu wykonywalnego | 15/24 | Cz | Test | Polityka w E07-01: DAST, testy mechanizmów bezpieczeństwa, skan obrazu | tak |
| PW.8.2 | Wykonanie testów i zapis znalezisk | 15/24 | P | Test | DAST (OWASP ZAP) na środowisku testowym (przykład 2), testy regresji dla znanych podatności (przykład 3), testy uwierzytelniania (przykład 1); fuzzing opcjonalnie, pentest poza potokiem | tak |
| PW.9.1 | Bezpieczna linia bazowa ustawień | 16/25 | Cz | Build, Wdrożenie | Bezpieczne ustawienia domyślne aplikacji, kontenera (użytkownik bez uprawnień root) i infrastruktury, zdefiniowane w kodzie | tak |
| PW.9.2 | Wdrożenie i udokumentowanie ustawień domyślnych | 16/25 | P | PR/commit, Eksploatacja | Konfiguracja jako kod (przykład 4), sprawdzenie zatwierdzonej konfiguracji (przykład 1: skan IaC, wykrywanie dryfu przez `terraform plan`) | tak |
| RV.1.1 | Zbieranie informacji o podatnościach | 16/25 | P | Eksploatacja | Cykliczny skan SBOM i obrazów wobec baz podatności (przykład 3), alerty Dependabot. Zgłoszenia od użytkowników: proces poza potokiem | nie (dod. B) |
| RV.1.2 | Szukanie niewykrytych wcześniej podatności | 16/25 | P | Eksploatacja | Workflow uruchamiany cyklicznie (`schedule`), który ponownie skanuje gałąź główną i wdrożony obraz (przykład 1) | nie (dod. B) |
| RV.1.3 | Polityka ujawniania i usuwania podatności | 17/26 | O | — | `SECURITY.md`, prywatne zgłaszanie podatności na GitHubie | nie (dod. B) |
| RV.2.1 | Analiza ryzyka każdej podatności | 17/26 | Cz | Test, Eksploatacja | Znaleziska trafiają do systemu zgłoszeń (zakładka Security, issues), ocena ważności ze skanera. Analiza: człowiek | nie (dod. B) |
| RV.2.2 | Odpowiedź na ryzyko | 18/27 | Cz | PR/commit, Wdrożenie | Akceptacja ryzyka jako udokumentowany wyjątek (przykład 1); poprawka zautomatyzowaną, zaufaną ścieżką: PR Dependabota → potok → wdrożenie (przykład 4) | nie (dod. B) |
| RV.3.1 | Przyczyny źródłowe | 18/27 | O | — | Poza potokiem | nie (dod. B) |
| RV.3.2 | Wzorce przyczyn w czasie | 18/27 | Cz | — | Własna reguła Semgrep dla wykrytego wzorca (przykład 2); dane z eksperymentu mogą wspierać analizę | nie (dod. B) |
| RV.3.3 | Usunięcie całej klasy podobnych podatności | 18/27 | Cz | PR/commit | Analiza i testy według PW.7 i PW.8 (przykład 1) z nową regułą | nie (dod. B) |
| RV.3.4 | Poprawa procesu SDLC | 18/27 | O | — | Poza potokiem; wnioski w ADR albo w dzienniku | nie (dod. B) |

**Podsumowanie** (42 zadania, liczenie agenta):

| Ocena | Liczba | Zadania |
|---|---|---|
| `P` | 16 | PO.3.1–3, PO.4.2, PS.1.1, PS.2.1, PS.3.1–2, PW.4.1, PW.4.4, PW.6.2, PW.7.2, PW.8.2, PW.9.2, RV.1.1–2 |
| `Cz` | 15 | PO.1.1–2, PO.4.1, PO.5.1, PW.1.2, PW.2.1, PW.5.1, PW.6.1, PW.7.1, PW.8.1, PW.9.1, RV.2.1–2, RV.3.2–3 |
| `O` | 7 | PO.2.1, PO.5.2, PW.1.1, PW.1.3, RV.1.3, RV.3.1, RV.3.4 |
| `N` | 4 | PO.1.3, PO.2.2, PO.2.3, PW.4.2 |

Wniosek wstępny: potok w całości albo częściowo realizuje 31 z 42 zadań. Grupa PS jest pokryta w całości, a z grupy PW wypadają głównie zadania projektowe (PW.1, PW.4.2). Organizacyjne zadania PO i analiza przyczyn (RV.3) zostają poza potokiem. Liczby zależą od oceny agenta i zmienią się po przeglądzie autora.

---

## 3. SSDF a SP 800-204D: rozbieżności

1. **Dodatek B SP 800-204D pomija PW.1–PW.4 i PW.7 jako praktyki „projektowe”.** Uzasadnienie (800-204D, dok. 32, PDF 41): dotyczą bezpiecznego projektowania, przeglądu projektu i ponownego użycia oprogramowania. W SSDF jednak:
   - **PW.7** to przegląd i analiza kodu, z wprost wymienionym narzędziem analizy statycznej (dok. 14, przykład 4 do PW.7.2). Przeglądem projektu jest PW.2.
   - **PW.4.4** obejmuje automatyczne wykrywanie znanych podatności w komponentach w łańcuchu narzędzi (dok. 13, przykład 2), czyli SCA.

   SP 800-204D wymaga SAST i SCA (TEST-1*, TEST-2* w `nist-800-204d.md`), ale mapuje je na PO.4 i PW.8, a nie na PW.7 i PW.4. **Wniosek do pracy:** w liście kontrolnej używać mapowania według definicji SSDF (SAST → PW.7, SCA → PW.4.4, DAST → PW.8). Rozbieżność opisać w 3.1 albo 5.3.
2. **RV.1–RV.3 uznano w SP 800-204D za politykę organizacji**, niezwiązaną z CI/CD. RV.1.2 (przykład 1) zakłada jednak, że łańcuch narzędzi cyklicznie analizuje i testuje wspierane wydania, a RV.1.1 (przykład 3) automatycznie przegląda SBOM pod kątem nowych podatności. To zadania dla potoku (cykliczny workflow). Proponowana interpretacja: polityka RV jest organizacyjna, ale jej wykonanie technicznie należy do potoku.
3. **Sekrety.** Ani SSDF, ani mapowanie w SP 800-204D nie mają osobnego zadania o sekretach. W SSDF najbliżej są PO.5.1 (ochrona środowisk, uwierzytelnianie) i PS.1.1 (najmniejsze uprawnienia do kodu). Dla skanowania sekretów (COMMIT-REQ-1) można więc przyjąć PS.1.1 jako interpretację. Do decyzji autora.
4. **Podpisy i atestacje.** SSDF daje dla nich miejsce w PS.2.1 i PS.3, a SP 800-204D w dodatku A nie mapuje ATT-2* i ATT-3* na żadną praktykę. Proponowane uzupełnienie: ATT-2* → PS.2.1, ATT-3* → PS.3.1 (przykład 2: dane do weryfikacji przechowywane osobno lub podpisane).
5. **DEPLOY-REQ-5** (otwarte z E02-02): przegląd skryptów buildu pod kątem złośliwego kodu odpowiada w SSDF zadaniu PO.3.2 (bezpieczne utrzymanie narzędzi) i częściowo PW.7.2 (eksperci szukający tylnych furtek, przykład 2). Skan obrazu przed wypchnięciem odpowiada PW.4.4 i PW.8.2. Nie rozstrzyga to, co dokładnie wpisano w tabeli 2 SP 800-204D. TODO: zweryfikować w PDF SP 800-204D, dok. 27.

---

## 4. Uwagi krytyczne (materiał do 3.1 i 5.3)

Obserwacje agenta. Autor potwierdza je przed użyciem w tekście.

1. **SSDF nie jest listą kontrolną** (dok. 3), a praca używa go jako ramy oceny. Uzasadnienie: dokument dopuszcza dokumentowanie obecnych i docelowych praktyk organizacji (dok. 2), a podejście oparte na ryzyku wymaga wyboru zadań z uzasadnieniem. Tak robi sekcja 2 tego pliku: ocena `N` i `O` z uzasadnieniem. Ewaluację warto więc ująć jako „pokrycie zadań stosowalnych”, a nie „zgodność z SSDF”.
2. **Poziom ogólności.** SSDF nie mówi, jak coś zrobić, a przykłady są poglądowe. Dwie osoby mogą różnie ocenić, czy zadanie jest spełnione. Kompensata: dla każdego zadania wskazać konkretny dowód (job, plik konfiguracji, raport).
3. **Projekt jednoosobowy.** Zadania z przeglądem przez drugą osobę (PS.1.1 przykład 4, PW.2.1, PW.7.2 przykład 1) i zadania organizacyjne (PO.2) nie dają się spełnić dosłownie. To samo ograniczenie co w SP 800-204D (PP-AUTH*).
4. **Python i kontenery a przykłady kompilatorowe.** PW.6 jest pisane z myślą o językach kompilowanych (ASLR, ostrzeżenia kompilatora). Dla Pythona i Dockera jego sens to kontrola środowiska i narzędzi buildu (Dockerfile, BuildKit, obraz bazowy).
5. **Wiek dokumentu.** Wersja 1.1 pochodzi z 2022 r. Nie zna GitHub artifact attestations ani dojrzałego SLSA. Wersja 1.2 jest od grudnia 2025 r. wstępnym projektem. Kierunku jej zmian agent nie analizował (TODO: zweryfikować, jeśli potrzebne do 3.1).
6. **Definicja „artefaktu”** w SSDF (dowód) różni się od używanej w CI/CD (produkt buildu). W tekście pracy trzeba to rozróżnić.

---

## 5. Do zrobienia

- [x] Autor czyta [`nist-ssdf-pytania.md`](nist-ssdf-pytania.md) (2026-10-06; źródło w stanie `zweryfikowane: opracowanie`).
- [ ] Autor czyta w oryginale przynajmniej dok. 1–4 (PDF 10–13), zanim napisze 3.1.
- [ ] Autor przegląda ocenę `P`/`Cz`/`O`/`N` w sekcji 2 (najpóźniej przy E07-01).
- [x] Decyzja: mapowanie listy kontrolnej według definicji SSDF (SAST → PW.7, SCA → PW.4.4, DAST → PW.8; sekcja 3 p. 1) zamiast mapowania z SP 800-204D. Decyzja autora z 2026-10-06.
- [ ] TODO: zweryfikować DEPLOY-REQ-5 w tabeli 2 SP 800-204D (dok. 27).
- [ ] Przed złożeniem pracy sprawdzić status SSDF 1.2 (SP 800-218 Rev. 1).
