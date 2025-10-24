Summary

Document Dimensions (2000–2025) publications CSV merge and Parquet conversion, with validation results and follow-ups.

Notebook
- notebooks/02_extraction/merge_dimension_2000_2025.ipynb

Key Results (latest run)
- Logical CSV rows (reader-based): 358,493
- Parquet rows: 358,493
- Columns: 76; Row groups: 3
- Size: CSV ≈ 2268.29 MB → Parquet ≈ 695.48 MB
- Primary key: id (uniqueness validated)

Method
- Union-of-columns across yearly CSVs (2000–2025); missing fields written as empty strings in the intermediate CSV
- Robust CSV parsing (handles multiline quoted fields); BOM-safe (utf-8-sig)
- Parquet conversion via DuckDB COPY with explicit VARCHAR mapping

Validation Checks
1) Row parity: CSV logical rows (reader-based) equals Parquet row count
2) id uniqueness: distinct == total and nulls == 0 (validated)
3) DOI normalization duplicates (if doi present): lower(trim(doi) without https://doi.org/) checked for duplicates
4) Year range/distribution (if year-like column exists): 2000–2025, counts by year, out-of-range/unparsable flagged
5) Key fields quality: null rate and distinct counts for title/authors/source/journal/year (when present)
6) Optional exact-duplicate rows: distinct full-rows check across all columns

How to Reproduce
1. Open the notebook and run all cells sequentially
2. Inspect the "Validation and Sampling" section outputs

Follow-ups
- Consider doi_norm-based deduplication where appropriate downstream
- Define acceptable null-ratio thresholds for key fields and alerting
- Schedule annual schema drift monitoring (per-year null rates by column)

