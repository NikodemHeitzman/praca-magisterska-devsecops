# 0029. Uprawnienia użytkownika IAM `terraform`: własna polityka w repozytorium

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0016](0016-uwierzytelnianie-do-aws.md), [0021](0021-dostep-do-konsoli-owner.md), [0026](0026-stan-terraform-i-warstwy.md), zadania E05-04, E05-06, E08-01, E15-08, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

ADR-0016 wprowadził lokalnego użytkownika IAM `terraform` z długoterminowym kluczem na komputerze autora (świadome odstępstwo) i zostawił otwarte pytanie, czy wystarczy coś węższego niż `AdministratorAccess`. Terraform z E05-04 musi tworzyć VPC, EC2, kubełki S3, role IAM i profile instancji. Rola instancji to rola IAM, więc użytkownik `terraform` musi móc tworzyć role i przekazywać je do EC2 (`iam:PassRole`).

## Czynniki decyzyjne

- skutki wycieku klucza z dysku autora,
- zgodność z tematem pracy (najmniejsze uprawnienia, NIST SP 800-204D),
- czas potrzebny na dopracowanie polityki.

## Rozważane opcje

1. własna polityka JSON w repozytorium: tylko potrzebne działania EC2 i VPC, S3 na kubełkach projektu, IAM na rolach z prefiksem projektu
2. polityka zarządzana `AdministratorAccess`, opisana jako odstępstwo
3. `AdministratorAccess` na start, potem zawężenie na podstawie logów CloudTrail

## Decyzja

Wybrano **własną politykę zapisaną w repozytorium** (`infra/iam/terraform-user-policy.json`). Autor tworzy użytkownika w konsoli i dołącza do niego tę politykę. Powody autora:

- **najmniejsze uprawnienia:** wyciek klucza z dysku nie daje dostępu do całego konta, co łagodzi odstępstwo z ADR-0016,
- **temat pracy:** praca dotyczy bezpieczeństwa potoku, a `AdministratorAccess` byłby łatwym zarzutem recenzenta,
- **polityka jako kod:** plik JSON w repozytorium można przejrzeć, skanować i opisać w pracy.

Zasady polityki (projekt agenta):

- działania IAM tylko na rolach i profilach instancji z prefiksem `devsecops-thesis-`, a `iam:PassRole` tylko do usługi `ec2.amazonaws.com`,
- działania S3 tylko na kubełkach z prefiksem `devsecops-thesis-`,
- działania EC2 i VPC potrzebne do warstwy roboczej, ograniczone do regionu `eu-north-1` (ADR-0030) warunkiem `aws:RequestedRegion`,
- brak uprawnień do IAM użytkowników, polityk konta, Billing i Organizations.

Uprawnienia do dostawcy OIDC (E05-06) i CloudTrail (E08-01) dopisują te zadania, kiedy dodadzą zasoby do `shared/`.

## Konsekwencje

- (+) Klucz `terraform` nie pozwala tworzyć użytkowników IAM ani dowolnych ról, więc wyciek nie daje trwałego przejęcia konta przez nowe tożsamości (ograniczenie z prefiksem nazw).
- (+) Polityka jest materiałem do 4.2 i do oceny zgodności z najmniejszymi uprawnieniami.
- (−) Polityka wymaga dopracowania przez kolejne próby (`AccessDenied` przy `plan` i `apply`). Każda zmiana zasobów w Terraformie może wymagać jej rozszerzenia.
- (−) Odczytowe działania EC2 (`Describe*`) nie obsługują ograniczeń do zasobów, więc obejmują całe konto w regionie.
- (−) Ryzyko szczątkowe (uwaga agenta): `iam:PutRolePolicy` na rolach z prefiksem pozwala dopisać roli dowolną politykę wbudowaną, a `iam:PassRole` i `ec2:RunInstances` pozwalają uruchomić instancję z tą rolą. Kto ma klucz `terraform`, może więc pośrednio uzyskać szersze uprawnienia. Domknięciem byłaby granica uprawnień (*permissions boundary*) wymagana przy `iam:CreateRole`. Do rozważenia w E05-06 albo jako ograniczenie w 5.3 (TODO: zweryfikować z autorem).
- (−) Zmiana polityki to krok ręczny autora w konsoli (polityka nie jest zarządzana przez Terraform, bo użytkownik `terraform` nie może zmieniać własnych uprawnień).
- Użytkownik i klucz są usuwane przy sprzątaniu po obronie (E15-08).

## Źródła

- AWS, *IAM JSON policy elements: Condition* i *Actions, resources, and condition keys for Amazon EC2*: TODO: zweryfikować adresy przy pisaniu polityki.
- [@NIST-SP800-204D]: zasada najmniejszych uprawnień dla poświadczeń potoku, TODO: zweryfikować numer rekomendacji.
