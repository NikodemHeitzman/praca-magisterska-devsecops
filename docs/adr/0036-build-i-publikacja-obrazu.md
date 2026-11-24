# 0036. Build i publikacja obrazu w wariancie A: docker CLI, publikacja tylko z pushu, po testach, bez podpisu i cache

- **Status:** przyjęty; format tagu SHA zastąpiony przez [0040](0040-tag-sha-z-nazwa-galezi.md)
- **Data:** 2026-11-16
- **Decydujący:** autor pracy
- **Powiązane:** [0022](0022-obraz-kontenera-aplikacji.md), [0027](0027-rejestr-obrazow-ghcr.md), [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md), [0033](0033-mechanizm-wdrozenia-pull.md), [0035](0035-workflow-ci-lint-i-testy.md), zadanie E06-02, `.github/workflows/baseline-ci.yml`, `experiment/PROTOCOL.md` (sekcje 0, 2.3 i 6, K2), [dziennik 2026-11-16](../log/2026-11-16.md)

## Kontekst

W modelu pull (ADR-0032, ADR-0033) potok kończy się na publikacji obrazu w GHCR. Agent wdrożenia na instancji śledzi tag gałęzi wariantu (`exp-variant-a` albo `exp-variant-b`), uruchamia obraz po digeście i odrzuca obraz bez etykiety OCI `org.opencontainers.image.revision` z SHA commita. Według protokołu (K2) build i publikacja obrazu są w obu wariantach identyczne, a workflow A powstaje z workflow B przez usunięcie kroków bezpieczeństwa. W wariancie B ZAP i Trivy potrzebują obrazu już na pull requeście. Pull requesty niczego nie publikują pod tagiem gałęzi (`PROTOCOL.md`, sekcja 6, punkt 4, w brzmieniu z ADR-0032). ADR-0033 zostawił decyzję o podpisie obrazu zadaniom E06 i E07.

Trzeba ustalić: czym budować i publikować obraz, co robi job na pull requeście, a co na pushu, z których gałęzi obraz trafia do rejestru, czy build czeka na lint i testy, czy obraz jest podpisany i czy build używa pamięci podręcznej warstw.

## Czynniki decyzyjne

- liczba akcji zewnętrznych do przypięcia i aktualizowania (łańcuch dostaw, AGENTS.md, zasada 5),
- zgodność z protokołem: K2, sekcja 6 i definicja wariantu A jako potoku bez kontroli bezpieczeństwa,
- porównywalność czasów potoku (E06-04, E09-04),
- zgodność z agentem wdrożenia z E05-07 (tag gałęzi, etykieta `revision`, wdrożenie po digeście).

## Rozważane opcje

Narzędzie:

1. `docker build` i `docker push` w kroku `run`, jak w tymczasowym workflow testu end-to-end z E05-07
2. akcje `docker/login-action`, `docker/setup-buildx-action`, `docker/build-push-action` (i ewentualnie `docker/metadata-action`)
3. `docker buildx build --push` w kroku `run`

Pull request i push:

1. pull request buduje obraz bez publikacji, push buduje i publikuje
2. job `build` tylko na pushu
3. pull request publikuje obraz z tagiem SHA (bez tagu gałęzi)

Gałęzie, z których obraz trafia do GHCR:

1. `main` i `exp/variant-*` (wszystkie gałęzie z wyzwalaczy workflow)
2. tylko `exp/variant-*`

Kolejność jobów:

1. `build` po zielonych `lint` i `test` (`needs`)
2. `build` równolegle z `lint` i `test`

Podpis obrazu:

1. podpis tylko w wariancie B, w E07
2. podpis cosign (keyless) w obu wariantach już teraz, bez weryfikacji na instancji
3. brak podpisu w całym projekcie

Pamięć podręczna warstw:

1. bez cache
2. cache warstw w rejestrze albo w GitHub Actions

## Decyzja

Wybrano **`docker build` i `docker push` w jobie `build` po `lint` i `test`. Pull request tylko buduje obraz, a push na `main` lub `exp/variant-*` buduje go i publikuje w GHCR z tagiem SHA commita i tagiem gałęzi. Obraz nie jest podpisany, a build nie używa cache.** Powody autora:

- **docker CLI:**
  - mniej akcji: żadnej nowej akcji firm trzecich do przypięcia i aktualizowania,
  - czytelność: w workflow są te same polecenia co lokalnie, łatwe do opisania w pracy.
- **Pull request buduje, push publikuje:** czysty rejestr. W GHCR są tylko obrazy z gałęzi, nie z każdej próby.
- **`main` i `exp/variant-*`:**
  - test przed eksperymentem: publikację da się sprawdzić teraz, zanim powstaną gałęzie wariantów,
  - jednakowe zachowanie: każda gałąź z wyzwalaczy workflow zachowuje się tak samo, a workflow ma mniej warunków.
- **`needs: [lint, test]`:**
  - tylko przetestowany kod: pod tag gałęzi, czyli do wdrożenia, nie trafi obraz z nieudanymi testami,
  - klasyczny potok: kolejność build → test → deploy z celu epiku E06, czytelna w opisie pracy,
  - mniej marnowania: obraz nie powstaje, gdy lint albo testy już zawiodły.
- **Podpis tylko w wariancie B (E07):** definicja wariantu A. A to potok bez kontroli bezpieczeństwa, a podpis jest kontrolą bezpieczeństwa.
- **Bez cache:** porównywalne czasy, jak w ADR-0035.

Postać joba (decyzje agenta przy implementacji):

- tagi `ghcr.io/<repozytorium>:sha-<pełny SHA commita>` i `ghcr.io/<repozytorium>:<gałąź z `/` zamienionym na `-`>` (`main`, `exp-variant-a`, `exp-variant-b`), jak w teście end-to-end z E05-07,
- etykiety OCI `org.opencontainers.image.source` (adres repozytorium) i `org.opencontainers.image.revision` (`GITHUB_SHA`),
- jeden job dla obu wyzwalaczy: logowanie do GHCR i push mają warunek `github.event_name == 'push'`; dwóch prawie identycznych jobów nie ma,
- `permissions` joba: `contents: read`, `packages: write`; logowanie przez `GITHUB_TOKEN`, wylogowanie na końcu joba (`if: always()`),
- outputy joba `image` i `digest`; digest z `RepoDigests` obrazu po pushu, sprawdzony wyrażeniem `^sha256:[0-9a-f]{64}$`; tagi i digest także w podsumowaniu przebiegu,
- `concurrency` joba w tej samej grupie co `rollback.yml` (`deploy-tag-<gałąź>`), żeby publikacja i rollback nie przesuwały tagu jednocześnie,
- `timeout-minutes: 15`, `persist-credentials: false` w checkout,
- obraz bazowy jest przypięty digestem w `app/Dockerfile` (ADR-0022), więc build nie potrzebuje `--pull`.

## Konsekwencje

- (+) Brak nowych akcji: job używa tylko `actions/checkout` przypiętego jak w ADR-0035 i Dockera z obrazu runnera.
- (+) Do rejestru i pod tag gałęzi trafia tylko obraz, który przeszedł lint i testy, a pull requesty niczego nie publikują (protokół, sekcja 6).
- (+) Diff A/B w pilotażu (K2) pokaże podpis obrazu jako krok bezpieczeństwa wariantu B.
- (−) Potok jest dłuższy o czas buildu, bo `build` startuje dopiero po `lint` i `test`. Ile: TODO: zweryfikować w danych z E06-04.
- (−) Token przebiegu z pull requesta też ma `packages: write`, choć żaden krok go wtedy nie używa. Ochroną są zasady z sekcji 6 protokołu: pull requesty tylko z gałęzi tego repozytorium, zgoda na uruchomienie workflow dla zewnętrznych kontrybutorów.
- (−) Na pull requeście `GITHUB_SHA` to commit scalający (merge), więc etykieta `revision` obrazu z PR wskazuje commit scalający. Ten obraz nie jest publikowany.
- (−) Wariant A nie ma podpisu, więc kto ma `packages: write`, ten wskazuje, co wdroży instancja (ryzyko szczątkowe z ADR-0033). Materiał do 2.3 i 5.3.
- (−) Push na `main` publikuje obraz pod tagiem `main`, którego agent wdrożenia nie śledzi, dopóki `deploy_branch` wskazuje gałąź wariantu.
- Typ manifestu: `docker build` z domyślnym sterownikiem `docker` dodaje atestację provenance tylko przy magazynie obrazów containerd, a atestacje zamieniają manifest w indeks obrazu (dokumentacja Docker, niżej). Na runnerze `ubuntu-24.04` obraz trafia do GHCR jako zwykły manifest bez atestacji (`application/vnd.docker.distribution.manifest.v2+json`, sprawdzone 2026-11-16, sekcja „Weryfikacja”). Zmiana obrazu runnera może to zmienić.
- Rozbieżność do rozstrzygnięcia: protokół (sekcja 2.3, punkt 3) zakłada „cache jak w codziennej pracy” z przebiegiem rozgrzewkowym, a ADR-0035 i ten ADR wyłączają cache. TODO: zweryfikować, czy zmienić protokół (zapis w dzienniku) przed serią czasową.

## Weryfikacja

Pojedyncze przebiegi z 2026-11-16, czasy jobów i kroków z GitHub REST API.

| Przebieg | Wynik |
|---|---|
| `pull_request` [43923746792](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/43923746792) (PR [#3](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/pull/3), commit `2cdbaa2`) | `build` po `lint` i `test`, 19 s; kroki logowania, pushu i wylogowania pominięte |
| `push` na `main` [43923993380](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/43923993380) (merge `575a9dd`) | `build` 42 s (budowanie 13 s, push 22 s); tagi `sha-575a9dd10e6fe8e8f4e31c35d59cb6be375122ea` i `main` wskazują `sha256:246817ba934e9e80efa366dd7b484fff31f938208b7d9bca4d32ae9a975890c3` |

Sprawdzenie w GHCR anonimowym tokenem, tak jak robi to agent wdrożenia:

- oba tagi zwracają HTTP 200 i ten sam digest; typ manifestu `application/vnd.docker.distribution.manifest.v2+json`, czyli bez indeksu i atestacji,
- konfiguracja obrazu ma etykiety `org.opencontainers.image.revision=575a9dd10e6fe8e8f4e31c35d59cb6be375122ea` i `org.opencontainers.image.source=https://github.com/NikodemHeitzman/praca-magisterska-devsecops` oraz `User` `10001:10001`,
- krok `Push image` kończy się sukcesem tylko wtedy, gdy digest pasuje do `^sha256:[0-9a-f]{64}$`; zapisuje go wtedy w outputach joba i w podsumowaniu przebiegu.

## Źródła

- Docker Docs, „Build attestations”, https://docs.docker.com/build/metadata/attestations/ (sprawdzone 2026-11-16): provenance `mode=min` dodawana domyślnie, sterownik `docker` wymaga magazynu containerd, atestacje dołączane do indeksu obrazu.
- Tymczasowy workflow `e2e-publish.yml` z testu end-to-end (commit `2de43b7`, ADR-0033, „Weryfikacja”).
