"""Collect GitHub Actions run, job and step timings for the pipeline experiment (task E06-04).

Decisions: docs/adr/0039-skrypt-zbierajacy-czasy-potoku.md. Formulas: docs/metodyka.md, p. 3.2:
  T_wait (T_czek) = max completed_at(j) - min created_at(j)
  T_exec (T_wyk)  = max completed_at(j) - min started_at(j)
over the jobs of attempt 1 of a run (skipped jobs excluded); step duration d(s) = completed_at - started_at.

Input: a manifest CSV with columns run_id, variant (A|B), trigger (pr|main), seq, role
(warmup|measure|pilot). Output, next to the manifest unless --out is given:
  raw/<run_id>-run.json     run object, as returned by the API
  raw/<run_id>-jobs.json    jobs of attempt 1, as returned by the API (pages merged)
  raw/<run_id>-runner.json  runner version, image, cloud and region read from each job log
  runs.csv, jobs.csv, steps.csv

Usage:
  python experiment/scripts/collect_timings.py MANIFEST [--out DIR] [--repo OWNER/NAME]
  python experiment/scripts/collect_timings.py MANIFEST --from-raw   # recompute CSVs, no network

Token: GH_TOKEN or GITHUB_TOKEN, otherwise `gh auth token`. Standard library only.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

API = "https://api.github.com"
DEFAULT_REPO = "NikodemHeitzman/praca-magisterska-devsecops"
API_VERSION = "2022-11-28"

VARIANTS = {"A", "B"}
TRIGGERS = {"pr": "pull_request", "main": "push"}  # manifest trigger -> expected run event
ROLES = {"warmup", "measure", "pilot"}
MANIFEST_FIELDS = ["run_id", "variant", "trigger", "seq", "role"]

RUN_FIELDS = MANIFEST_FIELDS + [
    "event", "head_branch", "head_sha", "run_attempt", "conclusion", "jobs_counted",
    "first_job_created_at", "first_job_started_at", "last_job_completed_at",
    "t_wait_s", "t_exec_s", "first_job_queue_s",
]
JOB_FIELDS = MANIFEST_FIELDS + [
    "job_id", "job_name", "conclusion", "counted", "created_at", "started_at", "completed_at",
    "queue_s", "duration_s", "runner_name", "labels",
    "runner_version", "runner_image", "runner_image_version", "runner_cloud", "runner_region",
]
STEP_FIELDS = MANIFEST_FIELDS + [
    "job_id", "job_name", "step_number", "step_name", "conclusion",
    "started_at", "completed_at", "duration_s",
]

LOG_PREFIX = re.compile(r"^﻿?\d{4}-\d{2}-\d{2}T[\d:.]+Z ")


class CollectError(Exception):
    """Invalid input or data that cannot be used for the timing metrics."""


# ---------------------------------------------------------------- manifest


def read_manifest(path):
    """Read and validate the manifest; return a list of dicts in file order."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or set(MANIFEST_FIELDS) - set(reader.fieldnames):
            raise CollectError(f"{path}: header must contain {', '.join(MANIFEST_FIELDS)}")
        rows = [{k: (r[k] or "").strip() for k in MANIFEST_FIELDS} for r in reader]
    seen = set()
    for n, r in enumerate(rows, start=2):
        where = f"{path}:{n}"
        if not r["run_id"].isdigit():
            raise CollectError(f"{where}: run_id must be a number, got {r['run_id']!r}")
        if r["run_id"] in seen:
            raise CollectError(f"{where}: duplicate run_id {r['run_id']}")
        seen.add(r["run_id"])
        if r["variant"] not in VARIANTS:
            raise CollectError(f"{where}: variant must be one of {sorted(VARIANTS)}")
        if r["trigger"] not in TRIGGERS:
            raise CollectError(f"{where}: trigger must be one of {sorted(TRIGGERS)}")
        if not r["seq"].isdigit():
            raise CollectError(f"{where}: seq must be a non-negative integer")
        if r["role"] not in ROLES:
            raise CollectError(f"{where}: role must be one of {sorted(ROLES)}")
    if not rows:
        raise CollectError(f"{path}: no runs listed")
    return rows


# ---------------------------------------------------------------- GitHub API


def get_token():
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(name):
            return os.environ[name]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        raise CollectError("no token: set GH_TOKEN or log in with `gh auth login`") from e
    return out.stdout.strip()


def build_request(url, token):
    """GitHub headers are 'unredirected': the job-log endpoint redirects (302) to a download
    host outside api.github.com, and the token must not follow it there."""
    req = urllib.request.Request(url)
    req.add_unredirected_header("Authorization", f"Bearer {token}")
    req.add_unredirected_header("Accept", "application/vnd.github+json")
    req.add_unredirected_header("X-GitHub-Api-Version", API_VERSION)
    req.add_header("User-Agent", "collect-timings")
    return req


def http_get(url, token):
    try:
        with urllib.request.urlopen(build_request(url, token), timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise CollectError(f"GET {url}: HTTP {e.code}") from e


def fetch_run(repo, run_id, token):
    return json.loads(http_get(f"{API}/repos/{repo}/actions/runs/{run_id}", token))


def fetch_jobs(repo, run_id, token):
    """All jobs of attempt 1; pages merged into one object of the API's shape."""
    jobs, page = [], 1
    while True:
        url = f"{API}/repos/{repo}/actions/runs/{run_id}/attempts/1/jobs?per_page=100&page={page}"
        data = json.loads(http_get(url, token))
        jobs.extend(data["jobs"])
        if len(jobs) >= data["total_count"] or not data["jobs"]:
            return {"total_count": data["total_count"], "jobs": jobs}
        page += 1


def fetch_job_log(repo, job_id, token):
    raw = http_get(f"{API}/repos/{repo}/actions/jobs/{job_id}/logs", token)
    return raw.decode("utf-8", errors="replace")


# ---------------------------------------------------------------- parsing and formulas


RUNNER_INFO_KEYS = ["runner_version", "runner_image", "runner_image_version", "runner_cloud",
                    "runner_region"]
# (log group, line prefix) -> key; GitHub-hosted Linux jobs run on AWS or Azure (multi-cloud pool)
LOG_GROUP_FIELDS = {
    ("Runner Image", "Image: "): "runner_image",
    ("Runner Image", "Version: "): "runner_image_version",
    ("Runner Image Provisioner", "Cloud: "): "runner_cloud",
    ("Runner Image Provisioner", "Region: "): "runner_region",
}


def parse_runner_log(text):
    """Runner version, the 'Runner Image' group and the provisioner's cloud and region
    from the head of a job log."""
    info = dict.fromkeys(RUNNER_INFO_KEYS, "")
    group = None
    for line in text.splitlines()[:200]:
        line = LOG_PREFIX.sub("", line).strip()
        m = re.match(r"Current runner version: '([^']+)'", line)
        if m:
            info["runner_version"] = m.group(1)
        elif line.startswith("##[group]"):
            group = line.removeprefix("##[group]")
        elif line.startswith("##[endgroup]"):
            group = None
        elif group:
            for (g, prefix), key in LOG_GROUP_FIELDS.items():
                if g == group and line.startswith(prefix) and not info[key]:
                    info[key] = line.removeprefix(prefix)
    return info


def ts(value):
    """API timestamp ('2026-11-20T12:33:34Z') to an aware datetime; None stays None."""
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seconds(start, end):
    if start is None or end is None:
        return ""
    return int((end - start).total_seconds())


def counted_jobs(jobs):
    return [j for j in jobs if j.get("conclusion") != "skipped"]


def run_times(jobs):
    """T_wait, T_exec and the first-job queue (T_wait - T_exec) in seconds, docs/metodyka.md p. 3.2."""
    counted = counted_jobs(jobs)
    if not counted:
        raise CollectError("no counted jobs (all skipped)")
    for j in counted:
        if not (j.get("created_at") and j.get("started_at") and j.get("completed_at")):
            raise CollectError(f"job {j.get('id')} ({j.get('name')}) has no complete timestamps")
    created = min(ts(j["created_at"]) for j in counted)
    started = min(ts(j["started_at"]) for j in counted)
    completed = max(ts(j["completed_at"]) for j in counted)
    t_wait, t_exec = seconds(created, completed), seconds(started, completed)
    return {
        "jobs_counted": len(counted),
        "first_job_created_at": created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "first_job_started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_job_completed_at": completed.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "t_wait_s": t_wait,
        "t_exec_s": t_exec,
        "first_job_queue_s": t_wait - t_exec,
    }


def check_run(entry, run, jobs):
    rid = entry["run_id"]
    if str(run["id"]) != rid:
        raise CollectError(f"run {rid}: API returned run {run['id']}")
    expected = TRIGGERS[entry["trigger"]]
    if run["event"] != expected:
        raise CollectError(f"run {rid}: trigger {entry['trigger']} expects event {expected}, "
                           f"run has {run['event']}")
    if run["status"] != "completed":
        raise CollectError(f"run {rid}: status {run['status']}, wait until it completes")
    for j in jobs["jobs"]:
        if j["status"] != "completed":
            raise CollectError(f"run {rid}: job {j['name']} has status {j['status']}")


def build_rows(entry, run, jobs, runner_info):
    """One runs.csv row, jobs.csv rows and steps.csv rows for a single run."""
    label = {k: entry[k] for k in MANIFEST_FIELDS}
    run_row = dict(label, event=run["event"], head_branch=run["head_branch"],
                   head_sha=run["head_sha"], run_attempt=run["run_attempt"],
                   conclusion=run["conclusion"], **run_times(jobs["jobs"]))
    job_rows, step_rows = [], []
    for j in jobs["jobs"]:
        info = runner_info.get(str(j["id"]), {})
        job_rows.append(dict(
            label, job_id=j["id"], job_name=j["name"], conclusion=j["conclusion"],
            counted=j.get("conclusion") != "skipped",
            created_at=j["created_at"], started_at=j["started_at"], completed_at=j["completed_at"],
            queue_s=seconds(ts(j["created_at"]), ts(j["started_at"])),
            duration_s=seconds(ts(j["started_at"]), ts(j["completed_at"])),
            runner_name=j.get("runner_name") or "", labels=";".join(j.get("labels") or []),
            **{k: info.get(k, "") for k in RUNNER_INFO_KEYS},
        ))
        for s in j.get("steps") or []:
            step_rows.append(dict(
                label, job_id=j["id"], job_name=j["name"], step_number=s["number"],
                step_name=s["name"], conclusion=s["conclusion"],
                started_at=s.get("started_at") or "", completed_at=s.get("completed_at") or "",
                duration_s=seconds(ts(s.get("started_at")), ts(s.get("completed_at"))),
            ))
    return run_row, job_rows, step_rows


# ---------------------------------------------------------------- files


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path):
    if not path.exists():
        raise CollectError(f"{path} missing; collect it first without --from-raw")
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def collect(manifest, out, repo, from_raw):
    entries = read_manifest(manifest)
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    token = None if from_raw else get_token()
    runs, jobs_all, steps_all, warnings = [], [], [], []
    for entry in entries:
        rid = entry["run_id"]
        run_p, jobs_p, runner_p = (raw / f"{rid}-run.json", raw / f"{rid}-jobs.json",
                                   raw / f"{rid}-runner.json")
        if from_raw:
            run, jobs, runner_info = read_json(run_p), read_json(jobs_p), read_json(runner_p)
            check_run(entry, run, jobs)
        else:
            run, jobs = fetch_run(repo, rid, token), fetch_jobs(repo, rid, token)
            check_run(entry, run, jobs)
            runner_info = {}
            for j in jobs["jobs"]:
                try:
                    runner_info[str(j["id"])] = parse_runner_log(fetch_job_log(repo, j["id"], token))
                except CollectError as e:
                    warnings.append(f"run {rid}, job {j['name']}: no log ({e})")
                    runner_info[str(j["id"])] = parse_runner_log("")
            write_json(run_p, run)
            write_json(jobs_p, jobs)
            write_json(runner_p, runner_info)
        for j in jobs["jobs"]:
            if j.get("conclusion") != "skipped" and not runner_info.get(str(j["id"]), {}).get(
                    "runner_image_version"):
                warnings.append(f"run {rid}, job {j['name']}: runner image version not found")
        run_row, job_rows, step_rows = build_rows(entry, run, jobs, runner_info)
        runs.append(run_row)
        jobs_all.extend(job_rows)
        steps_all.extend(step_rows)
        print(f"{rid} {entry['variant']}/{entry['trigger']}/{entry['seq']} {entry['role']}: "
              f"T_wait={run_row['t_wait_s']} s, T_exec={run_row['t_exec_s']} s, "
              f"jobs={run_row['jobs_counted']}, attempt={run_row['run_attempt']}")
    write_csv(out / "runs.csv", RUN_FIELDS, runs)
    write_csv(out / "jobs.csv", JOB_FIELDS, jobs_all)
    write_csv(out / "steps.csv", STEP_FIELDS, steps_all)
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    print(f"{len(runs)} runs, {len(jobs_all)} jobs, {len(steps_all)} steps -> {out}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("manifest", type=Path, help="CSV: run_id,variant,trigger,seq,role")
    p.add_argument("--out", type=Path, help="output directory (default: the manifest's directory)")
    p.add_argument("--repo", default=DEFAULT_REPO, help=f"OWNER/NAME (default: {DEFAULT_REPO})")
    p.add_argument("--from-raw", action="store_true",
                   help="recompute the CSVs from raw/ without calling the API")
    args = p.parse_args(argv)
    try:
        collect(args.manifest, args.out or args.manifest.parent, args.repo, args.from_raw)
    except CollectError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
