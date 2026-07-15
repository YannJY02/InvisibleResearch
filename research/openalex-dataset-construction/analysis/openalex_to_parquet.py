#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Iterator, List, Optional

import requests
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm
# Optional: load .env using python-dotenv if available; fallback to manual loader
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    def _simple_load_dotenv(path: str = ".env") -> None:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                os.environ.setdefault(key, val)
    _simple_load_dotenv()

# Configuration (fixed as per confirmation)
SUBFIELD_ID = "subfields/3315"  # Communication
START_YEAR = int(os.getenv("OPENALEX_START_YEAR", 2000))
END_YEAR = int(os.getenv("OPENALEX_END_YEAR", 2025))
PARQUET_PATH = str(Path(os.environ["DATA_ROOT"]) / "processed" / "communication_works.parquet")
PER_PAGE_CANDIDATES = [200, 150, 100]  # try larger first, fallback if needed
REQUEST_TIMEOUT = 60
RETRY_MAX = 5
BACKOFF_BASE = 1.5

# Polite pool email from environment
CONTACT_EMAIL = os.getenv("OPENALEX_MAILTO")
if not CONTACT_EMAIL:
    raise RuntimeError("Please set environment variable OPENALEX_MAILTO to your contact email.")

os.makedirs(os.path.dirname(PARQUET_PATH), exist_ok=True)

BASE_URL = "https://api.openalex.org/works"

# ---- CSV schema mapping for select ----
import csv
CSV_SCHEMA_PATH = os.getenv(
    "CSV_SCHEMA_PATH",
    str(Path(os.environ["DATA_ROOT"]) / "raw" / "works-2025-09-07T08-08-59.csv"),
)
with open(CSV_SCHEMA_PATH, "r", encoding="utf-8") as _f:
    _reader = csv.reader(_f)
    SCHEMA_COLUMNS = next(_reader)
TOP_LEVEL_FIELDS = set()
for col in SCHEMA_COLUMNS:
    if col == "abstract":
        TOP_LEVEL_FIELDS.add("abstract_inverted_index")
        continue
    if "." in col:
        TOP_LEVEL_FIELDS.add(col.split(".", 1)[0])
    else:
        TOP_LEVEL_FIELDS.add(col)
TOP_LEVEL_FIELDS.add("id")
SELECT_PARAM = ",".join(sorted(TOP_LEVEL_FIELDS))


def fetch_page(year: int, cursor: str, per_page: int, mailto: str) -> Dict[str, Any]:
    params = {
        "filter": f"primary_topic.subfield.id:{SUBFIELD_ID},publication_year:{year}",
        "per-page": per_page,
        "cursor": cursor,
        "mailto": mailto,
        "select": SELECT_PARAM,
    }
    resp = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def iterate_year(year: int, per_page: int, mailto: str, sleep_seconds: float = 0.3) -> Iterator[Dict[str, Any]]:
    cursor = "*"
    total_retrieved = 0
    meta_count: Optional[int] = None
    while True:
        data = fetch_page(year, cursor=cursor, per_page=per_page, mailto=mailto)
        if meta_count is None:
            meta_count = data.get("meta", {}).get("count")
            print(f"Year {year}: expected {meta_count} works with per_page={per_page}")
        results = data.get("results", [])
        for work in results:
            total_retrieved += 1
            yield work
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        cursor = next_cursor
        time.sleep(sleep_seconds)
    if meta_count is not None and total_retrieved != meta_count:
        print(f"WARNING: Year {year} mismatch: retrieved {total_retrieved} vs meta.count {meta_count}")
    else:
        print(f"Year {year}: validated {total_retrieved} works")


def robust_iterate_year(year: int, mailto: str) -> Iterator[Dict[str, Any]]:
    last_error: Optional[Exception] = None
    for per_page in PER_PAGE_CANDIDATES:
        for attempt in range(1, RETRY_MAX + 1):
            try:
                yield from iterate_year(year, per_page=per_page, mailto=mailto)
                last_error = None
                break
            except requests.HTTPError as e:
                last_error = e
                status = getattr(e.response, "status_code", None)
                if status in (429, 502, 503, 504):
                    delay = BACKOFF_BASE ** attempt
                    print(f"HTTP {status} on year {year}, per_page={per_page}, retry {attempt}/{RETRY_MAX} after {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                raise
            except requests.RequestException as e:
                last_error = e
                delay = BACKOFF_BASE ** attempt
                print(f"Network error on year {year}, per_page={per_page}, retry {attempt}/{RETRY_MAX} after {delay:.1f}s...")
                time.sleep(delay)
                continue
        if last_error is None:
            return
    if last_error is not None:
        raise last_error


def _flatten_list(values: List[Any]) -> List[Any]:
    out: List[Any] = []
    for v in values:
        if isinstance(v, list):
            out.extend(_flatten_list(v))
        else:
            out.append(v)
    return out


def extract_path(obj: Any, path: str) -> Any:
    if path == "abstract":
        inv = obj.get("abstract_inverted_index") if isinstance(obj, dict) else None
        if not isinstance(inv, dict):
            return None
        max_pos = -1
        for word, positions in inv.items():
            if positions:
                max_pos = max(max_pos, max(positions))
        if max_pos < 0:
            return None
        words = [None] * (max_pos + 1)
        for word, positions in inv.items():
            for pos in positions:
                if 0 <= pos < len(words) and words[pos] is None:
                    words[pos] = word
        return " ".join(w for w in words if isinstance(w, str))

    parts = path.split(".")
    def _walk(current: Any, idx: int) -> Any:
        if idx == len(parts):
            return current
        key = parts[idx]
        if isinstance(current, dict):
            return _walk(current.get(key), idx + 1)
        if isinstance(current, list):
            return _flatten_list([_walk(item, idx) for item in current])
        return None
    return _walk(obj, 0)


def flatten_work(record: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {}
    for col in SCHEMA_COLUMNS:
        try:
            v = extract_path(record, col)
            if isinstance(v, (list, dict)):
                v = json.dumps(v, ensure_ascii=False)
            row[col] = v
        except Exception:
            row[col] = None
    return row


start = datetime.now()
print(f"Writing to {PARQUET_PATH}")
writer: Optional[pq.ParquetWriter] = None
schema: Optional[pa.schema] = None

try:
    for year in range(START_YEAR, END_YEAR + 1):
        batch_rows: List[Dict[str, Any]] = []
        with tqdm(desc=f"Year {year}", unit="works") as pbar:
            for work in robust_iterate_year(year, mailto=CONTACT_EMAIL):
                batch_rows.append(flatten_work(work))
                # flush in chunks to manage memory
                if len(batch_rows) >= 2000:
                    table = pa.Table.from_pylist(batch_rows)
                    if writer is None:
                        schema = table.schema
                        writer = pq.ParquetWriter(PARQUET_PATH, schema=schema)
                    writer.write_table(table)
                    pbar.update(len(batch_rows))
                    batch_rows.clear()
            # flush remainder for the year
            if batch_rows:
                table = pa.Table.from_pylist(batch_rows)
                if writer is None:
                    schema = table.schema
                    writer = pq.ParquetWriter(PARQUET_PATH, schema=schema)
                writer.write_table(table)
                pbar.update(len(batch_rows))
                batch_rows.clear()
finally:
    if writer is not None:
        writer.close()
        print(f"Closed Parquet writer: {PARQUET_PATH}")
    elapsed = datetime.now() - start
    print(f"Completed in {elapsed}")
