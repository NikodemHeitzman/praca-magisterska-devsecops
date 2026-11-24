"""Gate of the iac job: ADR-0042 thresholds on the Checkov, Trivy config and hadolint reports.

Thresholds (ADR-0042, D5, D5a, D7; ADR-0047):
- Checkov: every failed check fails (Checkov without the platform reports no severity). A check
  suppressed in code (`#checkov:skip`, listed in skipped_checks) fails as well (D13).
- Trivy config: every failed misconfiguration of severity LOW and up fails; UNKNOWN only reports.
- hadolint: level `error` fails; `warning`, `info` and `style` only report. Inline
  `# hadolint ignore=` pragmas are disabled in the scan (--disable-ignore-pragma).

Beyond the reports (ADR-0047):
- I3: a `trivy:ignore` comment in a scanned file fails, because Trivy drops such findings from its
  report without a trace and has no option to disable the comments (D13).
- I4: a scanner configuration file anywhere in the repository fails (.checkov.yaml, .hadolint.yaml,
  trivy.yaml, .trivyignore and their variants): scanner options live only in the workflow.
Both are never excepted.

Exceptions come only from .github/gate-exceptions.yaml (D6, T8): tool + rule + path. A missing or
unreadable report, a report without one of the expected scan types (Terraform and Dockerfile), or
a file that Checkov could not parse fails the gate (fail closed).

Usage: python iac_gate.py --checkov reports/checkov.json --trivy reports/trivy-config.json \
           --hadolint reports/hadolint.json --exceptions .github/gate-exceptions.yaml \
           --scan-path infra/terraform --scan-path app/Dockerfile [--repo-root .]
Exit code: 0 pass, 1 blocking findings, 2 unusable input.
"""

import argparse
import json
import os
import re
import sys

import yaml

TRIVY_PASS_SEVERITIES = {"UNKNOWN"}
HADOLINT_BLOCK_LEVELS = {"error"}
EXPECTED_SCAN_TYPES = {"terraform", "dockerfile"}
EXCEPTION_FIELDS = ("tool", "rule", "path", "reason", "added")
TOOLS = ("checkov", "trivy-config", "hadolint")
CONFIG_FILES = {
    ".checkov.yaml",
    ".checkov.yml",
    ".hadolint.yaml",
    ".hadolint.yml",
    "trivy.yaml",
    "trivy.yml",
    ".trivyignore",
    ".trivyignore.yaml",
}
TRIVY_IGNORE = re.compile(r"trivy:ignore")
SKIPPED_DIRS = {".git", ".terraform", ".venv", "node_modules"}


class InputError(Exception):
    pass


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path}: {e}") from e


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


def checkov_findings(path):
    data = load_json(path)
    reports = data if isinstance(data, list) else [data]
    seen, parse_errors, findings = set(), [], []
    for r in reports:
        if not isinstance(r, dict) or not isinstance(r.get("results"), dict):
            raise InputError(f"{path}: unexpected report structure")
        seen.add(r.get("check_type"))
        results = r["results"]
        parse_errors += results.get("parsing_errors") or []
        for key, level in (("failed_checks", "failed"), ("skipped_checks", "suppressed in code")):
            for c in results.get(key) or []:
                findings.append(
                    {
                        "tool": "checkov",
                        "rule": c["check_id"],
                        "path": c["repo_file_path"].lstrip("/"),
                        "line": (c.get("file_line_range") or [1])[0],
                        "level": level,
                        "blocks": True,
                    }
                )
    missing = EXPECTED_SCAN_TYPES - seen
    if missing:
        raise InputError(f"{path}: no {', '.join(sorted(missing))} results (nothing scanned?)")
    if parse_errors:
        raise InputError(f"{path}: Checkov could not parse {', '.join(sorted(parse_errors))}")
    return findings


def trivy_findings(path):
    data = load_json(path)
    if not isinstance(data, dict) or data.get("SchemaVersion") != 2:
        raise InputError(f"{path}: not a Trivy JSON report (SchemaVersion 2)")
    results = data.get("Results") or []
    seen = {r.get("Type") for r in results}
    missing = EXPECTED_SCAN_TYPES - seen
    if missing:
        raise InputError(f"{path}: no {', '.join(sorted(missing))} results (nothing scanned?)")
    findings = []
    for r in results:
        for m in r.get("Misconfigurations") or []:
            if m.get("Status") != "FAIL":
                continue
            severity = m.get("Severity")
            findings.append(
                {
                    "tool": "trivy-config",
                    "rule": m["ID"],
                    "path": r["Target"],
                    "line": (m.get("CauseMetadata") or {}).get("StartLine") or 1,
                    "level": str(severity),
                    # anything but UNKNOWN fails, unexpected values included
                    "blocks": severity not in TRIVY_PASS_SEVERITIES,
                }
            )
    return findings


def hadolint_findings(path):
    data = load_json(path)
    if not isinstance(data, list):
        raise InputError(f"{path}: not a hadolint JSON report (list)")
    return [
        {
            "tool": "hadolint",
            "rule": h["code"],
            "path": h["file"],
            "line": h.get("line") or 1,
            "level": str(h.get("level")),
            "blocks": h.get("level") in HADOLINT_BLOCK_LEVELS,
        }
        for h in data
    ]


def walk_files(root, rel):
    full = os.path.join(root, rel)
    if os.path.isfile(full):
        yield rel
        return
    if not os.path.isdir(full):
        raise InputError(f"scan path {rel} does not exist")
    for dirpath, dirnames, filenames in os.walk(full):
        dirnames[:] = [d for d in dirnames if d != ".terraform"]
        for name in filenames:
            yield os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")


def trivy_ignore_comments(root, scan_paths):
    """I3: trivy:ignore comments in scanned files; never excepted."""
    for rel in scan_paths:
        for path in walk_files(root, rel):
            try:
                with open(os.path.join(root, path), encoding="utf-8", errors="replace") as f:
                    for n, line in enumerate(f, 1):
                        if TRIVY_IGNORE.search(line):
                            yield {"path": path, "line": n}
            except OSError as e:
                raise InputError(f"{path}: {e}") from e


def scanner_config_files(root):
    """I4: scanner configuration files anywhere in the repository; never excepted."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIPPED_DIRS]
        for name in filenames:
            if name in CONFIG_FILES:
                yield os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")


def summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkov", required=True)
    parser.add_argument("--trivy", required=True)
    parser.add_argument("--hadolint", required=True)
    parser.add_argument("--exceptions", required=True)
    parser.add_argument("--scan-path", action="append", required=True, dest="scan_paths")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    try:
        findings = (
            checkov_findings(args.checkov)
            + trivy_findings(args.trivy)
            + hadolint_findings(args.hadolint)
        )
        exceptions = load_exceptions(args.exceptions)
        ignores = list(trivy_ignore_comments(args.repo_root, args.scan_paths))
        configs = sorted(scanner_config_files(args.repo_root))
    except InputError as e:
        print(f"::error::iac gate input unusable: {e}")
        return 2

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

    for key in exceptions:
        if key[0] in TOOLS and key not in used:
            print(f"::warning::unused exception {key[0]} {key[1]} {key[2]}")
    for f in blocking:
        print(f"::error file={f['path']},line={f['line']}::{f['tool']} {f['rule']} ({f['level']})")
    for i in ignores:
        print(f"::error file={i['path']},line={i['line']}::trivy:ignore comment (D13, ADR-0047 I3)")
    for c in configs:
        print(f"::error file={c}::scanner configuration file (ADR-0047 I4)")

    def row(name, group):
        cells = [str(sum(f["tool"] == t for f in group)) for t in TOOLS]
        return f"| {name} | " + " | ".join(cells) + " |"

    suppressed = [f for f in findings if f["level"] == "suppressed in code"]
    failed = bool(blocking or ignores or configs)
    summary(
        [
            "### IaC gate",
            "",
            "| | Checkov | Trivy config | hadolint |",
            "|---|---|---|---|",
            row("findings", findings),
            row("blocking", blocking),
            row("excepted (gate-exceptions.yaml)", excepted),
            row("below threshold", below),
            row("suppressed in code (blocking, D13)", suppressed),
            "",
            f"`trivy:ignore` comments (blocking, I3): {len(ignores)}  ",
            f"Scanner configuration files (blocking, I4): {len(configs)}",
            "",
            f"Result: **{'FAIL' if failed else 'PASS'}**",
        ]
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
