#!/usr/bin/env python3
"""Forward the legacy OpenAlex command to the Shared Workspace entrypoint."""

from __future__ import annotations

import os
import sys
from pathlib import Path


# ponytail: temporary migration adapter; remove after the hybrid-workspace verification window.
project_root = Path(__file__).resolve().parents[2]
root_command = project_root / "run_pipeline.sh"
os.execv(
    root_command,
    [str(root_command), "openalex-merge", *sys.argv[1:]],
)
