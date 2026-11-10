# 0020. Konto AWS: nowe konto na planie darmowym

- **Status:** przyjęty
- **Data:** 2026-11-10
- **Decydujący:** autor pracy
- **Zastępuje:** [0018](0018-istniejace-konto-aws-plan-platny.md)
- **Powiązane:** [0017](0017-plan-konta-aws-darmowy.md), [0019](0019-srodowisko-efemeryczne-aws.md), zadania E01-07, E05, E09, E15-08, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-10](../log/2026-11-10.md)

## Kontekst

[ADR-0018](0018-istniejace-konto-aws-plan-platny.md) wybrał istniejące konto autora na planie płatnym, bo zakładano, że nowe konto nie dostanie kredytów Free Tier. Autor założył jednak nowe konto i dostał plan darmowy. Stan z konsoli (Billing, 2026-11-10): 100 USD kredytów, 183 dni do wygaśnięcia planu, czyli do 2027-05-10. Warunki planu darmowego opisuje [ADR-0017](0017-plan-konta-aws-darmowy.md): plan kończy się po 6 miesiącach albo po wyczerpaniu kredytów, potem konto zostaje zamknięte, a dane są przechowywane przez 90 dni.

Szacunek kosztu projektu w trybie efemerycznym ([0019](0019-srodowisko-efemeryczne-aws.md)) to około 15–20 USD bez VAT, więc mieści się w kredytach.

## Czynniki decyzyjne

- koszt,
- czas dostępności konta wobec harmonogramu (M4: 2027-04-25),
- zgodność z warunkami AWS.

## Rozważane opcje

1. nowe konto na planie darmowym (100 USD kredytów)
2. istniejące konto autora na planie płatnym ([0018](0018-istniejace-konto-aws-plan-platny.md))

## Decyzja

Wybrano **nowe konto na planie darmowym**. Powód autora: kredyty pokrywają koszt projektu, więc projekt nic nie kosztuje.

Dane właściciela konta (dane kontaktowe, metoda płatności) są danymi autora. Potwierdził to autor 2026-11-10. Stare konto autor zamyka.

Zasady środowiska efemerycznego z [0019](0019-srodowisko-efemeryczne-aws.md) obowiązują bez zmian. Chronią teraz kredyty: ich wyczerpanie zamyka konto tak samo jak upływ 6 miesięcy.

Plan B (z [0017](0017-plan-konta-aws-darmowy.md)): przejście na plan płatny przed wygaśnięciem planu albo w ciągu 90 dni po nim, także wtedy, gdyby AWS cofnął kredyty.

## Konsekwencje

- (+) Koszt projektu pokrywają kredyty (szacunek: 15–20 USD wobec 100 USD).
- (+) Czyste konto: bez zasobów, użytkowników IAM i historii kosztów (przegląd 2026-11-10, `docs/aws-konto.md`).
- (−) Plan wygasa 2027-05-10, 15 dni po M4 (2027-04-25). Opóźnienie E09 wymaga przejścia na plan płatny (plan B). Przypomnienie: przy punkcie kontrolnym tempa po M2 (2027-02-14) sprawdzić zapas.
- (−) Plan darmowy daje dostęp tylko do części usług. Dostępność ECS i Fargate sprawdzić w konsoli przed ADR-em architektury (E05-03). EC2 i ECR są dostępne (strona AWS Free Tier, 2026-10-30).
- (−) Warunki AWS Free Tier dają kredyty najwyżej dla jednego konta. Stare konto autora pochodzi sprzed modelu kredytowego z lipca 2025 i kredytów nie dostało (według autora, TODO: zweryfikować w warunkach, czy wcześniejsze konto wpływa na uprawnienie).
- (−) Dołączenie do AWS Organizations przełącza konto na plan płatny. Zgodne z [0016](0016-uwierzytelnianie-do-aws.md), który Organizations odrzuca.

## Źródła

- Konsola AWS Billing, stan kredytów i planu, 2026-11-10 (zrzut ekranu autora, nie publikowany).
- Źródła warunków planu darmowego: [ADR-0017](0017-plan-konta-aws-darmowy.md), sekcja „Źródła”.
