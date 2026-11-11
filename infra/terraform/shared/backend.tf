# Remote state in the bucket created by this layer (bootstrap: see ../README.md).
# Backend blocks cannot use variables, so values are literal.
terraform {
  backend "s3" {
    bucket       = "devsecops-thesis-tfstate-7602609f"
    key          = "shared/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true
  }
}
