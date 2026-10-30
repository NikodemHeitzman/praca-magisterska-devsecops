# 0015. Region AWS: eu-central-1 (Frankfurt)

- **Status:** przyjęty
- **Data:** 2026-10-30
- **Decydujący:** autor pracy
- **Powiązane:** [0003](0003-dostawca-chmury-aws.md), zadanie E01-07, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-10-30](../log/2026-10-30.md)

## Kontekst

[ADR-0003](0003-dostawca-chmury-aws.md) wybrał AWS i zostawił region zadaniu E01-07. Region trzeba ustalić przed pierwszą infrastrukturą w Terraformie (E05), bo od niego zależą dostępność usług, ceny i miejsce przechowywania danych. Całe środowisko ma działać w jednym regionie: projekt ma jedno środowisko, bez stagingu (E03-05).

## Czynniki decyzyjne

- wygoda pracy autora i znajomość regionu,
- prostota wyboru,
- przechowywanie danych w UE,
- dostępność usług potrzebnych w E05 (sprawdzana dopiero w E05).

Wytyczne AWS nie wskazują jednego zalecanego regionu, tylko kryteria: zgodność z przepisami o danych, opóźnienie sieciowe (najlepiej zmierzone, nie zakładane z geografii), koszt i dostępność usług. Wymienia je blog AWS Architecture i AWS Well-Architected Framework (źródła niżej). W tym projekcie nie ma danych osobowych prawdziwych użytkowników, a jedynym użytkownikiem aplikacji jest autor, więc te kryteria mają małą wagę.

## Rozważane opcje

1. `eu-central-1` (Frankfurt)
2. `eu-west-1` (Irlandia)
3. `us-east-1` (N. Virginia)

## Decyzja

Wybrano **`eu-central-1`**. Powody autora:

- autor dobrze się czuje w tym regionie,
- prościej wybrać `eu-central-1` niż analizować położenie geograficzne i opóźnienia do kilku regionów europejskich,
- dane zostają w UE,
- według autora to region polecany przez AWS. <!-- TODO: zweryfikować; nie znaleziono źródła AWS, które poleca konkretny region (wytyczne AWS podają kryteria, nie region) -->

Pierwsze dwa powody są subiektywne. W projekcie jednoosobowym bez wymogów co do lokalizacji danych i opóźnień wybór regionu ma mały wpływ na wyniki eksperymentu.

`us-east-1` odpadł, bo autor nie chce wdrażać do regionu w USA, choć wiele nowości AWS trafia do niego najpierw.

`eu-west-1` rozważano po sprawdzeniu, który region europejski dostaje nowości pierwszy. AWS nie publikuje takiej kolejności. W przykładowych ogłoszeniach z 2026 r. (CloudWatch Query Studio, Bedrock AgentCore Evaluations) na liście regionów startowych była Irlandia, a nie Frankfurt. Projekt nie korzysta z nowych usług, więc ten czynnik nie przeważył.

Pierwotne powody autora („najpopularniejszy region w Europie”, „najmniej awarii”, „najszybciej dostaje zmiany”, „lepsze wsparcie”) wycofano 2026-10-30, bo nie znaleziono dla nich źródeł. Sprawdzenie pokazało, że nowości dostaje wcześniej Irlandia, a poziom wsparcia zależy od planu wsparcia AWS, nie od regionu (TODO: zweryfikować w dokumentacji AWS Support). Drugie podejście („najbliższy region dla Polski”) też wycofano, bo Sztokholm (`eu-north-1`) leży od Warszawy podobnie daleko, a odległości nie mierzono.

## Konsekwencje

- (+) Jeden region dla całej infrastruktury: `region = "eu-central-1"` w providerze Terraformu i `aws-region` w akcji `configure-aws-credentials`.
- (−) Dostępność usług wybranych w E05 (np. do uruchamiania kontenerów) w `eu-central-1` i na planie darmowym ([0017](0017-plan-konta-aws-darmowy.md)) trzeba sprawdzić przed ADR-em architektury.
- (−) Region wybrano bez analizy według kryteriów AWS (bez pomiaru opóźnień i porównania cen). To materiał do 5.3 (ograniczenia). Wpływ na wyniki: wątpliwy, bo eksperyment mierzy skanery i czas potoku w GitHub Actions, a nie działanie aplikacji w regionie (TODO: zweryfikować przy E09, czy czas kroku wdrożenia zależy od regionu).
- Usługi globalne (IAM, Budgets) nie zależą od regionu.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować), sprawdzone 2026-10-30:

- AWS, *Document history for AWS Regions and Availability Zones*, https://docs.aws.amazon.com/global-infrastructure/latest/regions/doc-history.html (daty uruchomienia regionów: `eu-west-1` 2008, `eu-central-1` 2014).
- AWS, *AWS Observability ICYMI: Jan–May 2026*, https://aws.amazon.com/blogs/mt/aws-observability-icymi-jan-may-2026/ (regiony startowe CloudWatch Query Studio).
- AWS What's New, *Amazon Bedrock AgentCore Evaluations is now generally available* (2026-03), https://aws.amazon.com/about-aws/whats-new/2026/03/agentcore-evaluations-generally-available/.
- AWS Architecture Blog, *What to Consider when Selecting a Region for your Workloads*, https://aws.amazon.com/blogs/architecture/what-to-consider-when-selecting-a-region-for-your-workloads/ (kryteria: zgodność, opóźnienie, koszt, usługi).
- AWS Well-Architected Framework, *COST07-BP02 Choose Regions based on cost*, https://docs.aws.amazon.com/wellarchitected/latest/framework/cost_pricing_model_region_cost.html.
- aws-services.info, *AWS Services and Regions*, https://www.aws-services.info/regions.html (nieoficjalny licznik usług w regionach: 347 w `eu-west-1`, 341 w `eu-central-1`).
