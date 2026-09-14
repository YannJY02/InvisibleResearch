from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from invisible_research import project_intake as intake


def issue(number=1):
    return {"number": number, "html_url": f"https://github.com/{intake.REPOSITORY}/issues/{number}",
            "title": "A real task", "body": "Evidence", "state": "open", "assignees": [],
            "labels": [], "created_at": "2026-09-01", "updated_at": "2026-09-01", "comments": 1}


def comment(body="Original"):
    return {"id": 10, "html_url": "https://github.com/comment/10", "user": {"login": "author"},
            "body": body, "created_at": "2026-09-01", "updated_at": "2026-09-01"}


class ProjectIntakeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "artifacts/project-management"
        (self.root / "inbox").mkdir()
        (self.root / "meeting-reports").mkdir()
        (self.root / "inbox/private transcript.txt").write_text("Secret original meeting text")
        (self.root / "meeting-reports/meeting.md").write_text("Report")

    def snapshot(self, current=None, comments=None, events=None):
        with patch.object(intake, "api_pages", side_effect=[
            [current or issue()], comments if comments is not None else [comment()], events or [],
        ]):
            return intake.github_snapshot()

    def test_pagination_get_only_and_pr_filtering(self):
        pull = {"number": 99, "pull_request": {}}
        responses = [ [[issue()], [pull]], [[comment()], []], [[]] ]
        with patch.object(intake.subprocess, "run", side_effect=[
            subprocess.CompletedProcess([], 0, json.dumps(pages), "") for pages in responses
        ]) as run:
            result = intake.github_snapshot()
        self.assertEqual([item["number"] for item in result["issues"]], [1])
        self.assertEqual(result["coverage"]["excluded_pull_requests"], 1)
        for call in run.call_args_list:
            self.assertEqual(call.args[0][:6], ["gh", "api", "--method", "GET", "--paginate", "--slurp"])
            self.assertTrue(call.args[0][6].startswith(f"repos/{intake.REPOSITORY}/issues"))
            self.assertNotIn("shell", call.kwargs)
        self.assertEqual(run.call_count, 3)

    def test_old_comment_edit_and_assignment_history_detected(self):
        before = {"github": self.snapshot(), "local_sources": {}, "collected_at": "earlier"}
        updated = issue()
        updated["assignees"] = [{"login": "new-owner"}]
        event = {"id": 30, "event": "assigned", "created_at": "2026-09-02",
                 "assignee": {"login": "new-owner"}}
        after = {"github": self.snapshot(updated, [comment("Edited older comment")], [event]),
                 "local_sources": {}}
        change = intake.changes(before, after)["issue_details"]["1"]
        self.assertEqual(change["comments"]["changed"], [10])
        self.assertEqual(change["assignees_added"], ["new-owner"])
        self.assertEqual(change["new_assignment_events"][0]["event"], "assigned")
        # Even when an assign/unassign pair leaves the current assignees unchanged,
        # events preserve the actual assignment history.
        unassigned = {**event, "id": 31, "event": "unassigned"}
        after["github"] = self.snapshot(events=[event, unassigned])
        change = intake.changes(before, after)["issue_details"]["1"]
        self.assertEqual(change["assignees_added"], [])
        self.assertEqual(len(change["new_assignment_events"]), 2)

    def test_failure_preserves_previous_good_snapshot(self):
        with patch.object(intake, "github_snapshot", return_value=self.snapshot()):
            self.assertEqual(intake.collect(self.root, self.output)["status"], "ok")
        baseline = self.output / "github-snapshot.json"
        original = baseline.read_bytes()
        with patch.object(intake.subprocess, "run", side_effect=[
            subprocess.CompletedProcess([], 0, json.dumps([[issue()]]), ""),
            subprocess.CompletedProcess([], 1, "", "Pagination failure"),
        ]):
            result = intake.collect(self.root, self.output)
        self.assertEqual(result["status"], "error")
        self.assertEqual(original, baseline.read_bytes())
        self.assertTrue(json.loads((self.output / "change-summary.json").read_text())["baseline_preserved"])

    def test_private_source_hashes_and_changes_without_modifying_originals(self):
        source = self.root / "inbox/private transcript.txt"
        original = source.read_bytes()
        with patch.object(intake, "github_snapshot", return_value=self.snapshot()):
            result = intake.collect(self.root, self.output)
            self.assertTrue(result["changes"]["baseline"])
            text = (self.output / "github-snapshot.json").read_text()
            self.assertNotIn("Secret original", text)
            self.assertIn(intake.digest(original), text)
            self.assertEqual(source.read_bytes(), original)
            (self.root / "meeting-reports/meeting.md").write_text("Changed report")
            result = intake.collect(self.root, self.output)
        self.assertEqual(result["changes"]["local_sources"]["changed"], ["meeting-reports/meeting.md"])

    def test_missing_comments_are_unavailable_not_deleted(self):
        before = {"github": self.snapshot(), "local_sources": {}, "collected_at": "earlier"}
        after = deepcopy(before)
        after["github"]["issues"][0]["comments"] = []
        result = intake.changes(before, after)
        self.assertEqual(result["issue_details"]["1"]["comments"]["unavailable"], [10])
        self.assertIn("deletion is not established", result["unavailable_meaning"])

    def test_comment_count_drift_or_malformed_pages_rejected(self):
        with self.assertRaises(ValueError):
            self.snapshot(comments=[])
        with patch.object(intake.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, json.dumps({"message": "bad response"}), ""
        )), self.assertRaises(ValueError):
            intake.api_pages(f"repos/{intake.REPOSITORY}/issues")

    def test_duplicate_pages_fail_instead_of_claiming_complete_coverage(self):
        current = issue()
        current["comments"] = 2
        with self.assertRaises(ValueError):
            self.snapshot(current, [comment(), comment()])

    def test_meeting_artifacts_and_non_markdown_are_excluded(self):
        artifacts = self.root / "meeting-reports/artifacts/export"
        artifacts.mkdir(parents=True)
        (artifacts / "generated.md").write_text("Generated export")
        (self.root / "meeting-reports/render.pdf").write_bytes(b"PDF")
        sources = intake.local_snapshot(self.root)
        self.assertEqual(set(sources), {"inbox/private transcript.txt", "meeting-reports/meeting.md"})

    def test_pending_deltas_survive_unchanged_collection_and_explicit_ack(self):
        with patch.object(intake, "github_snapshot", return_value=self.snapshot()):
            first = intake.collect(self.root, self.output)
            initial_id = first["change_id"]
            baseline_record = (self.output / "pending" / f"{initial_id}.json").read_bytes()
            (self.root / "meeting-reports/meeting.md").write_text("A newer report")
            second = intake.collect(self.root, self.output)
            third = intake.collect(self.root, self.output)
        self.assertIsNone(third["change_id"])
        self.assertEqual(set(third["pending_change_ids"]), {initial_id, second["change_id"]})
        self.assertEqual((self.output / "pending" / f"{initial_id}.json").read_bytes(), baseline_record)
        with patch.object(intake, "github_snapshot", side_effect=RuntimeError("Offline")):
            failed = intake.collect(self.root, self.output)
        self.assertEqual(failed["pending_change_ids"], third["pending_change_ids"])
        with patch.object(intake.subprocess, "run") as run:
            acknowledged = intake.acknowledge(self.root, self.output, initial_id)
        run.assert_not_called()
        self.assertEqual(acknowledged["pending_change_ids"], [second["change_id"]])
        self.assertEqual((self.output / "acknowledged" / f"{initial_id}.json").read_bytes(), baseline_record)
        # A repeated explicit acknowledgement is harmless and does not consume newer records.
        self.assertEqual(intake.acknowledge(self.root, self.output, initial_id), acknowledged)

    def test_pending_write_failure_does_not_advance_baseline(self):
        with patch.object(intake, "github_snapshot", return_value=self.snapshot()):
            intake.collect(self.root, self.output)
            before = (self.output / "github-snapshot.json").read_bytes()
            (self.root / "meeting-reports/meeting.md").write_text("Changed")
            writer = intake.atomic_json
            def fail_pending(path, value):
                if path.parent.name == "pending":
                    raise OSError("Disk write failed")
                return writer(path, value)
            with patch.object(intake, "atomic_json", side_effect=fail_pending):
                result = intake.collect(self.root, self.output)
        self.assertEqual(result["status"], "error")
        self.assertEqual((self.output / "github-snapshot.json").read_bytes(), before)

    def test_intermediate_upstream_comment_body_survives_later_edit(self):
        snapshots = [self.snapshot(comments=[comment(body)]) for body in ("Version A", "Version B", "Version C")]
        with patch.object(intake, "github_snapshot", side_effect=snapshots):
            intake.collect(self.root, self.output)
            intermediate = intake.collect(self.root, self.output)
            latest = intake.collect(self.root, self.output)
        baseline = json.loads((self.output / "github-snapshot.json").read_text())
        pending = json.loads((self.output / "pending" / f"{intermediate['change_id']}.json").read_text())
        self.assertEqual(baseline["github"]["issues"][0]["comments"][0]["body"], "Version C")
        self.assertEqual(pending["observation"]["github"]["issues"][0]["comments"][0]["body"], "Version B")
        self.assertEqual(pending["previous"]["github"]["issues"][0]["comments"][0]["body"], "Version A")
        self.assertEqual(pending["observation"]["github"]["issues"][0]["body"], "Evidence")
        self.assertIn(intermediate["change_id"], latest["pending_change_ids"])
        self.assertNotIn("Secret original meeting text", json.dumps(pending))

    def test_output_cannot_touch_originals_and_ack_rejects_path_traversal(self):
        for directory in ("inbox", "meeting-reports"):
            with self.assertRaises(ValueError):
                intake.collect(self.root, self.root / directory)
            self.assertFalse((self.root / directory / "change-summary.json").exists())
        with self.assertRaises(ValueError):
            intake.acknowledge(self.root, self.output, "../../inbox/private transcript.txt")


if __name__ == "__main__":
    unittest.main()
