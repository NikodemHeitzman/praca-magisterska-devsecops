# Fails at plan time if the pinned AMI does not exist or is not published by Canonical.
data "aws_ami" "ubuntu" {
  owners = [var.ami_owner]

  filter {
    name   = "image-id"
    values = [var.ami_id]
  }
}

# The deployment settings are prepended as shell assignments instead of using templatefile(),
# so user-data.sh stays a plain bash file that ShellCheck can lint (its own shebang then
# reads as a comment). GHCR tags cannot contain "/", hence exp/variant-a -> exp-variant-a.
locals {
  deploy_tag = replace(var.deploy_branch, "/", "-")

  user_data = join("\n", [
    "#!/bin/bash",
    "# Deployment settings rendered by Terraform (infra/terraform/work/ec2.tf, ADR-0033).",
    "IMAGE_REPOSITORY='${var.image_repository}'",
    "DEPLOY_TAG='${local.deploy_tag}'",
    "SOURCE_REPOSITORY='${var.source_repository}'",
    "S3_BUCKET='${aws_s3_bucket.attachments.id}'",
    "AWS_REGION='${var.region}'",
    "DEPLOY_AGENT_GZ_B64='${base64gzip(file("${path.module}/deploy-agent.sh"))}'",
    file("${path.module}/user-data.sh"),
  ])
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  iam_instance_profile        = aws_iam_instance_profile.instance.name
  associate_public_ip_address = true
  ebs_optimized               = true

  # Detailed monitoring is billed per metric; basic monitoring is enough for an ephemeral host.
  monitoring = false

  # IMDSv2 only. Hop limit 2: the app runs in a Docker bridge network and needs the
  # instance role credentials for S3, which is one network hop more than from the host.
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
    instance_metadata_tags      = "disabled"
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size
    encrypted             = true
    delete_on_termination = true
  }

  # Docker, security updates and hardening on first boot (ADR-0031), then the deploy agent
  # (ADR-0033). A changed script or deploy setting (e.g. deploy_branch) replaces the
  # instance, so every apply starts from the same configuration.
  user_data                   = local.user_data
  user_data_replace_on_change = true

  # check-host.sh and check-deploy.sh find the instance by its Name tag. SkipCleanup=true
  # keeps the instance past its time to live (cleanup.tf, ADR-0034).
  tags = merge(
    { Name = "${var.name_prefix}-app" },
    var.skip_cleanup ? { SkipCleanup = "true" } : {},
  )

  volume_tags = {
    Name = "${var.name_prefix}-app-root"
  }
}
