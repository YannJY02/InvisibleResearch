# Article Metadata Conversion

Status: **Exploratory Analysis**.

## Question

Can the large ArticleInfo CSV be converted to a smaller Parquet dataset while
preserving the fields needed by downstream exploration?

## Referenced inputs

- `$DATA_ROOT/raw/articleInfo.csv`
- Output: `$DATA_ROOT/processed/articleInfo.parquet`

## Run

```bash
DATA_ROOT=/path/to/data PYTHONPATH=src python research/article-metadata-conversion/analysis/convert_article_info.py
DATA_ROOT=/path/to/data PYTHONPATH=src jupyter lab research/article-metadata-conversion/notebooks/csv_to_parquet_converter.ipynb
```

The analysis command owns conversion-specific orchestration and validation; the
notebook is its interactive adapter. Neither changes the source CSV.
