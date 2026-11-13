# 0034. Automatyczne sprzątanie: EventBridge Scheduler usuwa instancję po 8 godzinach

- **Status:** przyjęty
- **Data:** 2026-11-13
- **Decydujący:** autor pracy
- **Powiązane:** doprecyzowuje [0019](0019-srodowisko-efemeryczne-aws.md) (zasada 2: codzienne sprzątanie); [0020](0020-nowe-konto-aws-plan-darmowy.md), [0026](0026-stan-terraform-i-warstwy.md), [0029](0029-uprawnienia-uzytkownika-terraform.md), [0030](0030-region-aws-eu-north-1.md), [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md), zadania E05-08, E09-02, E09-03, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-13](../log/2026-11-13.md)

## Kontekst

ADR-0019 wymaga, żeby warstwa robocza istniała tylko w czasie pracy, a to, co zostało po dniu pracy, było usuwane automatycznie. Wybór mechanizmu zostawił zadaniu E05-08. Od tego czasu zmieniły się dwie rzeczy:

- **Potok nie ma poświadczeń AWS.** SCP konta-projektu odrzuca tworzenie dostawcy OIDC, więc wdrożenie działa w modelu pull ([0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md)). Pierwsza opcja z ADR-0019, czyli zaplanowany workflow GitHub z `terraform destroy` przez OIDC, jest niewykonalna, a klucze AWS w GitHub Secrets wyklucza `AGENTS.md`.
- **Konto jest na planie darmowym** ([0020](0020-nowe-konto-aws-plan-darmowy.md)). Wbudowany w AWS Settings limit wydatków (*spend limit*), który wstrzymuje zasoby projektu, wymaga planu płatnego.

Koszt warstwy roboczej to prawie w całości instancja: EC2 `t3.small`, publiczny IPv4 i wolumen EBS. VPC, podsieć, grupy bezpieczeństwa i pusty kubełek załączników są bezpłatne. Zapomniana instancja kosztuje około 0,76 USD na dobę ([`docs/aws-konto.md`](../aws-konto.md)).

Na koncie-projekcie dozwolone są EventBridge Scheduler (`scheduler:*`), Lambda i AWS Budgets: SCP `AllowFreeTierServices` (sprawdzone 2026-11-13). SCP dla limitów wydatków blokuje `scheduler:CreateSchedule` i `lambda:CreateFunction`, ale działa tylko przy włączonym limicie wydatków, więc na tym koncie nie obowiązuje.

## Czynniki decyzyjne

- działanie bez udziału autora i niezależnie od jego komputera,
- działanie także wtedy, gdy instancja jest uszkodzona,
- brak poświadczeń AWS poza kontem (ADR-0032),
- prostota: jak najmniej własnego kodu,
- zgodność z przebiegami eksperymentu, które mogą trwać kilka godzin (E09).

## Rozważane opcje

**Mechanizm:**

1. **EventBridge Scheduler** z celem uniwersalnym `ec2:TerminateInstances`, bez Lambdy.
2. **Samousunięcie instancji:** `instance_initiated_shutdown_behavior = terminate` i timer systemd, który wyłącza host.
3. **Harmonogram zadań Windows** na komputerze autora, uruchamiający `terraform destroy`.
4. **Dwa mechanizmy naraz**, np. samousunięcie i EventBridge Scheduler jako zapas.
5. **Akcja AWS Budgets** zatrzymująca instancję. Agent przedstawił ją w odprawie jako słabszą: akcja zatrzymuje instancję, ale publiczny IPv4 i EBS dalej kosztują, a dane w Budgets odświeżają się z opóźnieniem.

Odpadły przed wywiadem: zaplanowany workflow GitHub (brak OIDC) i limit wydatków AWS (plan płatny).

**Zakres:** tylko instancja (EC2, publiczny IPv4, EBS) albo cała warstwa `work/`.

**Kiedy:** o stałej godzinie wieczorem (22:00 albo 23:30 czasu warszawskiego), po N godzinach od startu instancji, albo oba warunki naraz.

**Wyjątek:** tag na instancji, który wyłącza sprzątanie, albo brak wyjątków.

## Decyzja

Decyzje autora z 2026-11-13. Opcje przygotował agent, a autor wybrał je i wskazał powody z listy.

### Mechanizm: EventBridge Scheduler

Powody autora:

- **niezależny od komputera:** działa, gdy laptop jest wyłączony albo uśpiony,
- **niezależny od hosta:** zadziała także wtedy, gdy instancja się zawiesi albo user-data się nie wykona,
- **usługa zarządzana AWS:** natywny mechanizm chmury, który da się opisać w pracy i zapisać jako kod w Terraformie,
- **bez Lambdy i kodu:** cel uniwersalny wywołuje API EC2 bezpośrednio, więc nie ma własnego kodu do utrzymania.

### Zakres: tylko instancja

Automat usuwa instancję, a z nią publiczny IPv4 i wolumen (`delete_on_termination = true`). VPC, podsieć, grupy bezpieczeństwa, rola instancji i kubełek załączników zostają do najbliższego `terraform destroy`. Powody autora:

- **usuwa to, co kosztuje:** EC2, publiczny IPv4 i EBS to cały koszt warstwy roboczej, a pozostałe zasoby są bezpłatne,
- **pełny `destroy` wymaga Terraformu:** uruchomienie Terraformu w AWS oznaczałoby np. CodeBuild z uprawnieniami do całego stanu, czyli więcej złożoności i szersze uprawnienia,
- **ponowny `apply` odtwarza:** rozjechany stan nie jest problemem, bo kolejny `apply` odtworzy instancję, a `destroy` i tak sprząta resztę.

### Kiedy: 8 godzin od utworzenia instancji

Każda instancja dostaje jednorazowy harmonogram na moment 8 godzin po swoim utworzeniu, a nie stałą godzinę. Powody autora:

- **chroni też w dzień:** instancja zapomniana rano nie czeka do wieczora,
- **niezależny od pory pracy:** autor pracuje o różnych porach, także w nocy, więc stała godzina mogłaby przerwać sesję.

8 godzin to typowy dzień pracy, a koszt zapomnianej instancji do chwili usunięcia to około 0,25 USD.

### Wyjątek: tag `SkipCleanup=true`

Instancja z tym tagiem nie zostanie usunięta. Powody autora:

- **długie przebiegi E09:** tag pozwala dokończyć przebieg eksperymentu bez wyłączania automatu,
- **alert jako druga linia:** zapomniany tag nadal wyłapie dzienny alert budżetowy 0,50 USD.

### Doprecyzowania agenta

Autor ich nie wybierał. Wynikają z powyższych decyzji i zasad projektu:

- **Harmonogram i jego rola są w warstwie roboczej (`work/`)**, nie w stałej. Harmonogram istnieje tylko razem z instancją, którą ma usunąć, więc `destroy` usuwa go razem z nią i warstwa stała nie rośnie.
- **Jednorazowy harmonogram z wyrażeniem `at()`.** Cel uniwersalny wywołuje API z ustalonymi parametrami i nie umie sam odczytać wieku instancji. Dlatego Terraform tworzy harmonogram na moment `apply` + 8 h, z ID tej konkretnej instancji, i odtwarza go przy każdej wymianie instancji (`replace_triggered_by`). Po wykonaniu harmonogram sam się usuwa (`action_after_completion = DELETE`), bo wykonane harmonogramy jednorazowe nadal liczą się do limitu konta.
- **Wyjątek przez politykę roli, nie przez kod.** Rola harmonogramu ma zezwolenie tylko na `ec2:TerminateInstances` dla instancji z tagiem `Project=devsecops-thesis` w regionie konta. Jawna odmowa dla instancji z tagiem `SkipCleanup=true` sprawia, że wywołanie kończy się odmową dostępu, a instancja zostaje. Tag można nadać zmienną Terraform przy `apply` albo w konsoli w trakcie sesji.
- **Zaufanie roli ograniczone do usługi, konta i harmonogramów projektu:** `scheduler.amazonaws.com` z warunkami `aws:SourceAccount` i `aws:SourceArn` (grupa harmonogramów `default` w regionie konta), co chroni przed *confused deputy*. Według dokumentacji `aws:SourceArn` musi być ARN grupy harmonogramów, nie harmonogramu ani prefiksu nazwy. Pierwsza wersja z prefiksem nazwy harmonogramu skończyła się w teście odmową `CreateSchedule`.
- **Użytkownik `terraform` potrzebuje nowych uprawnień:** zarządzanie harmonogramami z prefiksem projektu i `iam:PassRole` roli harmonogramu do `scheduler.amazonaws.com`. Zmiana polityki w `infra/iam/` i w konsoli ([0029](0029-uprawnienia-uzytkownika-terraform.md)).
- **Harmonogram w UTC.** Moment wylicza Terraform z czasu planu (`plantimestamp()`), który jest w UTC, więc strefa czasowa nie ma znaczenia i nie ma problemu ze zmianą czasu.

## Konsekwencje

- (+) Zapomniana instancja kosztuje najwyżej około 8 godzin pracy `t3.small` z IPv4 i EBS (około 0,25 USD), a nie 0,76 USD za każdą dobę. Dotyczy to także dnia, w którym autor nie ma dostępu do komputera.
- (+) Brak własnego kodu i brak poświadczeń poza AWS. Rola harmonogramu umie tylko usunąć instancję projektu. Materiał do 4.2 i do rekomendacji dla małych zespołów.
- (+) Koszt mechanizmu jest pomijalny: EventBridge Scheduler ma 14 mln bezpłatnych wywołań miesięcznie (cennik, sprawdzone 2026-11-13), a projekt użyje najwyżej kilkudziesięciu.
- (−) **Sesja dłuższa niż 8 godzin wymaga działania autora:** tagu `SkipCleanup=true` albo ponownego `apply`, który odtworzy instancję z nowym harmonogramem. Przebiegi E09 trzeba zaplanować z tym ograniczeniem (`experiment/PROTOCOL.md` przy pilotażu E09-01).
- (−) **Po automatycznym usunięciu stan Terraformu nie zgadza się z AWS.** Następny `plan` pokaże odtworzenie instancji i harmonogramu. Reszta warstwy roboczej zostaje do `destroy`. Zasada z ADR-0019 („po zakończeniu zadania `destroy`”) nadal obowiązuje, a automat jest drugą linią obrony.
- (−) Automat nie usuwa niczego poza instancją. Zasób dodany w przyszłości do `work/`, który kosztuje sam z siebie (np. brama NAT, load balancer), wymagałby rozszerzenia mechanizmu. Obecna architektura takich zasobów nie ma ([0024](0024-architektura-aws-ec2-docker-compose.md)).
- (−) **Odmowa przy tagu wyjątku może wywołać ponowienia.** Harmonogram ponawia nieudane wywołania według polityki ponowień. W teście odmowa dostępu nie została ponowiona (sekcja „Weryfikacja”), a w kodzie i tak są tylko dwie próby. Dokumentacji, które błędy Scheduler ponawia, nie sprawdzono (TODO: zweryfikować).
- Akcja AWS Budgets, którą rozważał `docs/aws-konto.md`, nie jest potrzebna. Alerty budżetowe zostają jako druga linia obrony.
- Zasada 2 ADR-0019 („codzienne sprzątanie wieczorem”) przyjmuje postać „usunięcie instancji 8 godzin po utworzeniu”. Aktualizacja w `docs/aws-konto.md`.

## Weryfikacja

Test 2026-11-13 w `eu-north-1` (pojedynczy przebieg, `instance_ttl_hours = 0.25`):

- **Pierwsze `apply` nie utworzyło harmonogramu.** `CreateSchedule` zwrócił `ValidationException: The execution role you provide must allow AWS EventBridge Scheduler to assume the role`, bo warunek `aws:SourceArn` wskazywał prefiks nazwy harmonogramu zamiast grupy. Po zmianie na ARN grupy `default` harmonogram powstał w 16 s (`apply`: 1 dodany, 1 zmieniony).
- **Usunięcie przez harmonogram:** czas z harmonogramu 14:01:49 UTC, wywołanie `TerminateInstances` o 14:02:30 UTC (41 s później; dokumentacja podaje dokładność 60 s). Instancja przeszła `running` → `shutting-down` → `terminated`, powód stanu „User initiated (2026-11-13 14:02:30 GMT)”.
- **CloudTrail (Event history):** wywołujący `assumed-role/devsecops-thesis-cleanup/<sesja>`, `userAgent` `AmazonEventBridgeScheduler`, bez `errorCode`, jedno wywołanie.
- **Po usunięciu:** harmonogram usunął się sam (`list-schedules` puste), wolumen EBS usunięty razem z instancją. VPC, grupy bezpieczeństwa, role i kubełek zostały, zgodnie z decyzją.

- **Odtworzenie po automatycznym usunięciu:** następny `plan` wykrył, że instancja i harmonogram zniknęły poza Terraformem, i zaplanował tylko ich odtworzenie (2 do dodania, 0 zmian). `apply` trwał 14 s (instancja 13 s, harmonogram 1 s).
- **Tag `SkipCleanup=true`:** harmonogram na 14:30:20 UTC wywołał `TerminateInstances` o 14:30:42 UTC. CloudTrail zapisał `errorCode` `Client.UnauthorizedOperation` z komunikatem o jawnej odmowie w polityce tożsamości (instrukcja `KeepInstancesMarkedSkipCleanup`). Instancja dalej działała (`running` o 14:33 UTC), a harmonogram usunął się mimo nieudanego wywołania.
- **Ponowienia po odmowie:** w CloudTrail jest jedno wywołanie, choć `maximum_retry_attempts = 2`, więc Scheduler nie ponowił próby po błędzie uprawnień (obserwacja z kilku minut po wywołaniu, jeden przebieg). Odpowiada to na pytanie z sekcji „Konsekwencje”.

- **`teardown.ps1`:** `destroy` usunął 22 zasoby w 32 s, w tym instancję z tagiem `SkipCleanup=true` (użytkownik `terraform` nie podlega odmowie z polityki roli sprzątania). Harmonogramu nie było już w stanie, bo usunął się sam po wywołaniu, a `destroy` przeszedł bez błędu. Kontrola końcowa (pusty stan `work/`, brak instancji, wolumenów, VPC, adresów Elastic IP i harmonogramów projektu) zakończyła się wynikiem OK po 42 s.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować), wszystkie sprawdzone 2026-11-13:

- AWS, *Managed policies for your organization* (SCP kont-projektów, w tym `AllowFreeTierServices` i SCP dla limitów wydatków): https://docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html
- AWS, *Supported AWS services for Sign up for AWS (new)* (EventBridge, Lambda, AWS Budgets w planie darmowym): https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html
- AWS, *Create a spend limit in AWS Settings* (limit wydatków tylko w planie płatnym): https://docs.aws.amazon.com/accounts/latest/reference/create-spend-limit.html
- AWS, *Schedule types in EventBridge Scheduler* (harmonogramy jednorazowe `at()`, limit konta po wykonaniu, dokładność 60 s): https://docs.aws.amazon.com/scheduler/latest/UserGuide/schedule-types.html
- AWS, *Using universal targets in EventBridge Scheduler*: https://docs.aws.amazon.com/scheduler/latest/UserGuide/managing-targets-universal.html
- AWS, *Amazon EventBridge pricing* (14 mln bezpłatnych wywołań Scheduler miesięcznie): https://aws.amazon.com/eventbridge/pricing/
- Terraform AWS Provider 6.72.0, zasób `aws_scheduler_schedule` (`action_after_completion`, `retry_policy`): https://github.com/hashicorp/terraform-provider-aws/blob/v6.72.0/website/docs/r/scheduler_schedule.html.markdown
