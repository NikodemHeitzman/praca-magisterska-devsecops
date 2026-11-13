# Infrastruktura AWS (Terraform)

Infrastruktura z [ADR-0024](../../docs/adr/0024-architektura-aws-ec2-docker-compose.md) w dwóch warstwach z osobnymi plikami stanu ([ADR-0026](../../docs/adr/0026-stan-terraform-i-warstwy.md)):

| Katalog | Warstwa | Zasoby | Cykl życia |
|---|---|---|---|
| [`shared/`](shared/) | stała | kubełek stanu Terraformu (później: CloudTrail z E08-01; OIDC z E05-06 zablokowane przez SCP konta, ADR-0032) | zostaje do E15-08 |
| [`work/`](work/) | robocza | VPC, podsieć publiczna, brama internetowa, grupa bezpieczeństwa (wejście tylko 80), EC2 `t3.small` z IMDSv2 i szyfrowanym EBS, rola i profil instancji (SSM, kubełek załączników), kubełek załączników, harmonogram sprzątania z rolą ([ADR-0034](../../docs/adr/0034-automatyczne-sprzatanie-eventbridge-scheduler.md)) | `apply` na początku sesji, `destroy` na końcu ([ADR-0019](../../docs/adr/0019-srodowisko-efemeryczne-aws.md)); instancja usuwana automatycznie po 8 h |

Wersje: Terraform `1.17.1`, provider `hashicorp/aws` `6.72.0`, przypięte dokładnie, sumy kontrolne w `.terraform.lock.hcl` ([ADR-0025](../../docs/adr/0025-narzedzie-iac-terraform.md)). System instancji: przypięte AMI Ubuntu 24.04 LTS ([ADR-0028](../../docs/adr/0028-system-instancji-ubuntu-przypiete-ami.md)).

## Uwierzytelnianie

Lokalnie: użytkownik IAM `terraform` z polityką [`infra/iam/terraform-user-policy.json`](../iam/terraform-user-policy.json) ([ADR-0016](../../docs/adr/0016-uwierzytelnianie-do-aws.md), [ADR-0029](../../docs/adr/0029-uprawnienia-uzytkownika-terraform.md)). Klucz leży tylko w `~/.aws/credentials` w profilu nazwanym. Profil wybiera się zmienną środowiskową, nie w kodzie:

```bash
export AWS_PROFILE=devsecops-terraform
aws sts get-caller-identity
```

W PowerShell: `$env:AWS_PROFILE = "devsecops-terraform"`.

## Pierwsze uruchomienie (bootstrap warstwy stałej)

Kubełek stanu tworzy `shared/`, który sam przechowuje w nim swój stan. Za pierwszym razem backendu jeszcze nie ma, więc:

```bash
cd infra/terraform/shared
mv backend.tf backend.tf.off          # stan lokalny na czas tworzenia kubełka
terraform init
terraform apply
mv backend.tf.off backend.tf
terraform init -migrate-state         # przeniesienie stanu do S3, odpowiedź "yes"
rm -f terraform.tfstate terraform.tfstate.backup
```

Nazwa kubełka stanu (`devsecops-thesis-tfstate-7602609f`) jest w `shared/backend.tf`, `shared/variables.tf` i `work/backend.tf`. Na innym koncie trzeba ją zmienić we wszystkich trzech miejscach (nazwy kubełków są globalne).

## Sesja pracy

```bash
cd infra/terraform/work
terraform init
terraform plan -out=work.tfplan
terraform apply work.tfplan
# ... praca ...
terraform destroy
terraform state list                  # musi być pusto (docs/aws-konto.md, zasady kosztowe)
```

Zamiast dwóch ostatnich poleceń: skrypt teardown (sekcja „Koniec sesji: teardown”).

Pierwszy przebieg (2026-11-11, `eu-north-1`, Terraform 1.17.1, łącze domowe autora):

| Operacja | Zasoby | Czas |
|---|---|---|
| `shared/` `apply` (bootstrap, stan lokalny) | 7 | 68 s |
| `work/` `apply` | 20 | 29 s (instancja 17 s) |
| `work/` `destroy` | 20 | 50 s |

Po `apply` agent SSM zgłosił się jako `Online` (agent 3.3.4793.0, sprawdzone w CloudShell). Pojedynczy pomiar, bez powtórzeń.

Instancja nie ma klucza SSH ani otwartego portu 22. Dostęp: AWS Systems Manager, Session Manager (konsola albo `aws ssm start-session --target <instance_id>`). Wdrożenie aplikacji: sekcja „Wdrożenie (model pull)”.

Wariant wdrażany w sesji wybiera zmienna `deploy_branch` (domyślnie `exp/variant-a`), np. `terraform plan "-var=deploy_branch=exp/variant-b" "-out=work.tfplan"`. Zmiana wariantu tworzy nową instancję, bo zmienia user-data.

## Automatyczne sprzątanie (EventBridge Scheduler)

[`work/cleanup.tf`](work/cleanup.tf) tworzy razem z instancją jednorazowy harmonogram EventBridge Scheduler. Usuwa on instancję `instance_ttl_hours` (domyślnie 8) godzin po planie, który ją utworzył ([ADR-0034](../../docs/adr/0034-automatyczne-sprzatanie-eventbridge-scheduler.md)):

- cel uniwersalny `ec2:terminateInstances`, bez Lambdy; z instancją znikają publiczny IPv4 i wolumen,
- rola `devsecops-thesis-cleanup` może usunąć tylko instancję z tagiem `Project=devsecops-thesis` w `eu-north-1` i nigdy instancji z tagiem `SkipCleanup=true`,
- po wykonaniu harmonogram sam się usuwa (`action_after_completion = DELETE`),
- moment usunięcia (UTC) pokazuje wyjście `cleanup_at_utc`.

Sieć, grupy bezpieczeństwa, role i kubełek załączników zostają (są bezpłatne) i czekają na `destroy`. Następny `plan` po automatycznym usunięciu pokaże odtworzenie instancji i harmonogramu.

Dłuższa sesja (np. przebieg E09):

- przy `apply`: `terraform plan "-var=skip_cleanup=true" "-out=work.tfplan"` (tag zmienia się w miejscu, bez wymiany instancji),
- w trakcie sesji: tag `SkipCleanup` = `true` na instancji w konsoli EC2; kolejny `apply` bez zmiennej go usunie,
- albo ponowny `apply` po wykonaniu harmonogramu: harmonogram powstaje od nowa z nowym czasem.

Zmiana `instance_ttl_hours` nie przesuwa istniejącego harmonogramu (czas jest ustalany przy jego tworzeniu). Żeby go przesunąć: `terraform apply "-replace=aws_scheduler_schedule.cleanup"`.

## Koniec sesji: teardown

[`teardown.ps1`](teardown.ps1), w lokalnym PowerShell z katalogu repozytorium:

```powershell
powershell -ExecutionPolicy Bypass -File .\infra\terraform\teardown.ps1
```

`-ExecutionPolicy Bypass` dotyczy tylko tego jednego procesu. Bez niego Windows z domyślnymi zasadami wykonywania odrzuca skrypt („running scripts is disabled on this system”). Ustawień systemu nie zmieniamy.

Skrypt:

1. ustawia profil `devsecops-terraform` i region `eu-north-1`,
2. uruchamia `terraform destroy` warstwy `work/` (z potwierdzeniem; `-AutoApprove` je pomija),
3. sprawdza, że `terraform state list` jest pusty,
4. szuka w AWS zasobów z tagiem `Project=devsecops-thesis`: instancji (poza usuniętymi), wolumenów EBS, VPC i adresów Elastic IP, oraz harmonogramów z prefiksem projektu,
5. wypisuje czasy i kończy się kodem 0 tylko wtedy, gdy nic nie zostało.

`-CheckOnly` pomija `destroy` i robi tylko kontrolę, np. po automatycznym sprzątaniu. Warstwy stałej (`shared/`) skrypt nie dotyka.

Test 2026-11-13 (pojedynczy przebieg, `instance_ttl_hours = 0.25`, szczegóły w ADR-0034, sekcja „Weryfikacja”):

| Krok | Wynik |
|---|---|
| automatyczne usunięcie instancji | 41 s po czasie z harmonogramu; wywołanie przez rolę `devsecops-thesis-cleanup` (CloudTrail), harmonogram usunął się sam |
| `plan` po automatycznym usunięciu | tylko odtworzenie instancji i harmonogramu (2 do dodania) |
| instancja z `SkipCleanup=true` | przetrwała; jedno wywołanie z `Client.UnauthorizedOperation` (jawna odmowa), bez ponowień |
| `teardown.ps1` | `destroy` 22 zasobów w 32 s, kontrola OK, razem 42 s |

## Konfiguracja hosta (user-data)

Przy pierwszym starcie cloud-init uruchamia jako root [`work/user-data.sh`](work/user-data.sh) ([ADR-0031](../../docs/adr/0031-konfiguracja-hosta-user-data.md)):

1. Docker i wtyczka compose z archiwum Ubuntu (`docker.io`, `docker-compose-v2`),
2. `/etc/docker/daemon.json`: rotacja logów kontenerów i `no-new-privileges`,
3. użytkownik systemowy `app` bez powłoki logowania, w grupie `docker`, z katalogiem `/opt/app` (750),
4. `ssh.socket` i `ssh.service` zatrzymane i zamaskowane,
5. `unattended-upgrades`: łatki bezpieczeństwa według domyślnych źródeł Ubuntu, bez automatycznego restartu,
6. ufw wyłączony; jedyną zaporą jest grupa bezpieczeństwa (Docker omija ufw),
7. `/opt/app/.env` z sekretami losowanymi na instancji (hasło PostgreSQL, klucz JWT, hasła kont z `seed`) i z publicznym adresem z IMDSv2 jako jedynym originem CORS ([ADR-0033](../../docs/adr/0033-mechanizm-wdrozenia-pull.md)),
8. agent wdrożenia: `/etc/ticketing/deploy.conf`, `/usr/local/bin/ticketing-deploy` (z [`work/deploy-agent.sh`](work/deploy-agent.sh)) i timer systemd `ticketing-deploy.timer`.

`ec2.tf` dopisuje na początku skryptu ustawienia wdrożenia (repozytorium obrazu, tag, kubełek, region) i spakowany agent. Dzięki temu `user-data.sh` zostaje zwykłym plikiem bash, który sprawdza ShellCheck, bez składni `templatefile()`.

Każdy krok sprawdza stan przed zmianą, więc ponowne uruchomienie niczego nie zmienia i wypisuje `harden: done, 0 change(s)`. Zmiana skryptu tworzy przy `apply` nową instancję (`user_data_replace_on_change`).

Kontrola hosta po `apply`: [`check-host.sh`](check-host.sh) wywołuje przez SSM Run Command status cloud-init, drugie przebiegnięcie skryptu (test idempotencji), wersje pakietów i stan usług. Użytkownik `terraform` nie ma uprawnień SSM, więc skrypt uruchamia się w AWS CloudShell (`eu-north-1`) jako Owner:

```bash
bash check-host.sh
```

Test 2026-11-11 (pojedynczy pomiar, szczegóły w ADR-0031, sekcja „Weryfikacja”):

| Pomiar | Wynik |
|---|---|
| `work/` `apply` ze skryptem user-data | 20 zasobów w 25 s (instancja 13 s) |
| user-data przy pierwszym starcie | 7 zmian, 25,3 s (cały cloud-init 28,7 s) |
| drugie przebiegnięcie przez SSM | 0 zmian, poniżej 1 s |
| Docker / Compose z archiwum Ubuntu | 29.1.3 / 2.40.3 |
| port 22 | nic nie nasłuchuje (`ssh.socket` i `ssh.service` zamaskowane) |
| `work/` `destroy` | 20 zasobów w 29 s, `state list` pusty |

Uwaga dla Windows PowerShell 5.1: argument `-out=work.tfplan` trzeba wziąć w cudzysłów (`terraform plan "-out=work.tfplan"`), bo PowerShell rozbija go na kropce.

## Wdrożenie (model pull)

Potok nie ma poświadczeń AWS ([ADR-0032](../../docs/adr/0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md)). Wdrożenie działa tak ([ADR-0033](../../docs/adr/0033-mechanizm-wdrozenia-pull.md)):

1. Potok publikuje obraz w GHCR z tagiem SHA commita i z tagiem gałęzi wariantu (`exp-variant-a`, `exp-variant-b`) oraz z etykietą `org.opencontainers.image.revision`.
2. `ticketing-deploy.timer` mniej więcej co minutę uruchamia agenta jako użytkownik `app`. Agent pyta GHCR anonimowo, na który digest wskazuje tag. Gdy digest jest nowy, pobiera obraz po digeście, z etykiety bierze SHA commita i pobiera `app/compose.yaml` oraz [`app/compose.aws.yaml`](../../app/compose.aws.yaml) z tego commita.
3. `docker compose up` (`migrate`, `seed`, `app` na porcie 80, bez moto). Agent czeka, aż `/version` pokaże nowy obraz, a `/health` odpowie `200`.
4. Wynik trafia do `journalctl -u ticketing-deploy` i do `/opt/app/state/deployments.log` (czas, tag, obraz, commit, wynik, wersje Dockera i Compose). Digest, którego wdrożenie się nie udało, nie jest ponawiany do następnej zmiany tagu.

Rollback: workflow [`rollback`](../../.github/workflows/rollback.yml) (`workflow_dispatch`, gałąź i digest) przesuwa tag na wcześniej opublikowany obraz, kopiując manifest bez zmian, więc digest jest ten sam. Instancja wdraża go jak każdą wersję.

Potwierdzenie: `curl http://<public DNS>/version` (wyjście `version_url`) albo w CloudShell:

```bash
bash check-deploy.sh                        # historia wdrożeń, log agenta, kontenery
SHOW_SEED_PASSWORDS=1 bash check-deploy.sh  # dodatkowo hasła kont z seed (np. do audytu)
```

Wynik `send-command` z hasłami zostaje w historii poleceń SSM. Hasła są fikcyjne i giną z instancją, ale nie uruchamiaj tej opcji bez potrzeby.

Według dokumentacji GitHub nowy pakiet GHCR jest prywatny. W teście E05-07 pakiet opublikowany przez workflow tego publicznego repozytorium był od razu dostępny anonimowo. Jeśli instancja dostaje błąd przy zapytaniu o manifest, sprawdź widoczność pakietu (Package settings, Change visibility).

Test 2026-11-13 (pojedynczy przebieg, szczegóły w ADR-0033, sekcja „Weryfikacja”):

| Krok | Wynik |
|---|---|
| pierwsze wdrożenie po `apply` | `/version` i `/health` potwierdzone z zewnątrz |
| nowy digest pod tagiem | wdrożony 39 s po wypchnięciu tagu, bez kroku ręcznego |
| rollback (`rollback.yml`) | workflow 8 s, ten sam digest wdrożony 63 s później (samo wdrożenie 14 s) |
| user-data | 13 zmian w 30,0 s, drugie przebiegnięcie 0 zmian |
| `work/` `destroy` | 20 zasobów, instancja 20 s, `state list` pusty |

## Kontrola przed commitem

```bash
terraform fmt -check -recursive
terraform -chdir=shared validate
terraform -chdir=work validate
```

Skan IaC (Checkov, Trivy) uruchamia potok DevSecOps (E07). Kod w tym katalogu jest wersją czystą: nie zawiera wpisów z katalogu ground truth GT-10 (port 22 otwarty dla `0.0.0.0/0`) ani GT-11 (wyłączone szyfrowanie). Warianty podatne powstają jako osobne łatki ([`docs/app-spec.md`](../../docs/app-spec.md)).

Lokalny skan Trivy 0.76.0 (`trivy config infra/`, 2026-11-11) czystej wersji daje 8 trafień. Wszystkie wynikają ze świadomych decyzji, nie z GT. Kod ich nie wycisza, bo sposób liczenia takich trafień w eksperymencie ustala E07:

| Reguła | Gdzie | Dlaczego zostaje |
|---|---|---|
| AWS-0104 (×2) | wyjście 80 i 443 do `0.0.0.0/0` | adresy mirrorów Ubuntu, SSM, `ghcr.io` i S3 nie są stałe; bez NAT i proxy nie da się ich zawęzić (ADR-0024) |
| AWS-0132 (×2) | SSE-S3 zamiast klucza KMS klienta | koszt i prostota; dane są fikcyjne i efemeryczne |
| AWS-0089 (×2) | brak logów dostępu S3 | audyt wywołań API daje CloudTrail (E08-01) |
| AWS-0090 | brak wersjonowania kubełka załączników | dane efemeryczne, kubełek usuwany przy `destroy` |
| AWS-0178 | brak VPC Flow Logs | koszt CloudWatch; do rozważenia w E08 |
