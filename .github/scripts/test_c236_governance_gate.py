"""Offline adversarial tests for the C236-R17 technical gate."""

from __future__ import annotations

import copy
import unittest

import c236_governance_gate as gate

HEAD = "a" * 40
MAIN = "b" * 40
NEW_MAIN = "c" * 40
OTHER_HEAD = "d" * 40


def association(*, number=7, head=HEAD, base=MAIN, base_ref="main"):
    return {"number": number, "head": {"sha": head}, "base": {"ref": base_ref, "sha": base}}


def run_for(name="Backend CI", *, run_id=401, attempt=1, conclusion="success"):
    return {
        "id": run_id,
        "name": name,
        "path": gate.CI[name][0],
        "event": "pull_request",
        "head_sha": HEAD,
        "head_branch": "feature/demo",
        "repository": {"full_name": gate.REPO},
        "head_repository": {"full_name": gate.REPO},
        "run_attempt": attempt,
        "check_suite_id": run_id + 1000,
        "status": "completed" if conclusion is not None else "in_progress",
        "conclusion": conclusion,
        "pull_requests": [association()],
    }


class FakeAPI:
    def __init__(self, files=None, runs=None):
        self.main = MAIN
        self.pr = {
            "number": 7,
            "state": "open",
            "draft": False,
            "mergeable": True,
            "base": {"ref": "main", "sha": MAIN, "repo": {"full_name": gate.REPO}},
            "head": {"ref": "feature/demo", "sha": HEAD, "repo": {"full_name": gate.REPO}},
            "body": "**Status:** PASS stale and untrusted",
        }
        self.files = ["backend/app/api.py"] if files is None else files
        self.runs = [run_for()] if runs is None else runs
        self.main_reads = 0
        self.run_reads = 0
        self.on_second_main = None
        self.on_second_runs = None
        self.bad = {}

    def get(self, path):
        if path in self.bad:
            return copy.deepcopy(self.bad[path])
        if path == f"{gate.BASE}/git/ref/heads/main":
            self.main_reads += 1
            if self.main_reads == 2 and self.on_second_main:
                self.on_second_main(self)
            return {"ref": "refs/heads/main", "object": {"type": "commit", "sha": self.main}}
        if path == f"{gate.BASE}/pulls/7":
            return copy.deepcopy(self.pr)
        if path.startswith(f"{gate.BASE}/compare/"):
            base = path.split("/compare/", 1)[1].split("...", 1)[0]
            return {
                "status": "ahead" if base == MAIN else "diverged",
                "behind_by": 0 if base == MAIN else 1,
                "base_commit": {"sha": base},
                "merge_base_commit": {"sha": MAIN},
            }
        if path == f"{gate.BASE}/pulls/7/files?per_page=100&page=1":
            return [{"filename": name} for name in self.files]
        if path.startswith(f"{gate.BASE}/actions/runs?head_sha="):
            self.run_reads += 1
            if self.run_reads == 2 and self.on_second_runs:
                self.on_second_runs(self)
            return {"total_count": len(self.runs), "workflow_runs": copy.deepcopy(self.runs)}
        for run in self.runs:
            suite_id = run["check_suite_id"]
            job_id = run["id"] + 2000
            if path == f"{gate.BASE}/check-suites/{suite_id}":
                return {
                    "id": suite_id,
                    "head_sha": run["head_sha"],
                    "status": "completed",
                    "conclusion": "success",
                    "app": {"slug": "github-actions"},
                }
            if path == f"{gate.BASE}/actions/runs/{run['id']}/jobs?per_page=100&filter=latest":
                return {
                    "total_count": 1,
                    "jobs": [{
                        "id": job_id,
                        "name": gate.CI[run["name"]][1],
                        "head_sha": run["head_sha"],
                        "status": "completed",
                        "conclusion": "success",
                        "check_run_url": f"https://api.github.com{gate.BASE}/check-runs/{job_id}",
                    }],
                }
            if path == f"{gate.BASE}/check-runs/{job_id}":
                return {
                    "id": job_id,
                    "name": gate.CI[run["name"]][1],
                    "head_sha": run["head_sha"],
                    "status": "completed",
                    "conclusion": "success",
                    "check_suite": {"id": suite_id},
                    "app": {"slug": "github-actions"},
                    "details_url": f"https://github.com/{gate.REPO}/actions/runs/{run['id']}/job/{job_id}",
                }
        raise AssertionError(f"Unexpected API GET: {path}")


class GovernanceGateTests(unittest.TestCase):
    def verdict(self, api):
        return gate.evaluate_once(api, 7, HEAD)

    def test_success_with_proven_pr_head_and_live_main(self):
        result = self.verdict(FakeAPI())
        self.assertEqual((result.state, result.code), ("PASS", "CURRENT_EVIDENCE"))
        self.assertEqual(result.runs, (("Backend CI", 401, 1),))

    def test_missing_empty_or_malformed_pr_association_blocks(self):
        for associations in ([], None, {}, "invalid", [None], [association(number=True)]):
            with self.subTest(associations=associations):
                run = run_for()
                run["pull_requests"] = associations
                self.assertEqual(self.verdict(FakeAPI(runs=[run])).code, "RUN_ASSOCIATION_INVALID")
        run = run_for()
        del run["pull_requests"]
        self.assertEqual(self.verdict(FakeAPI(runs=[run])).code, "RUN_ASSOCIATION_INVALID")

    def test_stale_pass_in_body_has_no_authority(self):
        api = FakeAPI(files=["docs/notes.md"], runs=[])
        self.assertEqual(self.verdict(api).state, "PASS")
        api.main = NEW_MAIN
        self.assertEqual(self.verdict(api).state, "BLOCKED")

    def test_head_changes_after_event(self):
        api = FakeAPI()
        api.pr["head"]["sha"] = OTHER_HEAD
        self.assertEqual(self.verdict(api).code, "PR_STALE_OR_UNTRUSTED")

    def test_base_main_advances(self):
        api = FakeAPI()
        api.main = NEW_MAIN
        self.assertEqual(self.verdict(api).code, "PR_STALE_OR_UNTRUSTED")

    def test_main_must_be_ancestor_of_head(self):
        api = FakeAPI()
        api.bad[f"{gate.BASE}/compare/{MAIN}...{HEAD}"] = {
            "status": "diverged", "behind_by": 1,
            "base_commit": {"sha": MAIN}, "merge_base_commit": {"sha": OTHER_HEAD},
        }
        self.assertEqual(self.verdict(api).code, "MAIN_NOT_ANCESTOR")

    def test_missing_or_unfinished_ci_blocks(self):
        for runs, code in (([], "WAIT_CI_MISSING"), ([run_for(conclusion=None)], "WAIT_CI_INCOMPLETE")):
            with self.subTest(code=code):
                result = self.verdict(FakeAPI(runs=runs))
                self.assertEqual((result.state, result.code), ("BLOCKED", code))

    def test_non_success_conclusions_never_pass(self):
        for conclusion in ("failure", "timed_out", "action_required", "skipped", "neutral", "cancelled", None):
            with self.subTest(conclusion=conclusion):
                self.assertNotEqual(self.verdict(FakeAPI(runs=[run_for(conclusion=conclusion)])).state, "PASS")

    def test_latest_failed_attempt_overrides_old_success(self):
        api = FakeAPI(runs=[run_for(), run_for(run_id=402, attempt=2, conclusion="failure")])
        self.assertEqual(self.verdict(api).state, "FAIL")

    def test_mismatched_or_contradictory_pr_association_blocks(self):
        for associations in (
            [association(number=8)],
            [association(head=OTHER_HEAD)],
            [association(base=NEW_MAIN)],
            [association(base_ref="other")],
            [association(), association(number=8)],
        ):
            with self.subTest(associations=associations):
                run = run_for()
                run["pull_requests"] = associations
                self.assertEqual(self.verdict(FakeAPI(runs=[run])).code, "RUN_ASSOCIATION_INVALID")

    def test_pr_association_changes_between_reads_blocks(self):
        api = FakeAPI()
        api.on_second_runs = lambda instance: instance.runs[0].update(pull_requests=[])
        self.assertEqual(self.verdict(api).code, "RUN_ASSOCIATION_INVALID")

    def test_wrong_check_head_blocks_even_with_successful_run(self):
        api = FakeAPI()
        job_id = 401 + 2000
        path = f"{gate.BASE}/check-runs/{job_id}"
        check = api.get(path)
        check["head_sha"] = OTHER_HEAD
        api.bad[path] = check
        self.assertEqual(self.verdict(api).code, "CHECK_PROVENANCE_INVALID")

    def test_incomplete_suite_or_jobs_block(self):
        for path, value, code in (
            (f"{gate.BASE}/check-suites/1401", {}, "SUITE_PROVENANCE_INVALID"),
            (f"{gate.BASE}/actions/runs/401/jobs?per_page=100&filter=latest", {}, "JOBS_INVALID"),
        ):
            with self.subTest(path=path):
                api = FakeAPI()
                api.bad[path] = value
                self.assertEqual(self.verdict(api).code, code)

    def test_main_changes_during_verification(self):
        api = FakeAPI()
        api.on_second_main = lambda instance: setattr(instance, "main", NEW_MAIN)
        self.assertEqual(self.verdict(api).code, "PR_STALE_OR_UNTRUSTED")

    def test_new_ci_attempt_during_verification(self):
        api = FakeAPI()
        api.on_second_runs = lambda instance: instance.runs.append(run_for(run_id=402, attempt=2))
        self.assertEqual(self.verdict(api).code, "CONCURRENT_CI_ATTEMPT")

    def test_docs_only_has_no_functional_ci_but_requires_live_scope(self):
        api = FakeAPI(files=["docs/notes.md"], runs=[])
        self.assertEqual(self.verdict(api).state, "PASS")
        api.files = []
        self.assertEqual(self.verdict(api).code, "FILES_INVALID")

    def test_gate_change_requires_offline_ci(self):
        api = FakeAPI(files=[".github/workflows/c236-governance-gate-pilot.yml"], runs=[])
        self.assertEqual(self.verdict(api).code, "WAIT_CI_MISSING")
        api.runs = [run_for("C236 governance offline tests")]
        self.assertEqual(self.verdict(api).state, "PASS")

    def test_unknown_workflow_change_blocks(self):
        api = FakeAPI(files=[".github/workflows/new-privileged.yml"], runs=[])
        self.assertEqual(self.verdict(api).code, "WORKFLOW_UNCOVERED")

    def test_changed_file_scope_during_verification_blocks(self):
        api = FakeAPI()
        api.on_second_main = lambda instance: instance.files.append("mobile/lib/main.dart")
        self.assertEqual(self.verdict(api).code, "CONCURRENT_PR_OR_MAIN")

    def test_mobile_change_requires_both_mobile_workflows(self):
        api = FakeAPI(files=["mobile/lib/main.dart"], runs=[run_for("Flutter CI")])
        self.assertEqual(self.verdict(api).code, "WAIT_CI_MISSING")
        api.runs.append(run_for("Android APK CI", run_id=402))
        self.assertEqual(self.verdict(api).state, "PASS")

    def test_metadata_signal_is_not_functional_ci(self):
        api = FakeAPI(files=[".github/workflows/pr-metadata-signal.yml"], runs=[])
        self.assertEqual(self.verdict(api).code, "WAIT_CI_MISSING")

    def test_metadata_test_script_alone_requires_metadata_ci(self):
        api = FakeAPI(files=[".github/scripts/test_pr_status_sync.py"], runs=[])
        self.assertEqual(self.verdict(api).code, "WAIT_CI_MISSING")

    def test_same_attempt_failure_on_second_run_read_blocks(self):
        api = FakeAPI()
        api.on_second_runs = lambda instance: instance.runs[0].update(conclusion="failure")
        result = self.verdict(api)
        self.assertEqual((result.state, result.code), ("BLOCKED", "CONCURRENT_CI_EVIDENCE"))

    def test_check_result_changes_after_first_verification_blocks(self):
        api = FakeAPI()
        path = f"{gate.BASE}/check-runs/2401"

        def change_check(instance):
            check = instance.get(path)
            check["conclusion"] = "failure"
            instance.bad[path] = check

        api.on_second_runs = change_check
        result = self.verdict(api)
        self.assertEqual((result.state, result.code), ("BLOCKED", "CHECK_PROVENANCE_INVALID"))

    def test_draft_or_foreign_repository_blocks(self):
        for change in (
            lambda api: api.pr.update(draft=True),
            lambda api: api.pr["head"]["repo"].update(full_name="foreign/repo"),
        ):
            api = FakeAPI()
            change(api)
            self.assertEqual(self.verdict(api).state, "BLOCKED")

    def test_run_list_truncation_blocks(self):
        api = FakeAPI()
        api.bad[f"{gate.BASE}/actions/runs?head_sha={HEAD}&event=pull_request&per_page=100"] = {
            "total_count": 101, "workflow_runs": [],
        }
        self.assertEqual(self.verdict(api).code, "RUNS_TRUNCATED")


if __name__ == "__main__":
    unittest.main()
