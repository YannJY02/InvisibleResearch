# Author Name Sampling

Status: **Exploratory Analysis**.

## Question

What author-field patterns and author-count groups should be inspected before
running shared author-name processing?

## Referenced inputs

- `$DATA_ROOT/processed/data_for_analysis.parquet`
- `$DATA_ROOT/processed/articleInfo.parquet`
- Shared sampling logic: `invisible_research.processing.author_sampling`
- Outputs: `$DATA_ROOT/processed/creator_sample.parquet` and
  `$DATA_ROOT/processed/new_creator_sample.parquet`

## Run

```bash
DATA_ROOT=/path/to/data PYTHONPATH=src python research/author-name-sampling/analysis/inspect_creators.py
DATA_ROOT=/path/to/data PYTHONPATH=src python research/author-name-sampling/analysis/sample_creators.py
DATA_ROOT=/path/to/data PYTHONPATH=src python research/author-name-sampling/analysis/sample_article_authors.py
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/author-name-sampling/notebooks/new_test_LLM_name_detect_parquet.ipynb
```

The notebook is an interactive adapter over the same owner command and shared
sampling capability; it is not a second implementation.
