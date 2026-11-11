# Konto AWS

Konfiguracja konta AWS dla części praktycznej pracy (zadanie E01-07). Decyzje: [ADR-0030](adr/0030-region-aws-eu-north-1.md) (region; zastąpił [ADR-0015](adr/0015-region-aws-eu-central-1.md)), [ADR-0016](adr/0016-uwierzytelnianie-do-aws.md) (uwierzytelnianie), [ADR-0020](adr/0020-nowe-konto-aws-plan-darmowy.md) (nowe konto, plan darmowy), [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md) (środowisko efemeryczne). Zastąpione: [ADR-0017](adr/0017-plan-konta-aws-darmowy.md), [ADR-0018](adr/0018-istniejace-konto-aws-plan-platny.md).

Repozytorium jest publiczne. Ten plik nie zawiera ID konta, adresów e-mail, nazw urządzeń MFA ani kluczy.

## Stan

| Pozycja | Stan |
|---|---|
| Konto | nowe konto autora, dane właściciela potwierdzone przez autora 2026-11-10 |
| Plan | darmowy (Free account plan), 100 USD kredytów |
| Wygaśnięcie planu | 2027-05-10 albo wcześniej, po wyczerpaniu kredytów (konsola Billing, 2026-11-10); plan B: przejście na plan płatny |
| Przegląd konta (2026-11-10) | Cost Explorer bez danych (nowe konto), Resource Explorer: brak zasobów w `eu-north-1` (wyszukiwanie we wszystkich regionach jeszcze niewłączone), IAM: 0 użytkowników |
| Stare konto autora | do zamknięcia (decyzja autora) |
| Root bez kluczy dostępu | tak: `AccountAccessKeysPresent = 0` (`aws iam get-account-summary` w CloudShell, 2026-11-10) |
| MFA | logowanie właściciela przez AWS Builder ID: MFA TOTP od 2026-11-10; klasyczny root: MFA dodane 2026-11-10 (potwierdzenie autora; wcześniej `AccountMFAEnabled = 0`), TODO: zapisać wynik `AccountMFAEnabled = 1` z CloudShell |
| Alerty budżetowe | utworzone 2026-11-10 przez `aws budgets create-budget` w CloudShell: `devsecops-thesis-monthly` (10 USD) i `devsecops-thesis-daily` (0,50 USD), oba bez kredytów; subskrybent e-mail sprawdzony (`describe-subscribers-for-notification`); test doręczenia e-maila odłożony do pierwszego kosztu w E05 (decyzja autora 2026-11-10: na pustym koncie koszt wynosi 0, więc alert się nie wyzwoli) |

## Region

`eu-north-1` (Sztokholm) dla całej infrastruktury, od 2026-11-11. Konto-projekt z nowego typu rejestracji ma region przypisany według kraju, a SCP `RegionFloor` zarządzana przez AWS odrzuca żądania w innych regionach (poza `us-east-1` i `us-west-2`). Uzasadnienie w [ADR-0030](adr/0030-region-aws-eu-north-1.md); wcześniej `eu-central-1` według [ADR-0015](adr/0015-region-aws-eu-central-1.md).

## Tożsamości

| Tożsamość | Do czego | MFA | Klucz dostępu |
|---|---|---|---|
| właściciel konta (Owner, AWS Builder ID) | codzienna praca w konsoli ([ADR-0021](adr/0021-dostep-do-konsoli-owner.md)) | tak (TOTP) | nie dotyczy |
| klasyczny root | tylko czynności wymagające roota | tak | brak (`AccountAccessKeysPresent = 0`) |
| użytkownik IAM `terraform` | lokalny Terraform (warstwy `shared/` i `work/`) | nie dotyczy (dostęp programowy) | tak, tylko na komputerze autora, profil nazwany w `~/.aws/credentials` |
| rola instancji EC2 | pobranie i uruchomienie wdrażanego obrazu (model pull, [ADR-0032](adr/0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md)), SSM, kubełek załączników | nie dotyczy | brak, poświadczenia krótkotrwałe z IMDSv2 |

Odstępstwo dla klucza `terraform` opisuje [ADR-0016](adr/0016-uwierzytelnianie-do-aws.md). Kluczy AWS nie zapisujemy w repozytorium ani w GitHub Secrets. Potok GitHub Actions nie ma tożsamości w AWS: SCP konta-projektu odrzuca tworzenie dostawców tożsamości (`iam:*Provider*`), więc OIDC z ADR-0016 jest niewykonalne ([ADR-0032](adr/0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md)).

## Zasady kosztowe (wymóg projektu)

Według [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md):

1. **Środowisko istnieje tylko w czasie pracy.** Po `terraform apply` i zakończeniu zadania (albo sesji) zawsze `terraform destroy` warstwy roboczej. Dotyczy autora i agentów AI.
2. **Codzienne sprzątanie wieczorem.** Mechanizm automatyczny usuwa warstwę roboczą, jeśli została. Mechanizm i godzinę ustala E05-08. Do czasu jego wdrożenia sprzątanie jest ręczne, na koniec każdego dnia pracy.
3. **Warstwa stała** (stan Terraformu, użytkownicy IAM, budżety, CloudTrail z kubełkiem logów, rejestr obrazów) zostaje do sprzątania po obronie (E15-08).
4. **Przed zakończeniem sesji** sprawdzenie, że nic nie zostało: `terraform state list` dla warstwy roboczej jest pusty, a w Cost Explorer lub Resource Explorer nie ma zasobów z `Project=devsecops-thesis` poza warstwą stałą.

## Budżety i alerty

Progi zaproponował agent, autor zażądał rygorystycznych alertów:

| Budżet | Okres | Kwota | Alerty e-mail |
|---|---|---|---|
| projekt, miesięczny | miesiąc | 10 USD | rzeczywisty ≥ 50% (5 USD), ≥ 80% (8 USD), ≥ 100% (10 USD); prognozowany ≥ 100% |
| zapomniane zasoby, dzienny | dzień | 0,50 USD | rzeczywisty ≥ 100% |

Uzasadnienie progu dziennego: dzień pracy (około 8 h `t3.small` z IPv4 i EBS) kosztuje około 0,25 USD, a doba z zapomnianą instancją około 0,76 USD. Próg 0,50 USD nie reaguje na zwykły dzień pracy, a reaguje na zapomniane środowisko. Czy budżety dzienne obsługują alerty prognozowane: TODO: zweryfikować (dlatego tylko alert rzeczywisty).

Adres alertów: główny e-mail autora (nie zapisujemy go tutaj). Budżety bez akcji są bezpłatne (cennik AWS Budgets, sprawdzone 2026-10-30). Na planie darmowym koszty pokrywają kredyty, więc budżet ma liczyć koszt przed odjęciem kredytów (w opcjach budżetu odznaczyć kredyty), inaczej pokaże 0 USD i nie ostrzeże przed zużywaniem kredytów. Dane kosztowe w Budgets odświeżają się z opóźnieniem (TODO: zweryfikować jak dużym), więc alert jest drugą linią obrony po `destroy` i sprzątaniu. Akcję budżetu zatrzymującą EC2 rozważa E05-08.

Test działania: TODO: po ustawieniu zapisać datę testowego e-maila albo pierwszego alertu.

## Szacunek kosztu

Ceny `eu-central-1` z AWS Price List API (publikacja z października 2026, sprawdzone 2026-10-30), bez VAT. Po zmianie regionu (ADR-0030) EC2 i EBS są w `eu-north-1` tańsze: około 21 USD miesięcznie przy 24/7 zamiast 23 USD (tabela w ADR-0030). Architektura według [ADR-0024](adr/0024-architektura-aws-ec2-docker-compose.md): EC2 z docker compose (aplikacja i PostgreSQL w kontenerach), dostęp przez SSM, bez load balancera i bramy NAT. Rzeczywiste koszty zapisuje E05-08 w `docs/koszty.md`.

| Pozycja | Cena | Za miesiąc 24/7 |
|---|---|---|
| EC2 `t3.small` (2 vCPU, 2 GiB) | 0,024 USD/h | 17,52 USD |
| publiczny IPv4 | 0,005 USD/h | 3,65 USD |
| EBS gp3, 20 GB | 0,0952 USD/GB-mies. | 1,90 USD |
| ECR, około 1 GB | 0,10 USD/GB-mies. | 0,10 USD |
| S3 (stan, załączniki, logi CloudTrail), poniżej 1 GB | 0,0245 USD/GB-mies. | ~0,10 USD |
| CloudTrail, zdarzenia zarządcze (pierwsza kopia) | 0 | 0 |
| CloudWatch: logi około 1 GB, 1–2 alarmy | 0,63 USD/GB, 0,10 USD/alarm | ~0,80 USD |
| **Razem** | | **~24 USD** |

Wariant oszczędny z [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md) (około 100 h działania w miesiącu, przez 4 miesiące): około 15–20 USD za cały projekt. Porównanie z alternatywami (`t4g.small`, `t3.micro`, RDS, ECS Fargate, ECS Express Mode, App Runner) na cenach z 2026-11-11 jest w [ADR-0024](adr/0024-architektura-aws-ec2-docker-compose.md).

## Konwencja tagów

Każdy zasób tworzony przez Terraform dostaje tagi przez `default_tags` w providerze `aws`:

| Tag | Wartości | Znaczenie |
|---|---|---|
| `Project` | `devsecops-thesis` | wszystkie zasoby pracy; filtr w Cost Explorer i przy sprzątaniu |
| `Variant` | `a`, `b`, `shared` | wariant potoku, który wdrożył zasób; `shared` dla wspólnych (np. kubełek stanu) |
| `ManagedBy` | `terraform`, `manual` | czy zasób jest w stanie Terraformu |
| `Owner` | `NikodemHeitzman` | login GitHub autora |

Zasoby założone ręcznie (np. budżety, użytkownicy IAM) dostają te same tagi z `ManagedBy=manual`, jeśli usługa obsługuje tagi. Tag `Project` aktywować jako *cost allocation tag* w Billing.

## Lista kroków przygotowania konta (autor)

1. **Przegląd konta.** Wykonany 2026-11-10 (sekcja „Stan”). Opcjonalnie: włączyć w Resource Explorer wyszukiwanie we wszystkich regionach.
2. **Root:** MFA, brak kluczy dostępu (menu konta → Security credentials).
3. **Dostęp do konsoli:** praca jako Owner z MFA ([ADR-0021](adr/0021-dostep-do-konsoli-owner.md)). Użytkownik IAM `Admin-magister` (utworzony przed tą decyzją) do usunięcia.
4. **Budżety i alerty** według sekcji wyżej, test e-maila.
5. **Użytkownik IAM `terraform`** z kluczem dostępu, profil w `~/.aws/credentials`, test `aws sts get-caller-identity --profile <profil>`.
6. Region: `eu-north-1`, narzucony przez konto (ADR-0030); w konsoli nie da się go zmienić.
7. Uzupełnienie sekcji „Stan” i daty testu alertu w tym pliku.

Roli dla potoku nie ma: SCP konta blokuje dostawcę OIDC, a wdrożenie działa w modelu pull ([ADR-0032](adr/0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md)).
