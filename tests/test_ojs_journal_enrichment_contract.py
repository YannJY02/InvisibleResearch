from pathlib import Path


ANALYSIS_DIR = (
    Path(__file__).parents[1]
    / "research"
    / "ojs-journal-metadata"
    / "analysis"
)
QMD_PATH = ANALYSIS_DIR / "ojs_journal_enrichment.qmd"


def test_full_pipeline_has_no_python_parquet_conversion_layer():
    qmd = QMD_PATH.read_text()

    assert not (ANALYSIS_DIR / "ndjson_to_parquet.py").exists()
    for fragment in ("pyarrow", ".parquet", ".ndjson", "parquet-validation", "uv <-"):
        assert fragment not in qmd


def test_full_pipeline_declares_compressed_tabular_outputs():
    qmd = QMD_PATH.read_text()

    for filename in (
        "pkp-ojs-multisource-enriched.csv.gz",
        "openalex-source-index.csv.gz",
        "crossref-journal-index.csv.gz",
        "pkp-openalex-disagreement-audit.csv.gz",
    ):
        assert filename in qmd
