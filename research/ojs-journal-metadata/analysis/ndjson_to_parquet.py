#!/usr/bin/env python3
"""Stream a fixed-schema NDJSON artifact into Parquet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.json as pajson
import pyarrow.parquet as pq


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("schema", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-rows", type=int, required=True)
    args = parser.parse_args()

    columns = json.loads(args.schema.read_text())["columns"]
    schema = pa.schema((column, pa.string()) for column in columns)
    reader = pajson.open_json(
        args.input,
        read_options=pajson.ReadOptions(block_size=64 * 1024 * 1024),
        parse_options=pajson.ParseOptions(explicit_schema=schema),
    )

    rows = 0
    with pq.ParquetWriter(args.output, schema, compression="zstd") as writer:
        for batch in reader:
            writer.write_batch(batch)
            rows += batch.num_rows

    if rows != args.expected_rows:
        args.output.unlink(missing_ok=True)
        raise RuntimeError(f"Parquet row count mismatch: {rows}")

    parquet = pq.ParquetFile(args.output)
    if parquet.schema_arrow.names != columns:
        args.output.unlink(missing_ok=True)
        raise RuntimeError("Parquet schema does not match the declared columns")
    print(
        json.dumps(
            {"rows": rows, "columns": len(columns), "pyarrow": pa.__version__}
        )
    )


if __name__ == "__main__":
    main()
