"""C236-R17: read-only, fail-closed technical gate for a PR against main.

The result is not a Master approval. This module never reads a PR body, writes
to GitHub, or executes code from a pull request.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

REPO = "fronassor-art/FRcaixinha-2.2"
BASE = f"/repos/{REPO}"
SHA = re.compile(r"[0-9a-f]{40}\Z")
MAX_FILES = 3000
MAX_RUNS = 100
POLL_SECONDS = 30
POLL_LIMIT_SECONDS = 32 * 60

# Names and paths are both checked. The signal and writer are not functional CI.
CI = {
    "Backend CI": (".github/workflows/backend-ci.yml", "unittest"),
    "Flutter CI": (".github/workflows/flutter-ci.yml", "flutter"),
    "Android APK CI": (".github/workflows/android-apk-ci.yml", "debug-apk"),
    "PR metadata tests": (".github/workflows/pr-metadata-tests.yml", "unittest"),
    "C236 governance offline tests": (
        ".github/workflows/c236-governance-gate-tests.yml",
        "c236-governance-offline",
    ),
}
GATE_FILES = {
    ".github/workflows/c236-governance-gate-pilot.yml",
    ".github/workflows/c236-governance-gate-tests.yml",
    ".github/scripts/c236_governance_gate.py",
    ".github/scripts/test_c236_governance_gate.py",
}


class GateError(Exception):
    """Stable diagnostic code, without API payloads or token material."""


@dataclass(frozen=True)
class Verdict:
    state: str
    code: str
    head: str = ""
    main: str = ""
    runs: tuple[tuple[str, int, int], ...] = ()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise GateError("API_REDIRECT")


class GitHubAPI:
    def __init__(self, token: str):
        if not token:
            raise GateError("TOKEN_MISSING")
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect())

    def get(self, path: str):
        if not path.startswith(BASE + "/") or ".." in path.replace("...", ""):
            raise GateError("API_PATH_INVALID")
        request = urllib.request.Request(
            "https://api.github.com" + path,
            method="GET",
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with self.opener.open(request, timeout=15) as response:
                return json.load(response)
        except GateError:
            raise
        except urllib.error.HTTPError as exc:
            raise GateError("API_FORBIDDEN" if exc.code in (401, 403) else "API_UNAVAILABLE") from None
        except Exception:
            raise GateError("API_UNAVAILABLE") from None


def valid_sha(value) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def positive_int(value) -> bool:
    return type(value) is int and value > 0


def main_sha(api) -> str:
    ref = api.get(f"{BASE}/git/ref/heads/main")
    if not isinstance(ref, dict) or ref.get("ref") != "refs/heads/main":
        raise GateError("MAIN_INVALID")
    obj = ref.get("object")
    if not isinstance(obj, dict) or obj.get("type") != "commit" or not valid_sha(obj.get("sha")):
        raise GateError("MAIN_INVALID")
    return obj["sha"]


def changed_files(api, number: int) -> tuple[str, ...]:
    files = []
    for page in range(1, 31):
        entries = api.get(f"{BASE}/pulls/{number}/files?per_page=100&page={page}")
        if not isinstance(entries, list) or len(entries) > 100:
            raise GateError("FILES_INVALID")
        for entry in entries:
            name = entry.get("filename") if isinstance(entry, dict) else None
            if not isinstance(name, str) or not name or name.startswith("/") or ".." in name.split("/"):
                raise GateError("FILES_INVALID")
            files.append(name)
        if len(entries) < 100:
            if not files or len(files) != len(set(files)):
                raise GateError("FILES_INVALID")
            return tuple(sorted(files))
    raise GateError("FILES_TRUNCATED")


def required_ci(files: tuple[str, ...]) -> tuple[str, ...]:
    found = set(files)
    required = []
    if any(f.startswith("backend/") for f in files) or CI["Backend CI"][0] in found:
        required.append("Backend CI")
    if any(f.startswith("mobile/") for f in files) or any(
        CI[n][0] in found for n in ("Flutter CI", "Android APK CI")
    ):
        required.extend(("Flutter CI", "Android APK CI"))
    if any(f in (".github/scripts/pr_status_sync.py", ".github/scripts/test_pr_status_sync.py") for f in files) or any(
        f in found for f in (
            ".github/workflows/pr-metadata-sync.yml",
            ".github/workflows/pr-metadata-tests.yml",
            ".github/workflows/pr-metadata-signal.yml",
        )
    ):
        required.append("PR metadata tests")
    if found & GATE_FILES:
        required.append("C236 governance offline tests")
    return tuple(required)


@dataclass(frozen=True)
class Snapshot:
    number: int
    head: str
    main: str
    head_branch: str
    files: tuple[str, ...]
    required: tuple[str, ...]


def snapshot(api, number: int, event_head: str) -> Snapshot:
    if not positive_int(number) or not valid_sha(event_head):
        raise GateError("EVENT_INVALID")
    live_main = main_sha(api)
    pr = api.get(f"{BASE}/pulls/{number}")
    if not isinstance(pr, dict) or pr.get("number") != number or pr.get("state") != "open" or pr.get("draft") is not False:
        raise GateError("PR_INVALID")
    base, head = pr.get("base"), pr.get("head")
    if not isinstance(base, dict) or not isinstance(head, dict):
        raise GateError("PR_INVALID")
    if (
        base.get("ref") != "main"
        or not isinstance(base.get("repo"), dict)
        or base["repo"].get("full_name") != REPO
        or base.get("sha") != live_main
        or not isinstance(head.get("repo"), dict)
        or head["repo"].get("full_name") != REPO
        or not isinstance(head.get("ref"), str)
        or not head["ref"]
        or head.get("sha") != event_head
        or pr.get("mergeable") is not True
    ):
        raise GateError("PR_STALE_OR_UNTRUSTED")
    comparison = api.get(f"{BASE}/compare/{live_main}...{event_head}")
    if (
        not isinstance(comparison, dict)
        or comparison.get("behind_by") != 0
        or comparison.get("status") not in ("ahead", "identical")
        or not isinstance(comparison.get("base_commit"), dict)
        or comparison["base_commit"].get("sha") != live_main
        or not isinstance(comparison.get("merge_base_commit"), dict)
        or comparison["merge_base_commit"].get("sha") != live_main
    ):
        raise GateError("MAIN_NOT_ANCESTOR")
    files = changed_files(api, number)
    known = {path for path, _job in CI.values()} | {".github/workflows/pr-metadata-sync.yml", ".github/workflows/pr-metadata-signal.yml", ".github/workflows/c236-governance-gate-pilot.yml"}
    if any(name.startswith(".github/workflows/") and name not in known for name in files):
        raise GateError("WORKFLOW_UNCOVERED")
    return Snapshot(number, event_head, live_main, head["ref"], files, required_ci(files))


def latest_runs(api, snap: Snapshot) -> dict:
    if not snap.required:
        return {}
    response = api.get(f"{BASE}/actions/runs?head_sha={snap.head}&event=pull_request&per_page=100")
    if not isinstance(response, dict) or type(response.get("total_count")) is not int:
        raise GateError("RUNS_INVALID")
    runs = response.get("workflow_runs")
    if response["total_count"] > MAX_RUNS or not isinstance(runs, list) or len(runs) > MAX_RUNS:
        raise GateError("RUNS_TRUNCATED")
    selected = {}
    for run in runs:
        if not isinstance(run, dict):
            raise GateError("RUNS_INVALID")
        name = run.get("name")
        if name not in snap.required:
            continue
        if (
            run.get("path") != CI[name][0]
            or run.get("event") != "pull_request"
            or run.get("head_sha") != snap.head
            or run.get("head_branch") != snap.head_branch
            or not isinstance(run.get("repository"), dict)
            or run["repository"].get("full_name") != REPO
            or not isinstance(run.get("head_repository"), dict)
            or run["head_repository"].get("full_name") != REPO
            or not positive_int(run.get("id"))
            or not positive_int(run.get("run_attempt"))
            or not positive_int(run.get("check_suite_id"))
        ):
            raise GateError("RUN_PROVENANCE_INVALID")
        associations = run.get("pull_requests")
        if not isinstance(associations, list) or not associations or not all(
            isinstance(item, dict)
            and type(item.get("number")) is int
            and item["number"] == snap.number
            and isinstance(item.get("head"), dict)
            and item["head"].get("sha") == snap.head
            and isinstance(item.get("base"), dict)
            and item["base"].get("ref") == "main"
            and item["base"].get("sha") == snap.main
            for item in associations
        ):
            raise GateError("RUN_ASSOCIATION_INVALID")
        previous = selected.get(name)
        if previous is None or (run["id"], run["run_attempt"]) > (previous["id"], previous["run_attempt"]):
            selected[name] = run
    return selected


def verify_run(api, snap: Snapshot, name: str, run: dict) -> Verdict | None:
    if run.get("status") != "completed":
        return Verdict("BLOCKED", "WAIT_CI_INCOMPLETE", snap.head, snap.main)
    if run.get("conclusion") != "success":
        state = "FAIL" if run.get("conclusion") in ("failure", "timed_out", "action_required") else "BLOCKED"
        return Verdict(state, "CI_NOT_SUCCESS", snap.head, snap.main)
    suite = api.get(f"{BASE}/check-suites/{run['check_suite_id']}")
    if (
        not isinstance(suite, dict)
        or suite.get("id") != run["check_suite_id"]
        or suite.get("head_sha") != snap.head
        or suite.get("status") != "completed"
        or suite.get("conclusion") != "success"
        or not isinstance(suite.get("app"), dict)
        or suite["app"].get("slug") != "github-actions"
    ):
        raise GateError("SUITE_PROVENANCE_INVALID")
    jobs_response = api.get(f"{BASE}/actions/runs/{run['id']}/jobs?per_page=100&filter=latest")
    if not isinstance(jobs_response, dict) or jobs_response.get("total_count") != 1:
        raise GateError("JOBS_INVALID")
    jobs = jobs_response.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise GateError("JOBS_INVALID")
    job = jobs[0]
    if (
        not isinstance(job, dict)
        or not positive_int(job.get("id"))
        or job.get("name") != CI[name][1]
        or job.get("head_sha") != snap.head
        or job.get("status") != "completed"
        or job.get("conclusion") != "success"
        or job.get("check_run_url") != f"https://api.github.com{BASE}/check-runs/{job['id']}"
    ):
        raise GateError("JOB_PROVENANCE_INVALID")
    check = api.get(f"{BASE}/check-runs/{job['id']}")
    if (
        not isinstance(check, dict)
        or check.get("id") != job["id"]
        or check.get("name") != CI[name][1]
        or check.get("head_sha") != snap.head
        or check.get("status") != "completed"
        or check.get("conclusion") != "success"
        or not isinstance(check.get("check_suite"), dict)
        or check["check_suite"].get("id") != run["check_suite_id"]
        or not isinstance(check.get("app"), dict)
        or check["app"].get("slug") != "github-actions"
        or not isinstance(check.get("details_url"), str)
        or not check["details_url"].startswith(f"https://github.com/{REPO}/actions/runs/{run['id']}/job/")
    ):
        raise GateError("CHECK_PROVENANCE_INVALID")
    return None


def evaluate_once(api, number: int, event_head: str) -> Verdict:
    """Return PASS only after a second full snapshot and CI attempt check."""
    try:
        first = snapshot(api, number, event_head)
        runs = latest_runs(api, first)
        for name in first.required:
            run = runs.get(name)
            if run is None:
                return Verdict("BLOCKED", "WAIT_CI_MISSING", first.head, first.main)
            result = verify_run(api, first, name, run)
            if result is not None:
                return result
        signatures = tuple((name, runs[name]["id"], runs[name]["run_attempt"]) for name in first.required)
        evidence = tuple((name, runs[name]["check_suite_id"], runs[name]["status"], runs[name]["conclusion"]) for name in first.required)
        second = snapshot(api, number, event_head)
        if second != first:
            raise GateError("CONCURRENT_PR_OR_MAIN")
        repeated = latest_runs(api, second)
        if tuple((name, repeated[name]["id"], repeated[name]["run_attempt"]) for name in second.required) != signatures:
            raise GateError("CONCURRENT_CI_ATTEMPT")
        if tuple((name, repeated[name]["check_suite_id"], repeated[name]["status"], repeated[name]["conclusion"]) for name in second.required) != evidence:
            raise GateError("CONCURRENT_CI_EVIDENCE")
        for name in second.required:
            result = verify_run(api, second, name, repeated[name])
            if result is not None:
                return result
        return Verdict("PASS", "CURRENT_EVIDENCE", first.head, first.main, signatures)
    except (GateError, KeyError, TypeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, GateError) else "API_PAYLOAD_INVALID"
        return Verdict("BLOCKED", code)


def run_gate(api, number: int, event_head: str, *, clock=time.monotonic, sleep=time.sleep) -> Verdict:
    deadline = clock() + POLL_LIMIT_SECONDS
    while True:
        result = evaluate_once(api, number, event_head)
        if not result.code.startswith("WAIT_CI_") or clock() >= deadline:
            return result
        sleep(POLL_SECONDS)


def main() -> int:
    try:
        with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as stream:
            event = json.load(stream)
        pr = event.get("pull_request") if isinstance(event, dict) else None
        if (
            event.get("repository", {}).get("full_name") != REPO
            or not isinstance(pr, dict)
            or not positive_int(pr.get("number"))
            or not isinstance(pr.get("head"), dict)
        ):
            raise GateError("EVENT_INVALID")
        result = run_gate(GitHubAPI(os.environ.get("GITHUB_TOKEN", "")), pr["number"], pr["head"].get("sha"))
    except Exception as exc:
        result = Verdict("BLOCKED", str(exc) if isinstance(exc, GateError) else "ENVIRONMENT_INVALID")
    print(f"C236_GATE_{result.state} code={result.code} head={result.head} main={result.main} runs={result.runs}")
    print("MASTER_AUTHORIZATION_SEPARATE")
    return 0 if result.state == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
