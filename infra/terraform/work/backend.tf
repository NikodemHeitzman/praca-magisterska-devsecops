# State bucket created by ../shared. Backend blocks cannot use variables.
terraform {
  backend "s3" {
    bucket       = "devsecops-thesis-tfstate-7602609f"
    key          = "work/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true
  }
}
