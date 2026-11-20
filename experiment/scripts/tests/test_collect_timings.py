"""Tests for experiment/scripts/collect_timings.py (no network).

Fixtures: the jobs of attempt 1 of run 44736780743 (push on exp/variant-a, 2026-11-20) as returned
by the GitHub API, and the head of the log of its `lint` job.

Run: python -m unittest discover -s experiment/scripts/tests
"""

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import collect_timings as ct  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
JOBS = json.loads((FIXTURES / "jobs-44736780743.json").read_text(encoding="utf-8"))
LOG_HEAD = (FIXTURES / "log-head.txt").read_text(encoding="utf-8")
RUN = {
    "id": 44736780743, "event": "push", "status": "completed", "conclusion": "success",
    "head_branch": "exp/variant-a", "head_sha": "5f102d5e0494411dd038955319337061ff78a8e7",
    "run_attempt": 1,
}
ENTRY = {"run_id": "44736780743", "variant": "A", "trigger": "main", "seq": "1", "role": "pilot"}


def write_manifest(test, text):
    d = tempfile.TemporaryDirectory()
    test.addCleanup(d.cleanup)
    path = Path(d.name) / "manifest.csv"
    path.write_text(text, encoding="utf-8")
    return path


class RunTimes(unittest.TestCase):
    def test_formulas_on_real_run(self):
        # created 12:33:34 (lint, test), started 12:33:35 (lint), completed 12:34:49 (build)
        t = ct.run_times(JOBS["jobs"])
        self.assertEqual(t["t_wait_s"], 75)
        self.assertEqual(t["t_exec_s"], 74)
        self.assertEqual(t["first_job_queue_s"], 1)
        self.assertEqual(t["jobs_counted"], 3)
        self.assertEqual(t["last_job_completed_at"], "2026-11-20T12:34:49Z")

    def test_skipped_job_is_not_counted(self):
        jobs = copy.deepcopy(JOBS["jobs"])
        late = copy.deepcopy(jobs[0])
        late.update(id=1, name="skipped-job", conclusion="skipped",
                    created_at="2026-11-20T12:40:00Z", started_at="2026-11-20T12:40:00Z",
                    completed_at="2026-11-20T12:40:00Z")
        t = ct.run_times(jobs + [late])
        self.assertEqual(t["t_wait_s"], 75)
        self.assertEqual(t["jobs_counted"], 3)

    def test_missing_timestamp_is_an_error(self):
        jobs = copy.deepcopy(JOBS["jobs"])
        jobs[0]["started_at"] = None
        with self.assertRaises(ct.CollectError):
            ct.run_times(jobs)


class RunnerLog(unittest.TestCase):
    def test_parse_real_log_head(self):
        info = ct.parse_runner_log(LOG_HEAD)
        self.assertEqual(info, {"runner_version": "2.338.2", "runner_image": "ubuntu-24.04",
                                "runner_image_version": "20261116.376.1",
                                "runner_cloud": "Azure", "runner_region": "eastus2"})

    def test_provisioner_version_is_not_image_version(self):
        # The 'Runner Image Provisioner' group also has a 'Version:' line (20261111.635).
        info = ct.parse_runner_log(LOG_HEAD)
        self.assertNotEqual(info["runner_image_version"], "20261111.635")

    def test_empty_log(self):
        self.assertEqual(ct.parse_runner_log(""), dict.fromkeys(ct.RUNNER_INFO_KEYS, ""))


class Manifest(unittest.TestCase):
    HEADER = "run_id,variant,trigger,seq,role\n"

    def test_valid(self):
        p = write_manifest(self, self.HEADER + "1,A,pr,0,warmup\n2,B,main,1,measure\n")
        rows = ct.read_manifest(p)
        self.assertEqual([r["run_id"] for r in rows], ["1", "2"])

    def test_rejects_bad_values(self):
        for line in ["x,A,pr,1,measure", "1,C,pr,1,measure", "1,A,push,1,measure",
                     "1,A,pr,-1,measure", "1,A,pr,1,rerun"]:
            with self.subTest(line=line), self.assertRaises(ct.CollectError):
                ct.read_manifest(write_manifest(self, self.HEADER + line + "\n"))

    def test_rejects_duplicates_and_missing_columns(self):
        with self.assertRaises(ct.CollectError):
            ct.read_manifest(write_manifest(self, self.HEADER + "1,A,pr,1,measure\n1,B,pr,1,measure\n"))
        with self.assertRaises(ct.CollectError):
            ct.read_manifest(write_manifest(self, "run_id,variant\n1,A\n"))


class Checks(unittest.TestCase):
    def test_trigger_must_match_event(self):
        ct.check_run(ENTRY, RUN, JOBS)
        with self.assertRaises(ct.CollectError):
            ct.check_run(dict(ENTRY, trigger="pr"), RUN, JOBS)

    def test_incomplete_run_is_an_error(self):
        with self.assertRaises(ct.CollectError):
            ct.check_run(ENTRY, dict(RUN, status="in_progress"), JOBS)


class Rows(unittest.TestCase):
    def test_rows_from_real_run(self):
        info = {str(j["id"]): ct.parse_runner_log(LOG_HEAD) for j in JOBS["jobs"]}
        run_row, job_rows, step_rows = ct.build_rows(ENTRY, RUN, JOBS, info)
        self.assertEqual(run_row["t_exec_s"], 74)
        self.assertEqual(set(run_row), set(ct.RUN_FIELDS))
        self.assertEqual([r["job_name"] for r in job_rows], ["lint", "test", "build"])
        self.assertEqual([r["duration_s"] for r in job_rows], [8, 37, 34])
        self.assertEqual(job_rows[2]["queue_s"], 2)
        self.assertEqual(job_rows[0]["runner_image_version"], "20261116.376.1")
        pytest_step = next(s for s in step_rows if s["step_name"] == "pytest")
        self.assertEqual(pytest_step["duration_s"], 16)
        self.assertTrue(all(set(r) == set(ct.STEP_FIELDS) for r in step_rows))


class Request(unittest.TestCase):
    def test_token_is_not_sent_after_redirect(self):
        req = ct.build_request("https://api.github.com/x", "secret")
        self.assertIn("Authorization", req.unredirected_hdrs)
        self.assertNotIn("Authorization", req.headers)


class FromRaw(unittest.TestCase):
    def test_recompute_without_network(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            (out / "raw").mkdir()
            rid = ENTRY["run_id"]
            (out / "raw" / f"{rid}-run.json").write_text(json.dumps(RUN), encoding="utf-8")
            (out / "raw" / f"{rid}-jobs.json").write_text(json.dumps(JOBS), encoding="utf-8")
            info = {str(j["id"]): ct.parse_runner_log(LOG_HEAD) for j in JOBS["jobs"]}
            (out / "raw" / f"{rid}-runner.json").write_text(json.dumps(info), encoding="utf-8")
            manifest = out / "manifest.csv"
            manifest.write_text("run_id,variant,trigger,seq,role\n" + ",".join(ENTRY.values())
                                + "\n", encoding="utf-8")
            ct.collect(manifest, out, ct.DEFAULT_REPO, from_raw=True)
            runs = (out / "runs.csv").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(runs), 2)
            self.assertIn(",75,74,1", runs[1])


if __name__ == "__main__":
    unittest.main()
