#!/usr/bin/env python3
"""
Sample 10 rows for every distinct author-count (based on multi-delimiter split),
print them **and** write the combined sample to `creator_sample.parquet`
with extra context columns: id, identifier, title.

Usage:
    python judge_creator.py
"""

from pathlib import Path
import random
import re
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd

# ---------------------------------------------------------------------
PARQUET_PATH = Path("/Users/yann.jy/InvisibleResearch/data_for_analysis.parquet")
OUT_PATH     = Path("creator_sample.parquet")
MAX_SAMPLES  = 10

# Regex for author delimiters EXCLUDING comma (',' may appear in Last, First)
DELIM_RE = re.compile(r"\s*(?:;|&|\band\b|\+|/|\\)\s*", flags=re.IGNORECASE)
# ---------------------------------------------------------------------

# ========== load data =================================================
if not PARQUET_PATH.exists():
    raise SystemExit(f"❌ Parquet file not found: {PARQUET_PATH}")

print(f"🔍 Loading columns from {PARQUET_PATH} …")

# Decide whether 'relation' exists
schema = pq.read_schema(PARQUET_PATH)
has_relation = "relation" in schema.names
cols_needed  = ["id", "identifier", "title", "creator"]
if has_relation:
    cols_needed.append("relation")

table = pq.read_table(PARQUET_PATH, columns=cols_needed)
df = table.to_pandas()

# ========== compute creator_count =====================================
# Count authors by splitting on delimiters (; & 'and' + / \) – comma is ignored
df["creator_count"] = (
    df["creator"]
      .fillna("")            # avoid NaN
      .astype(str)
      .apply(
          lambda x: len([p for p in DELIM_RE.split(x) if p.strip()]) if x.strip() else 0
      )
)

# ========== group & sample ============================================
results = []
sample_frames = []

for count, grp in df.groupby("creator_count"):
    if count == 0:       # skip empty rows
        continue
    sample_n = min(len(grp), MAX_SAMPLES)
    sample_df = grp.sample(sample_n, random_state=0).copy()
    sample_frames.append(sample_df)          # for parquet output

    # gather tuples for pretty printing
    display_cols = ["creator"] + (["relation"] if has_relation else [])
    sample_tuples = list(sample_df[display_cols].itertuples(index=False, name=None))
    results.append((count, sample_tuples))

# ========== print to console ==========================================
for count, creators in sorted(results):
    print(f"\n📝 Author count = {count} (showing {len(creators)} samples)")
    print("-" * 60)
    for i, tup in enumerate(creators, 1):
        creator_str = tup[0]
        rel_str = tup[1] if has_relation else None
        print(f"{i:2d}. {creator_str}")
        if has_relation:
            print(f"    ↳ relation: {rel_str}")

# ========== write sample parquet ======================================
if sample_frames:
    sample_df_total = pd.concat(sample_frames, ignore_index=True)
    # Ensure Arrow engine for compatibility
    sample_df_total.to_parquet(OUT_PATH, index=False, engine="pyarrow")
    print(f"\n✅ Sample parquet written to {OUT_PATH} with {len(sample_df_total)} rows")
else:
    print("⚠️  No non-empty creator rows found; sample parquet not created.")