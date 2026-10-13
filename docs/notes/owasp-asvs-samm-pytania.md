# OWASP Top 10:2025, ASVS 5.0.0 i SAMM 2.2.0: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia [`owasp-asvs-samm.md`](owasp-asvs-samm.md), gdzie są notatki, wybrane wymagania ASVS i materiał do katalogu podatności.

- Odpowiedzi opracował agent (Claude Code) 2026-10-09 na podstawie tekstu źródeł z oficjalnych repozytoriów OWASP (wersje w nagłówku notatek).
- Dokumenty są webowe i nie mają numeracji stron. Miejsce w źródle podano jako nazwę rozdziału (Top 10, ASVS), identyfikator wymagania ASVS (`v5.0.0-…`) albo identyfikator czynności SAMM (np. `I-SB-3-A`).
- Po przeczytaniu tego pliku źródła dostają `zweryfikowane: opracowanie` (decyzja autora z 2026-10-09). Szczegół z liczbą albo nazwą wymagania autor sprawdza w oryginale przed wpisaniem do tekstu pracy.

---

## 1. OWASP Top 10:2025

**Czym Top 10 jest, a czym nie jest?** (rozdz. `index`, „Introduction”)

Dokument świadomościowy o najważniejszych ryzykach aplikacji webowych. Nie jest standardem weryfikacji: nie daje wymagań z wynikiem „spełnia / nie spełnia”. Do tego służy ASVS. W pracy Top 10 klasyfikuje podatności (katalog, znaleziska skanerów), a nie mierzy zgodność.

**Skąd biorą się kategorie?** („Introduction”, „Methodology”)

Z dwóch źródeł. 8 kategorii wynika z danych z testów ponad 2,8 mln aplikacji. 2 kategorie wybrali praktycy w ankiecie. Ankieta istnieje, bo dane pokazują przeszłość: nowa klasa podatności trafia do narzędzi i do statystyk z opóźnieniem lat. Autorzy nazywają to podejściem „opartym na danych, ale nie ślepo” (*data-informed, not blindly data-driven*).

**Co mierzy „częstość występowania” (*incidence rate*)?** („How the categories are structured”)

Odsetek aplikacji, w których co najmniej raz znaleziono dane CWE. Liczba wystąpień w jednej aplikacji się nie liczy. Powód: narzędzia automatyczne raportują każde wystąpienie osobno, a tester ręczny zwykle raz. Bez tej zasady narzędzia automatyczne zawyżałyby wynik.

> Związek z pracą: w H2b liczymy unikalne zgłoszenia z tego samego powodu (`docs/metodyka.md`, p. 2.2).

**Dlaczego kategorie zamiast listy 10 CWE?** („How the categories are structured”)

1. Nie każde CWE występuje w każdym języku i frameworku, więc lista pojedynczych CWE byłaby częściowo niestosowalna.
2. Ta sama podatność ma często kilka CWE (np. kilka dla wstrzyknięcia poleceń albo zakodowanych haseł), a różni testerzy wybierają różne.

Kategoria grupuje do 40 CWE. Razem kategorie obejmują ok. 250 CWE (tabele kategorii sumują się do 249, wprowadzenie podaje 248).

**Co zmieniło się względem 2021?** („What's changed”)

- Dwie nowe kategorie: A03 Software Supply Chain Failures (rozszerzenie dawnej A06:2021 o cały łańcuch dostaw) i A10 Mishandling of Exceptional Conditions.
- Jedno połączenie: SSRF weszło do A01.
- A02 Security Misconfiguration awansowała z 5. na 2. miejsce. Autorzy tłumaczą to tym, że coraz więcej zachowania aplikacji zależy od konfiguracji.

**Co A03 mówi o potoku CI/CD?** (A03, „Description”, „How to prevent”)

- Wśród oznak podatności: brak regularnego skanowania zależności, brak rozdziału obowiązków (jedna osoba doprowadza kod do produkcji bez nadzoru drugiej) i potok słabiej zabezpieczony niż systemy, które buduje i wdraża.
- Zalecenia: SBOM, śledzenie zależności przechodnich, narzędzia SCA, komponenty tylko z zaufanych źródeł, utwardzenie repozytorium (ochrona gałęzi, brak sekretów), potoku (podpisane buildy, sekrety ograniczone do środowiska) i artefaktów (provenance, podpisy, promowanie artefaktu zamiast przebudowy).
- A03 ma najmniej wystąpień w danych, ale najwyższe średnie wskaźniki *exploit* i *impact* z CVE. Autorzy przypisują małą liczbę wystąpień trudności testowania tego obszaru.

**Czym A08 różni się od A03?** (A08, „Background”, „Description”)

A08 dotyczy integralności „na niższym poziomie”: zaufania do kodu i danych bez ich weryfikacji. Przykłady: potok pobierający artefakty z niezaufanego źródła bez sprawdzenia podpisu, aktualizacje bez weryfikacji integralności, niebezpieczna deserializacja (CWE-502). A03 dotyczy całego łańcucha dostaw i jego procesu.

**Które dane liczbowe z Top 10 trzeba cytować ostrożnie?** (notatki, p. 1.5)

Liczby w rozdz. „Introduction” i w opisach kategorii nie zawsze zgadzają się z tabelami kategorii, np. liczba CWE w A03 (5 lub 6) i średnia częstość A03 (5,19% lub 5,72%). W pracy podajemy liczby z tabel i piszemy, skąd są.

---

## 2. OWASP ASVS 5.0.0

**Co jest przedmiotem ASVS?** („What is the ASVS?”, „Scope”)

Wymagania bezpieczeństwa dla aplikacji webowych i usług, czyli dla produktu. ASVS wprost nie opisuje, jak budować aplikację w potoku CI/CD. Opisuje efekt, który ma osiągnąć sama aplikacja. Zaznacza też, że atakujący nie respektuje zakresu, więc ASVS trzeba stosować razem z wytycznymi dla CI/CD, hostingu i eksploatacji.

> Wniosek dla pracy: ASVS jest źródłem wymagań wobec aplikacji badawczej i odniesieniem dla katalogu podatności, a nie listą kontrolną potoku. Listą kontrolną potoku jest SP 800-204D i OWASP Top 10 CI/CD (`docs/metodyka.md`, p. 1.5).

**Jakie cechy musi mieć wymaganie ASVS?** („Scope”: Security, Verification, Requirement)

1. Ma wpływ na bezpieczeństwo: jego brak pogarsza bezpieczeństwo, a spełnienie zmniejsza prawdopodobieństwo albo skutek ryzyka.
2. Da się je zweryfikować z wynikiem „pass/fail”.
3. Jest obowiązkiem (*must*), nie zaleceniem (*should*).
4. Nie jest przywiązane do konkretnej technologii ani metody weryfikacji.

**Czym są wymagania dokumentacyjne?** („Documented security decisions”)

Wymagania, żeby organizacja udokumentowała decyzje, których ASVS nie może narzucić, bo zależą od aplikacji (np. dozwolone typy plików, reguły autoryzacji, terminy usuwania podatności w zależnościach). Są na początku rozdziału i zawsze mają powiązane wymaganie implementacyjne. Sprawdzenie dokumentacji i sprawdzenie implementacji to osobne czynności.

> Przykład w pracy: `v5.0.0-15.1.1` (udokumentowane terminy usuwania podatności w zależnościach) i `v5.0.0-15.2.1` (brak komponentów po terminie). Pierwsze uzasadnia politykę bramki SCA, drugie sprawdza ją bramka.

**Jak działają poziomy L1–L3?** („Application Security Verification Levels”)

- L1: minimum, pierwsza linia obrony przed częstymi atakami bez warunków wstępnych. Ok. 20% wymagań (70 z 345).
- L2: poziom, do którego powinna dążyć większość aplikacji. Spełnienie L2 oznacza spełnienie L1 i L2, czyli ok. 70% wymagań.
- L3: obrona w głąb i zabezpieczenia trudne we wdrożeniu, pozostałe ok. 30%.

Poziom wybiera organizacja według ryzyka i oczekiwań użytkowników. ASVS go nie narzuca.

**Co się zmieniło w poziomach względem 4.x?** („Changes Compared to v4.x”, „Rethinking Level Definitions”)

W 4.x o L1 decydowała m.in. możliwość sprawdzenia z zewnątrz (test penetracyjny „black box”). W 5.0 o poziomie decyduje stosunek redukcji ryzyka do nakładu wdrożenia. Autorzy nazywają dawne kryterium „złudzeniem testowalności”: to, że wymaganie da się przetestować, nie znaczy, że da się to zrobić automatycznie, ani że jest ważne. L1 zmalał z 128 wymagań (46%) w 4.0.3 do 70 (20%).

**Dlaczego ASVS 5.0 nie podaje CWE i co to oznacza dla katalogu?** („Moving Away from Common Weakness Enumeration”)

Twórcy zrezygnowali z bezpośredniego mapowania na CWE z powodu CWE kategorii, trudności przypisania wymagania do jednego CWE i nieprecyzyjnych mapowań w 4.x. Dla katalogu (E03-03) CWE bierzemy więc z list CWE kategorii Top 10:2025, a z ASVS wymaganie, które pozycja katalogu łamie.

**Jak cytować wymaganie ASVS?** („How to Reference ASVS Requirements”)

W formacie `v<wersja>-<rozdział>.<sekcja>.<wymaganie>`, np. `v5.0.0-1.2.5`. Bez wersji identyfikator odnosi się do najnowszej wersji, a numery mogą się zmienić między wersjami głównymi.

**Jaki poziom ASVS ma aplikacja badawcza i dlaczego?** (decyzja autora z 2026-10-09, notatki p. 5 i 7)

L1 w stosowalnych rozdziałach i wybrane wymagania L2, które odpowiadają pozycjom katalogu (np. hashowanie haseł `11.4.2`, zarządzanie sekretami `13.3.1`, tryb debug `13.4.2`). Pełne L2 wymagałoby m.in. całego rozdziału o logowaniu (V16), co przekracza cel aplikacji badawczej. ASVS sam zachęca do okrojonej wersji standardu bez rozdziałów niestosowalnych (OAuth, WebRTC), byle zachować identyfikatory wymagań („Flexibility with the ASVS”).

---

## 3. OWASP SAMM 2.2.0

**Czym SAMM różni się od ASVS?** (`model/`)

SAMM ocenia dojrzałość praktyk bezpieczeństwa w organizacji (proces, ludzi, metryki). ASVS stawia wymagania aplikacji. SAMM odpowiada na pytanie, jak dobrze organizacja wytwarza bezpieczne oprogramowanie, a ASVS, czy konkretna aplikacja jest zabezpieczona.

**Jak zbudowany jest model?** (`business_functions/`, `security_practices/`, `streams/`, `maturity_levels/`)

5 funkcji biznesowych (Governance, Design, Implementation, Verification, Operations), w każdej 3 praktyki, razem 15. Każda praktyka ma 2 strumienie i 3 poziomy dojrzałości, a na każdym poziomie jedną czynność w każdym strumieniu.

**Co oznaczają poziomy dojrzałości?** (`maturity_levels/1–3`)

1. Czynność wykonywana doraźnie, na zasadzie „najlepszego wysiłku”.
2. Spójny, powtarzalny proces, na którym można polegać.
3. Maksymalna skuteczność przez ciągłe doskonalenie na podstawie informacji zwrotnej.

**Które praktyki SAMM realizuje potok DevSecOps?** (notatki, p. 3.2)

Głównie Implementation (Secure Build, Secure Deployment) i Verification (Security Testing):

- `I-SB-2-A`: automatyczne budowanie z wbudowanymi narzędziami bezpieczeństwa, np. SAST.
- `I-SB-3-A`: zdefiniowane kryteria bezpieczeństwa i przerwanie buildu po ich przekroczeniu. Wyjątki tylko zatwierdzone jawnie i zalogowane z uzasadnieniem. Odpowiada to bramkom blokującym wariantu B.
- `I-SB-1-B`: spis zależności (BOM) i sprawdzanie znanych podatności.
- `I-SD-3-A`: weryfikacja podpisów artefaktów przed wdrożeniem. Artefaktu bez ważnego podpisu się nie wdraża.
- `I-SD-1-B`: programiści nie mają dostępu do sekretów produkcyjnych, a sekrety nie leżą jawnie w repozytorium.
- `V-ST-3-A`: narzędzia testujące uruchamiane automatycznie w procesie budowania i wdrażania, wyniki przeglądane na bieżąco.

**Czy praca ocenia potok według SAMM?** (notatki, p. 3.2)

Nie jako pomiar. Poziomy SAMM opisują organizację, a jednoosobowy projekt realizuje tylko techniczną część czynności (bez np. SLA czy raportowania kierownictwu). SAMM służy jako tło w 3.3 i do opisu w 5.3, a nie jako pytanie badawcze.

**Czym wersja 2.2.0 różni się od 2.1.0?** (porównanie tagów w repozytorium `owaspsamm/core`)

Tylko redakcyjnie: 117 zmienionych plików, żaden nie doszedł ani nie zniknął, struktura modelu bez zmian. Wydanie nie ma opisu zmian.

---

## 4. Pytania na obronę

**„Tytuł mówi o zgodności z OWASP. Z którym dokumentem OWASP potok jest zgodny?”**

„OWASP” w tytule to rodzina dokumentów o różnych rolach (notatki, p. 4). Zgodność potoku oceniamy względem OWASP Top 10 CI/CD Security Risks razem z SP 800-204D. Wymagania wobec aplikacji bierzemy z ASVS. Top 10:2025 klasyfikuje podatności z katalogu i znaleziska skanerów. SAMM daje tło procesowe.

**„Dlaczego aplikacja nie spełnia pełnego ASVS L2?”**

Bo to aplikacja badawcza, a nie produkcyjna. Jej rola to nośnik kontrolowanych podatności. ASVS sam pozwala wybrać poziom według ryzyka i pominąć rozdziały niestosowalne. Wybrane wymagania L2 to te, które łamią pozycje katalogu, więc są w pracy sprawdzane.

**„Skąd CWE w katalogu, skoro ASVS 5.0 ich nie podaje?”**

Z list CWE przypisanych do kategorii Top 10:2025. To mapowanie publikuje sam OWASP, więc pozycja katalogu ma kategorię i CWE z jednego spójnego źródła. Pozycje potoku i infrastruktury, które nie mieszczą się w Top 10 aplikacji, klasyfikujemy dodatkowo według OWASP Top 10 CI/CD.

**„Top 10 opiera się na danych od dostawców narzędzi. Czy to nie przekłada się na wyniki pracy?”**

Częściowo tak. Dane pochodzą m.in. od producentów skanerów, więc kategorie łatwe do testowania automatycznego są w nich lepiej widoczne. Autorzy Top 10 sami to przyznają i dlatego dwie kategorie wybiera ankieta. W pracy katalog celowo zawiera pozycje poza zasięgiem narzędzi (E03-03), żeby wynik nie premiował tylko tego, co skanery już umieją.
