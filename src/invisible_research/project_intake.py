"""Read-only evidence collection; never creates or synchronizes tracker issues.

GitHub bodies are retained locally as untrusted evidence for delayed reconciliation.
Local Inbox originals are represented only by filenames and content hashes.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


REPOSITORY = "invisibleinfo/invisible-research"
DEFAULT_OUTPUT = Path("docs/operations/artifacts/project-management")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(value: str | bytes) -> str:
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def api_pages(endpoint: str) -> list[dict]:
    """gh follows every Link page; a failed page invalidates the entire read."""
    result = subprocess.run(
        ["gh", "api", "--method", "GET", "--paginate", "--slurp", endpoint],
        capture_output=True, text=True, check=False, timeout=300,
    )
    if result.returncode:
        raise RuntimeError(f"GitHub GET failed for {endpoint} (exit {result.returncode})")
    pages = json.loads(result.stdout)
    if not isinstance(pages, list) or not pages or any(
        not isinstance(page, list) or any(not isinstance(item, dict) for item in page)
        for page in pages
    ):
        raise ValueError(f"Invalid GitHub pagination response for {endpoint}")
    return [item for page in pages for item in page]


def login(value: dict | None) -> str | None:
    return value.get("login") if value else None


def github_snapshot() -> dict:
    prefix = f"repos/{REPOSITORY}/issues"
    issues = []
    raw = api_pages(f"{prefix}?state=all&per_page=100")
    seen_numbers = set()
    for issue in raw:
        if "pull_request" in issue:
            continue
        number = issue["number"]
        if type(number) is not int or number < 1:
            raise ValueError("Invalid issue number")
        if number in seen_numbers:
            raise ValueError("Issue pagination contains duplicates; rerun for consistent coverage")
        seen_numbers.add(number)
        comments = api_pages(f"{prefix}/{number}/comments?per_page=100")
        events = api_pages(f"{prefix}/{number}/events?per_page=100")
        for records in (comments, events):
            if len({record["id"] for record in records}) != len(records):
                raise ValueError(f"Issue #{number} pagination contains duplicate records; rerun")
        if len(comments) != issue["comments"]:
            raise ValueError(f"Issue #{number} comment count changed during collection; rerun")
        issues.append({
            "number": number, "url": issue["html_url"], "title": issue["title"],
            "body": issue.get("body") or "",
            "body_sha256": digest(issue.get("body") or ""),
            "state": issue["state"], "state_reason": issue.get("state_reason"),
            "assignees": sorted(person["login"] for person in issue["assignees"]),
            "labels": sorted(label["name"] for label in issue["labels"]),
            "milestone": ({key: issue["milestone"].get(key) for key in ("number", "title", "due_on", "state")}
                          if issue.get("milestone") else None),
            "created_at": issue["created_at"], "updated_at": issue["updated_at"],
            "closed_at": issue.get("closed_at"),
            "comments": sorted([{
                "id": comment["id"], "url": comment["html_url"],
                "author": login(comment.get("user")),
                "created_at": comment["created_at"], "updated_at": comment["updated_at"],
                "body": comment.get("body") or "",
                "body_sha256": digest(comment.get("body") or ""),
            } for comment in comments], key=lambda item: item["id"]),
            "events": sorted([{
                "id": event["id"], "event": event["event"],
                "created_at": event["created_at"], "actor": login(event.get("actor")),
                "assignee": login(event.get("assignee")),
                "assigner": login(event.get("assigner")),
                "payload_sha256": digest(json.dumps(event, sort_keys=True)),
            } for event in events], key=lambda item: item["id"]),
        })
    return {
        "repository": REPOSITORY, "issues": sorted(issues, key=lambda item: item["number"]),
        "coverage": {
            "issues": len(issues), "excluded_pull_requests": len(raw) - len(issues),
            "comments": sum(len(item["comments"]) for item in issues),
            "events": sum(len(item["events"]) for item in issues),
            "pagination": "all Link pages for issues, comments and events",
            "scope": "all issues visible to the current gh identity; PRs excluded",
            "consistency": "sequential reads, not a point-in-time server transaction",
        },
    }


def local_snapshot(root: Path) -> dict:
    """Record private source identity only; never persist extracted source text."""
    sources = {}
    for directory in ("inbox", "meeting-reports"):
        base = root / directory
        if not base.is_dir():
            raise FileNotFoundError(f"Missing source directory: {directory}")
        for parent, directories, filenames in os.walk(base, followlinks=False):
            directories[:] = sorted(name for name in directories if not name.startswith(".")
                                    and not (directory == "meeting-reports" and name == "artifacts"))
            for name in [*directories, *filenames]:
                path = Path(parent) / name
                if path.is_symlink():
                    raise ValueError(f"Source symlink requires manual review: {path.relative_to(root)}")
            for name in sorted(filenames):
                path = Path(parent) / name
                if name.startswith(".") or (directory == "meeting-reports" and path.suffix != ".md"):
                    continue
                if directory == "inbox" and path.name == "README.md":
                    continue
                hasher = hashlib.sha256()
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        hasher.update(chunk)
                sources[path.relative_to(root).as_posix()] = hasher.hexdigest()
    return sources


def compare_records(before: list[dict], after: list[dict], key: str) -> dict:
    old = {item[key]: item for item in before}
    new = {item[key]: item for item in after}
    return {
        "new": sorted(new.keys() - old.keys()),
        "changed": sorted(k for k in new.keys() & old.keys() if new[k] != old[k]),
        "unavailable": sorted(old.keys() - new.keys()),
    }


def changes(previous: dict | None, current: dict) -> dict:
    if previous is None:
        return {"baseline": True, "message": "Initial inventory; no inferred task creation"}
    old_issues, new_issues = previous["github"]["issues"], current["github"]["issues"]
    details = {}
    old = {item["number"]: item for item in old_issues}
    for issue in new_issues:
        prior = old.get(issue["number"])
        if prior == issue:
            continue
        prior = prior or {"comments": [], "events": [], "assignees": []}
        old_event_ids = {event["id"] for event in prior["events"]}
        details[str(issue["number"])] = {
            "fields_changed": sorted(key for key in issue if key not in ("comments", "events")
                                     and prior.get(key) != issue[key]),
            "assignees_added": sorted(set(issue["assignees"]) - set(prior["assignees"])),
            "assignees_removed": sorted(set(prior["assignees"]) - set(issue["assignees"])),
            "comments": compare_records(prior["comments"], issue["comments"], "id"),
            "events": compare_records(prior["events"], issue["events"], "id"),
            "new_assignment_events": [event for event in issue["events"]
                                      if event["id"] not in old_event_ids
                                      and event["event"] in ("assigned", "unassigned")],
        }
    old_sources, new_sources = previous["local_sources"], current["local_sources"]
    return {
        "baseline": False, "previous_collected_at": previous["collected_at"],
        "issues": compare_records(old_issues, new_issues, "number"), "issue_details": details,
        "local_sources": {
            "new": sorted(new_sources.keys() - old_sources.keys()),
            "changed": sorted(k for k in new_sources.keys() & old_sources.keys()
                              if new_sources[k] != old_sources[k]),
            "unavailable": sorted(old_sources.keys() - new_sources.keys()),
        },
        "unavailable_meaning": "Not observed in this successful read; deletion is not established",
    }


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_output(root: Path, output: Path) -> None:
    if any(output.resolve().is_relative_to((root / source).resolve())
           for source in ("inbox", "meeting-reports")):
        raise ValueError("Collector output must be outside inbox and meeting-reports")


def pending_ids(output: Path) -> list[str]:
    return sorted(path.stem for path in (output / "pending").glob("*.json"))


def enqueue(output: Path, previous: dict | None, current: dict, summary: dict) -> str | None:
    delta = summary["changes"]
    if not (delta["baseline"] or any(delta["issues"].values()) or any(delta["local_sources"].values())):
        return None
    # Stable across retries before baseline advancement; distinct after later observations.
    identity = {"previous_collected_at": previous["collected_at"] if previous else None,
                "github": current["github"], "local_sources": current["local_sources"]}
    change_id = digest(json.dumps(identity, sort_keys=True))
    path = output / "pending" / f"{change_id}.json"
    if not path.exists() and not (output / "acknowledged" / path.name).exists():
        atomic_json(path, {"schema_version": 1, "change_id": change_id, "summary": summary,
                           "previous": previous, "observation": current})
    return change_id


def acknowledge(root: Path, output: Path, change_id: str) -> dict:
    """Caller must verify reconciliation before explicitly acknowledging its record."""
    validate_output(root, output)
    if len(change_id) != 64 or any(character not in "0123456789abcdef" for character in change_id):
        raise ValueError("change-id must be a 64-character lowercase SHA-256 identifier")
    source = output / "pending" / f"{change_id}.json"
    destination = output / "acknowledged" / source.name
    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)
    elif not destination.is_file():
        raise ValueError("Unknown change-id; no record acknowledged")
    return {"status": "ok", "acknowledged_change_id": change_id, "pending_change_ids": pending_ids(output)}


def collect(root: Path, output: Path) -> dict:
    validate_output(root, output)
    baseline = output / "github-snapshot.json"
    started = now()
    try:
        previous = json.loads(baseline.read_text()) if baseline.exists() else None
        if previous and (previous["schema_version"] != 1 or previous["github"]["repository"] != REPOSITORY):
            raise ValueError("Baseline schema or repository mismatch")
        github = github_snapshot()
        local = local_snapshot(root)
        current = {"schema_version": 1, "started_at": started, "collected_at": now(),
                   "github": github, "local_sources": local}
        summary = {"status": "ok", "collected_at": current["collected_at"],
                   "coverage": {**github["coverage"], "local_sources": len(local)},
                   "changes": changes(previous, current)}
        # Persist reconciliation evidence before advancing the latest observation.
        summary["change_id"] = enqueue(output, previous, current, summary)
        summary["pending_change_ids"] = pending_ids(output)
        atomic_json(output / "change-summary.json", summary)
        atomic_json(baseline, current)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
        summary = {"status": "error", "attempted_at": started,
                   "error": str(error), "baseline_preserved": True,
                   "pending_change_ids": pending_ids(output)}
        atomic_json(output / "change-summary.json", summary)
        return summary
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["collect", "acknowledge"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, help="Defaults beneath the repository's ignored artifacts")
    parser.add_argument("--change-id", help="Acknowledge only this pending record after reconciliation readback")
    args = parser.parse_args()
    if (args.command == "acknowledge") != bool(args.change_id):
        parser.error("--change-id is required only for acknowledge")
    try:
        root, output = args.root.resolve(), args.output or args.root / DEFAULT_OUTPUT
        result = (acknowledge(root, output, args.change_id) if args.command == "acknowledge"
                  else collect(root, output))
    except (OSError, ValueError) as error:
        result = {"status": "error", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
