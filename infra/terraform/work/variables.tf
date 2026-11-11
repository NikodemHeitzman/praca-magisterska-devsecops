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
