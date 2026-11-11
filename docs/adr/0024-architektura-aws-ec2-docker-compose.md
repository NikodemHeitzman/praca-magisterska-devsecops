# 0024. Architektura w AWS: EC2 z Docker Compose, PostgreSQL w kontenerze, dostęp przez SSM

- **Status:** przyjęty; region zmieniony przez [0030](0030-region-aws-eu-north-1.md) (ceny `eu-north-1` w ADR-0030)
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0003](0003-dostawca-chmury-aws.md), [0005](0005-baza-danych-postgresql.md), [0006](0006-przechowywanie-zalacznikow-s3.md), [0015](0015-region-aws-eu-central-1.md), [0016](0016-uwierzytelnianie-do-aws.md), [0019](0019-srodowisko-efemeryczne-aws.md), [0020](0020-nowe-konto-aws-plan-darmowy.md), [0023](0023-uruchamianie-stosu-docker-compose.md), zadania E05-03, E05-04, E05-05, E05-07, E05-08, E06-03, [`docs/aws-konto.md`](../aws-konto.md), [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Aplikacja działa w kontenerach: aplikacja (ADR-0022) i PostgreSQL (ADR-0005), a lokalnie i w CI dodatkowo moto jako atrapa S3 (ADR-0009). Stos uruchamia jeden plik Docker Compose z jednorazowymi usługami `migrate` i `seed` (ADR-0023). Potrzebny jest sposób uruchomienia tego stosu w AWS, w regionie `eu-central-1` (ADR-0015), na koncie z planem darmowym i kredytami 100 USD (ADR-0020), w środowisku tworzonym i usuwanym w każdej sesji pracy (ADR-0019).

Ten ADR rozstrzyga też sprawy odłożone wcześniej:

- PostgreSQL w AWS jako kontener czy RDS (ADR-0005),
- wdrożenie z `main`, gdy infrastruktura jest usunięta (ADR-0019),
- czy compose z usługą `seed` posłuży do wdrożenia w AWS (ADR-0023).

## Czynniki decyzyjne

- koszt przy pracy 24/7 i w trybie efemerycznym, przy kredytach 100 USD,
- dostępność usługi dla nowego konta na planie darmowym,
- zgodność środowiska lokalnego, CI i AWS (kontrola zmiennych w eksperymencie),
- prostota konfiguracji w Terraformie i opisu w pracy,
- bezpieczeństwo: otwarte porty, klucze, uprawnienia potoku, audytowalność,
- czas tworzenia i usuwania środowiska.

## Rozważane opcje

Platforma uruchomieniowa:

1. EC2 (jedna instancja) z Docker Compose
2. ECS na Fargate z publicznym adresem zadania, bez load balancera, baza w RDS
3. ECS Express Mode (Fargate z Application Load Balancer), baza w RDS
4. AWS App Runner, baza w RDS

PostgreSQL w AWS:

1. kontener na tej samej instancji EC2
2. Amazon RDS `db.t4g.micro`

Dostęp administracyjny do instancji:

1. tylko AWS Systems Manager (Session Manager, Run Command), port 22 zamknięty
2. SSH z dostępem ograniczonym do adresu autora
3. SSM jako podstawa i SSH awaryjnie

Typ instancji (wszystkie na liście typów dostępnych na planie darmowym):

1. `t3.small` (2 vCPU, 2 GiB, x86)
2. `t4g.small` (2 vCPU, 2 GiB, ARM)
3. `t3.micro` (2 vCPU, 1 GiB, x86)

Sieć:

1. własne VPC z podsiecią publiczną, publiczny IPv4, bez bramy NAT
2. podsieć prywatna z ALB i punktami końcowymi VPC dla SSM
3. domyślne VPC

Wdrożenie po merge'u do `main`:

1. tylko przy postawionym środowisku: job szuka instancji, a gdy jej nie ma, pomija wdrożenie
2. potok sam stawia warstwę roboczą (`terraform apply`) i wdraża
3. tylko ręcznie (`workflow_dispatch`)

Dane startowe w AWS:

1. ten sam compose z usługami `migrate` i `seed`
2. w AWS tylko migracje, konta tworzone inaczej

Protokół:

1. tylko HTTP (port 80), brak HTTPS opisany jako ograniczenie
2. własna domena i certyfikat Let's Encrypt za reverse proxy
3. certyfikat self-signed

### Porównanie kosztu

Ceny `eu-central-1` z AWS Price List API, bez VAT, sprawdzone 2026-11-11 (wersje cenników: AmazonEC2 `20261110173852`, AmazonECS `20261019224317`, AWSAppRunner `20260911124525`, AmazonRDS `20261029070635`, AmazonVPC `20261105181945`). Założenia:

- 730 h to praca 24/7, a 100 h to miesiąc w trybie efemerycznym (ADR-0019),
- EBS i pamięć RDS po 20 GB,
- zadanie Fargate i usługa App Runner mają 0,5 vCPU i 1 GB,
- jeden publiczny IPv4 na instancję albo zadanie, a ALB w dwóch strefach dostępności ma dwa adresy.

Kwoty nie obejmują warstwy stałej (ECR, S3, CloudWatch, CloudTrail; około 1 USD miesięcznie według `docs/aws-konto.md`), transferu danych ani jednostek LCU load balancera (stawka LCU: TODO: zweryfikować).

| Wariant | Składniki | USD/mies. 24/7 | USD/mies. 100 h |
|---|---|---|---|
| **EC2 + compose, PostgreSQL w kontenerze** | `t3.small` 0,024 USD/h, IPv4 0,005 USD/h, EBS gp3 0,0952 USD/GB-mies. | **23,07** | **3,16** |
| to samo na `t4g.small` | instancja 0,0192 USD/h | 19,57 | 2,68 |
| to samo na `t3.micro` | instancja 0,012 USD/h | 14,31 | 1,96 |
| EC2 + RDS | `t3.small` + `db.t4g.micro` 0,019 USD/h, pamięć 0,137 USD/GB-mies. | 39,68 | 5,44 |
| ECS Fargate bez ALB + RDS | 0,04656 USD za vCPU-h, 0,00511 USD za GB-h, IPv4, RDS | 40,98 | 5,61 |
| ECS Express Mode + RDS | Fargate, ALB 0,027 USD/h z dwoma adresami IPv4, RDS | 67,99 | 9,31 |
| App Runner + RDS | 0,074496 USD za vCPU-h (aktywny), 0,008176 USD za GB-h, RDS | 49,77 | 6,82 |

Koszty, których unika wybrana sieć (24/7):

- brama NAT: 0,052 USD/h, czyli 37,96 USD miesięcznie i 0,052 USD za każdy GB,
- trzy punkty końcowe VPC dla SSM w podsieci prywatnej (`ssm`, `ssmmessages`, `ec2messages`): 3 × 0,012 USD/h, czyli 26,28 USD miesięcznie,
- ALB: 0,027 USD/h, czyli 19,71 USD miesięcznie.

### Porównanie jakościowe

| Czynnik | EC2 + compose | ECS Fargate + RDS | ECS Express Mode + RDS | App Runner |
|---|---|---|---|---|
| Dostępność dla nowego konta | EC2 na liście usług planu darmowego | ECS na liście, Fargate niewymieniony osobno (TODO: zweryfikować w konsoli) | jak ECS | zamknięty dla nowych klientów od 2026-04-30, brak na liście planu darmowego |
| Zgodność z lokalnym i CI | ten sam compose (bez moto, S3 prawdziwy) | inna definicja środowiska (definicja zadania, RDS) | jak ECS Fargate | inna definicja środowiska |
| Zasoby w Terraformie | VPC, podsieć, SG, EC2, rola i profil instancji | dodatkowo klaster, definicja zadania, usługa, RDS i grupa podsieci | dodatkowo ALB i role infrastruktury | usługa App Runner, RDS, konektor VPC |
| Odpowiedzialność za system operacyjny | po stronie autora (aktualizacje, utwardzanie, E05-05) | po stronie AWS | po stronie AWS | po stronie AWS |
| Dostęp administracyjny | SSM bez otwartych portów | ECS Exec | ECS Exec | brak |

## Decyzja

Wybrano **jedną instancję EC2 `t3.small` w podsieci publicznej własnego VPC. PostgreSQL działa na niej w kontenerze, stos uruchamia ten sam Docker Compose co lokalnie, a dostęp administracyjny i wdrożenie idą przez SSM bez SSH.** Powody autora:

- **EC2 + compose zamiast Fargate:**
  - koszt: około 23 USD miesięcznie przy 24/7 wobec około 41 USD dla Fargate z RDS,
  - ten sam compose lokalnie, w CI i w AWS, więc mniej zmiennych w eksperymencie,
  - prostota konfiguracji i opisu w pracy: bez klastra, definicji zadań i RDS,
  - pełna kontrola nad hostem: system można utwardzić (E05-05) i pokazać odpowiedzialność klienta za system operacyjny.
- **ECS Express Mode** odpada z tych samych powodów co Fargate, a ALB podnosi koszt do około 68 USD miesięcznie.
- **App Runner** jest niedostępny: od 2026-04-30 nie przyjmuje nowych klientów, a AWS poleca zamiast niego ECS Express Mode.
- **PostgreSQL w kontenerze zamiast RDS:**
  - koszt: RDS dokłada około 16,6 USD miesięcznie przy 24/7,
  - jednakowe środowisko: ten sam obraz bazy lokalnie, w CI i w AWS (czynnik z ADR-0005),
  - dane są odtwarzalne: środowisko jest efemeryczne, a dane pochodzą z `seed`, więc kopie zapasowe i trwałość RDS nic tu nie dają,
  - szybsze `apply` i `destroy` (o ile szybsze: TODO: zweryfikować pomiarem w E05-04).
- **Tylko SSM, bez SSH:**
  - port 22 jest zamknięty, więc powierzchnia ataku jest mniejsza,
  - nie ma kluczy SSH u autora ani w GitHub Secrets, a potok działa przez OIDC i rolę IAM (ADR-0016),
  - wywołania SSM są logowane w CloudTrail jako wywołania API (audytowalność, E08-01).
- **`t3.small`:**
  - zapas pamięci: 2 GiB mieszczą aplikację, PostgreSQL i agenta SSM, a na `t3.micro` (1 GiB) grozi brak pamięci (TODO: zweryfikować zużycie pamięci po wdrożeniu),
  - typ jest na liście typów dostępnych na planie darmowym,
  - różnica kosztu względem `t4g.small` jest mała: około 0,50 USD miesięcznie przy 100 h.
- **Własne VPC z podsiecią publiczną:**
  - koszt: bez bramy NAT, punktów końcowych VPC i ALB,
  - sieć opisana kodem: własne VPC w Terraformie zamiast domyślnego, więc można je skanować (Checkov) i odtworzyć.
- **Wdrożenie tylko przy postawionym środowisku.** Job wdrożenia szuka instancji po tagach, a gdy jej nie ma, pomija wdrożenie z ostrzeżeniem. Powody:
  - najmniejsze uprawnienia: rola OIDC potoku nie dostaje praw do tworzenia sieci, instancji ani ról IAM,
  - krótszy potok: bez kilkuminutowego `apply` w każdym przebiegu na `main`,
  - zgodność z ADR-0019: środowisko stawia i usuwa autor w sesji pracy, a potok tylko wdraża,
  - pomiar nie cierpi: H2a mierzy workflow PR, a pełny potok z wdrożeniem raportujemy opisowo (E03-02).
- **Ten sam compose z `migrate` i `seed` w AWS.** Powód: jednakowe środowisko lokalnie, w CI i w AWS.
- **Tylko HTTP, bez HTTPS.** Powody:
  - brak domeny, więc nie ma zaufanego certyfikatu (TODO: zweryfikować, czy urzędy certyfikacji wystawiają certyfikaty dla adresów IP),
  - koszt i czas: domena, DNS i reverse proxy wykraczają poza cel pracy,
  - aplikacja jest badawcza: dane są fikcyjne, środowisko działa tylko w czasie pracy, a skan DAST idzie w CI na compose.

Wszystkie wybrane opcje zarekomendował agent, a autor je przyjął i wskazał powody z listy przygotowanej przez agenta. Rekomendacja „EC2 z compose i dostęp przez SSM” pochodzi też z definicji zadania E05-03 w katalogu zadań.

Wybór rejestru obrazów (GHCR albo ECR) należy do E05-04, a szczegóły wdrożenia (pobieranie obrazu po digeście, przekazanie sekretów na instancję, rollback) do E05-07.

## Konsekwencje

- (+) Koszt środowiska roboczego wynosi około 3,2 USD na 100 godzin pracy. Kredyty 100 USD pokrywają projekt z dużym zapasem (TODO: zweryfikować z rzeczywistymi kosztami w `docs/koszty.md`, E05-08).
- (+) Środowisko w AWS różni się od lokalnego tylko magazynem plików: zamiast usługi `s3` (moto) aplikacja używa prawdziwego kubełka S3 przez rolę instancji (ADR-0006). Potrzebna jest nakładka compose dla AWS albo profil bez moto (E05-07).
- (+) Brak otwartego portu 22 i brak kluczy SSH. Grupa bezpieczeństwa wpuszcza tylko port 80. Katalog E05-04 przewidywał 80/443, ale bez HTTPS port 443 nie jest potrzebny.
- (+) Obraz aplikacji jest budowany w CI dla `linux/amd64`, a `t3.small` ma tę samą architekturę, więc nie potrzeba budowania wieloarchitekturowego.
- (−) Autor odpowiada za system operacyjny instancji: aktualizacje, instalację Dockera, utwardzanie (E05-05). Model współdzielonej odpowiedzialności przesuwa się w stronę klienta. To materiał do 2.3 i 5.3.
- (−) Jedna instancja w jednej strefie dostępności: brak wysokiej dostępności. To akceptowalne dla aplikacji badawczej i opisane jako ograniczenie w 5.3.
- (−) Dane PostgreSQL leżą na wolumenie EBS instancji i znikają przy `destroy` (ADR-0019). Każde `apply` i wdrożenie odtwarza je przez `migrate` i `seed`.
- (−) Ruch HTTP jest nieszyfrowany: dane logowania kont testowych i token JWT idą otwartym tekstem. Ograniczenie do 5.3. Wdrożona aplikacja nie powinna przyjmować prawdziwych danych.
- (−) Instancja w podsieci publicznej ma publiczny adres IPv4, a ruch wychodzący (SSM, rejestr obrazów, S3) idzie przez bramę internetową. Ochronę zapewnia grupa bezpieczeństwa, nie izolacja sieci.
- (−) Merge do `main` przy usuniętej infrastrukturze nic nie wdraża. Wdrożenie trzeba wtedy wywołać ponownie po postawieniu środowiska (E06-03).
- Ceny i dostępność usług pochodzą z 2026-11-11. App Runner może zostać całkiem wycofany (TODO: zweryfikować przy pisaniu 4.2).
- Rozstrzyga sprawy otwarte w ADR-0005 (kontener, nie RDS), ADR-0019 (wdrożenie tylko przy postawionym środowisku) i ADR-0023 (compose z `seed` także w AWS). Treści tamtych ADR-ów się nie zmienia.
- E05-04: Terraform tworzy VPC, podsieć publiczną, bramę internetową, grupę bezpieczeństwa (wejście 80), instancję `t3.small` z IMDSv2 i szyfrowanym EBS, rolę i profil instancji z politykami SSM i dostępu do kubełka S3.
- E05-07: wdrożenie przez SSM Run Command, sprawdzenie istnienia instancji po tagach i źródło sekretów `.env` na instancji.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- AWS Price List API, cenniki regionalne `eu-central-1` (wersje w sekcji „Porównanie kosztu”): https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/
- AWS, *AWS App Runner availability change*: https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html (sprawdzone 2026-11-11)
- AWS, *Amazon ECS Express Mode*: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html
- AWS, *Supported AWS services for Sign up for AWS (new)*: https://docs.aws.amazon.com/accounts/latest/reference/supported-services-sign-up-new.html (sprawdzone 2026-11-11)
- AWS, *Track your Free Tier usage for Amazon EC2* (typy instancji na planie darmowym): https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html
- AWS, *AWS Systems Manager pricing* (Session Manager i Run Command na EC2 bez dodatkowych opłat): https://aws.amazon.com/systems-manager/pricing/
