# 0042. Projekt potoku DevSecOps (wariant B): etapy, miejsce kontroli i polityka bramek

- **Status:** przyjęty
- **Data:** 2026-11-20
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [`docs/projekt-potoku.md`](../projekt-potoku.md) (diagram, tabela krok → zagrożenie → standard, polityka bramek, decyzje D1–D13), [0022](0022-obraz-kontenera-aplikacji.md), [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md), [0033](0033-mechanizm-wdrozenia-pull.md), [0036](0036-build-i-publikacja-obrazu.md), [0037](0037-wdrozenie-wariantu-a-z-galezi-bazowej.md), [0041](0041-zamrozenie-wariantu-a.md), zadanie E07-01, `experiment/PROTOCOL.md` (sekcja 0, K2, K4, K5), `docs/narzedzia.md`, [dziennik 2026-11-20](../log/2026-11-20.md)

## Kontekst

Wariant A jest zamrożony tagiem `pipeline-a-v1` (ADR-0041). Wariant B przejmuje z niego joby `lint`, `test` i `build` i dodaje kontrole bezpieczeństwa zgodne z SP 800-204D i OWASP [@NIST-SP800-204D; @OWASP-DevSecOps-Guideline]. Workflow A ma powstawać z workflow B przez usunięcie jobów i kroków bezpieczeństwa (K2). Narzędzia wybrano wcześniej (E02-10, `docs/narzedzia.md`), a o miejscu DAST zdecydowano w E03-05. Do ustalenia zostało:

- gdzie w potoku stoi każda kontrola,
- jak w modelu pull (ADR-0032, ADR-0033) wymusić, że na AWS trafia tylko obraz po wszystkich bramkach,
- co blokuje, a co tylko ostrzega, oraz jak obsłużyć zgłoszenia czystej wersji,
- jak uruchamiać narzędzia.

Katalog zadań przewidywał jeden ADR dla projektu potoku (rezultat E07-01, pierwotnie `0003-projekt-potoku.md`, ale numer 0003 jest zajęty). Dlatego ten ADR zbiera kilka powiązanych decyzji. Szczegóły, w tym diagram, tabela krok → zagrożenie → standard (25 kroków) i progi każdej bramki, są w [`docs/projekt-potoku.md`](../projekt-potoku.md).

## Czynniki decyzyjne

- zgodność z SP 800-204D, SSDF i OWASP [@NIST-SP800-204D; @NIST-SP800-218; @OWASP-Top10-CICD],
- trafność eksperymentu: K2 (różnica A/B tylko w krokach bezpieczeństwa), K5 (progi zamrożone), TW1 (progi niedopasowane do katalogu),
- koszt: czas PR (H2a), liczba fałszywych alarmów (M6, H2b),
- bezpieczeństwo łańcucha dostaw samego potoku (CICD-SEC-8),
- prostota opisu i odtworzenia.

## Rozważane opcje

Pełna lista opcji dla każdego pytania jest w `docs/projekt-potoku.md`, sekcja 5 (pole „Odrzucone” przy każdej decyzji). W skrócie:

| Pytanie | Rozważane opcje |
|---|---|
| Skan obrazu | krok w `build` przed push; osobny job `image-scan`; skan po push z GHCR |
| Obraz dla DAST | artefakt z `build`; osobny build w `dast`; DAST jako krok `build`; na pushu z GHCR |
| Wymuszenie bramek przed wdrożeniem | atestacja jako dowód (agent wdraża tylko obraz z atestacją); job promocji tagu; oba naraz |
| Bramki na pushu | wszystkie; tylko bramki artefaktu; żadne |
| Progi skanerów kodu | wszystko poza poziomem informacyjnym; HIGH+ (Guideline); MEDIUM+; progi dla każdego narzędzia |
| Progi Trivy | config LOW+ i image MEDIUM+ z poprawką; HIGH+ dla obu; MEDIUM+ dla obu |
| Zgłoszenia czystej wersji | lista wyjątków przed serią; poprawienie czystej wersji; bramka tylko na nowe zgłoszenia |
| hadolint i `dependency-review-action` | hadolint bramką, dep-review poza B; oba raportują; oba bramkami; pominąć oba |
| Próg ZAP | ryzyko Medium+; każde `WARN`; lista reguł `FAIL` |
| Wyciszenia w kodzie | ignorować; honorować; honorować i raportować |
| Uruchamianie narzędzi | bezpośrednio (obrazy po digeście, PyPI), akcje minimum; oficjalne akcje narzędzi; mieszane |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-20. Poniżej są tylko powody autora. Rekomendację dla progów Trivy agent przygotował na prośbę autora, a autor ją przyjął.

| # | Decyzja | Powody autora |
|---|---|---|
| D1 | Trivy skanuje obraz w jobie `build` między `docker build` a `docker push` | zgodność z DEPLOY-REQ-5 (skan przed wypchnięciem do rejestru) |
| D2 | `build` zapisuje zeskanowany obraz jako artefakt (`docker save`), a job `dast` uruchamia go przez compose w runnerze | ZAP skanuje ten sam obraz co Trivy |
| D3 | Job `attest` ma `needs:` na wszystkie bramki; agent wdrożenia wdraża digest tylko z ważną atestacją provenance, a brak atestacji oznacza „czekaj” | K2 zachowane: `build`, łącznie z przesunięciem tagu gałęzi, zostaje jak w A |
| D4 | Na pushu (po scaleniu) biegnie ten sam zestaw jobów co na PR | jeden workflow bez warunków |
| D5 | Semgrep, Bandit i zizmor blokują wszystko poza najniższym, informacyjnym poziomem; skutki dla katalogu sprawdzane po przyjęciu zasady | obrona przed TW1, bezpieczny wariant domyślny |
| D5a | Trivy config blokuje LOW i wyżej, Trivy image MEDIUM i wyżej z dostępną poprawką | jedna reguła dla całego potoku, mały koszt |
| D6 | Zgłoszenia czystej wersji obsługuje lista wyjątków (reguła, plik, uzasadnienie, data), zamrożona z progami (K5) | zgodne z Guideline, jawnie widoczne |
| D7 | hadolint blokuje na poziomie `error`; `dependency-review-action` nie wchodzi do wariantu B | dep-review dubluje pip-audit, krótszy PR; hadolint: PW.6.2 (clean build) |
| D8 | ZAP blokuje alerty o ryzyku Medium i High (próg stosowany do raportu JSON) | obrona przed TW1, mniej wyjątków |
| D9 | Narzędzia z oficjalnych obrazów po digeście albo z PyPI w dokładnej wersji; akcje tylko `upload-sarif`, `upload-artifact`/`download-artifact`, `actions/attest` | mniej kodu firm trzecich, czytelność w pracy |
| D10 | Uzupełnienia mapowania SSDF jako interpretacja autora: ATT-2* → PS.2.1, ATT-3* → PS.3.1, skan sekretów → PS.1.1 | wynikają z treści SSDF, pełna tabela, jawna adnotacja |
| D11 | CodeQL, harden-runner, OpenSSF Scorecard, wykrywanie dryfu, cykliczny skan i podpisane commity poza wariantem B | lekki potok, nie pasują do środowiska efemerycznego, czysty pomiar |
| D12 | Przegląd ocen wstępnych tylko dla pozycji użytych w projekcie; reszta przy E13 | projekt na sprawdzonych ocenach, pełny obraz przy E13 |
| D13 | Bramki ignorują `# nosec` i `# nosemgrep` (`--ignore-nosec`, `--disable-nosem`) | jedno miejsce wyjątków, prostsza polityka |

Reguła progów, która wynika z D5, D5a i D8: własny kod i konfiguracja blokują wszystko poza poziomem informacyjnym, a komponenty zewnętrzne i działająca aplikacja blokują od poziomu Medium. Narzędzia bez skali ważności (Gitleaks, pip-audit, actionlint, Checkov bez platformy, kontrola `requirements.txt` ↔ `uv.lock`) blokują każde zgłoszenie.

Zasady polityki bramek przyjęte razem z projektem (`docs/projekt-potoku.md`, sekcja 4.1), wynikające z wcześniejszych decyzji (PROTOCOL, E02-04):

- bramka = job i wymagany *status check* w rulesecie `exp/variant-b`,
- narzędzie zapisuje pełny raport, a osobny krok stosuje próg,
- „fail closed”: brak raportu, błąd narzędzia albo przekroczenie czasu kończy bramkę błędem,
- progi, lista wyjątków i konfiguracja ZAP zamarzają przed serią (K5).

Przegląd ocen (D12) zmienił jedną ocenę: GitOps-REQ-4 ma stosowalność N (środowisko efemeryczne). Tabela B SP 800-204D wchodzi do listy kontrolnej, z ocenami przy E13.

## Konsekwencje

- (+) Każdy krok wariantu B ma przypisane ryzyko CICD-SEC, pozycje katalogu, rekomendację SP 800-204D i zadanie SSDF (`docs/projekt-potoku.md`, sekcja 3). To podstawa rozdz. 4.3 i oceny zgodności (C5).
- (+) Job `build` zostaje jak w wariancie A, a różnica A/B to tylko kroki i joby bezpieczeństwa (K2).
- (+) Na AWS nie trafi obraz bez atestacji, nawet jeśli tag gałęzi przesunie ktoś spoza potoku.
- (+) Progi wynikają z jednej reguły ogólnej, a nie z ważności reguł dla pozycji katalogu (TW1).
- (−) Surowe progi (D5, D5a) zwiększają liczbę zgłoszeń blokujących, więc obniżają precyzję bramek (M6) i zwiększają ryzyko, że H2b nie zostanie potwierdzona.
- (−) Transfer obrazu jako artefaktu (D2) i wszystkie bramki na pushu (D4) wydłużają przebiegi wariantu B (M4, M5).
- (−) DEPLOY-REQ-2 nie ma bezpośredniego pokrycia (D7).
- (−) PR może zmienić konfigurację bramki albo krok bramki przy tej samej nazwie joba; bez drugiego recenzenta to ryzyko resztkowe (materiał do 5.3).
- Kolejne zadania:
  - **E07-09:** agent wdrożenia musi odróżniać „atestacji jeszcze nie ma” (ponów) od „atestacja nieważna” (odrzuć); dziś nie ponawia digestu, który raz się nie powiódł. Weryfikacja włączana tylko dla wariantu B, np. zmienną Terraform,
  - **E07-07:** skan obrazu to krok w `build`, a nie osobny job `image-scan` z katalogu,
  - **E07-02:** jeśli doda harden-runner albo wymóg podpisanych commitów, to zmiana D11 i nowy ADR,
  - **przed zamrożeniem B:** uruchomić bramki na czystej wersji, spisać wyjątki (D6), zapisać wersje w `experiment/versions/variant-b.yaml`, sprawdzić skutki reguły progów dla katalogu i zapisać je w dzienniku,
  - **pilotaż:** czy `docker save`/`docker load` zachowuje obraz tak, że DAST na pushu skanuje digest z produkcji.
- TODO: zweryfikować przed zamrożeniem: nazwy poziomów ważności w Semgrep 1.181.0, zizmorze i hadolint 2.15.1; pewność B105 w Bandit 1.9.4; ryzyko reguł ZAP 10020 i 10098; opcje `--ignore-nosec` i `--disable-nosem`; kody wyjścia wszystkich narzędzi; obrazy z digestami dla narzędzi z D9; filtr ważności w pip-audit.

## Źródła

- [@NIST-SP800-204D]: rekomendacje i identyfikatory w tabeli kroków, w tym DEPLOY-REQ-5 (D1) i DEPLOY-REQ-3 (D3); notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: zadania SSDF w tabeli kroków, PW.6.2 (D7), PS.1.1, PS.2.1, PS.3.1 (D10); notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-Top10-CICD]: ryzyka CICD-SEC w tabeli kroków; notatki `docs/notes/owasp-devsecops.md`, sekcja 3.
- [@OWASP-DevSecOps-Guideline]: „fail closed”, progi wyjściowe i wyjątki (`2-3-5 Security Gates`, D6); notatki `docs/notes/owasp-devsecops.md`, p. 1.5.
- [@Incydent-tj-actions], [@Incydent-Trivy]: przykłady kompromitacji akcji (D9).
- Materiał wewnętrzny: `experiment/PROTOCOL.md`, `experiment/ground-truth.yaml`, `docs/narzedzia.md`, ADR-0022, ADR-0032–ADR-0041, notatki zadań E02-02, E02-03, E02-04, E02-10, E03-07, E05-01, E05-04, E06-05.
