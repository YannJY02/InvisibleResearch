# 02_extraction - Data Extraction Notebooks

This directory contains notebooks for data extraction and conversion tasks, mirroring the functionality of `scripts/02_extraction/` with enhanced interactive processing capabilities.

## Files

## CSV to Parquet Converter

## Overview

This directory contains a Jupyter notebook for high-performance conversion of large CSV files to Parquet format, specifically designed for the InvisibleResearch project's 15GB academic paper metadata.

## Files

- `csv_to_parquet_converter.ipynb` - Main conversion notebook with complete documentation
- `README.md` - This file

### Dimensions Merge (2000–2025)
- `merge_dimension_2000_2025.ipynb` – Merge yearly Dimensions CSVs (`data/raw/dimensions_cs/publications_2000.csv … publications_2025.csv`) using union-of-columns, produce `data/processed/dimension_merged.csv`, then convert to `data/processed/dimension_merged.parquet` via DuckDB. Includes a comprehensive validation block (logical row count parity, `id` uniqueness, DOI normalization duplicates, year range/distribution, key field quality, optional exact-duplicate check).

## Features

### 🚀 High-Performance Processing
- **Streaming Processing**: Memory-efficient chunk-based processing
- **Optimized Configuration**: Tuned for 15GB+ files
- **Progress Tracking**: Real-time progress bars and ETA estimates
- **Error Handling**: Robust error handling with recovery mechanisms

### 📊 Data Quality Assurance
- **Type Optimization**: Intelligent data type conversion and optimization
- **Null Handling**: Proper handling of \N values and missing data
- **Validation**: Comprehensive result validation and integrity checks
- **Performance Benchmarks**: Built-in performance comparison tests

### 🔧 Technical Specifications
- **Input Format**: CSV (any size)
- **Output Format**: Parquet with Snappy compression
- **Memory Management**: Garbage collection and memory cleanup
- **Batch Size**: 50,000 rows per chunk (optimized for 15GB files)
- **Expected Compression**: 70-80% size reduction

## Usage

### Prerequisites
```bash
pip install pandas pyarrow numpy tqdm
```

### Quick Start
1. Open `csv_to_parquet_converter.ipynb` in Jupyter Lab/Notebook
2. Update file paths if necessary
3. Run all cells sequentially
4. Monitor progress and review results

### Configuration
Key parameters can be adjusted in the notebook:
- `CHUNK_SIZE`: Number of rows per processing batch
- `COMPRESSION`: Compression algorithm (default: 'snappy')
- File paths for input/output

## Expected Performance

### File Size Comparison
- **Input CSV**: ~15GB
- **Output Parquet**: ~3-5GB (70-80% compression)

### Processing Time
- **Estimated Duration**: 30-60 minutes
- **Processing Speed**: ~200K-400K rows/minute
- **Memory Usage**: <2GB peak memory

### Query Performance
- **Read Speed Improvement**: 3-10x faster than CSV
- **Storage Efficiency**: 70-80% space savings
- **Type Safety**: Proper data types for reliable processing

## Integration

The converted Parquet file integrates seamlessly with existing InvisibleResearch analysis scripts:

```python
# Data exploration
python scripts/03_analysis/judge_creator.py
python scripts/04_processing/result_GlotLID.py

# Advanced processing (requires API setup)
python scripts/04_processing/LLM_name_detect.py

# Validation
python scripts/05_validation/start_validation.py
```

## File Management

### Input
- `data/raw/articleInfo.csv` - Source CSV file (15GB)

### Output
- `data/processed/articleInfo.parquet` - Converted Parquet file
- Processing logs and statistics displayed in notebook

### Backup Strategy
- Original CSV file is preserved as backup
- Conversion creates new Parquet file without modifying source
- Progress can be resumed if interrupted

## Troubleshooting

### Memory Issues
- Reduce `CHUNK_SIZE` if experiencing memory problems
- Ensure sufficient disk space (2x input file size)
- Close other memory-intensive applications

### Performance Optimization
- SSD storage recommended for optimal performance
- Ensure stable power supply for long conversion process
- Monitor system resources during conversion

### File Path Issues
- Verify input file path exists and is accessible
- Ensure output directory has write permissions
- Check available disk space before starting

## Academic Reproducibility

This notebook is designed for academic reproducibility:
- **Complete Documentation**: Every step is documented and explained
- **Parameter Transparency**: All configuration parameters are clearly specified
- **Progress Tracking**: Detailed logs for conversion statistics
- **Validation**: Built-in result validation ensures data integrity

## Support

For technical issues or questions:
1. Check the notebook's built-in error messages and diagnostics
2. Review the troubleshooting section above
3. Consult the main InvisibleResearch project documentation

---

**Created for InvisibleResearch Project - Academic Data Processing Pipeline**

