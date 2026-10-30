# Konto AWS

Konfiguracja konta AWS dla części praktycznej pracy (zadanie E01-07). Decyzje: [ADR-0015](adr/0015-region-aws-eu-central-1.md) (region), [ADR-0016](adr/0016-uwierzytelnianie-do-aws.md) (uwierzytelnianie), [ADR-0018](adr/0018-istniejace-konto-aws-plan-platny.md) (istniejące konto, plan płatny), [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md) (środowisko efemeryczne). [ADR-0017](adr/0017-plan-konta-aws-darmowy.md) (plan darmowy) jest zastąpiony.

Repozytorium jest publiczne. Ten plik nie zawiera ID konta, adresów e-mail, nazw urządzeń MFA ani kluczy.

## Stan

| Pozycja | Stan |
|---|---|
| Konto | istniejące konto autora |
| Plan | płatny (*pay-as-you-go*), bez kredytów Free Tier |
| Przegląd pozostałości starego konta | TODO: wykonać (lista kroków niżej) |
| Root z MFA, bez kluczy dostępu | TODO: potwierdzić |
| Alerty budżetowe | TODO: ustawić i przetestować |

## Region

`eu-central-1` (Frankfurt) dla całej infrastruktury. Uzasadnienie w [ADR-0015](adr/0015-region-aws-eu-central-1.md).

## Tożsamości

| Tożsamość | Do czego | MFA | Klucz dostępu |
|---|---|---|---|
| root | tylko czynności awaryjne i wymagające roota | tak | brak (sprawdzić w IAM → Security credentials) |
| użytkownik IAM administratora (autor) | praca w konsoli | tak | brak |
| użytkownik IAM `terraform` | lokalny Terraform, utworzenie roli OIDC (bootstrap E05) | nie dotyczy (dostęp programowy) | tak, tylko na komputerze autora, profil nazwany w `~/.aws/credentials` |
| rola IAM potoku (OIDC) | wdrożenie z GitHub Actions | nie dotyczy | brak, poświadczenia krótkotrwałe |

Odstępstwo dla klucza `terraform` opisuje [ADR-0016](adr/0016-uwierzytelnianie-do-aws.md). Kluczy AWS nie zapisujemy w repozytorium ani w GitHub Secrets.

## Zasady kosztowe (wymóg projektu)

Według [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md):

1. **Środowisko istnieje tylko w czasie pracy.** Po `terraform apply` i zakończeniu zadania (albo sesji) zawsze `terraform destroy` warstwy roboczej. Dotyczy autora i agentów AI.
2. **Codzienne sprzątanie wieczorem.** Mechanizm automatyczny usuwa warstwę roboczą, jeśli została. Mechanizm i godzinę ustala E05-08. Do czasu jego wdrożenia sprzątanie jest ręczne, na koniec każdego dnia pracy.
3. **Warstwa stała** (stan Terraformu, OIDC i rola potoku, użytkownicy IAM, budżety, CloudTrail z kubełkiem logów, rejestr obrazów) zostaje do sprzątania po obronie (E15-08).
4. **Przed zakończeniem sesji** sprawdzenie, że nic nie zostało: `terraform state list` dla warstwy roboczej jest pusty, a w Cost Explorer lub Resource Explorer nie ma zasobów z `Project=devsecops-thesis` poza warstwą stałą.

## Budżety i alerty

Progi zaproponował agent, autor zażądał rygorystycznych alertów:

| Budżet | Okres | Kwota | Alerty e-mail |
|---|---|---|---|
| projekt, miesięczny | miesiąc | 10 USD | rzeczywisty ≥ 50% (5 USD), ≥ 80% (8 USD), ≥ 100% (10 USD); prognozowany ≥ 100% |
| zapomniane zasoby, dzienny | dzień | 0,50 USD | rzeczywisty ≥ 100% |

Uzasadnienie progu dziennego: dzień pracy (około 8 h `t3.small` z IPv4 i EBS) kosztuje około 0,25 USD, a doba z zapomnianą instancją około 0,76 USD. Próg 0,50 USD nie reaguje na zwykły dzień pracy, a reaguje na zapomniane środowisko. Czy budżety dzienne obsługują alerty prognozowane: TODO: zweryfikować (dlatego tylko alert rzeczywisty).

Adres alertów: główny e-mail autora (nie zapisujemy go tutaj). Budżety bez akcji są bezpłatne (cennik AWS Budgets, sprawdzone 2026-10-30). Dane kosztowe w Budgets odświeżają się z opóźnieniem (TODO: zweryfikować jak dużym), więc alert jest drugą linią obrony po `destroy` i sprzątaniu. Akcję budżetu zatrzymującą EC2 rozważa E05-08.

Test działania: TODO: po ustawieniu zapisać datę testowego e-maila albo pierwszego alertu.

## Szacunek kosztu

Ceny `eu-central-1` z AWS Price List API (publikacja z października 2026, sprawdzone 2026-10-30), bez VAT. Architektura z rekomendacji E05-03: EC2 z docker compose (aplikacja i PostgreSQL w kontenerach), dostęp przez SSM, bez load balancera i bramy NAT. Rzeczywiste koszty zapisuje E05-08 w `docs/koszty.md`.

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

Wariant oszczędny z [ADR-0019](adr/0019-srodowisko-efemeryczne-aws.md) (około 100 h działania w miesiącu, przez 4 miesiące): około 15–20 USD za cały projekt. Alternatywy do E05-03: `t4g.small` 0,0192 USD/h, `t3.micro` 0,012 USD/h (1 GiB, ryzyko braku pamięci), RDS `db.t4g.micro` PostgreSQL 0,019 USD/h + 0,137 USD/GB-mies., Fargate 0,04656 USD za vCPU-h + 0,00511 USD za GB-h.

## Konwencja tagów

Każdy zasób tworzony przez Terraform dostaje tagi przez `default_tags` w providerze `aws`:

| Tag | Wartości | Znaczenie |
|---|---|---|
| `Project` | `devsecops-thesis` | wszystkie zasoby pracy; filtr w Cost Explorer i przy sprzątaniu |
| `Variant` | `a`, `b`, `shared` | wariant potoku, który wdrożył zasób; `shared` dla wspólnych (np. rola OIDC, sieć) |
| `ManagedBy` | `terraform`, `manual` | czy zasób jest w stanie Terraformu |
| `Owner` | `NikodemHeitzman` | login GitHub autora |

Zasoby założone ręcznie (np. budżety, użytkownicy IAM) dostają te same tagi z `ManagedBy=manual`, jeśli usługa obsługuje tagi. Tag `Project` aktywować jako *cost allocation tag* w Billing.

## Lista kroków przygotowania konta (autor)

1. **Przegląd pozostałości.** W Billing → Bills sprawdzić, czy konto generuje koszty. W Resource Explorer albo w konsoli EC2, S3, RDS, Lambda i Elastic IP przejrzeć wszystkie regiony. Usunąć to, co niepotrzebne. Usunąć nieużywanych użytkowników IAM i ich klucze.
2. **Root:** MFA, brak kluczy dostępu (IAM → Security credentials). Stare konta mogą mieć klucze roota, które trzeba usunąć.
3. **Użytkownik IAM administratora** z MFA. Dalsza praca z niego, nie z roota.
4. **Budżety i alerty** według sekcji wyżej, test e-maila.
5. **Użytkownik IAM `terraform`** z kluczem dostępu, profil w `~/.aws/credentials`, test `aws sts get-caller-identity --profile <profil>`.
6. Region w konsoli: `eu-central-1`.
7. Uzupełnienie sekcji „Stan” i daty testu alertu w tym pliku.

Rola OIDC dla potoku powstaje w E05 z Terraformu.
