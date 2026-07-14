"""Content-identity records for research artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256_file(path: str | Path) -> str:
    """Calculate the SHA-256 identity of a file's content."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_location(path: str | Path) -> str:
    """Identify a file or a directory's deterministic component manifest."""
    location = Path(path)
    if location.is_file():
        return sha256_file(location)
    if not location.is_dir():
        raise FileNotFoundError(location)

    manifest = [
        {
            "path": component.relative_to(location).as_posix(),
            "sha256": sha256_file(component),
        }
        for component in sorted(
            candidate for candidate in location.rglob("*") if candidate.is_file()
        )
    ]
    serialized_manifest = json.dumps(
        manifest,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(serialized_manifest).hexdigest()


def build_artifact_version(
    artifact_name: str,
    location: str | Path,
    source: Iterable[str],
) -> dict[str, object]:
    """Build the workspace's four-field Artifact Version record."""
    artifact_path = Path(location).expanduser().resolve()
    sha256 = sha256_location(artifact_path)
    return {
        "id": f"{artifact_name}@sha256:{sha256}",
        "sha256": sha256,
        "location": str(artifact_path),
        "source": list(source),
    }


def write_artifact_record(
    record_path: str | Path,
    record: dict[str, object],
) -> None:
    """Write a previously built Artifact Version record."""
    destination = Path(record_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_artifact_version(
    record_path: str | Path,
    artifact_name: str,
    location: str | Path,
    source: Iterable[str],
) -> dict[str, object]:
    """Write and return a four-field Artifact Version record."""
    record = build_artifact_version(artifact_name, location, source)
    write_artifact_record(record_path, record)
    return record
