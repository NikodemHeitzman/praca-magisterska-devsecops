# 0033. Mechanizm wdrożenia w modelu pull: ruchomy tag w GHCR i timer na instancji

- **Status:** przyjęty
- **Data:** 2026-11-13
- **Decydujący:** autor pracy
- **Powiązane:** rozwija [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md); [0019](0019-srodowisko-efemeryczne-aws.md), [0022](0022-obraz-kontenera-aplikacji.md), [0023](0023-uruchamianie-stosu-docker-compose.md), [0024](0024-architektura-aws-ec2-docker-compose.md), [0027](0027-rejestr-obrazow-ghcr.md), [0031](0031-konfiguracja-hosta-user-data.md), zadania E05-07, E06-02, E06-03, E07, E09, protokół v1 (`experiment/PROTOCOL.md`, sekcje 3, 4 i 6)

## Kontekst

ADR-0032 przyjął model pull: potok GitHub Actions nie ma żadnych poświadczeń AWS, publikuje obraz w GHCR, a instancja sama pobiera wskazaną wersję i uruchamia stos swoją rolą. Szczegóły zostawił temu ADR:

- skąd instancja wie, który digest wdrożyć,
- jak często sprawdza,
- jak wygląda rollback,
- jak potwierdzić wdrożenie, skoro potok nie widzi instancji,
- z której gałęzi wdrażać (protokół v1 przewiduje `exp/variant-a` i `exp/variant-b`, wywiad OIDC wybrał `main`),
- czy instancja weryfikuje pochodzenie obrazu.

Do tego ADR-0024 zostawił dwie sprawy: skąd na instancji biorą się sekrety z `.env` i skąd plik compose dla AWS (bez usługi `s3` z moto, z prawdziwym kubełkiem).

## Czynniki decyzyjne

- brak poświadczeń w potoku i tokenów na instancji (ADR-0032),
- najmniejsze uprawnienia roli instancji,
- zgodność z zamrożonym protokołem v1,
- odtwarzalność: wdrażany jest konkretny digest, a compose pasuje do obrazu,
- prostota i koszt.

## Rozważane opcje

**Źródło digestu:**

1. Ruchomy tag gałęzi w GHCR (np. `:exp-variant-b`): potok przesuwa go przy publikacji, instancja zamienia tag na digest i uruchamia stos po digeście.
2. Plik z digestem w repozytorium (`deploy/<gałąź>.digest`), commitowany przez potok.
3. GitHub Deployments API odpytywane przez instancję.
4. Digest jako zmienna Terraform (wdrożenie = `terraform apply`, wymiana instancji).

**Wyzwalacz:** timer systemd co 1 minutę, timer co 5 minut, tylko przy starcie i ręcznie przez SSM.

**Gałąź:** `exp/variant-*` wybierana zmienną Terraform, tylko `main`, `main` i `exp/variant-*`.

**Sekrety `.env`:** losowane na instancji przy pierwszym starcie, SSM Parameter Store (`SecureString` z `random_password`), Secrets Manager.

**Rollback:** przesunięcie tagu w GHCR na poprzedni digest, skrypt na instancji przez SSM, oba, `git revert` i nowy build.

**Potwierdzenie wdrożenia:** endpoint wersji w aplikacji i skrypt kontrolny, tylko log na instancji i SSM, raport instancji do GitHub (commit status) tokenem.

**Pochodzenie obrazu:** odroczyć podpis do E06/E07, podpis cosign (keyless) i weryfikacja na instancji teraz, bez podpisu w całym projekcie.

**Plik compose dla AWS:** z repozytorium w commicie obrazu, wbudowany w user-data, z bieżącego HEAD gałęzi.

## Decyzja

Decyzje autora z 2026-11-13. Opcje przygotował agent, a autor wybrał je i wskazał powody z listy.

### Źródło digestu: ruchomy tag w GHCR

Potok przy publikacji obrazu nadaje mu, oprócz tagu z SHA commita, tag gałęzi (`exp-variant-a` albo `exp-variant-b`, bo tag nie może zawierać `/`). Instancja zamienia tag na digest zapytaniem o manifest i uruchamia stos z obrazem przypiętym do digestu (`ghcr.io/...@sha256:...`), nie do tagu. Powody autora:

- **bez zapisu do repozytorium:** potok nie commituje do chronionej gałęzi, więc historia git i dane eksperymentu zostają czyste,
- **prostota:** to ten sam `push` co przy publikacji, z jednym tagiem więcej.

### Wyzwalacz: timer systemd co 1 minutę

Plus wdrożenie przy pierwszym starcie instancji. Powody autora:

- **krótkie czekanie:** przy seriach przebiegów „main” z protokołu opóźnienie wdrożenia jest małe wobec czasu potoku,
- **lekkie zapytanie:** sprawdzenie to jedno zapytanie o manifest, a obraz jest pobierany tylko wtedy, gdy digest się zmienił.

### Gałąź: `exp/variant-*`, wybierana zmienną Terraform

Zmienna warstwy roboczej (np. `deploy_branch`) mówi instancji, tag której gałęzi śledzić. W danej sesji działa jeden wariant. Powody autora:

- **zgodność z protokołem v1:** protokół (sekcje 3, 4 i 6) zakłada wdrożenia z gałęzi bazowych wariantów, więc nie trzeba go znowu zmieniać,
- **koszt:** jedna instancja zamiast dwóch równoległych środowisk.

Uwaga agenta: pull requesty nie dostają tagu gałęzi, więc ta reguła zastępuje zabezpieczenie z sekcji 6, punkt 4 protokołu, jak zapowiedział ADR-0032.

### Sekrety: losowane na instancji

Skrypt user-data przy pierwszym starcie generuje `POSTGRES_PASSWORD`, `JWT_SECRET` i hasła kont z `seed` (`SEED_ALICE_PASSWORD`, `SEED_BOB_PASSWORD`, `SEED_ADMIN_PASSWORD`) do pliku `.env` z prawami 0600, którego właścicielem jest użytkownik `app`. Sekrety nie istnieją poza instancją i znikają z nią przy `destroy`. Hasła kont autor i skrypt audytu odczytują z instancji przez SSM z CloudShell. Losowanie haseł kont to decyzja autora z 2026-11-13, podjęta po wywiadzie, w ramach tej samej decyzji o sekretach. Powody autora:

- **mniej uprawnień:** rola instancji nie potrzebuje `ssm:GetParameter` ani `kms:Decrypt`,
- **prostota:** kilka linii w user-data zamiast zasobów Terraform i odczytu przy starcie.

### Rollback: przesunięcie tagu w GHCR

Workflow uruchamiany ręcznie (`workflow_dispatch`) z digestem przesuwa tag gałęzi na wskazany, wcześniej opublikowany obraz. Timer instancji wdraża go jak każdą inną wersję. Powody autora:

- **ta sama droga co wdrożenie:** rollback to zwykłe wdrożenie innego digestu, więc jest jeden mechanizm do testowania i opisu,
- **ten sam obraz:** wraca dokładnie poprzedni digest, a nie nowy build z revertu,
- **szybkość:** retag i jeden cykl timera zamiast całego potoku.

### Potwierdzenie wdrożenia: endpoint wersji i skrypt kontrolny

Aplikacja zwraca wdrożony digest i commit (np. `/version`, wartości przekazane przy starcie kontenera). Instancja zapisuje każde wdrożenie w dzienniku systemowym (journald). Wdrożenie potwierdza autor albo skrypt audytu: zapytaniem HTTP na publiczny adres albo przez SSM z CloudShell. Potok nie potwierdza wdrożenia. Powody autora:

- **brak tokenu na instancji:** raport do GitHub wymagałby na hoście tokenu z prawem zapisu, więc przejęcie hosta dawałoby dostęp do repozytorium,
- **prostota:** jedna ścieżka w aplikacji i `curl`, bez integracji z API GitHub.

### Pochodzenie obrazu: podpis odroczony

Instancja na razie nie weryfikuje podpisu obrazu. Decyzja o podpisie należy do projektu potoku (E06, E07). Powody autora:

- **K2, krok wspólny A i B:** podpis zmienia publikację w obu wariantach, a według protokołu build, publikacja i wdrożenie są w nich identyczne,
- **czas:** najpierw działające wdrożenie end-to-end, potem wzmocnienia,
- **materiał do 5.3:** brak weryfikacji pochodzenia na hoście to ryzyko szczątkowe modelu pull, które praca opisuje wprost.

### Plik compose dla AWS: z repozytorium w commicie obrazu

Obraz ma etykietę OCI `org.opencontainers.image.revision` z SHA commita. Po pobraniu obrazu instancja odczytuje etykietę i pobiera `compose.yaml` oraz nakładkę dla AWS z `raw.githubusercontent.com` dla tego SHA. Powody autora:

- **spójność obrazu i compose:** oba pochodzą z tego samego commita, bez wyścigu z HEAD gałęzi,
- **bez tokenów:** repozytorium jest publiczne (ADR-0004), więc pliki czyta się anonimowo.

## Konsekwencje

- (+) Wdrożenie i rollback nie wymagają poświadczeń AWS w potoku ani tokenu GitHub na instancji. Instancja czyta tylko publiczne zasoby: pakiet GHCR i pliki repozytorium.
- (+) Wdrażany jest zawsze konkretny digest, zapisany w dzienniku instancji i widoczny w `/version`. Audyt po wdrożeniu (protokół, sekcja 4) może pobrać ten sam obraz po digeście.
- (+) Rola instancji się nie zmienia: SSM do kontroli i kubełek S3 na załączniki (E05-04).
- (−) **Pakiet GHCR trzeba raz ustawić jako publiczny.** Pierwsza publikacja tworzy pakiet prywatny, a zmiany na publiczny nie da się cofnąć (GitHub Docs, sprawdzone 2026-11-13). To zamyka TODO z ADR-0027.
- (−) **Tag w GHCR jest zmienny.** Kto ma `packages: write` w tym repozytorium, ten wskazuje, co wdroży instancja. Ochroną są gałęzie bazowe wariantów, uprawnienie `packages: write` tylko w workflow i przypięcie po digeście. Podpis obrazu jest odroczony (wyżej). Materiał do 2.3 i 5.3.
- (−) **Potok kończy się na publikacji.** Czas i wynik wdrożenia nie są widoczne w potoku. Pomiaru to nie zmienia: H2 mierzy workflow PR, a protokół opisuje pełny potok z wdrożeniem opisowo. Uwaga agenta: E06-03 („Merge do main = nowa wersja na AWS”, OIDC, środowisko `production`) trzeba odczytać przez ten ADR.
- (−) **Opóźnienie wdrożenia do około minuty** plus czas pobrania obrazu. Limity anonimowych zapytań do GHCR nie są opisane w dokumentacji (TODO: zweryfikować); timer robi około 60 zapytań o manifest na godzinę.
- (−) **Sekrety, w tym hasła kont z `seed`, są różne na każdej instancji.** Skrypt audytu po wdrożeniu (protokół, sekcja 4) musi najpierw odczytać hasła przez SSM z CloudShell. Komentarz w `app/.env.example` (hasła w AWS z GitHub Secrets) poprawiono w E05-07.
- (−) `CORS_ORIGINS` musi zawierać publiczny adres instancji. Instancja może go odczytać z IMDSv2 przy starcie (TODO: zweryfikować przy implementacji).
- (−) Zmienna `deploy_branch` w Terraformie: zmiana wariantu w sesji to `apply` z inną wartością. Czy wymusza nową instancję, zależy od tego, czy trafia do user-data (`user_data_replace_on_change`); ustalane przy implementacji.
- Do zrobienia w E05-07: skrypt wdrożenia i jednostki systemd w user-data, nakładka compose dla AWS (bez `s3`, z kubełkiem z Terraformu), endpoint `/version`, zmienna `deploy_branch`, workflow retagu, test end-to-end z rollbackiem. Komentarz w `infra/terraform/work/ec2.tf` o szukaniu instancji po tagach jest nieaktualny.
- Test end-to-end przed E06-02: tymczasowy workflow `e2e-publish.yml` publikuje obraz z tagiem gałęzi i jest usuwany po teście. To decyzja agenta na wzór workflow testowego z E05-06 (dowód zostaje w historii git, skanery E07 nie widzą pliku spoza porównywanych potoków).
- Do E06-02: publikacja z tagiem SHA i tagiem gałęzi oraz etykietami OCI (`org.opencontainers.image.source`, `org.opencontainers.image.revision`).
- Do E05-05 i E09: skrypt wdrożenia zapisuje wersje Dockera i Compose przy każdym wdrożeniu.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- GitHub Docs, *Working with the Container registry* (anonimowy dostęp do publicznych obrazów, `GITHUB_TOKEN`, etykieta `org.opencontainers.image.source`): https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry (sprawdzone 2026-11-13)
- GitHub Docs, *Configuring a package's access control and visibility* (domyślnie prywatny, publicznego nie da się cofnąć): https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility (sprawdzone 2026-11-13)
- Test 2026-11-13: anonimowe zapytanie `HEAD /v2/<obraz>/manifests/<tag>` do `ghcr.io` z tokenem z `ghcr.io/token` zwraca `200` i nagłówek `docker-content-digest` (na publicznym obrazie `zaproxy/zaproxy:stable`).
- Retag bez pobierania obrazu (`docker buildx imagetools create`): TODO: zweryfikować w dokumentacji Dockera przy implementacji.
