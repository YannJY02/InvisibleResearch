#!/usr/bin/env python3
from __future__ import annotations

import os
import csv
from pathlib import Path
from typing import List

DATA_ROOT = Path(os.environ['DATA_ROOT']).expanduser().resolve()
RAW_DIR = DATA_ROOT / 'raw' / 'openalex_data'
MERGED_CSV = DATA_ROOT / 'processed' / 'openalex_merged.csv'
MERGED_PARQUET = DATA_ROOT / 'processed' / 'openalex_merged.parquet'


def list_csv_files(root: Path) -> List[Path]:
    return sorted(root.rglob('*.csv'))


def count_csv_rows(file_path: Path) -> int:
    """Count data rows in a CSV (excluding header), robust to quoted newlines."""
    total = 0
    with open(file_path, 'r', encoding='utf-8', errors='replace', newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"', doublequote=True, escapechar='\\')
        _ = next(reader, None)  # skip header
        for _row in reader:
            total += 1
    return total


def count_parquet_rows(parquet_path: Path) -> int:
    """Count rows in Parquet using metadata; falls back to DuckDB if needed."""
    try:
        import pyarrow.parquet as pq  # type: ignore
        pf = pq.ParquetFile(str(parquet_path))
        return pf.metadata.num_rows
    except Exception:
        try:
            import duckdb  # type: ignore
            con = duckdb.connect()
            return con.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path.as_posix()}')").fetchone()[0]
        except Exception as e2:
            raise RuntimeError(f"Failed to count Parquet rows: {e2}")



# %%

# Compute counts + per-file breakdown and export
raw_files = list_csv_files(RAW_DIR)

# Per-file counts
file_counts = []
raw_total = 0
for fp in raw_files:
    rows = count_csv_rows(fp)
    file_counts.append((fp.relative_to(RAW_DIR).as_posix(), rows))
    raw_total += rows

# Prepare totals
merged_csv_rows = count_csv_rows(MERGED_CSV)
parquet_rows = count_parquet_rows(MERGED_PARQUET)

# Print aligned table
name_width = max((len(name) for name, _ in file_counts), default=10)
print(f"{'CSV File'.ljust(name_width)} | Rows")
print('-' * (name_width + 7))
for name, cnt in file_counts:
    print(f"{name.ljust(name_width)} | {cnt}")

# Export to CSV
from pathlib import Path
import csv as _csv
OUTPUT_CSV = Path(
    os.getenv(
        'OWNER_ARTIFACTS_DIR',
        'research/openalex-dataset-construction/artifacts',
    )
).resolve() / 'openalex_csv_row_counts_by_file.csv'
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
    w = _csv.writer(f)
    w.writerow(['file', 'rows'])
    for name, cnt in file_counts:
        w.writerow([name, cnt])
    # Append totals
    w.writerow(['TOTAL_raw_csv_files', raw_total])
    w.writerow(['TOTAL_merged_csv', merged_csv_rows])
    w.writerow(['TOTAL_parquet', parquet_rows])
print(f"\nExported per-file counts to: {OUTPUT_CSV}")

# Previous totals and parity checks
print('raw_csv_total_rows:', raw_total)
print('merged_csv_rows:', merged_csv_rows)
print('parquet_rows:', parquet_rows)
print('raw_vs_merged_equal:', raw_total == merged_csv_rows)
print('merged_vs_parquet_equal:', merged_csv_rows == parquet_rows)
print('raw_vs_parquet_equal:', raw_total == parquet_rows)
