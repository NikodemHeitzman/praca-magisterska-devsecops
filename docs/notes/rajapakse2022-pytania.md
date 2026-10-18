# Rajapakse i in. (2022), wyzwania i rozwiązania DevSecOps: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia kartę pracy w [`literature-matrix.md`](../literature-matrix.md), p. 2.1.

- Odpowiedzi opracował agent (Claude Code) na podstawie tekstu pracy [@Rajapakse2022], 2026-10-14. Przykłady „w naszym projekcie” to propozycje agenta, a nie treść pracy.
- Tekst: preprint arXiv:2103.08266v2 (29.07.2021), plik `Zrodla/pdf/Rajapakse2022-preprint-arXiv2103.08266v2.pdf` w vaulcie. Numer strony na dole strony = numer w przeglądarce PDF, więc podaję jeden numer (s. N). Wersja w czasopiśmie ma inną numerację. Przed cytowaniem strony sprawdź ją w wersji wydawcy.
- Część merytoryczna to s. 1–23, dalej bibliografia i lista 54 prac.

---

## Najpierw w pięciu zdaniach

1. To **przegląd systematyczny 54 recenzowanych prac** o tym, co przeszkadza we wdrażaniu DevSecOps i co literatura proponuje w zamian.
2. Wynik to **21 wyzwań i 31 rozwiązań** w czterech tematach: narzędzia, praktyki, infrastruktura, ludzie. Najwięcej prac dotyczy narzędzi.
3. Główny konflikt to **szybkość wydań kontra bezpieczeństwo**: skanery są wolne i dają fałszywe alarmy, a wiele praktyk bezpieczeństwa jest ręcznych.
4. Autorzy wskazują **luki**: brak empirycznie zweryfikowanych narzędzi i metryk oraz brak zgody, co i gdzie umieścić w potoku.
5. W mojej pracy to **rama dla 2.1 i 2.5** i punkt odniesienia w 5.3. Moja praca odpowiada na część tych luk pomiarem na jednym potoku.

---

## 1. Po co jest ta praca (abstrakt, rozdz. 1; s. 1–2)

**Jaki problem badają autorzy?**

DevOps przyspieszył wydawanie oprogramowania, ale tradycyjne testy bezpieczeństwa są ręczne albo czasochłonne, np. przegląd kodu czy DAST. Wstawione bez zmian do DevOps spowalniałyby wdrożenia (s. 1). DevSecOps ma pogodzić szybkość z bezpieczeństwem, ale jego wdrożenie w praktyce sprawia trudność (s. 1).

**Jakie trzy pytania badawcze stawiają?** (Tabela 2, s. 5)

1. Jakie wyzwania przy wdrażaniu DevSecOps opisuje literatura?
2. Jakie rozwiązania proponuje?
3. Gdzie są luki do dalszych badań i braki w narzędziach albo ramach?

**Czym ta praca różni się od wcześniejszych przeglądów?** (rozdz. 2.4, s. 3–4)

Wcześniejsze przeglądy obejmowały mało prac, np. 5 recenzowanych w 2016 r., albo opierały się na literaturze szarej. Autorzy dołączyli też prace o bezpieczeństwie praktyk ciągłych (CI, CDE, CD), a nie tylko te ze słowem „DevSecOps”. Dzięki temu znaleźli więcej prac (s. 4).

---

## 2. Definicje (rozdz. 2; s. 2–3)

**Czym różnią się CI, Continuous Delivery i Continuous Deployment?** (s. 2)

- **CI:** programiści często, zwykle codziennie, scalają zmiany z główną gałęzią, a automatyczny build i testy je sprawdzają.
- **Continuous Delivery (CDE):** oprogramowanie jest zawsze gotowe do wdrożenia, ale o wydaniu na produkcję decyduje człowiek.
- **Continuous Deployment (CD):** zmiana, która przejdzie wszystkie bramki jakości, trafia na produkcję automatycznie, bez udziału człowieka.

*W naszym projekcie:* trzeba w 2.1 jasno powiedzieć, który model realizuje potok. Wariant z ręcznym zatwierdzeniem wdrożenia to CDE, nie CD.

**Jak autorzy definiują DevSecOps?** (s. 3)

Jako włączenie zasad i praktyk bezpieczeństwa do DevOps przez lepszą komunikację, współpracę i integrację zespołów deweloperskich i operacyjnych z zespołem bezpieczeństwa. Warianty nazwy (SecDevOps, DevOpsSec) oznaczają to samo: bezpieczeństwo przez cały cykl DevOps.

---

## 3. Metoda (rozdz. 3; s. 4–7)

**Jak szukali prac?** (s. 4–5)

- Według wytycznych Kitchenham i Chartersa.
- Jedna baza indeksująca (Scopus) i dwie biblioteki wydawców (IEEE Xplore, ACM DL), wyszukiwanie w czerwcu 2020.
- Zapytanie łączyło nazwy DevSecOps z „secur*” i nazwami praktyk ciągłych.

**Ile prac przeszło przez kolejne etapy?** (s. 5–6, rys. 3 s. 7)

460 znalezionych → 283 po usunięciu duplikatów → 62 po kryteriach włączenia i wykluczenia → 48 po ocenie jakości → 54 po snowballingu (+4 prace z cytowań, +2 z list innych przeglądów).

**Co wykluczyli?** (s. 5)

Prace nierecenzowane, przeglądy (prace wtórne) i prace krótkie, do 5 stron włącznie.

*Uwaga dla mnie:* według tego kryterium [@Biswas2025] (4 strony) zostałby z przeglądu wykluczony, a [@Cheenepalli2025] (6 stron) przeszedłby tuż nad progiem. Autorzy przeglądu przyjęli więc, że bardzo krótkie prace mają mniejszą wagę dowodową. To warto pamiętać przy ocenie tych dwóch prac.

**Jak analizowali dane?** (s. 6)

Analiza tematyczna według Brauna i Clarke w programie NVivo: kodowanie otwarte, potem grupowanie kodów w tematy. Pierwotny temat „Technologia” podzielono na „Narzędzia” i „Infrastrukturę”, bo był niespójny.

---

## 4. Wyzwania (RQ1 autorów, rozdz. 4.3; s. 8–13, Tabela 3 s. 9)

**Jakie są cztery tematy i ile w nich wyzwań?** (s. 7, Tabela 3 s. 9)

Narzędzia (Ch1–Ch9), praktyki (Ch10–Ch14), infrastruktura (Ch15–Ch17), ludzie (Ch18–Ch21). Razem 21.

**Co jest nie tak ze skanerami SAST?** (Ch4, s. 10)

Dwa problemy:
1. Dużo fałszywych alarmów, których ręczna ocena zabiera czas i wymaga osób, które umieją je rozpoznać.
2. Długi czas skanowania i duże zużycie zasobów, zwłaszcza przy skanie całego kodu. Przy częstych, małych commitach skan każdej zmiany bywa niepraktyczny.

*W naszym projekcie:* to uzasadnienie RQ2, gdzie mierzymy narzut czasu i udział fałszywych alarmów.

**A ze skanerami dynamicznymi (DAST)?** (Ch5, s. 10)

Wymagają zbudowanej, zainstalowanej i skonfigurowanej aplikacji. Ich ustawienie i uruchamianie wymaga ręcznej pracy, trwają długo i mają ograniczony zakres scenariuszy.

**Jakie zagrożenia dotyczą samego potoku i jego narzędzi?** (Ch6–Ch9, s. 10–11)

- Obrazy kontenerów z publicznych źródeł mogą być zmodyfikowane i zawierać podatności (Ch6).
- Systemy CI są bardziej narażone, bo uruchamiają kod dostarczony przez użytkowników (Ch7).
- Skrypty IaC zawierają „zapachy bezpieczeństwa” (Ch8).
- Potok CD otwiera dodatkowe powierzchnie ataku, a przejęty lub źle skonfigurowany potok może wprowadzić złośliwy kod na produkcję. Problemem jest też ten sam poziom dostępu do potoku dla wszystkich członków zespołu (Ch9).

*W naszym projekcie:* to tło dla OWASP Top 10 CI/CD (rozdz. 2.2), choć sama praca nie używa tej klasyfikacji.

**Na czym polega konflikt szybkości i bezpieczeństwa?** (Ch14, s. 12)

Testy bezpieczeństwa, np. testy penetracyjne, wymagają pracy człowieka, więc są czasochłonne. Szybkie wydania nie sprzyjają dokładnym testom. Programiści wybierają między szybkością a bezpieczeństwem, a niektóre organizacje uważają je za niezgodne.

**Co mówi praca o włączaniu bezpieczeństwa do potoku?** (Ch13, s. 12)

Ciągła ocena podatności rzadko jest stosowana w praktyce. Brakuje zgody, czyli ustandaryzowanej metodyki, które środki bezpieczeństwa i w którym miejscu potoku umieścić.

---

## 5. Rozwiązania (RQ2 autorów, rozdz. 4.4; s. 13–19, Tabela 4 s. 14–15)

**Które rozwiązania są najbliższe mojemu potokowi?**

- **S3, dobre praktyki użycia narzędzi** (s. 15): konfiguracja skanera do kontekstu zamiast domyślnej, wykluczenie kodu nieprodukcyjnego ze skanowania, unikanie zdublowanych sprawdzeń, długie skany SAST w równoległym potoku.
- **S6, ciągła ocena podatności** (s. 15): sprawdzanie przy każdym commicie i łączenie kilku narzędzi statycznych i dynamicznych, żeby ograniczyć słabości pojedynczego narzędzia, np. fałszywe alarmy.
- **S9, analiza statyczna IaC** (s. 16): narzędzie SLIC do wykrywania „zapachów bezpieczeństwa” w skryptach IaC. *W naszym projekcie:* ten sam cel realizują Checkov i Trivy.
- **S16, przesunięcie w lewo** (s. 17): bezpieczeństwo od wczesnych etapów, żeby unikać drogich poprawek później.
- **S17, ciągła ocena bezpieczeństwa** (s. 17): bezpieczeństwo na wszystkich etapach, także po wdrożeniu, np. przez ciągły monitoring.
- **S20, ścisłe zarządzanie dostępem** (s. 17): dostęp według potrzeb (najmniejsze uprawnienia) i automatyczne zmiany na produkcji zamiast ręcznego dostępu programistów. *W naszym projekcie:* OIDC i minimalne uprawnienia ról AWS.

**Jak autorzy proponują wyważyć szybkość i bezpieczeństwo w praktyce?** (rozdz. 4.5, s. 19)

Zestawić potok od początku projektu, używać narzędzi przyjaznych szybkim wdrożeniom (proponują IAST), a długie skany SAST puszczać równolegle, żeby główny potok szedł dalej. Alternatywą jest testowanie bezpieczeństwa jako usługa.

---

## 6. Luki badawcze (RQ3 autorów, rozdz. 4.6; s. 19–22)

**Jakie luki wskazują autorzy?** (s. 21–22)

1. Narzędzia testowania bezpieczeństwa dopasowane do szybkich cykli CI/CD. Mało jest empirycznie zweryfikowanych rozwiązań do ciągłej oceny podatności (4.6.1, s. 21).
2. Testowanie bezpieczeństwa jako usługa, np. DAST (4.6.2, s. 21).
3. Narzędzia projektowane dla programistów, a nie dla ekspertów bezpieczeństwa (4.6.3, s. 21).
4. Ciągłe wykrywanie podatności i zarządzanie nimi. Programiści potrzebują konkretnych wskazówek, jak wyważyć szybkość wydań i bezpieczeństwo (4.6.4, s. 21).
5. Zgoda co do przesunięcia w lewo: co przesuwać, co automatyzować i do którego miejsca potoku (4.6.5, s. 21).
6. Empirycznie zweryfikowane metryki bezpieczeństwa dla DevSecOps (4.6.6, s. 22).
7. Jasne role bezpieczeństwa w zespole (4.6.7, s. 22).
8. Badania socjotechniczne o ludziach (4.6.8, s. 22).
9. Empirycznie zweryfikowane ramy dla trudnych środowisk (4.6.9, s. 22).

**Które z nich dotyczą mojej pracy?**

Luki 1, 4, 5 i 6. Moja praca:
- mierzy na jednym potoku, ile podatności zatrzymują skanery (RQ1),
- mierzy, ile to kosztuje w czasie i fałszywych alarmach (RQ2),
- opiera wybór „co i gdzie w potoku” na SP 800-204D i OWASP (RQ3).

Nie twierdzę, że zamykam te luki. Daję jeden opisany, odtwarzalny przypadek.

---

## 7. Ograniczenia pracy (rozdz. 5 i ocena agenta; s. 5, 22)

**Jakie ograniczenia podają sami autorzy?** (s. 22)

- Mogli pominąć prace, bo szukali w trzech źródłach.
- Selekcja i ekstrakcja danych mogła być stronnicza. Ograniczali to protokołem i przeglądem przez innych autorów.
- Tendencja do publikowania wyników pozytywnych. Autorzy uważają ją za umiarkowane zagrożenie, bo zebrali wiele opisów problemów.

**Jakie ograniczenia widzę z perspektywy mojej pracy?** (ocena agenta)

- **Wiek literatury.** Przegląd kończy się w czerwcu 2020 (s. 5), czyli przed SolarWinds, SP 800-204D (2024) i SLSA. W tekście nie ma słów *supply chain*, SBOM, SLSA ani GitHub. To samo w sobie argument, że temat łańcucha dostaw w potoku jest w literaturze naukowej nowszy i słabiej opisany.
- **Brak pomiarów.** To synteza cudzych prac. Liczby (np. wydłużenie cyklu przez skaner, s. 8) pochodzą z pojedynczych prac pierwotnych [P28], a nie z pomiaru autorów.

---

## 8. Pytania, które może zadać recenzent

**„Skoro przegląd jest z 2020 r., czy nie jest przestarzały?”**

Opisane wyzwania nadal obowiązują: fałszywe alarmy, czas skanów, konflikt szybkości i bezpieczeństwa. Brakuje w nim natomiast łańcucha dostaw. Dlatego zestawiam go z SP 800-204D (2024) i OWASP Top 10 CI/CD (2022), które ten obszar pokrywają.

**„Dlaczego w ogóle mierzysz fałszywe alarmy?”**

Bo przegląd wskazuje je jako jedno z głównych wyzwań przy SAST w szybkich cyklach wydań (Ch4, s. 10). Wymienia też brak empirycznie zweryfikowanych metryk (s. 22).

**„Co Twoja praca dodaje do tego przeglądu?”**

Pomiar na konkretnym, odtwarzalnym potoku zamiast syntezy. Do tego obszar łańcucha dostaw, którego przegląd nie obejmuje.
