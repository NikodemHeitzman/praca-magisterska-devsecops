#!/bin/bash
# Attestation check of an image in GHCR (docs/adr/0050-atestacje-i-weryfikacja-przed-wdrozeniem.md).
#
# Shared by the deploy agent on the instance (installed as /usr/local/bin/ticketing-verify,
# called by deploy-agent.sh for variant B) and by the `verify` job of devsecops-ci.yml, so CI
# tests the exact command the instance runs. No GitHub token and no registry login: the package
# is public and the attestations are stored in GHCR next to the image (push-to-registry); the
# script downloads the bundles anonymously and gh verifies them from disk.
#
#   verify-attestation.sh <image repository> <digest>
#   e.g. verify-attestation.sh ghcr.io/owner/repo sha256:...
#
# Environment:
#   SOURCE_REPOSITORY  owner/repo that built and attested the image (gh --repo)
#   SOURCE_REF         git ref the image was built from, e.g. refs/heads/exp/variant-b
#   SIGNER_WORKFLOW    workflow that signed the attestation (default: the reusable attest.yml)
#   GH                 path to gh (default: gh)
#
# Exit codes (B4, A4):
#   0   a provenance attestation exists and gh verified it
#   10  no provenance attestation for the digest yet: the caller waits (D3)
#   11  a provenance attestation exists but gh rejected it: the caller rejects the digest
#   1   registry or usage error: the caller retries later
set -euo pipefail

PROVENANCE_TYPE=https://slsa.dev/provenance/v1
OCI_INDEX=application/vnd.oci.image.index.v1+json

repository=${1:?image repository}
digest=${2:?digest}
: "${SOURCE_REPOSITORY:?}" "${SOURCE_REF:?}"
SIGNER_WORKFLOW=${SIGNER_WORKFLOW:-$SOURCE_REPOSITORY/.github/workflows/attest.yml}
GH=${GH:-gh}

if [[ ! $digest =~ ^sha256:([0-9a-f]{64})$ ]]; then
  echo "verify: invalid digest '$digest'" >&2
  exit 1
fi
hex=${BASH_REMATCH[1]}
registry=${repository%%/*}
path=${repository#*/}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# 1. Is there a provenance attestation? Two places, because @sigstore/oci uses the referrers
# API when the registry supports it and otherwise an index under the tag sha256-<hex>
# (OCI Referrers Tag Schema). An empty list or a 404 in one place is not an answer on its own.
# GHCR has no referrers API (404) and uses the tag (checked 2026-11-27).
token=$(curl -fsS --max-time 20 "https://$registry/token?scope=repository:$path:pull" |
  python3 -c 'import json, sys; print(json.load(sys.stdin)["token"])') || {
  echo "verify: no anonymous token from $registry" >&2
  exit 1
}

fetch_index() { # <url> <output file>; prints the HTTP status
  curl -sS --max-time 20 -o "$2" -w '%{http_code}' \
    -H "Authorization: Bearer $token" -H "Accept: $OCI_INDEX" "$1"
}

found=()
for source in referrers tag; do
  case $source in
    referrers) url="https://$registry/v2/$path/referrers/$digest" ;;
    tag) url="https://$registry/v2/$path/manifests/sha256-$hex" ;;
  esac
  code=$(fetch_index "$url" "$work/$source.json") || code=000
  case $source:$code in
    *:200) found+=("$work/$source.json") ;;
    *:404) ;;
    # A registry without the referrers API may also answer 400, 405 or 501 there.
    referrers:400 | referrers:405 | referrers:501) ;;
    *)
      echo "verify: registry answered HTTP $code for the $source lookup" >&2
      exit 1
      ;;
  esac
done

# 2. Download the provenance bundles: index entry -> bundle manifest -> bundle blob, each bundle
# as one line of a JSON lines file. gh only runs without a login for a bundle on disk (--bundle);
# --bundle-from-oci always asks for `gh auth login` (gh 2.105.0, verify.go; ADR-0050, B4a).
count=0
if ((${#found[@]})); then
  count=$(python3 - "$PROVENANCE_TYPE" "https://$registry/v2/$path" "$token" \
    "$work/bundles.jsonl" "${found[@]}" <<'PY'
import json, sys, urllib.request
wanted, base, token, out, files = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
BUNDLE = "application/vnd.dev.sigstore.bundle"

def get(url, accept):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": accept})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

digests = []
for name in files:
    with open(name) as f:
        index = json.load(f)
    for m in index.get("manifests") or []:
        if (m.get("annotations") or {}).get("dev.sigstore.bundle.predicateType") == wanted:
            if m["digest"] not in digests:
                digests.append(m["digest"])
with open(out, "w") as f:
    for d in digests:
        manifest = json.loads(get(f"{base}/manifests/{d}", "application/vnd.oci.image.manifest.v1+json"))
        layers = [l for l in manifest.get("layers") or [] if l.get("mediaType", "").startswith(BUNDLE)]
        if len(layers) != 1:
            raise SystemExit(f"bundle manifest {d} has {len(layers)} bundle layers")
        bundle = json.loads(get(f"{base}/blobs/{layers[0]['digest']}", "*/*"))
        f.write(json.dumps(bundle, separators=(",", ":")) + "\n")
print(len(digests))
PY
  ) || {
    echo "verify: could not read the attestation index or download a bundle" >&2
    exit 1
  }
fi
if ((count == 0)); then
  echo "verify: no provenance attestation for $repository@$digest"
  exit 10
fi

# 3. Verify them. gh checks the Sigstore signature and transparency log entry, the image digest
# (resolved anonymously from oci://), the repository, the signer workflow (SLSA Build L3
# recipe, docs/notes/slsa.md 3.3), the source ref and a GitHub-hosted runner.
if "$GH" attestation verify "oci://$repository@$digest" --bundle "$work/bundles.jsonl" \
  --repo "$SOURCE_REPOSITORY" --signer-workflow "$SIGNER_WORKFLOW" \
  --source-ref "$SOURCE_REF" --deny-self-hosted-runners \
  --format json >"$work/result.json"; then
  echo "verify: provenance of $repository@$digest verified (signer $SIGNER_WORKFLOW, ref $SOURCE_REF)"
  exit 0
fi
echo "verify: provenance attestation of $repository@$digest REJECTED by gh" >&2
exit 11
