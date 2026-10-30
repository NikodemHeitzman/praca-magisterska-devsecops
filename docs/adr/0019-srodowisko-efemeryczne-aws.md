# 0019. Środowisko AWS efemeryczne: zasoby tylko w czasie pracy

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0018](0018-istniejace-konto-aws-plan-platny.md), [0016](0016-uwierzytelnianie-do-aws.md), zadania E05-03, E05-04, E05-07, E05-08, E06-03, E08-01, E09-02, E09-03, E15-08, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Konto działa na planie płatnym ([0018](0018-istniejace-konto-aws-plan-platny.md)), więc zasoby kosztują za każdą godzinę. Środowisko z E05-03 działające 24/7 kosztuje około 24 USD miesięcznie bez VAT. Aplikacja jest potrzebna tylko wtedy, gdy autor pracuje nad zadaniem albo gdy trwa przebieg eksperymentu. Infrastruktura jest w Terraformie, więc można ją postawić i usunąć jedną komendą.

## Czynniki decyzyjne

- koszt,
- ryzyko zapomnianych zasobów,
- wpływ na zadania, które wymagają działającego środowiska (wdrożenie z `main`, audyt po wdrożeniu).

## Rozważane opcje

1. środowisko stałe (24/7) przez cały projekt
2. środowisko efemeryczne: `terraform apply` na początku pracy, `terraform destroy` po zakończeniu zadania, codzienne sprzątanie wieczorem i alerty budżetowe

## Decyzja

Wybrano **środowisko efemeryczne**. Powód autora: to najbardziej logiczne przy płatnym koncie. Zasady (autor):

1. **Po każdym `terraform apply` i zakończeniu zadania środowisko idzie w dół** (`terraform destroy`). Dotyczy także sesji agentów AI (zasada w `AGENTS.md`).
2. **Codzienne sprzątanie wieczorem.** Wszystko, co zostało po dniu pracy, jest usuwane automatycznie.
3. **Rygorystyczne alerty budżetowe** (progi w `docs/aws-konto.md`).

Doprecyzowania agenta (do potwierdzenia w E05-08):

- **Dwie warstwy zasobów.** Warstwa robocza (EC2, publiczny IPv4, EBS, grupy bezpieczeństwa, sieć) podlega `destroy`. Warstwa stała jest tania i potrzebna między sesjami: kubełek stanu Terraformu, dostawca OIDC i rola potoku, użytkownicy IAM, budżety, trail CloudTrail z kubełkiem logów (wymóg audytowalności z E08-01), repozytorium ECR albo GHCR. Szacunek warstwy stałej: poniżej 1 USD miesięcznie, TODO: zweryfikować w E05-08 na podstawie Cost Explorer.
- **Mechanizm codziennego sprzątania** wybiera E05-08 (ADR). Opcje: zaplanowany workflow GitHub Actions (`schedule`) z `terraform destroy` warstwy roboczej przez OIDC; EventBridge Scheduler z funkcją Lambda; akcja AWS Budgets zatrzymująca instancje EC2 po przekroczeniu progu. Godzina: wieczorem, dokładną ustala E05-08. Zaplanowane workflow GitHub uruchamiają się według UTC i mogą się opóźniać (TODO: zweryfikować w dokumentacji GitHub).

## Konsekwencje

- (+) Koszt projektu spada z około 97 USD (4 miesiące 24/7) do około 15–20 USD bez VAT (szacunek z [0018](0018-istniejace-konto-aws-plan-platny.md)).
- (+) Środowisko jest regularnie odtwarzane z kodu, więc Terraform jest stale sprawdzany pod kątem powtarzalności. Materiał do 4.2.
- (−) **Wdrożenie z `main` (E06-03, E05-07) wymaga działającego środowiska.** Merge do `main` przy usuniętej infrastrukturze zakończy job deploy błędem. Do rozstrzygnięcia w E05-03 i E06-03: potok stawia warstwę roboczą sam (`terraform apply` w potoku) albo deploy działa tylko w sesjach, w których środowisko jest postawione. Pierwsza opcja wydłuża potok. H2a dotyczy workflow PR, a pełny potok z wdrożeniem raportujemy opisowo (E03-02), więc wpływ na pomiar jest ograniczony (TODO: zweryfikować przy E06-03).
- (−) Przebiegi E09-02 i E09-03 z audytem po wdrożeniu muszą się zmieścić w jednej sesji ze środowiskiem postawionym albo stawiać je za każdym razem od nowa. Każde odtworzenie to dodatkowa zmienna (nowy adres IP, nowy wolumen). Ująć w `experiment/PROTOCOL.md` przy pilotażu (E09-01).
- (−) Dane w bazie PostgreSQL na EBS znikają przy `destroy`. Aplikacja ma dane z `seed.py`, więc odtworzenie jest proste, ale trzeba je wykonać przy każdym `apply` (np. w user-data albo kroku wdrożenia).
- (−) Alerty AWS Budgets przychodzą z opóźnieniem, bo dane kosztowe odświeżają się kilka razy na dobę (TODO: zweryfikować). Główną ochroną jest więc `destroy` i automatyczne sprzątanie, a alerty są drugą linią.
- Sprzątanie po obronie (E15-08) obejmuje warstwę stałą.

## Źródła

- Szacunek kosztu: [0018](0018-istniejace-konto-aws-plan-platny.md), `docs/aws-konto.md`.
- Mechanizmy sprzątania: TODO: zweryfikować w dokumentacji GitHub (`on.schedule`) i AWS (EventBridge Scheduler, AWS Budgets actions) w E05-08.
