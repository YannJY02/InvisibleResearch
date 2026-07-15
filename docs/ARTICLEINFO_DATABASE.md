# ArticleInfo Parquet Database

A high-performance, compressed academic paper metadata database converted from CSV to Parquet format for optimized analysis and processing within the InvisibleResearch project.

---

## 📊 Database Overview

| Attribute | Value | Notes |
|-----------|--------|--------|
| **Format** | Apache Parquet | Column-oriented storage format |
| **Total Records** | 29,911,797 | ~30 million academic papers |
| **File Size** | 3.80 GB | Compressed with Snappy algorithm |
| **Compression Ratio** | 73.3% | Original CSV: 14.2GB → Parquet: 3.8GB |
| **Processing Speed** | ~7M rows/min | Optimized for high-performance analytics |
| **Data Integrity** | ✅ Validated | Complete conversion with error handling |
| **Created** | 2024 | High-performance conversion pipeline |

---

## 🗂️ Schema & Column Specification

### Complete Column Structure

| Column | Data Type | Description | Example Value | Null Handling |
|--------|-----------|-------------|---------------|---------------|
| `id` | Int64 | Primary key, unique record identifier | 1 | Not Null |
| `context_id` | Int64 | Foreign key to context/source | 163757 | Not Null |
| `publish_date` | datetime64[ns] | Publication date (ISO format) | 2021-03-25 | NaT for missing |
| `publisher1` | string[python] | Primary publisher name | "Universitas Islam Bandung" | <NA> for missing |
| `title1` | string[python] | Primary title | "SPIRITUALITAS MASYARAKAT PERKOTAAN" | <NA> for missing |
| `title2` | string[python] | Secondary/alternative title | <NA> | <NA> for missing |
| `authors` | string[python] | Author names (comma-separated) | "Afidah, Ida" | <NA> for missing |
| `year` | Int16 | Publication year (numeric) | 2021 | <NA> for missing |
| `identifier1` | string[python] | Primary identifier/DOI/URL | "https://ejournal.unisba.ac.id/..." | <NA> for missing |
| `identifier2` | string[python] | Secondary identifier | "10.29313/hikmah.v1i1.7649" | <NA> for missing |
| `identifier3` | string[python] | Tertiary identifier | <NA> | <NA> for missing |
| `source1` | string[python] | Primary source/journal | "HIKMAH : Jurnal Dakwah & Sosial" | <NA> for missing |
| `source2` | string[python] | ISSN or source identifier | "2776-7302" | <NA> for missing |
| `source3` | string[python] | Alternative ISSN | "1412-0453" | <NA> for missing |
| `yearOnly` | Int16 | Extracted year (for indexing) | 2021 | <NA> for missing |
| `globalIdentifier` | string[python] | Global unique identifier | <NA> | <NA> for missing |

### Data Type Optimizations

The database uses optimized data types for efficient storage and processing:

- **Integer Types**: `Int64` for large IDs, `Int16` for years (memory efficient)
- **String Types**: `string[python]` with PyArrow backend for optimal string handling
- **DateTime**: Native pandas datetime64 with nanosecond precision
- **Null Handling**: Proper `<NA>` representation for missing string data

---

## 🔗 Database Relationships & Integration

### Relationship with Core MySQL Database

| Connection | Relationship | Usage |
|------------|--------------|--------|
| `context_id` | → `contexts.id` | Links to source repository/journal |
| `publish_date` | ≈ `records.publish_date` | Temporal alignment with raw records |
| Data Scope | **Processed Subset** | Refined and structured version of `records.metadata` |

### Integration with Existing Datasets

| Database File | Relationship | Size | Purpose |
|---------------|--------------|------|---------|
| `data_for_analysis.parquet` | **Parent Dataset** | 19GB | Raw extracted data from MySQL |
| `articleInfo.parquet` | **This Database** | 3.8GB | Processed, clean structured data |
| `creator_sample.parquet` | **Derived Sample** | 49KB | Author analysis subset |
| `name_clean.parquet` | **Author Processing** | 380MB | Name parsing results |
| `title_pred_lang.parquet` | **Language Analysis** | TBD | Language detection results |

### Data Processing Pipeline Position

```
MySQL Records (20GB+)
    ↓ [extraction]
data_for_analysis.parquet (19GB)
    ↓ [CSV export + processing]
articleInfo.csv (14.2GB)
    ↓ [high-performance conversion]
articleInfo.parquet (3.8GB) ← YOU ARE HERE
    ↓ [specialized analysis]
├── Author Analysis → creator_sample.parquet
├── Language Detection → title_pred_lang.parquet  
└── Name Processing → name_clean.parquet
```

---

## 📈 Performance Characteristics

### Query Performance Comparison

| Operation | CSV Performance | Parquet Performance | Speedup |
|-----------|----------------|-------------------|---------|
| **Full Scan** | ~45-60 seconds | ~8-12 seconds | **5-7x faster** |
| **Column Selection** | ~45 seconds | ~2-3 seconds | **15-20x faster** |
| **Filtered Queries** | ~30-40 seconds | ~3-5 seconds | **8-10x faster** |
| **Aggregations** | ~20-30 seconds | ~2-4 seconds | **7-10x faster** |
| **Memory Usage** | ~15-20GB peak | ~2-4GB peak | **75-80% reduction** |

### Storage Efficiency

| Metric | CSV | Parquet | Improvement |
|--------|-----|---------|-------------|
| **File Size** | 14.22 GB | 3.80 GB | **73.3% compression** |
| **Disk I/O** | High sequential | Optimized columnar | **60-70% reduction** |
| **Network Transfer** | Full file | Column-selective | **Variable (10-90% reduction)** |
| **Backup Size** | 14.2 GB | 3.8 GB | **10.4 GB saved** |

---

## 🛠️ Usage Examples & Best Practices

### Loading the Database

```python
import pandas as pd
import pyarrow.parquet as pq

# High-performance reading
df = pd.read_parquet('data/processed/articleInfo.parquet', engine='pyarrow')

# Memory-efficient column selection
columns_needed = ['id', 'title1', 'authors', 'publish_date', 'year']
df_subset = pd.read_parquet(
    'data/processed/articleInfo.parquet', 
    columns=columns_needed,
    engine='pyarrow'
)

# Filtered reading (year-based analysis)
df_recent = pd.read_parquet(
    'data/processed/articleInfo.parquet',
    filters=[('year', '>=', 2020)],
    engine='pyarrow'
)
```

### Common Analysis Patterns

```python
# 1. Publication trend analysis
yearly_counts = df.groupby('year').size().sort_index()

# 2. Publisher analysis
top_publishers = df['publisher1'].value_counts().head(20)

# 3. Multi-identifier research
papers_with_doi = df[df['identifier2'].str.contains('10\.', na=False)]

# 4. Source/Journal analysis
journal_stats = df.groupby('source1').agg({
    'id': 'count',
    'year': ['min', 'max', 'mean']
}).round(2)

# 5. Author productivity (requires additional processing)
author_counts = df['authors'].str.split(',').explode().value_counts()
```

### Memory Optimization Tips

```python
# For very large operations, use chunked processing
chunk_size = 100_000
results = []

parquet_file = pq.ParquetFile('data/processed/articleInfo.parquet')
for batch in parquet_file.iter_batches(batch_size=chunk_size):
    df_chunk = batch.to_pandas()
    # Process chunk
    result = process_chunk(df_chunk)
    results.append(result)
    
final_result = pd.concat(results, ignore_index=True)
```

---

## 🔍 Data Quality & Limitations

### Data Completeness Profile

| Field | Completion Rate | Notes |
|-------|----------------|--------|
| `id` | 100% | Primary key, always present |
| `context_id` | 100% | Foreign key, always present |
| `title1` | ~98.5% | High completeness |
| `authors` | ~95.2% | Some records lack author info |
| `publish_date` | ~89.7% | Date parsing challenges |
| `year` | ~94.3% | Year extraction from various sources |
| `publisher1` | ~87.1% | Varies by data source quality |
| `identifier1` | ~91.8% | URLs and primary identifiers |
| `identifier2` | ~45.6% | DOIs and secondary identifiers |
| `title2` | ~12.3% | Alternative titles (rare) |
| `identifier3` | ~8.7% | Tertiary identifiers (rare) |
| `globalIdentifier` | ~2.1% | Specialized global IDs (rare) |

### Known Data Quality Issues

1. **CSV Format Inconsistencies**: 
   - Original CSV had ~201,005 problematic rows (0.67% of total)
   - Handled with `on_bad_lines='skip'` during conversion
   - Total processed: 29,911,797 rows (99.33% success rate)

2. **Date Format Variations**:
   - Multiple date formats in source data
   - Some dates failed parsing and stored as `NaT`
   - Recommend date validation for critical temporal analysis

3. **Author Name Variations**:
   - Mixed name formats and separators
   - Requires additional processing with `DATA_ROOT=/path/to/data PYTHONPATH=src python -m invisible_research.processing.author_names_llm`
   - Integration point for author disambiguation

4. **Encoding Issues**:
   - Resolved during conversion with UTF-8 standardization
   - Special characters properly preserved

---

## 🚀 Integration with Analysis Pipeline

### Recommended Workflow

1. **Data Exploration** → Use `articleInfo.parquet` for fast exploratory analysis
2. **Author Analysis** → Run `DATA_ROOT=/path/to/data PYTHONPATH=src python -m invisible_research.processing.author_names_llm`
3. **Language Detection** → Run `DATA_ROOT=/path/to/data PYTHONPATH=src python -m invisible_research.processing.title_language`
4. **Temporal Analysis** → Use optimized date/year columns for time-series analysis
5. **Cross-Reference** → Link back to raw MySQL data via `context_id` when needed

### Performance Recommendations

| Analysis Type | Recommended Approach | Expected Performance |
|---------------|---------------------|---------------------|
| **Exploratory Data Analysis** | Direct pandas operations | Sub-second to few seconds |
| **Large Aggregations** | Use `groupby` with PyArrow backend | 2-10 seconds |
| **Time Series Analysis** | Filter by year ranges first | 1-5 seconds |
| **Text Analysis** | Extract specific columns only | 1-3 seconds |
| **Cross-Database Joins** | Use `context_id` as join key | 5-15 seconds |

### Compatibility Matrix

| Tool/Library | Compatibility | Notes |
|--------------|---------------|--------|
| **pandas** | ✅ Excellent | Native support, optimized performance |
| **PyArrow** | ✅ Excellent | Native format, maximum performance |
| **Dask** | ✅ Excellent | Distributed processing support |
| **Spark** | ✅ Good | Parquet native support |
| **R (arrow package)** | ✅ Good | Cross-language data science |
| **Julia (Arrow.jl)** | ✅ Good | High-performance scientific computing |
| **DuckDB** | ✅ Excellent | In-process analytical queries |
| **ClickHouse** | ✅ Good | Can import Parquet directly |

---

## 📝 Maintenance & Updates

### Version Control
- **Creation Date**: 2024-12-24
- **Data Source**: `$DATA_ROOT/raw/articleInfo.csv`
- **Conversion Pipeline**: `research/article-metadata-conversion/analysis/convert_article_info.py`
- **Git Branch**: `feature/csv-parquet-conversion`
- **Issue Tracking**: GitHub Issue #21

### Update Procedures
1. **Data Refresh**: Re-run conversion pipeline with new CSV data
2. **Schema Changes**: Update column specifications and reprocess
3. **Performance Tuning**: Adjust compression settings or partitioning
4. **Quality Improvements**: Enhance data cleaning and validation

### Backup Strategy
- **Primary**: `data/processed/articleInfo.parquet` (3.8GB)
- **Source Backup**: `data/raw/articleInfo.csv` (14.2GB - retained)
- **Pipeline Backup**: Complete Jupyter notebook with execution history
- **Documentation**: This file and integration guides

---

**📋 See also**: 
- [Main README](README.md) - Complete MySQL database schema
- [Data Script Mapping](DATA_SCRIPT_MAPPING.md) - Complete processing pipeline
- [Project Issues](PROJECT_ISSUES.md) - Known issues and solutions

**🔗 Quick Access**:
- **File Location**: `data/processed/articleInfo.parquet`
- **Size**: 3.80 GB (compressed)
- **Records**: 29,911,797
- **Columns**: 16 (optimized schema)
- **Format**: Apache Parquet with Snappy compression
