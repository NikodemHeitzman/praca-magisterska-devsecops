#!/bin/bash
# Host bootstrap and hardening for the app instance (ADR-0031) and the pull-model deploy
# agent (ADR-0033).
#
# cloud-init runs this once, as root, on the first boot. Every step checks the current
# state first, so a second run changes nothing and prints "0 change(s)". The idempotency
# test re-runs it through SSM: sudo bash /var/lib/cloud/instance/scripts/part-001
#
# ec2.tf prepends the deployment settings (IMAGE_REPOSITORY, DEPLOY_TAG, SOURCE_REPOSITORY,
# S3_BUCKET, AWS_REGION) and the gzipped, base64-encoded deploy-agent.sh (DEPLOY_AGENT_GZ_B64).
set -euo pipefail
: "${IMAGE_REPOSITORY:?}" "${DEPLOY_TAG:?}" "${SOURCE_REPOSITORY:?}" "${S3_BUCKET:?}"
: "${AWS_REGION:?}" "${DEPLOY_AGENT_GZ_B64:?}"
export DEBIAN_FRONTEND=noninteractive

APP_USER=app
APP_HOME=/opt/app

changes=0
changed() {
  echo "harden: changed: $*"
  changes=$((changes + 1))
}

# apt-daily may hold the dpkg lock right after boot; wait for it instead of failing.
apt_get() {
  apt-get -q -o DPkg::Lock::Timeout=600 "$@"
}

# Writes stdin to a file only when the content differs. Returns 0 when the file changed.
write_if_changed() {
  local path=$1 mode=$2 tmp
  tmp=$(mktemp)
  cat >"$tmp"
  if [[ -f $path ]] && cmp -s "$tmp" "$path"; then
    rm -f "$tmp"
    return 1
  fi
  install -D -m "$mode" "$tmp" "$path"
  rm -f "$tmp"
  return 0
}

# 1. Docker and the compose plugin from the Ubuntu archive (docker-compose-v2 is in universe).
missing=()
for pkg in docker.io docker-compose-v2 unattended-upgrades; do
  if ! dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q 'install ok installed'; then
    missing+=("$pkg")
  fi
done
if ((${#missing[@]})); then
  apt_get update
  apt_get install -y --no-install-recommends "${missing[@]}"
  changed "installed ${missing[*]}"
fi

# 2. Docker daemon defaults: bounded json-file logs, no privilege escalation in containers.
if write_if_changed /etc/docker/daemon.json 0644 <<'EOF'; then
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "no-new-privileges": true
}
EOF
  changed "/etc/docker/daemon.json"
  if systemctl is-active --quiet docker; then
    systemctl restart docker
  fi
fi

if ! systemctl is-enabled --quiet docker || ! systemctl is-active --quiet docker; then
  systemctl enable --now docker
  changed "docker service enabled and started"
fi

# 3. Service user that owns the compose project and .env (E05-07). No login shell.
#    Membership in the docker group is root-equivalent on the host (ADR-0031).
if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --home-dir "$APP_HOME" --shell /usr/sbin/nologin "$APP_USER"
  changed "user $APP_USER created"
fi
if ! id -nG "$APP_USER" | tr ' ' '\n' | grep -qx docker; then
  usermod -aG docker "$APP_USER"
  changed "user $APP_USER added to docker group"
fi
if [[ $(stat -c '%U:%G %a' "$APP_HOME") != "$APP_USER:$APP_USER 750" ]]; then
  chown "$APP_USER:$APP_USER" "$APP_HOME"
  chmod 0750 "$APP_HOME"
  changed "$APP_HOME owner and mode"
fi

# 4. No SSH server: access is only through SSM (ADR-0024). Ubuntu 24.04 starts sshd through
#    socket activation, so both units are stopped and masked.
for unit in ssh.socket ssh.service; do
  if systemctl list-unit-files "$unit" --no-legend | grep -q .; then
    if [[ $(systemctl is-enabled "$unit" 2>/dev/null || true) != masked ]]; then
      systemctl disable --now "$unit" >/dev/null 2>&1 || true
      systemctl mask "$unit" >/dev/null
      changed "$unit stopped and masked"
    fi
    if systemctl is-active --quiet "$unit"; then
      systemctl stop "$unit"
      changed "$unit stopped"
    fi
  fi
done

# 5. Automatic security updates without automatic reboot. The allowed origins stay at the
#    Ubuntu default in 50unattended-upgrades; this file only makes the schedule explicit.
if write_if_changed /etc/apt/apt.conf.d/20auto-upgrades 0644 <<'EOF'; then
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
  changed "/etc/apt/apt.conf.d/20auto-upgrades"
fi
if write_if_changed /etc/apt/apt.conf.d/52devsecops-unattended-upgrades 0644 <<'EOF'; then
// ADR-0031: the host is ephemeral; patches apply without a reboot.
Unattended-Upgrade::Automatic-Reboot "false";
EOF
  changed "/etc/apt/apt.conf.d/52devsecops-unattended-upgrades"
fi

# 6. No host firewall: the security group is the only filter, because published Docker
#    ports bypass ufw rules (ADR-0031).
if command -v ufw >/dev/null && ufw status | grep -q '^Status: active'; then
  ufw --force disable >/dev/null
  changed "ufw disabled"
fi

# 7. Secrets and settings of the app, generated once and never leaving the instance (ADR-0033).
#    The public address comes from IMDSv2 and is the only allowed CORS origin.
if [[ ! -f $APP_HOME/.env ]]; then
  imds_token=$(curl -fsS -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
    http://169.254.169.254/latest/api/token)
  imds() {
    curl -fsS -H "X-aws-ec2-metadata-token: $imds_token" "http://169.254.169.254/latest/meta-data/$1"
  }
  public_ip=$(imds public-ipv4)
  public_dns=$(imds public-hostname)
  secret() { openssl rand -hex "$1"; }
  (
    umask 077
    cat >"$APP_HOME/.env" <<EOF
# Generated by user-data.sh on first boot (ADR-0033). Exists only on this instance.
POSTGRES_PASSWORD=$(secret 32)
JWT_SECRET=$(secret 48)
JWT_EXPIRE_MINUTES=30
CORS_ORIGINS=http://$public_dns,http://$public_ip
S3_BUCKET=$S3_BUCKET
AWS_DEFAULT_REGION=$AWS_REGION
LOG_LEVEL=INFO
SEED_ALICE_PASSWORD=$(secret 24)
SEED_BOB_PASSWORD=$(secret 24)
SEED_ADMIN_PASSWORD=$(secret 24)
EOF
  )
  chown "$APP_USER:$APP_USER" "$APP_HOME/.env"
  changed "$APP_HOME/.env generated"
fi

# 8. Deploy agent: tag in GHCR -> digest -> docker compose, about once a minute (ADR-0033).
if write_if_changed /etc/ticketing/deploy.conf 0644 <<EOF; then
IMAGE_REPOSITORY=$IMAGE_REPOSITORY
DEPLOY_TAG=$DEPLOY_TAG
SOURCE_REPOSITORY=$SOURCE_REPOSITORY
EOF
  changed "/etc/ticketing/deploy.conf"
fi
if base64 -d <<<"$DEPLOY_AGENT_GZ_B64" | gunzip | write_if_changed /usr/local/bin/ticketing-deploy 0755; then
  changed "/usr/local/bin/ticketing-deploy"
fi
if write_if_changed /etc/systemd/system/ticketing-deploy.service 0644 <<EOF; then
[Unit]
Description=Pull-model deploy of the app (ADR-0033)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_HOME
ExecStart=/usr/local/bin/ticketing-deploy
TimeoutStartSec=15min
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$APP_HOME
EOF
  changed "/etc/systemd/system/ticketing-deploy.service"
  systemctl daemon-reload
fi
if write_if_changed /etc/systemd/system/ticketing-deploy.timer 0644 <<'EOF'; then
[Unit]
Description=Check GHCR for a new app image about once a minute (ADR-0033)

[Timer]
OnActiveSec=10s
OnUnitInactiveSec=1min
AccuracySec=5s

[Install]
WantedBy=timers.target
EOF
  changed "/etc/systemd/system/ticketing-deploy.timer"
  systemctl daemon-reload
fi
if ! systemctl is-enabled --quiet ticketing-deploy.timer || ! systemctl is-active --quiet ticketing-deploy.timer; then
  systemctl enable --now ticketing-deploy.timer
  changed "ticketing-deploy.timer enabled and started"
fi

echo "harden: done, ${changes} change(s)"
