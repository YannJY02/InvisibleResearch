from __future__ import annotations

import os
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).parents[1]
OWNER_NOTEBOOKS = {
    "article-metadata-conversion": {"csv_to_parquet_converter.ipynb"},
    "author-name-sampling": {"new_test_LLM_name_detect_parquet.ipynb"},
    "dimensions-dataset-construction": {
        "dimension_create_variables.ipynb",
        "merge_dimension_2000_2025.ipynb",
    },
    "openalex-dataset-construction": {
        "csv_parquet_rowcount_validation.ipynb",
        "csv_parquet_semantic_parity_validation.ipynb",
        "openalex_by_year_to_parquet.ipynb",
    },
    "scimago-openalex-coverage": {
        "merge_sjr_communication_1999_2024.ipynb",
        "scim_openalex_coverage_1999_2024.ipynb",
    },
}
OWNER_ANALYSES = {
    "article-metadata-conversion": {"convert_article_info.py"},
    "author-name-sampling": {
        "inspect_creators.py",
        "sample_article_authors.py",
        "sample_creators.py",
    },
    "dimensions-dataset-construction": {"create_variables.py", "merge_dimensions.py"},
    "openalex-dataset-construction": {
        "openalex_to_parquet.py",
        "validate_row_counts.py",
        "validate_semantic_parity.py",
    },
    "scimago-openalex-coverage": {"coverage.py", "match_by_issn.py", "merge_sjr.py"},
}


def run_owner_command(
    data_root: Path,
    relative_command: str,
    *args: str,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DATA_ROOT"] = str(data_root)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    env.update(extra_env or {})
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / relative_command), *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_all_exploratory_notebooks_have_named_owner_contracts() -> None:
    actual_notebooks: dict[str, set[str]] = {}
    actual_analyses: dict[str, set[str]] = {}
    for owner_dir in sorted((PROJECT_ROOT / "research").iterdir()):
        if not owner_dir.is_dir():
            continue
        readme = (owner_dir / "README.md").read_text(encoding="utf-8")
        assert "## Question" in readme
        assert "## Referenced inputs" in readme
        assert "## Run" in readme
        notebook_dir = owner_dir / "notebooks"
        actual_notebooks[owner_dir.name] = {
            path.name for path in notebook_dir.glob("*.ipynb")
        }
        for notebook_path in notebook_dir.glob("*.ipynb"):
            notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
            code_cells = [
                cell for cell in notebook["cells"] if cell["cell_type"] == "code"
            ]
            assert len(code_cells) == 1
            assert "".join(code_cells[0]["source"]).startswith(
                f"%run research/{owner_dir.name}/analysis/"
            )
            assert code_cells[0]["execution_count"] is None
            assert code_cells[0]["outputs"] == []
        actual_analyses[owner_dir.name] = {
            path.name for path in (owner_dir / "analysis").glob("*.py")
        }

    assert actual_notebooks == OWNER_NOTEBOOKS
    assert actual_analyses == OWNER_ANALYSES
    old_sources = subprocess.run(
        ["git", "ls-files", "notebooks", "scripts/03_analysis"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert old_sources.stdout == ""


def test_notebook_launch_commands_include_shared_source_path() -> None:
    for owner in OWNER_NOTEBOOKS:
        readme = (PROJECT_ROOT / "research" / owner / "README.md").read_text(
            encoding="utf-8"
        )
        notebook_commands = [
            line for line in readme.splitlines() if "jupyter lab" in line
        ]
        assert notebook_commands
        assert all("PYTHONPATH=src" in line for line in notebook_commands)


def test_reviewed_owner_scripts_do_not_duplicate_shared_or_local_helpers() -> None:
    dimensions_merge = (
        PROJECT_ROOT
        / "research/dimensions-dataset-construction/analysis/merge_dimensions.py"
    ).read_text(encoding="utf-8")
    assert "from invisible_research.acquisition.openalex_merge import" in dimensions_merge
    assert "def read_header" not in dimensions_merge
    assert "def merge_to_csv" not in dimensions_merge

    openalex_acquisition = (
        PROJECT_ROOT
        / "research/openalex-dataset-construction/analysis/openalex_to_parquet.py"
    ).read_text(encoding="utf-8")
    assert openalex_acquisition.count("def fetch_page") == 1
    assert openalex_acquisition.count("def flatten_work") == 1

    for name in ("validate_row_counts.py", "validate_semantic_parity.py"):
        validation = (
            PROJECT_ROOT
            / "research/openalex-dataset-construction/analysis"
            / name
        ).read_text(encoding="utf-8")
        assert "os.walk" not in validation

    dimensions_variables = (
        PROJECT_ROOT
        / "research/dimensions-dataset-construction/analysis/create_variables.py"
    ).read_text(encoding="utf-8")
    assert dimensions_variables.count("TOK = re.compile") == 1
    assert "def norm_tokens" not in dimensions_variables


def test_article_conversion_owner_runs_on_tiny_fixture(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    pd.DataFrame(
        {
            "id": ["1", "2"],
            "year": ["2020", "\\N"],
            "title1": ["First", "Second"],
        }
    ).to_csv(raw / "articleInfo.csv", index=False)

    result = run_owner_command(
        tmp_path,
        "research/article-metadata-conversion/analysis/convert_article_info.py",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    converted = pq.read_table(tmp_path / "processed/articleInfo.parquet")
    assert converted.num_rows == 2
    assert converted.column_names == ["id", "year", "title1"]


def test_dimensions_construction_owner_runs_on_tiny_fixture(tmp_path: Path) -> None:
    raw = tmp_path / "raw/dimensions_cs"
    raw.mkdir(parents=True)
    pd.DataFrame({"id": ["a"], "year": ["2000"]}).to_csv(
        raw / "publications_2000.csv", index=False
    )
    pd.DataFrame({"id": ["b"], "title": ["Second"]}).to_csv(
        raw / "publications_2001.csv", index=False
    )

    result = run_owner_command(
        tmp_path,
        "research/dimensions-dataset-construction/analysis/merge_dimensions.py",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    converted = pq.read_table(tmp_path / "processed/dimension_merged.parquet")
    assert converted.num_rows == 2
    assert set(converted.column_names) == {"id", "title", "year"}


def test_openalex_validation_owner_runs_on_tiny_fixture(tmp_path: Path) -> None:
    raw = tmp_path / "raw/openalex_data"
    processed = tmp_path / "processed"
    artifacts = tmp_path / "artifacts"
    raw.mkdir(parents=True)
    processed.mkdir()
    rows = pd.DataFrame({"id": ["a", "b"], "title": ["First", "Second"]})
    rows.to_csv(raw / "part.csv", index=False)
    rows.to_csv(processed / "openalex_merged.csv", index=False)
    pq.write_table(pa.Table.from_pandas(rows), processed / "openalex_merged.parquet")

    result = run_owner_command(
        tmp_path,
        "research/openalex-dataset-construction/analysis/validate_row_counts.py",
        extra_env={"OWNER_ARTIFACTS_DIR": str(artifacts)},
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = pd.read_csv(artifacts / "openalex_csv_row_counts_by_file.csv")
    assert report.tail(3)["rows"].tolist() == [2, 2, 2]


def test_author_sampling_owner_uses_data_root(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    pq.write_table(
        pa.table(
            {
                "id": [1, 2, 3],
                "identifier": ["a", "b", "c"],
                "title": ["A", "B", "C"],
                "creator": ["Ada Lovelace", "Alan Turing & Joan Clarke", None],
            }
        ),
        processed / "data_for_analysis.parquet",
    )

    result = run_owner_command(
        tmp_path,
        "research/author-name-sampling/analysis/sample_creators.py",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    sampled = pq.read_table(processed / "creator_sample.parquet").to_pandas()
    assert sampled[["id", "creator_count"]].to_dict("records") == [
        {"id": 1, "creator_count": 1},
        {"id": 2, "creator_count": 2},
    ]


def test_coverage_owner_writes_owner_local_artifacts(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    artifacts = tmp_path / "artifacts"
    raw.mkdir()
    processed.mkdir()
    pd.DataFrame(
        [
            {"Title": "Covered", "Sourceid": "1", "Type": "journal", "Issn": "1234-5678"},
            {"Title": "Missing", "Sourceid": "2", "Type": "journal", "Issn": "9999-9999"},
        ]
    ).to_csv(raw / "scimagojr_communication_journals.csv", sep=";", index=False)
    pq.write_table(
        pa.table({"issn": ["1234-5678"], "source_display_name": ["Elsewhere"]}),
        processed / "openalex_merged.parquet",
    )

    result = run_owner_command(
        tmp_path,
        "research/scimago-openalex-coverage/analysis/coverage.py",
        "--output-dir",
        str(artifacts),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    summary = pd.read_csv(artifacts / "scim_openalex_coverage_summary.csv")
    assert summary.to_dict("records") == [
        {
            "total_journals": 2,
            "covered_journals": 1,
            "unmatched_journals": 1,
            "coverage_rate": 0.5,
        }
    ]
