# Historical Dimensions Workflow Notes

Status: historical snapshot moved from the former `docs/README.md` on 2026-09-14.
The run counts below are previously recorded observations, not a new validation.
Use the [owner instructions](../../research/dimensions-dataset-construction/README.md)
for current commands and external `DATA_ROOT` locations.

## Dimensions CSV Merge → Parquet

- Owner analysis: `research/dimensions-dataset-construction/analysis/merge_dimensions.py`
- Notebook adapter: `research/dimensions-dataset-construction/notebooks/merge_dimension_2000_2025.ipynb`
- Inputs: `data/raw/dimensions_cs/publications_2000.csv … publications_2025.csv`
- Outputs:
  - Intermediate CSV (retained): `data/processed/dimension_merged.csv`
  - Parquet (Snappy): `data/processed/dimension_merged.parquet`
- Method:
  - Union-of-columns across yearly CSVs; missing columns written as empty strings in the CSV stage
  - Robust CSV parsing (handles multiline quoted fields) and BOM-safe reading (`utf-8-sig`)
  - Parquet conversion via DuckDB `COPY ... FORMAT parquet` with explicit `VARCHAR` mapping
- Validation (latest run):
  - Logical CSV rows (reader-based): 358,493
  - Parquet rows: 358,493
  - Columns: 76; Row groups: 3
  - Size: CSV ≈ 2268.29 MB → Parquet ≈ 695.48 MB
  - Primary key: `id` (uniqueness validated in the notebook)
- How to run:
  1) Open the notebook and run all cells
  2) Inspect the "Validation and Sampling" section for integrity checks (row counts, `id` uniqueness, DOI normalization duplicates, year distribution, key field quality)

---

## Dimension Variables Creation (analysis-ready)

- Owner analysis: `research/dimensions-dataset-construction/analysis/create_variables.py`
- Notebook adapter: `research/dimensions-dataset-construction/notebooks/dimension_create_variables.ipynb`
- Input: `data/processed/dimension_merged.parquet`
- Output: `data/processed/dimension_data_for_analysis.parquet` (Snappy)
- Method summary:
  - Print full schema and a small preview
  - Derive/retain variables in separate, academically documented sections; each module includes `id`
  - Variables and column blocks:
    - Invisibility block: `invisibility` (1 if `times_cited==0` else 0), plus `times_cited`, `date`
    - Geographic/Institutional: `research_org_country_names`, `research_org_names`, `research_org_types`
    - Topical: `concepts`, `concepts_scores`
    - Disciplinary: `issn`, `isbn`, and binary `disciplinary` matched against SJR ISSN list (`data/processed/scimagojr_communication_journal_1999_2024.csv`)
    - OA: `open_access`
    - Controls: `document_type`, `type`, `authors_count`, `reference_ids`, `referenced_pubs`
  - Column ordering groups the above blocks for readability; only the final Parquet is written
- Quality checks printed by the notebook:
  - Missingness per column; `id` uniqueness
  - Domain sanity: `invisibility`∈{0,1}; non-negativity for `times_cited`, `authors_count`
  - Identifier format sanity: ISSN/ISBN token length checks after normalization
  - Base-level normalized DOI duplicates (if DOI exists upstream)
