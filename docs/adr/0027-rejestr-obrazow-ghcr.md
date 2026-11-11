# 0027. Rejestr obrazów: GitHub Container Registry

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0004](0004-publiczne-repozytorium.md), [0016](0016-uwierzytelnianie-do-aws.md), [0022](0022-obraz-kontenera-aplikacji.md), [0024](0024-architektura-aws-ec2-docker-compose.md), zadania E05-04, E05-06, E05-07, E06, [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Potok buduje obraz aplikacji (ADR-0022), a instancja EC2 pobiera go po digeście i uruchamia przez compose (ADR-0024). Obraz musi leżeć w rejestrze dostępnym dla potoku (zapis) i dla instancji (odczyt). ADR-0024 odłożył wybór rejestru do E05-04.

## Czynniki decyzyjne

- uprawnienia roli AWS potoku (OIDC, E05-06),
- koszt na koncie z kredytami 100 USD,
- prostota: liczba zasobów i kroków logowania.

## Rozważane opcje

1. GitHub Container Registry (GHCR), pakiet publiczny
2. Amazon ECR, repozytorium prywatne

## Decyzja

Wybrano **GHCR z publicznym pakietem**. Powody autora:

- **Węższa rola OIDC:** potok wypycha obraz tokenem `GITHUB_TOKEN` z uprawnieniem `packages: write`, więc rola AWS potoku nie potrzebuje uprawnień do rejestru. Wystarczą jej uprawnienia do SSM Run Command (E05-06, E05-07).
- **Koszt:** GitHub Packages jest bezpłatny dla pakietów publicznych, a przechowywanie i transfer obrazów w Container registry są obecnie bezpłatne (GitHub Docs, sprawdzone 2026-11-11). ECR kosztuje 0,10 USD za GB miesięcznie (`docs/aws-konto.md`).
- **Prostota:** rejestr jest obok repozytorium, nie ma zasobu w Terraformie, a instancja pobiera publiczny obraz bez logowania.

## Konsekwencje

- (+) Terraform nie tworzy repozytorium ECR, a rola instancji nie potrzebuje uprawnień `ecr:*`.
- (+) Obraz jest publiczny jak repozytorium (ADR-0004). Recenzent może go pobrać po digeście.
- (−) Publiczne są też obrazy z celowo wprowadzonymi podatnościami (warianty z katalogu GT). To aplikacja badawcza bez sekretów w obrazie, ale trzeba to opisać w 5.3.
- (−) Wbudowanego skanu ECR nie ma. Skan obrazu robi Trivy w potoku (`docs/narzedzia.md`).
- (−) Instancja pobiera obraz z `ghcr.io` przez internet, a dostępność wdrożenia zależy od GitHuba. Bezpłatność Container registry jest opisana jako „obecna”, a GitHub zapowiada zmiany z miesięcznym wyprzedzeniem.
- Pakiet trzeba ustawić jako publiczny po pierwszym wypchnięciu (domyślna widoczność: TODO: zweryfikować w E06).

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- GitHub Docs, *GitHub Packages billing*: https://docs.github.com/en/billing/concepts/product-billing/github-packages (sprawdzone 2026-11-11)
