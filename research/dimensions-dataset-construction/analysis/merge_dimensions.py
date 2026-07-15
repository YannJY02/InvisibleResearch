#!/usr/bin/env python3
from __future__ import annotations

from IPython.display import display
# Environment setup
from pathlib import Path
import os
import csv

import pandas as pd
import pyarrow as pa

from invisible_research.acquisition.openalex_merge import (
    inspect_columns,
    write_union_csv,
)

# Ensure duckdb is available
try:
    import duckdb  # type: ignore
except Exception:
    import sys, subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "duckdb>=0.10.0"], check=True)
    import duckdb  # type: ignore

DATA_ROOT = Path(os.environ['DATA_ROOT']).expanduser().resolve()
INPUT_DIR = DATA_ROOT / "raw" / "dimensions_cs"
OUTPUT_DIR = DATA_ROOT / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Inputs (2000–2025)
INPUT_FILES = [INPUT_DIR / f"publications_{year}.csv" for year in range(2000, 2026)]

# Outputs
OUTPUT_CSV = OUTPUT_DIR / "dimension_merged.csv"
OUTPUT_PARQUET = OUTPUT_DIR / "dimension_merged.parquet"

print("Data root:", DATA_ROOT)
print("Input dir:", INPUT_DIR)
print("Output dir:", OUTPUT_DIR)
print("Output CSV:", OUTPUT_CSV)
print("Output Parquet:", OUTPUT_PARQUET)


# %%

existing_files = [p for p in INPUT_FILES if p.exists()]
missing = [p for p in INPUT_FILES if not p.exists()]

if not existing_files:
    raise FileNotFoundError("No input files found under " + str(INPUT_DIR))

print(f"Existing files: {len(existing_files)}")
if missing:
    print("Missing files (skipped):")
    for m in missing[:10]:
        print(" -", m)
    if len(missing) > 10:
        print(f" ... (+{len(missing)-10} more)")

EXISTING_FILES = existing_files


# %%

UNION_COLUMNS, all_same, differing_files = inspect_columns(
    [str(path) for path in EXISTING_FILES]
)
print(f"Total unique columns: {len(UNION_COLUMNS)}")
print("All files share same columns:" if all_same else "Column differences detected.")
if differing_files:
    print("Examples of differing files (first 5):")
    for ex in differing_files[:5]:
        print(" -", ex)


# %%

# Increase CSV field size limit to accommodate long text fields
try:
    csv.field_size_limit(10_000_000)
except Exception:
    pass

rows_written = write_union_csv(
    [str(path) for path in EXISTING_FILES],
    UNION_COLUMNS,
    str(OUTPUT_CSV),
)
print(f"Merged CSV rows: {rows_written:,}")


# %%

# Build explicit column mapping for DuckDB as VARCHAR
columns_pairs = ", ".join([f"'{c}':'VARCHAR'" for c in UNION_COLUMNS])
columns_spec = "{" + columns_pairs + "}"

# Clean output parquet if exists
if OUTPUT_PARQUET.exists():
    OUTPUT_PARQUET.unlink()

con = duckdb.connect()
con.execute("PRAGMA threads=4")

safe_csv = str(OUTPUT_CSV).replace("'", "''")
safe_parquet = str(OUTPUT_PARQUET).replace("'", "''")

copy_sql = (
    f"COPY (SELECT * FROM read_csv('{safe_csv}', AUTO_DETECT=FALSE, HEADER=TRUE, "
    f"COLUMNS={columns_spec}, delim=',', quote='\"', escape='\"', strict_mode=FALSE, null_padding=TRUE, "
    f"maximum_line_size=20000000, parallel=FALSE)) TO '{safe_parquet}' (FORMAT 'parquet', COMPRESSION 'SNAPPY')"
)
print("Executing DuckDB COPY → Parquet ...")
con.execute(copy_sql)

# Count rows in Parquet
row_count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{safe_parquet}')").fetchone()[0]
con.close()
print(f"Parquet rows: {row_count:,}")


# %%

import pyarrow.parquet as pq
import duckdb

# Count logical rows in CSV using csv.reader (handles multiline fields correctly)
print("Counting CSV logical rows (this may take a moment)...")
csv_rows = 0
with OUTPUT_CSV.open('r', encoding='utf-8-sig', errors='replace', newline='') as f:
    reader = csv.reader(f, delimiter=',', quotechar='"', doublequote=True, escapechar='\\')
    next(reader, None)  # skip header
    for _ in reader:
        csv_rows += 1
print(f"CSV logical rows: {csv_rows:,}")

# Read Parquet metadata and show schema
parquet_file = pq.ParquetFile(OUTPUT_PARQUET)
parquet_rows = parquet_file.metadata.num_rows
print(f"Parquet rows: {parquet_rows:,}")
print(f"Parquet columns: {len(parquet_file.schema)}")
print(f"Row groups: {parquet_file.num_row_groups}")

# Validate row count consistency
if csv_rows == parquet_rows:
    print(f"✅ Row count validated: CSV and Parquet both have {csv_rows:,} records")
else:
    print(f"⚠️ Row count mismatch: CSV={csv_rows:,}, Parquet={parquet_rows:,}, diff={abs(csv_rows-parquet_rows):,}")

# Build a DuckDB view on Parquet for further checks
con = duckdb.connect()
parquet_path = str(OUTPUT_PARQUET).replace("'", "''")
con.execute(f"CREATE OR REPLACE VIEW v AS SELECT * FROM read_parquet('{parquet_path}')")

cols = [r[0] for r in con.execute("DESCRIBE SELECT * FROM v").fetchall()]

def quote_identifier(name: str) -> str:
    return '"' + name.replace('"','""') + '"'

# 1) id uniqueness (as requested)
if 'id' in cols:
    id_stats = con.execute(
        f"""
        SELECT
          COUNT(*)::BIGINT AS total,
          COUNT(DISTINCT {quote_identifier('id')})::BIGINT AS distinct_ids,
          SUM(CASE WHEN {quote_identifier('id')} IS NULL OR {quote_identifier('id')}='' THEN 1 ELSE 0 END)::BIGINT AS null_ids
        FROM v
        """
    ).fetch_df()
    total, distinct_ids, null_ids = int(id_stats['total'][0]), int(id_stats['distinct_ids'][0]), int(id_stats['null_ids'][0])
    print(f"\n[id] total={total:,}, distinct={distinct_ids:,}, nulls={null_ids:,}, unique={distinct_ids==total and null_ids==0}")

    # show any duplicated ids (top 10)
    if not (distinct_ids==total and null_ids==0):
        print("Examples of duplicated id:")
        print(con.execute(
            f"""
            SELECT {quote_identifier('id')} AS id, COUNT(*) AS c
            FROM v
            GROUP BY 1
            HAVING COUNT(*) > 1
            ORDER BY c DESC
            LIMIT 10
            """
        ).fetch_df())
else:
    print("\n[id] column not found; skip uniqueness check.")

# 2) DOI normalization duplicates (if doi exists)
if 'doi' in cols:
    con.execute(f"""
    CREATE OR REPLACE VIEW v_doi AS
    SELECT *,
           lower(regexp_replace(regexp_replace(coalesce({quote_identifier('doi')}, ''), '^https?://(dx\\.)?doi\\.org/', ''), '\\s+', '')) AS doi_norm
    FROM v
    """)
    dup_rows = con.execute(
        """
        SELECT COALESCE(SUM(c),0)::BIGINT FROM (
          SELECT COUNT(*) AS c
          FROM v_doi
          WHERE doi_norm <> ''
          GROUP BY doi_norm
          HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]
    print("\nDOI_norm duplicate rows:", f"{dup_rows:,}")
    print("Top duplicated doi_norm:")
    print(con.execute(
        """
        SELECT doi_norm, COUNT(*) AS c
        FROM v_doi
        WHERE doi_norm <> ''
        GROUP BY 1
        HAVING COUNT(*) > 1
        ORDER BY c DESC
        LIMIT 10
        """
    ).fetch_df())
else:
    print("\n[doi] column not found; skip DOI checks.")

# 3) Year range/distribution (if year-like column exists)
year_col = None
for cand in ['year', 'pub_year', 'publication_year']:
    if cand in cols:
        year_col = cand
        break

if year_col:
    print("\nYear stats:")
    print(con.execute(
        f"""
        SELECT
          MIN(try_cast({quote_identifier(year_col)} AS INTEGER)) AS min_year,
          MAX(try_cast({quote_identifier(year_col)} AS INTEGER)) AS max_year,
          SUM(CASE WHEN {quote_identifier(year_col)} IS NULL THEN 1 ELSE 0 END) AS null_years
        FROM v
        """
    ).fetch_df())

    print("Out-of-range/unparsable years (should be small or zero):")
    print(con.execute(
        f"""
        SELECT COUNT(*) AS bad_years
        FROM v
        WHERE try_cast({quote_identifier(year_col)} AS INTEGER) IS NULL
           OR try_cast({quote_identifier(year_col)} AS INTEGER) < 2000
           OR try_cast({quote_identifier(year_col)} AS INTEGER) > 2025
        """
    ).fetch_df())

    print("Counts by year:")
    print(con.execute(
        f"""
        SELECT try_cast({quote_identifier(year_col)} AS INTEGER) AS y, COUNT(*) AS c
        FROM v
        GROUP BY 1
        ORDER BY 1
        """
    ).fetch_df())
else:
    print("\n[year] column not found; skip year checks.")

# 4) Key field quality (null rate, distinct counts)
key_fields = [c for c in ['title','authors','source','journal','year'] if c in cols]
if key_fields:
    print("\nKey field quality:")
    for c in key_fields:
        df = con.execute(
            f"""
            SELECT
              COUNT(*)::BIGINT AS total,
              SUM(CASE WHEN {quote_identifier(c)} IS NULL OR {quote_identifier(c)}='' THEN 1 ELSE 0 END)::BIGINT AS nulls,
              COUNT(DISTINCT {quote_identifier(c)})::BIGINT AS distinct_vals
            FROM v
            """
        ).fetch_df()
        df['null_ratio'] = (df['nulls'] / df['total']).round(4)
        print(f"[{c}]"); display(df)
else:
    print("\nNo key fields to profile.")

# 5) Optional: exact-duplicate rows across all columns (may be slower)
try:
    all_rows = con.execute("SELECT COUNT(*) FROM v").fetchone()[0]
    distinct_rows = con.execute("SELECT COUNT(*) FROM (SELECT DISTINCT * FROM v)").fetchone()[0]
    print("\nExact duplicate rows (all-columns):", f"{all_rows - distinct_rows:,}")
except Exception as e:
    print("\nExact-duplicate check skipped:", str(e))

# Sample a few rows
print("\nSample rows from Parquet:")
sample_df = pd.read_parquet(OUTPUT_PARQUET, engine='pyarrow').head(5)
sample_df


# %%

import platform
import sys

# Library versions
print("Python:", sys.version.split()[0])
print("Platform:", platform.platform())
print("pandas:", pd.__version__)
print("pyarrow:", pa.__version__)
print("duckdb:", duckdb.__version__)

# Basic file stats
if OUTPUT_CSV.exists():
    print("CSV size (MB):", round(OUTPUT_CSV.stat().st_size / (1024**2), 2))
if OUTPUT_PARQUET.exists():
    print("Parquet size (MB):", round(OUTPUT_PARQUET.stat().st_size / (1024**2), 2))
