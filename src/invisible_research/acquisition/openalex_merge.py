"""
Merge all CSV files under a source directory into a single Parquet file (Snappy),
preserving all rows and columns. Original CSVs remain unchanged.

Features:
- Recursively discover .csv files under input directory
- Validate schema consistency; if differences exist, use union-of-columns
- Streaming read to control memory usage
- Write a single Parquet file using PyArrow (Snappy compression)
- Emit a stats JSON with file count, total rows, and columns summary

Usage:
  DATA_ROOT=/path/to/data PYTHONPATH=src python -m invisible_research.acquisition.openalex_merge

All code and documentation are in English as required by the repository standards.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional, Set

import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

from ..artifacts import (
    build_artifact_version,
    write_artifact_record,
    write_artifact_version,
)
from ..data import resolve_data_root


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
            with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
                reader = csv.reader(
                    f,
                    delimiter=",",
                    quotechar='"',
                    doublequote=True,
                    # Preserve the legacy workflow's backslash-escape behavior.
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

    output_parent = os.path.dirname(output_csv_path)
    if output_parent:
        os.makedirs(output_parent, exist_ok=True)
    total_rows = 0

    with open(output_csv_path, "w", encoding="utf-8", errors="replace", newline="") as out_f:
        writer = csv.writer(out_f, delimiter=",", quotechar='"', lineterminator="\n")
        writer.writerow(union_columns)

        for path in files:
            with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as in_f:
                reader = csv.reader(
                    in_f,
                    delimiter=",",
                    quotechar='"',
                    doublequote=True,
                    # Preserve the legacy workflow's backslash-escape behavior.
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
        escape_char=False,
        newlines_in_values=True,
    )
    read_options = pacsv.ReadOptions(
        block_size=1 << 20,
        encoding="utf8",
        autogenerate_column_names=False,
    )
    convert_options = pacsv.ConvertOptions(
        column_types={name: pa.string() for name in union_columns},
        null_values=[""],
        strings_can_be_null=True,
    )

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
                output_parent = os.path.dirname(output_parquet)
                if output_parent:
                    os.makedirs(output_parent, exist_ok=True)
                writer = pq.ParquetWriter(
                    output_parquet,
                    (arrow_schema or table.schema),
                    compression="snappy",
                )
            writer.write_table(table)
            total_rows += table.num_rows

    if writer is not None:
        writer.close()
    elif arrow_schema is not None:
        output_parent = os.path.dirname(output_parquet)
        if output_parent:
            os.makedirs(output_parent, exist_ok=True)
        empty_writer = pq.ParquetWriter(
            output_parquet,
            arrow_schema,
            compression="snappy",
        )
        empty_writer.close()

    return total_rows


def save_stats(stats_path: str, stats: MergeStats) -> None:
    stats_parent = os.path.dirname(stats_path)
    if stats_parent:
        os.makedirs(stats_parent, exist_ok=True)
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(asdict(stats), f, ensure_ascii=False, indent=2)


def validate_output_locations(
    input_dir: str,
    output_locations: Iterable[str | Path],
) -> None:
    """Reject generated output paths that would contaminate input discovery."""
    input_path = Path(input_dir).expanduser().resolve()
    for location in output_locations:
        output_path = Path(location).expanduser().resolve()
        try:
            output_path.relative_to(input_path)
        except ValueError:
            continue
        raise ValueError(
            f"Output path {output_path} must be outside the input directory "
            f"{input_path}"
        )


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge CSVs into a single Parquet file")
    parser.add_argument(
        "--input-dir",
        default=None,
        help="Root directory containing CSV files (recursively discovered)",
    )
    parser.add_argument(
        "--output-parquet",
        default=None,
        help="Destination Parquet file path",
    )
    parser.add_argument(
        "--output-csv",
        default=None,
        help="Destination intermediate CSV file path (will be kept)",
    )
    parser.add_argument(
        "--stats-json",
        default=None,
        help="Path to write stats JSON",
    )
    parser.add_argument(
        "--artifact-record",
        default=None,
        help="Path to write the four-field Artifact Version record",
    )
    parser.add_argument(
        "--artifact-id",
        default="openalex-merged",
        help="Stable name prefixed to the content-addressed Artifact Version ID",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if any(
        value is None
        for value in (
            args.input_dir,
            args.output_parquet,
            args.output_csv,
            args.stats_json,
        )
    ):
        data_root = resolve_data_root()
        args.input_dir = args.input_dir or str(data_root / "raw" / "openalex_data")
        args.output_parquet = args.output_parquet or str(
            data_root / "processed" / "openalex_merged.parquet"
        )
        args.output_csv = args.output_csv or str(
            data_root / "processed" / "openalex_merged.csv"
        )
        args.stats_json = args.stats_json or str(
            data_root / "processed" / "openalex_merged_stats.json"
        )

    args.artifact_record = args.artifact_record or str(
        Path(args.output_parquet).with_suffix(".artifact.json")
    )
    return args


def main() -> None:
    args = parse_args()

    start_time = time.time()
    print("🚀 Starting OpenAlex CSV merge to Parquet")
    print(f"Input dir: {args.input_dir}")
    print(f"Output parquet: {args.output_parquet}")
    print(f"Output CSV: {args.output_csv}")
    print(f"Stats JSON: {args.stats_json}")
    print(f"Artifact record: {args.artifact_record}")

    validate_output_locations(
        args.input_dir,
        (
            args.output_parquet,
            args.output_csv,
            args.stats_json,
            args.artifact_record,
        ),
    )

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

    if os.path.exists(args.output_parquet):
        os.remove(args.output_parquet)
    # Will overwrite CSV during rebuild

    # 1) Write intermediate CSV (kept) with union-of-columns
    print("Writing intermediate CSV with union-of-columns ...")
    written_rows = write_union_csv(files, union_columns, args.output_csv)
    print(f"Intermediate CSV rows: {written_rows}")

    # 2) Convert CSV → Parquet
    print("Converting CSV to Parquet via PyArrow ...")
    arrow_schema = pa.schema([(column, pa.string()) for column in union_columns])
    total_rows = stream_merge_to_parquet(
        [args.output_csv],
        union_columns,
        args.output_parquet,
        arrow_schema=arrow_schema,
    )

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

    input_record = build_artifact_version(
        "openalex-inputs",
        args.input_dir,
        ["OpenAlex CSV export"],
    )
    input_record_path = Path(args.output_parquet).with_name(
        f"openalex_inputs.{input_record['sha256']}.artifact.json"
    )
    write_artifact_record(input_record_path, input_record)
    write_artifact_version(
        args.artifact_record,
        args.artifact_id,
        args.output_parquet,
        [str(input_record["id"])],
    )
    print(f"Input Artifact Version written to {input_record_path}")
    print(f"Artifact Version written to {args.artifact_record}")


if __name__ == "__main__":
    main()
