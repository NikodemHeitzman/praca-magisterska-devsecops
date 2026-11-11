# 0030. Region AWS: eu-north-1 (Sztokholm), region przypisany kontu

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** zastępuje [0015](0015-region-aws-eu-central-1.md); [0020](0020-nowe-konto-aws-plan-darmowy.md), [0024](0024-architektura-aws-ec2-docker-compose.md), [0028](0028-system-instancji-ubuntu-przypiete-ami.md), [0029](0029-uprawnienia-uzytkownika-terraform.md), zadanie E05-04, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

ADR-0015 wybrał region `eu-central-1` (Frankfurt). Pierwsze `terraform apply` w E05-04 (2026-11-11) skończyło się błędem `AccessDenied` z dopiskiem „explicit deny in a service control policy”. Ustalenia:

- Konto z ADR-0020 założono przez nowy typ rejestracji AWS („Sign up for AWS (new)”, konta-projekty). Należy ono do organizacji AWS, którą AWS tworzy i zarządza w imieniu właściciela (`aws organizations describe-organization` w CloudShell).
- Polityka SCP tej organizacji ma instrukcję `RegionFloor`, która odrzuca żądania poza dopuszczonymi regionami. Dla tego konta są to `eu-north-1`, `us-east-1` i `us-west-2`, plus żądania bez regionu. Wyjątek dotyczy kilku działań Amazon Bedrock. Źródło: zdekodowany komunikat odmowy (`aws sts decode-authorization-message`, 2026-11-11).
- Według dokumentacji AWS konto-projekt dostaje jeden region według kraju w adresie kontaktowym. Dla Polski to Europe (Stockholm), `eu-north-1`. Region nie zmienia się po zmianie adresu. Inny region daje tylko aktywacja zaawansowanych funkcji („activate advanced features”), która wymaga przejścia na plan płatny, usuwa limit wydatków i jest nieodwracalna.

## Czynniki decyzyjne

- pozostanie na planie darmowym z kredytami (ADR-0020),
- dane w UE (powód z ADR-0015),
- odwracalność decyzji,
- liczba zmian w już przyjętych decyzjach.

## Rozważane opcje

1. `eu-north-1`, czyli region przypisany kontu
2. aktywacja zaawansowanych funkcji (plan płatny), zmiana SCP `RegionFloor` i pozostanie w `eu-central-1`
3. nowe konto z klasycznej rejestracji („Sign up for AWS (advanced)”) z wolnym wyborem regionu

## Decyzja

Wybrano **`eu-north-1` (Sztokholm)** dla całej infrastruktury. Powody autora:

- **pozostanie na planie darmowym:** kredyty i limit wydatków zostają, a opcja 2 wymaga planu płatnego,
- **dane nadal w UE:** Sztokholm jest w UE, więc powód „dane w UE” z ADR-0015 pozostaje spełniony.

Opcja 3 odpada razem z opcją 2 z powodu planu darmowego. Byłaby też kolejną zmianą konta po ADR-0017, 0018 i 0020 (uwaga agenta, nie powód autora).

### Koszt po zmianie regionu

Ceny `eu-north-1` z AWS Price List API, bez VAT, sprawdzone 2026-11-11 (AmazonEC2 `20261110173852`, AmazonVPC `20261105181945`). Założenia jak w ADR-0024: 730 h przy 24/7, 100 h w trybie efemerycznym, EBS 20 GB.

| Składnik | `eu-central-1` (ADR-0024) | `eu-north-1` |
|---|---|---|
| `t3.small` | 0,024 USD/h | 0,0216 USD/h |
| publiczny IPv4 | 0,005 USD/h | 0,005 USD/h |
| EBS gp3 | 0,0952 USD/GB-mies. | 0,0836 USD/GB-mies. |
| **razem 24/7** | **23,07 USD/mies.** | **21,09 USD/mies.** |
| **razem 100 h** | **3,16 USD** | **2,89 USD** |

Porównania wariantów z ADR-0024 (Fargate, RDS, App Runner) nie przeliczano. Wybór EC2 z compose nie zależał od regionu.

## Konsekwencje

- (+) Konto zostaje na planie darmowym z kredytami (ADR-0020). Koszt środowiska jest o około 9% niższy.
- (+) SCP `RegionFloor` zarządzana przez AWS jest dodatkową barierą: zasoby nie powstaną przypadkiem w innym regionie. To materiał do 2.3 (model współdzielonej odpowiedzialności) i 4.2.
- (−) Zmiana regionu w kodzie Terraform (provider, backend, strefa dostępności `eu-north-1a`), w polityce użytkownika `terraform` (warunek `aws:RequestedRegion`) i w `app/.env.example`.
- (−) Nowe AMI: identyfikatory AMI są regionalne. Przypięty obraz w ADR-0028 zmienia się na `ami-06fb1802e2b757f09` (ta sama kompilacja Ubuntu 24.04 z 2026-10-23).
- (−) Większe opóźnienie z Polski niż do Frankfurtu (TODO: zweryfikować pomiarem, jeśli będzie potrzebne w pracy). Dla aplikacji badawczej bez ruchu użytkowników to bez znaczenia.
- (−) Konto-projekt nie pozwala zmienić regionu bez nieodwracalnej aktywacji zaawansowanych funkcji. To ograniczenie do 5.3 i ciekawostka dla rekomendacji dla małych zespołów: nowy typ konta upraszcza start, ale narzuca region.
- Lekcja procesowa: ADR-0015 przyjęto przed sprawdzeniem ograniczeń nowego typu konta (ADR-0020). Dokumentacja AWS zaleca sprawdzenie regionu projektu w AWS Settings przed tworzeniem zasobów.
- Aktualizacja: `AGENTS.md`, `docs/aws-konto.md`, ADR-0026, ADR-0028, ADR-0029, `infra/`.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- AWS, *AWS Regions for your projects*: https://docs.aws.amazon.com/accounts/latest/reference/project-regions.html (sprawdzone 2026-11-11)
- AWS, *Activate advanced AWS features*: https://docs.aws.amazon.com/accounts/latest/reference/activate-advanced-features.html (sprawdzone 2026-11-11)
- AWS, *Supported AWS services for Sign up for AWS (new)*: https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html (sprawdzone 2026-11-11)
- AWS Price List API, cenniki regionalne `eu-north-1` (AmazonEC2 `20261110173852`, AmazonVPC `20261105181945`): https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/
- Ubuntu Cloud Image Locator (AMI `eu-north-1`), sprawdzone 2026-11-11
