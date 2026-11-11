#!/bin/bash
# Checks the hardened app instance through SSM Run Command (ADR-0031, E05-05).
# Run it where the caller may use ssm:SendCommand, e.g. AWS CloudShell in eu-north-1:
#   bash check-host.sh
# It waits for cloud-init, prints the first-boot log of user-data.sh, runs the script a
# second time (idempotency: expects "0 change(s)") and prints the resulting host state.
set -euo pipefail

# CloudShell's AWS CLI pipes long output through less; print everything at once instead.
export AWS_PAGER=""

REGION=${REGION:-eu-north-1}
NAME=${NAME:-devsecops-thesis-app}

iid=$(aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:Name,Values=$NAME" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)
if [[ -z $iid || $iid == None ]]; then
  echo "no running instance tagged Name=$NAME in $REGION" >&2
  exit 1
fi
echo "instance: $iid"

until [[ $(aws ssm describe-instance-information --region "$REGION" \
  --filters "Key=InstanceIds,Values=$iid" \
  --query 'InstanceInformationList[0].PingStatus' --output text) == Online ]]; do
  echo "waiting for the SSM agent..."
  sleep 10
done

read -r -d '' remote <<'EOF' || true
set -u
section() { printf '\n=== %s ===\n' "$1"; }
section "cloud-init"
cloud-init status --wait --long
cloud-init analyze show | grep -E 'Finished stage|config-scripts_user|Total Time'
section "first run (cloud-init-output.log)"
grep '^harden:' /var/log/cloud-init-output.log
section "second run"
start=$(date +%s)
bash /var/lib/cloud/instance/scripts/part-001
echo "second run seconds: $(( $(date +%s) - start ))"
section "packages"
dpkg-query -W -f='${Package} ${Version}\n' docker.io docker-compose-v2 containerd runc unattended-upgrades
docker version --format 'docker server {{.Server.Version}}'
docker compose version
section "docker daemon"
cat /etc/docker/daemon.json
systemctl is-enabled docker; systemctl is-active docker
section "service user"
id app
stat -c '%n %U:%G %a' /opt/app
getent passwd app
section "ssh"
for u in ssh.socket ssh.service; do echo "$u: $(systemctl is-enabled $u 2>&1) / $(systemctl is-active $u 2>&1)"; done
ss -Htlnp '( sport = :22 )' | grep . || echo "no listener on :22"
section "unattended-upgrades"
cat /etc/apt/apt.conf.d/20auto-upgrades
apt-config dump | grep -E '^Unattended-Upgrade::(Allowed-Origins|Automatic-Reboot)'
systemctl is-enabled apt-daily-upgrade.timer unattended-upgrades.service
section "firewall"
ufw status
section "ssm agent"
snap services amazon-ssm-agent
section "listeners"
ss -Htlnp
EOF

params=$(jq -n --arg c "$remote" '{commands: [$c]}')
cid=$(aws ssm send-command --region "$REGION" --instance-ids "$iid" \
  --document-name AWS-RunShellScript --comment "E05-05 host check" \
  --parameters "$params" --query 'Command.CommandId' --output text)
echo "command: $cid"

until status=$(aws ssm get-command-invocation --region "$REGION" --command-id "$cid" \
  --instance-id "$iid" --query Status --output text 2>/dev/null) &&
  [[ $status != Pending && $status != InProgress && $status != Delayed ]]; do
  sleep 5
done
echo "status: $status"
aws ssm get-command-invocation --region "$REGION" --command-id "$cid" --instance-id "$iid" \
  --query '[StandardOutputContent, StandardErrorContent]' --output text
