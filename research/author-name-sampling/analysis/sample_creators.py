#!/usr/bin/env python3
"""Create the creator sample consumed by shared author-name processing."""

from __future__ import annotations

import pyarrow.parquet as pq

from invisible_research.data import resolve_data_root
from invisible_research.processing.author_sampling import stratified_author_sample


MAX_SAMPLES = 10


def main() -> None:
    data_root = resolve_data_root()
    input_path = data_root / "processed" / "data_for_analysis.parquet"
    output_path = data_root / "processed" / "creator_sample.parquet"
    if not input_path.exists():
        raise SystemExit(f"Parquet file not found: {input_path}")

    schema = pq.read_schema(input_path)
    columns = ["id", "identifier", "title", "creator"]
    if "relation" in schema.names:
        columns.append("relation")
    frame = pq.read_table(input_path, columns=columns).to_pandas()
    sample = stratified_author_sample(frame, "creator", MAX_SAMPLES)
    if sample.empty:
        print("No non-empty creator rows found; sample was not created.")
        return

    sample = sample.rename(columns={"author_count": "creator_count"})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(output_path, index=False, engine="pyarrow")
    print(f"Creator sample written to {output_path} with {len(sample)} rows")


if __name__ == "__main__":
    main()
