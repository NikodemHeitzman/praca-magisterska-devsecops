# 0025. Narzędzie IaC: Terraform z przypiętymi wersjami

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0003](0003-dostawca-chmury-aws.md), [0016](0016-uwierzytelnianie-do-aws.md), [0024](0024-architektura-aws-ec2-docker-compose.md), [0026](0026-stan-terraform-i-warstwy.md), zadania E05-04, E07 (skan IaC), [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Infrastrukturę z ADR-0024 (VPC, podsieć, grupa bezpieczeństwa, EC2, rola instancji, kubełek S3) trzeba tworzyć i usuwać kodem w każdej sesji pracy (ADR-0019). Katalog zadań, `README.md` i lista narzędzi (`hashicorp/setup-terraform`, Checkov dla GT-10 i GT-11 w `docs/narzedzia.md`) zakładały Terraform, ale wybór narzędzia nie miał dotąd ADR-u. Recenzent może zapytać, czemu Terraform, a nie inne narzędzie IaC.

## Czynniki decyzyjne

- znajomość narzędzia przez autora,
- obsługa przez skanery IaC z potoku (Checkov, Trivy),
- odtwarzalność: przypięte wersje narzędzia i providera,
- licencja.

## Rozważane opcje

1. Terraform (HashiCorp)
2. OpenTofu (otwarty fork Terraformu)
3. AWS CloudFormation albo AWS CDK

## Decyzja

Wybrano **Terraform**. Powód autora: zna go i używał go wcześniej.

Wersje (zasada 6 `AGENTS.md`), najnowsze w dniu decyzji:

- Terraform `1.17.1` (HashiCorp Checkpoint API, sprawdzone 2026-11-11), w `required_version` jako dokładna wersja,
- provider `hashicorp/aws` `6.72.0` (Terraform Registry, sprawdzone 2026-11-11), w `required_providers` jako dokładna wersja, z plikiem `.terraform.lock.hcl` w repozytorium (sumy kontrolne providera).

Pozostałe opcje autor odrzucił bez osobnego powodu. Agent odnotowuje różnice, które nie były powodem decyzji:

- OpenTofu ma licencję MPL-2.0 i niemal tę samą składnię. Terraform od 2023 r. ma licencję Business Source License (TODO: zweryfikować datę i warunki w źródle HashiCorp). Dla pracy magisterskiej licencja BSL nie ogranicza użycia (TODO: zweryfikować).
- CloudFormation trzyma stan po stronie AWS, więc nie potrzebuje kubełka stanu, ale wiąże kod z jednym dostawcą.

## Konsekwencje

- (+) Ten sam język i narzędzie w lokalnej pracy autora i w potoku (`hashicorp/setup-terraform` przypięta do SHA w `docs/narzedzia.md`).
- (+) Checkov i Trivy skanują pliki `.tf`, więc GT-10 i GT-11 pozostają mierzalne.
- (−) Stan Terraformu trzeba przechowywać i chronić samemu (ADR-0026).
- (−) Dokładne przypięcie wersji wymaga świadomej aktualizacji (zmiana `required_version`, `terraform init -upgrade`, commit pliku blokady).
- Licencja Terraformu (BSL) to uwaga do 5.3 albo do opisu narzędzi w 4.x.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- HashiCorp Checkpoint API, `https://checkpoint-api.hashicorp.com/v1/check/terraform` (aktualna wersja 1.17.1, sprawdzone 2026-11-11)
- Terraform Registry, `https://registry.terraform.io/v1/providers/hashicorp/aws/versions` (najnowsza 6.72.0, sprawdzone 2026-11-11)
- [@Brikman2022]: *Terraform: Up & Running* (rdzeń literatury), tło dla wyboru narzędzia; nie był powodem decyzji autora.
