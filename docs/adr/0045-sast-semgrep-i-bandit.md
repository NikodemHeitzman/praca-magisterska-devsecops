# 0045. SAST: Semgrep z zestawem `p/default` i regułami własnymi oraz Bandit, wspólna lista wyjątków bramek

- **Status:** przyjęty
- **Data:** 2026-11-24
- **Decydujący:** autor pracy, po rekomendacjach agenta
- **Powiązane:** [0042](0042-projekt-potoku-wariantu-b.md) (kroki B08, B09; D5, D6, D9, D11, D13), [0043](0043-utwardzenie-workflowow.md) (H3, H6), [0044](0044-skanowanie-sekretow.md) (S3, S4), [`docs/projekt-potoku.md`](../projekt-potoku.md), [`docs/narzedzia.md`](../narzedzia.md) (p. 4), [`semgrep-rules/README.md`](../../semgrep-rules/README.md), [`.github/workflows/devsecops-gates.yml`](../../.github/workflows/devsecops-gates.yml), [`.github/scripts/sast_gate.py`](../../.github/scripts/sast_gate.py), [`.github/gate-exceptions.yaml`](../../.github/gate-exceptions.yaml), [`.github/tools/`](../../.github/tools/), zadanie E07-04, `experiment/ground-truth.yaml`, [dziennik 2026-11-24](../log/2026-11-24.md)

## Kontekst

ADR-0042 przewidział job `sast` z dwoma narzędziami: Semgrep z regułami z rejestru i regułami własnymi dla GT-06 i GT-14 (B08) oraz Bandit (B09). Próg (D5): własny kod blokuje wszystko poza najniższym, informacyjnym poziomem; dla Bandita ważność LOW i wyżej przy pewności MEDIUM i wyżej. Narzędzia instalowane z PyPI w dokładnej wersji (D9), wyciszenia w kodzie ignorowane (D13), wyjątki tylko na liście czystej wersji (D6). CodeQL zostaje poza wariantem B (D11). Oczekiwane pozycje katalogu: GT-01, GT-03–GT-06, GT-12, GT-14 (Semgrep) i GT-01–GT-04 (Bandit).

Rozpoznanie agenta (2026-11-24, kontener `python:3.12-slim`, czysty eksport `HEAD`):

- **Wersje:** Semgrep 1.181.0 z `docs/narzedzia.md` nie jest najnowszy; 1.185.0 (2026-11-10) przeszła karencję 7 dni (H6), 1.186.0 (2026-11-18) przejdzie ją 2026-11-25. Bandit 1.9.4 nadal najnowszy.
- **Opcje:** `--disable-nosem` (Semgrep) i `--ignore-nosec` (Bandit) istnieją w obu wersjach.
- **Kody wyjścia:** Semgrep 0 = OK, 1 = zgłoszenia (tylko z `--error`), 2 i wyżej = błąd (pomoc `semgrep scan --help`, sekcja „EXIT STATUS”). Bandit zwraca 1 przy zgłoszeniach (sprawdzone), a `--exit-zero` daje 0 mimo zgłoszeń (pomoc `bandit --help`); kodu przy awarii narzędzia nie sprawdzano, więc job traktuje każdy niezerowy kod jako błąd.
- **Skala ważności Semgrepa jest mieszana:** reguły rejestru mają starą skalę `ERROR`/`WARNING`/`INFO`, a 11 reguł `p/default` ma już `MEDIUM`. Opcja `--severity` przyjmuje tylko `INFO`, `WARNING` i `ERROR`.
- **B105 w Bandit 1.9.4:** ważność LOW, pewność MEDIUM (`bandit/plugins/general_hardcoded_password.py`), więc według D5 blokuje.
- **Czysta wersja:** `p/default` daje 2 zgłoszenia (`uv-missing-dependency-cooldown` w `app/pyproject.toml`, `django-no-csrf-token` w `templates/login.html`) i błąd częściowego parsowania szablonu Jinja `index.html`; `p/python`, `p/security-audit`, `p/fastapi`, `p/jwt` i reguły własne: 0 zgłoszeń. Bandit: 118× B101 i 4× B105 w `app/tests/`, 1× B108 w `app/ticketing/config.py`.
- **Rejestr się zmienia:** `p/default` miał 1073 reguły 2026-10-18 i 1074 reguły 2026-11-24. Licencja reguł rejestru (Semgrep Rules License v1.0) nie pozwala ich rozpowszechniać, więc nie trafiają do repozytorium (`docs/narzedzia.md`).
- **Bandit SARIF** wymaga dodatku `bandit[sarif]` (pakiety `sarif-om` i `jschema-to-python` z 2019 roku); Bandit zapisuje jeden format na przebieg.

## Czynniki decyzyjne

- skuteczność wobec pozycji katalogu w kodzie aplikacji (M1, H1) i mało fałszywych alarmów na czystej wersji (M6),
- trafność eksperymentu: reguły niedopasowane do katalogu (TW1), odtwarzalność (K5, zasada 6 z `AGENTS.md`), stały czas joba (H2a),
- zgodność z SP 800-204D (TEST-1*) [@NIST-SP800-204D] i SSDF (PW.7.1, PW.7.2) [@NIST-SP800-218], polityka bramek ADR-0042 [@OWASP-DevSecOps-Guideline],
- lekki potok: mało kodu firm trzecich i mało plików.

## Rozważane opcje

| Pytanie | Rozważane opcje |
|---|---|
| T1. Zestaw reguł rejestru | `p/default`; `p/python`; `p/default` + `p/security-audit`; `p/python` + `p/fastapi` + `p/jwt` |
| T2. Odtwarzalność rejestru | pobieranie w przebiegu, w artefakcie SHA-256 i lista ID reguł; to samo, ale zmiana sumy blokuje; bez kontroli |
| T3. Zakres skanu | `app/` bez `app/tests/`; całe `app/` z testami na liście wyjątków; repozytorium bez `semgrep-rules/` |
| T4. Wersja Semgrepa | 1.185.0; 1.181.0; czekać na 1.186.0 |
| T5. Błędy narzędzia | blokują tylko błędy fatalne; każdy wpis w `errors` blokuje; wykluczyć szablony HTML |
| T6. SARIF Bandita | dwa uruchomienia (JSON i SARIF); tylko JSON; własna konwersja JSON → SARIF |
| T7. Poziom `LOW` w nowej skali Semgrepa | blokuje (wszystko poza `INFO`); jak `INFO` |
| T8. Format listy wyjątków (D6) | jeden plik dla bramek; mechanizmy narzędzi (`.semgrepignore`, `--exclude-rule`, `-s`); plik na narzędzie |

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał opcje i wskazał swoje powody z listy w wywiadzie z 2026-11-24. Poniżej są tylko powody autora. We wszystkich pytaniach autor wybrał rekomendację agenta.

| # | Decyzja | Powody autora |
|---|---|---|
| T1 | Zestaw rejestru `p/default` oraz reguły własne z `semgrep-rules/` | domyślny zestaw narzędzia, szerszy zasięg |
| T2 | Job pobiera zestaw z rejestru do pliku i skanuje tym plikiem. Do artefaktu trafia tylko SHA-256 i lista ID reguł (`reports/semgrep-ruleset.json`), bez treści reguł. Po teście w CI suma jest kanoniczna, a ID reguł mają swoje sumy (decyzje agenta niżej). Zmianę zestawu w trakcie serii wykrywa analiza i zapisuje w dzienniku | zgodne z licencją, mały koszt |
| T3 | Oba narzędzia skanują `app/` bez `app/tests/`. `semgrep-rules/` nigdy nie jest celem | testy nie trafiają do obrazu, krótsza lista wyjątków |
| T4 | Semgrep 1.185.0 | aktualne łatki narzędzia, bez czekania na 1.186.0 |
| T5 | Blokuje błąd fatalny: kod wyjścia narzędzia inny niż oczekiwany, brak albo nieczytelny raport. Błędy częściowego parsowania nie blokują, ale ich liczba trafia do podsumowania przebiegu i zostaje w raporcie | brak raportu nadal blokuje, ślad w danych |
| T6 | Bandit uruchamiany dwa razy: JSON (dane i bramka) i SARIF (code scanning, kategoria `bandit`) | oba narzędzia widoczne w zakładce Security, pomijalny koszt czasu (skan poniżej 1 s) |
| T7 | Semgrep blokuje każdą ważność poza `INFO`, także `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` i każdą nieznaną wartość | dosłownie D5 |
| T8 | Jeden wspólny plik `.github/gate-exceptions.yaml` (narzędzie, reguła, plik, uzasadnienie, data). Stosuje go krok bramki, a raporty narzędzi zostają pełne | pełne raporty dla M1, łatwy przegląd |

Decyzje agenta (techniczne, w ramach decyzji autora i ADR-0042):

- **instalacja z PyPI z hashami:** `.github/tools/semgrep.txt` i `bandit.txt` wygenerowane przez `uv pip compile --generate-hashes` dla Pythona 3.12 i Linuksa, z `--exclude-newer` 7 dni wstecz (karencja H6 także dla zależności narzędzi); instalacja `pip install --no-deps --require-hashes` w osobnych środowiskach wirtualnych, żeby zależności narzędzi się nie mieszały. Pliki wejściowe `.in` zawierają polecenie odtworzenia,
- **próg w osobnym skrypcie** `.github/scripts/sast_gate.py` na raportach JSON, bo `--severity` Semgrepa nie zna nowej skali (T7). Skrypt zwraca 0 (przechodzi), 1 (zgłoszenia blokujące) albo 2 (nieczytelne wejście, niepełny wpis na liście wyjątków); każde niezerowe wyjście zatrzymuje job,
- **dopasowanie wyjątku:** narzędzie + ID reguły + plik, bez numeru linii, żeby wyjątek przetrwał niezwiązane zmiany pliku. Nieużyty wyjątek daje ostrzeżenie,
- **plik zestawu rejestru w katalogu głównym repozytorium:** Semgrep dodaje do ID reguł z lokalnego pliku prefiks z jego katalogu (np. `tmp.rt.` dla `/tmp/rt/`), więc plik w katalogu głównym daje ID takie jak w rejestrze; reguły własne dostają stały prefiks `semgrep-rules.`. Plik nie leży w `app/` ani `reports/`, więc nie jest skanowany ani wysyłany do artefaktu,
- **Semgrep bez `--error`** (zgłoszenia dają 0, każdy inny kod to błąd) i **Bandit z `--exit-zero`** (każdy niezerowy kod to błąd), zgodnie z zasadą „raport, potem osobny krok bramki” z ADR-0042,
- **PyYAML** dopisany jawnie do `bandit.in`, bo skrypt bramki czyta listę wyjątków (jest i tak zależnością Bandita),
- **suma kanoniczna zestawu (T2):** w CI dwa przebiegi odległe o 23 s (PR #22 i #23, 2026-11-24) dostały plik `p/default` o innej surowej sumie SHA-256 (`43b45d87…` i `9c76333a…`) przy tych samych 1074 ID reguł. Surowa suma nie pokazuje więc zmiany reguł. Artefakt zawiera sumę każdej sparsowanej reguły (klucze posortowane), sumę kanoniczną z nich i surową sumę tylko pomocniczo. Analiza porównuje sumę kanoniczną, a przy różnicy wskazuje zmienione reguły bez ich treści. Przyczyna różnicy bajtów: TODO: zweryfikować (przypuszczalnie różne węzły CDN; ponowne przebiegi i pobrania lokalne dały te same bajty),
- **`--metrics=off`** i **`--disable-version-check`:** Semgrep nie wysyła danych do producenta i nie sprawdza nowej wersji w czasie pomiaru,
- **Python runnera bez przypięcia** (`python3` obrazu `ubuntu-24.04`, w teście 3.12); wersja trafia do logu i do `variant-b.yaml` jako nieprzypięta.

## Konsekwencje

- (+) Kroki B08 i B09 z `docs/projekt-potoku.md` są zrealizowane. Zamknięte TODO z ADR-0042: nazwy ważności Semgrepa, pewność B105, opcje `--disable-nosem` i `--ignore-nosec`, kody wyjścia Semgrepa i Bandita.
- (+) Test lokalny na kopii aplikacji z łatkami próbnymi (2026-11-24, kroki joba odtworzone w kontenerze `python:3.12-slim`): bramka blokuje GT-02 (Bandit B105 i Semgrep `detected-generic-secret`), GT-06 i GT-14 (reguły własne) oraz GT-12 (`wildcard-cors`). Komentarze `# nosec` przy GT-02 i `# nosemgrep` przy GT-12 nie wyłączyły zgłoszeń. Łatki próbne mają postać z `docs/narzedzia.md`, ale nie są docelowymi łatkami z E04.
- (+) Test w CI (2026-11-24):
  - **PR #22** (czysta wersja): `sast` przechodzi (Semgrep 2 i Bandit 1 zgłoszenie, wszystkie na liście wyjątków; 1 błąd częściowego parsowania). Zakładka Security pokazuje analizy `semgrep` (Semgrep OSS 1.185.0) i `bandit` (Bandit 1.9.4). Python runnera 3.12.3,
  - **PR #23** (test negatywny z łatkami próbnymi, zamknięty bez scalania): `sast` blokuje 5 zgłoszeń (Semgrep 4, Bandit 1), tak jak lokalnie; `secrets` blokuje GT-02. Check code scanningu `Semgrep OSS` też nie przechodzi (zgłoszenia `ERROR`), a `Bandit` przechodzi (poziomy `note` i `warning`); blokuje job `sast`,
  - suma kanoniczna zestawu `p/default` w obu przebiegach po zmianie i lokalnie: `29893075…` (1074 reguły).
- (+) GT-02 ma w wariancie B trzy detektory blokujące: Gitleaks, Bandit B105 i Semgrep `detected-generic-secret`. Regułę Semgrepa wnosi wybór `p/default` (T1); analiza z 2026-10-20 jej nie uwzględniała.
- (+) Czysta wersja przechodzi z trzema wyjątkami (lista niżej), a ich uzasadnienia sprawdzi autor.
- (−) Zestaw rejestru nie jest przypięty: aktualizacja rejestru w trakcie serii zmieni reguły (T2). Analiza porównuje SHA-256 z artefaktów przebiegów i zapisuje zmianę w dzienniku. Materiał do 5.3 (odtwarzalność).
- (−) Job zależy od dostępności `semgrep.dev` w czasie przebiegu; brak sieci kończy job błędem (fail closed).
- (−) `p/default` obejmuje wiele języków i plików konfiguracji, więc skan szablonów Jinja daje błędy częściowego parsowania (T5) i reguły innych frameworków (Django) na szablonach.
- (−) Wyjątek dopasowany po pliku ukrywa też nowe zgłoszenie tej samej reguły w tym samym pliku. Żadna pozycja katalogu nie oczekuje tych reguł w tych plikach (`experiment/ground-truth.yaml`).
- (−) Lista wyjątków i skrypt bramki są w repozytorium, więc PR może je zmienić. To ryzyko resztkowe z `docs/projekt-potoku.md` (4.6), jak `.gitleaks.toml` w ADR-0044; materiał do 5.3.
- Lista wyjątków czystej wersji (2026-11-24, `.github/gate-exceptions.yaml`):
  - Bandit B108 w `app/ticketing/config.py` (domyślny katalog podręczny `/tmp/ticketing-attachments`),
  - Semgrep `uv-missing-dependency-cooldown` w `app/pyproject.toml`,
  - Semgrep `django-no-csrf-token` w `app/ticketing/templates/login.html`.
  - uzasadnienia zatwierdził autor 2026-11-24; lista zamarza z progami (K5, E07-14).
- Czas skanu w teście lokalnym: Semgrep około 7 s, Bandit poniżej 1 s, bez instalacji i pobrania zestawu. Czas joba zmierzy seria (M4/M5).
- Kolejne kroki:
  - ~~**po scaleniu:** `sast` jako wymagany check, `settings.sh apply` za zgodą autora~~ wykonane 2026-11-24: PR #22 scalony (`c4dfd49`), `apply` zaktualizował rulesety `main`, `tags` i `exp-variant-b`; `show` potwierdza `sast` jako wymagany check w `main` i `exp-variant-b`. Pierwszy przebieg `devsecops-gates` na pushu do `main` (45423688051, `c4dfd49`): `secrets` i `sast` przechodzą,
  - **łatki z E04 a `lint`:** łatka próbna na PR #23 nie przeszła `ruff format` (job `lint`). Docelowe łatki muszą przejść `lint`, inaczej próba zatrzyma się przed bramkami bezpieczeństwa w obu wariantach (sprawdzić w pilotażu),
  - **E07-05, E07-06:** dopisują swoje wyjątki do `.github/gate-exceptions.yaml`,
  - **E07-14:** zamrożenie listy wyjątków i wersji z `variant-b.yaml`.

## Źródła

- [@NIST-SP800-204D]: TEST-1*; notatki `docs/notes/nist-800-204d.md`.
- [@NIST-SP800-218]: PW.7.1, PW.7.2; notatki `docs/notes/nist-ssdf.md`.
- [@OWASP-Top10-CICD]: CICD-SEC-4 (wyciszenia w kodzie, D13); notatki `docs/notes/owasp-devsecops.md`.
- [@OWASP-DevSecOps-Guideline]: SAST w CI, „fail closed”; notatki `docs/notes/owasp-devsecops.md`.
- Dokumentacja techniczna (poza rejestrem źródeł, dostęp 2026-11-24):
  - pomoc `semgrep scan --help` w Semgrep 1.181.0 (opcje, „EXIT STATUS”); te same opcje użyte w teście joba na 1.185.0,
  - pomoc `bandit --help` i kod wtyczki `bandit/plugins/general_hardcoded_password.py` w Bandit 1.9.4,
  - PyPI, historia wydań `semgrep` i `bandit`: https://pypi.org/project/semgrep/#history, https://pypi.org/project/bandit/#history
  - zestaw rejestru: https://semgrep.dev/c/p/default
