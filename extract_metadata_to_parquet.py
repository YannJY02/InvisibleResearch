"""
extract_metadata_to_parquet.py
------------------------------
Batch‑extracts specific Dublin Core fields from the `metadata` column
in the `records` table and writes them to a compressed Parquet file.

Fields extracted per record:
  • identifier   • title
  • description  • subject
  • language    • date
  • creator     • type
  • context_id  • set_spec
  • oai_url    • repository_name

The script streams the table in chunks, parses XML in parallel
using multiple CPU cores, and appends results to a single Parquet
file (`records_metadata.parquet`) with Snappy compression.

Run:
    python extract_metadata_to_parquet.py
"""

import os
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, Dict, Any

import pandas as pd
from sqlalchemy import create_engine
from lxml import etree
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
MYSQL_URI = "mysql+pymysql://root:secret@127.0.0.1:3306/invisible_research"
CHUNK_SIZE = 100_000                       # rows per chunk
MAX_WORKERS = 6        # parallel XML parsers
OUT_FILE = "records_metadata.parquet"    # output file
# ---------------------------------------------------------------------

TARGET_COLS = [
    "id",
    "identifier",
    "title",
    "description",
    "subject",
    "language",
    "date",
    "creator",
    "type",
    "context_id"
]

# XML namespace for Dublin‑Core
DC_NS = {"dc": "http://purl.org/dc/elements/1.1/"}


def parse_xml(record: Tuple[Any, str, Any]) -> Dict[str, Any]:
    """
    Parse a single metadata XML string and return the desired fields.
    Falls back to None when a tag is missing or XML is invalid.
    """
    rec_id, xml, ctx_id = record
    out = {"id": rec_id, "context_id": ctx_id}
    # Initialise keys with None
    for col in TARGET_COLS[1:]:
        if col not in out:
            out[col] = None

    if not xml:
        return out

    try:
        root = etree.fromstring(xml.encode("utf-8"))
        # Extract each tag text once
        out["identifier"]  = root.findtext(".//dc:identifier",  namespaces=DC_NS)
        out["title"]       = root.findtext(".//dc:title",       namespaces=DC_NS)
        out["description"] = root.findtext(".//dc:description", namespaces=DC_NS)
        out["subject"]     = root.findtext(".//dc:subject",     namespaces=DC_NS)
        out["language"]    = root.findtext(".//dc:language",    namespaces=DC_NS)
        out["date"]        = root.findtext(".//dc:date",        namespaces=DC_NS)
        out["creator"]     = root.findtext(".//dc:creator",     namespaces=DC_NS)
        out["type"]        = root.findtext(".//dc:type",        namespaces=DC_NS)
    except Exception:
        # Keep None values on parse error
        pass

    return out


def main() -> None:
    start = time.time()
    engine = create_engine(MYSQL_URI)

    writer = None
    total_rows = 0
    chunk_no = 0

    SQL = "SELECT id, metadata, context_id FROM records"

    with engine.connect().execution_options(stream_results=True) as conn:
        ctx_df = pd.read_sql("SELECT id AS context_id, set_spec, endpoint_id FROM contexts", conn)
        ep_df = pd.read_sql("SELECT id AS endpoint_id, oai_url, repository_name FROM endpoints", conn)

        for chunk in pd.read_sql(SQL, conn, chunksize=CHUNK_SIZE):
            chunk_no += 1
            # Parallel XML parsing
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
                parsed_rows = list(pool.map(parse_xml, chunk.itertuples(index=False, name=None)))

            df = pd.DataFrame(parsed_rows, columns=TARGET_COLS)

            # merge endpoint_id first to bring it into df
            df = df.merge(ctx_df, on="context_id", how="left")
            df = df.merge(ep_df, on="endpoint_id", how="left", suffixes=("", ""))

            df = df.drop(columns=["endpoint_id"])

            for col in ["set_spec", "oai_url", "repository_name"]:
                if col not in df.columns:
                    df[col] = None
                df[col] = df[col].astype("string[pyarrow]")

            table = pa.Table.from_pandas(df, preserve_index=False)

            if writer is None:
                writer = pq.ParquetWriter(
                    OUT_FILE,
                    table.schema,
                    compression="snappy",
                )

            writer.write_table(table)
            total_rows += len(df)

            elapsed = time.time() - start
            print(f"[{chunk_no}] wrote {len(df):,} rows "
                  f"(total {total_rows:,})  elapsed {elapsed/60:.1f} min")

    if writer:
        writer.close()

    print(f"\n✅ Completed. {total_rows:,} rows saved to {OUT_FILE}. "
          f"Total time: {(time.time()-start)/60:.1f} min.")


if __name__ == "__main__":
    main()