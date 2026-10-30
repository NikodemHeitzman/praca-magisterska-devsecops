# 0016. Uwierzytelnianie do AWS: OIDC w potoku, użytkownicy IAM lokalnie

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0003](0003-dostawca-chmury-aws.md), [0004](0004-publiczne-repozytorium.md), zadania E01-07, E05, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

Do konta AWS potrzebują dostępu trzy strony: autor w konsoli, autor uruchamiający Terraform u siebie i potok GitHub Actions, który wdraża aplikację. Repozytorium jest publiczne ([0004](0004-publiczne-repozytorium.md)), a `AGENTS.md` (zasada 4) wymaga uwierzytelniania do AWS przez OIDC, bez długoterminowych kluczy. Temat pracy to bezpieczeństwo łańcucha dostaw w potoku według NIST SP 800-204D, więc sposób uwierzytelniania potoku sam podlega ocenie.

## Czynniki decyzyjne

- liczba osób z dostępem (jedna: autor),
- prostota konfiguracji w projekcie jednoosobowym,
- brak długoterminowych kluczy w potoku i w repozytorium (zasada 4 `AGENTS.md`, [0004](0004-publiczne-repozytorium.md)),
- doświadczenie autora z dotychczasowych projektów.

## Rozważane opcje

Dostęp autora:

1. użytkownik IAM z MFA (konsola) i osobny użytkownik IAM `terraform` z kluczem dostępu (lokalnie),
2. IAM Identity Center (SSO) z krótkotrwałymi poświadczeniami w CLI,
3. AWS Organizations z osobnymi kontami.

Dostęp potoku:

1. OIDC: rola IAM przyjmowana przez GitHub Actions, zaufanie ograniczone do repozytorium,
2. klucz dostępu użytkownika IAM w GitHub Secrets.

## Decyzja

Wybrano **użytkowników IAM lokalnie i OIDC w potoku**:

- **Root** z MFA, bez kluczy dostępu, tylko do czynności awaryjnych.
- **Użytkownik IAM administratora** (autor) z MFA do pracy w konsoli. Powód autora: projekt jest mały i autor jest jedyną osobą, która potrzebuje poświadczeń. Dlatego bez IAM Identity Center i bez AWS Organizations.
- **Użytkownik IAM `terraform`** z kluczem dostępu zapisanym tylko na komputerze autora, do lokalnego uruchamiania Terraformu. Powód autora: tak pracował w dotychczasowych projektach i to działało.
- **Potok przez OIDC.** Rola IAM z polityką zaufania ograniczoną do repozytorium `NikodemHeitzman/praca-magisterska-devsecops` (dokładny warunek `sub` ustala E05). Autor przyjął rekomendację agenta zamiast klucza w GitHub Secrets, którego używał dotąd.

Odrzucona opcja „klucz w GitHub Secrets” wymagałaby zmiany zasady 4 `AGENTS.md` i [0004](0004-publiczne-repozytorium.md). Długoterminowy klucz w potoku byłby też słabością w ocenie zgodności potoku z NIST SP 800-204D.

### Świadome odstępstwo

Klucz użytkownika `terraform` jest długoterminowy, więc to odstępstwo od zasady „bez długoterminowych kluczy”. Obejmuje tylko komputer autora. Klucz nie trafia do repozytorium ani do GitHub Secrets. Zabezpieczenia proponowane przez agenta (przyjęte przez autora bez osobnego powodu):

- klucz w `~/.aws/credentials` w profilu nazwanym, nie w zmiennych środowiskowych zapisanych w plikach projektu,
- usunięcie klucza i użytkownika przy sprzątaniu AWS (E15-08),
- uprawnienia użytkownika `terraform` ustala E05. Do tego czasu TODO: zweryfikować, czy wystarczy coś węższego niż `AdministratorAccess`.

## Konsekwencje

- (+) Potok nie ma długoterminowych poświadczeń AWS. Poświadczenia z OIDC wygasają po zakończeniu jobu (TODO: zweryfikować domyślny czas sesji roli).
- (+) Prosta konfiguracja dla jednej osoby, znana autorowi.
- (−) Klucz `terraform` na dysku nie wymaga MFA. Jego wyciek z komputera autora daje dostęp do konta. Ryzyko opisać w 5.3 (ograniczenia).
- (−) Dostawcę OIDC i rolę potoku tworzy lokalny Terraform (użytkownik `terraform`), więc przed pierwszym wdrożeniem z potoku jest krok ręczny (*bootstrap*) w E05.
- Potok używa akcji `aws-actions/configure-aws-credentials` przypiętej do SHA ([`docs/narzedzia.md`](../narzedzia.md)) z uprawnieniem `id-token: write`.

## Źródła

- `docs/narzedzia.md`, sekcja 3: GitHub, *OpenID Connect in Amazon Web Services*; AWS, *Create an OpenID Connect (OIDC) identity provider in IAM*.
- Wymóg ochrony poświadczeń potoku w NIST SP 800-204D: TODO: zweryfikować numer rekomendacji w `docs/notes/nist-800-204d.md` [@NIST-SP800-204D].
