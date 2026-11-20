# 0039. Zbieranie czasów potoku: skrypt w Pythonie bez zależności, lista ID przebiegów, wynik w JSON i trzech CSV

- **Status:** proponowany
- **Data:** 2026-11-20
- **Decydujący:** autor pracy
- **Powiązane:** [0035](0035-workflow-ci-lint-i-testy.md), [0038](0038-seria-czasowa-bez-cache.md), zadanie E06-04, `experiment/scripts/collect_timings.py`, `experiment/PROTOCOL.md` (P4, P5, 2.3, K12), `docs/metodyka.md` (p. 3.2, M4, M5), [dziennik 2026-11-20](../log/2026-11-20.md)

## Kontekst

M4 i M5 liczymy z GitHub REST API (`docs/metodyka.md`, p. 3.2):

- T_czek = max `completed_at` − min `created_at`,
- T_wyk = max `completed_at` − min `started_at`,
- oba po jobach próby 1 przebiegu (`/actions/runs/{run_id}/attempts/1/jobs`),
- rozbicie M5 z czasów kroków.

Protokół wymaga zapisu surowych odpowiedzi API (P4), wersji obrazu runnera „z logu joba” przy każdym przebiegu (2.3, pkt 4) i jednego skryptu dla obu wariantów (K12). Trzeba ustalić, co skrypt liczy, czym rozmawia z API, skąd wie, które przebiegi pobrać, jakie pliki zapisuje i gdzie leży.

Sprawdzenie API na przebiegu 44736780743 (2026-11-20):

- obiekt joba ma pola `created_at`, `started_at`, `completed_at`, `runner_name` i `labels` oraz listę kroków z `started_at` i `completed_at`, z dokładnością do sekundy,
- wersji obrazu runnera w API nie ma. Jest w logu joba (`/actions/jobs/{job_id}/logs`), w grupie `Runner Image` (`Image: ubuntu-24.04`, `Version: 20261116.376.1`), obok wersji programu runnera (`Current runner version`) i grupy `Runner Image Provisioner` z chmurą i regionem maszyny (`Cloud: Azure`, `Region: eastus2`).

## Czynniki decyzyjne

- zgodność z definicjami M4 i M5 oraz z P4 i 2.3 protokołu,
- powtarzalność zbioru danych,
- łańcuch dostaw: liczba zależności do przypinania (AGENTS.md, zasady 5 i 6),
- czytelność skryptu i danych dla recenzenta,
- prostota.

## Rozważane opcje

Zakres skryptu:

1. zbiera dane i liczy T_czek i T_wyk, statystyka w analizie (E09, E13)
2. tylko zbiera dane, wszystkie wyliczenia w analizie
3. zbiera, liczy i podsumowuje (mediana, p90, min, max dla każdej pary wariant–wyzwalacz)

Klient API:

1. biblioteka standardowa Pythona (`urllib`)
2. `requests` jako zależność skryptu uv (PEP 723), uruchamianie przez `uv run`
3. `gh api` wywoływane z `subprocess`

Wybór przebiegów:

1. jawna lista ID przebiegów z wariantem, wyzwalaczem i numerem kolejnym
2. filtr z API: workflow, gałąź, zdarzenie, okno czasu
3. oba sposoby

Wersja obrazu runnera:

1. skrypt czyta log każdego joba
2. skrypt czyta log jednego joba na przebieg
3. poza skryptem (skrypt wywołujący serię albo zapis ręczny)

Pliki wynikowe:

1. surowy JSON na przebieg i trzy CSV: przebiegi, joby, kroki
2. surowy JSON i dwa CSV: przebiegi oraz kroki z kolumnami joba

Położenie: `experiment/scripts/` obok `validate_ground_truth.py` albo `experiment/`, jak w definicji zadania.

## Decyzja

Wybrano: **skrypt `experiment/scripts/collect_timings.py` na bibliotece standardowej, który zbiera dane i liczy T_czek i T_wyk dla przebiegów z jawnej listy ID, czyta wersję obrazu runnera z logu każdego joba i zapisuje surowy JSON oraz trzy CSV.** Powody autora:

- **Zbiera i liczy T_czek i T_wyk:**
  - wzory przy danych: definicje z metodyki są w jednym miejscu, a analiza dostaje gotowe czasy przebiegów,
  - szybkie sprawdzenie: od razu widać wynik do porównania z interfejsem GitHub (pilotaż, znaczenie `created_at`),
  - mniej pracy później: analiza w E09 i E13 będzie prostsza.
- **Biblioteka standardowa:**
  - brak zależności: nic do przypinania i aktualizowania,
  - czytelność: każde zapytanie do API widać wprost w kodzie.
- **Jawna lista ID:**
  - powtarzalność: ta sama lista zawsze daje ten sam zbiór danych, niezależnie od tego, co później pojawi się w repozytorium,
  - prostota: mniej logiki w skrypcie.
- **Log każdego joba:** zgodność z protokołem (2.3, pkt 4: „z logu joba”).
- **JSON i trzy CSV:**
  - jeden poziom szczegółowości na plik, bez powtarzania danych joba w wierszach kroków,
  - czytelność: każdy plik łatwo otworzyć i sprawdzić ręcznie.
- **`experiment/scripts/`:**
  - porządek w katalogu: wszystkie skrypty eksperymentu w jednym miejscu,
  - spójność z `validate_ground_truth.py`.

Postać skryptu (decyzje agenta przy implementacji):

- **Wejście:** plik CSV z kolumnami `run_id`, `variant` (`A`/`B`), `trigger` (`pr`/`main`), `seq`, `role` (`warmup`/`measure`/`pilot`). Skrypt sprawdza zgodność wyzwalacza ze zdarzeniem przebiegu: `pr` wymaga `pull_request`, `main` wymaga `push`.
- **Odczyt:** obiekt przebiegu, joby próby 1, log każdego joba. Skrypt kończy się błędem, gdy przebieg albo job nie jest zakończony.
- **Wynik:**
  - `raw/<run_id>-run.json` i `raw/<run_id>-jobs.json`: odpowiedzi API bez zmian (strony listy jobów połączone w jedną),
  - `raw/<run_id>-runner.json`: wartości odczytane z logu każdego joba, żeby CSV dało się przeliczyć bez sieci (`--from-raw`), także po wygaśnięciu logów,
  - `runs.csv`: etykiety z listy, zdarzenie, gałąź, commit, numer próby przebiegu (`run_attempt`, żeby wykryć ponowne uruchomienie), wynik, T_czek, T_wyk i kolejka pierwszego joba (T_czek − T_wyk) w sekundach,
  - `jobs.csv`: czasy joba, kolejka joba (`started_at` − `created_at`), runner, etykiety oraz z logu: wersja programu runnera, obraz, wersja obrazu, chmura i region,
  - `steps.csv`: czas każdego kroku d(s).
- **Logi:** skrypt nie zapisuje całych logów, tylko wartości z grupy `Runner Image` i wersję runnera.
- **Joby pominięte** (`conclusion: skipped`) trafiają do `jobs.csv`, ale nie wchodzą do T_czek i T_wyk. Metodyka mówi o „jobach próby”. W wariancie A nie ma jobów warunkowych, więc reguła dotyczy dopiero wariantu B. TODO: zweryfikować w pilotażu, jakie znaczniki czasu API daje jobom pominiętym.
- **Token:**
  - ze zmiennej `GH_TOKEN` albo `GITHUB_TOKEN`, a gdy ich nie ma, z `gh auth token`,
  - wystarczy odczyt publicznego repozytorium,
  - nagłówek `Authorization` nie przechodzi przez przekierowanie: endpoint logów odpowiada przekierowaniem 302 na adres pobrania poza api.github.com.
- **Testy:** `unittest` z biblioteki standardowej, na zapisanej odpowiedzi API i fragmencie logu, bez sieci.

## Konsekwencje

- (+) Skrypt działa na samym Pythonie, bez instalacji pakietów (lokalnie przez `uv run --no-project`, bo na komputerze autora nie ma `python` w PATH).
- (+) Wariant, wyzwalacz i rola przebiegu pochodzą z listy, a nie z nazwy gałęzi. Przebiegi `push` i `pull_request` na tej samej gałęzi PR (otwarta kwestia z ADR-0035) nie mieszają się, bo do danych trafia tylko to, co jest na liście.
- (−) Listę ID musi ktoś przygotować. W serii E09 zrobi to skrypt wywołujący przebiegi, który zapisze ID każdego wywołanego przebiegu. Do tego czasu lista jest ręczna.
- (−) Logi jobów są przechowywane przez ograniczony czas (według dokumentacji GitHub domyślnie 90 dni), więc dane trzeba zebrać niedługo po serii. Odpowiedzi API z czasami i wartości z logów zapisujemy od razu.
- (−) Czasy z API mają dokładność do sekundy. Krótkie kroki (np. `ruff check`) mają czas 0–1 s. Dla M5 wystarczy, bo skanery trwają dłużej. TODO: zweryfikować w pilotażu.
- (−) Wzory T_czek i T_wyk są w skrypcie, więc zmiana definicji w metodyce wymaga zmiany skryptu i ponownego przeliczenia z zapisanego JSON (sieć nie jest do tego potrzebna).
- Struktura `experiment/data/` (P4, TODO z E09) dostaje pierwszy element: katalog serii z listą przebiegów, `raw/` i trzema CSV.
- Pilotaż pokazał, że chmura, region i wersja obrazu runnera nie są jedną wartością na przebieg (sekcja „Weryfikacja”). Dlatego skrypt zapisuje je dla każdego joba, a mitygację TN2 w metodyce (p. 4.5) i protokół (2.3, pkt 4; 5.2) zmieniono 2026-11-20 decyzją autora: rejestr dla każdego joba i porównanie rozkładów w obu wariantach zamiast porównania „przed i po zmianie obrazu”.

## Weryfikacja

2026-11-20, wszystkie 15 przebiegów `baseline-ci` wariantu A z 16–20 listopada (E06-01, E06-02, E06-03 i przebieg PR #5 tego zadania; lista w `experiment/data/pilot-e06-04/manifest.csv`, rola `pilot`, poza wynikami eksperymentu, P5). Pięć pierwszych przebiegów ma dwa joby (`lint`, `test`), bo job `build` doszedł w E06-02.

| Sprawdzenie | Wynik |
|---|---|
| Testy `unittest` (14) na zapisanej odpowiedzi API i nagłówku logu | wszystkie przechodzą |
| Zbieranie z API: 15 przebiegów, 40 jobów, 380 kroków | bez błędów i bez ostrzeżeń; wartości odczytane z 40 logów |
| Czasy jobów kontra notatki E06-02 i E06-03 | zgodne: PR 43923746792 lint 11 s, test 39 s, build 19 s; push 43923993380 8 s, 43 s, 42 s; push 44736780743 8 s, 37 s, 34 s |
| Czasy w interfejsie GitHub (przebieg 44736780743) | czasy jobów 8, 37 i 34 s, równe `completed_at` − `started_at`. „Total duration” 1m 17s to czas od utworzenia przebiegu do jego ostatniej zmiany (`updated_at`), a nie T_czek (75 s). Kolejki zakończonych jobów interfejs nie pokazuje |
| T_czek i T_wyk | T_czek 41–89 s, T_wyk 39–87 s; kolejka pierwszego joba 1–2 s |
| `--from-raw` | `runs.csv`, `jobs.csv` i `steps.csv` identyczne bajt w bajt z wynikiem zbierania z API (15 przebiegów) |
| Infrastruktura runnerów | 40 jobów: 25 na Azure i 15 na AWS, w 10 regionach; 4 wersje obrazu `ubuntu-24.04` (20261111.370.1: 21 jobów, 20261111.127.1: 8, 20261116.133.1: 7, 20261116.376.1: 4). Numer po dacie różni się między chmurami (`.370` i `.376` na Azure, `.127` i `.133` na AWS). W 9 z 15 przebiegów joby jednego przebiegu działały w obu chmurach, a w 10 z 15 na różnych wersjach obrazu. Wydanie 20261116.376 miało w `actions/runner-images` status prerelease, a przebiegi z 2026-11-20 dostawały jeszcze obraz z 20261111. Wersja programu runnera wszędzie 2.338.2 |
| Czas jobów według chmury (opisowo) | `lint`: AWS 15 s (2 joby), Azure mediana 8 s (13 jobów); różnica głównie w checkout (4 s kontra 1–2 s). `test`: AWS mediana 43 s (5), Azure 40 s (10). Mała próba, nie pomiar |

Dokumentacja GitHub mówi, że joby Linux na standardowych runnerach trafiają do puli wielochmurowej (AWS albo Azure), a aktualizacja obrazów trwa kilka dni. Nie podaje regionów ani tego, że joby jednego przebiegu mogą dostać różne wersje obrazu.

Znaczenie `created_at` joba (P5). Dokumentacja REST API nie opisuje znaczenia pola. Pierwsze joby mają `created_at` 0–1 s po utworzeniu przebiegu. Obserwacja na żywo przebiegu `pull_request` 44744281273 (PR #5, 2026-11-20; `experiment/scripts/watch_jobs.py`, wynik w `experiment/data/pilot-e06-04/watch-pr-1fdf7c2.csv`): job `build` (`needs: [lint, test]`) pojawił się w API dopiero po zakończeniu `test`, od razu ze statusem `queued`. Jego `created_at` (13:26:52) jest równe `completed_at` joba `test`. Przy odpytaniach od 13:26:12 (co około 2 s) joba `build` nie było na liście. Ten sam wzór, `created_at` joba zależnego równe zakończeniu ostatniej zależności z dokładnością do 1 s, występuje w 10 z 10 przebiegów z jobem `build`. Wniosek: `created_at` to chwila utworzenia joba, czyli jego wejścia do kolejki. Dodatkowo: dopóki job czeka w kolejce, API zwraca `started_at` równe `created_at`; prawdziwą wartość podaje dopiero po starcie joba. Skrypt odrzuca przebiegi niezakończone, więc tej wartości nie zapisuje.

## Źródła

- GitHub Docs, „REST API endpoints for workflow jobs”: https://docs.github.com/en/rest/actions/workflow-jobs (sprawdzone 2026-11-20; pola czasu bez opisu znaczenia, link do logu ważny 1 minutę).
- GitHub Docs, „About GitHub-hosted runners”: https://docs.github.com/en/actions/using-github-hosted-runners/using-github-hosted-runners/about-github-hosted-runners (sprawdzone 2026-11-20; pula wielochmurowa AWS i Azure, aktualizacja obrazów trwa kilka dni).
- GitHub Docs, okres przechowywania logów: https://docs.github.com/en/organizations/managing-organization-settings/configuring-the-retention-period-for-github-actions-artifacts-and-logs-in-your-organization (sprawdzone 2026-11-20; domyślnie 90 dni).
- Źródła spoza rejestru `Zrodla/`; notatkę zakładamy, gdy trafią do tekstu pracy.
- Materiał wewnętrzny: `docs/metodyka.md` (p. 3.2), `experiment/PROTOCOL.md` (P4, P5, 2.3, K12), ADR-0035.
