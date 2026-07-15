# OpenAlex Dataset Construction

Status: **Exploratory Analysis**.

## Question

Can Communication works be acquired and converted to Parquet while preserving
row counts and meaningful CSV tokens?

## Referenced inputs

- `$DATA_ROOT/raw/openalex_data/**/*.csv`
- `$DATA_ROOT/raw/works-2025-09-07T08-08-59.csv` as the optional schema header
- Shared acquisition modules under `src/invisible_research/acquisition/`
- Merged outputs under `$DATA_ROOT/processed/`
- Regenerable validation reports under this owner's ignored `artifacts/`

## Run

```bash
DATA_ROOT=/path/to/data PYTHONPATH=src OPENALEX_MAILTO=you@example.org python research/openalex-dataset-construction/analysis/openalex_to_parquet.py
DATA_ROOT=/path/to/data PYTHONPATH=src python research/openalex-dataset-construction/analysis/validate_row_counts.py
DATA_ROOT=/path/to/data PYTHONPATH=src python research/openalex-dataset-construction/analysis/validate_semantic_parity.py
DATA_ROOT=/path/to/data PYTHONPATH=src OPENALEX_MAILTO=you@example.org jupyter lab research/openalex-dataset-construction/notebooks/openalex_by_year_to_parquet.ipynb
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/openalex-dataset-construction/notebooks/csv_parquet_rowcount_validation.ipynb
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/openalex-dataset-construction/notebooks/csv_parquet_semantic_parity_validation.ipynb
```

The notebooks adapt the external data and shared acquisition seam for this
experiment. The removed executed notebook was a Generated Artifact; Git history
retains it.
