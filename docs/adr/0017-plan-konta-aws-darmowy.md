# 0017. Plan konta AWS: darmowy (Free account plan)

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0003](0003-dostawca-chmury-aws.md), [0015](0015-region-aws-eu-central-1.md), zadania E01-07, E05, E09, E15-08, [`docs/aws-konto.md`](../aws-konto.md), harmonogram pracy (`docs/harmonogram.md` w vaulcie Obsidiana, poza repozytorium), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Autor zakłada nowe konto AWS, bo stare nie ma już darmowego pakietu. Od 15 lipca 2025 r. nowe konto wybiera przy rejestracji plan darmowy albo płatny. Według dokumentacji AWS (sprawdzone 2026-10-30) oba plany dają 100 USD kredytów na start i do 100 USD więcej za wykonanie zadań. Plan darmowy nie nalicza opłat, ale kończy się po 6 miesiącach albo po wyczerpaniu kredytów, zależnie od tego, co nastąpi wcześniej. Potem konto zostaje zamknięte, a AWS przechowuje dane przez 90 dni, w trakcie których można przejść na plan płatny. Plan darmowy daje dostęp tylko do części usług.

Infrastruktura AWS jest potrzebna od E05 (styczeń 2027) do zebrania danych eksperymentu, M4 (2027-04-25 według harmonogramu).

## Czynniki decyzyjne

- koszt: autor nie chce płacić za infrastrukturę pracy,
- czas dostępności konta wobec harmonogramu,
- dostęp do usług potrzebnych w E05.

## Rozważane opcje

1. plan darmowy
2. plan płatny z kredytami i alertem budżetowym

## Decyzja

Wybrano **plan darmowy**, ponieważ autor nie chce płacić za magisterkę, a według niego 6 miesięcy wystarczy na testy i pisanie pracy. Aktywne konto nie jest potrzebne na obronie.

Ryzyko wygaśnięcia przed końcem eksperymentu autor przyjmuje.

Plan B: przejście na plan płatny przed wygaśnięciem albo w ciągu 90 dni po nim. Konto i dane zostają, a niewykorzystane kredyty przechodzą na kolejne rachunki (dokumentacja AWS). Alert budżetowy ogranicza koszt. Propozycja agenta, przyjęta przez autora 2026-10-30.

Odrzucony plan B: nowe konto na nowy e-mail i nową kartę i odtworzenie infrastruktury z Terraformu. Warunki AWS Free Tier mówią, że kredytów Free Tier nie można otrzymać dla więcej niż jednego konta („you are not eligible to receive Free Tier Credits for more than one account”). Drugie konto tej samej osoby nie dostałoby więc kredytów zgodnie z warunkami, a zakładanie go po to, by je obejść, łamałoby warunki.

## Konsekwencje

- (+) Brak opłat. Na planie darmowym AWS nie nalicza kosztów.
- (−) Konto założone na początku listopada 2026 r. wygaśnie około początku maja 2027 r., tydzień po M4. Opóźnienie dopuszczalne w harmonogramie (decyzja o przesunięciu po M4) może zamknąć konto w trakcie E09. Termin wygaśnięcia zapisać w `docs/aws-konto.md` po założeniu konta.
- (−) Plan B oznacza koszty po wyczerpaniu kredytów. Górną granicę wyznacza budżet z `docs/aws-konto.md`.
- (−) Usługi wybrane w E05 muszą być dostępne na planie darmowym. Stan sprawdzony 2026-10-30 na stronie AWS Free Tier dla kontenerów:
  - **EC2:** dostępne na planie darmowym, za kredyty; typy instancji kwalifikujące się do planu darmowego to m.in. `t3.micro`, `t3.small`, `t4g.micro`, `t4g.small`,
  - **ECR:** dostępne na obu planach, za kredyty,
  - **Lightsail:** 90-dniowy okres próbny tylko na planie płatnym,
  - **ECS (poza ECS Anywhere), Fargate, App Runner:** strona ich nie wymienia. TODO: zweryfikować w konsoli po założeniu konta (warunki odsyłają do listy w konsoli) przed ADR-em architektury w E05.
- (−) Warunki AWS: konta na planie darmowym służą do ewaluacji i nie powinny przetwarzać danych wrażliwych. Aplikacja ma tylko dane testowe z `seed.py`, więc to nie ogranicza projektu.
- (−) Dołączenie do AWS Organizations automatycznie przełącza konto na plan płatny (dokumentacja AWS). Zgodne z [0016](0016-uwierzytelnianie-do-aws.md), który odrzuca Organizations.
- Alert budżetowy chroni przed szybkim zużyciem kredytów, które też zamyka konto (`docs/aws-konto.md`).

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować), sprawdzone 2026-10-30:

- AWS Billing, *Choosing a plan*, https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html.
- AWS Billing, *Explore AWS services with AWS Free Tier*, https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier.html.
- AWS, *AWS Free Tier FAQs*, https://aws.amazon.com/free/free-tier-faqs/.
- AWS, *AWS Free Tier Terms*, https://aws.amazon.com/free/terms/ (jedno konto z kredytami, zastosowanie ewaluacyjne, przejście na plan płatny przy Organizations).
- AWS, *AWS Free Tier: Containers*, https://aws.amazon.com/free/containers/ (EC2, ECR, Lightsail na planach).
- AWS What's New (2025-07), *AWS Free Tier now offers $200 in credits and 6-month free plan*, https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/.
