#!/bin/bash
# Deploy agent of the pull model (docs/adr/0033-mechanizm-wdrozenia-pull.md).
#
# user-data.sh installs it as /usr/local/bin/ticketing-deploy; ticketing-deploy.timer runs it
# as the app user about once a minute. The pipeline has no AWS access (ADR-0032), so the
# instance asks GHCR which image the branch tag points to and deploys it by digest:
#   1. resolve DEPLOY_TAG to a digest (anonymous token, public package),
#   2. stop if the digest is already deployed, or already failed (wait for a new tag),
#   3. pull the image by digest and read the commit from its OCI revision label,
#   4. download compose.yaml and compose.aws.yaml from that commit,
#   5. docker compose up, then wait until /version reports the new image.
# Rollback = moving the tag back to an earlier digest (.github/workflows/rollback.yml).
set -euo pipefail

CONF=${DEPLOY_CONF:-/etc/ticketing/deploy.conf}
# shellcheck source=/dev/null
. "$CONF"
: "${IMAGE_REPOSITORY:?}" "${DEPLOY_TAG:?}" "${SOURCE_REPOSITORY:?}"

APP_HOME=${APP_HOME:-/opt/app}
STATE=$APP_HOME/state
HEALTH_TIMEOUT=${HEALTH_TIMEOUT:-180}
REGISTRY=${IMAGE_REPOSITORY%%/*}
IMAGE_PATH=${IMAGE_REPOSITORY#*/}
MANIFEST_TYPES="application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v2+json"

# stdout goes to journald (journalctl -u ticketing-deploy).
log() { echo "deploy: $*"; }

mkdir -p "$STATE" "$APP_HOME/releases"
cd "$APP_HOME"

# 1. Tag -> digest. One token request and one HEAD request per run; nothing is pulled here.
token=$(curl -fsS --max-time 20 "https://$REGISTRY/token?scope=repository:$IMAGE_PATH:pull" |
  python3 -c 'import json, sys; print(json.load(sys.stdin)["token"])')
headers=$(mktemp)
trap 'rm -f "$headers"' EXIT
code=$(curl -sS --max-time 20 -I -o "$headers" -w '%{http_code}' \
  -H "Authorization: Bearer $token" -H "Accept: $MANIFEST_TYPES" \
  "https://$REGISTRY/v2/$IMAGE_PATH/manifests/$DEPLOY_TAG")
if [[ $code == 404 ]]; then
  # Normal before the first publish from the branch; not a failure of the unit.
  [[ -f $STATE/no-tag ]] || log "no image tagged $DEPLOY_TAG in $IMAGE_REPOSITORY yet"
  touch "$STATE/no-tag"
  exit 0
fi
rm -f "$STATE/no-tag"
if [[ $code != 200 ]]; then
  log "registry answered HTTP $code for $IMAGE_REPOSITORY:$DEPLOY_TAG" >&2
  exit 1
fi
digest=$(tr -d '\r' <"$headers" | awk -F': ' 'tolower($1) == "docker-content-digest" { print $2 }')
if [[ ! $digest =~ ^sha256:[0-9a-f]{64}$ ]]; then
  log "no valid digest in the registry response: '$digest'" >&2
  exit 1
fi

# 2. Nothing new. A failed digest is not retried; the next tag move (or a rollback) is.
current=$(cat "$STATE/current" 2>/dev/null || true)
failed=$(cat "$STATE/failed" 2>/dev/null || true)
if [[ $digest == "$current" || $digest == "$failed" ]]; then
  exit 0
fi

image=$IMAGE_REPOSITORY@$digest
log "new image for $DEPLOY_TAG: $image (deployed: ${current:-none})"

record() {
  local result=$1 revision=$2
  printf '%s tag=%s image=%s revision=%s result=%s docker=%s compose=%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$DEPLOY_TAG" "$image" "$revision" "$result" \
    "$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo unknown)" \
    "$(docker compose version --short 2>/dev/null || echo unknown)" >>"$STATE/deployments.log"
}

fail() {
  log "FAILED: $1" >&2
  echo "$digest" >"$STATE/failed"
  record failed "${revision:-unknown}"
  exit 1
}

start=$(date +%s)

# 3. Pull by digest; the commit comes from the image, not from the branch head.
docker pull --quiet "$image" >/dev/null || fail "docker pull $image"
revision=$(docker image inspect --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}' "$image")
[[ $revision =~ ^[0-9a-f]{40}$ ]] || fail "image has no org.opencontainers.image.revision label with a commit SHA"

# 4. Compose files from the same commit as the image (public repository, no token).
release=$APP_HOME/releases/$revision
mkdir -p "$release"
for file in compose.yaml compose.aws.yaml; do
  curl -fsS --max-time 30 -o "$release/$file" \
    "https://raw.githubusercontent.com/$SOURCE_REPOSITORY/$revision/app/$file" ||
    fail "download app/$file at $revision"
  install -m 0640 "$release/$file" "$APP_HOME/$file"
done

# 5. Start the stack. migrate and seed run before app (depends_on in compose.yaml).
export APP_IMAGE=$image APP_REVISION=$revision
printf 'APP_IMAGE=%s\nAPP_REVISION=%s\n' "$image" "$revision" >"$APP_HOME/release.env"
docker compose -f compose.yaml -f compose.aws.yaml up --detach --remove-orphans --quiet-pull ||
  fail "docker compose up"

deadline=$(($(date +%s) + HEALTH_TIMEOUT))
until curl -fsS --max-time 5 http://127.0.0.1/version 2>/dev/null | grep -qF "\"$image\"" &&
  curl -fsS --max-time 5 -o /dev/null http://127.0.0.1/health 2>/dev/null; do
  (($(date +%s) < deadline)) || fail "/version or /health not confirmed within ${HEALTH_TIMEOUT}s"
  sleep 3
done

echo "$digest" >"$STATE/current"
rm -f "$STATE/failed"
record deployed "$revision"
log "deployed $image (revision $revision) in $(($(date +%s) - start))s"

# Old app images are not needed: a rollback pulls its digest again.
docker image prune --all --force --filter "label=org.opencontainers.image.source" >/dev/null || true
