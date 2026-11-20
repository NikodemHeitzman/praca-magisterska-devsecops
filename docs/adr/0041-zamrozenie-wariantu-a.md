# 0041. Zamrożenie wariantu A: tag z adnotacją `pipeline-a-v1` na `main`, wersje w pliku YAML, zmiana przez nowy tag

- **Status:** przyjęty
- **Data:** 2026-11-20
- **Decydujący:** autor pracy, po rekomendacji agenta
- **Powiązane:** [0035](0035-workflow-ci-lint-i-testy.md), [0036](0036-build-i-publikacja-obrazu.md), [0037](0037-wdrozenie-wariantu-a-z-galezi-bazowej.md), [0038](0038-seria-czasowa-bez-cache.md), [0040](0040-tag-sha-z-nazwa-galezi.md), [0008](0008-menedzer-zaleznosci-uv.md), zadanie E06-05 (kamień milowy M2), `experiment/PROTOCOL.md` (P1, P2, P3, P4, K2), [`experiment/versions/variant-a.yaml`](../../experiment/versions/variant-a.yaml), [dziennik 2026-11-20](../log/2026-11-20.md)

## Kontekst

Wariant A (potok bazowy bez kontroli bezpieczeństwa) jest gotowy:

- joby `lint` i `test` (ADR-0035) i `build` (ADR-0036, ADR-0040),
- wdrożenie w modelu pull (ADR-0037),
- skrypt czasów (ADR-0039).

Jest punktem odniesienia eksperymentu, a wariant B przejmie joby `lint`, `test` i `build` bez zmian i doda obok nich kontrole bezpieczeństwa (K2). Wariant A trzeba więc zamrozić, zanim powstanie wariant B (E07).

Protokół (P1, P3) przewiduje osobny tag czystej wersji aplikacji (roboczo `exp-clean-v1`), z którego powstaną gałęzie bazowe `exp/variant-a` i `exp/variant-b`. Tego tagu jeszcze nie ma. Katalog zadań nazywa tag zamrożenia potoku `pipeline-a-v1`. Do ustalenia było:

- gdzie założyć tag,
- jaki to rodzaj tagu,
- gdzie zapisać wersje,
- co zamrożenie obejmuje,
- co zrobić, gdy wariant A trzeba będzie zmienić.

## Czynniki decyzyjne

- zgodność z protokołem (P1, P3),
- prostota,
- odczyt wersji przez skrypty eksperymentu (P4, E09),
- ślad każdej zmiany wariantu A,
- koszt konfiguracji.

## Rozważane opcje

Miejsce tagu:

1. tag `pipeline-a-v1` na commicie `main`; gałąź `exp/variant-a` powstaje przy E09 z tagu czystej wersji i bierze workflow z `pipeline-a-v1`
2. gałąź `exp/variant-a` utworzona teraz, tag na niej
3. jeden tag dla workflow A i aplikacji (pełni też rolę `exp-clean-v1`)

Rodzaj tagu:

1. tag z adnotacją (`git tag -a`)
2. tag podpisany (`git tag -s`, GPG albo SSH)
3. tag lekki

Miejsce listy wersji:

1. plik YAML w `experiment/`
2. plik Markdown w `experiment/`
3. sekcja w tym ADR
4. opis tagu i dziennik badawczy

Zmiana wariantu A po zamrożeniu:

1. dozwolona przed serią właściwą: PR, nowy tag `pipeline-a-v<N>`, wpis w dzienniku, aktualizacja pliku wersji
2. zakaz zmian
3. zmiana z wpisem w dzienniku, bez nowego tagu

## Decyzja

Opcje i rekomendacje przygotował agent. Autor wybrał rekomendowane opcje i wskazał swoje powody.

| Decyzja | Odrzucone | Powody autora |
|---|---|---|
| Tag `pipeline-a-v1` na commicie `main` (merge PR zamrożenia) | gałąź `exp/variant-a` teraz, jeden tag z aplikacją | zgodność z protokołem (gałęzie powstają z tagu czystej wersji, którego jeszcze nie ma), prostota |
| Tag z adnotacją | podpisany, lekki | bez konfiguracji kluczy |
| Lista wersji w [`experiment/versions/variant-a.yaml`](../../experiment/versions/variant-a.yaml) | Markdown, ADR, opis tagu i dziennik | czytelny dla skryptów |
| Zamrożenie obejmuje `baseline-ci.yml` i `rollback.yml` | tylko `baseline-ci.yml` | `rollback.yml` trafi na obie gałęzie wariantów |
| Zmiana po zamrożeniu tylko przed serią właściwą, przez PR, z tagiem `pipeline-a-v<N>`, wpisem w dzienniku i aktualizacją pliku wersji; po starcie serii obowiązuje P1 (zmiana = powtórzenie serii) | zakaz zmian, zmiana bez tagu | ślad zmian, realizm |
| Jeden ADR dla zamrożenia | wpis w dzienniku zamiast ADR | uzasadnienie w jednym miejscu |

Powiązana decyzja autora o zakresie wariantu A: sprawdzanie zgodności `requirements.txt` z `uv.lock` (konsekwencja ADR-0008) wchodzi do wariantu B (E07), a nie do rdzenia A ani poza CI. Powody: `requirements.txt` służy pip-audit, a `baseline-ci.yml` nie trzeba zmieniać przed tagiem.

Decyzje agenta:

- katalog `experiment/versions/` zamiast `experiment/manifests/`, bo w `experiment/README.md` „manifest” oznacza już listę przebiegów (`manifest.csv`),
- plik rozróżnia wersje przypięte w repozytorium (`przypiete: true`: SHA, digest, suma kontrolna, lockfile) od wersji zależnych od środowiska (`przypiete: false`: obraz runnera, wersja łatkowa Pythona w CI, Docker), dla których podaje obserwację z przebiegu kontrolnego,
- przebieg kontrolny to ostatni zielony push na `main` przed zamrożeniem, 44747792543,
- actionlint i zizmor, uruchomione lokalnie w Dockerze przed tagiem, są zapisane w osobnej sekcji `kontrola_zamrozenia`, bo nie należą do wariantu A.

## Konsekwencje

- (+) Wariant A ma jedną nazwaną wersję. Wariant B (E07) bierze joby wspólne z `pipeline-a-v1`, a gałąź `exp/variant-a` (E09) bierze z niego workflow.
- (+) Plik wersji czytają skrypty E09. Wariant B dostanie plik `variant-b.yaml` w tym samym układzie.
- (+) Każda późniejsza wersja wariantu A ma własny tag i wpis w dzienniku, więc wiadomo, która była użyta w serii.
- (−) Tag nie jest podpisany. Jego autentyczność opiera się na dostępie do repozytorium, a nie na kluczu.
- (−) Tag na `main` obejmuje też aplikację w bieżącym stanie, ale jej nie zamraża. O wersji aplikacji w eksperymencie decyduje tag czystej wersji (P1).
- (−) Część wersji zależy od GitHub i nie da się jej przypiąć: obraz runnera, wersja Dockera na runnerze, wersja łatkowa Pythona pobieranego przez uv (`.python-version` = `3.14`). TODO: zweryfikować, czy wersja łatkowa zależy tylko od wersji uv. Obraz runnera każdego joba zapisuje skrypt czasów (TN2, ADR-0039).
- Zamrożenie dotyczy `.github/workflows/` w stanie z tagu. Inne pliki używane przez potok (`app/compose.yaml`, `app/scripts/ci-env.sh`, `app/Dockerfile`, `app/uv.lock`) należą do aplikacji i zamraża je tag czystej wersji.
- Kontrola `requirements.txt` ↔ `uv.lock` trafia do zakresu E07.

## Źródła

- Materiał wewnętrzny: `experiment/PROTOCOL.md` (P1–P4, K2), ADR-0008, ADR-0035–ADR-0040, przebieg kontrolny https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/44747792543.
- Źródeł zewnętrznych nie użyto.
