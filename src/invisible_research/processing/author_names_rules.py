"""
nameparse.py

Utility script to count the total number of **unique authors** (“creator” field)
in the dataset stored at `data_for_analysis.parquet`.
This version streams the file row‑group by row‑group, so it works even on machines with limited RAM.

It relies on the *python‑nameparser* library to split and normalise personal
names before deduplication.

Usage (from project root):

    python nameparse.py
"""
from __future__ import annotations

from pathlib import Path
import re
import unicodedata
import pyarrow.parquet as pq
import pyarrow as pa

from nameparser import HumanName

from ..data import resolve_data_root

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
NAME_DELIM_REGEX = re.compile(r",\s+")


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def _strip_diacritics(text: str) -> str:
    """Return *text* with all diacritics removed (NFD → ASCII)."""
    norm = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in norm if not unicodedata.combining(ch))


def _canonical(raw_name: str) -> str:
    """
    Convert a **raw** author string to a canonical representation suitable for
    deduplication:

    1. Parse with ``HumanName``.
    2. Keep only *first* + *last* (titles, middle names & suffixes are ignored).
    3. Lower‑case, collapse extra spaces, strip diacritics.

    Empty strings are returned unchanged so the caller can filter them out.
    """
    if not raw_name:
        return raw_name

    human = HumanName(raw_name)
    simplified = f"{human.first} {human.last}".strip()
    if not simplified:
        return ""

    simplified = _strip_diacritics(simplified)
    simplified = re.sub(r"\s+", " ", simplified).lower()
    return simplified


def _canonical_field(field: str | None) -> str:
    """
    Given one raw *creator* field, return a single string where every
    individual author name has been canonicalised and re‑joined with
    ", " (comma + space).  Returns an empty string for null/blank input.
    """
    if not field:
        return ""

    parts = [p.strip() for p in NAME_DELIM_REGEX.split(str(field))]
    canons = [_canonical(p) for p in parts if p]
    canons = [c for c in canons if c]          # filter empties
    return ", ".join(canons)


def _write_clean_parquet(pf: pq.ParquetFile, clean_path: Path) -> None:
    """
    Create a new Parquet file at *CLEAN_PATH* containing a single column
    'creator_clean', row‑for‑row aligned with the original dataset.
    """
    # Overwrite if it already exists
    if clean_path.exists():
        clean_path.unlink()

    writer: pq.ParquetWriter | None = None
    try:
        for i in range(pf.num_row_groups):
            table = pf.read_row_group(i, columns=["creator"])
            canon_array = pa.array(
                [_canonical_field(v) for v in table.column("creator").to_pylist()],
                type=pa.string()
            )
            clean_table = pa.Table.from_arrays([canon_array], names=["creator_clean"])

            if writer is None:
                writer = pq.ParquetWriter(clean_path, clean_table.schema)
            writer.write_table(clean_table)
    finally:
        if writer is not None:
            writer.close()


def _extract_unique_authors_arrow(pf: pq.ParquetFile, column_name: str) -> set[str]:
    """
    Return canonical unique author names from a ParquetFile.
    Reads one row‑group at a time to avoid loading the entire file into RAM.
    Only the specified column is materialised.
    """
    unique: set[str] = set()

    for i in range(pf.num_row_groups):
        table = pf.read_row_group(i, columns=[column_name])
        # `table.column(column_name)` returns a chunked array; use to_pylist().
        for field in table.column(column_name).to_pylist():
            if field is None or field == "":
                continue
            # Split possible multi‑author fields
            for part in NAME_DELIM_REGEX.split(str(field)):
                part = part.strip()
                if not part:
                    continue
                canon = _canonical(part)
                if canon:
                    unique.add(canon)

    return unique


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #
def main() -> None:
    """Load Parquet, compute, and print the total number of unique authors."""
    data_root = resolve_data_root()
    data_path = data_root / "processed" / "data_for_analysis.parquet"
    clean_path = data_root / "processed" / "name_clean.parquet"
    if not data_path.exists():
        raise SystemExit(f"❌ Parquet file not found: {data_path}")

    print(f"📖 Reading Parquet in streaming mode: {data_path}")
    pf = pq.ParquetFile(data_path)

    clean_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"🛠  Writing cleaned names to: {clean_path}")
    _write_clean_parquet(pf, clean_path)

    pf_clean = pq.ParquetFile(clean_path)
    authors = _extract_unique_authors_arrow(pf_clean, "creator_clean")
    print(f"✅ Total unique authors: {len(authors):,}")


if __name__ == "__main__":
    main()
