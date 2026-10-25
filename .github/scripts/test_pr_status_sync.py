"""Offline adversarial tests for the trusted PR metadata updater."""

import copy
import unittest
from pathlib import Path

import pr_status_sync as sync

HEAD = "a" * 40
BASE_SHA = "b" * 40


def make_pr():
    return {
        "number": 7,
        "state": "open",
        "merged_at": None,
        "updated_at": "2026-10-25T09:00:00Z",
        "body": "Histórico literal.\n<!-- C232:ESTADO_ATUAL:INICIO -->\nAntigo.\n",
        "title": "Título não deve ser alterado",
        "head": {"sha": HEAD, "ref": "feat/test", "repo": {"full_name": sync.REPO}},
        "base": {"sha": BASE_SHA, "ref": "main", "repo": {"full_name": sync.REPO}},
    }


def make_run(run_id=90, name="Backend CI", conclusion="success"):
    return {
        "id": run_id,
        "run_attempt": 1,
        "name": name,
        "path": sync.WORKFLOW_PATHS.get(name, ".github/workflows/unknown.yml"),
        "event": "pull_request",
        "head_sha": HEAD,
        "head_repository": {"full_name": sync.REPO},
        "repository": {"full_name": sync.REPO},
        "pull_requests": [{"number": 7, "head": {"sha": HEAD}, "base": {"sha": BASE_SHA}}],
        "status": "completed" if conclusion is not None else "in_progress",
        "conclusion": conclusion,
        "updated_at": "2026-10-25T10:00:00Z",
    }


class FakeAPI:
    def __init__(self, pr=None, files=None, runs=None):
        self.pr = copy.deepcopy(pr or make_pr())
        self.files = files if files is not None else ["backend/app/example.py"]
        self.runs = runs if runs is not None else [make_run()]
        self.commit_pulls = [{"number": 7}]
        self.pr_reads = 0
        self.patches = []
        self.on_second_read = None
        self.on_patch = None
        self.patch_error = None
        self.run_reads = 0
        self.on_second_run_read = None
        self.on_third_run_read = None

    def get(self, path):
        if path == f"{sync.BASE}/pulls/7":
            self.pr_reads += 1
            if self.pr_reads == 2 and self.on_second_read:
                self.on_second_read(self.pr)
            return copy.deepcopy(self.pr)
        if path.startswith(f"{sync.BASE}/pulls/7/files?"):
            return [{"filename": name} for name in self.files] if path.endswith("page=1") else []
        if path.startswith(f"{sync.BASE}/actions/runs?"):
            self.run_reads += 1
            if self.run_reads == 2 and self.on_second_run_read:
                self.on_second_run_read(self.runs)
            if self.run_reads == 3 and self.on_third_run_read:
                self.on_third_run_read(self.runs)
            return {"total_count": len(self.runs), "workflow_runs": copy.deepcopy(self.runs)}
        if path == f"{sync.BASE}/actions/runs/90":
            return copy.deepcopy(self.runs[0])
        if path == f"{sync.BASE}/commits/{HEAD}/pulls":
            return copy.deepcopy(self.commit_pulls)
        if path == f"{sync.BASE}/pulls/8":
            stale = copy.deepcopy(self.pr)
            stale["number"] = 8
            stale["head"]["sha"] = "d" * 40
            return stale
        if path.startswith(f"{sync.BASE}/pulls?state=open"):
            return [{"number": 7}]
        raise AssertionError("unexpected API path")

    def patch(self, path, payload):
        if self.patch_error:
            raise self.patch_error
        self.patches.append((path, copy.deepcopy(payload)))
        self.pr["body"] = payload["body"]
        self.pr["updated_at"] = "2026-10-25T10:01:00Z"
        if self.on_patch:
            self.on_patch(self.pr)
        return copy.deepcopy(self.pr)


def run_event():
    return {"repository": {"full_name": sync.REPO}, "workflow_run": {"id": 90}}


class MetadataTests(unittest.TestCase):
    def test_old_base_ci_cannot_produce_pass_after_main_advances(self):
        api = FakeAPI()
        api.pr["base"]["sha"] = "c" * 40
        api.runs[0]["pull_requests"] = [{"number": 7, "head": {"sha": HEAD},
                                         "base": {"sha": BASE_SHA}}]
        sync.synchronize(api, "workflow_run", run_event())
        self.assertNotIn("**Status:** PASS", api.pr["body"])

    def test_main_push_signal_rechecks_open_pr_with_unchanged_head(self):
        signal = make_run(name="PR metadata signal")
        signal["event"] = "push"
        signal["head_branch"] = "main"
        signal["head_sha"] = "c" * 40
        signal["pull_requests"] = []
        old_ci = make_run(run_id=91)
        api = FakeAPI(runs=[signal, old_ci])
        api.pr["base"]["sha"] = "c" * 40
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UPDATED")
        self.assertIn("**Status:** BLOCKED", api.pr["body"])
        self.assertNotIn("**Status:** PASS", api.pr["body"])

    def test_ci_without_base_provenance_cannot_produce_pass(self):
        api = FakeAPI()
        api.runs[0]["pull_requests"] = []
        sync.synchronize(api, "workflow_run", run_event())
        self.assertNotIn("**Status:** PASS", api.pr["body"])

    def test_discovery_falls_back_when_commit_association_is_stale(self):
        run = make_run()
        run["pull_requests"] = []
        api = FakeAPI(runs=[run])
        api.commit_pulls = [{"number": 8}]
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UPDATED")

    def test_workflow_change_requires_human_review_even_with_successful_ci(self):
        api = FakeAPI(files=["backend/app/example.py", ".github/workflows/backend-ci.yml"])
        api.runs[0]["pull_requests"] = [{"number": 7, "head": {"sha": HEAD},
                                         "base": {"sha": BASE_SHA}}]
        sync.synchronize(api, "workflow_run", run_event())
        self.assertIn("**Status:** BLOCKED", api.pr["body"])
        self.assertIn("revisão humana", api.pr["body"].lower())

    def test_test_module_change_requires_human_review_even_with_successful_ci(self):
        files = [".github/scripts/test_pr_status_sync.py"]
        self.assertEqual(sync.required_workflows(files), ("PR metadata tests",))
        api = FakeAPI(files=files, runs=[make_run(name="PR metadata tests")])
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UPDATED")
        self.assertIn("**Status:** BLOCKED", api.pr["body"])
        self.assertIn("revisão humana", api.pr["body"].lower())
        self.assertNotIn("**Status:** PASS", api.pr["body"])

    def test_existing_sensitive_paths_still_require_human_review(self):
        for filename in (
            ".github/workflows/backend-ci.yml",
            ".github/workflows/pr-metadata-sync.yml",
            ".github/scripts/pr_status_sync.py",
        ):
            with self.subTest(filename=filename):
                self.assertTrue(sync.needs_human_review([filename]))

    def test_read_only_signal_covers_document_only_pr(self):
        signal = (Path(__file__).resolve().parents[1] / "workflows" / "pr-metadata-signal.yml").read_text()
        writer = (Path(__file__).resolve().parents[1] / "workflows" / "pr-metadata-sync.yml").read_text()
        self.assertIn("pull_request:", signal)
        self.assertNotIn("pull_request_target:", writer)
        self.assertIn("PR metadata signal", writer)
        self.assertNotIn("actions/checkout", signal)
        self.assertNotIn("pull-requests: write", signal)
        api = FakeAPI(files=["docs/only.md"], runs=[make_run(name="PR metadata signal")])
        sync.synchronize(api, "workflow_run", run_event())
        self.assertIn("**Status:** BLOCKED", api.pr["body"])

    def test_writer_documents_non_atomic_patch_limit(self):
        self.assertIn("compare-and-swap", sync.synchronize.__doc__ or "")

    def test_success_and_history_are_preserved(self):
        api = FakeAPI()
        original = api.pr["body"]
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UPDATED")
        body = api.pr["body"]
        self.assertEqual(body.count(sync.START), 1)
        self.assertEqual(body.count(sync.END), 1)
        self.assertTrue(body.endswith(original))
        self.assertIn("**Status:** PASS", body)
        self.assertEqual(len(api.patches), 1)
        self.assertEqual(set(api.patches[0][1]), {"body"})
        self.assertEqual(api.pr["title"], "Título não deve ser alterado")

    def test_repeated_event_is_idempotent(self):
        api = FakeAPI()
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UPDATED")
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UNCHANGED")
        self.assertEqual(len(api.patches), 1)

    def test_duplicate_or_reversed_markers_fail_closed(self):
        for body in (
            sync.START + sync.START + sync.END,
            sync.END + sync.START,
            sync.START + "missing end",
        ):
            with self.subTest(body=body):
                with self.assertRaises(sync.SyncError):
                    sync.upsert(body, "block")

    def test_failed_pending_and_cancelled_ci(self):
        for conclusion, expected in (
            ("failure", "FAIL"),
            (None, "PENDING"),
            ("cancelled", "BLOCKED"),
        ):
            with self.subTest(conclusion=conclusion):
                api = FakeAPI(runs=[make_run(conclusion=conclusion)])
                sync.synchronize(api, "workflow_run", run_event())
                self.assertIn("**Status:** " + expected, api.pr["body"])

    def test_document_only_change_does_not_reuse_old_pass(self):
        api = FakeAPI(files=["docs/continuidade/new.md"])
        sync.synchronize(api, "workflow_run", run_event())
        self.assertIn("**Status:** BLOCKED", api.pr["body"])
        self.assertNotIn("**Status:** PASS", api.pr["body"])

    def test_relevant_workflows_are_selected_without_executing_paths(self):
        files = ["backend/x.py", "mobile/x.dart", ".github/scripts/pr_status_sync.py"]
        self.assertEqual(
            sync.required_workflows(files),
            ("Backend CI", "Flutter CI", "Android APK CI", "PR metadata tests"),
        )

    def test_newer_run_wins_over_rerun_of_old_id(self):
        older = make_run(run_id=90, conclusion="success")
        older["run_attempt"] = 8
        newer = make_run(run_id=91, conclusion=None)
        api = FakeAPI(runs=[older, newer])
        result = sync.latest_runs(api, HEAD, ("Backend CI",))
        self.assertEqual(result["Backend CI"]["id"], 91)
        self.assertEqual(sync.classification(("Backend CI",), result)[0], "PENDING")

    def test_head_changes_between_read_and_write(self):
        api = FakeAPI()
        api.on_second_read = lambda pr: pr["head"].update(sha="c" * 40)
        with self.assertRaisesRegex(sync.SyncError, "CONCURRENT_CHANGE"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_base_changes_between_read_and_write(self):
        api = FakeAPI()
        api.on_second_read = lambda pr: pr["base"].update(sha="c" * 40)
        with self.assertRaisesRegex(sync.SyncError, "CONCURRENT_CHANGE"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_run_base_association_changes_before_write(self):
        api = FakeAPI()
        api.on_second_run_read = lambda runs: runs[0]["pull_requests"][0]["base"].update(sha="c" * 40)
        with self.assertRaisesRegex(sync.SyncError, "CONCURRENT_RUN"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_body_edit_between_read_and_write(self):
        api = FakeAPI()
        api.on_second_read = lambda pr: pr.update(body=pr["body"] + "edição humana")
        with self.assertRaisesRegex(sync.SyncError, "CONCURRENT_CHANGE"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_closed_pr_and_fork_are_rejected(self):
        for change in (
            lambda pr: pr.update(state="closed", merged_at="2026-10-25T11:00:00Z"),
            lambda pr: pr["head"]["repo"].update(full_name="someone/untrusted"),
        ):
            api = FakeAPI()
            change(api.pr)
            with self.assertRaises(sync.SyncError):
                sync.synchronize(api, "workflow_run", run_event())
            self.assertEqual(api.patches, [])

    def test_empty_workflow_pull_request_list_uses_commit_lookup(self):
        run = make_run()
        run["pull_requests"] = []
        api = FakeAPI(runs=[run])
        self.assertEqual(sync.synchronize(api, "workflow_run", run_event()), "UPDATED")
        self.assertEqual(len(api.patches), 1)

    def test_stale_workflow_event_does_not_write(self):
        api = FakeAPI()
        api.pr["head"]["sha"] = "c" * 40
        with self.assertRaisesRegex(sync.SyncError, "PR_NOT_UNAMBIGUOUS"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_untrusted_workflow_is_rejected(self):
        api = FakeAPI(runs=[make_run(name="Unknown workflow")])
        with self.assertRaisesRegex(sync.SyncError, "RUN_UNTRUSTED"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_workflow_name_spoofed_from_another_path_is_rejected(self):
        run = make_run()
        run["path"] = ".github/workflows/evil.yml"
        api = FakeAPI(runs=[run])
        with self.assertRaisesRegex(sync.SyncError, "RUN_UNTRUSTED"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_untrusted_title_branch_and_history_are_not_interpreted(self):
        api = FakeAPI()
        api.pr["title"] = "${{ secrets.GITHUB_TOKEN }}"
        api.pr["head"]["ref"] = "x; echo leak"
        api.pr["body"] += "<script>do-not-execute</script>"
        original = api.pr["body"]
        sync.synchronize(api, "workflow_run", run_event())
        self.assertTrue(api.pr["body"].endswith(original))
        self.assertNotIn("echo leak", api.pr["body"][:-len(original)])
        self.assertNotIn("secrets.GITHUB_TOKEN", api.pr["body"][:-len(original)])

    def test_test_count_is_never_inferred_from_workflow_success(self):
        api = FakeAPI()
        sync.synchronize(api, "workflow_run", run_event())
        self.assertIn("CONTAGEM NÃO VERIFICADA", api.pr["body"])
        self.assertNotIn("508/508", api.pr["body"])

    def test_api_permission_failure_does_not_patch_or_expose_secret(self):
        api = FakeAPI()
        api.patch_error = sync.SyncError("API_FORBIDDEN")
        with self.assertRaisesRegex(sync.SyncError, "^API_FORBIDDEN$"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])
        with self.assertRaisesRegex(sync.SyncError, "TOKEN_MISSING"):
            sync.GitHubAPI("")

    def test_post_write_concurrent_change_is_detected(self):
        api = FakeAPI()
        api.on_patch = lambda pr: pr.update(body=pr["body"] + "edição concorrente")
        with self.assertRaisesRegex(sync.SyncError, "POST_WRITE_CONFLICT"):
            sync.synchronize(api, "workflow_run", run_event())

    def test_newer_run_before_write_is_denied(self):
        api = FakeAPI()
        api.on_second_run_read = lambda runs: runs.append(make_run(run_id=91, conclusion=None))
        with self.assertRaisesRegex(sync.SyncError, "CONCURRENT_RUN"):
            sync.synchronize(api, "workflow_run", run_event())
        self.assertEqual(api.patches, [])

    def test_newer_run_after_write_is_detected(self):
        api = FakeAPI()
        api.on_third_run_read = lambda runs: runs.append(make_run(run_id=91, conclusion=None))
        with self.assertRaisesRegex(sync.SyncError, "POST_WRITE_CONFLICT"):
            sync.synchronize(api, "workflow_run", run_event())

    def test_workflow_never_checks_out_pr_with_write_token(self):
        workflow = (Path(__file__).resolve().parents[1] / "workflows" / "pr-metadata-sync.yml").read_text()
        self.assertIn("ref: main", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertNotIn("pull_request.head.sha", workflow)
        self.assertNotIn("secrets.", workflow)


if __name__ == "__main__":
    unittest.main()
