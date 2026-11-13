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
| 2026-11 (wstępnie, 1–13 XI) | 0,0059 | 0,0059 | TODO | 0,18 (niepełne) | 2026-11-13 | odczyt wstępny, dane szacunkowe (`Estimated: True`) i opóźnione; powtórzyć po zamknięciu miesiąca |

„Godziny instancji” pochodzą z Cost Explorer (Usage type `BoxUsage:t3.small`, jednostka Hrs) albo z sumy czasów sesji w dzienniku badawczym.

**Odczyt z 2026-11-13 jest niepełny.** Cost Explorer pokazał 0,18 h `t3.small` (około 11 minut), a tego samego dnia instancje działały łącznie ponad 50 minut (test ADR-0034, przy czym wcześniejsze sesje E05-04, E05-05 i E05-07 też trwały dłużej). Dane w Cost Explorer dochodzą z opóźnieniem i są oznaczone jako szacunkowe, więc ostateczne wartości za listopad trzeba odczytać po zamknięciu miesiąca (TODO: początek grudnia 2026).

### Pozycje według usług

Wypełniać dla każdego miesiąca z tabeli wyżej.

| Miesiąc | Usługa | Koszt (USD) | Uwagi |
|---|---|---|---|
| 2026-11 (wstępnie) | Amazon Elastic Compute Cloud – Compute | 0,0038820 | `t3.small`, 0,18 h |
| 2026-11 (wstępnie) | Amazon Virtual Private Cloud | 0,0009597 | publiczny IPv4, 0,19 h |
| 2026-11 (wstępnie) | Amazon Simple Storage Service | 0,0005682 | żądania do kubełków stanu i załączników |
| 2026-11 (wstępnie) | EC2 – Other | 0,0004509 | wolumen EBS gp3 i transfer danych |
| 2026-11 (wstępnie) | AWS Secrets Manager | 0,0000100 | 2 żądania API; projekt nie używa tej usługi (TODO: zweryfikować pochodzenie w CloudTrail) |
| 2026-11 (wstępnie) | AWS CloudShell | 0,0000010 | |
| 2026-11 (wstępnie) | AWS Glue, AWS KMS, Amazon SNS, Amazon SQS | 0 | w darmowym limicie |
| 2026-11 (wstępnie) | **razem** | **0,0058718** | równe wykorzystanym kredytom |

### Surowe dane: typy użycia

Odczyt 2026-11-13 (CloudShell, `aws ce get-cost-and-usage`, okres 2026-11-01 do 2026-11-14 bez dnia końcowego, `RECORD_TYPE = Usage`, grupowanie `USAGE_TYPE`, metryki `UnblendedCost` i `UsageQuantity`). Wartości jak w odpowiedzi API.

| Typ użycia | Koszt (USD) | Ilość | Jednostka |
|---|---|---|---|
| EUC1-DataTransfer-In-Bytes | 0 | 0.00000036 | GB |
| EUC1-DataTransfer-Out-Bytes | 0 | 0.0000005076 | GB |
| EUC1-Requests-Tier1 | 0.0000054 | 1 | Requests |
| EUN1-AWSSecretsManagerAPIRequest | 0.00001 | 2 | API Requests |
| EUN1-BoxUsage:t3.small | 0.0038819952 | 0.179722 | Hrs |
| EUN1-Catalog-Request | 0 | 7 | Requests |
| EUN1-DataTransfer-In-Bytes | 0 | 0.0054128403 | GB |
| EUN1-DataTransfer-Out-Bytes | 0 | 0.0004748804 | GB |
| EUN1-DataTransfer-Regional-Bytes | 0 | 0.1167659155 | GB |
| EUN1-DataTransfer-xAZ-In-Bytes | 0 | 0.00185614 | GB |
| EUN1-DataTransfer-xAZ-Out-Bytes | 0 | 0.0108927945 | GB |
| EUN1-EBS:VolumeUsage.gp3 | 0.0004508982 | 0.0053935186 | GB-Month |
| EUN1-EBSOptimized:t3.small | 0 | 0.179722 | Hrs |
| EUN1-EU-AWS-In-Bytes | 0 | 0.00000863 | GB |
| EUN1-EU-AWS-Out-Bytes | 0.0000000236 | 0.0000011791 | GB |
| EUN1-EUW2-AWS-In-Bytes | 0 | 0.0000060871 | GB |
| EUN1-EUW2-AWS-Out-Bytes | 0.0000001217 | 0.0000060871 | GB |
| EUN1-PublicIPv4:InUseAddress | 0.00095972 | 0.191944 | Hrs |
| EUN1-Requests-Tier1 | 0.000435 | 91 | Requests |
| EUN1-Requests-Tier2 | 0.0001276 | 319 | Requests |
| EUN1-TimedStorage-ByteHrs | 0.0000001978 | 0.0000086 | GB-Month |
| EUN1-USE1-AWS-In-Bytes | 0 | 0.00005507 | GB |
| EUN1-USE1-AWS-Out-Bytes | 0.000000877 | 0.00004385 | GB |
| Global-Bucket-Hrs-FreeTier | 0 | 0.0027777778 | Bucket-Mo |
| eu-north-1-KMS-Requests | 0 | 10 | Requests |

Kredyty w tym samym okresie (`RECORD_TYPE = Credit`): −0,0058718337 USD.

Obserwacje:

- **Pozycje `EUC1-…` (Frankfurt)** pochodzą z pierwszej próby `apply` w `eu-central-1`, którą odrzuciła SCP konta (E05-04, ADR-0030).
- **Żądania KMS** wynikają najpewniej z szyfrowania wolumenu EBS kluczem zarządzanym przez AWS (`aws/ebs`) i mieszczą się w darmowym limicie (TODO: zweryfikować).
- **Odczyt przez API kosztuje więcej niż infrastruktura.** Pięć zapytań `ce` z 2026-11-13 to 0,05 USD, czyli około ośmiokrotność kosztu całej infrastruktury w tym okresie. Kolejne odczyty lepiej robić w konsoli albo ograniczyć do jednego zapytania zbiorczego na miesiąc.

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
