"""Candidate export retains current-ID objects without declaring old-ID merges."""

import csv
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

DIRECTORY = Path(__file__).parents[1] / "research" / "openalex-journal-baseline" / "analysis"
sys.path.insert(0, str(DIRECTORY))
SPEC = importlib.util.spec_from_file_location("candidate_csv", DIRECTORY / "export_source_retry_candidates.py")
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


def run_for(tmp_path, complete=True):
    run = tmp_path / "artifacts" / "source-retry-test"
    run.mkdir(parents=True)
    PIPELINE.base.save_json(run / "summary.json", {
        "status": "complete" if complete else "running",
        "verification": {"passed": complete}, "completed_at": "2026-10-01T04:00:00Z"})
    return run


def observation(run, phase, key, source, at, status="ok"):
    directory = run / "observed-json" / phase
    directory.mkdir(parents=True, exist_ok=True)
    raw = PIPELINE.base.dumps(source) + b"\n"
    source_path = directory / (key + ".json")
    source_path.write_bytes(raw)
    receipt = {"key": key, "phase": phase, "endpoint": "/sources/" + key,
               "status": status, "status_code": 200,
               "resolved_id": PIPELINE.base.source_id(source["id"]),
               "completed_at": at, "json_file": str(source_path.relative_to(run)),
               "json_bytes": len(raw), "json_sha256": PIPELINE.sha(raw),
               "attempts": [{"status_code": 200, "outcome": "ok"}]}
    path = run / "checkpoints" / phase / (key + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    PIPELINE.base.save_json(path, receipt)
    return source_path, path


def test_latest_current_id_object_deduplicated_with_full_selection_provenance(tmp_path):
    run = run_for(tmp_path)
    older = {"id": "https://openalex.org/S99", "type": "journal", "obsolete_field": "old"}
    latest = {"id": "https://openalex.org/S99", "type": "journal", "display_name": "中文,期刊",
              "summary_stats": {"h_index": 0, "nullable": None}, "topics": [
                  {"id": "T1", "count": 0, "nested": {"flag": False, "items": []}}],
              "ambiguous_string": "false", "literal_marker": "\\N", "empty": {}}
    one = observation(run, "pass1", "S1", older, "2026-10-01T10:00:00+08:00", "redirected")
    two = observation(run, "issn", "0011-9571", latest, "2026-10-01T03:00:00Z")
    original_bytes = {path: path.read_bytes() for pair in (one, two) for path in pair}
    result = PIPELINE.export_candidates(run)
    assert result["csv"]["rows"] == 1
    assert result["successful_observations"] == 2
    assert result["observations_deduplicated"] == 1
    assert result["verification"]["all_source_fields_roundtrip_equal"]
    assert "obsolete_field" not in result["field_types"]
    output = run / "candidate-csv"
    assert (output / "sources/S99.json").read_bytes() == two[0].read_bytes()
    with (output / "sources.csv").open(newline="") as stream:
        row = next(csv.DictReader(stream))
    restored = PIPELINE.base.unflatten({field: PIPELINE.base.decode_cell(row[field])
                                       for field in result["field_types"]})
    assert restored == latest
    assert row["source_id"] == row["resolved_id"] == "https://openalex.org/S99"
    provenance = PIPELINE.base.loads((output / "selection-provenance.json").read_bytes())
    assert provenance["selections"][0]["selected_receipt_file"] == "checkpoints/issn/0011-9571.json"
    assert len(provenance["selections"][0]["observations"]) == 2
    assert result["api_requests"] == 0
    assert "does not confirm" in result["identity_interpretation"]
    assert all(path.read_bytes() == raw for path, raw in original_bytes.items())
    # Repeating a finished export has the same CSV and full selection provenance.
    repeated = PIPELINE.export_candidates(run)
    assert repeated["csv"]["sha256"] == result["csv"]["sha256"]
    assert repeated["selection_provenance"]["sha256"] == result["selection_provenance"]["sha256"]


@pytest.mark.parametrize("change", ["body", "id", "phase", "timezone"])
def test_corrupted_receipts_or_objects_are_rejected_before_copy(tmp_path, change):
    run = run_for(tmp_path)
    source, path = observation(run, "merge", "S88", {"id": "https://openalex.org/S99"},
                               "2026-10-01T03:00:00Z")
    receipt = PIPELINE.base.loads(path.read_bytes())
    if change == "body":
        source.write_bytes(b"{}")
    elif change == "id":
        receipt["resolved_id"] = "S100"
    elif change == "phase":
        receipt["phase"] = "issn"
    else:
        receipt["completed_at"] = "2026-10-01T03:00:00"
    PIPELINE.base.save_json(path, receipt)
    with pytest.raises(ValueError):
        PIPELINE.export_candidates(run)
    assert not list((run / "candidate-csv/sources").glob("*.json"))
    assert not (run / "candidate-csv/sources.csv").exists()


def test_unfinished_retry_cannot_export(tmp_path):
    run = run_for(tmp_path, complete=False)
    with pytest.raises(ValueError, match="complete and verified"):
        PIPELINE.export_candidates(run)
    assert not (run / "candidate-csv").exists()


def test_receipt_source_cannot_escape_retry_run(tmp_path):
    run = run_for(tmp_path)
    source, path = observation(run, "issn", "0011-9571", {"id": "https://openalex.org/S99"},
                               "2026-10-01T03:00:00Z")
    outside = tmp_path / "outside.json"
    outside.write_bytes(source.read_bytes())
    receipt = PIPELINE.base.loads(path.read_bytes())
    receipt["json_file"] = str(outside)
    PIPELINE.base.save_json(path, receipt)
    with pytest.raises(ValueError, match="escapes"):
        PIPELINE.export_candidates(run)


def test_different_retry_summary_cannot_replace_derived_export(tmp_path):
    run = run_for(tmp_path)
    observation(run, "issn", "0011-9571", {"id": "https://openalex.org/S99"},
                "2026-10-01T03:00:00Z")
    PIPELINE.export_candidates(run)
    path = run / "summary.json"
    summary = PIPELINE.base.loads(path.read_bytes())
    summary["completed_at"] = "2026-10-02T00:00:00Z"
    PIPELINE.base.save_json(path, summary)
    with pytest.raises(ValueError, match="different retry summary"):
        PIPELINE.export_candidates(run)


def test_apfs_clone_has_independent_mutations_and_inode(tmp_path):
    if PIPELINE._CLONEFILE is None:
        pytest.skip("macOS clonefile is unavailable")
    source, target = tmp_path / "source.json", tmp_path / "derived.json"
    raw = b'{"id":"https://openalex.org/S99","topics":[]}'
    source.write_bytes(raw)
    method = PIPELINE.atomic_source_copy(source, target, raw)
    if method != "apfs_clonefile_copy_on_write":
        pytest.skip("Temporary filesystem does not support APFS cloning")
    assert source.stat().st_ino != target.stat().st_ino
    source.write_bytes(b"changed original")
    assert target.read_bytes() == raw
    target.write_bytes(b"changed derived")
    assert source.read_bytes() == b"changed original"


def test_ordinary_copy_fallback_refuses_insufficient_reserved_space(tmp_path, monkeypatch):
    source, target = tmp_path / "source.json", tmp_path / "derived.json"
    raw = b"verified body"
    source.write_bytes(raw)
    target.write_bytes(b"existing derived body")
    monkeypatch.setattr(PIPELINE, "clone_file", lambda source, target: False)
    monkeypatch.setattr(PIPELINE.shutil, "disk_usage", lambda path: SimpleNamespace(free=112))
    with pytest.raises(OSError, match="reserved"):
        PIPELINE.atomic_source_copy(source, target, raw, reserve_bytes=100)
    assert target.read_bytes() == b"existing derived body"
    assert not list(tmp_path.glob("*.clone-*"))


def test_ordinary_copy_fallback_with_enough_reserved_space_is_verified(tmp_path, monkeypatch):
    source, target = tmp_path / "source.json", tmp_path / "derived.json"
    raw = b"verified body"
    source.write_bytes(raw)
    monkeypatch.setattr(PIPELINE, "clone_file", lambda source, target: False)
    monkeypatch.setattr(PIPELINE.shutil, "disk_usage", lambda path: SimpleNamespace(free=113))
    assert PIPELINE.atomic_source_copy(source, target, raw, reserve_bytes=100) == "ordinary_byte_copy"
    assert target.read_bytes() == source.read_bytes() == raw
    assert target.stat().st_ino != source.stat().st_ino


def test_bad_clone_bytes_do_not_replace_existing_derived_file(tmp_path, monkeypatch):
    source, target = tmp_path / "source.json", tmp_path / "derived.json"
    raw = b"verified body"
    source.write_bytes(raw)
    target.write_bytes(b"existing derived body")
    def bad_clone(source, destination):
        destination.write_bytes(b"corrupt")
        return True
    monkeypatch.setattr(PIPELINE, "clone_file", bad_clone)
    with pytest.raises(ValueError, match="verified response bytes"):
        PIPELINE.atomic_source_copy(source, target, raw)
    assert target.read_bytes() == b"existing derived body"
    assert not list(tmp_path.glob("*.clone-*"))
