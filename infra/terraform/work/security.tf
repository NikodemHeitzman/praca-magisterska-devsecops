# Inbound HTTP only: no SSH (access through SSM) and no HTTPS (docs/adr/0024-architektura-aws-ec2-docker-compose.md).
resource "aws_security_group" "web" {
  name        = "${var.name_prefix}-web"
  description = "Ticketing app: HTTP in; HTTP and HTTPS out"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "${var.name_prefix}-web"
  }
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.web.id
  description       = "HTTP from the internet (no HTTPS, ADR-0024)"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

# Outbound traffic the host needs: Ubuntu mirrors (HTTP), SSM, ghcr.io and S3 (HTTPS).
# DNS to the VPC resolver and NTP to the link-local Amazon Time Sync Service are not
# filtered by security groups.
resource "aws_vpc_security_group_egress_rule" "http" {
  security_group_id = aws_security_group.web.id
  description       = "Package mirrors (apt over HTTP)"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.web.id
  description       = "SSM, ghcr.io, S3 and package mirrors over HTTPS"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}
