# 0018. Konto AWS: istniejące konto autora, plan płatny

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Zastępuje:** [0017](0017-plan-konta-aws-darmowy.md)
- **Powiązane:** [0016](0016-uwierzytelnianie-do-aws.md), [0019](0019-srodowisko-efemeryczne-aws.md), zadania E01-07, E05-03, E05-08, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

[ADR-0017](0017-plan-konta-aws-darmowy.md) zakładał nowe konto na planie darmowym ze 100 USD kredytów. Warunki AWS Free Tier dają kredyty tylko nowym klientom i tylko dla jednego konta („you are not eligible to receive Free Tier Credits for more than one account”). Autor ma już konto AWS, więc nowe konto najpewniej nie dostałoby kredytów. Bez kredytów nowe konto nie daje nic poza tym, co daje istniejące.

Szacunek kosztu z 2026-10-30 (ceny `eu-central-1` z AWS Price List API, bez VAT): architektura z E05-03 (EC2 `t3.small` z docker compose, publiczny IPv4, EBS 20 GB, ECR, S3, CloudTrail, CloudWatch) kosztuje około 24 USD miesięcznie przy pracy 24/7, czyli około 97 USD za 4 miesiące (styczeń–kwiecień 2027). Gdy środowisko działa tylko w czasie pracy (około 100 h miesięcznie), wychodzi około 15–20 USD za cały projekt. Szczegóły w `docs/aws-konto.md`.

## Czynniki decyzyjne

- koszt,
- wysiłek założenia i zabezpieczenia konta,
- zgodność z warunkami AWS.

## Rozważane opcje

1. istniejące konto autora, plan płatny (*pay-as-you-go*)
2. nowe konto na planie darmowym ([0017](0017-plan-konta-aws-darmowy.md))
3. nowe konto na nowe dane (e-mail, karta), żeby dostać kredyty jeszcze raz

## Decyzja

Wybrano **istniejące konto autora na planie płatnym**. Powody autora:

- nowe konto najpewniej nie dostanie kredytów, bo autor miał już konto AWS, więc nie obniża kosztu,
- istniejące konto jest gotowe i nie trzeba zakładać nowego,
- koszt ogranicza dyscyplina: środowisko istnieje tylko w czasie pracy ([0019](0019-srodowisko-efemeryczne-aws.md)).

Opcję 3 odrzucono w [0017](0017-plan-konta-aws-darmowy.md): łamie warunki AWS Free Tier.

## Konsekwencje

- (+) Konto nie wygasa, więc znika ryzyko zamknięcia konta w trakcie E09 opisane w [0017](0017-plan-konta-aws-darmowy.md).
- (+) Dostęp do wszystkich usług, łącznie z Fargate i Lightsail, bez ograniczeń planu darmowego.
- (−) Każda godzina działania zasobów kosztuje. Ochrona kosztowa to zasady z [0019](0019-srodowisko-efemeryczne-aws.md) i alerty budżetowe.
- (−) Stare konto może mieć pozostałości: zasoby w innych regionach, klucze dostępu roota, nieużywanych użytkowników IAM. Przed pracą trzeba je przejrzeć (lista kroków w `docs/aws-konto.md`). Kryteria E01-07 obowiązują bez zmian.
- (−) AWS dolicza VAT do faktur klientów indywidualnych w UE. Stawka 23% według wiedzy agenta, TODO: zweryfikować na pierwszej fakturze.
- Darmowe limity *Always Free* (np. część limitów CloudWatch) obowiązują też na planie płatnym. TODO: zweryfikować, które dotyczą starego konta.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować), sprawdzone 2026-10-30:

- AWS, *AWS Free Tier Terms*, https://aws.amazon.com/free/terms/.
- AWS Price List API, `eu-central-1`: AmazonEC2, AmazonRDS, AmazonECS, AmazonECR, AmazonS3, AmazonCloudWatch, AWSCloudTrail, `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<usługa>/current/eu-central-1/index.json`.
- AWS, *Amazon VPC Pricing* (publiczne IPv4: 0,005 USD/h), https://aws.amazon.com/vpc/pricing/.
