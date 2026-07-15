from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq

from invisible_research.artifacts import (
    build_artifact_version,
    sha256_file,
    validate_artifact_record,
)


PROJECT_ROOT = Path(__file__).parents[1]


def test_artifact_version_uses_content_identity(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    moved = tmp_path / "moved.txt"
    changed = tmp_path / "changed.txt"
    original.write_bytes(b"stable")
    shutil.copy2(original, moved)
    changed.write_bytes(b"changed")

    original_record = build_artifact_version("fixture", original, ["source-a"])
    moved_record = build_artifact_version("fixture", moved, ["source-a"])
    changed_record = build_artifact_version("fixture", changed, ["source-a"])

    assert set(original_record) == {"id", "sha256", "location", "source"}
    assert original_record["sha256"] == hashlib.sha256(b"stable").hexdigest()
    assert moved_record["sha256"] == original_record["sha256"]
    assert moved_record["id"] == original_record["id"]
    assert moved_record["location"] != original_record["location"]
    assert changed_record["sha256"] != original_record["sha256"]
    assert changed_record["id"] != original_record["id"]


def test_retained_artifact_versions_link_derived_data_to_upstream_ids() -> None:
    record_paths = sorted((PROJECT_ROOT / "data/artifact-versions").glob("*.json"))
    records = [
        validate_artifact_record(json.loads(path.read_text(encoding="utf-8")))
        for path in record_paths
    ]
    records_by_id = {record["id"]: record for record in records}

    for record in records:
        location = str(record["location"])
        if location.startswith("data/component-manifests/"):
            manifest_path = PROJECT_ROOT / location
            assert manifest_path.is_file()
            assert sha256_file(manifest_path) == record["sha256"]

    derived_record_names = {
        "creator-sample-manifest.json",
        "creator-sample-clean.json",
        "creator-sample-clean-v2.json",
        "title-pred-lang-manifest.json",
    }
    for path in record_paths:
        if path.name not in derived_record_names:
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        assert record["source"]
        assert all(source_id in records_by_id for source_id in record["source"])


def test_openalex_merge_runs_through_shared_module(tmp_path: Path) -> None:
    input_dir = tmp_path / "raw" / "openalex_data"
    input_dir.mkdir(parents=True)
    (input_dir / "a.csv").write_text(
        "id,title,path\n1,Alpha,C:\\Users\\name\n",
        encoding="utf-8",
    )
    (input_dir / "b.csv").write_text("id,abstract\n2,Beta\n", encoding="utf-8")

    env = os.environ.copy()
    env["DATA_ROOT"] = str(tmp_path)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "invisible_research.acquisition.openalex_merge"],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    output = tmp_path / "processed" / "openalex_merged.parquet"
    stats = json.loads((tmp_path / "processed" / "openalex_merged_stats.json").read_text())
    input_record_paths = list(
        (tmp_path / "processed").glob("openalex_inputs.*.artifact.json")
    )
    assert len(input_record_paths) == 1
    input_record = json.loads(input_record_paths[0].read_text())
    record = json.loads((tmp_path / "processed" / "openalex_merged.artifact.json").read_text())
    table = pq.read_table(output)

    assert table.column_names == ["abstract", "id", "path", "title"]
    assert table.to_pylist() == [
        {
            "abstract": None,
            "id": "1",
            "path": "C:Usersname",
            "title": "Alpha",
        },
        {"abstract": "Beta", "id": "2", "path": None, "title": None},
    ]
    assert stats["total_files"] == 2
    assert stats["total_rows"] == 2
    assert set(input_record) == {"id", "sha256", "location", "source"}
    assert input_record["id"] == f"openalex-inputs@sha256:{input_record['sha256']}"
    assert input_record["location"] == str(input_dir.resolve())
    assert set(record) == {"id", "sha256", "location", "source"}
    assert record["id"] == f"openalex-merged@sha256:{record['sha256']}"
    assert record["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert record["location"] == str(output.resolve())
    assert record["source"] == [input_record["id"]]


def test_openalex_merge_writes_an_empty_parquet_for_header_only_input(
    tmp_path: Path,
) -> None:
    input_dir = tmp_path / "raw" / "openalex_data"
    input_dir.mkdir(parents=True)
    (input_dir / "empty.csv").write_text("id,title\n", encoding="utf-8")

    env = os.environ.copy()
    env["DATA_ROOT"] = str(tmp_path)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "invisible_research.acquisition.openalex_merge"],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    output = tmp_path / "processed" / "openalex_merged.parquet"
    stats = json.loads((tmp_path / "processed" / "openalex_merged_stats.json").read_text())
    record = json.loads((tmp_path / "processed" / "openalex_merged.artifact.json").read_text())

    assert pq.read_table(output).to_pylist() == []
    assert stats["total_rows"] == 0
    assert record["sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()


def test_openalex_merge_rejects_outputs_inside_the_input_tree(tmp_path: Path) -> None:
    input_dir = tmp_path / "raw" / "openalex_data"
    input_dir.mkdir(parents=True)
    (input_dir / "input.csv").write_text("id\n1\n", encoding="utf-8")
    output = input_dir / "openalex_merged.parquet"

    env = os.environ.copy()
    env["DATA_ROOT"] = str(tmp_path)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "invisible_research.acquisition.openalex_merge",
            "--output-parquet",
            str(output),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "must be outside the input directory" in result.stderr
    assert not output.exists()


def test_retired_top_level_paths_are_absent() -> None:
    retired_paths = (
        "run_pipeline.sh",
        "scripts",
        "config",
        "backup",
        "archive",
        "notebooks",
        "outputs",
        "Writing Report",
    )

    assert not [path for path in retired_paths if (PROJECT_ROOT / path).exists()]


def test_supervisor_meeting_reports_are_discoverable_and_non_authoritative() -> None:
    root_readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    context = (PROJECT_ROOT / "CONTEXT.md").read_text(encoding="utf-8")
    meeting_readme = PROJECT_ROOT / "meeting-reports/README.md"

    assert "[`meeting-reports/`](meeting-reports/README.md)" in root_readme
    assert "**Supervisor Meeting Report**:" in context
    assert meeting_readme.is_file()

    guidance = meeting_readme.read_text(encoding="utf-8")
    assert "YYYY-MM-DD-short-topic.md" in guidance
    assert "communication records" in guidance
    assert "Paper Analysis" in guidance
    assert "Designation Event" in guidance

    for target in (
        "../research/README.md",
        "../papers/README.md",
        "../inbox/README.md",
        "../CONTEXT.md",
    ):
        assert target in guidance
        assert (meeting_readme.parent / target).is_file()
