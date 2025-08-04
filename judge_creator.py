#!/usr/bin/env python3
"""
Show 10 sample rows for every distinct author-count (based on ';' delimiter).
"""

from pathlib import Path
import random
import re
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd

# ---------------------------------------------------------------------
PARQUET_PATH = Path("/Users/yann.jy/InvisibleResearch/data_for_analysis.parquet")
MAX_SAMPLES  = 10
# Regex pattern for author delimiters EXCLUDING comma (',' may appear inside names)
DELIM_RE = re.compile(r"\s*(?:;|&|\band\b|\+|/|\\)\s*", flags=re.IGNORECASE)
# ---------------------------------------------------------------------

if not PARQUET_PATH.exists():
    raise SystemExit(f"❌ Parquet file not found: {PARQUET_PATH}")

print(f"🔍 Loading 'creator' column from {PARQUET_PATH} …")
# 'relation' is expected to contain the PDF or external download URL for manual verification
table = pq.read_table(PARQUET_PATH, columns=["creator", "relation"])
df = table.to_pandas()

 # ① Count authors by splitting on delimiters (; & 'and' + / \) – comma is ignored
df["creator_count"] = (
    df["creator"]
    .fillna("")            # avoid NaN
    .astype(str)
    .apply(
        lambda x: len([p for p in DELIM_RE.split(x) if p.strip()]) if x.strip() else 0
    )
)

 # ② Group by author_count and sample
results = []
for count, grp in df.groupby("creator_count"):
    if count == 0:       # skip empty rows
        continue
    sample_n = min(len(grp), MAX_SAMPLES)
    sample_df = grp.sample(sample_n, random_state=0)[["creator", "relation"]]
    sample_tuples = list(sample_df.itertuples(index=False, name=None))  # (creator, relation)
    results.append((count, sample_tuples))

# ③ Print results
for count, creators in sorted(results):
    print(f"\n📝 Author count = {count} (showing {len(creators)} samples)")
    print("-" * 60)
    for i, (c, rel) in enumerate(creators, 1):
        print(f"{i:2d}. {c}")
        print(f"    ↳ relation: {rel}")