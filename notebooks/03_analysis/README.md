# 03_analysis - Notebooks

This directory contains Jupyter notebooks for data analysis tasks, mirroring the functionality of `scripts/03_analysis/` with enhanced interactive exploration capabilities.

## Files

### `new_test_LLM_name_detect_parquet.ipynb`
**Purpose**: Interactive author name sampling and quality inspection from ArticleInfo parquet dataset

**Key Features**:
- 📊 **Data Source**: `data/processed/articleInfo.parquet` (3.8GB, ~30M records)
- 🎯 **Sampling Strategy**: 10 samples per author count group
- 📋 **Column Preservation**: All 16 original columns maintained
- 💾 **Output**: `new_creator_sample.parquet` for manual inspection
- 👁️ **Interactive Display**: Real-time author pattern analysis

**Adapted From**: `scripts/03_analysis/test_LLM_name_detect_parquet.py`

**Key Differences from Original Script**:
- **Data Source**: `articleInfo.parquet` instead of `data_for_analysis.parquet`
- **Author Column**: Uses `authors` field instead of `creator`
- **Column Coverage**: Preserves all 16 columns vs. 4-5 core columns
- **Output File**: `new_creator_sample.parquet` vs. `creator_sample.parquet`
- **Interactive Features**: Enhanced visualization and real-time feedback

## Usage

### Prerequisites
```bash
pip install pandas pyarrow numpy jupyter ipython
```

### Quick Start
1. Open `new_test_LLM_name_detect_parquet.ipynb` in Jupyter Lab/Notebook
2. Run cells sequentially to perform author sampling analysis
3. Review displayed samples for data quality patterns
4. Check generated `new_creator_sample.parquet` for detailed inspection

## Expected Outputs

### Generated Files
- `data/processed/new_creator_sample.parquet` - Complete stratified sample with all columns

### Analysis Results
- Author count distribution statistics
- Stratified samples by author count (10 per group)
- Data quality assessment for manual review

## Integration with Scripts

This notebook complements the existing script-based workflow:
- **Original Script**: `scripts/03_analysis/test_LLM_name_detect_parquet.py` (preserved)
- **Original Output**: `data/processed/creator_sample.parquet` (preserved)
- **New Notebook**: Interactive version with enhanced features
- **New Output**: `data/processed/new_creator_sample.parquet` (additional)

Both outputs can be used for different analysis purposes without conflicts.
