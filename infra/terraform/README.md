# Infrastruktura AWS (Terraform)

Infrastruktura z [ADR-0024](../../docs/adr/0024-architektura-aws-ec2-docker-compose.md) w dwóch warstwach z osobnymi plikami stanu ([ADR-0026](../../docs/adr/0026-stan-terraform-i-warstwy.md)):

| Katalog | Warstwa | Zasoby | Cykl życia |
|---|---|---|---|
| [`shared/`](shared/) | stała | kubełek stanu Terraformu (później: OIDC z E05-06, CloudTrail z E08-01) | zostaje do E15-08 |
| [`work/`](work/) | robocza | VPC, podsieć publiczna, brama internetowa, grupa bezpieczeństwa (wejście tylko 80), EC2 `t3.small` z IMDSv2 i szyfrowanym EBS, rola i profil instancji (SSM, kubełek załączników), kubełek załączników | `apply` na początku sesji, `destroy` na końcu ([ADR-0019](../../docs/adr/0019-srodowisko-efemeryczne-aws.md)) |

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

Pierwszy przebieg (2026-11-11, `eu-north-1`, Terraform 1.17.1, łącze domowe autora):

| Operacja | Zasoby | Czas |
|---|---|---|
| `shared/` `apply` (bootstrap, stan lokalny) | 7 | 68 s |
| `work/` `apply` | 20 | 29 s (instancja 17 s) |
| `work/` `destroy` | 20 | 50 s |

Po `apply` agent SSM zgłosił się jako `Online` (agent 3.3.4793.0, sprawdzone w CloudShell). Pojedynczy pomiar, bez powtórzeń.

Instancja nie ma klucza SSH ani otwartego portu 22. Dostęp: AWS Systems Manager, Session Manager (konsola albo `aws ssm start-session --target <instance_id>`). Docker i utwardzanie systemu: E05-05. Wdrożenie aplikacji: E05-07.

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
