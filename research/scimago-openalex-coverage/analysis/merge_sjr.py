#!/usr/bin/env python3
from __future__ import annotations

from IPython.display import display
# Imports and configuration
import os
import re
import json
import csv
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple

import pandas as pd
import numpy as np


def find_project_root() -> Path:
    # Try git to locate repo root
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
        p = Path(root)
        if (p / 'data').exists():
            return p
    except Exception:
        pass
    # Fallback: walk up parents looking for data/raw/SJR
    cur = Path.cwd()
    for candidate in [cur] + list(cur.parents):
        if (candidate / 'data' / 'raw' / 'SJR').exists():
            return candidate
    return cur

DATA_ROOT = Path(os.environ['DATA_ROOT']).expanduser().resolve()
RAW_DIR = DATA_ROOT / 'raw' / 'SJR'
OUT_DIR = DATA_ROOT / 'processed'
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_MAIN = OUT_DIR / 'scimagojr_communication_journal_1999_2024.csv'
OUTPUT_DUP = OUT_DIR / 'scimagojr_communication_journal_1999_2024_repeat.csv'
OUTPUT_NON = OUT_DIR / 'scimagojr_communication_journal_1999_2024_non.csv'

YEAR_PATTERN = re.compile(r'(19|20)\d{2}')

pd.set_option('display.max_columns', 200)
pd.set_option('display.width', 200)



# %%

# Utility functions

def extract_year_from_filename(filename: str) -> int | None:
    years = YEAR_PATTERN.findall(filename)
    # findall returns list of tuples or strings depending on groups; rebuild
    # We want full match, not the leading (19|20) only
    years_full = re.findall(r'(?:19|20)\d{2}', filename)
    if not years_full:
        return None
    # prefer last occurrence (e.g., filenames could contain multiple years)
    try:
        return int(years_full[-1])
    except Exception:
        return None


def sniff_csv_params(path: Path) -> dict:
    # Use Python csv.Sniffer for delimiter/quotechar detection with fallback defaults
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as f:
            sample = f.read(2048)
            dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t'])
            has_header = csv.Sniffer().has_header(sample)
            return {
                'sep': dialect.delimiter,
                'quotechar': dialect.quotechar,
                'doublequote': True,
                'escapechar': None,
                'header': 0 if has_header else None,
            }
    except Exception:
        return {'sep': ',', 'quotechar': '"', 'doublequote': True, 'escapechar': None, 'header': 0}


def safe_read_csv(path: Path) -> pd.DataFrame:
    # Robust read with multiple strategies
    param = sniff_csv_params(path)
    encodings = ['utf-8-sig', 'utf-8', 'latin-1']
    engines = ['c', 'python']
    on_bad_lines_opts = ['warn', 'skip']

    for enc in encodings:
        for eng in engines:
            for obl in on_bad_lines_opts:
                try:
                    df = pd.read_csv(
                        path,
                        encoding=enc,
                        engine=eng,
                        sep=param['sep'],
                        quotechar=param['quotechar'],
                        doublequote=param['doublequote'],
                        escapechar=param['escapechar'],
                        header=param['header'],
                        on_bad_lines=obl,
                    )
                    return df
                except Exception:
                    continue
    # Last resort
    return pd.read_csv(path, engine='python', on_bad_lines='skip')


def normalize_sourceid(value: Any) -> str | None:
    if pd.isna(value):
        return None
    v = str(value).strip()
    if v == '' or v.lower() in {'nan', 'none', 'null'}:
        return None
    return v


def find_sourceid_column(columns: List[Any]) -> str | None:
    # Normalize by lowercasing and removing non-alphanumerics
    for col in columns:
        col_str = str(col)
        norm = re.sub(r'[^a-z0-9]', '', col_str.lower())
        if norm == 'sourceid':
            return col_str
    return None


def file_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def compute_changed_columns(row_removed: pd.Series, row_kept: pd.Series, exclude: List[str]) -> List[str]:
    changed = []
    cols = sorted(set(row_kept.index.tolist()) | set(row_removed.index.tolist()))
    for c in cols:
        if c in exclude:
            continue
        rv = row_removed.get(c, np.nan)
        kv = row_kept.get(c, np.nan)
        if pd.isna(rv) and pd.isna(kv):
            continue
        if isinstance(rv, float) and np.isnan(rv) and isinstance(kv, float) and np.isnan(kv):
            continue
        if pd.isna(rv) != pd.isna(kv):
            changed.append(c)
            continue
        # Normalize string comparison by stripping whitespace
        if isinstance(rv, str):
            rv = rv.strip()
        if isinstance(kv, str):
            kv = kv.strip()
        if rv != kv:
            changed.append(c)
    return changed



# %%

# Discover and load CSVs
from tqdm.auto import tqdm

csv_files = sorted([p for p in RAW_DIR.rglob('*.csv') if p.is_file()])
print(f"Found {len(csv_files)} CSV files under {RAW_DIR}")

frames: List[pd.DataFrame] = []
non_sourceid_rows: List[pd.DataFrame] = []

for path in tqdm(csv_files):
    df = safe_read_csv(path)
    # Normalize columns: strip whitespace from column names
    df.columns = [str(c).strip() for c in df.columns]
    # Attach provenance
    df['source_filename'] = str(path.relative_to(RAW_DIR))
    df['source_mtime'] = file_mtime(path)
    # Add year from filename if present
    year = extract_year_from_filename(path.name)
    df['year'] = year
    # Normalize sourceid: try to locate best matching column name
    sid_col = find_sourceid_column(df.columns)
    if sid_col is not None:
        df['sourceid_norm'] = df[sid_col].apply(normalize_sourceid)
    else:
        df['sourceid_norm'] = None
    # Split rows missing sourceid
    non_mask = df['sourceid_norm'].isna()
    if non_mask.any():
        non_sourceid_rows.append(df[non_mask].copy())
    frames.append(df[~non_mask].copy())

raw_non_df = pd.concat(non_sourceid_rows, axis=0, ignore_index=True) if non_sourceid_rows else pd.DataFrame()
raw_df = pd.concat(frames, axis=0, ignore_index=True) if frames else pd.DataFrame()

print(f"Rows with sourceid: {len(raw_df)}; rows without sourceid: {len(raw_non_df)}")
print(f"Columns union (with provenance): {len(raw_df.columns)} columns")


# %%

# Deduplicate by sourceid (keep most recent)

if raw_df.empty:
    print("No rows with sourceid found. Nothing to deduplicate.")
    dedup_df = raw_df.copy()
    dup_removed_df = pd.DataFrame()
else:
    # Sort by priority: year desc (None last), then mtime desc
    # Use fillna(-inf) / fillna(0) to push missing years to the end
    sort_year = raw_df['year'].fillna(-1).astype(int)
    sort_mtime = raw_df['source_mtime'].fillna(0.0).astype(float)
    raw_df = raw_df.assign(_sort_year=sort_year, _sort_mtime=sort_mtime)
    raw_df = raw_df.sort_values(by=['sourceid_norm', '_sort_year', '_sort_mtime'], ascending=[True, False, False], kind='mergesort')

    # Mark duplicates keeping the first (which is most recent due to sorting)
    dup_mask = raw_df.duplicated(subset=['sourceid_norm'], keep='first')

    dedup_df = raw_df[~dup_mask].drop(columns=['_sort_year', '_sort_mtime'])
    dup_removed_df = raw_df[dup_mask].drop(columns=['_sort_year', '_sort_mtime'])

print(f"Kept rows: {len(dedup_df)}; Removed duplicates: {len(dup_removed_df)}")


# %%

# Build duplicate report with changed columns

if dup_removed_df.empty:
    dup_report_df = pd.DataFrame(columns=list(dedup_df.columns) + ['original_filename', 'changed_columns'])
else:
    # For each removed row, find the kept row for the same sourceid_norm
    kept_index = dedup_df.set_index('sourceid_norm')
    records = []
    exclude_cols = {'source_filename', 'source_mtime', 'year', 'sourceid_norm'}

    for idx, row in dup_removed_df.iterrows():
        sid = row['sourceid_norm']
        if sid not in kept_index.index:
            # Should not happen, but fallback: treat as no change
            kept_row = pd.Series(dtype=object)
        else:
            kept_row = kept_index.loc[sid]
            # In rare case of duplicate index, take the first kept
            if isinstance(kept_row, pd.DataFrame):
                kept_row = kept_row.iloc[0]
        changed = compute_changed_columns(row, kept_row, exclude=list(exclude_cols))
        rec = row.to_dict()
        rec['original_filename'] = row.get('source_filename')
        rec['changed_columns'] = ','.join(changed) if changed else 'none'
        records.append(rec)
    dup_report_df = pd.DataFrame.from_records(records)

print(f"Duplicate report rows: {len(dup_report_df)}")


# %%

# Prepare outputs: drop helper columns in main; keep provenance

main_df = dedup_df.copy()
# Keep provenance columns
if 'sourceid' in main_df.columns and 'sourceid_norm' in main_df.columns:
    # Ensure canonical sourceid column is consistent with normalized
    # Do not overwrite original; keep both for traceability
    pass

# Save outputs
main_df.to_csv(OUTPUT_MAIN, index=False, encoding='utf-8')
if not dup_report_df.empty:
    dup_report_df.to_csv(OUTPUT_DUP, index=False, encoding='utf-8')
else:
    # Write empty CSV with header
    pd.DataFrame(columns=list(main_df.columns) + ['original_filename', 'changed_columns']).to_csv(OUTPUT_DUP, index=False, encoding='utf-8')

if not raw_non_df.empty:
    raw_non_df.to_csv(OUTPUT_NON, index=False, encoding='utf-8')
else:
    pd.DataFrame().to_csv(OUTPUT_NON, index=False, encoding='utf-8')

print("Saved:")
print(f" - {OUTPUT_MAIN}")
print(f" - {OUTPUT_DUP}")
print(f" - {OUTPUT_NON}")


# %%

# Quick sanity checks
summary = {
    'input_files': len(csv_files),
    'rows_with_sourceid': int(len(raw_df)),
    'rows_without_sourceid': int(len(raw_non_df)),
    'kept_rows': int(len(main_df)),
    'duplicates_removed': int(len(dup_removed_df)),
    'main_columns': sorted(list(main_df.columns)),
}
print(json.dumps(summary, indent=2))

# Show sample diffs if any
if not dup_report_df.empty:
    cols_to_show = [c for c in ['sourceid_norm', 'year', 'original_filename', 'changed_columns'] if c in dup_report_df.columns]
    display(dup_report_df[cols_to_show].head(20))
