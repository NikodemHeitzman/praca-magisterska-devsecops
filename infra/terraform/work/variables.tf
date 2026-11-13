variable "region" {
  description = "AWS region (docs/adr/0030-region-aws-eu-north-1.md)."
  type        = string
  default     = "eu-north-1"
}

variable "owner" {
  description = "Value of the Owner tag: GitHub login of the thesis author."
  type        = string
  default     = "NikodemHeitzman"
}

variable "name_prefix" {
  description = "Prefix of resource names; the IAM policy of the terraform user is scoped to it (docs/adr/0029-uprawnienia-uzytkownika-terraform.md)."
  type        = string
  default     = "devsecops-thesis"
}

variable "availability_zone" {
  description = "Single availability zone of the public subnet."
  type        = string
  default     = "eu-north-1a"
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block of the public subnet."
  type        = string
  default     = "10.42.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type (docs/adr/0024-architektura-aws-ec2-docker-compose.md)."
  type        = string
  default     = "t3.small"
}

variable "ami_id" {
  description = "Pinned Ubuntu Server 24.04 LTS AMI, amd64, hvm-ssd-gp3, build 20261023 (docs/adr/0028-system-instancji-ubuntu-przypiete-ami.md)."
  type        = string
  default     = "ami-06fb1802e2b757f09"
}

variable "ami_owner" {
  description = "Account ID of Canonical; the plan fails if ami_id is published by anyone else."
  type        = string
  default     = "099720109477"
}

variable "root_volume_size" {
  description = "Size of the encrypted gp3 root volume in GiB."
  type        = number
  default     = 20
}

# Deployment in the pull model (docs/adr/0033-mechanizm-wdrozenia-pull.md).
variable "deploy_branch" {
  description = "Base branch of the experiment variant whose GHCR tag the instance follows; one variant per session (experiment/PROTOCOL.md)."
  type        = string
  default     = "exp/variant-a"

  validation {
    condition     = contains(["exp/variant-a", "exp/variant-b"], var.deploy_branch)
    error_message = "deploy_branch must be exp/variant-a or exp/variant-b."
  }
}

variable "image_repository" {
  description = "Public GHCR package of the app image, lowercase (docs/adr/0027-rejestr-obrazow-ghcr.md)."
  type        = string
  default     = "ghcr.io/nikodemheitzman/praca-magisterska-devsecops"

  validation {
    condition     = can(regex("^ghcr[.]io/[a-z0-9._-]+/[a-z0-9._/-]+$", var.image_repository))
    error_message = "image_repository must be a lowercase ghcr.io/<owner>/<name> reference without a tag."
  }
}

variable "source_repository" {
  description = "Public GitHub repository (owner/name) the instance downloads compose files from, at the commit of the image."
  type        = string
  default     = "NikodemHeitzman/praca-magisterska-devsecops"
}

# Automatic cleanup (docs/adr/0034-automatyczne-sprzatanie-eventbridge-scheduler.md).
variable "instance_ttl_hours" {
  description = "Hours after the plan that creates the instance until EventBridge Scheduler terminates it."
  type        = number
  default     = 8

  validation {
    condition     = var.instance_ttl_hours >= 0.25 && var.instance_ttl_hours <= 24
    error_message = "instance_ttl_hours must be from 0.25 (15 min, for testing the cleanup) to 24."
  }
}

variable "skip_cleanup" {
  description = "Tag the instance SkipCleanup=true so the scheduled cleanup leaves it running (long experiment runs, E09)."
  type        = bool
  default     = false
}
