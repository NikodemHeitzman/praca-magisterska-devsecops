#!/bin/bash
# Host bootstrap and hardening for the app instance (ADR-0031).
#
# cloud-init runs this once, as root, on the first boot. Every step checks the current
# state first, so a second run changes nothing and prints "0 change(s)". The idempotency
# test re-runs it through SSM: sudo bash /var/lib/cloud/instance/scripts/part-001
set -euo pipefail
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

echo "harden: done, ${changes} change(s)"
