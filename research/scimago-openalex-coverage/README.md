# SCImago and OpenAlex Coverage

Status: **Exploratory Analysis**.

## Question

Which SCImago Communication journals are represented in the OpenAlex dataset by
ISSN or normalized source title?

## Referenced inputs

- `$DATA_ROOT/raw/SJR/**/*.csv`
- `$DATA_ROOT/raw/scimagojr_communication_journals.csv`
- `$DATA_ROOT/processed/openalex_merged.parquet`
- Owner outputs under ignored `research/scimago-openalex-coverage/artifacts/`

## Run

```bash
DATA_ROOT=/path/to/data PYTHONPATH=src python research/scimago-openalex-coverage/analysis/coverage.py
DATA_ROOT=/path/to/data PYTHONPATH=src python research/scimago-openalex-coverage/analysis/match_by_issn.py --per-journal
DATA_ROOT=/path/to/data PYTHONPATH=src python research/scimago-openalex-coverage/analysis/merge_sjr.py
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/scimago-openalex-coverage/notebooks/merge_sjr_communication_1999_2024.ipynb
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/scimago-openalex-coverage/notebooks/scim_openalex_coverage_1999_2024.ipynb
```

Coverage artifacts are regenerable and do not carry Paper Analysis authority.
