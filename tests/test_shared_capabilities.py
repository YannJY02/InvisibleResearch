from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).parents[1]


def run_shared_command(data_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DATA_ROOT"] = str(data_root)
    return subprocess.run(
        [str(PROJECT_ROOT / "run_pipeline.sh"), *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_rule_based_name_processing_runs_through_shared_command(
    tmp_path: Path,
) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    pq.write_table(
        pa.table({"creator": ["Ada Lovelace, Alan Turing", None]}),
        processed / "data_for_analysis.parquet",
    )

    result = run_shared_command(tmp_path, "author-names-rules")

    assert result.returncode == 0, result.stdout + result.stderr
    assert pq.read_table(processed / "name_clean.parquet").to_pylist() == [
        {"creator_clean": "ada lovelace, alan turing"},
        {"creator_clean": ""},
    ]


def test_validation_check_uses_data_root(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    final = tmp_path / "final"
    processed.mkdir()
    final.mkdir()
    (processed / "creator_sample.parquet").write_bytes(b"fixture")
    (final / "creator_sample_clean_v2.parquet").write_bytes(b"fixture")

    result = run_shared_command(tmp_path, "validation", "--check")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "系统检查通过" in result.stdout
    assert (tmp_path / "validation" / "reports").is_dir()
    assert (tmp_path / "logs").is_dir()
