#!/bin/bash
# Shows the state of the pull-model deployment through SSM Run Command (ADR-0033, E05-07).
# Run it where the caller may use ssm:SendCommand, e.g. AWS CloudShell in eu-north-1:
#   bash check-deploy.sh                       # deployment history, agent log, containers
#   SHOW_SEED_PASSWORDS=1 bash check-deploy.sh # also the generated passwords of the seed accounts
# The deployed version is also public: curl http://<public DNS>/version
set -euo pipefail

# CloudShell's AWS CLI pipes long output through less; print everything at once instead.
export AWS_PAGER=""

REGION=${REGION:-eu-north-1}
NAME=${NAME:-devsecops-thesis-app}
SHOW_SEED_PASSWORDS=${SHOW_SEED_PASSWORDS:-0}

iid=$(aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag:Name,Values=$NAME" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)
if [[ -z $iid || $iid == None ]]; then
  echo "no running instance tagged Name=$NAME in $REGION" >&2
  exit 1
fi
echo "instance: $iid"

read -r -d '' remote <<'EOF' || true
set -u
section() { printf '\n=== %s ===\n' "$1"; }
section "deploy settings"
cat /etc/ticketing/deploy.conf
section "deployments (state/deployments.log)"
cat /opt/app/state/deployments.log 2>/dev/null || echo "no deployment yet"
echo "current: $(cat /opt/app/state/current 2>/dev/null || echo none)"
echo "failed:  $(cat /opt/app/state/failed 2>/dev/null || echo none)"
section "agent log (last 30 lines)"
journalctl -u ticketing-deploy --no-pager -n 30 -o short-iso
systemctl list-timers ticketing-deploy.timer --no-pager
section "containers"
cd /opt/app && sudo -u app env $(cat release.env 2>/dev/null) \
  docker compose -f compose.yaml -f compose.aws.yaml ps --all 2>/dev/null || echo "no stack"
section "version"
curl -fsS http://127.0.0.1/version; echo
curl -fsS http://127.0.0.1/health; echo
EOF
if [[ $SHOW_SEED_PASSWORDS == 1 ]]; then
  remote+=$'\nsection "seed accounts"\ngrep "^SEED_" /opt/app/.env'
fi

params=$(jq -n --arg c "$remote" '{commands: [$c]}')
cid=$(aws ssm send-command --region "$REGION" --instance-ids "$iid" \
  --document-name AWS-RunShellScript --comment "E05-07 deploy check" \
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
