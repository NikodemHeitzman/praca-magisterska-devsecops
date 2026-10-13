# NIST SP 800-204D: pytania kontrolne z odpowiedziami

Ściąga do nauki i na obronę. Uzupełnia [`nist-800-204d.md`](nist-800-204d.md), gdzie są notatki z sekcji i lista kontrolna.

- Odpowiedzi opracował agent (Claude Code) na podstawie tekstu dokumentu [@NIST-SP800-204D].
- Strony podano dwojako: numer z dokumentu i numer w przeglądarce PDF.
- Odpowiedzi do pytań 1–2 uwzględniają poprawki do notatek autora z 2026-10-02.

---

## 1. Rozdz. 4: potoki CI/CD (dok. s. 13–14, PDF 22–23)

**Jakie są dwa cele bezpieczeństwa potoku CI/CD?**

1. Aktywnie bronić samego potoku i procesów budowania: przed włamaniem, podmianą lub dodaniem kroku i kradzieżą sekretów.
2. Zapewnić integralność źródeł i artefaktów, które do potoku wchodzą (kod, zależności, obrazy), czyli pewność, że są tym, za co się podają, i że nikt ich nie zmienił.

Integralność to nie brak podatności. Oryginalna, podpisana biblioteka może mieć znaną podatność (Log4Shell). Integralność potwierdzają podpisy i atestacje, a podatności wykrywają skanery.

**Co dokument rozumie przez „artefakt” i „repozytorium”?**

- **Artefakt** to kod źródłowy i wszystko, co z niego powstaje: buildy, pakiety, a w tym projekcie także obraz Dockera. Każdy artefakt ma właściciela.
- **Repozytorium** to logiczny kontener na artefakty. Tabela 1 rozróżnia cztery rodzaje:

  | Artefakt | Repozytorium | W tym projekcie |
  |---|---|---|
  | własny kod | SCM | GitHub |
  | kod zewnętrzny | menedżer artefaktów | PyPI, Docker Hub |
  | buildy | repozytorium buildów | |
  | pakiety | repozytorium pakietów | rejestr obrazów |

  Zaufania wymagają też SBOM-y i raporty skanów.

**Na czym polega budowanie zaufania w potoku (p. 4.2) i jak ma się do zero trust?**

1. Podmioty wykonujące czynności, także maszyny (runner, orkiestrator), są uwierzytelniane, a potem autoryzowane według polityk. Sama tożsamość nie wystarcza, potrzebne są też uprawnienia.
2. Integralność artefaktów i repozytoriów potwierdza się, weryfikując podpisy cyfrowe. Rzeczom też się nie ufa.
3. Zaufanie ustanawia się wielokrotnie, przy każdym przejściu artefaktu między repozytoriami.
4. Sprawdza się wejścia i wyjścia każdego kroku buildu, czyli czy właściwy krok wykonał właściwy podmiot.

W CI/CD zakres zaufania jest szerszy niż w klasycznym zero trust, który chroni głównie serwery i usługi.

## 2. Wstęp do rozdz. 5 i p. 5.1 (dok. s. 15, PDF 24)

**Jakie warunki trzeba spełnić przed uruchomieniem potoku?**

1. Utwardzić środowisko wykonawcze CI/CD (maszynę wirtualną albo pod).
2. Zdefiniować role osób obsługujących potoki.
3. Nadać szczegółowe uprawnienia do konkretnych zadań. Rola to nie to samo co uprawnienie.
4. Zautomatyzować cały potok narzędziami, w tym SAST, DAST i SCA. Orkiestrator działa na wyższym poziomie zaufania niż pojedyncze kroki.
5. Dla każdego rodzaju kodu określić czynności i wymagania bezpieczeństwa. Rodzaje kodu: aplikacja, infrastruktura jako kod (IaC), polityki jako kod, konfiguracja (YAML).

**Z jakich workflow składa się CI i czego dokument tu nie obejmuje?**

- **Cztery workflow:** operacje budowania, operacje pull i push na repozytoriach (publicznych i prywatnych), aktualizacje oprogramowania, commity kodu. Odpowiadają im kolejno p. 5.1.1–5.1.4.
- **Cele ram dla CI:**
  - obsługa aplikacji cloud-native i innych,
  - standardowe struktury dowodów (metadane, podpisy),
  - wiele platform,
  - wsparcie dla generatorów dowodów (SBOM, podpisy).
- **Poza zakresem:** testowanie artefaktów, które tworzy odporny na manipulację zapis przebiegów testów i ich wyników. Dokument uznaje to za ważny cel, ale go nie omawia.

## 3. P. 5.1.1 Secure Build (dok. s. 16–17, PDF 25–26)

**Jakie trzy zadania są wymagane przy bezpiecznym buildzie?**

1. **Określić politykę buildu:**
   - (a) izolowana, utwardzona platforma,
   - (b) narzędzia, których używa build,
   - (c) uwierzytelnianie i autoryzacja osób uruchamiających build.
2. **Egzekwować tę politykę**, np. agentem i silnikiem polityk.
3. **Równolegle z buildem generować dowody do atestacji**, które przy dostarczeniu oprogramowania pokażą, że build był bezpieczny.

**Czym jest atestacja i jakie są jej rodzaje?**

Atestacja to podpisany dowód. Najpierw zbiera się dane: potwierdzenie izolacji środowiska oraz hashe artefaktu, plików, bibliotek i zdarzeń. Potem zaufany komponent buildu, na który deweloperzy nie mają wpływu, podpisuje je certyfikatem. Dzięki temu odbiorca może sam sprawdzić artefakt, bez polegania na producencie.

Cztery rodzaje atestacji:
1. **Środowiska:** inwentarz platformy, na której biegnie build. Platforma ma być utwardzona i izolowana.
2. **Procesu:** programy, które przekształciły źródła w artefakt (kompilator, narzędzie do pakowania) albo go testowały. Dokument uznaje tę atestację za „best effort”, bo trudno oddzielić ją od materiałów.
3. **Materiałów:** surowe dane wejściowe, czyli konfiguracja, kod źródłowy i zależności.
4. **Artefaktów:** wynik kroku, np. plik binarny albo wynik skanu SAST.

**Dlaczego dowody ma generować coś bardziej zaufanego niż sam build?**

Gdyby build sam o sobie wystawiał zaświadczenie, przejęty build wystawiłby sobie fałszywe. Proces o wyższym poziomie zaufania albo izolacji chroni dowody przed manipulacją. Tu ma znaczenie warunek wstępny o orkiestratorze z wyższym zaufaniem.

**Jakie wymagania dotyczą podpisu i przechowywania atestacji?**

- Atestacje **muszą** być podpisane kryptograficznie bezpiecznym kluczem.
- Miejsce przechowywania **musi** być odporne na manipulację i chronione silną kontrolą dostępu.

Zgodność ocenia podpisana polityka. Sprawdza, czy właściwe podmioty użyły właściwych kluczy, czy są wszystkie wymagane atestacje i jak je oceniać. Daje to dwie gwarancje:
- oprogramowanie zbudowały uprawnione systemy, uprawnionymi narzędziami, we właściwej kolejności,
- nie ma śladów manipulacji.

## 4. P. 5.1.2 Pull/Push na repozytoriach (dok. s. 17–18, PDF 26–27)

**Jakie dwie kontrole są potrzebne przy operacjach PULL i PUSH?**

1. Uwierzytelnianie zgodne z rolą. Osoba z prawem zatwierdzania scaleń nie zatwierdza własnych.
2. Pewność, że kod w repozytorium jest nienaruszony i można na nim dalej pracować.

**Co mówią PULL-PUSH-REQ-1…4?**

- **REQ-1:** automatyczne kontrole każdej zmiany: testy jednostkowe, lintery, testy integralności, kontrole bezpieczeństwa.
- **REQ-2:** w CI uruchamiać tylko narzędzia, których źródłu pochodzenia ufamy. Z tego wynika przypinanie akcji GitHuba do SHA, ale to nasza interpretacja, dokument nie mówi o SHA.
- **REQ-3:** workflow uruchamiane przez PR od zewnętrznych kontrybutorów muszą spełniać jeden z dwóch wariantów:
  - (a) działać w sandboksie bez sieci, uprawnień i dostępu do sekretów, albo
  - (b) czekać na zatwierdzenie przez maintainera z prawem zapisu, w najsurowszym ustawieniu („Require approval for all outside collaborators”).

  **Dotyczy wprost tego projektu, bo repozytorium jest publiczne.** Zagrożenie: kradzież sekretów przez PR z forka (p. 3.1.5).
- **REQ-4:** jeśli SCM nie ma wbudowanych zabezpieczeń, potrzebne jest zewnętrzne narzędzie, które ocenia i poprawia konfigurację SCM, np. OpenSSF Scorecard.

## 5. P. 5.1.3 Software Updates (dok. s. 18–19, PDF 27–28)

**O jakie systemy chodzi i czy dotyczy to projektu?**

Chodzi o systemy aktualizacji oprogramowania: menedżery pakietów, aktualizatory aplikacji i menedżery bibliotek (dokument odwołuje się do The Update Framework, TUF). Atak celuje w generowanie dowodów, żeby nie dało się stwierdzić, czy aktualizacja była prawdziwa.

Wymagania:
- ochrona przed znanymi atakami na podpisywanie i klucze,
- wiele kluczy i progi,
- brak kluczy online dla ról, którym ufają klienci,
- klucze online tylko w HSM i tylko po spełnieniu polityki z 5.1.1.

**Projekt nie dystrybuuje aktualizacji, więc punkt dotyczy go tylko częściowo.** Najbliższy odpowiednik to podpis obrazu bez długoterminowego klucza (Sigstore) i weryfikacja przed wdrożeniem.

## 6. P. 5.1.4 Secure Code Commits (dok. s. 19–20, PDF 28–29)

**Jakie testy mają być w potoku i co z zależnościami?**

- SAST i DAST dla wszystkich używanych języków, z raportami pokrycia dla deweloperów i zespołu bezpieczeństwa.
- Zależności open source **muszą** być wyliczone, zrozumiane i ocenione wobec polityki, np. narzędziem SCA, łącznie z przechodnimi i najlepiej bez limitu głębokości.

**Co mówią COMMIT-REQ-1 i 2?**

- **REQ-1:** sprawdzać commitowany kod pod kątem polityki, w szczególności braku sekretów (klucze, tokeny API). Wykryte sekrety mają być dobrze widoczne (dashboard), z alertami i udokumentowanym sposobem naprawy.
- **REQ-2:** push protection włączone we wszystkich repozytoriach. Obejmuje weryfikację tożsamości i uprawnień, wymuszone podpisywanie commitów i weryfikację nazw plików.

## 7. P. 5.2 CD (dok. s. 20–21, PDF 29–30)

**Co mówią DEPLOY-REQ-1…5?**

Wszystkie realizuje się przez polityki dopuszczania artefaktu do wdrożenia.

- **REQ-1:** skanować kod gotowy do wdrożenia pod kątem sekretów, a samo repozytorium nawet zanim trafi do niego kod. Sekret w publicznym repozytorium oznacza, że już wyciekł.
- **REQ-2:** przed scaleniem PR musi być widać podatne wersje zależności (*dependency review*).
- **REQ-3:** wdrażać tylko artefakt (obraz) wytworzony przez zaufany proces budowania.
- **REQ-4:** musi istnieć dowód, że obraz zeskanowano i atestowano wyniki skanu. Liczy się aktualność skanu, bo bazy podatności stale się zmieniają. Wdrożenie dopuszcza się albo blokuje według polityki organizacji.
- **REQ-5:** okresowo sprawdzać skrypty buildu wydania pod kątem złośliwego kodu. Skanować obraz zaraz po zbudowaniu, przed wypchnięciem do rejestru. Narzędzia do repozytoriów mają być zintegrowane z CD.

**Które dotyczą etapu przed scaleniem, a nie wdrożenia?**

REQ-1 (skan sekretów) i REQ-2 (*dependency review* przed scaleniem PR). Mimo że stoją w części o CD, w potoku działają na etapie PR. To uwaga krytyczna do dyskusji.

## 8. P. 5.2.1 GitOps (dok. s. 21–22, PDF 30–31)

**Jaka jest główna idea GitOps-REQ-1…4?**

Repozytorium Git jest **jedynym źródłem prawdy** o tym, co działa w środowisku.

- **REQ-1:** automatyzacja zamiast ręcznych operacji.
- **REQ-2:** zachowanie pełnych danych każdego wydania: wersje, konfiguracje, metadane.
- **REQ-3:** żadnych ręcznych zmian w środowisku uruchomieniowym. Zmiana idzie przez kod i nowe wydanie.
- **REQ-4:** wykrywanie dryfu, czyli porównywanie stanu faktycznego z zapisanym w Git. Potem automatyczna resynchronizacja albo powiadomienie i ręczna naprawa.

**Co da się zastosować bez Kubernetesa?**

Idea tak, narzędzia (Argo CD, Flux) nie. Odpowiedniki w projekcie:
- REQ-1: Terraform i Ansible uruchamiane z potoku,
- REQ-2: tag obrazu równy SHA commita, zachowane SBOM i atestacje,
- REQ-3: zasada „bez zmian w konsoli AWS”,
- REQ-4: cykliczny `terraform plan`, który wykrywa dryf.

## 9. P. 5.3 Implementation Strategy (dok. s. 22, PDF 31)

**Na jakie typy dokument dzieli rozwiązania?**

Wszystkiego nie da się wdrożyć naraz bez zakłóceń i kosztów, więc rozwiązania dzielą się na cztery typy:
1. Funkcje przy każdym zadaniu potoku:
   - (a) weryfikacja, że oprogramowanie zbudowano poprawnie, czyli wgląd w zależności i kroki buildu. Najczęstszym źródłem zatrutych workflow są skompromitowane zależności i narzędzia,
   - (b) listy kontrolne dla każdego kroku i egzekwowanie ich.
2. Integralność i pochodzenie przez podpisy cyfrowe i atestacje.
3. Pilnowanie, żeby uruchomiony kod był aktualny.
4. Zabezpieczenie klientów CI/CD przed kradzieżą kodu, kluczy i poświadczeń chmurowych, odczytem zmiennych środowiskowych z sekretami i wysyłaniem danych do atakującego.

**Co to jest „build horizon”?**

Granica wieku: kod starszy niż ustalony okres nie jest uruchamiany. Dzięki temu produkcja pozostaje blisko kodu w repozytorium. Można to łatwo zmierzyć w eksperymencie, np. jako wiek wdrożonego obrazu.

## 10. Rozdz. 6 Summary (dok. s. 23, PDF 32)

**Czego dokument świadomie nie rekomenduje i dlaczego?**

- Nie podaje rekomendacji dla konkretnych artefaktów i ram bezpieczeństwa łańcucha dostaw: **SBOM, podpisywania kodu i atestacji**. Ich specyfikacje i standardy wciąż się kształtują w instytucjach rządowych i forach branżowych.
- Pomija też zintegrowane platformy DevSecOps, które obejmują CI i CD w jednym. Są niedojrzałe i nie ma zgody, jakie funkcje bazowe powinny mieć.

**Wniosek dla pracy:** tę lukę uzupełnia specyfikacja SLSA (E02-05).

## Dodatki A i B (dok. s. 26–32, PDF 35–41)

**Do jakich praktyk SSDF przypisano wymagania (dodatek A)?**

| Praktyka SSDF | Co obejmuje | Wymagania z SP 800-204D |
|---|---|---|
| PO.1 | wymagania bezpieczeństwa | polityka buildu i jej egzekwowanie, DEPLOY-REQ |
| PO.2 | role | role i uprawnienia z warunków wstępnych |
| PO.3 | łańcuch narzędzi | automatyzacja |
| PO.4 | kryteria kontroli | SAST, DAST, SCA |
| PO.5 | bezpieczne środowiska | atestacja środowiska, utwardzona platforma |
| PS.1 | ochrona kodu | kontrole przy PULL i PUSH |
| PS.2 | weryfikacja integralności wydania | 5.1.3 |
| PS.3 | archiwizacja wydań | GitOps-REQ-2 |
| PW.5 | bezpieczne kodowanie | PULL-PUSH-REQ-1…4 |
| PW.6 | konfiguracja buildu | atestacja środowiska |
| PW.8 | testy | SAST, DAST, SCA |
| PW.9 | bezpieczne ustawienia domyślne | wymagania dla aplikacji, IaC, polityk i konfiguracji |

Mapowanie jest niepełne. Brakuje COMMIT-REQ, części GitOps-REQ oraz wymagań wobec podpisu i magazynu atestacji.

**Które praktyki pominięto (dodatek B) i dlaczego?**

- **PW.1–PW.4 i PW.7:** projektowanie, przegląd projektu, ponowne użycie. Potok CI/CD przygotowuje środowisko wytwarzania i wdrażania, a nie projekt oprogramowania.
- **RV.1–RV.3:** reagowanie na podatności. To polityka na poziomie organizacji, a nie element potoku.
