# 0028. System instancji EC2: Ubuntu Server 24.04 LTS z przypiętym ID AMI

- **Status:** przyjęty
- **Data:** 2026-11-11
- **Decydujący:** autor pracy
- **Powiązane:** [0024](0024-architektura-aws-ec2-docker-compose.md), [0025](0025-narzedzie-iac-terraform.md), zadania E05-04, E05-05, E05-07, [dziennik 2026-11-11](../log/2026-11-11.md)

## Kontekst

Instancja EC2 `t3.small` (ADR-0024) potrzebuje obrazu systemu (AMI). Na instancji mają działać Docker z wtyczką compose (E05-05) i agent SSM (dostęp bez SSH, ADR-0024). Zasada 6 `AGENTS.md` wymaga przypiętych wersji obrazów bazowych. Instalacja i utwardzanie systemu należą do E05-05.

## Czynniki decyzyjne

- znajomość systemu przez autora,
- dostępność Dockera i wtyczki compose z pakietów systemu,
- obecność agenta SSM w obrazie,
- odtwarzalność: każde `apply` startuje z tego samego obrazu.

## Rozważane opcje

System:

1. Ubuntu Server 24.04 LTS (Canonical)
2. Amazon Linux 2023

Wybór ID AMI:

1. przypięte ID AMI w kodzie, zmieniane świadomie
2. najnowsze AMI z publicznego parametru SSM przy każdym `apply`

## Decyzja

Wybrano **Ubuntu Server 24.04 LTS z przypiętym ID AMI**. Rekomendacją agenta był Amazon Linux 2023. Powody autora:

- **Ubuntu zamiast Amazon Linux 2023:**
  - autor zna Ubuntu,
  - Docker i compose są w pakietach systemu: `docker.io` i `docker-compose-v2` (w wydaniu noble 2.24.6, komponent universe; packages.ubuntu.com, sprawdzone 2026-11-11),
  - przenośność: ten sam system działa poza AWS.
- **Przypięte ID zamiast parametru SSM:** odtwarzalność. Każde `apply` daje ten sam system bazowy, więc w eksperymencie jest mniej zmiennych.

Przypięty obraz: `ami-06fb1802e2b757f09`, Ubuntu 24.04 LTS (noble), amd64, `hvm-ssd-gp3`, kompilacja z 2026-10-23, region `eu-north-1` (ADR-0030; pierwotnie `ami-0c228cd2b65888e1b` w `eu-central-1`) (Ubuntu Cloud Image Locator, sprawdzone 2026-11-11). Terraform sprawdza przy `plan`, że AMI należy do Canonical (ID właściciela `099720109477`: TODO: zweryfikować w dokumentacji Canonical).

Agent SSM jest preinstalowany w AMI Ubuntu Server 24.04 LTS (dokumentacja AWS Systems Manager) jako pakiet snap.

## Konsekwencje

- (+) Każda sesja startuje z tego samego obrazu, a zmiana systemu jest widoczna w historii repozytorium jako commit.
- (+) Instalacja Dockera w E05-05 nie wymaga ręcznego pobierania binariów compose.
- (−) Przypięty obraz się starzeje. Łatki z nowszych kompilacji trafiają na instancję dopiero po aktualizacji ID albo przez aktualizacje pakietów na działającej instancji (E05-05). Do zapisania jako kompromis między odtwarzalnością a aktualnością w 5.3.
- (−) Wersje `docker.io` i `docker-compose-v2` z Ubuntu są starsze od wydań Dockera. Źródło pakietów (Ubuntu czy repozytorium Dockera) ustala E05-05.
- (−) Agent SSM jako snap ma inną nazwę usługi (`snap.amazon-ssm-agent.amazon-ssm-agent.service`) niż w wersji z pakietu deb. To ważne przy diagnostyce i w E05-05.
- (−) Odchodzi od rekomendacji agenta: Amazon Linux 2023 ma wersjonowane repozytoria pakietów i wsparcie AWS. W pracy trzeba to zestawić z powodami autora.

## Źródła

Źródła spoza rejestru `Zrodla/` (TODO: zweryfikować, czy rejestrować):

- Ubuntu Cloud Image Locator, `https://cloud-images.ubuntu.com/locator/releasesTable` (sprawdzone 2026-11-11)
- Ubuntu Packages, *docker-compose-v2 (noble)*: https://packages.ubuntu.com/noble/docker-compose-v2 (sprawdzone 2026-11-11)
- AWS, *Find AMIs with the SSM Agent preinstalled*: https://docs.aws.amazon.com/systems-manager/latest/userguide/ami-preinstalled-agent.html (sprawdzone 2026-11-11)
