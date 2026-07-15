# Dimensions Dataset Construction

Status: **Exploratory Analysis**.

## Question

How can yearly Dimensions Communication exports be merged and transformed into
the current exploratory variables without changing their definitions?

## Referenced inputs

- `$DATA_ROOT/raw/dimensions_cs/publications_2000.csv` through
  `publications_2025.csv`
- `$DATA_ROOT/processed/scimagojr_communication_journal_1999_2024.csv`
- `$DATA_ROOT/processed/scimagoir_2025_Overall Rank_Communication.csv`
- Outputs under `$DATA_ROOT/processed/`

## Run

```bash
DATA_ROOT=/path/to/data PYTHONPATH=src python research/dimensions-dataset-construction/analysis/merge_dimensions.py
DATA_ROOT=/path/to/data PYTHONPATH=src python research/dimensions-dataset-construction/analysis/create_variables.py
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/dimensions-dataset-construction/notebooks/merge_dimension_2000_2025.ipynb
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/dimensions-dataset-construction/notebooks/dimension_create_variables.ipynb
```

The analysis commands retain the owner-specific orchestration and the notebooks
are interactive adapters. Their variable definitions remain exploratory and are
not paper-authorized results.
