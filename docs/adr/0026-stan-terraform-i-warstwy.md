# 0026. Stan Terraformu w S3 i podział na warstwę stałą i roboczą

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0006](0006-przechowywanie-zalacznikow-s3.md), [0019](0019-srodowisko-efemeryczne-aws.md), [0024](0024-architektura-aws-ec2-docker-compose.md), [0025](0025-narzedzie-iac-terraform.md), zadania E05-04, E05-06, E05-08, E08-01, [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Terraform zapisuje stan zasobów w pliku stanu. Katalog zadań wymaga stanu zdalnego w S3, szyfrowanego i wersjonowanego, z natywną blokadą S3. Kubełek na stan trzeba jednak najpierw utworzyć, a Terraform potrzebuje do tego stanu. ADR-0019 dzieli zasoby na warstwę roboczą, usuwaną po każdej sesji, i warstwę stałą (stan, OIDC, CloudTrail, rejestr), która zostaje do E15-08. Potrzebny jest sposób, w jaki kod odwzorowuje ten podział, tak żeby `terraform destroy` warstwy roboczej nie usunął stanu ani roli potoku.

## Czynniki decyzyjne

- wszystkie zasoby opisane kodem i skanowane,
- bezpieczeństwo `destroy`: usunięcie warstwy roboczej nie może dotknąć warstwy stałej,
- prostota: liczba katalogów i plików stanu,
- koszt zasobów trwających między sesjami.

## Rozważane opcje

Utworzenie kubełka stanu (bootstrap):

1. katalog Terraformu ze stanem lokalnym, który tworzy kubełek, a potem przenosi własny stan do tego kubełka (`terraform init -migrate-state`)
2. kubełek tworzony ręcznie poleceniami AWS CLI
3. stan w HCP Terraform zamiast S3

Podział na warstwy:

1. osobne katalogi główne z osobnymi plikami stanu
2. jeden katalog, warstwa robocza usuwana przez `terraform destroy -target=…`
3. jeden kod z osobnymi workspace'ami

Układ katalogów i miejsce kubełka na załączniki (ADR-0006):

1. `shared/` (warstwa stała i zarazem bootstrap) i `work/` (warstwa robocza), kubełek załączników w `work/`
2. `bootstrap/` (tylko kubełek stanu), `shared/` i `work/`
3. jak opcja 1, ale kubełek załączników w `shared/`

## Decyzja

Wybrano **dwa katalogi główne z osobnymi stanami: `infra/terraform/shared/` i `infra/terraform/work/`.** `shared/` tworzy kubełek stanu i przechowuje w nim także własny stan. `work/` zawiera sieć, instancję, rolę instancji i kubełek załączników. Powody autora:

- **Bootstrap w Terraformie zamiast CLI albo HCP Terraform:** wszystko jako kod. Ustawienia kubełka stanu (szyfrowanie, wersjonowanie, blokada publicznego dostępu) są opisane i skanowane tak jak reszta infrastruktury.
- **Osobne katalogi i stany zamiast `-target` albo workspace'ów:** bezpieczny `destroy`. `terraform destroy` w `work/` nie widzi zasobów warstwy stałej, więc nie może ich usunąć.
- **`shared/` + `work/` z załącznikami w `work/`:**
  - mniej katalogów: dwa stany zamiast trzech, a bootstrap to po prostu warstwa stała,
  - koszt: między sesjami nic nie leży w kubełku załączników.

Ustawienia stanu (rekomendacja agenta przyjęta przez autora razem z opcjami):

- backend `s3` w regionie `eu-north-1` ([ADR-0030](0030-region-aws-eu-north-1.md)), klucze `shared/terraform.tfstate` i `work/terraform.tfstate` w jednym kubełku,
- blokada stanu przez plik blokady w S3 (`use_lockfile = true`), bez tabeli DynamoDB. Blokadę w DynamoDB dokumentacja backendu `s3` oznacza jako przestarzałą. `use_lockfile` pojawił się eksperymentalnie w Terraform 1.10 i przestał być eksperymentalny w 1.11 (przewodniki aktualizacji 1.10 i 1.11),
- kubełek stanu: wersjonowanie, domyślne szyfrowanie SSE-S3, blokada publicznego dostępu, `prevent_destroy` w cyklu życia zasobu,
- nazwa kubełka ze stałym losowym przyrostkiem zapisanym w kodzie (nazwy kubełków są globalne). ID konta nie trafia do repozytorium (`docs/aws-konto.md`).

## Konsekwencje

- (+) `destroy` warstwy roboczej jest bezpieczny dla stanu, przyszłej roli OIDC (E05-06) i CloudTrail (E08-01), które trafią do `shared/`.
- (+) Pliki stanu są wersjonowane, więc uszkodzony stan można przywrócić z poprzedniej wersji obiektu.
- (−) Pierwsze uruchomienie wymaga dwóch kroków w `shared/`: `apply` ze stanem lokalnym, potem włączenie backendu i `terraform init -migrate-state`. Opis w `infra/terraform/README.md`.
- (−) `work/` potrzebuje wartości z `shared/` (np. nazwy kubełka stanu) przez zmienne albo `terraform_remote_state`. Na razie zależność ogranicza się do backendu.
- (−) Ktoś, kto chce odtworzyć infrastrukturę na własnym koncie, musi zmienić nazwę kubełka stanu w kodzie (globalna przestrzeń nazw S3).
- (−) Dane z kubełka załączników znikają przy `destroy` (`force_destroy`), tak jak dane bazy (ADR-0024).
- Uwaga do GT-11 (`docs/app-spec.md`): od 2023-01-05 S3 szyfruje każdy nowy obiekt SSE-S3 i szyfrowania nowych obiektów nie da się wyłączyć (AWS, *Default encryption FAQ*). Wariant podatny GT-11 dla kubełka S3 nie jest więc możliwy w AWS. Pozostaje nieszyfrowany wolumen EBS, który katalog już dopuszcza. Wybór należy do autora.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- HashiCorp, *Backend Type: s3*: https://developer.hashicorp.com/terraform/language/backend/s3 (sprawdzone 2026-11-11)
- HashiCorp, *Upgrading to Terraform v1.10* i *Upgrading to Terraform v1.11*: https://developer.hashicorp.com/terraform/language/v1.10.x/upgrade-guides, https://developer.hashicorp.com/terraform/language/v1.11.x/upgrade-guides
- AWS, *Default encryption FAQ*: https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html (sprawdzone 2026-11-11)
