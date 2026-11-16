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

Według dokumentacji AWS (*Sign up for AWS*, sprawdzone 2026-11-16) na kontach z nowej ścieżki rejestracji użytkownicy i role IAM służą tylko do dostępu programowego, nie do konsoli. Którą ścieżką założono konto projektu (`docs/aws-konto.md` wymienia też klasycznego roota): TODO: zweryfikować.

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
- Materiał do 2.3 (model współdzielonej odpowiedzialności): konsola AWS w 2026 r. zmieniła model tożsamości dla nowych kont. Nowa ścieżka rejestracji (What's New z 2026-09-16, wdrażana stopniowo) tworzy konto należące do AWS Builder ID, bez użytkownika root: https://aws.amazon.com/about-aws/whats-new/2026/09/New-AWS-Builder-Experience (sprawdzone 2026-11-16).

## Źródła

- Konsola AWS (IAM, Team, AWS Builder ID), stan z 2026-11-10 (zrzuty ekranu autora, nie publikowane).
- AWS, *Sign up for AWS*: https://docs.aws.amazon.com/accounts/latest/reference/sign-up-for-aws.html; What's New z 2026-09-16 (jw.); sprawdzone 2026-11-16.
