output "instance_id" {
  description = "ID of the app instance (target of SSM Session Manager and Run Command)."
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IPv4 address of the app instance."
  value       = aws_instance.app.public_ip
}

output "app_url" {
  description = "HTTP URL of the app (no HTTPS, ADR-0024)."
  value       = "http://${aws_instance.app.public_dns}"
}

output "attachments_bucket" {
  description = "Value of S3_BUCKET in the app .env on the instance."
  value       = aws_s3_bucket.attachments.id
}

output "deploy_tag" {
  description = "GHCR tag the deploy agent follows (ADR-0033)."
  value       = "${var.image_repository}:${local.deploy_tag}"
}

output "version_url" {
  description = "Deployed image digest and commit, to confirm a deployment from outside (ADR-0033)."
  value       = "http://${aws_instance.app.public_dns}/version"
}
