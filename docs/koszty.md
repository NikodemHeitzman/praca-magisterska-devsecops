# Koszty AWS

Rzeczywiste koszty części praktycznej (zadanie E05-08). To dane do rozdziału 5.3 i do rekomendacji dla małych zespołów: ile kosztuje lekki potok DevSecOps z efemerycznym środowiskiem w AWS. Szacunki przed wdrożeniem są w [`aws-konto.md`](aws-konto.md) (sekcja „Szacunek kosztu”) i w [ADR-0024](adr/0024-architektura-aws-ec2-docker-compose.md).

Repozytorium jest publiczne. Ten plik nie zawiera ID konta ani danych rozliczeniowych poza kwotami.

## Jak ograniczamy koszty

| Mechanizm | Co robi | Decyzja |
|---|---|---|
| środowisko efemeryczne | warstwa robocza istnieje tylko w czasie pracy, `terraform destroy` na końcu sesji | [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md) |
| skrypt teardown | `destroy` warstwy `work/` i kontrola, że nic nie zostało | [`infra/terraform/teardown.ps1`](../infra/terraform/teardown.ps1) |
| automatyczne sprzątanie | EventBridge Scheduler usuwa instancję 8 h po utworzeniu (chyba że ma tag `SkipCleanup=true`) | [ADR-0034](adr/0034-automatyczne-sprzatanie-eventbridge-scheduler.md) |
| budżety | 10 USD miesięcznie, 0,50 USD dziennie, alerty e-mail, koszt przed kredytami | [`aws-konto.md`](aws-konto.md), sekcja „Budżety i alerty” |

## Jak odczytać koszty

Raz w miesiącu, po zamknięciu miesiąca (dane rozliczeniowe dochodzą z opóźnieniem, więc najlepiej kilka dni po jego końcu), odczyt w konsoli AWS jako Owner:

1. **Billing and Cost Management → Cost Explorer.**
2. Zakres dat: cały miesiąc. Granulacja: **Monthly**. Grupowanie: **Service**.
3. Filtr **Charge type**: tylko **Usage**. Bez tego kredyty zerują wynik i tabela pokazuje 0 USD.
4. Zapisać do tabel niżej koszt całkowity i pozycje większe niż 0,01 USD.
5. Osobno odczytać kredyty: ten sam widok z filtrem **Charge type = Credit**. Pozostałe kredyty pokazuje AWS Settings albo Billing (Credits).

Konsola Cost Explorer jest bezpłatna. Każde zapytanie do API Cost Explorer (`aws ce ...`) kosztuje 0,01 USD (cennik AWS Cost Explorer, sprawdzone 2026-11-13). Jeśli zamiast konsoli wolisz CloudShell, wystarczy jedno zapytanie na miesiąc:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-11-01,End=2026-12-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --filter '{"Dimensions":{"Key":"RECORD_TYPE","Values":["Usage"]}}' \
  --group-by Type=DIMENSION,Key=SERVICE
```

Użytkownik `terraform` nie ma uprawnień `ce:*` i nie powinien ich mieć, bo jego polityka obejmuje tylko zasoby projektu ([ADR-0029](adr/0029-uprawnienia-uzytkownika-terraform.md)).

**Tag `Project` jako tag alokacji kosztów.** Żeby filtrować koszty po tagu `Project=devsecops-thesis`, trzeba go aktywować w Billing → Cost allocation tags. Tag działa tylko dla kosztów od chwili aktywacji, nie wstecz. Stan: TODO: aktywować (autor) i wpisać tu datę. Na tym koncie nie ma innych projektów, więc koszt całego konta jest równy kosztowi pracy.

## Koszty miesięczne

Koszt przed odjęciem kredytów, bez VAT, w USD.

| Miesiąc | Koszt (Usage) | Kredyty wykorzystane | Kredyty pozostałe | Godziny instancji | Data odczytu | Uwagi |
|---|---|---|---|---|---|---|
| 2026-11 | TODO | TODO | TODO | TODO | TODO | pierwszy miesiąc: sesje E05-04, E05-05, E05-07, E05-08 |

„Godziny instancji” pochodzą z Cost Explorer (Usage type `BoxUsage:t3.small`, jednostka Hrs) albo z sumy czasów sesji w dzienniku badawczym.

### Pozycje według usług

Wypełniać dla każdego miesiąca z tabeli wyżej.

| Miesiąc | Usługa | Koszt (USD) | Uwagi |
|---|---|---|---|
| 2026-11 | Amazon EC2 (instancja) | TODO | |
| 2026-11 | Amazon VPC (publiczny IPv4) | TODO | |
| 2026-11 | EC2 – Other (EBS) | TODO | |
| 2026-11 | Amazon S3 (stan, załączniki) | TODO | |
| 2026-11 | pozostałe | TODO | |

## Warstwa stała

ADR-0019 szacuje warstwę stałą (kubełek stanu, użytkownicy IAM, budżety, później CloudTrail z kubełkiem logów) na mniej niż 1 USD miesięcznie (TODO: zweryfikować na podstawie miesiąca, w którym warstwa robocza nie działała, albo z pozycji S3 i CloudTrail w tabeli wyżej).

## Szacunek a rzeczywistość

| Pozycja | Szacunek | Rzeczywistość |
|---|---|---|
| środowisko 24/7, `eu-north-1` | około 21 USD/mies. ([ADR-0030](adr/0030-region-aws-eu-north-1.md)) | nie dotyczy (środowisko efemeryczne) |
| 100 godzin pracy w miesiącu | około 2,9 USD | TODO |
| dzień pracy (8 h) | około 0,25 USD | TODO |
| doba z zapomnianą instancją | około 0,76 USD; po ADR-0034 najwyżej około 0,25 USD | TODO |
| cały projekt (4 miesiące) | około 15–20 USD ([ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md)) | TODO (podsumowanie w E15) |
