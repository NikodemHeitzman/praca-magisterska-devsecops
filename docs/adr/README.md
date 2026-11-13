# Rejestr decyzji architektonicznych (ADR)

ADR (*Architecture Decision Record*) to krótki zapis jednej decyzji technicznej: jaki był problem, jakie opcje rozważono, co wybrano i z jakimi konsekwencjami. Rejestr zachowuje uzasadnienie wyborów, nie tylko ich wynik. Jest źródłem materiału do rozdziału 4 (projekt i realizacja potoku) i do podrozdziału 5.3 (ograniczenia).

## Zasady

1. **Jedna decyzja na plik.** Jeśli w jednym ADR pojawia się „i”, na przykład „GitHub Actions i AWS”, zwykle są to dwie decyzje.
2. **Nazwa pliku:** `NNNN-krotki-tytul.md`, gdzie numer jest czterocyfrowy i nadawany kolejno (`0001`, `0002`, …). Tytuł pisz małymi literami, bez polskich znaków, z myślnikami.
3. **Kopiuj [`_szablon.md`](_szablon.md).** Sekcje: kontekst, czynniki decyzyjne, rozważane opcje, decyzja, konsekwencje.
4. **Statusy:** `proponowany` → `przyjęty`; później ewentualnie `zastąpiony przez NNNN` albo `wycofany`.
5. **Nie edytuj treści przyjętego ADR.** Gdy decyzja się zmienia, napisz nowy ADR, a w starym zmień tylko status na `zastąpiony przez NNNN`. Historia zmian zdania jest materiałem do pracy.
6. **Uzasadnienia muszą być prawdziwe.** Nie dopisuj powodów, których nie było, ani źródeł z pamięci. Czego nie wiadomo, oznacz `TODO: zweryfikować`. Źródła cytuj kluczem z rejestru źródeł (`[@KLUCZ]`).
7. **Wpis w dzienniku** ([`../log/`](../log/)) z dnia decyzji zawiera link do ADR.

## Indeks

| Nr | Decyzja | Status | Data |
|---|---|---|---|
| [0001](0001-platforma-ci-cd-github-actions.md) | Platforma CI/CD: GitHub Actions | przyjęty | 2026-10-01 |
| [0002](0002-konteneryzacja-docker.md) | Konteneryzacja aplikacji: Docker | przyjęty | 2026-10-01 |
| [0003](0003-dostawca-chmury-aws.md) | Dostawca chmury: AWS | przyjęty | 2026-10-01 |
| [0004](0004-publiczne-repozytorium.md) | Publiczne repozytorium | przyjęty | 2026-10-01 |
| [0005](0005-baza-danych-postgresql.md) | Baza danych aplikacji: PostgreSQL | przyjęty | 2026-10-30 |
| [0006](0006-przechowywanie-zalacznikow-s3.md) | Przechowywanie załączników: S3 z lokalnym katalogiem podręcznym | przyjęty | 2026-10-30 |
| [0007](0007-wersja-pythona-aplikacji.md) | Wersja Pythona aplikacji: 3.14 | przyjęty | 2026-10-30 |
| [0008](0008-menedzer-zaleznosci-uv.md) | Menedżer zależności Pythona: uv | przyjęty | 2026-10-30 |
| [0009](0009-lokalna-usluga-s3-moto.md) | Usługa zgodna z S3 lokalnie i w CI: moto | przyjęty | 2026-10-30 |
| [0010](0010-biblioteka-argon2.md) | Biblioteka do skrótów haseł: argon2-cffi | przyjęty | 2026-10-30 |
| [0011](0011-baza-danych-testow-postgresql.md) | Baza danych testów: PostgreSQL z compose | przyjęty | 2026-10-30 |
| [0012](0012-s3-w-testach-moto-w-procesie.md) | S3 w testach: moto w procesie (`mock_aws`) | przyjęty | 2026-10-30 |
| [0013](0013-klient-http-testow-httpx2.md) | Klient HTTP dla `TestClient`: httpx2 | przyjęty | 2026-10-30 |
| [0014](0014-linting-i-formatowanie-ruff.md) | Linting i formatowanie: ruff bez reguł bezpieczeństwa | przyjęty | 2026-10-30 |
| [0015](0015-region-aws-eu-central-1.md) | Region AWS: eu-central-1 (Frankfurt) | zastąpiony przez 0030 | 2026-10-30 |
| [0016](0016-uwierzytelnianie-do-aws.md) | Uwierzytelnianie do AWS: OIDC w potoku, użytkownicy IAM lokalnie | przyjęty; potok zastąpiony przez 0032 | 2026-10-30 |
| [0017](0017-plan-konta-aws-darmowy.md) | Plan konta AWS: darmowy | zastąpiony przez 0018 | 2026-10-30 |
| [0018](0018-istniejace-konto-aws-plan-platny.md) | Konto AWS: istniejące konto autora, plan płatny | zastąpiony przez 0020 | 2026-10-30 |
| [0019](0019-srodowisko-efemeryczne-aws.md) | Środowisko AWS efemeryczne: zasoby tylko w czasie pracy | przyjęty; mechanizm sprzątania w 0034 | 2026-10-30 |
| [0020](0020-nowe-konto-aws-plan-darmowy.md) | Konto AWS: nowe konto na planie darmowym | przyjęty | 2026-11-10 |
| [0021](0021-dostep-do-konsoli-owner.md) | Dostęp autora do konsoli AWS: Owner z MFA | przyjęty | 2026-11-10 |
| [0022](0022-obraz-kontenera-aplikacji.md) | Obraz kontenera aplikacji: python:3.14-slim bez pip, uv w etapie budowania, migracje poza obrazem | przyjęty | 2026-11-11 |
| [0023](0023-uruchamianie-stosu-docker-compose.md) | Uruchamianie aplikacji z zależnościami: Docker Compose z jednorazowymi usługami migrate i seed, `.env` w CI generowany przez workflow | przyjęty | 2026-11-11 |
| [0024](0024-architektura-aws-ec2-docker-compose.md) | Architektura w AWS: EC2 z Docker Compose, PostgreSQL w kontenerze, dostęp przez SSM | przyjęty; wdrożenie zastąpione przez 0032 | 2026-11-11 |
| [0025](0025-narzedzie-iac-terraform.md) | Narzędzie IaC: Terraform z przypiętymi wersjami | przyjęty | 2026-11-11 |
| [0026](0026-stan-terraform-i-warstwy.md) | Stan Terraformu w S3 i podział na warstwę stałą (`shared/`) i roboczą (`work/`) | przyjęty | 2026-11-11 |
| [0027](0027-rejestr-obrazow-ghcr.md) | Rejestr obrazów: GitHub Container Registry | przyjęty | 2026-11-11 |
| [0028](0028-system-instancji-ubuntu-przypiete-ami.md) | System instancji EC2: Ubuntu Server 24.04 LTS z przypiętym ID AMI | przyjęty | 2026-11-11 |
| [0029](0029-uprawnienia-uzytkownika-terraform.md) | Uprawnienia użytkownika IAM `terraform`: własna polityka w repozytorium | przyjęty | 2026-11-11 |
| [0030](0030-region-aws-eu-north-1.md) | Region AWS: eu-north-1 (Sztokholm), region przypisany kontu | przyjęty | 2026-11-11 |
| [0031](0031-konfiguracja-hosta-user-data.md) | Konfiguracja i utwardzenie instancji: skrypt user-data zamiast Ansible | przyjęty | 2026-11-11 |
| [0032](0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md) | Potok bez poświadczeń AWS: wdrożenie w modelu pull zamiast OIDC (SCP konta blokuje dostawców tożsamości) | przyjęty | 2026-11-11 |
| [0033](0033-mechanizm-wdrozenia-pull.md) | Mechanizm wdrożenia w modelu pull: ruchomy tag w GHCR i timer na instancji | przyjęty | 2026-11-13 |
| [0034](0034-automatyczne-sprzatanie-eventbridge-scheduler.md) | Automatyczne sprzątanie: EventBridge Scheduler usuwa instancję po 8 godzinach | przyjęty | 2026-11-13 |
