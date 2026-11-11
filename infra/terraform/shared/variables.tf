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

variable "state_bucket_name" {
  description = "Globally unique name of the Terraform state bucket; must match the bucket in backend.tf of both layers."
  type        = string
  default     = "devsecops-thesis-tfstate-7602609f"
}

variable "state_noncurrent_days" {
  description = "Days after which noncurrent versions of state objects are deleted."
  type        = number
  default     = 90
}
