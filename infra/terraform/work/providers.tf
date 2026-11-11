provider "aws" {
  region = var.region

  # Tagging convention: docs/aws-konto.md. Pipeline variants (a, b) share this environment.
  default_tags {
    tags = {
      Project   = "devsecops-thesis"
      Variant   = "shared"
      ManagedBy = "terraform"
      Owner     = var.owner
    }
  }
}
