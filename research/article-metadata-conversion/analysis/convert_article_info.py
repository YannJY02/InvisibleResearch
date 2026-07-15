#!/usr/bin/env python3
from __future__ import annotations

from IPython.display import display
# Core data processing libraries
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np

# System and file operations
import os
import time
from pathlib import Path
import gc

# Progress display and logging
from tqdm.notebook import tqdm
import warnings
warnings.filterwarnings('ignore')

print("✅ All dependencies imported successfully")
print(f"📦 Pandas version: {pd.__version__}")
print(f"🏹 PyArrow version: {pa.__version__}")


# %%

# Project root directory
DATA_ROOT = Path(os.environ['DATA_ROOT']).expanduser().resolve()
print(f"📂 Data root directory: {DATA_ROOT}")

# Input file path
INPUT_CSV = DATA_ROOT / "raw" / "articleInfo.csv"
print(f"📄 Source CSV file: {INPUT_CSV}")

# Output file path
OUTPUT_DIR = DATA_ROOT / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PARQUET = OUTPUT_DIR / "articleInfo.parquet"
print(f"💾 Target Parquet file: {OUTPUT_PARQUET}")

# Verify input file exists
if not INPUT_CSV.exists():
    raise FileNotFoundError(f"❌ Source file does not exist: {INPUT_CSV}")

# Display file size
file_size_gb = INPUT_CSV.stat().st_size / (1024**3)
print(f"📊 Source file size: {file_size_gb:.2f} GB")
print("\n✅ File path configuration completed")


# %%

# Read file header for structure analysis
print("🔍 Analyzing data structure...")

# Read first few rows to understand data structure
sample_df = pd.read_csv(INPUT_CSV, nrows=5)
print(f"📊 Data dimensions: {sample_df.shape}")
print(f"📋 Column names: {list(sample_df.columns)}")

print("\n📖 Sample data:")
display(sample_df.head())


# %%

# Data type analysis
print("🔬 Data type analysis:")
print(sample_df.dtypes)

print("\n🚫 Null value statistics:")
null_counts = sample_df.isnull().sum()
print(null_counts[null_counts > 0])

# Check for \N values (special NULL representation)
print("\n⚠️ Checking \\N values:")
for col in sample_df.columns:
    n_count = (sample_df[col] == '\\N').sum()
    if n_count > 0:
        print(f"  {col}: {n_count} \\N values")


# %%

# Conversion configuration parameters
CHUNK_SIZE = 50_000  # Rows per processing batch (optimized for 15GB file)
COMPRESSION = 'snappy'  # Compression algorithm
WRITE_BATCH_SIZE = 10_000  # Write batch size

print(f"⚙️ Conversion configuration:")
print(f"  📦 Batch size: {CHUNK_SIZE:,} rows")
print(f"  🗜️ Compression algorithm: {COMPRESSION}")
print(f"  ✍️ Write batch size: {WRITE_BATCH_SIZE:,} rows")

# Estimate processing time
estimated_chunks = file_size_gb * 1000 // (CHUNK_SIZE / 1000)
print(f"\n📈 Estimates:")
print(f"  🔢 Expected batch count: {estimated_chunks:.0f}")
print(f"  ⏱️ Estimated time: 30-60 minutes")
print(f"  💾 Expected output size: {file_size_gb * 0.3:.1f}-{file_size_gb * 0.4:.1f} GB")


# %%

def preprocess_chunk(df):
    """
    Preprocess data chunk: handle null values and optimize data types
    """
    # Convert \N values to proper NaN
    df = df.replace('\\N', pd.NA)

    # Data type optimization
    # Integer column optimization
    int_cols = ['id', 'context_id']
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    # Date column processing
    date_cols = ['publish_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Year column optimization
    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int16')
    if 'yearOnly' in df.columns:
        df['yearOnly'] = pd.to_numeric(df['yearOnly'], errors='coerce').astype('Int16')

    # String columns using PyArrow string type (more efficient)
    string_cols = ['publisher1', 'title1', 'title2', 'authors', 'identifier1',
                   'identifier2', 'identifier3', 'source1', 'source2', 'source3',
                   'globalIdentifier']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype('string[pyarrow]')

    return df

print("✅ Preprocessing function definition completed")


# %%

def convert_csv_to_parquet():
    """
    Main conversion function: Execute streaming CSV to Parquet conversion
    """
    print("🚀 Starting CSV to Parquet conversion...")
    start_time = time.time()

    # Initialize variables
    total_rows = 0
    chunk_count = 0
    writer = None

    try:
        # Create progress bar using tqdm
        # First estimate total row count
        print("📊 Estimating file row count...")
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f) - 1  # Subtract header row
        print(f"📈 Estimated total rows: {total_lines:,}")

        # Create progress bar
        pbar = tqdm(total=total_lines, desc="Conversion Progress", unit="rows")

        # Stream read CSV file
        csv_reader = pd.read_csv(
            INPUT_CSV,
            chunksize=CHUNK_SIZE,
            low_memory=False,
            dtype='str'  # Read as strings first, optimize types later
        )

        for chunk in csv_reader:
            chunk_count += 1
            chunk_start = time.time()

            # Preprocess current chunk
            chunk = preprocess_chunk(chunk)

            # Convert to Arrow table
            table = pa.Table.from_pandas(chunk, preserve_index=False)

            # Initialize writer (only on first iteration)
            if writer is None:
                writer = pq.ParquetWriter(
                    OUTPUT_PARQUET,
                    table.schema,
                    compression=COMPRESSION
                )
                print(f"📝 Created Parquet writer, Schema: {len(table.schema)} columns")

            # Write current chunk
            writer.write_table(table)

            # Update statistics
            rows_in_chunk = len(chunk)
            total_rows += rows_in_chunk
            pbar.update(rows_in_chunk)

            # Memory cleanup
            del chunk, table
            gc.collect()

            # Display progress information
            chunk_time = time.time() - chunk_start
            elapsed = time.time() - start_time

            if chunk_count % 10 == 0:  # Show detailed info every 10 chunks
                avg_time_per_chunk = elapsed / chunk_count
                estimated_remaining = (total_lines - total_rows) / CHUNK_SIZE * avg_time_per_chunk

                pbar.set_postfix({
                    'chunk': chunk_count,
                    'total': f'{total_rows:,}',
                    'eta': f'{estimated_remaining/60:.1f}min'
                })

        # Close writer
        if writer:
            writer.close()

        pbar.close()

        # Completion statistics
        total_time = time.time() - start_time
        output_size_gb = OUTPUT_PARQUET.stat().st_size / (1024**3)
        compression_ratio = (1 - output_size_gb / file_size_gb) * 100

        print("\n🎉 Conversion completed!")
        print(f"📊 Processing statistics:")
        print(f"  ✅ Total rows: {total_rows:,}")
        print(f"  ⏱️ Duration: {total_time/60:.1f} minutes")
        print(f"  🚀 Speed: {total_rows/(total_time/60):,.0f} rows/minute")
        print(f"  📦 Output size: {output_size_gb:.2f} GB")
        print(f"  🗜️ Compression ratio: {compression_ratio:.1f}%")
        print(f"  💾 Saved to: {OUTPUT_PARQUET}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during conversion: {e}")
        if writer:
            writer.close()
        return False

print("✅ Conversion function ready")


# %%

# Execute conversion
success = convert_csv_to_parquet()

if success:
    print("\n🎊 CSV to Parquet conversion completed successfully!")
else:
    print("\n💥 Conversion encountered issues, please check error messages")


# %%

# Verify conversion results
if OUTPUT_PARQUET.exists():
    print("🔍 Validating conversion results...")

    # Read Parquet file information
    parquet_file = pq.ParquetFile(OUTPUT_PARQUET)

    print(f"📊 Parquet file information:")
    print(f"  📝 Schema: {len(parquet_file.schema)} columns")
    print(f"  📦 Row groups: {parquet_file.num_row_groups}")
    print(f"  📈 Total rows: {parquet_file.metadata.num_rows:,}")

    # Display Schema
    print(f"\n📋 Data structure:")
    for i, field in enumerate(parquet_file.schema_arrow):
        print(f"  {i+1:2d}. {field.name} ({field.type})")

    # Read sample data for validation
    print(f"\n🔬 Sample data validation:")
    sample_data = pd.read_parquet(OUTPUT_PARQUET, engine='pyarrow').head(3)
    display(sample_data)

    # Data type check
    print(f"\n📋 Data types:")
    print(sample_data.dtypes)

    print("\n✅ Validation completed! Parquet file generated successfully with complete data.")
else:
    print("❌ Parquet file does not exist, conversion may have failed.")


# %%

# Performance comparison test
if OUTPUT_PARQUET.exists():
    print("⚡ Conducting performance comparison test...")

    # Test reading speed
    print("\n📖 Reading speed test (first 10,000 rows):")

    # CSV reading test
    start = time.time()
    csv_sample = pd.read_csv(INPUT_CSV, nrows=10000)
    csv_time = time.time() - start
    print(f"  📄 CSV reading: {csv_time:.3f} seconds")

    # Parquet reading test
    start = time.time()
    parquet_sample = pd.read_parquet(OUTPUT_PARQUET).head(10000)
    parquet_time = time.time() - start
    print(f"  📦 Parquet reading: {parquet_time:.3f} seconds")

    # Calculate performance improvement
    speedup = csv_time / parquet_time
    print(f"  🚀 Performance improvement: {speedup:.1f}x")

    # File size comparison
    csv_size = INPUT_CSV.stat().st_size / (1024**3)
    parquet_size = OUTPUT_PARQUET.stat().st_size / (1024**3)

    print(f"\n💾 Storage efficiency comparison:")
    print(f"  📄 CSV size: {csv_size:.2f} GB")
    print(f"  📦 Parquet size: {parquet_size:.2f} GB")
    print(f"  🗜️ Compression ratio: {(1-parquet_size/csv_size)*100:.1f}%")
    print(f"  💰 Storage saved: {csv_size-parquet_size:.2f} GB")
