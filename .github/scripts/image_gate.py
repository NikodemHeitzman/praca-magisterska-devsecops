"""Gate of the image-scan job: applies the ADR-0042 threshold to the Trivy image JSON report.

Thresholds (ADR-0042, D5a; ADR-0048):
- vulnerabilities: MEDIUM, HIGH and CRITICAL with an available fix (status `fixed`) block;
  LOW, UNKNOWN and vulnerabilities without a fix are kept in the report only;
- secrets (in image layers or in the image configuration): every finding blocks, as in the
  secrets job (Gitleaks has no levels).

Exceptions come only from .github/gate-exceptions.yaml (D6): tool `trivy-image`,
- vulnerability: rule = the vulnerability id, path = `<package type>/<source package>`, e.g.
  `debian/glibc` (one entry per CVE and source package, not per binary package: libc6 and
  libc-bin share the glibc fixes);
- secret: rule = the Trivy secret rule id, path = the file in the image, as in the report, or
  `image-config` for the image configuration (ENV, commands in the history).

Fail closed: a missing or unreadable report, a report of another artifact type, a report without
a detected operating system (no OS packages scanned), or missing vulnerability database metadata
fail the gate (exit 2). The database is pinned by digest (ADR-0048, M3); its metadata go to the
job summary next to the result.

Usage: python image_gate.py --trivy reports/trivy-image.json --db-metadata reports/trivy-db.json \
           --exceptions .github/gate-exceptions.yaml
Exit code: 0 pass, 1 blocking findings, 2 unusable input.
"""

import argparse
import json
import os
import sys

import yaml

TOOL = "trivy-image"
EXCEPTION_FIELDS = ("tool", "rule", "path", "reason", "added")
BLOCKING_SEVERITIES = ("MEDIUM", "HIGH", "CRITICAL")
IMAGE_CONFIG = "image-config"


class InputError(Exception):
    pass


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path}: {e}") from e


def load_report(path):
    report = load_json(path)
    if not isinstance(report, dict) or report.get("ArtifactType") != "container_image":
        raise InputError(f"{path}: not a Trivy container image report")
    if not isinstance(report.get("Results"), list):
        raise InputError(f"{path}: no 'Results' list")
    os_info = (report.get("Metadata") or {}).get("OS") or {}
    if not os_info.get("Family"):
        raise InputError(f"{path}: no operating system detected, OS packages were not scanned")
    return report


def load_db_metadata(path):
    meta = load_json(path)
    if not isinstance(meta, dict) or not meta.get("UpdatedAt") or not meta.get("Repository"):
        raise InputError(f"{path}: no 'UpdatedAt' or 'Repository' of the vulnerability database")
    return meta


def load_exceptions(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise InputError(f"{path}: {e}") from e
    entries = (data or {}).get("exceptions") or []
    for i, entry in enumerate(entries):
        missing = [k for k in EXCEPTION_FIELDS if not str(entry.get(k) or "").strip()]
        if missing:
            raise InputError(f"{path}: entry {i} lacks {', '.join(missing)}")
    return [e for e in entries if e["tool"] == TOOL]


def is_fixed(vuln):
    status = vuln.get("Status")
    if status:
        return status == "fixed"
    return bool(vuln.get("FixedVersion"))


def findings(report):
    """Gate candidates, unique by (rule, path), and counts for the summary."""
    unique = {}
    counts = {"vulnerabilities": 0, "secrets": 0, "above threshold (package entries)": 0}
    for result in report["Results"]:
        sources = {
            p.get("ID"): p.get("SrcName") or p.get("Name") for p in result.get("Packages") or []
        }
        for vuln in result.get("Vulnerabilities") or []:
            counts["vulnerabilities"] += 1
            if vuln.get("Severity") not in BLOCKING_SEVERITIES or not is_fixed(vuln):
                continue
            counts["above threshold (package entries)"] += 1
            source = sources.get(vuln.get("PkgID")) or vuln["PkgName"]
            key = (vuln["VulnerabilityID"], f"{result.get('Type')}/{source}")
            entry = unique.setdefault(
                key,
                {
                    "kind": "vulnerability",
                    "rule": key[0],
                    "path": key[1],
                    "severity": vuln["Severity"],
                    "packages": [],
                },
            )
            entry["packages"].append(
                f"{vuln['PkgName']} {vuln.get('InstalledVersion')} -> {vuln.get('FixedVersion')}"
            )
        # Secrets in the image configuration (ENV, RUN in the history) have the scanned archive
        # as their target, which depends on where the job puts it; they get a fixed path.
        target = result.get("Target")
        if target == report.get("ArtifactName"):
            target = IMAGE_CONFIG
        for secret in result.get("Secrets") or []:
            counts["secrets"] += 1
            key = (secret.get("RuleID"), target)
            unique.setdefault(
                key,
                {
                    "kind": "secret",
                    "rule": key[0],
                    "path": key[1],
                    "severity": secret.get("Severity"),
                    "packages": [],
                },
            )
    return list(unique.values()), counts


def summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trivy", required=True)
    parser.add_argument("--db-metadata", required=True)
    parser.add_argument("--exceptions", required=True)
    args = parser.parse_args()

    try:
        report = load_report(args.trivy)
        db = load_db_metadata(args.db_metadata)
        exceptions = load_exceptions(args.exceptions)
    except InputError as e:
        print(f"::error::image-scan gate input unusable: {e}")
        return 2

    found, counts = findings(report)
    used = set()
    blocking, excepted = [], []
    for f in found:
        match = next(
            (
                i
                for i, e in enumerate(exceptions)
                if e["rule"] == f["rule"] and e["path"] == f["path"]
            ),
            None,
        )
        if match is None:
            blocking.append(f)
        else:
            used.add(match)
            excepted.append(f)

    for i, e in enumerate(exceptions):
        if i not in used:
            print(f"::warning::unused exception {TOOL} {e['rule']} {e['path']}")
    for f in sorted(blocking, key=lambda x: (x["kind"], x["path"], x["rule"])):
        detail = "; ".join(f["packages"]) or "secret"
        print(f"::error::{f['kind']} {f['rule']} ({f['severity']}) in {f['path']}: {detail}")

    os_info = report["Metadata"]["OS"]
    summary(
        [
            "### Image scan gate (Trivy image)",
            "",
            f"Image `{report['Metadata'].get('ImageID')}`, "
            f"OS {os_info.get('Family')} {os_info.get('Name')}, "
            f"Trivy {report.get('Trivy', {}).get('Version')}, "
            f"vulnerability DB updated {db['UpdatedAt']} (`{db['Repository']}`)",
            "",
            "| | count |",
            "|---|---|",
            *(f"| {k} | {v} |" for k, v in counts.items()),
            f"| gate findings (unique rule, path) | {len(found)} |",
            f"| blocking | {len(blocking)} |",
            f"| excepted (gate-exceptions.yaml) | {len(excepted)} |",
            "",
            f"Result: **{'FAIL' if blocking else 'PASS'}**",
        ]
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
