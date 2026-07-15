#!/usr/bin/env python3
"""Print deterministic creator examples for manual exploratory inspection."""

from __future__ import annotations

import pyarrow.parquet as pq

from invisible_research.data import resolve_data_root
from invisible_research.processing.author_sampling import stratified_author_sample


MAX_SAMPLES = 10


def main() -> None:
    input_path = resolve_data_root() / "processed" / "data_for_analysis.parquet"
    if not input_path.exists():
        raise SystemExit(f"Parquet file not found: {input_path}")

    schema = pq.read_schema(input_path)
    columns = ["creator"]
    if "relation" in schema.names:
        columns.append("relation")
    sample = stratified_author_sample(
        pq.read_table(input_path, columns=columns).to_pandas(),
        "creator",
        MAX_SAMPLES,
    )

    for count, group in sample.groupby("author_count"):
        print(f"\nAuthor count = {count} (showing {len(group)} samples)")
        for index, row in enumerate(group.itertuples(index=False), start=1):
            print(f"{index:2d}. {row.creator}")
            if "relation" in group.columns:
                print(f"    relation: {row.relation}")


if __name__ == "__main__":
    main()
