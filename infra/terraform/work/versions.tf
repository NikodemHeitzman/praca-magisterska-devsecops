# Working layer (docs/adr/0026-stan-terraform-i-warstwy.md): created at the start of a work
# session and destroyed at its end (docs/adr/0019-srodowisko-efemeryczne-aws.md).
# Architecture: docs/adr/0024-architektura-aws-ec2-docker-compose.md.
terraform {
  required_version = "1.17.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.72.0"
    }
  }
}
