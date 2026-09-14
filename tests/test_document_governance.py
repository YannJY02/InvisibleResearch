from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from invisible_research.document_governance import RULES_PATH, check


PROJECT_ROOT = Path(__file__).parents[1]


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def write_rules(root: Path, **changes) -> None:
    rules = {
        "document_extensions": [".md", ".qmd", ".rmd", ".ipynb", ".pdf", ".docx", ".html", ".pptx", ".tex", ".typ"],
        "path_rules": [
            {"pattern": r"README\.md", "description": "Repository entry"},
            {"pattern": r"docs/(governance|reference)/[a-z0-9]+(?:-[a-z0-9]+)*\.md", "description": "Repository guidance"},
            {"pattern": r"research/[a-z0-9-]+/(README\.md|notes/[a-z0-9-]+\.md|analysis/[a-z0-9-]+\.qmd)", "description": "Research owner documents"},
            {"pattern": r"papers/[a-z0-9-]+/(README\.md|literature/[a-z0-9-]+\.md|manuscript/[a-z0-9-]+\.Rmd)", "description": "Publication documents"},
        ],
        "required_files": ["README.md"],
        "link_exemptions": [],
        "protected_files": [],
    }
    rules.update(changes)
    write(root, RULES_PATH, json.dumps(rules))


class DocumentGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repository = Path(temporary.name)
        run_git(self.repository, "init", "--quiet")
        write(self.repository, "README.md", "# Research\n")
        write_rules(self.repository)

    def test_valid_owner_layout_and_local_link_forms(self) -> None:
        repository = self.repository
        write(repository, "research/journal-quality/README.md", "# Journal quality\n")
        write(repository, "research/journal-quality/analysis/quality-profile.qmd", "---\ntitle: Analysis\n---\n")
        write(repository, "papers/visibility/manuscript/conference-talk.Rmd", "# Talk\n")
        write(repository, "assets/chart (final).png", "fixture")
        write(repository, "README.md", """# Research
[Owner](research/journal-quality/)
[Directory](/research/journal-quality/)
[Query and anchor](research/journal-quality/README.md?raw=1#question)
![Figure](<assets/chart (final).png> "Figure title")
![Escaped figure](assets/chart%20\\(final\\).png)
[Angle](assets/chart%20(final).png)
[Research][owner]
[owner][]
[owner]: research/journal-quality/README.md "Owner entry"
[Multiline reference][paper]
[paper]:
  papers/visibility/manuscript/conference-talk.Rmd
[Site](https://example.org/missing)
[Email](mailto:research@example.org)
[Zotero](zotero://select/library/items/ABC)
[Fragment](#research)
`[Inline sample](missing.md)`
````markdown
[Fenced sample](missing.md)
```
[Still fenced](missing.md)
````
~~~markdown
[Other fence](missing.md)
~~~
<!-- [Hidden sample](missing.md) -->
[Template](papers/<paper-slug>/README.md)
[Template variable](papers/{paper}/README.md)
""")
        assert check(repository) == []

    def test_misplaced_documents_and_invalid_names_are_reported(self) -> None:
        repository = self.repository
        write(repository, "random-notes.md", "# Loose document\n")
        write(repository, "docs/reference/Bad_Name.md", "# Incorrect name\n")
        problems = check(repository)
        assert sum("placement or name" in problem for problem in problems) == 2
        assert any("random-notes.md" in problem for problem in problems)
        assert any("Bad_Name.md" in problem for problem in problems)

    def test_broken_inline_reference_and_escape_links_are_reported(self) -> None:
        repository = self.repository
        write(repository, "README.md", """[Missing](docs/reference/missing.md)
[Reference][broken]
[broken]: docs/reference/absent.md
[Undefined][never-defined]
[Outside](../outside.md)
""")
        problems = check(repository)
        assert any("README.md:1: broken local link" in problem for problem in problems)
        assert any("absent.md" in problem for problem in problems)
        assert any("undefined link reference [never-defined]" in problem for problem in problems)
        assert any("escapes the repository" in problem for problem in problems)

    def test_exemptions_match_only_the_exact_source_and_literal_target(self) -> None:
        repository = self.repository
        write(repository, "README.md", "[Download](data/download.csv)\n[Other](data/other.csv)\n")
        write(repository, "docs/reference/data-access.md", "[Download](../../data/download.csv)\n")
        write_rules(repository, link_exemptions=[{
            "source": "README.md", "target": "data/download.csv", "reason": "Private dataset downloaded separately",
        }])
        problems = check(repository)
        assert len(problems) == 2
        assert any("data/other.csv" in problem for problem in problems)
        assert any("data-access.md" in problem for problem in problems)

    def test_malformed_config_has_a_clear_diagnostic(self) -> None:
        repository = self.repository
        changes = [
            {"path_rules": [{"pattern": "[", "description": "Invalid regex"}]},
            {"link_exemptions": [{"source": "README.md", "target": "missing.md", "reason": ""}]},
            {"required_files": ["../outside.md"]},
            {"protected_files": [{"path": "README.md", "sha256": "invalid", "reason": "Frozen"}]},
            {"document_extensions": ".md"},
        ]
        for change in changes:
            with self.subTest(change=change):
                write_rules(repository, **change)
                with self.assertRaisesRegex(ValueError, "invalid configuration"):
                    check(repository)

    def test_deleted_worktree_files_are_not_checked_but_required_files_are_reported(self) -> None:
        repository = self.repository
        write(repository, "docs/reference/obsolete.md", "[Stale](missing.md)\n")
        run_git(repository, "add", ".")
        (repository / "docs/reference/obsolete.md").unlink()
        assert check(repository) == []
        (repository / "README.md").unlink()
        assert check(repository) == ["README.md: required file is missing"]

    def test_staged_markdown_and_targets_are_read_from_index(self) -> None:
        repository = self.repository
        write(repository, "README.md", "[Destination](docs/reference/target.md)\n")
        run_git(repository, "add", ".")
        # An unstaged target and an unstaged fix cannot repair the staged snapshot.
        write(repository, "docs/reference/target.md", "# Target\n")
        write(repository, "README.md", "# Fixed only in the worktree\n")
        assert check(repository) == []
        assert any("broken local link" in problem for problem in check(repository, staged=True))
        run_git(repository, "add", "docs/reference/target.md")
        assert check(repository, staged=True) == []
        # Deleting a staged target from disk does not delete it from the index.
        (repository / "docs/reference/target.md").unlink()
        assert check(repository, staged=True) == []

    def test_unstaged_rules_cannot_hide_a_staged_bad_path(self) -> None:
        repository = self.repository
        write(repository, "misplaced.md", "# Misplaced\n")
        run_git(repository, "add", ".")
        write_rules(repository, path_rules=[{"pattern": r".*\.md", "description": "Unstaged permissive rule"}])
        assert check(repository) == []
        assert any("misplaced.md: document placement" in problem for problem in check(repository, staged=True))

    def test_protected_bytes_are_verified_in_both_snapshots(self) -> None:
        repository = self.repository
        frozen_path = "papers/visibility/manuscript/conference-talk.Rmd"
        content = "# Frozen manuscript\r\n"
        (repository / frozen_path).parent.mkdir(parents=True)
        (repository / frozen_path).write_bytes(content.encode())
        write_rules(repository, protected_files=[{
            "path": frozen_path, "sha256": hashlib.sha256(content.encode()).hexdigest(), "reason": "Historical presentation",
        }])
        run_git(repository, "add", ".")
        assert check(repository) == []
        assert check(repository, staged=True) == []
        write(repository, frozen_path, "# Edited manuscript\n")
        assert any("protected file content changed" in problem for problem in check(repository))
        assert check(repository, staged=True) == []
        run_git(repository, "add", frozen_path)
        (repository / frozen_path).write_bytes(content.encode())
        assert check(repository) == []
        assert any("protected file content changed" in problem for problem in check(repository, staged=True))

    def test_ignored_generated_renders_are_found_with_a_bounded_scan(self) -> None:
        repository = self.repository
        write(repository, ".gitignore", "*.html\n*.pdf\n*.docx\n")
        misplaced = [
            "research/journal-quality/analysis/profile/profile.html",
            "research/journal-quality/analysis/profile.pdf",
            "papers/visibility/manuscript/talk.docx",
        ]
        excluded = [
            "research/journal-quality/artifacts/profile/profile.html",
            "research/journal-quality/analysis/profile/artifacts/run/profile.html",
            "research/journal-quality/analysis/profile/profile_files/help.html",
            "research/journal-quality/analysis/renv/help.html",
            "research/journal-quality/analysis/libs/help.html",
            "papers/visibility/manuscript/.quarto/cache.html",
            "inbox/school-rules.pdf",
        ]
        for path in misplaced + excluded:
            write(repository, path, "fixture")
        problems = check(repository)
        assert len(problems) == len(misplaced)
        assert all(any(path in problem and "ignored generated render" in problem for problem in problems) for path in misplaced)
        run_git(repository, "add", ".")
        assert check(repository, staged=True) == []

    def test_external_symlinks_are_never_read_as_documents_or_link_targets(self) -> None:
        repository = self.repository
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        external = Path(temporary.name)
        (external / "secret.md").write_text("# Private file\n")
        (repository / "docs/reference").mkdir(parents=True)
        (repository / "docs/reference/external.md").symlink_to(external / "secret.md")
        (repository / "outside").symlink_to(external, target_is_directory=True)
        write(repository, "README.md", "[Outside](outside/secret.md)\n")
        for staged in (False, True):
            if staged:
                run_git(repository, "add", ".")
            problems = check(repository, staged=staged)
            assert any("cannot check Markdown" in problem for problem in problems)
            assert any("broken local link: outside/secret.md" in problem for problem in problems)

    def test_deployment_state_is_reported_without_reading_its_contents(self) -> None:
        repository = self.repository
        write(repository, "research/journal-quality/analysis/profile/rsconnect/deployment.json", "not parsed")
        write(repository, "papers/visibility/manuscript/rsconnect/deployment.json", "not parsed")
        write(repository, "research/journal-quality/artifacts/profile/rsconnect/deployment.json", "allowed")
        for ignore in ("", "rsconnect/\n"):
            with self.subTest(ignore=ignore):
                write(repository, ".gitignore", ignore)
                problems = check(repository)
                assert len(problems) == 2
                assert all("deployment metadata is misplaced" in problem for problem in problems)

    def test_cli_accepts_root_and_returns_nonzero_for_a_bad_document(self) -> None:
        repository = self.repository
        write(repository, "misplaced.md", "# Misplaced\n")
        result = subprocess.run(
            [sys.executable, "-m", "invisible_research.document_governance", "check", "--root", str(repository)],
            cwd=repository, env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
            capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "misplaced.md: document placement or name" in result.stderr

    def test_actual_pre_commit_hook_blocks_only_invalid_staged_documents(self) -> None:
        repository = self.repository
        for path in (
            ".githooks/pre-commit",
            "src/invisible_research/__init__.py",
            "src/invisible_research/document_governance.py",
        ):
            (repository / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT_ROOT / path, repository / path)
        (repository / ".githooks/pre-commit").chmod(0o755)
        run_git(repository, "config", "core.hooksPath", ".githooks")
        run_git(repository, "config", "user.name", "Governance Test")
        run_git(repository, "config", "user.email", "governance-test@example.invalid")
        run_git(repository, "config", "commit.gpgsign", "false")
        write(repository, "misplaced.md", "# Draft\n")
        run_git(repository, "add", ".")
        # The real hook must set PYTHONPATH itself, independent of the test runner.
        env = {**os.environ, "PYTHONPATH": str(repository / "nonexistent-import-path"), "PYTHONDONTWRITEBYTECODE": "1"}
        rejected = subprocess.run(
            ["git", "commit", "-m", "test: reject misplaced document"],
            cwd=repository, env=env, capture_output=True, text=True,
        )
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
        self.assertIn("misplaced.md: document placement or name", rejected.stderr)
        missing_head = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=repository, capture_output=True,
        )
        self.assertNotEqual(missing_head.returncode, 0)

        destination = repository / "docs/reference/located.md"
        destination.parent.mkdir(parents=True)
        (repository / "misplaced.md").rename(destination)
        run_git(repository, "add", "-A")
        write(repository, "untracked-draft.md", "# Uncommitted draft\n")
        accepted = subprocess.run(
            ["git", "commit", "-m", "test: place document under its owner"],
            cwd=repository, env=env, capture_output=True, text=True,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        self.assertIn("Document governance passed (Git index).", accepted.stdout + accepted.stderr)
        self.assertIn("untracked-draft.md: document placement or name", accepted.stderr)
        self.assertIn("Working-tree document warnings", accepted.stderr)
        committed_paths = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=repository,
            check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        self.assertIn("docs/reference/located.md", committed_paths)
        self.assertNotIn("untracked-draft.md", committed_paths)
        self.assertNotIn("misplaced.md", committed_paths)

    def test_render_wrapper_keeps_paths_with_spaces_inside_owner_artifacts(self) -> None:
        fixture = self.repository / "project with spaces"
        relative_script = "research/ojs-journal-metadata/analysis/render_simple.sh"
        script = fixture / relative_script
        script.parent.mkdir(parents=True)
        shutil.copy2(PROJECT_ROOT / relative_script, script)
        source = script.parent / "ojs_journal_enrichment_simple_ver/ojs_journal_enrichment_simple_ver.qmd"
        source.parent.mkdir()
        source.write_text("# Fixture only\n", encoding="utf-8")
        stub_dir = fixture / "stub tools"
        stub_dir.mkdir()
        stub = stub_dir / "quarto"
        stub.write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" > "$CAPTURE_PATH"\n', encoding="utf-8")
        stub.chmod(0o755)
        captured = fixture / "captured arguments.txt"
        result = subprocess.run(
            ["sh", str(script)], cwd=fixture,
            env={**os.environ, "PATH": str(stub_dir) + os.pathsep + os.environ.get("PATH", ""), "CAPTURE_PATH": str(captured)},
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        arguments = captured.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(arguments), 4, arguments)
        self.assertEqual(arguments[0], "render")
        self.assertTrue(Path(arguments[1]).is_absolute())
        self.assertEqual(Path(arguments[1]).resolve(), source.resolve())
        self.assertEqual(arguments[2], "--output-dir")
        output_dir = Path(arguments[3])
        expected = script.parent.parent / "artifacts/ojs_journal_enrichment_simple_ver/rendered"
        self.assertTrue(output_dir.is_absolute())
        self.assertEqual(output_dir.resolve(), expected.resolve())
        self.assertTrue(output_dir.is_dir())

    def test_analysis_and_manuscript_markdown_links_are_checked(self) -> None:
        repository = self.repository
        paths = (
            "research/journal-quality/analysis/quality-profile.qmd",
            "papers/visibility/manuscript/conference-talk.Rmd",
        )
        for path in paths:
            write(repository, path, "[Missing source](missing-source.md)\n```{r}\n'[Example](code-only.md)'\n```\n")
        for staged in (False, True):
            with self.subTest(staged=staged):
                if staged:
                    run_git(repository, "add", ".")
                problems = check(repository, staged=staged)
                self.assertEqual(len(problems), 2, problems)
                for path in paths:
                    self.assertTrue(any(path in problem and "missing-source.md" in problem for problem in problems))
                self.assertFalse(any("code-only.md" in problem for problem in problems))

    def test_json_rules_cover_document_records_without_claiming_code_fixtures(self) -> None:
        repository = self.repository
        rules = json.loads((repository / RULES_PATH).read_text())
        rules["document_extensions"].append(".json")
        rules["path_rules"].append({
            "pattern": r"docs/(governance|reference)/[a-z0-9]+(?:-[a-z0-9]+)*\.json",
            "description": "Document records",
        })
        write_rules(repository, **rules)
        write(repository, "tests/fixtures/request_payload.json", '{"fixture": true}')
        write(repository, "src/invisible_research/config_defaults.json", '{"config": true}')
        write(repository, "docs/reference/source-record.json", '{"document": true}')
        self.assertEqual(check(repository), [])
        write(repository, "docs/loose-record.json", '{"document": true}')
        write(repository, "docs/reference/Bad_Name.json", '{"document": true}')
        for staged in (False, True):
            with self.subTest(staged=staged):
                if staged:
                    run_git(repository, "add", ".")
                problems = check(repository, staged=staged)
                self.assertEqual(len(problems), 2, problems)
                self.assertTrue(any("docs/loose-record.json" in problem for problem in problems))
                self.assertTrue(any("docs/reference/Bad_Name.json" in problem for problem in problems))

    def test_actual_rules_reject_office_documents_at_root_and_noncanonical_manuscript_names(self) -> None:
        repository = self.repository
        rules = json.loads((PROJECT_ROOT / RULES_PATH).read_text())
        rules["required_files"] = ["README.md"]
        rules["protected_files"] = []
        write_rules(repository, **rules)
        write(repository, "papers/visibility/manuscript/paper-draft.md", "# Paper draft\n")
        write(repository, "papers/visibility/manuscript/established_analysis.Rmd", "# Established source\n")
        self.assertEqual(check(repository), [])
        write(repository, "papers/visibility/manuscript/Final_V2.md", "# Incorrect name\n")
        write(repository, "notes.doc", "fixture office document")
        problems = check(repository)
        self.assertEqual(len(problems), 2, problems)
        self.assertTrue(any("Final_V2.md: document placement or name" in problem for problem in problems))
        self.assertTrue(any("notes.doc: document placement or name" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
