# Weryfikacja źródeł z propozycji tematu

Zadanie E02-01. Data weryfikacji: 2026-10-01. Wykonał: Claude Code z autorem pracy.

## Cel i metoda

Po rozdzieleniu ASVS i SAMM oraz scaleniu zdublowanego przewodnika Codefresh lista z propozycji tematu liczy 26 pozycji: 10 książek, 6 standardów i stron projektów, 7 artykułów naukowych i 3 teksty branżowe. Część opisów brzmi jak wynik wyszukiwania wspomaganego przez AI (np. „nie pojawiły się w wynikach jako osobne linki”), dlatego żadnej pozycji nie przyjęto bez sprawdzenia.

Każdą pozycję sprawdzono w jednym lub kilku miejscach:

- **Artykuły:** Crossref (`api.crossref.org`), strona wydawcy lub czasopisma, arXiv.
- **Standardy:** strony NIST CSRC i NCCoE, strony projektów OWASP, repozytoria GitHub projektów (daty wydań przez API GitHub).
- **Książki:** Open Library oraz katalogi księgarń i bibliotek. Strona O'Reilly odrzuca pobieranie automatyczne (HTTP 403), więc metadane książek warto potwierdzić na stronie redakcyjnej posiadanego egzemplarza.
- **Blogi:** sama strona artykułu (autor, data, powiązanie z produktem).

Statusy:

- **potwierdzone:** źródło istnieje, a opis w propozycji się zgadza,
- **poprawione:** źródło istnieje, ale propozycja podaje błędny rok, tytuł, adres lub instytucję,
- **odrzucone:** źródła nie da się potwierdzić albo nie nadaje się do cytowania w pracy.

Rekomendacja określa rolę źródła w pracy: **główne**, **uzupełniające** lub **nie cytować**. Weryfikacja dotyczy metadanych. Tego, czy treść źródła rzeczywiście wspiera tezy przypisane mu w propozycji, nie sprawdzano. To wyjdzie przy lekturze (E02-02 i dalsze).

## Podsumowanie

| Status | Liczba |
|---|---|
| potwierdzone | 21 |
| poprawione | 4 |
| odrzucone | 1 |
| **razem** | **26** |

Najważniejsze ustalenia:

1. **Żadne źródło naukowe nie okazało się zmyślone.** Wszystkie 7 artykułów ma DOI w Crossref, a tytuły zgadzają się co do słowa.
2. **Rajapakse i in.: rok 2022, nie 2021.** Wersja online ukazała się w 2021 r., ale artykuł należy do tomu 141 z 2022 r.
3. **Dwa artykuły pochodzą od wydawców o wątpliwej renomie.** Abiona i in. (2024, GSC Online Press) oraz Gupta (2022, Seventh Sense Research Group) to krótkie teksty (7 i 5 stron) u wydawców, którzy publikują masowo i bardzo szybko. Przed cytowaniem trzeba sprawdzić indeksację czasopism w Scopus i w wykazie czasopism punktowanych MNiSW. TODO: zweryfikować. Do czasu sprawdzenia pozostają źródłami uzupełniającymi. Jako przegląd literatury znacznie mocniejszy jest [@Rajapakse2022].
4. **Strona projektu „NIST DevSecOps” już nie istnieje pod starym adresem.** `csrc.nist.gov/projects/devsecops` przekierowuje do projektu NCCoE „Software Supply Chain and DevOps Security Practices”. Zamiast strony projektu lepiej cytować jego publikację. Wersja robocza NIST SP 1800-44 z lipca 2025 r. została w marcu 2026 r. wycofana i zastąpiona „żywym dokumentem” pod adresem `pages.nist.gov/nccoe-devsecops`.
5. **Standardy mają nowsze wersje, niż sugeruje propozycja:**
   - SSDF: obowiązuje wersja 1.1 (SP 800-218, 2022), a wersja 1.2 (SP 800-218 Rev. 1) jest od grudnia 2025 r. wersją roboczą,
   - OWASP ASVS: wersja 5.0.0 z maja 2025 r.,
   - OWASP SAMM: wersja 2.2.0 z lipca 2026 r. Strona `owaspsamm.org/model` nadal opisuje wersję 2.0.
6. **Przewodnik Codefresh przeniesiono do Octopus Deploy.** Codefresh jest teraz częścią Octopus Deploy, a adres przekierowuje do `octopus.com`. W propozycji przewodnik występuje dwa razy (raz wśród przewodników AWS, raz wśród blogów).

## Wyniki

### Książki

Wszystkie są wydane przez O'Reilly Media. Autor pracy ma egzemplarze, więc rok i wydanie najprościej potwierdzić na stronie redakcyjnej.

| # | Pozycja w propozycji | Ustalony opis | Status | Rekomendacja | Klucz |
|---|---|---|---|---|---|
| 1 | Learning DevSecOps | S. Suehring, *Learning DevSecOps: A Practical Guide to Processes and Tools*, 2024, ISBN 978-1-098-14486-9 | potwierdzone | główne | `Suehring2024` |
| 2 | Learning GitHub Actions | B. Laster, *Learning GitHub Actions: Automation and Integration of CI/CD with GitHub*, 2023, ISBN 978-1-098-13107-4 | potwierdzone | główne | `Laster2023` |
| 3 | Learning Git | A. Skoulikari, *Learning Git: A Hands-On and Visual Guide to the Basics of Git*, 2023, ISBN 978-1-098-13391-7 | potwierdzone | uzupełniające | `Skoulikari2023` |
| 4 | Efficient Linux at the Command Line | D. J. Barrett, *Efficient Linux at the Command Line: Boost Your Command-Line Skills*, 2022, ISBN 978-1-098-11340-7 | potwierdzone | pomocnicze, raczej nie do cytowania | `Barrett2022` |
| 5 | Terraform: Up & Running (3rd Edition) | Y. Brikman, *Terraform: Up and Running: Writing Infrastructure as Code*, wyd. 3, 2022, ISBN 978-1-098-11674-3 | potwierdzone | główne | `Brikman2022` |
| 6 | Ansible: Up and Running (3rd Edition) | B. Meijer, L. Hochstein, R. Moser, *Ansible: Up and Running: Automating Configuration Management and Deployment the Easy Way*, wyd. 3, 2022 | potwierdzone | główne (jeśli Ansible zostanie w zakresie) | `Meijer2022` |
| 7 | Python for DevOps | N. Gift, K. Behrman, A. Deza, G. Gheorghiu, *Python for DevOps: Learn Ruthlessly Effective Automation*, 2019, ISBN 978-1-492-05769-7 | potwierdzone | uzupełniające | `Gift2019` |
| 8 | Network Programmability and Automation (2nd Edition) | M. Oswalt, C. Adell, S. S. Lowe, J. Edelman, *Network Programmability and Automation: Skills for the Next-Generation Network Engineer*, wyd. 2, 2023, ISBN 978-1-098-11083-3 | potwierdzone | nie cytować (poza zakresem) | `Oswalt2023` |
| 9 | Web Application Security (2nd Edition) | A. Hoffman, *Web Application Security: Exploitation and Countermeasures for Modern Web Applications*, wyd. 2, 2024, ISBN 978-1-098-14393-0 | potwierdzone | główne | `Hoffman2024` |
| 10 | FastAPI | B. Lubanovic, *FastAPI: Modern Python Web Development*, 2023, ISBN 978-1-098-13550-8 | potwierdzone | uzupełniające | `Lubanovic2023` |

Uwagi:

- (3) Open Library podaje rok 2022, księgarnie podają czerwiec 2023. Przyjęto 2023. TODO: zweryfikować na stronie redakcyjnej.
- (6) Źródła podają różne ISBN wydania drukowanego (978-1-098-10915-8 albo 978-1-098-10914-1). TODO: zweryfikować na egzemplarzu.
- (8) Pierwsze wydanie (2018) miało trzech autorów. Drugie ma czterech, a pierwszym autorem jest Oswalt, nie Edelman.

### Standardy i strony projektów

| # | Pozycja w propozycji | Ustalony opis | Status | Rekomendacja | Klucz |
|---|---|---|---|---|---|
| 11 | NIST DevSecOps – strona projektu (NIST CSRC) | Stary adres przekierowuje do projektu NCCoE „Software Supply Chain and DevOps Security Practices”. Obecna publikacja projektu: A. Kerman, M. Ogata, P. Grayeli i in., *Secure Software Development, Security, and Operations (DevSecOps) Practices*, NIST NCCoE, „live document” (wersja robocza, seria „Other”), 2026-03-24, https://pages.nist.gov/nccoe-devsecops/ | poprawione | uzupełniające (dokument roboczy, aktualizowany na bieżąco) | `NIST-NCCoE-DevSecOps-2026` |
| 12 | NIST SP 800-204D (2024) | R. Chandramouli, F. Kautz, S. Torres-Arias, NIST SP 800-204D, luty 2024, doi: 10.6028/NIST.SP.800-204D | potwierdzone | główne | `NIST-SP800-204D` (już w rejestrze) |
| 13 | NIST SSDF, SP 800-218 | M. Souppaya, K. Scarfone, D. Dodson, *Secure Software Development Framework (SSDF) Version 1.1*, NIST SP 800-218, luty 2022, doi: 10.6028/NIST.SP.800-218 | potwierdzone | główne | `NIST-SP800-218` |
| 14 | OWASP DevSecOps Guideline | Projekt OWASP (status Incubator, lider A. Yazdani), treść na GitHub `OWASP/DevSecOpsGuideline`, bez numerowanych wydań, ostatni commit 2026-09-24 | potwierdzone | główne (cytować z datą dostępu) | `OWASP-DevSecOps-Guideline` |
| 15a | OWASP ASVS | *OWASP Application Security Verification Standard 5.0.0*, maj 2025 (projekt Flagship) | potwierdzone | główne | `OWASP-ASVS-5.0` |
| 15b | OWASP SAMM | *OWASP Software Assurance Maturity Model* v2.2.0, wydanie 2026-07-06 (`owaspsamm/core`) | potwierdzone | uzupełniające | `OWASP-SAMM-2.2` |

Uwagi:

- (11) Wersja robocza NIST SP 1800-44 Vol. A z 2025-07-30 została 2026-03-24 wycofana (CSRC: „Withdrawn”, „Obsoleted”). Zastąpił ją dokument publikowany jako „live document”, który ma być aktualizowany na bieżąco. Nie ma DOI ani numeru wersji, więc w pracy cytować go z datą dostępu. Przed złożeniem pracy sprawdzić, czy NIST wydał wersję ostateczną.
- (13) SSDF 1.2 (NIST SP 800-218 Rev. 1, H. Booth i in., doi: 10.6028/NIST.SP.800-218r1.ipd) jest od 2025-12-17 wersją roboczą, a uwagi zbierano do 2026-01-30. Cytować wersję 1.1. Wersję 1.2 można wspomnieć jako kierunek zmian. Przed złożeniem pracy sprawdzić, czy ukazała się wersja ostateczna.
- (13) Teza z propozycji, że SP 800-204D omawia związek SSDF z CI/CD, wymaga sprawdzenia przy lekturze (E02-02). **Potwierdzone 2026-10-02 (E02-02):** dodatek A SP 800-204D mapuje zadania CI/CD na praktyki SSDF (PO.1–PO.5, PS.1–PS.3, PW.5, PW.6, PW.8, PW.9), a dodatek B uzasadnia pominięcie PW.1–PW.4, PW.7 i RV.1–RV.3. Szczegóły: [`notes/nist-800-204d.md`](notes/nist-800-204d.md).
- (15a) W propozycji ASVS i SAMM tworzą jedną pozycję. W rejestrze są to dwa osobne źródła.

### Artykuły naukowe

| # | Pozycja w propozycji | Ustalony opis | Status | Rekomendacja | Klucz |
|---|---|---|---|---|---|
| 16 | „The emergence and importance of DevSecOps…” (2024) | O. O. Abiona, O. J. Oladapo, O. T. Modupe, O. C. Oyeniran, A. O. Adewusi, A. M. Komolafe, *World Journal of Advanced Engineering Technology and Sciences*, t. 11, nr 2, s. 127–133, 2024, doi: 10.30574/wjaets.2024.11.2.0093 | potwierdzone | uzupełniające (wątpliwy wydawca) | `Abiona2024` |
| 17 | „Challenges and solutions when adopting DevSecOps: A systematic review” (2021) | R. N. Rajapakse, M. Zahedi, M. A. Babar, H. Shen, *Information and Software Technology*, t. 141, art. 106700, **2022**, doi: 10.1016/j.infsof.2021.106700 | poprawione (rok) | główne | `Rajapakse2022` (już w rejestrze) |
| 18 | „An Integrated Framework for DevSecOps Adoption” (2022) | A. Gupta, *International Journal of Computer Trends and Technology*, t. 70, nr 6, s. 19–23, 2022, doi: 10.14445/22312803/IJCTT-V70I6P102; także arXiv:2207.04093 | potwierdzone | uzupełniające (wątpliwy wydawca) | `Gupta2022` |
| 19 | „Advancing DevSecOps in SMEs…” (2025) | J. Cheenepalli, J. D. Hastings, K. M. Ahmed, C. Fenner, w: *2025 13th International Symposium on Digital Forensics and Security (ISDFS)*, IEEE, 2025, s. 1–6, doi: 10.1109/ISDFS65363.2025.11011960; także arXiv:2503.22612 | potwierdzone | główne | `Cheenepalli2025` |
| 20 | „Implementacja praktyk DevSecOps w środowiskach chmurowych…” (WSB Poznań, 2025) | T. Janczewski (WSB **Warszawa**), „Implementacja praktyk DevSecOps w środowiskach chmurowych dla infrastruktury krytycznej: analiza integracji bezpieczeństwa z procesami CI/CD”, *Zeszyty Naukowe Wyższej Szkoły Bankowej w Poznaniu*, t. 108, nr 1, 2025, doi: 10.58683/dnswsb.2064 | poprawione (afiliacja, pełny tytuł) | uzupełniające | `Janczewski2025` |
| 21 | „Streamlined DevSecOps: Automated Vulnerability Exception Management…” (2025) | B. N. Biswas, w: *2025 12th International Conference on Reliability, Infocom Technologies and Optimization (Trends and Future Directions) (ICRITO)*, IEEE, 2025, s. 1–4, doi: 10.1109/ICRITO66076.2025.11241906 | potwierdzone | uzupełniające | `Biswas2025` |
| 22 | „Resilient Cloud cluster with DevSecOps security model…” (2024) | A. S. A. Alghawli, T. Radivilova, „Resilient cloud cluster with DevSecOps security model, automates a data analysis, vulnerability search and risk calculation”, *Alexandria Engineering Journal*, t. 107, s. 136–149, 2024, doi: 10.1016/j.aej.2024.07.036 | potwierdzone | główne | `Alghawli2024` |

Uwagi:

- (16, 18) Jakość wydawców: patrz „Najważniejsze ustalenia”, pkt 3. TODO: zweryfikować indeksację.
- (20) Czasopismo wydaje WSB w Poznaniu, ale autor jest z WSB w Warszawie. Opisy metody są niespójne: wyniki wyszukiwania mówią o ankiecie wśród ekspertów, a strona czasopisma o przeglądzie literatury i analizie przypadków. Zakresu stron nie ustalono. TODO: zweryfikować w PDF.
- (21) Krótki (4 strony) artykuł konferencyjny jednego autora. Przydatny w dyskusji o akceptowanych podatnościach (5.3), nie jako podstawa teoretyczna.

### Teksty branżowe i blogi

Według definicji zadania blogi mogą być tylko źródłami uzupełniającymi.

| # | Pozycja w propozycji | Ustalenia | Status | Rekomendacja | Klucz |
|---|---|---|---|---|---|
| 23 | „DevSecOps on AWS: A Practical Guide – Codefresh” (wymieniony dwukrotnie) | Autor: D. Garfield (współzałożyciel Codefresh, obecnie Octopus Deploy). Adres `codefresh.io/learn/devsecops/devsecops-on-aws/` przekierowuje do `octopus.com/devops/devsecops/devsecops-aws/`. Brak daty. Treść promuje produkty firmy, ale przegląda usługi AWS do skanowania, monitoringu i audytu (Inspector, Security Hub, GuardDuty, CloudTrail, Config i in.) | poprawione (adres, wydawca) | uzupełniające: lista usług AWS do porównania z projektem; fakty o usługach cytować z dokumentacji AWS | `Octopus-DevSecOps-AWS` |
| 24 | „Securing the DevOps Pipeline: Best Practices for DevSecOps in 2025” (dev.to) | Autor: R. Mathews, serwis DEV Community. Tekst bez odwołań do źródeł. Data publikacji niejednoznaczna (strona podaje 11 października 2025 i edycję 22 maja) | potwierdzone | nie cytować: brak źródeł, treść ogólna, każdą tezę lepiej oprzeć na standardzie | — |
| 25 | „DevSecOps Frameworks in 2026: NIST, OWASP, SLSA Explained” | Prawdziwy tytuł: „DevSecOps Framework in 2026: NIST, OWASP, SLSA, and How to Choose the Right One”. Autor: D. Kiessling, Cloudaware, 2026-08-06. Treść promuje produkt Cloudaware (CMDB) | odrzucone | nie cytować: tekst marketingowy, w propozycji z błędnym tytułem; do łączenia NIST, OWASP i SLSA użyć źródeł pierwotnych (SP 800-204D, SSDF, slsa.dev) | — |

## Co dalej

- Nowe źródła mają notatki w rejestrze (`Zrodla\` w vaulcie) z polem `metadane_sprawdzone: 2026-10-01`. Wyjątkiem są blogi z rekomendacją „nie cytować”.
- Otwarte kwestie z oznaczeniem TODO:
  - indeksacja WJAETS i IJCTT,
  - zakres stron i metoda u Janczewskiego,
  - ISBN Ansible,
  - rok wydania Learning Git.
- Brakująca literatura (luka do uzupełnienia w E02-07 i E02-08): propozycja ma niewiele recenzowanych badań empirycznych o skuteczności skanerów w potokach CI/CD i o bezpieczeństwie GitHub Actions. Warto przeszukać IEEE Xplore, ACM DL i Scopus (np. prace o zatrutym wykonaniu potoku i o bezpieczeństwie workflowów GitHub Actions).
