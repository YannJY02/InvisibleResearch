#!/usr/bin/env python3
"""Stream a fixed-schema NDJSON artifact into Parquet."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.json as pajson
import pyarrow.parquet as pq


def convert(args: argparse.Namespace) -> None:
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


def validate(args: argparse.Namespace) -> None:
    contract = json.loads(args.contract.read_text())
    master = pq.read_table(
        args.master,
        columns=[
            "oai_url",
            "repository_name",
            "set_spec",
            "openalex_match_status",
            "openalex_candidate_ids",
        ],
    )
    catalog = pq.read_table(
        args.catalog,
        columns=["openalex_source_id", "checkpoint_file"],
    )

    identities = set(
        zip(
            master["oai_url"].to_pylist(),
            master["repository_name"].to_pylist(),
            master["set_spec"].to_pylist(),
            strict=True,
        )
    )
    statuses = Counter(master["openalex_match_status"].to_pylist())
    source_ids = catalog["openalex_source_id"].to_pylist()
    checkpoint_files = catalog["checkpoint_file"].to_pylist()
    catalog_ids = set(source_ids)
    candidate_ids = {
        candidate_id
        for cell in master["openalex_candidate_ids"].to_pylist()
        if cell
        for candidate_id in cell.split("|")
    }
    private_names = {"admin_email", "openalex_api_key", "crossref_mailto"}
    master_names = {name.casefold() for name in master.schema.names}

    if master.num_rows != contract["master_rows"]:
        raise RuntimeError("Master Parquet row count mismatch")
    if len(identities) != master.num_rows:
        raise RuntimeError("Master Parquet contains duplicate PKP identities")
    if statuses != Counter(contract["status_counts"]):
        raise RuntimeError("Master Parquet status counts do not reconcile")
    if len(source_ids) != len(catalog_ids):
        raise RuntimeError("Source catalog contains duplicate Source IDs")
    if not candidate_ids <= catalog_ids:
        raise RuntimeError("Master candidate IDs are missing from the Source catalog")
    if private_names & master_names:
        raise RuntimeError("Private configuration appears in Parquet columns")
    for checkpoint_file in checkpoint_files:
        if Path(checkpoint_file).name != checkpoint_file:
            raise RuntimeError("Unsafe checkpoint path in Source catalog")
        if not (args.batch_dir / checkpoint_file).is_file():
            raise RuntimeError("Source catalog references a missing checkpoint")

    print(
        json.dumps(
            {
                "master_rows": master.num_rows,
                "unique_identities": len(identities),
                "catalog_rows": catalog.num_rows,
                "candidate_ids": len(candidate_ids),
            }
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    convert_parser = subparsers.add_parser("convert")
    convert_parser.add_argument("input", type=Path)
    convert_parser.add_argument("schema", type=Path)
    convert_parser.add_argument("output", type=Path)
    convert_parser.add_argument("--expected-rows", type=int, required=True)
    convert_parser.set_defaults(func=convert)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("master", type=Path)
    validate_parser.add_argument("catalog", type=Path)
    validate_parser.add_argument("batch_dir", type=Path)
    validate_parser.add_argument("contract", type=Path)
    validate_parser.set_defaults(func=validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
