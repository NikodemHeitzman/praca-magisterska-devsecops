"""Gate of the sast job: applies the ADR-0042 thresholds to the Semgrep and Bandit JSON reports.

Thresholds (ADR-0042, D5; ADR-0045, T7):
- Semgrep: every severity except INFO fails, including LOW and any unknown value (fail closed).
- Bandit: every severity (LOW and up) fails when confidence is MEDIUM or HIGH; confidence LOW
  passes; any unknown confidence fails (fail closed).

Exceptions come only from .github/gate-exceptions.yaml (D6, T8); `# nosec` and `# nosemgrep`
are already disabled in the scan (D13). Partial parse errors listed in a report do not fail the
gate but are counted (T5); a missing or unreadable report fails it.

Usage: python sast_gate.py --semgrep reports/semgrep.json --bandit reports/bandit.json \
           --exceptions .github/gate-exceptions.yaml
Exit code: 0 pass, 1 blocking findings, 2 unusable input.
"""

import argparse
import json
import os
import sys

import yaml

SEMGREP_PASS_SEVERITIES = {"INFO"}
BANDIT_PASS_CONFIDENCES = {"LOW"}
EXCEPTION_FIELDS = ("tool", "rule", "path", "reason", "added")


class InputError(Exception):
    pass


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path}: {e}") from e
    if not isinstance(report.get("results"), list):
        raise InputError(f"{path}: no 'results' list")
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
    return {(e["tool"], e["rule"], e["path"]): e for e in entries}


def semgrep_findings(report):
    for r in report["results"]:
        severity = r.get("extra", {}).get("severity")
        yield {
            "tool": "semgrep",
            "rule": r["check_id"],
            "path": r["path"],
            "line": r["start"]["line"],
            "level": str(severity),
            "blocks": severity not in SEMGREP_PASS_SEVERITIES,
        }


def bandit_findings(report):
    for r in report["results"]:
        confidence = r.get("issue_confidence")
        yield {
            "tool": "bandit",
            "rule": r["test_id"],
            "path": r["filename"],
            "line": r["line_number"],
            "level": f"{r.get('issue_severity')}/{confidence}",
            # anything but LOW confidence fails, unknown values included
            "blocks": confidence not in BANDIT_PASS_CONFIDENCES,
        }


def summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--semgrep", required=True)
    parser.add_argument("--bandit", required=True)
    parser.add_argument("--exceptions", required=True)
    args = parser.parse_args()

    try:
        semgrep = load_json(args.semgrep)
        bandit = load_json(args.bandit)
        exceptions = load_exceptions(args.exceptions)
    except InputError as e:
        print(f"::error::sast gate input unusable: {e}")
        return 2

    findings = list(semgrep_findings(semgrep)) + list(bandit_findings(bandit))
    used = set()
    blocking, excepted, below = [], [], []
    for f in findings:
        key = (f["tool"], f["rule"], f["path"])
        if not f["blocks"]:
            below.append(f)
        elif key in exceptions:
            used.add(key)
            excepted.append(f)
        else:
            blocking.append(f)

    parse_errors = {
        "semgrep": len(semgrep.get("errors") or []),
        "bandit": len(bandit.get("errors") or []),
    }
    for tool, n in parse_errors.items():
        if n:
            print(f"::warning::{tool} reported {n} partial error(s); see the report artifact")
    for key in exceptions:
        if key[0] in ("semgrep", "bandit") and key not in used:
            print(f"::warning::unused exception {key[0]} {key[1]} {key[2]}")
    for f in blocking:
        print(f"::error file={f['path']},line={f['line']}::{f['tool']} {f['rule']} ({f['level']})")

    def row(name, group):
        semgrep_n = sum(f["tool"] == "semgrep" for f in group)
        bandit_n = sum(f["tool"] == "bandit" for f in group)
        return f"| {name} | {semgrep_n} | {bandit_n} |"

    summary(
        [
            "### SAST gate",
            "",
            "| | Semgrep | Bandit |",
            "|---|---|---|",
            row("findings", findings),
            row("blocking", blocking),
            row("excepted (gate-exceptions.yaml)", excepted),
            row("below threshold", below),
            f"| partial errors | {parse_errors['semgrep']} | {parse_errors['bandit']} |",
            "",
            f"Result: **{'FAIL' if blocking else 'PASS'}**",
        ]
    )
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
