# SLSA v1.2: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia [`slsa.md`](slsa.md), gdzie są notatki, tabela wymagań ścieżki Build, przeniesienie na GitHub Actions i ocena docelowego poziomu.

- Odpowiedzi opracował agent (Claude Code) 2026-10-28 na podstawie tekstu specyfikacji v1.2 z gałęzi `releases/v1.2` repozytorium `slsa-framework/slsa` (commit `ae7fc76`). Odpowiedzi o GitHubie oparto na dokumentacji GitHuba i kodzie akcji (źródła na końcu `slsa.md`).
- Specyfikacja jest serwisem HTML bez numeracji stron. Miejsce w źródle podano jako stronę i kotwicę, np. `build-requirements#isolated` oznacza https://slsa.dev/spec/v1.2/build-requirements#isolated. Odpowiada to numerowi strony z innych opracowań: zwykle wystarczy przeczytać jedną sekcję.
- Po przeczytaniu tego pliku źródło [@SLSA-1.2] dostaje `zweryfikowane: opracowanie` (`Zrodla/_Rdzen.md`, zasada 3). Szczegół z nazwą wymagania albo słowem MUST/SHOULD autor sprawdza w oryginale przed wpisaniem do tekstu pracy.
- Odpowiedzi oznaczone **(analiza agenta)** nie pochodzą ze specyfikacji, tylko są wnioskiem z jej tekstu i z dokumentacji GitHuba. Na obronie trzeba je przedstawić jako własną interpretację.

---

## 1. Czym jest SLSA (`about`, `principles`, `tracks`)

**Co znaczy skrót i kto utrzymuje specyfikację?** (`about#what-is-slsa`, README repozytorium)

*Supply-chain Levels for Software Artifacts*, wym. „salsa”. To zbiór wytycznych bezpieczeństwa łańcucha dostaw, które wdraża się stopniowo i które ustalono „konsensusem branżowym”. Projekt należy do OpenSSF (Linux Foundation). Specyfikacja przechodzi etapy Draft → Candidate → Approved. Wersja v1.2 ma status Approved (`spec-stages`).

**Do czego specyfikacja ma służyć?** (`about#what-is-slsa`)

Do czterech rzeczy:
1. wspólnego słownictwa,
2. oceny wiarygodności konsumowanych artefaktów,
3. listy kontrolnej dla własnego oprogramowania,
4. mierzenia zgodności z SSDF.

Czwarte zastosowanie łączy SLSA z [@NIST-SP800-218].

**Dlaczego skanowanie kodu nie wystarcza?** (`about#why-slsa-is-needed`)

Kod może się zmienić po skanie: przez pomyłkę, przez insidera albo przez przejęte konto. Może się to stać na każdym ogniwie od źródła przez build do dystrybucji. SLSA ma dać pewność, że analiza kodu źródłowego nadal dotyczy binarium, które dotarło do odbiorcy. Jako przykłady specyfikacja podaje SolarWinds i Codecov.

> Związek z pracą: uzasadnia, dlaczego potok B ma atestację i weryfikację, a nie tylko skanery (rozdz. 1, 2.2).

**Czego SLSA nie obejmuje?** (`about#what-slsa-doesnt-cover`)

- Jakości kodu i bezpiecznego programowania.
- Zaufania do producenta, który celowo wydaje złośliwe oprogramowanie.
- Zależności przechodnich: poziom artefaktu nie zależy od poziomu jego zależności, a jednego poziomu dla artefaktu z zależnościami nie ma (`faq#q-why-is-slsa-not-transitive`).

**Czym jest ścieżka (*track*) i jakie ścieżki są w v1.2?** (`tracks`)

Ścieżka to osobny aspekt łańcucha dostaw z własnymi poziomami, wymaganiami i zagrożeniami. W v1.2 są dwie:
- **Build** (L0–L3): wiarygodność provenance artefaktu,
- **Source** (L1–L4): wiarygodność procesu tworzenia rewizji kodu, nowość v1.2.

**Co mówi zasada „ufaj platformom, weryfikuj artefakty”?** (`principles#trust-platforms-verify-artifacts`)

Zaufanie ogranicza się do kilku platform (zarządzanie zmianami, build, pakowanie), a artefakty tych platform weryfikuje się automatycznie. Analiza platformy jest ręczna i droga, a weryfikacja artefaktu tania. Wniosek: liczbę zaufanych platform trzeba minimalizować.

---

## 2. Model i pojęcia (`terminology`)

**Jakie role wyróżnia specyfikacja?** (`terminology#roles`)

- Producent tworzy i udostępnia oprogramowanie.
- Weryfikator sprawdza provenance.
- Konsument używa oprogramowania i może weryfikować sam albo delegować weryfikację.
- Dostawca infrastruktury utrzymuje np. rejestr albo platformę budowania.

Jedna osoba może pełnić kilka ról.

**Jak wygląda model buildu?** (`terminology#build-model`)

1. Najemca (*tenant*) wywołuje build, podając parametry zewnętrzne.
2. Płaszczyzna sterowania (*control plane*) interpretuje parametry, pobiera zależności i tworzy środowisko buildu.
3. Kroki buildu w środowisku kontroluje najemca. Platforma izoluje środowiska od siebie, a stopień tej izolacji mierzy poziom Build.
4. Od L2 płaszczyzna sterowania wydaje provenance.

**Czym różni się parametr zewnętrzny od zależności?** (`terminology#build-model`)

Parametr zewnętrzny to wartość literalna podana przez najemcę, np. adres repozytorium albo ścieżka workflow. Zależność to artefakt pobrany w trakcie buildu, np. kod źródłowy, narzędzie albo plik konfiguracyjny. Model nie ma pojęcia „źródła”: odwołanie do repozytorium jest parametrem, a samo repozytorium zależnością.

**Kto w modelu jest zaufany, a kto nie?** (`terminology#build-model`, tabela pojęć)

Zaufana jest platforma (oprogramowanie, sprzęt, ludzie i organizacje, którym trzeba ufać, że wykonają build wiernie) i jej płaszczyzna sterowania. Najemca jest „niezaufanym użytkownikiem”, który definiuje kroki i parametry.

**Dlaczego specyfikacja unika słowa *builder*?** (`terminology`, „Ambiguous terms to avoid”)

Bo może znaczyć platformę, środowisko, osobę uruchamiającą build albo narzędzie. Specyfikacja używa „build platform”. Wyjątkiem jest pole `builder.id` w provenance.

---

## 3. Poziomy Build (`build-track-basics`)

**Jakie są poziomy i przed czym chronią?** (`build-track-basics`, tabela na początku)

| Poziom | Wymaganie | Cel |
|---|---|---|
| L0 | brak | — |
| L1 | provenance pokazuje, jak zbudowano pakiet | pomyłki, dokumentacja |
| L2 | podpisane provenance z hostowanej platformy budowania | manipulacja po buildzie |
| L3 | utwardzona platforma budowania | manipulacja w trakcie buildu |

**Co daje L1 i dlaczego to mało?** (`build-track-basics#build-l1`)

Provenance istnieje, ale można je „trywialnie obejść lub sfałszować”, bo może być niepełne i niepodpisane. Wystarcza do wykrywania pomyłek, np. buildu z commita, którego nie ma w repozytorium upstream. Pomaga też inwentaryzować oprogramowanie.

**Co dodaje L2?** (`build-track-basics#build-l2`)

- Build działa na platformie hostowanej, która sama generuje i podpisuje provenance.
- Konsument sprawdza autentyczność provenance.

Fałszerstwo wymaga jawnego „ataku”, choć może być łatwe. Odstrasza przeciwników, którzy ponoszą ryzyko prawne lub finansowe (np. pracowników). Podpis cyfrowy chroni przed manipulacją po buildzie.

**Co dodaje L3?** (`build-track-basics#build-l3`)

Platforma ma silne zabezpieczenia, żeby:
- przebiegi buildu nie wpływały na siebie, nawet w ramach jednego projektu,
- sekret do podpisu provenance nie był dostępny dla kroków buildu zdefiniowanych przez użytkownika.

Fałszerstwo wymaga wtedy wykorzystania podatności, która przekracza możliwości większości przeciwników. Według specyfikacji L3 jest przeznaczony dla „większości wydań oprogramowania” i zwykle wymaga istotnych zmian istniejącej platformy.

**Czy „SLSA 4” istnieje?** (`build-track-basics`, uwaga pod tabelą; `future-directions#build-l4`)

Nie w v1.x. Numeracja SLSA 1–4 pochodzi z wersji v0.1, w której źródło i build były razem. Build L4 to tylko kierunek rozwoju. Mógłby obejmować przypięte zależności, buildy hermetyczne, pełną listę zależności w provenance i buildy odtwarzalne. Specyfikacja zastrzega, że te wymagania „mogą, ale nie muszą” się w nim znaleźć.

---

## 4. Wymagania (`build-requirements`)

**Jak podzielono odpowiedzialność?** (`build-requirements#build-levels`)

Platforma MUSI wzmocnić zabezpieczenia, żeby osiągnąć dany poziom. Producent MUSI wybrać platformę zdolną do docelowego poziomu i stosować zabezpieczenia, które ta platforma określa.

**Jakie wymagania ma producent?** (`build-requirements#producer`)

Trzy, na wszystkich poziomach (MUST):
1. wybrać odpowiednią platformę,
2. budować w spójny sposób, żeby weryfikator mógł ustalić, jak wygląda „poprawny” build,
3. dystrybuować provenance (może to przekazać ekosystemowi pakietów).

Bardziej szczegółowe wymagania z v0.1 (np. *scripted build*) usunięto w v1.0.

**Jakie wymagania ma platforma?** (`build-requirements`, tabela „Build levels”)

| Grupa | Wymaganie | Od poziomu |
|---|---|---|
| Generowanie provenance | istnieje (*Exists*) | L1 |
| Generowanie provenance | autentyczne (*Authentic*) | L2 |
| Generowanie provenance | niepodrabialne (*Unforgeable*) | L3 |
| Siła izolacji | hostowana (*Hosted*) | L2 |
| Siła izolacji | izolowana (*Isolated*) | L3 |

**W jakich trzech wymiarach ocenia się provenance?** (`build-requirements#provenance-generation`)

- Kompletność: co zawiera.
- Autentyczność: jak mocno da się je powiązać z platformą.
- Dokładność: jak trudno je zmienić od wewnątrz procesu buildu.

**Co znaczy „provenance istnieje” (L1)?** (`build-requirements#provenance-exists`)

Proces buildu MUSI generować provenance, które jednoznacznie identyfikuje pakiet digestem kryptograficznym i opisuje jego powstanie. Format MUSI być akceptowany przez ekosystem lub konsumenta. Zalecany jest SLSA Provenance. Kompletność to „best effort”, a autentyczność i dokładność nie mają wymagań.

**Co znaczy „provenance autentyczne” (L2)?** (`build-requirements#provenance-authentic`)

- Konsument MUSI móc sprawdzić autentyczność. POWINNO się to odbywać przez podpis kluczem dostępnym tylko dla komponentu platformy, który wygenerował provenance. Zalecane są metody z logiem przejrzystości.
- Provenance MUSI generować płaszczyzna sterowania, a nie najemca.
- Dane MUSZĄ pochodzić od platformy.
- Platforma MUSI mieć jakąś kontrolę przeciw manipulacji przez najemcę, przy czym „nie ma dolnej granicy siły”.
- Wyjątek: `subject` (nazwy i digesty wyjść) oraz pola niewymagane na L2 może podać najemca.

**Co znaczy „provenance niepodrabialne” (L3)?** (`build-requirements#provenance-unforgeable`)

- Provenance MUSI być silnie odporne na fałszerstwo przez najemców.
- Sekret do uwierzytelnienia provenance MUSI być w bezpiecznym magazynie, dostępny tylko dla konta usługi buildu i NIE MOŻE być dostępny dla środowiska, w którym działają kroki użytkownika.
- Każde pole MUSI wygenerować albo sprawdzić platforma.
- Parametry zewnętrzne MUSZĄ być w pełni wyliczone.

**Co znaczy „hostowana” (L2)?** (`build-requirements#hosted`)

Wszystkie kroki buildu działają na platformie hostowanej, a nie na stacji roboczej. Specyfikacja podaje wprost GitHub Actions jako przykład.

**Jakie gwarancje daje „izolowana” (L3)?** (`build-requirements#isolated`)

Pięć zakazów (MUST NOT):
1. build nie ma dostępu do sekretów platformy, np. klucza podpisu provenance,
2. buildy równoległe nie wpływają na siebie,
3. build nie wpływa na środowisko następnego buildu, więc każdy build MUSI mieć efemeryczne środowisko,
4. build nie może zatruć cache innego buildu; wynik MUSI być identyczny z cache i bez niego,
5. platforma nie otwiera usług zdalnego wpływu, chyba że są one ujęte w `externalParameters`.

**Czy „izolowana” znaczy „hermetyczna”?** (`build-requirements#isolated`, uwagi na końcu)

Nie. Hermetyczność, czyli build bez dostępu do sieci, jest w kierunkach rozwoju. L3 nie zabrania też buildowi wywoływać usług zewnętrznych ani runnerów samohostowanych spoza granicy zaufania. Zapewnia tylko, że build w dobrej wierze przebiega bezpiecznie.

**Czy wymagania ścieżki Build zmieniły się od v1.0?** (`whats-new`; porównanie wersji)

Według stron „What's new” v1.1 zmieniła VSA i model zagrożeń, a v1.2 dodała ścieżkę Source. Agent porównał linie normatywne sekcji „Build Platform” w v1.0 i v1.2 i są identyczne. Dlatego deklaracje GitHuba odnoszące się do v1.0 można stosować do v1.2.

---

## 5. Provenance i dystrybucja (`build-provenance`, `distributing-provenance`)

**Z czego składa się SLSA Provenance?** (`build-provenance#model`)

- `buildDefinition`:
  - `buildType`: szablon procesu,
  - `externalParameters`: niezaufane, MUSZĄ być w provenance i MUSZĄ być weryfikowane,
  - `internalParameters`: ustawia platforma, są opcjonalne,
  - `resolvedDependencies`: zależności, jeśli są znane.
- `runDetails`:
  - `builder.id`: zaufana platforma,
  - `metadata`.
- `subject`: wyjścia z digestami.

Predykat ma typ `https://slsa.dev/provenance/v1` i siedzi w zestawieniu in-toto.

**Gdzie publikuje się provenance?** (`distributing-provenance#where-attestations-are-published`)

Producent MUSI opublikować provenance w co najmniej jednym miejscu i POWINIEN w kilku:
- przy wydaniu w repozytorium źródłowym,
- obok artefaktu w rejestrze,
- gdziekolwiek, z wpisem w logu przejrzystości (np. Rekor).

Docelowo rejestry POWINNY przechowywać provenance, bo klient i tak im ufa i od nich zależy.

**Czy atestację można nadpisać?** (`distributing-provenance#immutability-of-attestations`)

Nie powinno się. Atestacje POWINNY być niezmienne, a nowe provenance oznacza nowe wydanie.

**Jak SLSA Provenance ma się do SBOM?** (`faq#q-how-does-slsa-and-slsa-provenance-relate-to-sbom`)

To dwa różne poziomy abstrakcji:
- SBOM drobnoziarniście opisuje składniki artefaktu (podatności, licencje),
- provenance gruboziarniście opisuje build, a kompletność jego `resolvedDependencies` to „best effort”.

Obecne formaty SBOM uznano za nieodpowiednie dla ścieżki Build. SBOM może wejść do przyszłej ścieżki podatności, a provenance może zwiększyć wiarygodność SBOM, bo opisuje, jak SBOM powstał.

> Związek z pracą: uzasadnia oba joby, SBOM (E07-08) i provenance (E07-09).

---

## 6. Weryfikacja (`verifying-artifacts`)

**Dlaczego weryfikacja jest konieczna?** (wstęp strony)

Provenance „nic nie daje, dopóki ktoś jej nie sprawdzi”. Weryfikacja to część SLSA, a nie dodatek.

**Jakie są kroki weryfikacji?** (`verifying-artifacts#how-to-verify`)

1. **Poziom Build:**
   - konfiguracja korzeni zaufania (tożsamość klucza i `builder.id` → maksymalny poziom),
   - sprawdzenie podpisu koperty,
   - porównanie `subject` z digestem artefaktu,
   - kontrola `predicateType`,
   - odczyt poziomu, domyślnie L1.
2. **Oczekiwania:** porównanie co najmniej tożsamości buildera, kanonicznego repozytorium, `buildType` i `externalParameters`.
3. **Opcjonalnie:** rekurencyjna kontrola zależności, np. przez VSA.

**Co z nierozpoznanymi parametrami zewnętrznymi?** (`verifying-artifacts#step-2-check-expectations`)

POWINNY powodować odrzucenie, żeby zachować ostrożność. Dopuszczalny jest zakres wartości, jeśli każda wartość z zakresu jest bezpieczna.

**Skąd biorą się oczekiwania?** (`verifying-artifacts#forming-expectations`)

Z jednego z trzech modeli:
- zaufanie przy pierwszym użyciu,
- oczekiwania określone przez producenta,
- oczekiwania zapisane w repozytorium źródłowym (tak działa Go).

Oczekiwania są przypisane do nazwy pakietu, a provenance do artefaktu.

**Gdzie można weryfikować?** (`verifying-artifacts#architecture-options`)

W ekosystemie pakietów przy publikacji (RECOMMENDED), u konsumenta przy instalacji lub wdrożeniu albo w monitorze. Co najmniej jedno z tych miejsc POWINNO być użyte.

**Czy L3 chroni przed złośliwym administratorem platformy?** (`verifying-artifacts#step-1-check-slsa-build-level`)

Nie. L3 nie obejmuje kompromitacji samej platformy, np. przez insidera. Weryfikator decyduje, którym platformom zaufać (`assessing-build-platforms`).

---

## 7. Zagrożenia (`threats`)

**Jak podzielono zagrożenia?** (`threats#overview`)

Na etapy (A)–(I):
- źródło: (A) producent, (B) modyfikacja źródła, (C) system kontroli wersji,
- build: (D) parametry zewnętrzne, (E) proces buildu, (F) publikacja artefaktu, (G) kanał dystrybucji,
- użycie: (H) wybór pakietu, (I) użycie.

Osobno ujęto zagrożenia zależności, dostępności i weryfikacji.

**Jakie przykłady zagrożenia (D) dotyczą GitHub Actions?** (`threats#d-external-build-parameters`)

- Build z nieoficjalnego forka albo z niechronionej gałęzi.
- Build z innego workflow (`debug.yml` zamiast `release.yml`).
- Build z parametrem z `github.event.inputs`, który wstrzykuje flagę kompilatora.

Środek zaradczy to porównanie provenance z oczekiwaniami, do czego wystarcza L1.

**Które zagrożenia procesu buildu (E) usuwa dopiero L3?** (`threats#e-build-process`)

- Wpływ jednego buildu na drugi (np. podmiana plików albo binarium `make` na tej samej maszynie).
- Kradzież sekretów kryptograficznych (klucz podpisu na workerze buildu).
- Zatrucie cache buildu.

L2 chroni przed fałszowaniem provenance i przed kompromitacją właściciela projektu.

**Czy podanie fałszywego digestu w provenance to problem?** (`threats#forged-digest`)

Nie. Provenance twierdzi tylko, że artefakt zbudowano, a nie że go opublikowano. Weryfikator i tak odrzuci artefakt, jeśli nie zgadza się źródło.

**Jak L1 i L2 chronią przed zagrożeniem (F)?** (`threats#f-artifact-publication`)

- L1: odrzucenie pakietu bez provenance i porównanie `subject` z hashem pakietu, co wykrywa modyfikację po CI/CD.
- L2: podpis, co wykrywa przeróbkę provenance. Przykład w specyfikacji: build w GitHub Actions z `evil/my-package` z provenance przerobionym na `good/my-package`.

---

## 8. Ścieżka Source (`source-requirements`)

**Jakie są poziomy ścieżki Source?** (`source-requirements#basics`)

- L1: system kontroli wersji.
- L2: ciągła, niezmienna historia i *Source Provenance*.
- L3: ciągłe egzekwowanie kontroli technicznych.
- L4: przegląd przez dwie zaufane osoby.

**Dlaczego praca nie ocenia ścieżki Source?** (`source-requirements#source-summary`; analiza agenta)

- Od L1 system kontroli wersji MUSI wydawać *Source VSA*, a bez niego rewizja ma L0. GitHub nie wydaje VSA natywnie (stan wymaga sprawdzenia, TODO).
- L4 wymaga dwóch recenzentów, więc w projekcie jednoosobowym jest nieosiągalny.
- Pytania badawcze dotyczą buildu i artefaktu.

---

## 9. SLSA na GitHub Actions (dokumentacja GitHuba, kod akcji)

**Jaki poziom deklaruje GitHub?** (GitHub Docs, „Artifact attestations”, sekcja o poziomach SLSA)

Same artifact attestations dają „SLSA v1.0 Build Level 2”. Build w reusable workflow z atestacjami pozwala według GitHuba osiągnąć Build L3 (strona „…achieve SLSA v1 Build Level 3”).

**Skąd pochodzi treść provenance z `actions/attest`?** (`actions/toolkit`, `packages/attest/src/provenance.ts`)

Z claimów tokenu OIDC, który podpisuje GitHub:
- `externalParameters.workflow`: ref, repozytorium, ścieżka,
- `internalParameters`: zdarzenie, identyfikatory, `runner_environment`,
- `resolvedDependencies`: tylko commit,
- `builder.id` = workflow, który wykonał atestację (`job_workflow_ref`).

Treść nie zawiera `inputs` ani `vars` workflow.

**Jak podpisywane jest provenance?** (GitHub Docs, „How GitHub generates artifact attestations”)

Przez Sigstore. Repozytoria publiczne używają instancji Public Good z wpisem w publicznym, niezmiennym logu przejrzystości, a prywatne instancji GitHuba bez logu.

**Dlaczego atestacja w jednym jobie z buildem nie daje L3?** **(analiza agenta)**

Uprawnienie `id-token: write` dotyczy całego joba. Każdy krok joba, także krok buildu albo akcja zewnętrzna, może pobrać token OIDC i podpisać dowolne provenance tą samą tożsamością. Narusza to wymaganie, żeby sekret uwierzytelniający provenance był niedostępny dla kroków użytkownika (`build-requirements#provenance-unforgeable`, `#isolated`). `slsa-github-generator` rozwiązuje to osobnymi jobami (osobnymi VM) do buildu i do provenance w zaufanym reusable workflow.

**Czy `slsa-github-generator` to dobra droga do L3?** (README generatora, stan 2026-10-28)

Nie. Projekt „nie jest już aktywnie utrzymywany”. Ostatnie wydanie to v2.1.0 z lutego 2025, a sam projekt zaleca artifact attestations GitHuba.

**Jakie flagi `gh attestation verify` odpowiadają krokom weryfikacji SLSA?** (`cli/cli`, `pkg/cmd/attestation/verify/verify.go`)

- Domyślnie wymagany jest predykat `https://slsa.dev/provenance/v1` (krok 1, `predicateType`).
- `--repo` lub `--owner`: kanoniczne repozytorium.
- `--signer-workflow` lub `--signer-repo`: tożsamość buildera; obowiązkowe przy reusable workflow.
- `--source-ref`, `--source-digest`: gałąź i commit źródła.
- `--deny-self-hosted-runners`: wymaganie „hostowana”.

Nierozpoznanych parametrów zewnętrznych `gh` sam nie odrzuca.

---

## 10. Pytania na obronę

**„Jaki poziom SLSA osiąga potok i jak to udowodniono?”**

Progiem hipotezy H3b jest L2, a L3 to cel rozszerzony (wariant A, decyzja autora z 2026-10-28, `slsa.md`, sekcja 4). Osiągnięty poziom podaje wynik M8 po eksperymencie. Dowodem jest tabela wymagań ścieżki Build (`slsa.md`, sekcja 2). Dla każdego wymagania podaje ona miejsce w specyfikacji i dowód z potoku: atestację, wynik `gh attestation verify`, konfigurację workflow i test negatywny. Poziomu nie przyjmuje się z deklaracji GitHuba, tylko sprawdza wymaganie po wymaganiu.

**„GitHub deklaruje L3 przy reusable workflow. Dlaczego nie przyjęto tego wprost?”** **(analiza agenta)**

L3 zakłada, że płaszczyzna sterowania jest poza kontrolą najemcy. W projekcie jednoosobowym autor pisze i workflow wywołujący, i reusable workflow, więc rozdział ról jest umowny. Do tego reusable workflow z atestacją w tym samym jobie co build nie spełnia litery wymagania o niedostępności sekretu.

**„Czy SLSA mówi coś o podatnościach w aplikacji?”**

Nie. SLSA dotyczy integralności buildu i pochodzenia artefaktu (`about#what-slsa-doesnt-cover`). Podatności wykrywają skanery w potoku. SLSA zapewnia, że wdrażany artefakt pochodzi z kodu, który skanery sprawdziły.

**„Czym SLSA różni się od SP 800-204D?”**

SP 800-204D podaje strategie i rekomendacje, ale celowo nie specyfikuje formatów SBOM ani atestacji (rozdz. 1.2, 6). SLSA daje format provenance, mierzalne poziomy i procedurę weryfikacji. BUILD-3* z 800-204D, czyli dowody generowane w procesie o wyższym zaufaniu niż build, odpowiada wymaganiom L2/L3 dotyczącym płaszczyzny sterowania.

**„Skoro weryfikacja jest w tym samym potoku, ktoś może ją usunąć.”** **(analiza agenta)**

Tak. To ograniczenie opisane w `slsa.md`, sekcja 3.4. SLSA dopuszcza weryfikację przez konsumenta przy wdrożeniu (`verifying-artifacts#consumer`). Silniejsze warianty, np. kontrola dopuszczenia po stronie AWS albo chroniony workflow wdrożeniowy, wykraczają poza zakres pracy.
