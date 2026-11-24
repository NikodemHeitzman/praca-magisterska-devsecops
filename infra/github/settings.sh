#!/usr/bin/env bash
# GitHub platform settings as code (docs/adr/0043-utwardzenie-workflowow.md, H12;
# inventory and rationale: docs/ustawienia-github.md).
#
#   infra/github/settings.sh show    print the current settings (read-only)
#   infra/github/settings.sh apply   apply the settings below and the rulesets in rulesets/
#
# Runs locally with the author's `gh` login (repository admin). No token with admin rights is
# stored in CI. Compare `show` with this file and rulesets/ to detect drift.
set -euo pipefail

cd "$(dirname "$0")"
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
api="repos/$repo"

# Third-party actions allowed besides GitHub-owned ones (actions/*, github/*), H7.
# Each new third-party action needs an entry here; versions are pinned by SHA in the workflows.
allowed_patterns='["astral-sh/setup-uv@*"]'

get() { gh api "$@"; echo; }

show() {
  echo "## repository security (secret scanning, push protection, Dependabot security updates)"
  get "$api" --jq '.security_and_analysis'
  echo "## Dependabot alerts (204 = enabled, 404 = disabled)"
  gh api -i "$api/vulnerability-alerts" 2>/dev/null | head -n 1 || true
  echo "## actions permissions"
  get "$api/actions/permissions"
  echo "## selected actions"
  if [ "$(gh api "$api/actions/permissions" --jq .allowed_actions)" = selected ]; then
    get "$api/actions/permissions/selected-actions"
  else
    echo "n/a (allowed_actions is not 'selected')"
  fi
  echo "## default GITHUB_TOKEN permissions"
  get "$api/actions/permissions/workflow"
  echo "## fork pull request approval"
  get "$api/actions/permissions/fork-pr-contributor-approval"
  echo "## rulesets"
  for id in $(gh api "$api/rulesets" --jq '.[].id'); do
    get "$api/rulesets/$id" --jq '{name, target, enforcement, bypass_actors, conditions, rules}'
  done
}

apply_ruleset() {
  local file=$1 name id
  name=$(sed -n 's/^  "name": "\(.*\)",$/\1/p' "$file")
  id=$(gh api "$api/rulesets" --jq ".[] | select(.name == \"$name\") | .id")
  if [ -n "$id" ]; then
    gh api --method PUT "$api/rulesets/$id" --input "$file" --jq '"updated ruleset \(.name) (\(.id))"'
  else
    gh api --method POST "$api/rulesets" --input "$file" --jq '"created ruleset \(.name) (\(.id))"'
  fi
}

apply() {
  # B03: secret scanning with push protection. Non-provider (generic) patterns are not set here:
  # GitHub ignores them for a personal-account repository (S6, docs/adr/0044-skanowanie-sekretow.md).
  gh api --method PATCH "$api" --silent --input - <<'JSON'
{"security_and_analysis": {
  "secret_scanning": {"status": "enabled"},
  "secret_scanning_push_protection": {"status": "enabled"}}}
JSON
  # B04: Dependabot alerts and security updates (version updates: .github/dependabot.yml), H6.
  gh api --method PUT "$api/vulnerability-alerts" --silent
  gh api --method PUT "$api/automated-security-fixes" --silent

  # B05: read-only default token that cannot approve pull requests.
  gh api --method PUT "$api/actions/permissions/workflow" --silent --input - <<'JSON'
{"default_workflow_permissions": "read", "can_approve_pull_request_reviews": false}
JSON
  # B05: every external contributor needs approval before workflows run (PROTOCOL.md, rule 4), H9.
  gh api --method PUT "$api/actions/permissions/fork-pr-contributor-approval" --silent --input - <<'JSON'
{"approval_policy": "all_external_contributors"}
JSON
  # H7: only GitHub-owned and listed actions, and only pinned to a full commit SHA.
  gh api --method PUT "$api/actions/permissions" --silent --input - <<'JSON'
{"enabled": true, "allowed_actions": "selected", "sha_pinning_required": true}
JSON
  gh api --method PUT "$api/actions/permissions/selected-actions" --silent --input - <<JSON
{"github_owned_allowed": true, "verified_allowed": false, "patterns_allowed": $allowed_patterns}
JSON

  # B02 and tag protection: H1-H3, H11, H13.
  for file in rulesets/*.json; do
    apply_ruleset "$file"
  done
}

case "${1:-}" in
  show) show ;;
  apply) apply ;;
  *) echo "usage: $0 show|apply" >&2; exit 2 ;;
esac
