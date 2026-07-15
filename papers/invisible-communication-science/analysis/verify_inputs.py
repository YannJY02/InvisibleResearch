#!/usr/bin/env python3
"""Verify a Publication Compendium input against its Artifact Version record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from invisible_research.artifacts import sha256_file, validate_artifact_record
from invisible_research.data import resolve_data_root


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RECORD = (
    PROJECT_ROOT
    / "data/artifact-versions/dimensions-april2025-consolidated.json"
)
def resolve_artifact_location(location: str) -> Path:
    prefix = "$DATA_ROOT/"
    if location.startswith(prefix):
        return resolve_data_root() / location.removeprefix(prefix)
    return Path(location).expanduser().resolve()


def verify_record(record_path: str | Path) -> dict[str, object]:
    record = json.loads(Path(record_path).read_text(encoding="utf-8"))
    validate_artifact_record(record)
    location = resolve_artifact_location(str(record["location"]))
    actual_sha256 = sha256_file(location)
    if actual_sha256 != record["sha256"]:
        raise ValueError(
            f"SHA-256 mismatch for {location}: expected {record['sha256']}, "
            f"found {actual_sha256}"
        )
    print(f"Verified {record['id']} at {location}")
    return record


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=str(DEFAULT_RECORD))
    return parser.parse_args(list(argv) if argv is not None else None)


def main() -> None:
    args = parse_args()
    verify_record(args.record)


if __name__ == "__main__":
    main()
