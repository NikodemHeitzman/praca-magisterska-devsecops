# 0032. Potok bez poświadczeń AWS: wdrożenie w modelu pull zamiast OIDC

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** zastępuje część „potok przez OIDC” w [0016](0016-uwierzytelnianie-do-aws.md) i mechanizm wdrożenia z potoku przez SSM Run Command w [0024](0024-architektura-aws-ec2-docker-compose.md); [0004](0004-publiczne-repozytorium.md), [0019](0019-srodowisko-efemeryczne-aws.md), [0020](0020-nowe-konto-aws-plan-darmowy.md), [0026](0026-stan-terraform-i-warstwy.md), [0027](0027-rejestr-obrazow-ghcr.md), [0029](0029-uprawnienia-uzytkownika-terraform.md), [0030](0030-region-aws-eu-north-1.md), zadania E05-06, E05-07, E05-08, E08-01, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

ADR-0016 przyjął, że potok GitHub Actions uwierzytelnia się do AWS przez OIDC: dostawca tożsamości OIDC w IAM i rola z polityką zaufania ograniczoną do repozytorium. W E05-06 przygotowano w warstwie stałej (`shared/`) dostawcę `token.actions.githubusercontent.com` i rolę `devsecops-thesis-github-actions`. `terraform plan` przeszedł (2 zasoby do dodania), ale `terraform apply` (2026-11-11) skończył się błędem:

- `AccessDenied` dla `iam:CreateOpenIDConnectProvider` „with an explicit deny in a service control policy”. Komunikat wskazuje SCP organizacji zarządzanej przez AWS, do której należy konto-projekt z ADR-0020 (to samo źródło ograniczeń co `RegionFloor` w ADR-0030).
- Dokumentacja AWS publikuje SCP planu darmowego i planu płatnego dla kont-projektów. Obie mają instrukcję `DenyIAMRestrictedActions`, która odrzuca m.in. `iam:*Provider*`, czyli tworzenie dostawców tożsamości OIDC i SAML. Według tej samej dokumentacji ograniczenia znosi tylko aktywacja zaawansowanych funkcji („activate advanced features”). Jak ustalono w ADR-0030, wymaga ona planu płatnego, usuwa limit wydatków i jest nieodwracalna.
- Która instrukcja SCP odrzuciła żądanie, wynika z porównania z opublikowaną treścią SCP, a nie ze zdekodowanego komunikatu (TODO: zweryfikować przez `GetRequestAuthorizationDetails` z identyfikatorem autoryzacji z komunikatu błędu).

W AWS nic nie powstało: rola zależy od ARN dostawcy, więc Terraform jej nie tworzył. Bez dostawcy OIDC GitHub Actions nie może przyjąć roli w tym koncie.

## Czynniki decyzyjne

- brak poświadczeń AWS w potoku i w GitHub Secrets (zasada 4 `AGENTS.md`, [0004](0004-publiczne-repozytorium.md)),
- pozostanie na planie darmowym z limitem wydatków ([0020](0020-nowe-konto-aws-plan-darmowy.md)),
- odwracalność decyzji,
- najmniejsze uprawnienia w AWS,
- praca ręczna w każdej sesji.

## Rozważane opcje

1. **Model pull:** potok nie ma żadnych poświadczeń AWS. Publikuje obraz w GHCR i informację, który digest wdrożyć, a instancja sama ją sprawdza i uruchamia stos swoją rolą instancji.
2. **Aktywacja zaawansowanych funkcji** i OIDC według pierwotnego planu (kod był gotowy).
3. **Krótkotrwałe poświadczenia STS na sesję:** autor na początku sesji generuje lokalnie tymczasowe poświadczenia, wpisuje je do GitHub Secrets i usuwa na końcu sesji.
4. **Długoterminowy klucz użytkownika IAM w GitHub Secrets**, odrzucony już w [0016](0016-uwierzytelnianie-do-aws.md).

## Decyzja

Wybrano **model pull: potok bez poświadczeń AWS**. Powody autora:

- **zero poświadczeń w CI:** przejęcie potoku albo repozytorium nie daje dostępu do konta AWS, bo na runnerze nie ma czego wykraść,
- **mniej uprawnień w AWS:** rola instancji już istnieje (E05-04), więc nie trzeba roli potoku ani uprawnień do SSM Run Command.

Dlaczego nie opcja 2. Powody autora:

- aktywacja jest nieodwracalna,
- ryzyko kosztów: plan płatny nie ma limitu wydatków, więc po wyczerpaniu kredytów konto nalicza opłaty, zamiast się zamknąć,
- spójność z [0030](0030-region-aws-eu-north-1.md), gdzie tę samą opcję odrzucono przy wyborze regionu.

Dlaczego nie opcja 3. Powody autora:

- ręczny krok w każdej sesji (wygenerowanie i usunięcie sekretów),
- klucze w GitHub Secrets, nawet tymczasowe, są sprzeczne z zasadą 4 i z kryterium zadania E05-06.

Szczegóły mechanizmu (skąd instancja wie, który digest wdrożyć, jak często sprawdza, jak wygląda rollback i jak potok dowiaduje się o wyniku) ustala E05-07 w osobnym ADR. Przygotowany kod OIDC usunięto z repozytorium (decyzja autora). Jego istotę opisuje sekcja niżej, żeby dało się go odtworzyć na koncie bez tej SCP.

### Ustalenia z przygotowania OIDC (nie wdrożone)

Decyzje autora z wywiadu przed blokadą. Obowiązywałyby, gdyby OIDC wróciło:

- **Warunek `sub` tylko na gałąź `main`**, a nie na środowisko GitHub ani na oba naraz. Powody autora: całe ograniczenie jest w kodzie, prostota, kryterium „repozytorium i gałąź” spełnione dosłownie. Uwaga agenta: protokół v1 (sekcja 6, punkt 4) przewidywał wdrożenia z gałęzi `exp/variant-*`, czego w wywiadzie nie uwzględniono.
- **Jedna rola dla wariantów A i B.** Powody autora: oba warianty wdrażają tak samo, mniej kodu, domyślny `sub` i tak nie rozróżnia workflowów.
- **Rola bez polityk uprawnień w E05-06**, a uprawnienia dopisuje zadanie wdrożenia. Powody autora: nic na zapas, zakres wynika z decyzji w E05-07.
- **Bez granicy uprawnień (permissions boundary) dla użytkownika `terraform`.** Ryzyko eskalacji opisuje 5.3. Powody autora: klucz `terraform` jest tylko lokalnie, a ryzyko szczątkowe to materiał do 5.3. Ta decyzja obowiązuje niezależnie od OIDC.
- **Workflow testowy usuwany po teście.** Powody autora: czyste dane eksperymentu (skanery E07 nie widzą pliku spoza porównywanych potoków), dowód zostaje w historii git.

Fakty sprawdzone 2026-11-11:

- **To repozytorium używa niezmiennego `sub`** z ID właściciela i repozytorium (API GitHub `repos/.../actions/oidc/customization/sub`: `use_immutable_subject: true`). Warunek miałby postać `repo:NikodemHeitzman@238629673/praca-magisterska-devsecops@1400349662:ref:refs/heads/main`. Warunek w postaci z przykładów AWS i GitHub (`repo:WŁAŚCICIEL/REPO:ref:...`) nie zadziałałby. Repozytorium utworzone na nowo pod tą samą nazwą dostaje inne ID, więc nie przejmie roli. Według dokumentacji GitHub niezmienny `sub` dotyczy repozytoriów utworzonych po 2026-07-15 (to repozytorium: 2026-10-01).
- **IAM odrzuca politykę zaufania do GitHub bez warunku `token.actions.githubusercontent.com:sub`** albo z samą gwiazdką.
- **Odcisk certyfikatu (thumbprint) nie jest potrzebny:** dla GitHub AWS weryfikuje certyfikat biblioteką zaufanych urzędów certyfikacji. W providerze `hashicorp/aws` 6.72.0 `thumbprint_list` jest opcjonalne.
- **Sesja roli z `aws-actions/configure-aws-credentials` trwa domyślnie godzinę.** To zamyka TODO z ADR-0016.
- Podgląd polityki zaufania (bez ID konta):

```json
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::<KONTO>:oidc-provider/token.actions.githubusercontent.com" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:NikodemHeitzman@238629673/praca-magisterska-devsecops@1400349662:ref:refs/heads/main"
    }
  }
}
```

## Konsekwencje

- (+) Na runnerze GitHub Actions nie ma poświadczeń AWS, ani długoterminowych, ani krótkotrwałych. W GitHub Secrets nie ma kluczy AWS (`gh secret list`: pusto, 2026-11-11).
- (+) W AWS nie ma roli potoku ani dostawcy tożsamości, czyli o jedną ścieżkę dostępu do konta mniej. Polityka użytkownika `terraform` nie dostaje uprawnień `iam:*OpenIDConnectProvider*`.
- (−) **Integralność wdrożenia przechodzi na łańcuch dostaw obrazu.** Kto może opublikować digest na `main`, ten wdraża kod na instancję. Ochroną są gałąź `main`, przypięcie po digeście i ewentualna weryfikacja podpisu obrazu na instancji (do rozważenia w E05-07 i E07). To materiał do 2.3 i 5.3.
- (−) **Potok nie widzi wyniku wdrożenia.** Bez poświadczeń AWS nie znajdzie instancji ani nie sprawdzi jej stanu. Sposób potwierdzania wdrożenia ustala E05-07.
- (−) Kryteria E05-06 z katalogu („workflow uzyskuje tymczasowe poświadczenia”, „trust policy ogranicza repo i gałąź”) są niewykonalne na tym koncie. Spełnione jest tylko „brak `AWS_ACCESS_KEY_ID` w sekretach”. Zmianę zakresu potwierdza autor przy zamknięciu zadania.
- (−) ADR-0024 zakładał wdrożenie z potoku przez SSM Run Command na instancję znalezioną po tagach. W modelu pull instancja sama pobiera bieżący digest, także przy pierwszym starcie. Grupa bezpieczeństwa już pozwala na ruch wychodzący 443 (GitHub, GHCR).
- (−) E05-08: odpada opcja z ADR-0019 „zaplanowany workflow GitHub Actions z `terraform destroy` przez OIDC”. Zostają mechanizmy wewnątrz konta (np. EventBridge Scheduler) albo sprzątanie lokalne.
- (−) E08-01: w CloudTrail nie będzie zdarzeń `AssumeRoleWithWebIdentity` z potoku. Ślad wdrożeń przenosi się na instancję i do historii GitHub.
- (−) **Zmiana względem zamrożonego protokołu v1** (`experiment/PROTOCOL.md`), zapisana w dzienniku 2026-11-11 zgodnie z jego nagłówkiem:
  - 5.1, K8: zmienna kontrolowana „rola OIDC” nie istnieje. Oba warianty mają jednakowo brak poświadczeń AWS w potoku, więc K8 pozostaje spełniona (to samo repozytorium, te same ustawienia i ochrona gałęzi).
  - 6, punkt 4: zabezpieczenie „rola AWS (OIDC) pozwala wdrażać tylko z gałęzi `exp/variant-*`, nie z pull requestów” zastępuje reguła modelu pull: instancja wdraża tylko digest opublikowany z wybranej gałęzi. Pull requesty niczego nie publikują. Którą gałąź (`main` czy `exp/variant-*`) bierze instancja, ustala E05-07.
- Materiał do 2.3, 5.3 i rekomendacji dla małych zespołów: nowy typ konta AWS blokuje federację OIDC, którą dokumentacja AWS i GitHub zaleca jako sposób uwierzytelniania potoku. Mały zespół na koncie-projekcie musi wybrać model pull, klucze w sekretach albo nieodwracalne przejście na plan płatny.
- Lekcja procesowa (jak w ADR-0030): ADR-0016 przyjęto przed sprawdzeniem SCP nowego typu konta. Ograniczenia SCP kont-projektów warto sprawdzić w dokumentacji przed każdą decyzją, która dotyczy IAM.
- Aktualizacja: `AGENTS.md` (zasada 4), `docs/aws-konto.md`, `docs/narzedzia.md`, README Terraformu, komentarz w `shared/versions.tf`, status ADR-0016 i ADR-0024.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- AWS, *Managed policies for your organization* (SCP i RCP kont-projektów, instrukcja `DenyIAMRestrictedActions`): https://docs.aws.amazon.com/accounts/latest/reference/scps-and-rcps-for-projects.html (sprawdzone 2026-11-11)
- AWS, *Supported AWS services for Sign up for AWS (new)*: https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html (sprawdzone 2026-11-11)
- AWS, *Create an OpenID Connect (OIDC) identity provider in IAM*: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html (sprawdzone 2026-11-11)
- AWS, *Create a role for OpenID Connect federation*, sekcja o GitHub: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html (sprawdzone 2026-11-11)
- GitHub Docs, *OpenID Connect in Amazon Web Services*: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws (sprawdzone 2026-11-11)
- GitHub Docs, *OpenID Connect reference* (format `sub`, niezmienne ID): https://docs.github.com/en/actions/reference/security/oidc (sprawdzone 2026-11-11)
- GitHub Changelog, *Immutable subject claims for GitHub Actions OIDC tokens* (2026-04-23, wpis później zmieniany): https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens
- `aws-actions/configure-aws-credentials` v6.3.0, `action.yml` (domyślny czas sesji, maskowanie ID konta)
- Ochrona poświadczeń potoku w NIST SP 800-204D: TODO: zweryfikować numer rekomendacji [@NIST-SP800-204D]
