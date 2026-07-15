#!/usr/bin/env python3
from __future__ import annotations

import os
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Iterable, Set

DATA_ROOT = Path(os.environ['DATA_ROOT']).expanduser().resolve()
RAW_DIR = DATA_ROOT / 'raw' / 'openalex_data'
MERGED_CSV = DATA_ROOT / 'processed' / 'openalex_merged.csv'
MERGED_PARQUET = DATA_ROOT / 'processed' / 'openalex_merged.parquet'
REPORTS_DIR = Path('research/openalex-dataset-construction/artifacts').resolve()

SUSPICIOUS_TOKENS: List[str] = [
    "", "NA", "N.A.", "N/A", "NULL", "NaN", "\\N", "None", "null", "nan", "Na"
]

# Utility to list raw CSV files

def list_csv_files(root: Path) -> List[Path]:
    return sorted(root.rglob('*.csv'))

# Robust CSV reader factory

def open_csv_reader(file_path: Path) -> Iterable[List[str]]:
    f = open(file_path, 'r', encoding='utf-8', errors='replace', newline='')
    reader = csv.reader(f, delimiter=',', quotechar='"', doublequote=True, escapechar='\\')
    return f, reader

# Read header and data row count only

def read_header_and_count_rows(file_path: Path) -> Tuple[List[str], int]:
    total = 0
    f, reader = open_csv_reader(file_path)
    try:
        header = next(reader, None)
        if header is None:
            return [], 0
        for _ in reader:
            total += 1
        return [c.strip() for c in header], total
    finally:
        f.close()

# Count suspicious tokens per-column for a single CSV file (only for columns present)

def count_tokens_in_csv(file_path: Path, columns: List[str], tokens: Set[str]) -> Tuple[Dict[str, Counter], int]:
    per_col: Dict[str, Counter] = {c: Counter() for c in columns}
    row_count = 0
    f, reader = open_csv_reader(file_path)
    try:
        header = next(reader, None)
        if header is None:
            return per_col, 0
        header = [c.strip() for c in header]
        name_to_idx = {name: i for i, name in enumerate(header)}
        present_columns = [c for c in columns if c in name_to_idx]

        for row in reader:
            row_count += 1
            row_len = len(row)
            for col in present_columns:
                idx = name_to_idx[col]
                if idx < row_len:
                    val = row[idx]
                else:
                    # Truncated row; treat as empty string to avoid IndexError
                    val = ""
                if val in tokens:
                    per_col[col][val] += 1
        return per_col, row_count
    finally:
        f.close()

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
print('Prepared environment. Raw dir exists:', RAW_DIR.exists())


# %%

# 1) Discover raw CSV files and build union of columns
raw_files = list_csv_files(RAW_DIR)
print(f"Discovered {len(raw_files)} raw CSV files")

union_columns: Set[str] = set()
per_file_headers: Dict[str, List[str]] = {}
per_file_rowcounts: Dict[str, int] = {}

for fp in raw_files:
    header, nrows = read_header_and_count_rows(fp)
    if header:
        union_columns.update(header)
    per_file_headers[fp.as_posix()] = header
    per_file_rowcounts[fp.as_posix()] = nrows

union_columns_sorted: List[str] = sorted(union_columns)
print(f"Union columns: {len(union_columns_sorted)}")

# 2) Scan raw CSVs for suspicious token counts per column
from copy import deepcopy

raw_token_counts: Dict[str, Counter] = {c: Counter() for c in union_columns_sorted}
raw_total_rows = 0

for fp in raw_files:
    per_col_counts, nrows = count_tokens_in_csv(fp, union_columns_sorted, set(SUSPICIOUS_TOKENS))
    raw_total_rows += nrows
    for col in union_columns_sorted:
        raw_token_counts[col].update(per_col_counts[col])

print('Raw total rows (data rows across files):', raw_total_rows)

# 3) Read merged CSV and compute suspicious token counts per column
merged_token_counts: Dict[str, Counter] = {c: Counter() for c in union_columns_sorted}
merged_total_rows = 0
f_m, rdr_m = open_csv_reader(MERGED_CSV)
try:
    header_m = next(rdr_m, None)
    if not header_m:
        raise RuntimeError('Merged CSV has no header')
    header_m = [c.strip() for c in header_m]
    if set(header_m) != set(union_columns_sorted):
        print('WARNING: merged CSV columns differ from union columns sizes:', len(header_m), 'vs', len(union_columns_sorted))
    name_to_idx_m = {name: i for i, name in enumerate(header_m)}
    for row in rdr_m:
        merged_total_rows += 1
        row_len = len(row)
        for col in union_columns_sorted:
            idx = name_to_idx_m.get(col)
            val = row[idx] if idx is not None and idx < row_len else ""
            if val in SUSPICIOUS_TOKENS:
                merged_token_counts[col][val] += 1
finally:
    f_m.close()

print('Merged CSV rows:', merged_total_rows)


# %%

# Ensure duckdb is available in this kernel and provide identifier escaping
try:
    import duckdb as _duckdb
except ModuleNotFoundError:
    import sys, subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', 'duckdb>=0.10.0'])
    import duckdb as _duckdb

# Provide escape_identifier if missing
def _escape_identifier_py(name: str) -> str:
    s = '"' + str(name).replace('"', '""') + '"'
    return s

if not hasattr(_duckdb, 'escape_identifier'):
    _duckdb.escape_identifier = _escape_identifier_py  # type: ignore

print('duckdb version:', getattr(_duckdb, '__version__', 'unknown'))


# %%

# 4) Parquet: NULL counts and suspicious string counts via DuckDB
import duckdb
con = duckdb.connect()

# Load schema (column names) from merged CSV to enforce order
csv_cols = union_columns_sorted

# Construct per-column NULL count queries and token counts
susp_list = SUSPICIOUS_TOKENS

# Build a temporary view for Parquet
parquet_path = MERGED_PARQUET.as_posix().replace("'", "''")
con.execute(f"CREATE OR REPLACE VIEW v_parquet AS SELECT * FROM read_parquet('{parquet_path}')")

# Get NULL counts
null_counts = {}
for col in csv_cols:
    q = f"SELECT COUNT(*) FROM v_parquet WHERE {duckdb.escape_identifier(col)} IS NULL"
    null_counts[col] = con.execute(q).fetchone()[0]

# Count suspicious tokens that survived as strings in Parquet
parquet_token_counts = {c: Counter() for c in csv_cols}
for col in csv_cols:
    for tok in susp_list:
        # We count literal matches; for empty string we use col = ''
        if tok == "":
            q = f"SELECT COUNT(*) FROM v_parquet WHERE {duckdb.escape_identifier(col)} = ''"
        else:
            # Compare as string; DuckDB will cast to VARCHAR
            q = f"SELECT COUNT(*) FROM v_parquet WHERE {duckdb.escape_identifier(col)} = ?"
        cnt = con.execute(q, [tok] if tok != "" else []).fetchone()[0]
        if cnt:
            parquet_token_counts[col][tok] = cnt

print('Parquet counts computed.')


# %%

# 5) Build discrepancy reports
from math import isfinite
import pandas as pd

# Compute missing-column-induced empty counts expected in merged CSV
missing_column_rows: Dict[str, int] = {c: 0 for c in union_columns_sorted}
for col in union_columns_sorted:
    miss_total = 0
    for fpath, hdr in per_file_headers.items():
        if col not in hdr:
            miss_total += per_file_rowcounts[fpath]
    missing_column_rows[col] = miss_total

# Helper to get count safely
get_raw = lambda c, t: int(raw_token_counts.get(c, Counter()).get(t, 0))
get_mrg = lambda c, t: int(merged_token_counts.get(c, Counter()).get(t, 0))
get_par = lambda c, t: int(parquet_token_counts.get(c, Counter()).get(t, 0))
get_null = lambda c: int(null_counts.get(c, 0))

# Long-form per-token report
rows_token: List[Dict[str, object]] = []
for col in union_columns_sorted:
    for tok in SUSPICIOUS_TOKENS:
        raw_cnt = get_raw(col, tok)
        mrg_cnt = get_mrg(col, tok)
        par_cnt = get_par(col, tok)
        null_cnt = get_null(col)
        miss_rows = missing_column_rows[col]
        expected_merged_empty = (get_raw(col, "") + miss_rows) if tok == "" else None
        lost_to_parquet = max(0, mrg_cnt - par_cnt)
        rows_token.append({
            'column': col,
            'token': tok,
            'raw_count': raw_cnt,
            'merged_count': mrg_cnt,
            'parquet_string_count': par_cnt,
            'parquet_null_count': null_cnt,
            'missing_column_rows': miss_rows,
            'expected_merged_empty': expected_merged_empty,
            'lost_to_parquet': lost_to_parquet,
            'flag_token_loss': lost_to_parquet > 0,
        })

df_token = pd.DataFrame(rows_token)

# Per-column summary
summary_rows: List[Dict[str, object]] = []
for col in union_columns_sorted:
    merged_empty = get_mrg(col, "")
    parquet_empty_str = get_par(col, "")
    empty_lost_to_null = max(0, merged_empty - parquet_empty_str)
    null_cnt = get_null(col)
    miss_rows = missing_column_rows[col]
    expected_merged_empty = get_raw(col, "") + miss_rows
    merged_empty_diff_vs_expected = merged_empty - expected_merged_empty
    # Sum of losses across all suspicious tokens
    sum_lost_tokens = int(sum(max(0, get_mrg(col, tok) - get_par(col, tok)) for tok in SUSPICIOUS_TOKENS))
    # Decide flags
    flag_null_inflation = null_cnt > empty_lost_to_null
    flag_merged_empty_mismatch = merged_empty_diff_vs_expected != 0
    flagged = (sum_lost_tokens > 0) or flag_null_inflation or flag_merged_empty_mismatch

    # Top lost token
    top_tok = None
    top_loss = 0
    for tok in SUSPICIOUS_TOKENS:
        loss = max(0, get_mrg(col, tok) - get_par(col, tok))
        if loss > top_loss:
            top_loss = loss
            top_tok = tok

    summary_rows.append({
        'column': col,
        'parquet_null_count': null_cnt,
        'merged_empty_count': merged_empty,
        'parquet_empty_as_string_count': parquet_empty_str,
        'empty_lost_to_null_min': empty_lost_to_null,
        'missing_column_rows': miss_rows,
        'expected_merged_empty': expected_merged_empty,
        'merged_empty_diff_vs_expected': merged_empty_diff_vs_expected,
        'sum_lost_suspicious_tokens': sum_lost_tokens,
        'flag_null_inflation': flag_null_inflation,
        'flag_merged_empty_mismatch': flag_merged_empty_mismatch,
        'flagged': flagged,
        'top_lost_token': top_tok,
        'top_lost_token_count': top_loss,
    })

df_summary = pd.DataFrame(summary_rows).sort_values(['flagged','parquet_null_count','sum_lost_suspicious_tokens'], ascending=[False, False, False])

# Export
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
per_token_csv = REPORTS_DIR / 'semantic_parity_per_token.csv'
per_col_csv = REPORTS_DIR / 'semantic_parity_summary_by_column.csv'
df_token.to_csv(per_token_csv, index=False)
df_summary.to_csv(per_col_csv, index=False)

print('Wrote reports:')
print(' -', per_token_csv)
print(' -', per_col_csv)

# Display top suspicious columns
df_summary.head(20)


# %%

# 6) Row-level spot checks for misalignment or token-to-NULL coercion

import re

SAMPLE_SIZE = 2000
SAMPLE_COLUMNS: List[str] = []  # leave empty to auto-select a few columns

# Decide join key
candidate_key = 'id'

# Inspect merged CSV header for key presence
f_tmp, rdr_tmp = open_csv_reader(MERGED_CSV)
try:
    header_tmp = next(rdr_tmp, None)
    if not header_tmp:
        raise RuntimeError('Merged CSV has no header')
    header_tmp = [c.strip() for c in header_tmp]
finally:
    f_tmp.close()

join_by_id = candidate_key in header_tmp

# Pick sample columns
if SAMPLE_COLUMNS:
    cols_for_sample = [c for c in SAMPLE_COLUMNS if c in header_tmp][:10]
else:
    # Auto-pick up to 10: include id if present, plus top flagged columns
    cols_for_sample = ([] if not join_by_id else [candidate_key])
    top_cols = df_summary.sort_values(['flagged','sum_lost_suspicious_tokens','parquet_null_count'], ascending=[False, False, False])['column'].tolist()
    for c in top_cols:
        if c not in cols_for_sample:
            cols_for_sample.append(c)
        if len(cols_for_sample) >= 10:
            break

print('Join by id:', join_by_id)
print('Sample columns:', cols_for_sample)

# Alias sanitizer to avoid dots and special chars in SQL aliases
sanitize = lambda s: re.sub(r'[^A-Za-z0-9_]', '_', s)

# Build sampling queries using DuckDB to compare merged CSV vs Parquet
csv_path = MERGED_CSV.as_posix().replace("'", "''")
con.execute("DROP VIEW IF EXISTS v_csv")
con.execute(f"CREATE VIEW v_csv AS SELECT * FROM read_csv('{csv_path}', AUTO_DETECT=TRUE, HEADER=TRUE)")

if join_by_id:
    # Ensure uniqueness of id in both sides (best-effort check)
    id_dups_csv = con.execute("SELECT COUNT(*) FROM (SELECT id, COUNT(*) c FROM v_csv GROUP BY 1 HAVING c>1)").fetchone()[0]
    id_dups_par = con.execute("SELECT COUNT(*) FROM (SELECT id, COUNT(*) c FROM v_parquet GROUP BY 1 HAVING c>1)").fetchone()[0]
    print('CSV duplicate ids:', id_dups_csv, 'Parquet duplicate ids:', id_dups_par)

    select_cols = ", ".join([duckdb.escape_identifier(c) for c in cols_for_sample])
    csv_aliases = {c: f"csv__{sanitize(c)}" for c in cols_for_sample if c != 'id'}
    par_aliases = {c: f"parquet__{sanitize(c)}" for c in cols_for_sample if c != 'id'}

    q = f"""
    WITH s AS (
      SELECT {select_cols}
      FROM v_csv
      USING SAMPLE {SAMPLE_SIZE} ROWS
    )
    SELECT s.id as key_id,
           {', '.join([f's.{duckdb.escape_identifier(c)} as ' + duckdb.escape_identifier(csv_aliases[c]) for c in cols_for_sample if c!='id'])},
           {', '.join([f'p.{duckdb.escape_identifier(c)} as ' + duckdb.escape_identifier(par_aliases[c]) for c in cols_for_sample if c!='id'])}
    FROM s
    LEFT JOIN v_parquet p ON p.id = s.id
    """
else:
    # Row-order based comparison using row_number
    select_cols = ", ".join([duckdb.escape_identifier(c) for c in cols_for_sample])
    csv_aliases = {c: f"csv__{sanitize(c)}" for c in cols_for_sample}
    par_aliases = {c: f"parquet__{sanitize(c)}" for c in cols_for_sample}

    q = f"""
    WITH c AS (
      SELECT row_number() OVER () AS rn, {select_cols}
      FROM v_csv
    ), p AS (
      SELECT row_number() OVER () AS rn, {select_cols}
      FROM v_parquet
    ), s AS (
      SELECT * FROM c USING SAMPLE {SAMPLE_SIZE} ROWS
    )
    SELECT s.rn as key_rn,
           {', '.join([f's.{duckdb.escape_identifier(c)} as ' + duckdb.escape_identifier(csv_aliases[c]) for c in cols_for_sample])},
           {', '.join([f'p.{duckdb.escape_identifier(c)} as ' + duckdb.escape_identifier(par_aliases[c]) for c in cols_for_sample])}
    FROM s LEFT JOIN p ON p.rn = s.rn
    """

sample_df = con.execute(q).fetch_df()

sample_path = REPORTS_DIR / 'semantic_parity_row_samples.csv'
sample_df.to_csv(sample_path, index=False)
print('Wrote row-level sample to:', sample_path)

# Heuristic mismatch markers
mismatch_cols = []
for c in cols_for_sample:
    if c == candidate_key and join_by_id:
        continue
    csv_col = csv_aliases.get(c)
    par_col = par_aliases.get(c)
    if csv_col in sample_df.columns and par_col in sample_df.columns:
        # Count where csv value is suspicious token but parquet differs (NULL or other)
        mask = sample_df[csv_col].isin(SUSPICIOUS_TOKENS) & (sample_df[csv_col].astype(str) != sample_df[par_col].astype(str))
        rate = float(mask.mean()) if len(sample_df) else 0.0
        mismatch_cols.append((c, rate))

print('Top mismatch columns (sample-based):', sorted(mismatch_cols, key=lambda x: x[1], reverse=True)[:10])
