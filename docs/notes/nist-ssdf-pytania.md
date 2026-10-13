# NIST SP 800-218 (SSDF): pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia [`nist-ssdf.md`](nist-ssdf.md), gdzie są pełne notatki i tabela 42 zadań.

- Odpowiedzi opracował agent (Claude Code) na podstawie tekstu dokumentu [@NIST-SP800-218], 2026-10-05. Przykłady „w naszym projekcie” to propozycje agenta, a nie treść dokumentu.
- Strony podano dwojako: numer z dokumentu (dok.) i numer w przeglądarce PDF. W części głównej PDF = dok. + 9.
- Plik PDF: `NIST.SP.800-218.pdf` (36 stron). Treść właściwa to około 19 stron, z czego 15 zajmuje jedna duża tabela.

---

## Najpierw w pięciu zdaniach

1. SSDF to katalog **dobrych praktyk bezpiecznego wytwarzania oprogramowania**, zebranych z istniejących standardów. NIST niczego tu nie wymyśla od zera.
2. Praktyki są podzielone na **cztery grupy**: przygotuj organizację (PO), chroń oprogramowanie (PS), twórz bezpieczne oprogramowanie (PW), reaguj na podatności (RV).
3. Dokument mówi, **co** ma być osiągnięte, a nie **jak** i jakim narzędziem. Dlatego pasuje do każdej firmy i technologii, ale wymaga własnej interpretacji.
4. To **nie jest lista kontrolna** do odhaczenia. Organizacja wybiera praktyki według ryzyka i kosztu.
5. W pracy SSDF to **rama odniesienia (3.1)**. SP 800-204D przekłada ją na konkretne zadania w potoku CI/CD.

---

## 1. Po co jest SSDF (streszczenie i rozdz. 1; dok. vi, 1–3; PDF 8, 10–12)

**Jaki problem rozwiązuje SSDF?**

Większość modeli wytwarzania oprogramowania (kaskadowy, zwinny, DevOps) mówi, *jak* organizować pracę, ale prawie nic o bezpieczeństwie. SSDF to zestaw praktyk, które można „dokleić” do dowolnego z tych modeli, żeby bezpieczeństwo było obecne przez cały cykl życia, a nie tylko na końcu (dok. 1).

**Jakie trzy cele mają praktyki SSDF?** (dok. 1)

1. Mniej podatności w wydanym oprogramowaniu.
2. Mniejsze szkody, gdy ktoś wykorzysta podatność, której nie wykryto albo nie naprawiono.
3. Usuwanie **przyczyn** podatności, żeby te same błędy nie wracały.

**Co SSDF uznaje za podatność?**

Nie tylko błąd w kodzie. Także złe ustawienia konfiguracji, błędne założenia o tym, komu lub czemu można ufać, i nieaktualną analizę ryzyka (dok. 1). *W naszym projekcie:* dlatego skanujemy też Terraform, Dockerfile i pliki workflow, a nie tylko kod aplikacji.

**Co to jest *shift left* i dlaczego SSDF o nim mówi?**

To zasada: zajmuj się bezpieczeństwem jak najwcześniej. Błąd znaleziony przy pisaniu kodu kosztuje mniej niż ten sam błąd znaleziony na produkcji. Dokument nazywa tę zasadę krytycznie ważną bez względu na model pracy (dok. 1). *W naszym projekcie:* skanery uruchamiane już przy pull requeście, a nie dopiero przed wdrożeniem.

**Czy SSDF wymyśla nowe praktyki?**

Nie. Dokument wprost mówi, że nie wprowadza nowych praktyk ani terminów, tylko zbiera je z uznanych źródeł (dok. 1). Przy każdym zadaniu podaje odwołania, np. do OWASP SAMM, OWASP ASVS, BSIMM i Microsoft SDL. Na obronie: SSDF to „wspólny mianownik” wielu standardów.

**Dlaczego SSDF nie mówi, jakich narzędzi użyć?**

Bo skupia się na wynikach, nie na środkach (dok. 1–2). Dzięki temu nadaje się dla każdej organizacji, języka i platformy, od IoT po aplikacje webowe. Ceną jest ogólność: SSDF nie powie, czy Semgrep wystarczy. To musimy uzasadnić sami.

**Czy SSDF odnosi się do DevOps?**

Tylko zapowiada, że w przyszłości mogą powstać wskazówki, jak stosować SSDF w konkretnych metodykach, np. w DevOps (dok. 1). *Interpretacja agenta:* tę lukę wypełnia potem SP 800-204D (2024). Dlatego praca czyta oba dokumenty razem: SSDF mówi *co*, a 800-204D *gdzie w potoku*.

**Czy trzeba wdrożyć wszystkie praktyki?**

Nie (dok. 3):
- nie każda praktyka ma sens w każdym projekcie. Dokument podaje przykład: jeśli nic nie kompilujesz, nie konfigurujesz kompilatora,
- o wyborze decydują ryzyko, koszt, wykonalność i stosowalność, a do tego to, czy praktykę da się zautomatyzować,
- praktyki nie mają priorytetów, a podane częstotliwości („raz w roku”) są tylko orientacyjne.

**Czy SSDF jest listą kontrolną?**

Dokument wprost mówi, że **nie**. Ma być podstawą do planowania podejścia opartego na ryzyku (dok. 3). **Ważne dla naszej pracy:** skoro i tak oceniamy potok względem SSDF, uczciwie jest mówić o „pokryciu zadań, które dotyczą projektu”, a nie o „zgodności z SSDF”. Zadania, które nas nie dotyczą, wykluczamy z uzasadnieniem.

**Kto odpowiada za praktyki, gdy korzystamy z chmury?**

Odpowiedzialność się dzieli: część praktyk realizuje dostawca platformy, część klient (model współodpowiedzialności, dok. 3). Klient powinien wiedzieć, kto za co odpowiada. *W naszym projekcie:* GitHub odpowiada za bezpieczeństwo runnerów hostowanych, AWS za fizyczną infrastrukturę. My odpowiadamy za konfigurację workflow, uprawnienia IAM i to, co wdrażamy.

---

## 2. Jak zbudowane są ramy (rozdz. 2; dok. 4; PDF 13)

**Jakie są cztery grupy praktyk?**

| Skrót | Nazwa | Po ludzku |
|---|---|---|
| PO | Prepare the Organization | Przygotuj ludzi, procesy i narzędzia |
| PS | Protect the Software | Chroń kod i wydania przed podmianą i kradzieżą |
| PW | Produce Well-Secured Software | Projektuj, pisz i testuj tak, żeby było jak najmniej dziur |
| RV | Respond to Vulnerabilities | Gdy dziura się znajdzie, wykryj ją szybko, napraw i wyciągnij wnioski |

**Czy to fazy cyklu życia, np. planowanie, budowanie, wdrażanie?**

Nie. To częsty błąd, który był też w propozycji tematu (fazy PLAN/DEVELOP/BUILD/DEPLOY/OPERATE). Grupy to kategorie praktyk, a nie etapy. Dokument zastrzega, że kolejność w tabeli nie oznacza ani kolejności wdrażania, ani ważności (dok. 4). Praktyki z różnych grup działają równolegle: RV działa cały czas, a nie „po” PW.

**Z czego składa się każda praktyka?**

Z czterech poziomów, od ogółu do szczegółu:
1. **Praktyka**, np. *PW.7 Przegląd i analiza kodu*, z jednozdaniowym celem.
2. **Zadania**, np. *PW.7.2 Wykonaj przegląd lub analizę i zapisz znaleziska*. To jednostka, którą oceniamy w tabeli zadań.
3. **Przykłady wdrożenia** (*notional implementation examples*), np. „użyj narzędzia analizy statycznej, a wyniki niech przejrzy człowiek”. Są poglądowe, żaden nie jest obowiązkowy.
4. **Odwołania** do standardów źródłowych. Przy lekturze można je pominąć.

Razem: 19 praktyk i 42 zadania (policzył agent, dokument nie podaje tych liczb).

**Jakie pojęcia SSDF zostawia do zdefiniowania organizacji?**

Między innymi „dane wrażliwe”, „osoba wykwalifikowana”, „dobrze zabezpieczone” i nazwy środowisk (development, build, test, staging, produkcja). Dokument podkreśla, że środowiska trzeba wyliczyć, bo dopiero wtedy można je chronić i utrudnić atakującemu przejście z jednego do drugiego (dok. 4). *Do zrobienia przy projekcie potoku (E07-01):* wymienić nasze środowiska, np. runner CI, środowisko testowe dla DAST, produkcja w AWS.

---

## 3. Grupa PO: przygotowanie organizacji (dok. 5–9; PDF 14–18)

**O co chodzi w PO w jednym zdaniu?**

Zanim zaczniesz pisać kod, ustal wymagania, role, narzędzia i kryteria oceny oraz zabezpiecz środowiska, w których powstaje oprogramowanie.

**Co mówi PO.1 (wymagania bezpieczeństwa)?** (dok. 5–6, PDF 14–15)

Wymagania bezpieczeństwa mają być spisane i aktualne. Dotyczą dwóch rzeczy:
- infrastruktury i procesów wytwarzania (PO.1.1), czyli na przykład jak chronimy potok,
- samego oprogramowania (PO.1.2), czyli na przykład jakie klasy błędów są niedopuszczalne.

Dwa przykłady szczególnie ważne dla nas:
- zgodność z wymaganiami sprawdzana w kluczowych punktach, m.in. **bramkami**, które wychwytują określone klasy błędów,
- **proces obsługi wyjątków** od wymagań, z okresowym przeglądem zatwierdzonych wyjątków.

*W naszym projekcie:* bramki w potoku to realizacja PO.1.2. Wyjątki od skanera, np. zignorowana podatność, powinny mieć uzasadnienie i datę przeglądu.

**Co mówi PO.2 (role)?** (dok. 6–7, PDF 15–16)

Każdy uczestnik ma znać swoją rolę w bezpieczeństwie i mieć szkolenie dopasowane do roli, a kierownictwo ma deklarować wsparcie. Jeden z przykładów: wyznaczyć **właściciela kodu** dla projektu. *W naszym projekcie:* jesteśmy jedną osobą, więc PO.2 w większości nie dotyczy. Śladem może być plik `CODEOWNERS`.

**Co mówi PO.3 (łańcuch narzędzi)?** (dok. 7–8, PDF 16–17)

Używaj automatyzacji, bo zmniejsza wysiłek, poprawia powtarzalność i **zostawia dowody**. Trzy zadania:
1. **PO.3.1:** ustal, jakie narzędzia mają być w łańcuchu i jak mają się ze sobą łączyć.
2. **PO.3.2:** same narzędzia też zabezpieczaj. Przykłady: potok jako kod, odtwarzalne buildy, aktualizacje narzędzi, **sprawdzanie integralności i pochodzenia każdego narzędzia**.
3. **PO.3.3:** narzędzia mają generować artefakty, czyli dowody, że praktyki są stosowane.

*W naszym projekcie:* workflow w YAML to „potok jako kod”. Przypinanie akcji GitHuba do SHA to sposób na PO.3.2 (zaufane pochodzenie narzędzia). Raporty skanerów zapisane w GitHubie to PO.3.3.

**Co SSDF rozumie przez „artefakt”?**

Dowód (przypis 6, dok. 7): zapis, który pokazuje, że praktykę stosowano. To **inaczej niż w CI/CD**, gdzie artefaktem nazywa się zwykle produkt buildu (obraz, paczka). W pracy trzeba to rozróżnić, np. pisać „artefakt buildu” i „dowód (artefakt w rozumieniu SSDF)”.

**Co mówi PO.4 (kryteria kontroli)?** (dok. 8, PDF 17)

Ustal, po czym poznasz, że oprogramowanie jest wystarczająco bezpieczne, i zbieraj dane, żeby to sprawdzać. Przykłady:
- wskaźniki (KPI, KRI) i progi ważności podatności,
- kryteria bezpieczeństwa w *Definition of Done*,
- rejestrowanie akceptacji, odrzuceń i wyjątków,
- **automatyzacja decyzji na podstawie kryteriów**,
- ochrona zebranych danych przed zmianą i usunięciem.

*W naszym projekcie:* „zablokuj wdrożenie, jeśli skaner znajdzie podatność CRITICAL” to dokładnie PO.4: kryterium (próg) plus zautomatyzowana decyzja (bramka).

**Co mówi PO.5 (bezpieczne środowiska)?** (dok. 8–9, PDF 17–18)

Środowiska, w których powstaje oprogramowanie (development, build, test, dystrybucja), mają być od siebie oddzielone i dobrze chronione (PO.5.1). Stacje robocze deweloperów mają być utwardzone (PO.5.2). Przykłady:
- MFA,
- oddzielenie od produkcji,
- **jak najmniej bezpośredniego dostępu ludzi do systemów buildu**,
- ciągłe monitorowanie wdrożonego oprogramowania pod kątem nowych podatności.

PO.5 to nowość wersji 1.1 (dok. 27), dodana po głośnych atakach na łańcuch dostaw. *W naszym projekcie:* runnery hostowane przez GitHuba są jednorazowe i nikt się na nie nie loguje. Środowiska GitHuba z regułami ochrony oraz osobne role IAM (OIDC) oddzielają test od produkcji.

---

## 4. Grupa PS: ochrona oprogramowania (dok. 9–10; PDF 18–19)

**O co chodzi w PS w jednym zdaniu?**

Nikt nie może niepostrzeżenie podmienić kodu ani wydania, a odbiorca ma mieć jak to sprawdzić.

**Co mówi PS.1?** (dok. 9, PDF 18)

Każda postać kodu (źródła, pliki wykonywalne, konfiguracja jako kod) jest przechowywana według zasady najmniejszych uprawnień. Przykłady:
- repozytorium z kontrolą dostępu,
- historia zmian przypisana do konkretnych kont,
- **podpisywanie commitów**,
- **przegląd zmian przez właściciela kodu**,
- podpisywanie plików wykonywalnych,
- hashe kryptograficzne.

*W naszym projekcie:* ochrona gałęzi `main`, podpisane commity, podpis obrazu. Przegląd przez drugą osobę jest niemożliwy w projekcie jednoosobowym. To ograniczenie do opisania w 5.3.

**Co mówi PS.2?** (dok. 10, PDF 19)

Odbiorca ma mieć sposób, żeby sprawdzić, że dostał prawdziwe, niezmienione oprogramowanie. Przykłady: opublikowane hashe, podpis certyfikatem uznanego urzędu, pilnowanie odnawiania i unieważniania certyfikatów. *W naszym projekcie:* digest obrazu i podpis lub atestacja (Sigstore, GitHub artifact attestations), sprawdzane przed wdrożeniem.

**Co mówi PS.3 i gdzie jest SBOM?** (dok. 10, PDF 19)

Każde wydanie trzeba zarchiwizować razem z danymi pomocniczymi (PS.3.1). Dla wszystkich komponentów wydania trzeba zbierać i udostępniać **dane o pochodzeniu** (*provenance*), na przykład w postaci **SBOM** (PS.3.2). Przykłady:
- archiwum tylko do odczytu,
- dane weryfikacyjne przechowywane osobno albo podpisane,
- SBOM w standardowym formacie, aktualizowany przy każdej zmianie komponentu.

To jedyne miejsce, gdzie SSDF wspomina SBOM. *W naszym projekcie:* SBOM generowany przy każdym buildzie i dołączany do obrazu jako atestacja.

**Co to jest *provenance*?**

Według definicji z przypisu 5 (dok. 6) to historia komponentu: skąd pochodzi, jak powstał, kto był właścicielem, gdzie był i co w nim zmieniano. W praktyce CI/CD to zapis, z jakiego kodu, jakim procesem i na jakiej maszynie zbudowano artefakt. Szczegółowo opisuje to SLSA (E02-05).

---

## 5. Grupa PW: wytwarzanie bezpiecznego oprogramowania (dok. 11–16; PDF 20–25)

**O co chodzi w PW w jednym zdaniu?**

Od projektu przez kod do testów rób wszystko tak, żeby w wydaniu było jak najmniej podatności.

**Jakie praktyki obejmuje PW?**

| Praktyka | O czym | Czy w potoku? |
|---|---|---|
| PW.1 | Projekt odporny na ryzyka (modelowanie zagrożeń, śledzenie decyzji) | Głównie nie, to praca projektowa |
| PW.2 | Przegląd projektu | Częściowo (skan IaC) |
| PW.3 | Wycofana w wersji 1.1, scalona z PW.4 | — |
| PW.4 | Bezpieczne komponenty zewnętrzne i ich weryfikacja (**SCA**) | Tak |
| PW.5 | Bezpieczne praktyki kodowania | Częściowo (lintery) |
| PW.6 | Bezpieczna konfiguracja buildu | Tak |
| PW.7 | Przegląd i analiza kodu (**SAST**) | Tak |
| PW.8 | Testy działającego kodu (**DAST**) | Tak |
| PW.9 | Bezpieczne ustawienia domyślne | Tak |

**Co mówi PW.1?** (dok. 11, PDF 20)

Zanim powstanie kod, oceń ryzyka. Narzędzia to modelowanie zagrożeń, modelowanie ataków i mapowanie powierzchni ataku (PW.1.1). Zapisuj wymagania, ryzyka i decyzje projektowe (PW.1.2). Korzystaj ze standardowych mechanizmów bezpieczeństwa zamiast pisać własne (PW.1.3). Ważny przykład: **zapisywać uzasadnienie każdego zatwierdzonego wyjątku** i okresowo te wyjątki przeglądać. *W naszym projekcie:* ADR-y to zapis decyzji z PW.1.2. Modelem zagrożeń potoku będzie OWASP Top 10 CI/CD (E02-04).

**Co mówi PW.2?** (dok. 12, PDF 21)

Projekt ma przejrzeć osoba, która go nie tworzyła, **albo** zautomatyzowany proces w łańcuchu narzędzi. Sprawdza się, czy projekt spełnia wymagania i odpowiada na ryzyka. *Interpretacja agenta:* skaner IaC (Checkov albo Trivy) sprawdza część decyzji projektowych infrastruktury, np. czy coś nie jest publicznie dostępne.

**Co mówi PW.4 i gdzie jest SCA?** (dok. 12–13, PDF 21–22)

Korzystaj ze sprawdzonych komponentów zewnętrznych (bibliotek, frameworków) zamiast pisać wszystko samemu, ale **weryfikuj je przez cały ich cykl życia** (PW.4.4). Przykłady z PW.4.4:
- regularnie sprawdzaj, czy komponenty mają znane, nienaprawione podatności,
- **wbuduj w łańcuch narzędzi automatyczne wykrywanie znanych podatności w komponentach**,
- sprawdzaj, czy komponent jest jeszcze utrzymywany i czy nie minął jego koniec życia (EOL),
- potwierdzaj integralność komponentów podpisem.

To jest właśnie SCA, choć SSDF nie używa tego skrótu. *W naszym projekcie:* pip-audit i Trivy dla zależności, `dependency-review-action` w PR, Dependabot do aktualizacji.

**Co mówi PW.5?** (dok. 13, PDF 22)

Pisz kod według bezpiecznych praktyk właściwych dla języka. Przykłady:
- walidacja wejścia i kodowanie wyjścia,
- unikanie niebezpiecznych funkcji,
- obsługa błędów i logowanie,
- lintery i formatery,
- przegląd własnego kodu przez autora. Jest to tylko uzupełnienie, nie zastępuje przeglądu przez innych.

*W naszym projekcie:* potok pomaga linterami i Banditem, ale samo pisanie bezpiecznego kodu dzieje się poza potokiem.

**Co mówi PW.6?** (dok. 14, PDF 23)

Narzędzia buildu (kompilator, interpreter, narzędzia budujące) mają być aktualne, sprawdzone i bezpiecznie skonfigurowane. Przykłady:
- *clean build*, czyli ostrzeżenia traktowane jak błędy,
- **budowanie w dedykowanym, ściśle kontrolowanym środowisku**,
- zatwierdzone konfiguracje zapisane jako kod.

Część przykładów dotyczy kompilatorów (np. losowanie układu pamięci) i nie ma sensu dla Pythona. *W naszym projekcie:* sensem PW.6 jest kontrola Dockerfile (hadolint), przypięty obraz bazowy i budowanie na jednorazowym runnerze.

**Czym różnią się PW.7 i PW.8?**

Rodzajem kodu, który się sprawdza:
- **PW.7: kod czytelny dla człowieka** (źródła, skrypty), sprawdzany przez przegląd człowieka albo analizę narzędziem. To **SAST** i code review (dok. 14).
- **PW.8: kod wykonywalny** (uruchomiona aplikacja, binaria), sprawdzany testami. To **DAST**, fuzzing, testy funkcjonalne zabezpieczeń i testy penetracyjne (dok. 15).

To przyda się na obronie: „Semgrep realizuje PW.7, a OWASP ZAP PW.8”.

**Co dokładnie wymaga PW.7?** (dok. 14–15, PDF 23–24)

Najpierw zdecyduj, czy stosujesz przegląd, analizę, czy oba (PW.7.1). Potem wykonaj je i **zapisz oraz posortuj wszystkie znaleziska** w systemie zgłoszeń zespołu (PW.7.2). Przykład wprost o naszym przypadku: narzędzie analizy statycznej automatycznie sprawdza kod, a człowiek przegląda zgłoszone problemy i je naprawia. Inny przykład: wykrywanie niebezpiecznych praktyk automatycznie przy każdym wprowadzeniu kodu do repozytorium. *W naszym projekcie:* SAST na każdym PR, wyniki w formacie SARIF w zakładce Security na GitHubie.

**Co dokładnie wymaga PW.8?** (dok. 15, PDF 24)

Zdecyduj, jakie testy działającego kodu są potrzebne (PW.8.1), a potem je zaplanuj, wykonaj i udokumentuj (PW.8.2). Przykłady:
- testy funkcjonalne mechanizmów bezpieczeństwa,
- **dynamiczne testy podatności w zautomatyzowanym zestawie testów**,
- testy regresji dla podatności, które już raz zgłoszono,
- fuzzing,
- testy penetracyjne, jeśli są zasoby.

*W naszym projekcie:* OWASP ZAP na środowisku testowym oraz testy jednostkowe uwierzytelniania.

**Co mówi PW.9?** (dok. 16, PDF 25)

Ustawienia domyślne mają być bezpieczne „od razu po instalacji”. Ustal bezpieczną linię bazową (PW.9.1), wdroż ją i udokumentuj (PW.9.2). Przykłady: sprawdzaj, czy zatwierdzona konfiguracja jest na miejscu, i trzymaj konfigurację domyślną jako kod pod kontrolą zmian. *W naszym projekcie:* kontener nie działa jako root, infrastruktura w Terraform z bezpiecznymi ustawieniami sprawdzanymi skanerem IaC, wykrywanie dryfu przez `terraform plan`.

---

## 6. Grupa RV: reagowanie na podatności (dok. 16–18; PDF 25–27)

**O co chodzi w RV w jednym zdaniu?**

Podatności i tak się znajdą, także po wydaniu. Trzeba je szybko wykrywać, rozsądnie naprawiać i uczyć się na nich.

**Co mówi RV.1?** (dok. 16–17, PDF 25–26)

Wykrywaj podatności w sposób ciągły:
- **RV.1.1:** zbieraj informacje od użytkowników i ze źródeł publicznych, np. bazy NVD. Ważny przykład: **automatycznie przeglądaj SBOM i dane o składzie, żeby wyłapać nowe podatności** w komponentach, które już są w wydaniu.
- **RV.1.2:** analizuj i testuj kod dalej, także po wydaniu. Przykład: łańcuch narzędzi ma **regularnie albo ciągle skanować wszystkie wspierane wydania**.
- **RV.1.3:** miej politykę ujawniania podatności, czyli sposób, w jaki ktoś z zewnątrz może zgłosić problem, oraz zespół i procedury reagowania.

*W naszym projekcie:* cykliczny workflow (np. raz w tygodniu) ponownie skanuje obraz z produkcji. Nowe CVE pojawiają się codziennie, więc obraz „czysty” w dniu buildu może tydzień później mieć znaną podatność. Do tego `SECURITY.md` dla RV.1.3.

**Co mówi RV.2?** (dok. 17–18, PDF 26–27)

Każdą podatność oceń pod kątem ryzyka (RV.2.1) i zaplanuj odpowiedź (RV.2.2). Odpowiedzią nie zawsze jest naprawa: można też **świadomie zaakceptować ryzyko** albo je przenieść, a do czasu poprawki zastosować obejście. Przykład: dostarczaj poprawki **zautomatyzowanym, zaufanym mechanizmem**. *W naszym projekcie:* Dependabot otwiera PR z poprawioną wersją, PR przechodzi przez cały potok i trafia na produkcję. Zaakceptowane ryzyko to wpis w pliku wyjątków z uzasadnieniem (por. Biswas2025 o wyjątkach w potoku).

**Co mówi RV.3?** (dok. 18, PDF 27)

Nie poprzestawaj na łataniu. Ustal przyczynę (RV.3.1), szukaj powtarzających się wzorców (RV.3.2), usuń całą klasę podobnych błędów (RV.3.3) i popraw sam proces (RV.3.4). Przykład bliski potokowi: **dodaj do łańcucha narzędzi mechanizm, który automatycznie wykryje kolejne wystąpienia tej samej przyczyny**. *W naszym projekcie:* własna reguła Semgrep napisana po znalezieniu konkretnego błędu.

---

## 7. Dodatek A i historia zmian (dok. 24, 27; PDF 33, 36)

**Skąd wziął się SSDF 1.1?**

Rozporządzenie wykonawcze prezydenta USA nr 14028 z 12 maja 2021 r. poleciło NIST opracować wytyczne dla bezpieczeństwa łańcucha dostaw oprogramowania (dok. 24). SSDF 1.1 z lutego 2022 r. jest jedną z odpowiedzi. Dodatek A przypisuje podpunktom sekcji 4e rozporządzenia odpowiednie zadania SSDF. Ten dodatek wystarczy przejrzeć.

**Co zmieniło się między 1.0 a 1.1?** (dok. 27)

Najważniejsze dla nas:
- dodano PO.5 (bezpieczne środowiska wytwarzania) i PS.3.2 (dane o pochodzeniu, SBOM),
- PW.3 scalono z PW.4,
- dodano definicje „provenance”, „artifact” i „evidence”.

Wniosek: tematy łańcucha dostaw weszły do SSDF dopiero w odpowiedzi na EO 14028.

**Czy jest nowsza wersja?**

Stan z 2026-10-05 (csrc.nist.gov): wersja 1.1 nadal obowiązuje. Wersja 1.2 (SP 800-218 Rev. 1) to od 17 grudnia 2025 r. wstępny projekt (*Initial Public Draft*). Uwagi zbierano do 30 stycznia 2026 r. W pracy cytujemy 1.1. Przed złożeniem pracy trzeba sprawdzić, czy 1.2 ma już wersję ostateczną.

---

## 8. SSDF w naszej pracy

**Które zadania SSDF realizuje nasz potok?**

Według wstępnej oceny agenta (tabela w `nist-ssdf.md`, sekcja 2):
- **16 z 42 zadań** potok realizuje w całości albo prawie w całości,
- **15** częściowo (potok dostarcza narzędzie lub dowód, decyzja należy do człowieka),
- **7** to sprawy organizacyjne poza potokiem,
- **4** nie dotyczą projektu jednoosobowego bez dostawców komercyjnych.

Najmocniej pokryta jest grupa PS: podpisy, archiwum, SBOM. Najsłabiej PO.2 (role i szkolenia) i RV.3 (analiza przyczyn).

**Jak SSDF ma się do SP 800-204D?**

SSDF to ogólny katalog praktyk niezależny od technologii. SP 800-204D (2024) przekłada go na zadania w potokach CI/CD i w dodatku A pokazuje, które zadania z potoku realizują które praktyki SSDF. Formuła na obronę: SSDF mówi *co*, a SP 800-204D *gdzie w potoku*.

**Gdzie SP 800-204D i SSDF się nie zgadzają?** (obserwacja agenta, do potwierdzenia)

SP 800-204D w dodatku B (dok. 32, PDF 41) pomija PW.1–PW.4 i PW.7. Uzasadnia to tym, że dotyczą projektowania, przeglądu projektu i ponownego użycia oprogramowania. Tymczasem w samym SSDF:
- **PW.7** to przegląd i analiza kodu, z narzędziem analizy statycznej wprost w przykładach (dok. 14). Przeglądem projektu jest PW.2.
- **PW.4.4** zawiera automatyczne wykrywanie podatności w komponentach w łańcuchu narzędzi (dok. 13), czyli SCA.

SP 800-204D sam wymaga SAST i SCA, ale przypisuje je do PO.4 i PW.8. W naszej liście kontrolnej proponujemy mapowanie według definicji SSDF: SAST → PW.7, SCA → PW.4.4, DAST → PW.8. Podobnie z RV: SP 800-204D uznaje je za politykę organizacji, a SSDF w RV.1.2 wprost oczekuje cyklicznego skanowania przez łańcuch narzędzi. To dobry materiał do dyskusji w 5.3.

**Jakie ograniczenia SSDF warto wymienić w pracy?**

1. To nie lista kontrolna (dok. 3). Ocena potoku wymaga własnej interpretacji i uzasadnienia, co nas nie dotyczy.
2. Duża ogólność. Bez wskazania konkretnego dowodu (job, plik, raport) dwie osoby mogą różnie ocenić to samo zadanie.
3. Część zadań zakłada zespół, np. przegląd przez drugą osobę albo szkolenia według ról.
4. Część przykładów pisano z myślą o językach kompilowanych (PW.6).
5. Wersja 1.1 jest z 2022 r. i nie zna nowszych mechanizmów, takich jak atestacje artefaktów na GitHubie.

---

## Do sprawdzenia w oryginale

Jeśli chcesz podnieść źródło do stanu `tak`, wystarczy przeczytać:
- **dok. 1–4 (PDF 10–13)**: wprowadzenie i opis ram, około 4 stron,
- w tabeli 1 tylko kolumny „Practices” i „Tasks” dla PS, PW.4, PW.7, PW.8 i RV.1 (dok. 9–10, 12–17; PDF 18–19, 21–26).

Zdania z numerem strony albo nazwą konkretnego zadania sprawdzaj w PDF przed wstawieniem do tekstu pracy (zasada stanu `opracowanie`).
