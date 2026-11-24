"""Gate of the sca job: applies the ADR-0042 threshold to the pip-audit JSON report.

pip-audit has no severity levels, so every known vulnerability fails (ADR-0042, D5; ADR-0046).
Exceptions come only from .github/gate-exceptions.yaml (D6, T8): tool `pip-audit`, rule = the
vulnerability id or any of its aliases (PYSEC, GHSA, CVE), path = the audited requirements file.

pip-audit exits 1 both on findings and on tool errors, and writes no report on an error, so the
gate trusts the report, not the exit code (fail closed): a missing or unreadable report, an empty
dependency list, or a dependency that could not be audited (`skip_reason`) fails the gate.

pip-audit 2.10.1 lists each vulnerability twice in the report (E07-05, cause unknown); the gate
counts unique (package, version, id) and reports the raw count next to it.

Usage: python sca_gate.py --pip-audit reports/pip-audit.json --path app/requirements.txt \
           --exceptions .github/gate-exceptions.yaml
Exit code: 0 pass, 1 blocking findings, 2 unusable input.
"""

import argparse
import json
import os
import sys

import yaml

TOOL = "pip-audit"
EXCEPTION_FIELDS = ("tool", "rule", "path", "reason", "added")


class InputError(Exception):
    pass


def load_report(path):
    try:
        with open(path, encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path}: {e}") from e
    deps = report.get("dependencies") if isinstance(report, dict) else None
    if not isinstance(deps, list) or not deps:
        raise InputError(f"{path}: no 'dependencies' or an empty list")
    skipped = [d for d in deps if "skip_reason" in d]
    if skipped:
        names = ", ".join(f"{d.get('name')} ({d['skip_reason']})" for d in skipped)
        raise InputError(f"{path}: not audited: {names}")
    return report


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


def findings(report):
    """Unique findings and the raw number of vulnerability entries in the report."""
    unique, raw = {}, 0
    for dep in report["dependencies"]:
        for vuln in dep.get("vulns") or []:
            raw += 1
            key = (dep["name"], dep["version"], vuln["id"])
            unique.setdefault(
                key,
                {
                    "package": dep["name"],
                    "version": dep["version"],
                    "id": vuln["id"],
                    "aliases": sorted(vuln.get("aliases") or []),
                    "fix_versions": vuln.get("fix_versions") or [],
                },
            )
    return list(unique.values()), raw


def summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip-audit", dest="report", required=True)
    parser.add_argument("--path", required=True, help="audited requirements file, as in exceptions")
    parser.add_argument("--exceptions", required=True)
    args = parser.parse_args()

    try:
        report = load_report(args.report)
        exceptions = load_exceptions(args.exceptions)
    except InputError as e:
        print(f"::error::sca gate input unusable: {e}")
        return 2

    found, raw = findings(report)
    used = set()
    blocking, excepted = [], []
    for f in found:
        ids = {f["id"], *f["aliases"]}
        match = next(
            (i for i, e in enumerate(exceptions) if e["path"] == args.path and e["rule"] in ids),
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
    for f in blocking:
        fix = ", ".join(f["fix_versions"]) or "none"
        aliases = ", ".join(f["aliases"]) or "-"
        print(
            f"::error file={args.path}::{f['package']} {f['version']} {f['id']} ({aliases}); "
            f"fixed in: {fix}"
        )

    summary(
        [
            "### SCA gate (pip-audit)",
            "",
            "| | count |",
            "|---|---|",
            f"| dependencies audited | {len(report['dependencies'])} |",
            f"| vulnerabilities (unique package, version, id) | {len(found)} |",
            f"| vulnerability entries in the report (raw) | {raw} |",
            f"| blocking | {len(blocking)} |",
            f"| excepted (gate-exceptions.yaml) | {len(excepted)} |",
            "",
            f"Result: **{'FAIL' if blocking else 'PASS'}**",
        ]
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
