#!/usr/bin/env python3

import argparse
import ast
import json
import os
from typing import Iterable, List, Optional, Set, Tuple

import pandas as pd


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
    return list(dict.fromkeys(out))  # de-duplicate, keep order


def explode_issn_columns(df: pd.DataFrame, issn_columns: List[str]) -> pd.DataFrame:
    present_cols = [c for c in issn_columns if c in df.columns]
    if not present_cols:
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


def detect_openalex_columns(df_head: pd.DataFrame) -> Tuple[List[str], str, Optional[str]]:
    # Candidate ISSN columns based on common schemas
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

    # publication year
    year_candidates = [
        "publication_year",
        "year",
        "from_publication_date_year",
        "biblio_year",
    ]
    year_col = next((c for c in year_candidates if c in df_head.columns), None)

    # id/work id
    id_candidates = [
        "id",
        "work_id",
        "openalex_id",
    ]
    id_col = next((c for c in id_candidates if c in df_head.columns), None)

    return issn_cols, (year_col or "publication_year"), id_col


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Match SCImago Communication journals to OpenAlex works (2020-2025) by ISSN")
    parser.add_argument("--scimagojr_csv", default="data/raw/scimagojr_communication_journals.csv")
    parser.add_argument("--openalex_parquet", default="data/processed/openalex_merged.parquet")
    parser.add_argument("--year_start", type=int, default=2020)
    parser.add_argument("--year_end", type=int, default=2025)
    parser.add_argument("--output_dir", default="outputs/reports")
    parser.add_argument("--per_journal", action="store_true", help="emit per-journal counts as well")
    args = parser.parse_args()

    ensure_output_dir(args.output_dir)

    # Load SCImago CSV
    scim_df = pd.read_csv(args.scimagojr_csv, sep=";", dtype=str, low_memory=False)
    # Try to locate ISSN column heuristically
    scim_cols_lc = {c.lower(): c for c in scim_df.columns}
    issn_col_name = None
    for k in ["issn", "issns", "eissn", "print_issn"]:
        if k in scim_cols_lc:
            issn_col_name = scim_cols_lc[k]
            break
    if issn_col_name is None:
        # Fallback by searching any column containing 'issn'
        for c in scim_df.columns:
            if "issn" in c.lower():
                issn_col_name = c
                break
    if issn_col_name is None:
        raise RuntimeError("Could not detect ISSN column in SCImago CSV")

    scim_df["_issn_list"] = scim_df[issn_col_name].apply(split_multi_issn)
    scim_issn_set: Set[str] = set([x for xs in scim_df["_issn_list"] for x in xs])

    # Load OpenAlex Parquet (minimal columns)
    # Read a small chunk to detect columns
    oa_head = pd.read_parquet(args.openalex_parquet, columns=None, engine="pyarrow").head(5)
    issn_cols, year_col, id_col = detect_openalex_columns(oa_head)
    if not issn_cols:
        # Try to infer by any col containing 'issn'
        inferred = [c for c in oa_head.columns if "issn" in c.lower()]
        issn_cols = inferred
    if not issn_cols:
        raise RuntimeError("No ISSN columns found in OpenAlex parquet")

    needed_cols = list(dict.fromkeys([*(issn_cols), year_col, id_col] if id_col else [*(issn_cols), year_col]))
    oa_df = pd.read_parquet(args.openalex_parquet, columns=[c for c in needed_cols if c in oa_head.columns], engine="pyarrow")

    # Filter by year
    if year_col not in oa_df.columns:
        raise RuntimeError(f"Publication year column '{year_col}' not found in OpenAlex data")
    # Ensure year column is numeric to avoid string-vs-int comparison errors
    oa_df[year_col] = pd.to_numeric(oa_df[year_col], errors="coerce")
    oa_df = oa_df[oa_df[year_col].between(args.year_start, args.year_end, inclusive="both")]

    # Explode ISSN
    oa_exploded = explode_issn_columns(oa_df, issn_cols)
    if oa_exploded.empty:
        raise RuntimeError("OpenAlex data produced no rows with ISSN after explosion")

    # Match
    matched = oa_exploded[oa_exploded["_issn_norm"].isin(scim_issn_set)].copy()

    # Aggregate counts
    if id_col and id_col in matched.columns:
        matched_ids = matched[[id_col, year_col]].drop_duplicates()
    else:
        # fallback: de-duplicate by all columns present
        matched_ids = matched[[year_col]].drop_duplicates()
        matched_ids[id_col or "_row_index"] = range(len(matched_ids))

    total_count = len(matched_ids)
    by_year = matched_ids.groupby(year_col).size().reset_index(name="count").sort_values(year_col)

    # Outputs
    summary_path = os.path.join(args.output_dir, "issn_match_summary_by_year.csv")
    by_year.to_csv(summary_path, index=False)

    per_journal_path = None
    if args.per_journal:
        # Build per-journal mapping by taking SCImago first ISSN hit per work
        # Note: a work may match multiple ISSNs; we keep all associations
        if id_col and id_col in matched.columns:
            per_journal = matched[[id_col, year_col, "_issn_norm"]].drop_duplicates()
        else:
            per_journal = matched[[year_col, "_issn_norm"]].drop_duplicates().assign(**{id_col or "_row_index": range(len(matched))})
        per_journal_counts = per_journal.groupby(["_issn_norm", year_col]).size().reset_index(name="count")
        per_journal_path = os.path.join(args.output_dir, "issn_match_by_journal.csv")
        per_journal_counts.to_csv(per_journal_path, index=False)

    # Console print minimal summary
    print(json.dumps({
        "total_matched_works": int(total_count),
        "year_counts": by_year.to_dict(orient="records"),
        "outputs": {
            "summary_by_year_csv": summary_path,
            "per_journal_csv": per_journal_path,
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
