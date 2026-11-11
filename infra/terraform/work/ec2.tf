# Fails at plan time if the pinned AMI does not exist or is not published by Canonical.
data "aws_ami" "ubuntu" {
  owners = [var.ami_owner]

  filter {
    name   = "image-id"
    values = [var.ami_id]
  }
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

  # Docker, updates and hardening: E05-05 (Ansible or user data).

  # The deploy job finds the instance by its tags (E05-07).
  tags = {
    Name = "${var.name_prefix}-app"
  }

  volume_tags = {
    Name = "${var.name_prefix}-app-root"
  }
}
