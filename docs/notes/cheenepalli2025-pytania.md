# Cheenepalli i in. (2025), DevSecOps w MŚP: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia kartę pracy w [`literature-matrix.md`](../literature-matrix.md), p. 2.2.

- Odpowiedzi opracował agent (Claude Code) na podstawie tekstu pracy [@Cheenepalli2025], 2026-10-14. Przykłady „w naszym projekcie” i oceny oznaczone „ocena agenta” to propozycje agenta, a nie treść pracy.
- Tekst: preprint arXiv:2503.22612v1 (28.03.2025), plik `Zrodla/pdf/Cheenepalli2025-preprint-arXiv2503.22612.pdf` w vaulcie. Preprint nie ma numerów na stronach, więc podaję numer w przeglądarce PDF (s. N). Wersja IEEE (s. 1–6) ma własną numerację, którą trzeba sprawdzić przed cytowaniem strony.
- Praca jest krótka: 5 stron treści i strona bibliografii.

---

## Najpierw w pięciu zdaniach

1. To **ankieta wśród 405 osób z małych i średnich firm (MŚP)**, które mają doświadczenie z DevSecOps.
2. Większość deklaruje wdrożenie DevSecOps (68%), ale **przy każdym commicie skanuje tylko 12%**, a kontenery zabezpiecza 34%.
3. Główne bariery to **złożoność techniczna (41%), opór kulturowy (38%) i brak zasobów (35%)**.
4. Autorzy dają **11 ogólnych zaleceń**, m.in. automatyzację skanów w CI/CD, wdrażanie etapami i tanie narzędzia open source.
5. W mojej pracy to **motywacja „lekkiego” potoku dla małych zespołów** (2.5) i tło dla pomiarów kosztu (5.3). Słabość: same deklaracje, bez pomiarów.

---

## 1. Problem i pytania (s. 1)

**Jaki problem badają autorzy?**

CI/CD przyspiesza wydania, ale często pomija bezpieczeństwo. MŚP mają mniej zasobów, wiedzy i infrastruktury niż duże firmy, więc trudniej im wdrożyć DevSecOps (s. 1).

**Jakie trzy pytania badawcze stawiają?** (s. 1)

1. Jakie wyzwania napotykają MŚP przy wdrażaniu DevSecOps?
2. Jakie strategie oparte na danych i opiniach ekspertów pomagają je wdrożyć?
3. Jakie są dobre praktyki wdrażania DevSecOps w MŚP?

---

## 2. Metoda (s. 1–2)

**Na jakich teoriach oparto ankietę?** (s. 1, Tabela I s. 2)

- **TAM (Technology Acceptance Model):** czy ludzie przyjmują technologię zależy od tego, czy uważają ją za użyteczną i łatwą w użyciu.
- **DOI (Diffusion of Innovations):** jak nowe praktyki rozchodzą się w organizacjach, przez jakie etapy i z jakimi barierami.

Każde pytanie ankiety przypisano do jednej z tych teorii (Tabela I, s. 2).

**Skąd byli respondenci?** (s. 2)

Z komercyjnego panelu badawczego Centiment. Warunek: praca w MŚP, doświadczenie z DevSecOps i udział w wytwarzaniu, utrzymaniu albo bezpieczeństwie oprogramowania. Osoby bez doświadczenia z DevSecOps wykluczono. Badanie miało zgodę komisji etycznej uczelni (s. 2).

**Kim byli respondenci?** (s. 3)

Programiści 35%, bezpieczeństwo 27%, operacje 22%, kierownictwo 16%. 49% ma ponad 5 lat doświadczenia, 81% ponad 3 lata.

**Jak analizowano wyniki?** (ocena agenta)

Wyniki podano jako odsetki odpowiedzi. W tekście nie ma testów statystycznych ani opisu analizy jakościowej, choć praca zapowiada „metody mieszane” (s. 1).

---

## 3. Wyniki (s. 2–4)

**Jak daleko MŚP są z wdrożeniem?** (Tabela II, s. 2)

68% w pełni wdrożyło, 22% wdraża, 10% nie zaczęło.

**Jakie narzędzia bezpieczeństwa są w potokach CI/CD?** (s. 3)

Bezpieczeństwo API 63%, SCA (analiza zależności) 62%, bezpieczeństwo IaC 61%, SAST 60%. Bezpieczeństwo kontenerów tylko 34%, co autorzy nazywają luką.

*W naszym projekcie:* potok skanuje także obraz kontenera (Trivy, hadolint), czyli właśnie obszar, który w MŚP jest najrzadszy.

**Co przeszkadza we wdrożeniu?** (s. 3, Tabela IV)

- złożoność techniczna 41%,
- opór kulturowy 38%,
- ograniczone zasoby 35%,
- 31% zgłasza umiarkowaną trudność wpięcia bezpieczeństwa w CI/CD (s. 3; na s. 4 podano 33%).

**Jak często MŚP skanują kod?** (s. 4)

Co tydzień 37%, codziennie 24%, przy każdym commicie tylko 12%.

*W naszym projekcie:* skany przy każdym pull requeście. Według tej ankiety to praktyka rzadka w MŚP, więc warto zmierzyć, ile kosztuje (RQ2).

**Jak firmy mierzą skuteczność DevSecOps?** (Tabela III, s. 3)

67% uważa DevSecOps za bardzo skuteczny. Używane metryki: częstotliwość skanów 53%, liczba wykrytych podatności 46%, czas naprawy 45%, spadek incydentów 44%.

**Jaką rolę gra kierownictwo?** (Tabela IV, s. 3; s. 4)

73% mówi, że kierownictwo traktuje bezpieczeństwo jako wysoki priorytet. Gotowość technologiczna (66%) i wsparcie kierownictwa (43%) to czynniki sprzyjające wdrożeniu.

**Czego firmy chcą na przyszłość?** (s. 4)

Więcej szkoleń (58%), lepszych narzędzi (55%), wsparcia kierownictwa (52%), budżetu (49%). Oczekują też dużego wpływu AI i uczenia maszynowego w ciągu 2–3 lat.

---

## 4. Zalecenia (rozdz. V, s. 5)

**Które z 11 zaleceń są najbliższe mojemu potokowi?**

- **Zal. 2:** integracja narzędzi bezpieczeństwa z IDE, repozytorium i CI/CD oraz automatyzacja częstych skanów.
- **Zal. 6:** kontrole zgodności wbudowane w przepływ pracy, od początku.
- **Zal. 7:** wdrażanie etapami, żeby nie przeciążyć zasobów, i wybór tanich, otwartoźródłowych narzędzi.
- **Zal. 9:** regularny audyt szablonów IaC i automatyczne egzekwowanie polityk.
- **Zal. 10:** KPI, np. częstotliwość skanów i tempo naprawy podatności.

Pozostałe zalecenia dotyczą kultury, szkoleń, kierownictwa i AI.

*W naszym projekcie:* potok realizuje zalecenia 2, 7 (wyłącznie narzędzia open source) i 9 (Checkov, Trivy dla Terraform). Zalecenie 6 realizuje lista kontrolna z SP 800-204D.

---

## 5. Ograniczenia (rozdz. VI, s. 5–6, i ocena agenta)

**Jakie ograniczenia podają autorzy?** (s. 5–6)

- Szeroki zakres wielkości firm, 1–5000 pracowników, co utrudnia uogólnienie.
- **Dane deklaratywne**, które mogą zawyżać albo zaniżać poziom wdrożenia i skuteczności. Autorzy zalecają walidację empiryczną: studia przypadków, wywiady, obserwację.
- Brak analizy według branż i brak pogłębienia tematu AI.

**Co jeszcze widzę?** (ocena agenta)

- **Dobór próby.** Do ankiety dopuszczono tylko osoby z doświadczeniem w DevSecOps (s. 2), więc 68% „pełnych wdrożeń” nie opisuje wszystkich MŚP.
- **Brak stopy odpowiedzi** mimo nagłówka „Survey Distribution and Response Rate” (s. 2).
- **Brak testów statystycznych.** Zdanie o „istotnie lepszej” integracji przy zaangażowanym kierownictwie (s. 4) nie jest poparte testem.
- **Definicja MŚP.** 1–5000 pracowników to znacznie więcej niż w definicji UE. TODO: zweryfikować definicję UE ze źródłem przed użyciem.
- **Brak łańcucha dostaw.** W tekście nie ma NIST, OWASP, SBOM, SLSA, GitHub ani fałszywych alarmów.
- Autorzy zaznaczają, że przy redakcji tekstu korzystali z Grammarly i ChatGPT (s. 6).

---

## 6. Pytania, które może zadać recenzent

**„Dlaczego cytujesz ankietę, skoro sam robisz eksperyment?”**

Ankieta pokazuje, co MŚP *deklarują*: barierą jest złożoność i brak zasobów, a skanowanie przy każdym commicie jest rzadkie. Mój eksperyment *mierzy*, ile taki potok kosztuje i co wykrywa. Autorzy sami wskazują walidację empiryczną jako potrzebny następny krok (s. 6).

**„Czy 68% wdrożeń w MŚP nie przeczy tezie, że brakuje lekkich rozwiązań?”**

Nie. Próba obejmowała tylko osoby z doświadczeniem w DevSecOps, a „wdrożenie” jest deklaracją. Te same dane pokazują, że per commit skanuje 12%, a kontenery zabezpiecza 34%. Dalszymi barierami są złożoność i zasoby.

**„Co z tej pracy bierzesz do swojego potoku?”**

Nacisk na narzędzia open source i wdrażanie etapami (zal. 7), automatyczne skany w CI/CD (zal. 2) i skanowanie IaC (zal. 9). Do tego metryki z Tabeli III (częstotliwość skanów, liczba wykrytych podatności) jako punkt odniesienia dla moich metryk.
