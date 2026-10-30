# Konto AWS

Konfiguracja konta AWS dla części praktycznej pracy (zadanie E01-07). Decyzje: [ADR-0015](adr/0015-region-aws-eu-central-1.md) (region), [ADR-0016](adr/0016-uwierzytelnianie-do-aws.md) (uwierzytelnianie), [ADR-0017](adr/0017-plan-konta-aws-darmowy.md) (plan konta).

Repozytorium jest publiczne. Ten plik nie zawiera ID konta, adresów e-mail, nazw urządzeń MFA ani kluczy.

## Stan

| Pozycja | Stan |
|---|---|
| Konto | do założenia (nowe, osobne konto do pracy) |
| Data założenia | TODO: uzupełnić po założeniu |
| Plan | darmowy (Free account plan) |
| Wygaśnięcie planu | data założenia + 6 miesięcy albo wyczerpanie kredytów; TODO: uzupełnić datę z konsoli Billing |

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

## Budżet i alerty

Wybór agenta, na prośbę autora:

- jeden budżet kosztów (*cost budget*), miesięczny, 10 USD,
- alert e-mail przy koszcie rzeczywistym ≥ 80% (8 USD),
- alert e-mail przy koszcie prognozowanym ≥ 100% (10 USD),
- adres: główny e-mail autora (nie zapisujemy go tutaj).

Budżety bez akcji są bezpłatne, a dwa budżety z akcjami miesięcznie też nic nie kosztują (cennik AWS Budgets, sprawdzone 2026-10-30). Na planie darmowym AWS nie nalicza opłat, więc alert ostrzega przed szybkim zużywaniem kredytów, którego wyczerpanie zamyka konto. Budżet ma liczyć koszt przed odjęciem kredytów, inaczej pokaże 0 USD (TODO: zweryfikować nazwę tej opcji przy zakładaniu budżetu).

Test działania: TODO: po założeniu zapisać datę testowego e-maila albo pierwszego alertu.

## Konwencja tagów

Każdy zasób tworzony przez Terraform dostaje tagi przez `default_tags` w providerze `aws`:

| Tag | Wartości | Znaczenie |
|---|---|---|
| `Project` | `devsecops-thesis` | wszystkie zasoby pracy; filtr w Cost Explorer i przy sprzątaniu (E15-08) |
| `Variant` | `a`, `b`, `shared` | wariant potoku, który wdrożył zasób; `shared` dla wspólnych (np. rola OIDC, sieć) |
| `ManagedBy` | `terraform`, `manual` | czy zasób jest w stanie Terraformu |
| `Owner` | `NikodemHeitzman` | login GitHub autora |

Zasoby założone ręcznie (np. budżet, użytkownicy IAM) dostają te same tagi z `ManagedBy=manual`, jeśli usługa obsługuje tagi. Tag `Project` aktywować jako *cost allocation tag* w Billing (TODO: zweryfikować, czy to działa na planie darmowym).

## Lista kroków przy zakładaniu konta (autor)

1. Rejestracja nowego konta, wybór planu darmowego, region w konsoli `eu-central-1`.
2. Root: MFA, sprawdzenie, że nie ma kluczy dostępu.
3. Użytkownik IAM administratora z MFA. Dalsza praca już z niego, nie z roota.
4. Budżet i alerty według sekcji wyżej, test e-maila.
5. Użytkownik IAM `terraform` z kluczem dostępu, profil w `~/.aws/credentials`, test `aws sts get-caller-identity --profile <profil>`.
6. Uzupełnienie sekcji „Stan” i daty testu alertu w tym pliku.

Rola OIDC dla potoku powstaje w E05 z Terraformu.
