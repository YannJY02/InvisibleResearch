#!/usr/bin/env python3
"""
Merge all CSV files under a source directory into a single Parquet file (Snappy),
preserving all rows and columns. Original CSVs remain unchanged.

Features:
- Recursively discover .csv files under input directory
- Validate schema consistency; if differences exist, use union-of-columns
- Streaming read with chunksize to control memory usage
- Write a single Parquet file using PyArrow (Snappy compression)
- Emit a stats JSON with file count, total rows, and columns summary

Usage:
  python scripts/02_extraction/merge_openalex_csv_to_parquet.py \
    --input-dir /Users/yann.jy/InvisibleResearch/data/raw/openalex_data \
    --output-parquet /Users/yann.jy/InvisibleResearch/data/processed/openalex_merged.parquet \
    --stats-json /Users/yann.jy/InvisibleResearch/data/processed/openalex_merged_stats.json

All code and documentation are in English as required by the repository standards.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional, Set
import csv
import subprocess

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pacsv


DEFAULT_INPUT_DIR = \
    "/Users/yann.jy/InvisibleResearch/data/raw/openalex_data"
DEFAULT_OUTPUT_PARQUET = \
    "/Users/yann.jy/InvisibleResearch/data/processed/openalex_merged.parquet"
DEFAULT_STATS_JSON = \
    "/Users/yann.jy/InvisibleResearch/data/processed/openalex_merged_stats.json"
DEFAULT_OUTPUT_CSV = \
    "/Users/yann.jy/InvisibleResearch/data/processed/openalex_merged.csv"


@dataclass
class MergeStats:
    total_files: int
    total_rows: int
    unique_columns: List[str]
    per_file_columns_same: bool
    differing_files: List[str]
    processing_seconds: float


def discover_csv_files(root_dir: str) -> List[str]:
    csv_files: List[str] = []
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith(".csv"):
                csv_files.append(os.path.join(dirpath, fname))
    csv_files.sort()
    return csv_files


def inspect_columns(files: List[str]) -> tuple[List[str], bool, List[str]]:
    """
    Read header row only using Python csv module for robustness.
    Returns (union_columns, all_same, differing_files)
    """
    union_cols: Set[str] = set()
    baseline: Optional[List[str]] = None
    all_same = True
    differing: List[str] = []

    for path in files:
        try:
            with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
                reader = csv.reader(
                    f,
                    delimiter=",",
                    quotechar='"',
                    doublequote=True,
                    escapechar="\\",
                )
                header = next(reader)
                cols = [c.strip() for c in header]
                union_cols.update(cols)
                if baseline is None:
                    baseline = cols
                elif cols != baseline:
                    all_same = False
                    differing.append(path)
        except Exception:
            all_same = False
            differing.append(path)

    return sorted(union_cols), all_same, differing


def write_union_csv(files: List[str], union_columns: List[str], output_csv_path: str) -> int:
    """
    Parse each CSV with Python's csv module and write a unified CSV with the union of columns.
    Missing columns for a file are filled with empty strings. Returns total data rows written.
    """
    if not files:
        raise ValueError("No CSV files provided for merge")

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    total_rows = 0

    with open(output_csv_path, "w", encoding="utf-8", errors="replace", newline="") as out_f:
        writer = csv.writer(out_f, delimiter=",", quotechar='"', lineterminator="\n")
        writer.writerow(union_columns)

        for path in files:
            with open(path, "r", encoding="utf-8", errors="replace", newline="") as in_f:
                reader = csv.reader(
                    in_f,
                    delimiter=",",
                    quotechar='"',
                    doublequote=True,
                    escapechar="\\",
                )
                header = next(reader, None)
                if header is None:
                    continue
                header = [c.strip() for c in header]
                name_to_idx = {name: i for i, name in enumerate(header)}

                for row in reader:
                    # Build output row aligned to union columns
                    out_row: List[str] = []
                    row_len = len(row)
                    for col in union_columns:
                        idx = name_to_idx.get(col)
                        out_row.append(row[idx] if idx is not None and idx < row_len else "")
                    writer.writerow(out_row)
                    total_rows += 1

    return total_rows


def stream_merge_to_parquet(
    files: List[str],
    union_columns: List[str],
    output_parquet: str,
    chunksize: int = 200_000,
    arrow_schema: Optional[pa.Schema] = None,
) -> int:
    """
    Stream-read CSV files and append to a single Parquet file.
    - Maintains union-of-columns across files, filling missing columns with NA.
    - Returns total rows written.
    """
    writer: Optional[pq.ParquetWriter] = None
    total_rows = 0

    parse_options = pacsv.ParseOptions(
        delimiter=",",
        quote_char='"',
        double_quote=True,
        escape_char="\\",
        newlines_in_values=True,
    )
    read_options = pacsv.ReadOptions(block_size=1 << 20, encoding="utf8", autogenerate_column_names=False)
    convert_options = pacsv.ConvertOptions(
        column_types={name: pa.string() for name in union_columns},
        null_values=[],
        strings_can_be_null=True,
    )
    # We intentionally do not set null_values to avoid converting empty strings to null implicitly

    for idx, path in enumerate(files, start=1):
        print(f"[File {idx}/{len(files)}] Processing {path}")

        # Open a streaming CSV reader using Arrow for robustness with malformed lines/newlines in values
        reader = pacsv.open_csv(
            path,
            read_options=read_options,
            parse_options=parse_options,
            convert_options=convert_options,
        )

        while True:
            try:
                batch = reader.read_next_batch()
            except StopIteration:
                break

            if batch is None or batch.num_rows == 0:
                break

            table = pa.Table.from_batches([batch])

            # Ensure all union columns present
            present_cols = set(table.schema.names)
            missing_cols = [c for c in union_columns if c not in present_cols]
            if missing_cols:
                for col in missing_cols:
                    table = table.append_column(col, pa.array([None] * table.num_rows, type=pa.string()))

            # Reorder to union schema
            table = table.select(union_columns)

            # Cast to fixed schema
            if arrow_schema is not None and table.schema != arrow_schema:
                table = table.cast(arrow_schema, safe=False)

            if writer is None:
                os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
                writer = pq.ParquetWriter(
                    output_parquet,
                    (arrow_schema or table.schema),
                    compression="snappy",
                )
            writer.write_table(table)
            total_rows += table.num_rows

    if writer is not None:
        writer.close()

    return total_rows


def save_stats(stats_path: str, stats: MergeStats) -> None:
    os.makedirs(os.path.dirname(stats_path), exist_ok=True)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(asdict(stats), f, ensure_ascii=False, indent=2)


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge CSVs into a single Parquet file")
    parser.add_argument(
        "--input-dir",
        default=DEFAULT_INPUT_DIR,
        help="Root directory containing CSV files (recursively discovered)",
    )
    parser.add_argument(
        "--output-parquet",
        default=DEFAULT_OUTPUT_PARQUET,
        help="Destination Parquet file path",
    )
    parser.add_argument(
        "--output-csv",
        default=DEFAULT_OUTPUT_CSV,
        help="Destination intermediate CSV file path (will be kept)",
    )
    parser.add_argument(
        "--stats-json",
        default=DEFAULT_STATS_JSON,
        help="Path to write stats JSON",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=200_000,
        help="CSV read chunksize for streaming",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main() -> None:
    args = parse_args()

    start_time = time.time()
    print("🚀 Starting OpenAlex CSV merge to Parquet")
    print(f"Input dir: {args.input_dir}")
    print(f"Output parquet: {args.output_parquet}")
    print(f"Output CSV: {args.output_csv}")
    print(f"Stats JSON: {args.stats_json}")

    files = discover_csv_files(args.input_dir)
    if not files:
        print("No CSV files found under input directory.")
        sys.exit(1)

    print(f"Discovered {len(files)} CSV files. Inspecting columns...")
    union_columns, all_same, differing_files = inspect_columns(files)
    print(f"Total unique columns: {len(union_columns)}")
    if all_same:
        print("All files share the same column layout.")
    else:
        print("Column differences detected; using union-of-columns strategy.")
        if differing_files:
            print(f"Files with differing columns: {len(differing_files)}")

    # Prefer robust DuckDB path for Parquet conversion; create CSV by byte-concatenation first
    try:
        import duckdb  # type: ignore
    except Exception:
        print("duckdb not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "duckdb>=0.10.0"], check=True)
        import duckdb  # type: ignore

    if os.path.exists(args.output_parquet):
        os.remove(args.output_parquet)
    # Will overwrite CSV during rebuild

    # 1) Write intermediate CSV (kept) with union-of-columns
    print("Writing intermediate CSV with union-of-columns ...")
    written_rows = write_union_csv(files, union_columns, args.output_csv)
    print(f"Intermediate CSV rows: {written_rows}")

    conn = duckdb.connect()
    conn.execute("PRAGMA threads=4")
    safe_out_parquet = args.output_parquet.replace("'", "''")
    safe_out_csv = args.output_csv.replace("'", "''")

    # 2) Convert CSV → Parquet
    columns_pairs = ", ".join([f"'{c}':'VARCHAR'" for c in union_columns])
    columns_spec = "{" + columns_pairs + "}"
    copy_parquet_sql = (
        f"COPY (SELECT * FROM read_csv('{safe_out_csv}', AUTO_DETECT=FALSE, HEADER=TRUE, "
        f"COLUMNS={columns_spec}, delim=',', quote='\"', escape='\"', strict_mode=FALSE, null_padding=TRUE, "
        f"maximum_line_size=20000000, parallel=FALSE)) TO '{safe_out_parquet}' (FORMAT 'parquet', COMPRESSION 'SNAPPY')"
    )
    print("Converting CSV to Parquet via DuckDB COPY ...")
    conn.execute(copy_parquet_sql)

    # Get row count from the produced Parquet for stats
    count_sql = f"SELECT COUNT(*) FROM read_parquet('{safe_out_parquet}')"
    total_rows = conn.execute(count_sql).fetchone()[0]
    conn.close()

    elapsed = time.time() - start_time
    print(f"✅ Completed. Rows written: {total_rows:,}. Time: {elapsed/60:.2f} min")

    stats = MergeStats(
        total_files=len(files),
        total_rows=total_rows,
        unique_columns=union_columns,
        per_file_columns_same=all_same,
        differing_files=differing_files,
        processing_seconds=elapsed,
    )
    save_stats(args.stats_json, stats)
    print(f"Stats written to {args.stats_json}")


if __name__ == "__main__":
    main()


