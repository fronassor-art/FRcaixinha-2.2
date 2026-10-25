"""Trusted-default-branch PR status metadata updater; no PR code execution."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = "fronassor-art/FRcaixinha-2.2"
BASE = f"/repos/{REPO}"
START = "<!-- FR22_PR_CI:INICIO -->"
END = "<!-- FR22_PR_CI:FIM -->"
SHA = re.compile(r"^[0-9a-f]{40}$")
WORKFLOW_PATHS = {
    "Backend CI": ".github/workflows/backend-ci.yml",
    "Flutter CI": ".github/workflows/flutter-ci.yml",
    "Android APK CI": ".github/workflows/android-apk-ci.yml",
    "PR metadata tests": ".github/workflows/pr-metadata-tests.yml",
    "PR metadata signal": ".github/workflows/pr-metadata-signal.yml",
}
WORKFLOWS = tuple(WORKFLOW_PATHS)


class SyncError(Exception):
    """Stable public error code; never include API payloads or credentials."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise SyncError("API_REDIRECT_BLOCKED")


class GitHubAPI:
    def __init__(self, token: str):
        if not token:
            raise SyncError("TOKEN_MISSING")
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, path: str, method: str = "GET", payload: dict | None = None):
        if not path.startswith(BASE + "/") or method not in ("GET", "PATCH"):
            raise SyncError("API_REQUEST_INVALID")
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "https://api.github.com" + path,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        try:
            with self.opener.open(req, timeout=12) as response:
                return json.load(response)
        except SyncError:
            raise
        except urllib.error.HTTPError as exc:
            raise SyncError("API_FORBIDDEN" if exc.code in (401, 403) else "API_FAILED") from None
        except Exception:
            raise SyncError("API_FAILED") from None

    def get(self, path: str):
        return self.request(path)

    def patch(self, path: str, payload: dict):
        return self.request(path, "PATCH", payload)


def valid_sha(value) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def valid_pr(pr: dict) -> bool:
    try:
        return (
        isinstance(pr, dict)
        and pr.get("state") == "open"
        and pr.get("merged_at") is None
        and pr.get("base", {}).get("ref") == "main"
        and pr.get("base", {}).get("repo", {}).get("full_name") == REPO
        and pr.get("head", {}).get("repo", {}).get("full_name") == REPO
        and valid_sha(pr.get("head", {}).get("sha"))
        and isinstance(pr.get("body") or "", str)
        )
    except (AttributeError, TypeError):
        return False


def pr_number(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise SyncError("PR_NUMBER_INVALID")
    return value


def get_pr(api, number: int) -> dict:
    return api.get(f"{BASE}/pulls/{pr_number(number)}")


def discover_pr(api, event_name: str, event: dict):
    if event_name != "workflow_run":
        raise SyncError("EVENT_NOT_ALLOWED")
    listed = event.get("workflow_run", {})
    run_id = listed.get("id")
    if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id <= 0:
        raise SyncError("RUN_ID_INVALID")
    run = api.get(f"{BASE}/actions/runs/{run_id}")
    if (
        run.get("event") != "pull_request"
        or run.get("name") not in WORKFLOWS
        or run.get("path") != WORKFLOW_PATHS.get(run.get("name"))
        or run.get("repository", {}).get("full_name") != REPO
        or run.get("head_repository", {}).get("full_name") != REPO
        or not valid_sha(run.get("head_sha"))
    ):
        raise SyncError("RUN_UNTRUSTED")
    sha = run["head_sha"]
    candidates = []
    for entry in run.get("pull_requests") or []:
        number = entry.get("number")
        if isinstance(number, int) and not isinstance(number, bool) and number > 0:
            candidates.append(number)
    if not candidates:
        entries = api.get(f"{BASE}/commits/{sha}/pulls")
        candidates.extend(
            entry.get("number") for entry in entries if isinstance(entry.get("number"), int)
        )
    def matching(numbers):
        matches = []
        for number in set(numbers):
            pr = get_pr(api, number)
            if valid_pr(pr) and pr["head"]["sha"] == sha:
                matches.append(pr)
        return matches

    matches = matching(candidates)
    # Commit association may contain only a closed or outdated PR. Scan open PRs
    # when it produces no matching open PR for the run's exact HEAD.
    if not matches:
        for page in range(1, 6):
            entries = api.get(f"{BASE}/pulls?state=open&per_page=100&page={page}")
            if not isinstance(entries, list):
                raise SyncError("PR_DISCOVERY_INVALID")
            candidates.extend(
                entry.get("number") for entry in entries
                if isinstance(entry.get("number"), int) and not isinstance(entry.get("number"), bool)
            )
            if len(entries) < 100:
                break
        else:
            raise SyncError("PR_DISCOVERY_TRUNCATED")
        matches = matching(candidates)
    if len(matches) != 1:
        raise SyncError("PR_NOT_UNAMBIGUOUS")
    return matches[0], run.get("updated_at", "")


def changed_files(api, number: int) -> list[str]:
    names = []
    for page in range(1, 6):
        entries = api.get(f"{BASE}/pulls/{number}/files?per_page=100&page={page}")
        if not isinstance(entries, list):
            raise SyncError("PR_FILES_INVALID")
        for entry in entries:
            name = entry.get("filename")
            if not isinstance(name, str):
                raise SyncError("PR_FILES_INVALID")
            names.append(name)
        if len(entries) < 100:
            return names
    raise SyncError("PR_FILES_TRUNCATED")


def required_workflows(files: list[str]) -> tuple[str, ...]:
    required = []
    if any(f.startswith("backend/") or f == ".github/workflows/backend-ci.yml" for f in files):
        required.append("Backend CI")
    if any(f.startswith("mobile/") or f in (".github/workflows/flutter-ci.yml", ".github/workflows/android-apk-ci.yml") for f in files):
        required.extend(("Flutter CI", "Android APK CI"))
    if any(f.startswith(".github/scripts/pr_status_sync") or f.startswith(".github/scripts/test_pr_status_sync") or f in (".github/workflows/pr-metadata-sync.yml", ".github/workflows/pr-metadata-tests.yml", ".github/workflows/pr-metadata-signal.yml") for f in files):
        required.append("PR metadata tests")
    return tuple(required)


def latest_runs(api, sha: str, required: tuple[str, ...]) -> dict[str, dict]:
    result = api.get(f"{BASE}/actions/runs?head_sha={sha}&event=pull_request&per_page=100")
    if not isinstance(result, dict) or result.get("total_count", 0) > 100:
        raise SyncError("RUN_LIST_TRUNCATED")
    selected = {}
    for run in result.get("workflow_runs", []):
        name = run.get("name")
        if (
            name not in required
            or run.get("path") != WORKFLOW_PATHS.get(name)
            or run.get("event") != "pull_request"
            or run.get("head_sha") != sha
            or run.get("head_repository", {}).get("full_name") != REPO
            or not isinstance(run.get("id"), int)
        ):
            continue
        previous = selected.get(name)
        if previous is None or (run["id"], run.get("run_attempt", 0)) > (
            previous["id"], previous.get("run_attempt", 0)
        ):
            selected[name] = run
    return selected


def run_signature(runs: dict[str, dict]) -> tuple:
    def associations(run):
        return tuple(sorted(
            (entry.get("number"), entry["head"]["sha"], entry["base"]["sha"])
            for entry in run.get("pull_requests") or []
            if isinstance(entry, dict)
            and isinstance(entry.get("head"), dict)
            and isinstance(entry.get("base"), dict)
            and isinstance(entry["head"].get("sha"), str)
            and isinstance(entry["base"].get("sha"), str)
            and isinstance(entry.get("number"), int)
        ))
    return tuple(sorted(
        (name, run.get("id"), run.get("run_attempt"), run.get("status"),
         run.get("conclusion"), run.get("updated_at"), associations(run))
        for name, run in runs.items()
    ))


def run_proves_base(run: dict, pr: dict) -> bool:
    """Require GitHub's PR association to bind this run to current head and base."""
    return any(
        isinstance(entry, dict)
        and entry.get("number") == pr["number"]
        and isinstance(entry.get("head"), dict)
        and isinstance(entry.get("base"), dict)
        and entry["head"].get("sha") == pr["head"]["sha"]
        and entry["base"].get("sha") == pr["base"]["sha"]
        for entry in run.get("pull_requests") or []
    )


def needs_human_review(files: list[str]) -> bool:
    return any(
        name.startswith(".github/workflows/")
        or name in (".github/scripts/pr_status_sync.py", ".github/scripts/test_pr_status_sync.py")
        for name in files
    )


def classification(required: tuple[str, ...], runs: dict[str, dict],
                   pr: dict | None = None, human_review: bool = False) -> tuple[str, str]:
    if not required:
        return "BLOCKED", "Nenhuma CI aplicável ao escopo desta PR."
    if any(name not in runs or runs[name].get("status") != "completed" for name in required):
        return "PENDING", "Aguardando a conclusão das CIs aplicáveis ao HEAD atual."
    if pr is None or any(not run_proves_base(runs[name], pr) for name in required):
        return "BLOCKED", "A CI não comprovou correspondência com a base main atual."
    conclusions = [runs[name].get("conclusion") for name in required]
    if any(value in ("failure", "timed_out", "action_required") for value in conclusions):
        return "FAIL", "Uma CI aplicável falhou."
    if any(value != "success" for value in conclusions):
        return "BLOCKED", "Uma CI aplicável foi cancelada, ignorada ou não comprovada."
    if human_review:
        return "BLOCKED", "Alterações de workflow ou do sincronizador exigem revisão humana independente."
    return "PASS", "Todas as CIs aplicáveis ao HEAD e à base atuais foram concluídas com sucesso."


def upsert(body: str, block: str) -> str:
    if body.count(START) > 1 or body.count(END) > 1 or body.count(START) != body.count(END):
        raise SyncError("BODY_MARKERS_INVALID")
    if START not in body:
        return block + "\n\n" + body
    first = body.index(START)
    last = body.index(END)
    if last < first:
        raise SyncError("BODY_MARKERS_INVALID")
    return body[:first] + block + body[last + len(END):]


def render(pr: dict, required: tuple[str, ...], runs: dict[str, dict],
           timestamp: str, human_review: bool = False) -> str:
    status, reason = classification(required, runs, pr, human_review)
    sha = pr["head"]["sha"]
    base_sha = pr["base"].get("sha")
    if not valid_sha(base_sha):
        raise SyncError("BASE_SHA_INVALID")
    evidence = []
    for name in required:
        run = runs.get(name)
        if run is None:
            evidence.append(f"- {name}: execução ainda não localizada para este HEAD.")
            continue
        run_id = run["id"]
        evidence.append(
            f"- {name}: [execução #{run_id}](https://github.com/{REPO}/actions/runs/{run_id}), "
            f"tentativa {int(run.get('run_attempt', 1))}, "
            f"estado {run.get('status') if run.get('status') in ('queued', 'in_progress', 'completed', 'waiting', 'pending', 'requested') else 'desconhecido'}, "
            f"conclusão {run.get('conclusion') if run.get('conclusion') in ('success', 'failure', 'cancelled', 'skipped', 'timed_out', 'action_required', None) else 'desconhecida'}."
        )
    if not evidence:
        evidence.append("- Nenhuma CI aplicável configurada para os arquivos desta PR.")
    if not isinstance(timestamp, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", timestamp):
        timestamp = "NÃO VERIFICADA"
    return "\n".join((
        START,
        "## Estado automático da PR",
        "",
        f"**Status:** {status}. {reason}",
        f"**HEAD verificado:** `{sha}`.",
        f"**Base main observada:** `{base_sha}`.",
        f"**Confirmação da evidência:** {timestamp}.",
        "**Testes:** CONTAGEM NÃO VERIFICADA; o status do workflow não prova sozinho o total de testes.",
        "**Correspondência:** PASS exige associação explícita da CI ao HEAD e à base main atuais; ausência de prova resulta em BLOCKED.",
        "**Concorrência:** a API REST não fornece compare-and-swap forte para esta edição; leituras antes e depois não tornam a escrita atômica.",
        "",
        *evidence,
        "",
        "Este bloco não concede autorização de merge, implantação, migration ou operação financeira.",
        END,
    ))


def open_pr_numbers(api) -> list[int]:
    numbers = []
    for page in range(1, 6):
        entries = api.get(f"{BASE}/pulls?state=open&per_page=100&page={page}")
        if not isinstance(entries, list):
            raise SyncError("PR_DISCOVERY_INVALID")
        numbers.extend(
            entry.get("number") for entry in entries
            if isinstance(entry.get("number"), int) and not isinstance(entry.get("number"), bool)
        )
        if len(entries) < 100:
            return numbers
    raise SyncError("PR_DISCOVERY_TRUNCATED")


def _synchronize_pr(api, pr: dict, fallback_time: str) -> str:
    """Best-effort guarded update; REST PATCH lacks strong compare-and-swap."""
    if not valid_pr(pr):
        raise SyncError("PR_CLOSED_OR_UNTRUSTED")
    number = pr_number(pr.get("number"))
    files = changed_files(api, number)
    required = required_workflows(files)
    runs = latest_runs(api, pr["head"]["sha"], required)
    times = [run.get("updated_at", "") for run in runs.values()]
    timestamp = max(times) if times else fallback_time
    old_body = pr.get("body") or ""
    new_body = upsert(old_body, render(pr, required, runs, timestamp,
                                       needs_human_review(files)))
    if new_body == old_body:
        return "UNCHANGED"
    # REST PATCH has no strong compare-and-swap; re-read immediately before write.
    if run_signature(latest_runs(api, pr["head"]["sha"], required)) != run_signature(runs):
        raise SyncError("CONCURRENT_RUN")
    current = get_pr(api, number)
    if (
        not valid_pr(current)
        or current["head"]["sha"] != pr["head"]["sha"]
        or current["base"]["sha"] != pr["base"]["sha"]
        or current.get("updated_at") != pr.get("updated_at")
        or (current.get("body") or "") != old_body
    ):
        raise SyncError("CONCURRENT_CHANGE")
    api.patch(f"{BASE}/pulls/{number}", {"body": new_body})
    after = get_pr(api, number)
    if (
        not valid_pr(after)
        or after["head"]["sha"] != pr["head"]["sha"]
        or after["base"]["sha"] != pr["base"]["sha"]
        or (after.get("body") or "") != new_body
        or run_signature(latest_runs(api, pr["head"]["sha"], required)) != run_signature(runs)
    ):
        raise SyncError("POST_WRITE_CONFLICT")
    return "UPDATED"


def synchronize(api, event_name: str, event: dict) -> str:
    """Dispatch trusted signals; REST PATCH has no strong compare-and-swap."""
    if event.get("repository", {}).get("full_name") != REPO:
        raise SyncError("REPOSITORY_INVALID")
    if event_name == "workflow_run":
        listed = event.get("workflow_run", {})
        run_id = listed.get("id")
        if isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0:
            run = api.get(f"{BASE}/actions/runs/{run_id}")
            if (
                run.get("name") == "PR metadata signal"
                and run.get("path") == WORKFLOW_PATHS["PR metadata signal"]
                and run.get("event") == "push"
                and run.get("head_branch") == "main"
                and run.get("repository", {}).get("full_name") == REPO
                and run.get("head_repository", {}).get("full_name") == REPO
                and valid_sha(run.get("head_sha"))
            ):
                results = []
                for number in open_pr_numbers(api):
                    pr = get_pr(api, number)
                    if valid_pr(pr):
                        results.append(_synchronize_pr(api, pr, run.get("updated_at", "")))
                return "UPDATED" if "UPDATED" in results else "UNCHANGED"
    pr, fallback_time = discover_pr(api, event_name, event)
    return _synchronize_pr(api, pr, fallback_time)


def main() -> int:
    try:
        token = os.environ.get("GITHUB_TOKEN", "")
        with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as file:
            event = json.load(file)
        result = synchronize(GitHubAPI(token), os.environ["GITHUB_EVENT_NAME"], event)
        print("PR_METADATA_" + result)
        return 0
    except Exception as exc:
        code = str(exc) if isinstance(exc, SyncError) else "ENVIRONMENT_INVALID"
        print("PR_METADATA_" + code, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
