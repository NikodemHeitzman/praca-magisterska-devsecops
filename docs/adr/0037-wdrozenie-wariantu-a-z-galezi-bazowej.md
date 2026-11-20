# 0037. Wdrożenie wariantu A: „main” to gałąź bazowa wariantu, bez środowiska GitHub i bez joba potwierdzającego

- **Status:** przyjęty
- **Data:** 2026-11-20
- **Decydujący:** autor pracy
- **Powiązane:** [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md), [0033](0033-mechanizm-wdrozenia-pull.md), [0036](0036-build-i-publikacja-obrazu.md), zadanie E06-03, `.github/workflows/baseline-ci.yml`, `infra/terraform/work/variables.tf` (`deploy_branch`), `experiment/PROTOCOL.md` (sekcje 0 i 2.3), [dziennik 2026-11-20](../log/2026-11-20.md)

## Kontekst

Zadanie E06-03 w katalogu zakłada job `deploy` uruchamiany tylko na `main`, uwierzytelnienie w AWS przez OIDC i środowisko GitHub „production”. Kryterium ukończenia brzmi: „merge do main = nowa wersja na AWS”. Po ADR-0032 potok nie ma poświadczeń AWS, bo SCP konta blokuje dostawców tożsamości. Według ADR-0033 instancja sama śledzi tag gałęzi w GHCR i wdraża nowy digest, a zmienna `deploy_branch` dopuszcza tylko `exp/variant-a` i `exp/variant-b`. Job `build` z ADR-0036 publikuje obraz z `main` i z `exp/variant-*`. Protokół eksperymentu (sekcja 2.3) nazywa wyzwalacz „main” pushem na gałąź bazową wariantu. Gałęzie bazowe powstaną z tagu czystej wersji (sekcja 0), a w chwili tej decyzji nie istnieją.

Trzeba ustalić: co w modelu pull znaczy „main” w kryterium, na jakiej gałęzi przetestować wdrożenie przed powstaniem gałęzi bazowych, czy wariant A ma środowisko GitHub i czy potok sam potwierdza wdrożenie.

## Czynniki decyzyjne

- zgodność z protokołem eksperymentu i z ADR-0033,
- ryzyko zmian w mechanizmie już sprawdzonym w E05-07, przed zamrożeniem wariantu A (E06-05),
- porównywalność czasów potoku (E06-04, E09-04),
- prostota potoku bazowego,
- czystość rejestru obrazów przed eksperymentem.

## Rozważane opcje

Znaczenie „main” w kryterium:

1. gałąź bazowa wariantu (`exp/variant-a`), bez zmian w kodzie
2. dodatkowo `main` jako dozwolona wartość `deploy_branch`
3. kryterium spełnione już przez E05-07 i E06-02, zapis samej interpretacji bez nowego testu

Gałąź testu end-to-end:

1. tymczasowa `exp/variant-a`, usuwana po teście razem z obrazami pod jej tagiem
2. `main` (wymaga opcji 2 z poprzedniej grupy)
3. trwała `exp/variant-a` utworzona teraz z bieżącego `main`

Środowisko GitHub:

1. brak środowiska
2. środowisko „production” na jobie `build` z regułą gałęzi (`exp/variant-*`)
3. środowisko bez reguł, tylko dla historii wdrożeń w interfejsie GitHub

Potwierdzenie wdrożenia w potoku:

1. brak, jak w ADR-0033: potwierdza `/version` i `check-deploy.sh`
2. job `verify-deploy`, który odpytuje publiczny `/version` instancji, aż zgodzi się commit

## Decyzja

Wybrano **„main” = gałąź bazowa wariantu `exp/variant-a`, test na tymczasowej gałęzi `exp/variant-a`, brak środowiska GitHub i brak joba potwierdzającego wdrożenie.** Kod potoku, agenta wdrożenia i Terraformu się nie zmienia. Powody autora:

- **„main” = gałąź bazowa wariantu:**
  - czysty eksperyment: w czasie eksperymentu na AWS trafia tylko czysta wersja z gałęzi wariantu, a `main` niesie zmiany robocze (dokumentacja, workflowy), które nie powinny być wdrażane,
  - bez zmian w kodzie: mechanizm sprawdzony w E05-07 zostaje taki sam, co zmniejsza ryzyko przed zamrożeniem wariantu A.
- **Tymczasowa `exp/variant-a` do testu:**
  - test prawdziwej ścieżki: test obejmuje dokładnie to, czego użyje eksperyment, czyli tag `exp-variant-a` i domyślne `deploy_branch`,
  - czysty rejestr: po teście gałąź i obrazy pod jej tagiem są usuwane, więc przed eksperymentem nie zostaje żaden tag gałęzi wariantu.
- **Brak środowiska GitHub:**
  - nic do ochrony: bez joba `deploy` i bez sekretów środowisko niczego nie strzeże (ADR-0032, ADR-0033),
  - prostota.
- **Brak joba potwierdzającego:**
  - czas potoku: odpytywanie `/version` przez około minutę wydłużyłoby mierzony czas potoku i zamazało porównanie A/B,
  - prostota.

Odczytanie kryterium: „merge do gałęzi bazowej wariantu A (`exp/variant-a`) = nowa wersja na AWS bez kroku ręcznego”. Potok kończy się na publikacji obrazu pod tagiem `exp-variant-a` (ADR-0036), a resztę robi agent wdrożenia (ADR-0033).

## Konsekwencje

- (+) Wariant A nie dostaje nowego kodu ani ustawień poza repozytorium, a test E06-03 sprawdza ścieżkę eksperymentu bez zmian.
- (+) Mierzony czas potoku kończy się na publikacji obrazu, tak samo w obu wariantach.
- (−) Merge do `main` repozytorium niczego nie wdraża. Obraz pod tagiem `main` istnieje, ale instancja go nie śledzi (konsekwencja już opisana w ADR-0036).
- (−) Potok nie wie, czy wdrożenie się udało. Potwierdzenie zostaje po stronie autora albo skryptu audytu (ADR-0033).
- (−) Tag `sha-<commit>` nie jest jednoznaczny między gałęziami. Push tego samego commita na `main` i na `exp/variant-a` buduje obraz dwa razy, a drugi build przesuwa tag `sha-<commit>` na nowy digest, jeśli build nie jest bitowo powtarzalny. Test potwierdził, że nie jest (sekcja „Weryfikacja”, punkt 4). Dotyczy to też eksperymentu, w którym obie gałęzie bazowe powstaną z jednego tagu czystej wersji. Do rozstrzygnięcia przed zamrożeniem wariantu A (E06-05). TODO: zweryfikować.
- (−) Usunięcie obrazów spod tagu `exp-variant-a` po teście wymaga usunięcia wersji pakietu w GHCR (uprawnienie `delete:packages` tokenu `gh`). Wersja z pierwszego wdrożenia niosła też tag `sha-<commit>` commita z `main`, więc przed jej usunięciem tag wrócił na obraz z `main` przez kopię manifestu (jak w `rollback.yml`).
- Definicja E06-03 w katalogu zadań (OIDC, środowisko „production”) jest nieaktualna i czyta się ją przez ten ADR.

## Weryfikacja

Test end-to-end z 2026-11-20 (czasy UTC). Czasy jobów z GitHub REST API, stan wdrożenia z publicznego `/version` instancji odpytywanego co 5 s. Pojedynczy przebieg, nie pomiar.

| Krok | Wynik |
|---|---|
| 1. Tymczasowa `exp/variant-a` z `main` (commit `400991f`) | przebieg [44735866366](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/44735866366): `exp-variant-a` → `sha256:daf6009890c7f56989d33c8815bdbdb9db0cf6a1760ee4dbf6ceb25ae0162367` |
| 2. `terraform apply` (23 zasoby, `deploy_tag` = `…:exp-variant-a`) | 12:31:44 `/version`: obraz `@sha256:daf60098…2367`, commit `400991f` |
| 3. PR [#4](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/pull/4) do `exp/variant-a` | przebieg `pull_request` [44736575951](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/44736575951): `build` bez publikacji |
| 3. Merge PR #4 (12:33:31, commit `5f102d5`) | przebieg push [44736780743](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/44736780743) 12:33:33–12:34:50 (lint 8 s, test 37 s, build 34 s); 12:35:15 `/version`: obraz `@sha256:3c4d9cc057f8f535e2d2d9cedfc746c1b69316931e6c340de50ff8606aac91cf`, commit `5f102d5`, bez kroku ręcznego. Od merge'u do nowej wersji około 104 s, z tego około 25 s po zakończeniu publikacji |
| 4. Ten sam commit `400991f` z `main` (przebieg [44735847511](https://github.com/NikodemHeitzman/praca-magisterska-devsecops/actions/runs/44735847511)) i z `exp/variant-a` | dwa różne digesty: `main` → `sha256:ea44c17d…986f`, `exp-variant-a` → `sha256:daf60098…2367`; tag `sha-400991f…` wskazywał obraz z drugiej publikacji |
| 5. Sprzątanie | `terraform destroy` 23 zasoby, `terraform state list` pusty; tag `sha-400991f…` przywrócony na `sha256:ea44c17d…` (kopia manifestu, HTTP 201); wersje `daf60098…` i `3c4d9cc0…` usunięte z GHCR, anonimowe zapytanie o `exp-variant-a` zwraca 404; gałęzie `exp/variant-a` i `test/e06-03-merge` usunięte |

Kryterium E06-03 w odczytaniu z tego ADR jest spełnione: merge do gałęzi bazowej wariantu A dał nową wersję na AWS bez kroku ręcznego.

## Źródła

- Materiał wewnętrzny: ADR-0032, ADR-0033 (sekcja „Weryfikacja”), ADR-0036, `experiment/PROTOCOL.md` (sekcje 0 i 2.3).
