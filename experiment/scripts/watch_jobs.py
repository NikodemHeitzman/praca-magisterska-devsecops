"""Watch the jobs of one workflow run live and record when each job is first seen in each status
(pilot check P5 of experiment/PROTOCOL.md: what the job field `created_at` means, docs/metodyka.md TK4).

Start it before the run exists (e.g. before opening a pull request). It waits for the run of the
given commit and event, then polls the run and the jobs of attempt 1 every --interval seconds until
the run completes. One CSV row per first observation of (job, status), with the observer's UTC
clock, the server clock (HTTP `Date` header) and the job's timestamps as the API reported them then.

Usage:
  python experiment/scripts/watch_jobs.py --head-sha SHA --event pull_request --out FILE.csv

Standard library only; token as in collect_timings.py.
"""

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from collect_timings import API, DEFAULT_REPO, CollectError, build_request, get_token  # noqa: E402

FIELDS = ["observed_utc", "server_utc", "run_id", "job_id", "job_name", "status",
          "created_at", "started_at", "completed_at"]


def get(url, token):
    """JSON body and the server time from the Date header."""
    try:
        with urllib.request.urlopen(build_request(url, token), timeout=30) as resp:
            server = parsedate_to_datetime(resp.headers["Date"]).strftime("%Y-%m-%dT%H:%M:%SZ")
            return json.loads(resp.read()), server
    except urllib.error.HTTPError as e:
        raise CollectError(f"GET {url}: HTTP {e.code}") from e


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


def watch(repo, head_sha, event, out, interval, timeout):
    token = get_token()
    deadline = time.monotonic() + timeout
    run_id = None
    print(f"waiting for the {event} run of {head_sha[:12]} ...")
    while run_id is None:
        data, _ = get(f"{API}/repos/{repo}/actions/runs?head_sha={head_sha}&event={event}", token)
        if data["workflow_runs"]:
            run_id = data["workflow_runs"][0]["id"]
        elif time.monotonic() > deadline:
            raise CollectError("timeout: no run appeared")
        else:
            time.sleep(interval)
    print(f"run {run_id}")
    seen, rows = set(), []
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        while True:
            run, server = get(f"{API}/repos/{repo}/actions/runs/{run_id}", token)
            jobs, server_j = get(
                f"{API}/repos/{repo}/actions/runs/{run_id}/attempts/1/jobs?per_page=100", token)
            observed = now_utc()
            items = [("run", "run", run["status"], run.get("created_at"), run.get("run_started_at"),
                      None, server)]
            items += [(j["id"], j["name"], j["status"], j["created_at"], j["started_at"],
                       j["completed_at"], server_j) for j in jobs["jobs"]]
            for job_id, name, status, created, started, completed, srv in items:
                if (job_id, status) in seen:
                    continue
                seen.add((job_id, status))
                row = dict(observed_utc=observed, server_utc=srv, run_id=run_id, job_id=job_id,
                           job_name=name, status=status, created_at=created or "",
                           started_at=started or "", completed_at=completed or "")
                w.writerow(row)
                f.flush()
                rows.append(row)
                print(f"{observed} {name:6} {status:12} created={created} started={started}")
            if run["status"] == "completed":
                break
            if time.monotonic() > deadline:
                raise CollectError("timeout: run did not complete")
            time.sleep(interval)
    print(f"{len(rows)} observations -> {out}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--head-sha", required=True)
    p.add_argument("--event", default="pull_request")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--repo", default=DEFAULT_REPO)
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--timeout", type=float, default=1200)
    args = p.parse_args(argv)
    try:
        watch(args.repo, args.head_sha, args.event, args.out, args.interval, args.timeout)
    except CollectError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
