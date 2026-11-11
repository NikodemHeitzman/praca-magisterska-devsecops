provider "aws" {
  region = var.region

  # Tagging convention: docs/aws-konto.md
  default_tags {
    tags = {
      Project   = "devsecops-thesis"
      Variant   = "shared"
      ManagedBy = "terraform"
      Owner     = var.owner
    }
  }
}
