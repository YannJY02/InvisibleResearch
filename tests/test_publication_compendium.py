from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
PAPER_ROOT = PROJECT_ROOT / "papers/invisible-communication-science"
SOURCE_AUTHORITY_SHA256 = (
    "42395d4f28ddaf3d1f062d74d215e68fc93b691d47f2e6632943f976c65797b5"
)
EXPECTED_ARCHIVE_SOURCES = {
    "Writing Report/Report/draft/draft1.md",
    "Writing Report/Report/generate_report.js",
    "Writing Report/Report/package.json",
    "Writing Report/Slides/analyze_v2.Rmd",
    "Writing Report/Slides/ascorthemes_tutorial.md",
    "Writing Report/Slides/backup_note.md",
    "Writing Report/Slides/extract_stats.R",
    "Writing Report/Slides/material/output.md",
    "Writing Report/Slides/skeleton.Rmd",
    "Writing Report/Slides/speaker_notes.md",
    "Writing Report/Support Doc/activity_summary.md",
    "Writing Report/Support Doc/template/template_content.md",
}


def test_publication_compendium_preserves_source_authority_without_designation() -> None:
    analysis = PAPER_ROOT / "analysis/analyze.Rmd"
    assert hashlib.sha256(analysis.read_bytes()).hexdigest() == SOURCE_AUTHORITY_SHA256
    attributes = (PROJECT_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert (
        "papers/invisible-communication-science/analysis/analyze.Rmd "
        "-text -whitespace"
    ) in attributes

    readme = (PAPER_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Exploratory Analysis" in readme
    assert "Paper Analysis Candidate" in readme
    assert "does not" in readme

    assert (PAPER_ROOT / "governance/README.md").is_file()
    assert not list((PAPER_ROOT / "governance").rglob("designation-events.jsonl"))
    assert not list((PAPER_ROOT / "governance").rglob("*.yaml"))


def test_publication_compendium_contains_only_selected_active_sources() -> None:
    expected = {
        "README.md",
        "analysis/analyze.Rmd",
        "analysis/verify_inputs.py",
        "artifacts/README.md",
        "environment/README.md",
        "governance/README.md",
        "manuscript/ascor.css",
        "manuscript/ascor_header.png",
        "manuscript/ascor_side.png",
        "manuscript/etmaal2026_presentation.Rmd",
    }
    actual = {
        Path(path).relative_to(PAPER_ROOT.relative_to(PROJECT_ROOT)).as_posix()
        for path in subprocess.run(
            [
                "git",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                str(PAPER_ROOT.relative_to(PROJECT_ROOT)),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
    }
    assert actual == expected

    tracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "papers",
            "inbox",
            "data/artifact-versions",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    assert not any(path.endswith((".csv", ".pdf", ".docx")) for path in tracked)
    assert not any("history.png" in path for path in tracked)
    assert all((PROJECT_ROOT / path).stat().st_size < 5_000_000 for path in tracked)


def test_input_verifier_consumes_shared_artifact_contract(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    artifact = processed / "fixture.csv"
    artifact.write_bytes(b"id,title\n1,Fixture\n")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    record_path = tmp_path / "fixture.artifact.json"
    record_path.write_text(
        json.dumps(
            {
                "id": f"fixture@sha256:{digest}",
                "sha256": digest,
                "location": "$DATA_ROOT/processed/fixture.csv",
                "source": ["test fixture"],
            }
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["DATA_ROOT"] = str(tmp_path)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    result = subprocess.run(
        [
            sys.executable,
            str(PAPER_ROOT / "analysis/verify_inputs.py"),
            "--record",
            str(record_path),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"Verified fixture@sha256:{digest}" in result.stdout

    invalid_record = json.loads(record_path.read_text(encoding="utf-8"))
    invalid_record["id"] = "fixture@sha256:" + ("0" * 64)
    record_path.write_text(json.dumps(invalid_record), encoding="utf-8")
    rejected = subprocess.run(
        [
            sys.executable,
            str(PAPER_ROOT / "analysis/verify_inputs.py"),
            "--record",
            str(record_path),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "does not match its sha256" in rejected.stderr


def test_external_input_record_uses_portable_data_root_location() -> None:
    record = json.loads(
        (
            PROJECT_ROOT
            / "data/artifact-versions/dimensions-april2025-consolidated.json"
        ).read_text(encoding="utf-8")
    )
    assert set(record) == {"id", "sha256", "location", "source"}
    assert record["sha256"] == (
        "9361454fd9e9c6479181dd60d98d44038aa4b346bb74654f7750345db6f27ab2"
    )
    assert record["id"] == f"dimensions-april2025-consolidated@sha256:{record['sha256']}"
    assert record["location"] == (
        "$DATA_ROOT/processed/dimensions_april2025_consolidated.csv"
    )


def test_intake_and_paper_artifacts_are_local_only() -> None:
    ignored = subprocess.run(
        [
            "git",
            "check-ignore",
            "--no-index",
            "inbox/raw-message.eml",
            "papers/invisible-communication-science/artifacts/figure.png",
            "papers/invisible-communication-science/manuscript/libs/generated.js",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ignored.returncode == 0, ignored.stdout + ignored.stderr
    assert set(ignored.stdout.splitlines()) == {
        "inbox/raw-message.eml",
        "papers/invisible-communication-science/artifacts/figure.png",
        "papers/invisible-communication-science/manuscript/libs/generated.js",
    }
    inbox_readme = (PROJECT_ROOT / "inbox/README.md").read_text(encoding="utf-8")
    assert "non-authoritative" in inbox_readme
    assert "move, rename, or delete" in inbox_readme


def test_external_archive_manifest_and_human_review_are_separate() -> None:
    manifest = json.loads(
        (PROJECT_ROOT / "docs/writing-report-archive-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert {entry["source"] for entry in manifest} == EXPECTED_ARCHIVE_SOURCES
    for entry in manifest:
        assert set(entry) == {"source", "archive_location", "sha256"}
        assert entry["archive_location"].startswith(
            "GoogleDrive:InvisibleResearch/archive/writing-report-legacy/"
        )
        assert len(entry["sha256"]) == 64

    archive_index = (PROJECT_ROOT / "archive.md").read_text(encoding="utf-8")
    assert "writing-report-legacy" in archive_index
    assert "docs/writing-report-archive-manifest.json" in archive_index
    for field in (
        "Source",
        "Purpose",
        "Last known good",
        "Dependencies",
        "Reuse likelihood",
        "Notes",
    ):
        assert field in archive_index

    review = (PROJECT_ROOT / "docs/writing-report-human-review.md").read_text(
        encoding="utf-8"
    )
    for path in (
        "Writing Report/Report/Internship Report.docx",
        "Writing Report/Support Doc/chat history/history.png",
        "Writing Report/Support Doc/template/",
        "Writing Report/Slides/material/*.pdf",
    ):
        assert path in review
    assert "left untouched" in review
