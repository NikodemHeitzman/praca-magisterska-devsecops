# Permanent layer (docs/adr/0026-stan-terraform-i-warstwy.md): Terraform state bucket.
# Later: CloudTrail (E08-01). No GitHub OIDC provider: blocked by the account SCP (docs/adr/0032-potok-bez-poswiadczen-aws-wdrozenie-pull.md).
# Versions pinned exactly (AGENTS.md rule 6, docs/adr/0025-narzedzie-iac-terraform.md).
terraform {
  required_version = "1.17.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.72.0"
    }
  }
}
