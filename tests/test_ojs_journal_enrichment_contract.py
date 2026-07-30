from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
ANALYSIS_DIR = PROJECT_ROOT / "research" / "ojs-journal-metadata" / "analysis"
QMD_PATH = ANALYSIS_DIR / "ojs_journal_enrichment.qmd"
DISAGREEMENT_OWNER_DIR = PROJECT_ROOT / "research" / "ojs-journal-metadata"
DISAGREEMENT_ANALYSIS_DIR = DISAGREEMENT_OWNER_DIR / "analysis"
DISAGREEMENT_QMD_PATH = (
    DISAGREEMENT_ANALYSIS_DIR / "ojs_journal_disagreement_analysis.qmd"
)
FULL_RENDER_PATH = ANALYSIS_DIR / "render_full.sh"
DISAGREEMENT_RENDER_PATH = DISAGREEMENT_ANALYSIS_DIR / "render_disagreement.sh"


def test_full_pipeline_has_no_cross_language_conversion_layer():
    qmd = QMD_PATH.read_text()

    assert not (ANALYSIS_DIR / "ndjson_to_parquet.py").exists()
    for fragment in ("pyarrow", ".ndjson", "parquet-validation", "uv <-"):
        assert fragment not in qmd


def test_enrichment_produces_one_wide_master():
    qmd = QMD_PATH.read_text()
    render = FULL_RENDER_PATH.read_text()

    assert "pkp-ojs-multisource-enriched.csv.gz" in qmd
    assert "expand_candidate_fields" in qmd
    assert "_candidates__json" in qmd
    assert "length(match$candidates) > 1L" in qmd
    assert "deduplicate = FALSE" in qmd
    assert "seen_keys" not in qmd
    assert 'prefix, "_candidate_"' not in qmd
    for filename in (
        "openalex-source-index.csv.gz",
        "crossref-journal-index.csv.gz",
        "pkp-openalex-disagreement-audit.csv",
        "pkp-openalex-disagreement-summary.csv",
    ):
        assert filename not in qmd
        assert filename not in render


def test_disagreement_analysis_is_separate_and_offline():
    assert not (
        PROJECT_ROOT / "research" / "ojs-journal-disagreement-analysis"
    ).exists()
    assert DISAGREEMENT_RENDER_PATH.stat().st_mode & 0o111
    owner_readme = (DISAGREEMENT_OWNER_DIR / "README.md").read_text()
    for heading in ("## Question", "## Referenced inputs", "## Run"):
        assert heading in owner_readme
    assert "ojs-journal-metadata" in (
        PROJECT_ROOT / "research" / "README.md"
    ).read_text()

    enrichment = QMD_PATH.read_text()
    disagreement = DISAGREEMENT_QMD_PATH.read_text()
    render = DISAGREEMENT_RENDER_PATH.read_text()

    for fragment in (
        "identity_outcome",
        "metadata_disagreement_summary",
        "country_evidence_comparison",
    ):
        assert fragment not in enrichment
        assert fragment in disagreement

    assert "pkp-ojs-multisource-enriched.csv.gz" in disagreement
    assert "is_missing_value(left) || is_missing_value(right)" in disagreement
    assert 'category = "unmapped_nonmissing"' in disagreement
    assert "match(row_identity(sample_spec), row_identity(audit))" in disagreement
    assert "file.rename(temporary_path, path)" in disagreement
    assert "ojs_journal_disagreement_analysis" in disagreement
    assert "ojs_journal_disagreement_analysis" in render
    assert 'test -d "$R_LIBS_USER"' in render
    assert 'mkdir -p "$render_source_dir" "$R_LIBS_USER"' not in render
    for fragment in (
        "api.openalex.org",
        "api.crossref.org",
        "OPENALEX_API_KEY",
        "CROSSREF_MAILTO",
    ):
        assert fragment not in disagreement
