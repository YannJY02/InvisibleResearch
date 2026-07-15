"""Portable data-location helpers."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_data_root(value: str | Path | None = None) -> Path:
    """Return the configured data root without assuming a personal filesystem path."""
    configured = value if value is not None else os.environ.get("DATA_ROOT")
    if configured is None or not str(configured).strip():
        raise ValueError(
            "DATA_ROOT is required when workflow paths are not supplied explicitly"
        )
    return Path(configured).expanduser().resolve()
