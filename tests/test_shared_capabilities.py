from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).parents[1]


def run_shared_module(
    data_root: Path, module: str, *args: str
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DATA_ROOT"] = str(data_root)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_database_commands_require_explicit_mysql_uri(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("MYSQL_URI", None)
    env["DATA_ROOT"] = str(tmp_path)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    for module in (
        "invisible_research.acquisition.database_sample",
        "invisible_research.acquisition.database_extract",
    ):
        result = subprocess.run(
            [sys.executable, "-m", module],
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode != 0
        assert "MYSQL_URI is required" in result.stderr


def test_rule_based_name_processing_runs_through_shared_command(
    tmp_path: Path,
) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    pq.write_table(
        pa.table({"creator": ["Ada Lovelace, Alan Turing", None]}),
        processed / "data_for_analysis.parquet",
    )

    result = run_shared_module(
        tmp_path, "invisible_research.processing.author_names_rules"
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert pq.read_table(processed / "name_clean.parquet").to_pylist() == [
        {"creator_clean": "ada lovelace, alan turing"},
        {"creator_clean": ""},
    ]


def test_validation_check_uses_data_root(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    derived = tmp_path / "derived"
    processed.mkdir()
    derived.mkdir()
    (processed / "creator_sample.parquet").write_bytes(b"fixture")
    (derived / "creator_sample_clean_v2.parquet").write_bytes(b"fixture")

    result = run_shared_module(
        tmp_path, "invisible_research.validation.start", "--check"
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "系统检查通过" in result.stdout
    assert (tmp_path / "validation" / "reports").is_dir()
    assert (tmp_path / "logs").is_dir()
