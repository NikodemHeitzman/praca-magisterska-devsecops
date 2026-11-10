# 0021. Dostęp autora do konsoli AWS: konto właściciela (Owner) z MFA

- **Status:** przyjęty
- **Data:** 2026-11-10
- **Decydujący:** autor pracy
- **Zastępuje częściowo:** [0016](0016-uwierzytelnianie-do-aws.md) (punkt „użytkownik IAM administratora do pracy w konsoli”)
- **Powiązane:** [0020](0020-nowe-konto-aws-plan-darmowy.md), [0019](0019-srodowisko-efemeryczne-aws.md), zadania E01-07, E05, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-10](../log/2026-11-10.md)

## Kontekst

[ADR-0016](0016-uwierzytelnianie-do-aws.md) zakładał, że autor pracuje w konsoli jako użytkownik IAM z MFA, a root służy tylko do czynności awaryjnych. Na koncie z [ADR-0020](0020-nowe-konto-aws-plan-darmowy.md) konsola działa inaczej (stan z 2026-11-10):

- właściciel konta loguje się przez AWS Builder ID i ma rolę *Owner*,
- strona IAM ostrzega, że użytkownicy IAM są przeznaczeni do dostępu programowego. Utworzony użytkownik `Admin-magister` nie miał w zakładce *Security credentials* sekcji logowania do konsoli,
- ludzi dodaje się przez *Team* (settings.aws.com/team). Członek zespołu dostaje dostęp deweloperski, bez uprawnień administracyjnych i finansowych, a zaproszenie wymaga osobnego adresu e-mail.

Czy logowanie użytkownika IAM do konsoli da się w tym modelu włączyć inną drogą: TODO: zweryfikować w dokumentacji AWS.

## Czynniki decyzyjne

- liczba osób (jedna),
- dostępne mechanizmy w nowej konsoli,
- zasada najmniejszych uprawnień i zalecenie, by nie pracować na co dzień na koncie właściciela.

## Rozważane opcje

1. praca jako Owner z MFA
2. drugi adres e-mail autora zaproszony do zespołu (dostęp deweloperski), Owner tylko do billingu i sytuacji awaryjnych
3. użytkownik IAM z hasłem do konsoli (droga z [0016](0016-uwierzytelnianie-do-aws.md))

## Decyzja

Wybrano **pracę jako Owner z MFA**. Powód autora: tak działa nowa konsola. Użytkownik IAM nie ma logowania do konsoli, a członek zespołu nie ma uprawnień administracyjnych, więc przy jednej osobie nie ma innej sensownej drogi.

Pozostałe ustalenia [0016](0016-uwierzytelnianie-do-aws.md) obowiązują: potok przez OIDC, osobny użytkownik IAM `terraform` z kluczem tylko lokalnie (E05), brak kluczy roota. Użytkownik `Admin-magister` jest zbędny i zostaje usunięty.

## Konsekwencje

- (+) Jedno logowanie z MFA, bez dodatkowych tożsamości do utrzymania.
- (−) Codzienna praca na koncie właściciela, czyli z pełnymi uprawnieniami, także finansowymi. To odstępstwo od zasady najmniejszych uprawnień, do opisania w 5.3 (ograniczenia).
- Środki łagodzące: MFA na Builder ID i na klasycznym roocie, brak kluczy dostępu roota (`AccountAccessKeysPresent = 0`), budżety z alertami, środowisko efemeryczne ([0019](0019-srodowisko-efemeryczne-aws.md)), zasoby tworzone przez Terraform, a nie ręcznie w konsoli.
- Materiał do 2.3 (model współdzielonej odpowiedzialności): konsola AWS w 2026 r. zmieniła model tożsamości dla nowych kont. TODO: zweryfikować w dokumentacji AWS i dodać źródło.

## Źródła

- Konsola AWS (IAM, Team, AWS Builder ID), stan z 2026-11-10 (zrzuty ekranu autora, nie publikowane).
- Dokumentacja AWS o Builder ID i zespołach: TODO: zweryfikować i dodać.
