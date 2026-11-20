# 0040. Tag SHA obrazu z nazwą gałęzi: `<gałąź>-sha-<commit>`

- **Status:** proponowany
- **Data:** 2026-11-20
- **Decydujący:** autor pracy, po rekomendacji agenta
- **Powiązane:** [0033](0033-mechanizm-wdrozenia-pull.md), [0036](0036-build-i-publikacja-obrazu.md) (zastępuje format tagu SHA), [0037](0037-wdrozenie-wariantu-a-z-galezi-bazowej.md), zadania E06-03 i E06-05, `.github/workflows/baseline-ci.yml` (job `build`), `experiment/PROTOCOL.md` (P1, P3, K2), [dziennik 2026-11-20](../log/2026-11-20.md)

## Kontekst

Job `build` (ADR-0036) publikuje obraz z każdego pushu na `main` i `exp/variant-*` pod dwoma tagami: `sha-<commit>` i tagiem gałęzi. Test z E06-03 (ADR-0037, „Weryfikacja”, punkt 4) pokazał dwie rzeczy:

- ten sam commit `400991f` zbudowany na `main` i na `exp/variant-a` dał dwa różne digesty (`ea44c17d…` i `daf60098…`), bo build nie jest powtarzalny co do bitu. Przyczyna: TODO: zweryfikować (prawdopodobnie znaczniki czasu w obrazie),
- drugi build przestawił tag `sha-400991f…` na swój obraz.

Tag `sha-<commit>` nie identyfikuje więc obrazu jednoznacznie, gdy ten sam commit trafi na dwie gałęzie publikujące.

Co korzysta z tego tagu:

- agent wdrożenia śledzi tag gałęzi i wdraża po digeście (ADR-0033),
- `rollback.yml` przyjmuje digest,
- job `build` używa tagu SHA tylko lokalnie, do odczytu digestu po pushu.

Tag SHA służy więc ludziom: do znalezienia obrazu po commicie w GHCR, w audycie (`PROTOCOL.md`, sekcja 4) i w tekście pracy.

W eksperymencie gałęzie wariantów powstaną z tagu czystej wersji i dostaną własne commity z workflow (P1, P3). Kolizja grozi przede wszystkim przy pierwszym pushu gałęzi wariantu, jeśli trafi na nią sam commit z `main`. Decyzja zapada przed zamrożeniem wariantu A (E06-05), bo zmienia job `build`, który jest wspólny dla obu wariantów (K2).

## Czynniki decyzyjne

- jednoznaczność tagu: tag nie może wskazać obrazu zbudowanego na innej gałęzi,
- ślad commita: możliwość znalezienia obrazu po commicie,
- zakres zmian przed zamrożeniem wariantu A,
- tożsamość obrazu dla wdrożenia, wycofania i (w wariancie B) podpisu.

## Rozważane opcje

1. tag SHA z nazwą gałęzi: `<gałąź>-sha-<commit>` (np. `exp-variant-a-sha-400991f…`)
2. usunięcie tagu SHA: tylko tag gałęzi, a tożsamość obrazu to digest i etykieta `org.opencontainers.image.revision`
3. zasada w protokole bez zmian w kodzie: zakaz pushowania tego samego commita na dwie gałęzie publikujące
4. bitowo powtarzalny build (ustalone znaczniki czasu, np. `SOURCE_DATE_EPOCH`), żeby ten sam commit dawał ten sam digest

## Decyzja

Wybrano **tag SHA z nazwą gałęzi (opcja 1)**: `<gałąź z „/” zamienionym na „-”>-sha-<pełny SHA commita>`, np. `main-sha-…`, `exp-variant-a-sha-…`. Opcję zarekomendował agent, a autor ją wybrał. Powód autora:

- **ślad commita:** obraz da się znaleźć po commicie i gałęzi (audyt, tekst pracy).

Kontekst rekomendacji agenta (nie jest powodem autora):

- tag w rejestrze OCI to ruchomy wskaźnik, a niezmienny jest tylko digest,
- zasada „buduj raz, promuj dalej” [@Humble2010] (TODO: zweryfikować rozdział i stronę) nie pasuje tu, bo każdy wariant celowo buduje obraz własnym potokiem: mierzymy czas tego potoku,
- opcja 2 usuwa ślad commita w GHCR,
- opcja 3 niczego nie wymusza,
- opcja 4 wymaga dodatkowej pracy i prawdopodobnie `docker buildx`, z którego ADR-0036 zrezygnował.

Postać zmiany (decyzja agenta): w kroku `Build image` tag `"$image:$tag-sha-$GITHUB_SHA"` zamiast `"$image:sha-$GITHUB_SHA"`, zmienna `SHA_TAG` dla kroku `Push image` i podsumowania przebiegu. Pozostałe ustalenia ADR-0036 się nie zmieniają.

## Konsekwencje

- (+) Każda publikacja ma własny tag SHA. Ten sam commit na `main` i na `exp/variant-a` daje tagi `main-sha-…` i `exp-variant-a-sha-…`, a żaden nie przeskakuje na obraz z drugiej gałęzi.
- (+) Agent wdrożenia, `rollback.yml` i Terraform bez zmian, bo nie używają tagu SHA.
- (−) Tag SHA nadal jest ruchomy w obrębie jednej gałęzi. Ponowne uruchomienie przebiegu („Re-run”) albo ponowny push tego samego commita zbudowałby obraz jeszcze raz pod tym samym tagiem. Protokół zakazuje ponownych uruchomień (2.2). Tożsamością wdrożenia pozostaje digest.
- (−) Obrazy opublikowane przed tą zmianą mają tagi w starym formacie (`sha-<commit>`). Zostają w GHCR bez zmian.
- (−) Build nadal nie jest powtarzalny co do bitu. Ograniczenie do 5.3: tag SHA identyfikuje commit i gałąź, nie zawartość obrazu.
- Zmiana wchodzi przed zamrożeniem wariantu A (E06-05), więc wariant B przejmie job `build` w tej postaci (K2).
- ADR-0036: format tagu SHA zastąpiony przez ten ADR, reszta decyzji obowiązuje.

## Źródła

- [@Humble2010]: zasada jednokrotnego budowania artefaktu. TODO: zweryfikować po lekturze (źródło ma w rejestrze `zweryfikowane: nie`).
- Materiał wewnętrzny: ADR-0033, ADR-0036, ADR-0037 („Weryfikacja”, punkt 4), `.github/workflows/rollback.yml`, `infra/terraform/work/deploy-agent.sh`.
