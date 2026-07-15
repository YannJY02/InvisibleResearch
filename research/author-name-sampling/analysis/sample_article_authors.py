#!/usr/bin/env python3
"""Create the full-column ArticleInfo author sample used for inspection."""

from __future__ import annotations

import pyarrow.parquet as pq

from invisible_research.data import resolve_data_root
from invisible_research.processing.author_sampling import stratified_author_sample


MAX_SAMPLES = 10


def main() -> None:
    data_root = resolve_data_root()
    input_path = data_root / "processed" / "articleInfo.parquet"
    output_path = data_root / "processed" / "new_creator_sample.parquet"
    if not input_path.exists():
        raise SystemExit(f"Parquet file not found: {input_path}")

    frame = pq.read_table(input_path).to_pandas()
    if "authors" not in frame.columns:
        raise SystemExit("Required authors column is missing")
    sample = stratified_author_sample(frame, "authors", MAX_SAMPLES)
    if sample.empty:
        print("No non-empty author rows found; sample was not created.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(output_path, index=False, engine="pyarrow")
    print(f"ArticleInfo author sample written to {output_path} with {len(sample)} rows")


if __name__ == "__main__":
    main()
