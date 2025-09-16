#!/usr/bin/env python3
"""
Compute coverage of SCImago Communication items (all types) in the merged OpenAlex dataset
using ISSN OR Title matching.

Definition of coverage: A SCImago item is considered covered if ANY of its ISSN variants
appears in the OpenAlex merged Parquet OR if the item Title matches a venue/source title
present in OpenAlex (case/whitespace/punctuation-insensitive). No publication year filtering.

Inputs (defaults):
- SCImago CSV: data/raw/scimagojr_communication_journals.csv (semicolon-separated)
- OpenAlex Parquet: data/processed/openalex_merged.parquet

Outputs:
- outputs/reports/scim_openalex_coverage_summary.csv
  Columns: total_journals, covered_journals, unmatched_journals, coverage_rate
- outputs/reports/scim_openalex_unmatched_journals.csv
  Columns: Title, Sourceid, Type, Issn, issn_parsed

Notes:
- Code and documentation are in English as required by repository standards.
- Keep solution simple (KISS) and self-contained.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from typing import Iterable, List, Optional, Set, Tuple

import pandas as pd


# ----------------------------- Utilities (ISSN & Title parsing) -----------------------------

def normalize_issn(value: str) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip().upper()
    if not s or s == "-" or s == "NA" or s == "NAN":
        return None
    # Keep only alphanumerics, ISSN can be like 1234-5678 or 1477450X
    s = "".join(ch for ch in s if ch.isalnum())
    if len(s) < 7:  # too short to be an ISSN
        return None
    return s


def split_multi_issn(raw: str) -> List[str]:
    if raw is None:
        return []
    s = str(raw)
    # Common delimiters in SCImago CSV: comma, semicolon, whitespace
    for sep in [";", ",", "|", "/", " "]:
        s = s.replace(sep, ";")
    parts = [p.strip() for p in s.split(";") if p.strip()]
    out: List[str] = []
    for p in parts:
        n = normalize_issn(p)
        if n:
            out.append(n)
    # de-duplicate, keep order
    return list(dict.fromkeys(out))


def normalize_title(value: str) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip().lower()
    if not s:
        return None
    # Remove all non-alphanumeric characters to be punctuation/whitespace-insensitive
    s = "".join(ch for ch in s if ch.isalnum())
    if not s:
        return None
    return s


def explode_issn_columns(df: pd.DataFrame, issn_columns: List[str]) -> pd.DataFrame:
    present_cols = [c for c in issn_columns if c in df.columns]
    if not present_cols:
        # return empty frame with proper column for downstream logic
        return df.assign(_issn_norm=pd.Series(dtype=object)).loc[[]]

    def row_issns(row) -> List[str]:
        collected: List[str] = []
        for col in present_cols:
            val = row[col]
            if pd.isna(val):
                continue
            if isinstance(val, (list, tuple, set)):
                for v in val:
                    n = normalize_issn(v)
                    if n:
                        collected.append(n)
            else:
                # try parse JSON/list-like strings
                if isinstance(val, str) and val.startswith("[") and val.endswith("]"):
                    try:
                        parsed = ast.literal_eval(val)
                        if isinstance(parsed, (list, tuple)):
                            for v in parsed:
                                n = normalize_issn(v)
                                if n:
                                    collected.append(n)
                            continue
                    except Exception:
                        pass
                # otherwise treat as scalar
                n = normalize_issn(val)
                if n:
                    collected.append(n)
        # dedupe while preserving order
        return list(dict.fromkeys(collected))

    exploded = df.assign(_issn_list=df.apply(row_issns, axis=1))
    exploded = exploded.explode("_issn_list")
    exploded = exploded.rename(columns={"_issn_list": "_issn_norm"})
    exploded = exploded.dropna(subset=["_issn_norm"])  # only rows with any issn
    return exploded


def detect_openalex_issn_columns(df_head: pd.DataFrame) -> List[str]:
    """Return candidate ISSN columns from a sample dataframe head."""
    candidate_issn_cols = [
        "host_venue.issn",
        "host_venue.issn_l",
        "host_venue_issn",
        "host_venue_issn_l",
        "primary_location.source.issn",
        "primary_location.source.issn_l",
        "primary_location_source_issn",
        "primary_location_source_issn_l",
        "issn",
        "issn_l",
        "journal_issn",
        "journal_issn_l",
        # Some datasets may store merged list as string column
        "issn_list",
        "host_venue.issn_list",
        "primary_location.source.issn_list",
    ]
    issn_cols = [c for c in candidate_issn_cols if c in df_head.columns]
    if not issn_cols:
        issn_cols = [c for c in df_head.columns if "issn" in c.lower()]
    return issn_cols


# Title detection and extraction
def detect_openalex_title_columns(df_head: pd.DataFrame) -> List[str]:
    """Return candidate venue/source title columns from a sample dataframe head."""
    candidate_title_cols = [
        "host_venue.display_name",
        "host_venue.title",
        "host_venue_name",
        "primary_location.source.display_name",
        "primary_location.source.title",
        "primary_location_source_display_name",
        "primary_location_source_title",
        "source_display_name",
        "journal_title",
        "venue",
        "venue_name",
        "source_title",
        "publication_name",
    ]
    title_cols = [c for c in candidate_title_cols if c in df_head.columns]
    # Fallback: any column name containing 'display_name' or ending with '.name' or containing 'title'
    if not title_cols:
        for c in df_head.columns:
            cl = c.lower()
            if "display_name" in cl or cl.endswith(".name") or "title" in cl or "venue" in cl:
                title_cols.append(c)
    # Deduplicate while preserving order
    title_cols = list(dict.fromkeys(title_cols))
    return title_cols


def explode_title_columns(df: pd.DataFrame, title_columns: List[str]) -> pd.DataFrame:
    present_cols = [c for c in title_columns if c in df.columns]
    if not present_cols:
        return df.assign(_title_norm=pd.Series(dtype=object)).loc[[]]

    def row_titles(row) -> List[str]:
        collected: List[str] = []
        for col in present_cols:
            val = row[col]
            if pd.isna(val):
                continue
            if isinstance(val, (list, tuple, set)):
                for v in val:
                    n = normalize_title(v)
                    if n:
                        collected.append(n)
            else:
                # try parse JSON/list-like strings
                if isinstance(val, str) and val.startswith("[") and val.endswith("]"):
                    try:
                        parsed = ast.literal_eval(val)
                        if isinstance(parsed, (list, tuple)):
                            for v in parsed:
                                n = normalize_title(v)
                                if n:
                                    collected.append(n)
                            continue
                    except Exception:
                        pass
                n = normalize_title(val)
                if n:
                    collected.append(n)
        return list(dict.fromkeys(collected))

    exploded = df.assign(_title_list=df.apply(row_titles, axis=1))
    exploded = exploded.explode("_title_list")
    exploded = exploded.rename(columns={"_title_list": "_title_norm"})
    exploded = exploded.dropna(subset=["_title_norm"])  # only rows with any title
    return exploded


# ----------------------------- Core logic -----------------------------


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_scimago_items(csv_path: str) -> pd.DataFrame:
    """Load SCImago CSV and return all rows (all types), with parsed ISSN list."""
    df = pd.read_csv(csv_path, sep=";", dtype=str, low_memory=False)

    # Normalize column names for robustness but keep originals
    cols_lc = {c.lower(): c for c in df.columns}
    type_col = cols_lc.get("type", "Type" if "Type" in df.columns else None)
    issn_col = None
    for k in ["issn", "issns", "eissn", "print_issn"]:
        if k in cols_lc:
            issn_col = cols_lc[k]
            break
    if issn_col is None:
        # Fallback by searching any column containing 'issn'
        for c in df.columns:
            if "issn" in c.lower():
                issn_col = c
                break
    if issn_col is None:
        raise RuntimeError("Could not detect ISSN column in SCImago CSV")

    title_col = cols_lc.get("title", "Title" if "Title" in df.columns else None)
    sourceid_col = cols_lc.get("sourceid", "Sourceid" if "Sourceid" in df.columns else None)

    # Parse ISSN list per journal
    df["_issn_list"] = df[issn_col].apply(split_multi_issn)

    # Normalize title for title-based matching
    if title_col and title_col in df.columns:
        df["_title_norm_scim"] = df[title_col].apply(normalize_title)

    # Keep useful columns for outputs
    keep_cols = [c for c in [title_col, sourceid_col, type_col, issn_col, "_issn_list"] if c]
    base = df[keep_cols].rename(columns={
        title_col or "Title": "Title",
        sourceid_col or "Sourceid": "Sourceid",
        type_col or "Type": "Type",
        issn_col: "Issn",
    })
    if "_title_norm_scim" in df.columns:
        base["_title_norm_scim"] = df["_title_norm_scim"]
    return base


def build_openalex_issn_set(parquet_path: str) -> Set[str]:
    """Read OpenAlex Parquet minimally and return a set of normalized ISSNs present anywhere."""
    head = pd.read_parquet(parquet_path, columns=None, engine="pyarrow").head(5)
    issn_cols = detect_openalex_issn_columns(head)
    if not issn_cols:
        raise RuntimeError("No ISSN columns found in OpenAlex parquet")

    cols_to_read = [c for c in issn_cols if c in head.columns]
    df = pd.read_parquet(parquet_path, columns=cols_to_read, engine="pyarrow")
    exploded = explode_issn_columns(df, cols_to_read)
    if exploded.empty:
        return set()
    return set(exploded["_issn_norm"].astype(str).tolist())


def build_openalex_title_set(parquet_path: str) -> Set[str]:
    """Read OpenAlex Parquet minimally and return a set of normalized venue/source titles present anywhere."""
    head = pd.read_parquet(parquet_path, columns=None, engine="pyarrow").head(5)
    title_cols = detect_openalex_title_columns(head)
    if not title_cols:
        return set()
    cols_to_read = [c for c in title_cols if c in head.columns]
    df = pd.read_parquet(parquet_path, columns=cols_to_read, engine="pyarrow")
    exploded = explode_title_columns(df, cols_to_read)
    if exploded.empty:
        return set()
    return set(exploded["_title_norm"].astype(str).tolist())


def compute_coverage(scim_df: pd.DataFrame, openalex_issn_set: Set[str], openalex_title_set: Set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (summary_df, unmatched_df) using ISSN OR normalized Title matching."""
    def covered_row(row) -> bool:
        # ISSN-based
        for s in row.get("_issn_list", []) or []:
            if s in openalex_issn_set:
                return True
        # Title-based
        t = row.get("_title_norm_scim")
        if t and t in openalex_title_set:
            return True
        return False

    work_df = scim_df.copy()
    work_df["_is_covered"] = work_df.apply(covered_row, axis=1)

    total = int(len(work_df))
    covered_cnt = int(work_df["_is_covered"].sum())
    unmatched_cnt = int(total - covered_cnt)
    coverage_rate = (covered_cnt / total) if total > 0 else 0.0

    summary = pd.DataFrame([
        {
            "total_journals": total,
            "covered_journals": covered_cnt,
            "unmatched_journals": unmatched_cnt,
            "coverage_rate": round(coverage_rate, 6),
        }
    ])

    unmatched = work_df[~work_df["_is_covered"]].copy()
    unmatched["issn_parsed"] = unmatched["_issn_list"].apply(lambda xs: ",".join(xs) if isinstance(xs, list) else "")
    unmatched_out = unmatched[["Title", "Sourceid", "Type", "Issn", "issn_parsed"]]

    return summary, unmatched_out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SCImago vs OpenAlex coverage via ISSN or Title (no year filter)")
    parser.add_argument("--scimago_csv", default="data/raw/scimagojr_communication_journals.csv", help="Path to SCImago CSV (semicolon-separated)")
    parser.add_argument("--openalex_parquet", default="data/processed/openalex_merged.parquet", help="Path to OpenAlex merged Parquet")
    parser.add_argument("--output_dir", default="outputs/reports", help="Directory to write outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_output_dir(args.output_dir)

    scim_df = load_scimago_items(args.scimago_csv)
    openalex_issn = build_openalex_issn_set(args.openalex_parquet)
    openalex_titles = build_openalex_title_set(args.openalex_parquet)

    summary_df, unmatched_df = compute_coverage(scim_df, openalex_issn, openalex_titles)

    summary_path = os.path.join(args.output_dir, "scim_openalex_coverage_summary.csv")
    unmatched_path = os.path.join(args.output_dir, "scim_openalex_unmatched_journals.csv")

    summary_df.to_csv(summary_path, index=False)
    unmatched_df.to_csv(unmatched_path, index=False)

    # Console output for quick view
    out = summary_df.iloc[0].to_dict()
    print(json.dumps({
        "outputs": {
            "coverage_summary_csv": summary_path,
            "unmatched_journals_csv": unmatched_path,
        },
        "summary": out,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()


