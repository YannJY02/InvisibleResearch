"""Stable author-count sampling used by exploratory owner commands."""

from __future__ import annotations

import re

import pandas as pd


AUTHOR_DELIMITER = re.compile(
    r"\s*(?:;|&|\band\b|\+|/|\\)\s*",
    flags=re.IGNORECASE,
)


def add_author_count(df: pd.DataFrame, author_column: str) -> pd.DataFrame:
    """Return a copy with an author count derived from known delimiters."""
    counted = df.copy()
    counted["author_count"] = (
        counted[author_column]
        .fillna("")
        .astype(str)
        .apply(
            lambda value: len(
                [part for part in AUTHOR_DELIMITER.split(value) if part.strip()]
            )
            if value.strip()
            else 0
        )
    )
    return counted


def stratified_author_sample(
    df: pd.DataFrame,
    author_column: str,
    max_samples: int = 10,
) -> pd.DataFrame:
    """Sample deterministically within every non-empty author-count group."""
    counted = add_author_count(df, author_column)
    samples = [
        group.sample(min(len(group), max_samples), random_state=0).copy()
        for count, group in counted.groupby("author_count")
        if count != 0
    ]
    if not samples:
        return counted.iloc[0:0].copy()
    return pd.concat(samples, ignore_index=True)
