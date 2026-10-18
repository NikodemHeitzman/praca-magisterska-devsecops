# Janczewski (2025), DevSecOps w chmurze dla infrastruktury krytycznej: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia kartę pracy w [`literature-matrix.md`](../literature-matrix.md), p. 2.4.

- Odpowiedzi opracował agent (Claude Code) na podstawie tekstu pracy [@Janczewski2025], 2026-10-14. Przykłady „w naszym projekcie” i oceny oznaczone „ocena agenta” to propozycje agenta, a nie treść pracy.
- Tekst: wersja opublikowana, plik `Zrodla/pdf/Janczewski2025.pdf` w vaulcie. Strony podaję według czasopisma (s. 77–90). Numer w przeglądarce PDF = numer strony − 76, np. s. 83 to PDF 7.
- Artykuł jest po polsku, więc w pracy możesz cytować go bez tłumaczenia.

---

## Najpierw w pięciu zdaniach

1. To **polski artykuł** o wdrażaniu DevSecOps w chmurze w sektorach infrastruktury krytycznej (energetyka, finanse, zdrowie, administracja).
2. Metoda to **przegląd literatury i ankieta wśród ekspertów**, ale artykuł nie podaje liczby respondentów ani żadnych wyników liczbowych.
3. Respondenci **deklarują**, że automatyzacja SAST, DAST i SCA w CI/CD zmniejsza liczbę podatności na produkcji i skraca czas reakcji.
4. Główne bariery to **systemy legacy i SCADA**. Ważną rolę grają **regulacje**: NIS2, RODO, ISO 27001, NIST.
5. W mojej pracy przydaje się jako **kontekst regulacyjny UE i polska perspektywa** (2.2, 2.3). Nie nadaje się na dowód skuteczności.

---

## 1. Problem i cel (rozdz. 1; s. 77–79)

**Co jest celem artykułu?** (s. 77, 79)

Analiza wdrażania DevSecOps w środowiskach chmurowych infrastruktury krytycznej, ze szczególnym naciskiem na CI/CD, narzędzia SAST, DAST, SCA i IAST, automatyzację testów i SBOM.

**Jakimi incydentami autor motywuje temat?** (s. 78)

- **Equifax (2017):** niezałatana podatność w Apache Struts (CVE-2017-5638) pozwoliła na wyciek danych ponad 140 mln osób. Łatka była dostępna od marca, a system nie był załatany do maja.
- **SolarWinds (2020):** złośliwy kod wstrzyknięty do aktualizacji i rozesłany do tysięcy klientów. To przykład ataku przez łańcuch dostaw.

*W naszym projekcie:* SolarWinds to też motywacja w rozdz. 1. Opis incydentu warto jednak oprzeć na źródle pierwotnym (zadanie z incydentami w E02), a nie na tym artykule.

**Co autor rozumie przez „shift-left” i „shift-right”?** (s. 78)

Shift-left to wcześniejsze włączanie bezpieczeństwa w cykl życia oprogramowania. Tradycyjne testowanie bezpieczeństwa na końcu autor nazywa „shift-right”.

---

## 2. Część przeglądowa (rozdz. 2; s. 79–83)

**Jakie regulacje i standardy autor wymienia?** (s. 80–81)

- **NIS2** (dyrektywa UE 2022/2555): szerszy zakres podmiotów, obowiązek środków technicznych i organizacyjnych, oceny ryzyka i zgłaszania incydentów. Kary do 10 mln euro lub 2% rocznego obrotu.
- **NIST SP 800-53 i NIST Cybersecurity Framework**, jako odpowiedniki w USA.
- **ISO/IEC 27001** i jej uzupełnienie dla chmury **ISO/IEC 27017**.
- **OWASP Top Ten** (wersja z 2021).

*W naszym projekcie:* SP 800-204D w artykule się nie pojawia. NIS2 to dobry argument w 2.2, dlaczego bezpieczeństwo potoku ma znaczenie także prawne w UE. Treść NIS2 trzeba jednak cytować z samej dyrektywy, nie z tego artykułu.

**Jakie wyzwania chmury przytacza?** (s. 81–82)

Współdzielona odpowiedzialność, wielodostępność, ryzyko utraty kontroli nad danymi i złożoność zarządzania tożsamością. Do tego, według raportu Gartnera, większość naruszeń w chmurze wynika z błędów konfiguracji i złego zarządzania tożsamością.

**Jak opisuje klasy narzędzi?** (s. 82–83)

- **SAST:** analiza kodu bez uruchamiania.
- **DAST:** testowanie działającej aplikacji, np. OWASP ZAP.
- **SCA:** analiza zewnętrznych bibliotek. Autor pisze, że 70–80% kodu współczesnych aplikacji to kod zewnętrzny, ale nie podaje źródła tej liczby.
- **IAST:** połączenie SAST i DAST, mniej fałszywych alarmów.
- **SBOM:** wykaz komponentów. Według CISA (2023) pozwala szybciej reagować na podatności w łańcuchu dostaw.

---

## 3. Metoda (rozdz. 3; s. 83–84)

**Jak autor prowadził badanie?** (s. 83–84)

Dwa etapy:
1. Przegląd literatury naukowej i branżowej, nazwany systematycznym. Kryteria: prace recenzowane, raporty i dokumentacja, po angielsku lub polsku, z ostatnich kilku lat.
2. Ankieta internetowa z pytaniami otwartymi i zamkniętymi wśród ekspertów z ośmiu sektorów: energetyka, finanse, zdrowie, administracja, telekomunikacja, transport, usługi komunalne, obronność.

**Czego brakuje w opisie metody?** (ocena agenta)

- Liczby respondentów, sposobu doboru, terminu i treści pytań.
- Jakichkolwiek wyników liczbowych.
- Protokołu przeglądu: baz, zapytań, liczby prac.

Bez tych danych nie da się ocenić, jak mocne są wnioski.

---

## 4. Wyniki (rozdz. 4; s. 84–87)

**Co deklarują respondenci?**

- DevSecOps ogranicza liczbę krytycznych podatności wykrywanych na produkcji, a dominuje trend shift-left (s. 84, rys. 1 s. 85).
- Ciągłe skanowanie w CI/CD skraca czas wykrycia i usunięcia luk (s. 84).
- Najbardziej cenione są narzędzia CSPM (wykrywanie błędnych konfiguracji chmury) i skanery kontenerów, np. Aqua i Snyk (s. 85).
- Polityki bezpieczeństwa dla IaC powinny być częścią procesu, np. Checkov dla Terraform (s. 86).
- Największy problem to integracja z systemami legacy i SCADA. Rozwiązaniem są warstwy adaptacyjne (s. 86).
- Ważne są zespoły interdyscyplinarne i szkolenia (s. 86).
- Monitoring SIEM (Splunk, ELK) połączony z automatyczną reakcją SOAR skraca czas reakcji (s. 86–87).
- Strategię kształtują NIS2, RODO, ISO/IEC 27001 i NIST (s. 87).

**Jakie przykłady techniczne podaje?** (s. 85–86)

Fragment konfiguracji potoku z etapem `security_scan` uruchamiającym SonarQube (składnia GitLab CI) i polecenie Checkov dla katalogu `terraform/`.

*W naszym projekcie:* Checkov na kodzie Terraform to ten sam pomysł. U nas w GitHub Actions, z zapisem wyników do raportu eksperymentu.

---

## 5. Ocena krytyczna (ocena agenta)

**Jakie są słabe strony tej pracy?**

1. **Ankieta bez danych.** Nie wiadomo, ilu było ekspertów ani co dokładnie odpowiedzieli. Wnioski to w praktyce opinia autora wsparta deklaracjami.
2. **Przegląd bez protokołu**, choć nazwany systematycznym.
3. **Źródła mieszane.** Obok prac recenzowanych są blogi firmowe (AmberTeam, Forward Security), raport Gartnera i czasopismo IJDO wydawnictwa IAEME (s. 89–90).
4. **Wątpliwe przypisanie.** Autor pisze, że według Rajapakse i in. (2022) DevSecOps „znacząco przyspiesza wykrywanie i eliminację podatności” (s. 80). Ten przegląd opisuje jednak wyzwania, rozwiązania i luki, a agent nie znalazł w nim takiego stwierdzenia. *Wniosek:* tezy z Rajapakse cytuj bezpośrednio z Rajapakse, nie przez Janczewskiego.
5. **Liczba bez źródła:** 70–80% kodu zewnętrznego (s. 82).

**Do czego mimo to się przydaje?**

Polska publikacja z 2025 r., kontekst UE (NIS2, RODO), infrastruktura krytyczna i SBOM. To tło dla 2.2 i 2.3, a w 2.5 przykład, że korzyści DevSecOps są w literaturze często deklarowane, a nie mierzone.

---

## 6. Pytania, które może zadać recenzent

**„Janczewski pisze, że DevSecOps zmniejsza liczbę podatności na produkcji. Po co więc Twój eksperyment?”**

Bo to deklaracja ekspertów bez liczb. Artykuł nie podaje liczebności próby ani wyników. Mój eksperyment mierzy na konkretnym potoku, ile podatności z katalogu dociera na produkcję w wariancie bez skanerów i ze skanerami (RQ1).

**„Dlaczego cytujesz tak słabą pracę?”**

Bo daje polski i unijny kontekst regulacyjny, którego nie mają inne prace z rdzenia, a temat (DevSecOps w chmurze) jest zbieżny. Używam jej jako tła, nie jako dowodu, a jej ograniczenia opisuję wprost.

**„Czy Twoja praca dotyczy infrastruktury krytycznej?”**

Nie. To aplikacja webowa w AWS. Wnioski Janczewskiego o systemach legacy i SCADA nie przenoszą się na mój przypadek. Przenoszą się wnioski ogólne o automatyzacji i shift-left.
