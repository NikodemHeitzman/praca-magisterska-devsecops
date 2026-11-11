# Permanent layer (docs/adr/0026-stan-terraform-i-warstwy.md): Terraform state bucket.
# Later: GitHub OIDC provider and pipeline role (E05-06), CloudTrail (E08-01).
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
