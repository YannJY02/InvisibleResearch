"""
result_GlotLID.py
-----------------
Stream‑read titles from a large Parquet file, predict their language
with GlotLID, and save a new Parquet with columns
[id, title, language_db, language_pred].

Input : $DATA_ROOT/processed/data_for_analysis.parquet
Output: $DATA_ROOT/derived/title_pred_lang.parquet
"""

import os
import pyarrow.dataset as ds
import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
import fasttext

from ..data import resolve_data_root

# ------------------------------------------------------------------
BATCH_SIZE  = 50_000   # adjust to available RAM
# ------------------------------------------------------------------

def main():
    data_root = resolve_data_root()
    parquet_in = data_root / "processed" / "data_for_analysis.parquet"
    parquet_out = data_root / "derived" / "title_pred_lang.parquet"
    parquet_out.parent.mkdir(parents=True, exist_ok=True)
    # Locate or download GlotLID model from Hugging Face cache
    model_path = hf_hub_download(repo_id="cis-lmu/glotlid", filename="model.bin")
    model = fasttext.load_model(model_path)
    print(f"GlotLID model loaded from {model_path}")

    # helper function to batch‑predict languages
    def predict_batch(texts):
        """
        fastText model.predict returns a list-of-lists, e.g.
        [['__label__en'], ['__label__id'], ...].
        Convert to plain ISO codes without the prefix.
        """
        # fastText cannot handle '\n' inside a line
        cleaned = [t.replace("\n", " ").replace("\r", " ") for t in texts]
        label_lists, _ = model.predict(cleaned)
        return [
            lst[0].replace("__label__", "") if lst else None
            for lst in label_lists
        ]

    dataset = ds.dataset(parquet_in, format="parquet")

    # prepare Parquet writer lazily
    writer = None
    total = 0

    # iterate over record batches
    for batch in dataset.to_batches(batch_size=BATCH_SIZE, columns=["id", "title", "language"]):
        tbl = pa.Table.from_batches([batch])

        # to pandas for convenience
        df = tbl.to_pandas()
        titles = df["title"].fillna("").astype(str).tolist()

        # predict language for each title
        preds = predict_batch(titles)
        df["language_pred"] = preds
        df = df.rename(columns={"language": "language_db"})

        # back to Arrow and write
        out_tbl = pa.Table.from_pandas(df, preserve_index=False)

        if writer is None:
            writer = pq.ParquetWriter(
                parquet_out, out_tbl.schema, compression="snappy"
            )
        writer.write_table(out_tbl)
        total += len(df)
        print(f"Processed {total:,} rows")

    if writer:
        writer.close()
    print(f"✅ Saved to {parquet_out}  (rows: {total:,})")

if __name__ == "__main__":
    main()
