# Data-Script Mapping and Dependencies

This document provides a comprehensive mapping between data files and scripts, showing the complete data processing pipeline with inputs, outputs, and dependencies.

## 📊 Complete Data Flow Diagram

The processing pipeline follows this sequence:

```
[Raw Data] → [Setup] → [Extraction] → [Analysis] → [Processing] → [Final Output]
```

## 🗂️ Script-Data Correspondence Table

| Script | Input Data | Output Data | Purpose | Dependencies |
|--------|------------|-------------|---------|--------------|
| `scripts/01_setup/pre_stage.bash` | `data/database.sql.gz` | MySQL Database | Database setup and initialization | Docker, MySQL |
| `scripts/01_setup/read_database.py` | MySQL Database | `data/raw/sample_records_language_title_abstract.csv` | Database exploration and sample extraction | MySQL Database |
| `scripts/02_extraction/data_for_analysis_to_parquet.py` | MySQL Database | `data/processed/data_for_analysis.parquet` | Main data extraction (19GB) | MySQL Database |
| `scripts/03_analysis/judge_creator.py` | `data/processed/data_for_analysis.parquet` | Console output | Author field analysis and statistics | - |
| `scripts/03_analysis/test_LLM_name_detect_parquet.py` | `data/processed/data_for_analysis.parquet` | `data/processed/creator_sample.parquet` | Create author samples for LLM processing | - |
| `scripts/03_analysis/scim_openalex_journal_coverage.py` | `data/raw/scimagojr_communication_journals.csv`, `data/processed/openalex_merged.parquet` | `outputs/reports/scim_openalex_coverage_summary.csv`, `outputs/reports/scim_openalex_unmatched_journals.csv` | Compute SCImago coverage (all types) in OpenAlex via ISSN OR Title (no year filter) | PyArrow (Parquet) |
| `scripts/04_processing/LLM_name_detect.py` | `data/processed/creator_sample.parquet` | `data/final/creator_sample_clean.parquet` | LLM-based author name parsing | OpenAI API |
| `scripts/04_processing/result_GlotLID.py` | `data/processed/data_for_analysis.parquet` | `data/final/title_pred_lang.parquet` | Language detection on titles | GlotLID model |
| `scripts/04_processing/ver1_nameparse.py` | `data/processed/data_for_analysis.parquet` | `data/processed/name_clean.parquet` | Traditional rule-based name parsing | - |

## 🔄 Detailed Processing Stages

### Stage 1: Environment Setup (01_setup)

**Script**: `scripts/01_setup/pre_stage.bash`
- **Input**: `data/database.sql.gz` (20GB+ database dump)
- **Output**: Running MySQL database in Docker
- **Purpose**: Initialize the research environment
- **Dependencies**: Docker, MySQL container
- **Execution**: `./scripts/01_setup/pre_stage.bash`

**Script**: `scripts/01_setup/read_database.py`
- **Input**: MySQL database (invisible_research)
- **Output**: `data/raw/sample_records_language_title_abstract.csv` (14KB)
- **Purpose**: Explore database structure and create sample data
- **Dependencies**: Running MySQL database
- **Execution**: `python scripts/01_setup/read_database.py`

### Stage 2: Data Extraction (02_extraction)

**Script**: `scripts/02_extraction/data_for_analysis_to_parquet.py`
- **Input**: MySQL database tables (records, contexts, endpoints)
- **Output**: `data/processed/data_for_analysis.parquet` (~19GB)
- **Purpose**: Extract and convert all data to efficient Parquet format
- **Features**: 
  - Streaming processing for large datasets
  - Multi-core XML parsing
  - Dublin Core field extraction
- **Dependencies**: MySQL database
- **Execution**: `python scripts/02_extraction/data_for_analysis_to_parquet.py`

### Stage 3: Data Analysis (03_analysis)

**Script**: `scripts/03_analysis/judge_creator.py`
- **Input**: `data/processed/data_for_analysis.parquet`
- **Output**: Console analysis results
- **Purpose**: Analyze author field patterns and complexity
- **Features**: Statistical analysis of author counts and formats
- **Dependencies**: None
- **Execution**: `python scripts/03_analysis/judge_creator.py`

**Script**: `scripts/03_analysis/test_LLM_name_detect_parquet.py`
- **Input**: `data/processed/data_for_analysis.parquet`
- **Output**: `data/processed/creator_sample.parquet` (50KB)
- **Purpose**: Create representative samples for LLM processing
- **Features**: Stratified sampling by author count
- **Dependencies**: None
- **Execution**: `python scripts/03_analysis/test_LLM_name_detect_parquet.py`

**Script**: `scripts/03_analysis/scim_openalex_journal_coverage.py`
- **Input**: `data/raw/scimagojr_communication_journals.csv`, `data/processed/openalex_merged.parquet`
- **Output**:
  - `outputs/reports/scim_openalex_coverage_summary.csv`
  - `outputs/reports/scim_openalex_unmatched_journals.csv`
- **Purpose**: Verify coverage of SCImago (all types) in OpenAlex by ISSN OR Title (ANY variant matches)
- **Features**: Robust ISSN parsing, automatic ISSN/Title column detection from OpenAlex, title normalization (case/whitespace/punctuation-insensitive), no year filtering
- **Dependencies**: PyArrow
- **Execution**: `python scripts/03_analysis/scim_openalex_journal_coverage.py`

### Stage 4: Advanced Processing (04_processing)

**Script**: `scripts/04_processing/LLM_name_detect.py`
- **Input**: `data/processed/creator_sample.parquet`
- **Output**: `data/final/creator_sample_clean.parquet` (92KB)
- **Purpose**: Intelligent author name and affiliation extraction
- **Features**: 
  - GPT-4o function calling
  - Async batch processing
  - Smart simple/complex classification
- **Dependencies**: OpenAI API key
- **Execution**: `OPENAI_API_KEY=your_key python scripts/04_processing/LLM_name_detect.py`

**Script**: `scripts/04_processing/result_GlotLID.py`
- **Input**: `data/processed/data_for_analysis.parquet`
- **Output**: `data/final/title_pred_lang.parquet` (~1.8GB)
- **Purpose**: Multilingual language detection for titles
- **Features**: GlotLID model, batch processing
- **Dependencies**: HuggingFace, FastText
- **Execution**: `python scripts/04_processing/result_GlotLID.py`

**Script**: `scripts/04_processing/ver1_nameparse.py`
- **Input**: `data/processed/data_for_analysis.parquet`
- **Output**: `data/processed/name_clean.parquet` (~380MB)
- **Purpose**: Traditional rule-based name parsing (baseline)
- **Features**: nameparser library, deduplication
- **Dependencies**: nameparser
- **Execution**: `python scripts/04_processing/ver1_nameparse.py`

## 🎯 Execution Order and Dependencies

### Required Sequential Order:
1. **Database Setup**: `pre_stage.bash` → `read_database.py`
2. **Data Extraction**: `data_for_analysis_to_parquet.py`
3. **Sample Creation**: `test_LLM_name_detect_parquet.py`

### Parallel Processing Possible:
After step 3, these can run independently:
- `judge_creator.py` (analysis only)
- `LLM_name_detect.py` (requires OpenAI API)
- `result_GlotLID.py` (language detection)
- `ver1_nameparse.py` (traditional parsing)

### Optional Steps:
- `judge_creator.py` - Analysis only, no data output
- `ver1_nameparse.py` - Baseline comparison method
- `read_database.py` - Only needed once for exploration

## 📋 Data File Sizes and Characteristics

| File | Size | Records | Description |
|------|------|---------|-------------|
| `database.sql.gz` | 20GB+ | ~20M | Complete database dump |
| `sample_records_language_title_abstract.csv` | 14KB | 10 | Sample exploration data |
| `data_for_analysis.parquet` | ~19GB | ~20M | Main analysis dataset |
| `articleInfo.parquet` | 3.8GB | ~30M | Processed metadata dataset |
| `creator_sample.parquet` | 50KB | ~100 | Author field samples (from data_for_analysis) |
| `new_creator_sample.parquet` | ~50KB | ~100 | Author field samples (from articleInfo) |
| `creator_sample_clean.parquet` | 92KB | ~100 | LLM-processed authors |
| `title_pred_lang.parquet` | ~1.8GB | ~20M | Language predictions |
| `name_clean.parquet` | ~380MB | ~20M | Traditional name parsing |

## ⚙️ Configuration and Paths

All file paths are configured in `config/settings.py`:

```python
DATA_PATHS = {
    'raw_sample': PROJECT_ROOT / 'data/raw/sample_records_language_title_abstract.csv',
    'database_dump': PROJECT_ROOT / 'data/database.sql.gz',
    'main_data': PROJECT_ROOT / 'data/processed/data_for_analysis.parquet',
    'creator_sample': PROJECT_ROOT / 'data/processed/creator_sample.parquet',
    'name_clean': PROJECT_ROOT / 'data/processed/name_clean.parquet',
    'creator_clean': PROJECT_ROOT / 'data/final/creator_sample_clean.parquet',
    'title_language': PROJECT_ROOT / 'data/final/title_pred_lang.parquet'
}
```

## 🚀 Quick Start Pipeline

Use the provided pipeline script for automatic execution:

```bash
# Full pipeline (with all dependencies)
./run_pipeline.sh

# Manual step-by-step execution
python scripts/02_extraction/data_for_analysis_to_parquet.py
python scripts/03_analysis/judge_creator.py
python scripts/03_analysis/test_LLM_name_detect_parquet.py
OPENAI_API_KEY=your_key python scripts/04_processing/LLM_name_detect.py
python scripts/04_processing/result_GlotLID.py
```

## 🔍 Troubleshooting

### Common Issues:
1. **Missing input files**: Check if previous steps completed successfully
2. **Large file processing**: Ensure sufficient RAM (16GB+ recommended)
3. **API dependencies**: Verify OpenAI API key for LLM processing
4. **Database connection**: Ensure MySQL container is running

### File Dependencies Check:
```bash
# Check if required files exist
ls -la data/processed/data_for_analysis.parquet
ls -la data/processed/creator_sample.parquet
ls -la data/processed/articleInfo.parquet
```

## 📓 Notebooks Integration

The project now includes Jupyter notebooks that mirror and extend the functionality of scripts with interactive capabilities:

### Notebooks Structure
```
notebooks/
├── 01_setup/              (mirrors scripts/01_setup/)
├── 02_extraction/          (data conversion notebooks)
│   ├── csv_to_parquet_converter.ipynb → articleInfo.parquet (3.8GB)
│   ├── merge_dimension_2000_2025.ipynb → dimension_merged.parquet (695.48MB; 358,493 rows; 76 columns)
│   └── README.md
├── 03_analysis/           (interactive analysis notebooks)
│   ├── new_test_LLM_name_detect_parquet.ipynb → new_creator_sample.parquet
│   └── README.md
├── 04_processing/         (mirrors scripts/04_processing/)
│   └── dimension_create_variables.ipynb → data/processed/dimension_data_for_analysis.parquet
└── 05_validation/         (mirrors scripts/05_validation/)
```

### Script-Notebook Correspondence

| Script | Notebook Equivalent | Key Differences |
|--------|-------------------|----------------|
| `scripts/03_analysis/test_LLM_name_detect_parquet.py` | `notebooks/03_analysis/new_test_LLM_name_detect_parquet.ipynb` | Uses `articleInfo.parquet`, preserves all 16 columns, interactive display |

### Additional Outputs from Notebooks

| File | Source | Size | Purpose |
|------|--------|------|---------|
| `articleInfo.parquet` | `notebooks/02_extraction/csv_to_parquet_converter.ipynb` | 3.8GB | High-performance CSV conversion result |
| `dimension_merged.parquet` | `notebooks/02_extraction/merge_dimension_2000_2025.ipynb` | ~695MB | Dimensions publications merged (2000–2025), DuckDB Parquet |
| `dimension_data_for_analysis.parquet` | `notebooks/04_processing/dimension_create_variables.ipynb` | ~0.7GB | Analysis-ready variables with grouped columns and QA summaries |
| `new_creator_sample.parquet` | `notebooks/03_analysis/new_test_LLM_name_detect_parquet.ipynb` | ~50KB | Author samples from articleInfo dataset |

### Notebooks Usage Benefits
- **Interactive Exploration**: Real-time data visualization and inspection
- **Educational Value**: Step-by-step documentation with markdown explanations
- **Experimentation**: Easy parameter tuning and result comparison
- **Enhanced Output**: Rich formatting and display capabilities
- **Complementary Workflow**: Works alongside existing scripts without conflicts

## OpenAlex CSV Merge → Parquet

- Script: `scripts/02_extraction/merge_openalex_csv_to_parquet.py`
- Input: `data/raw/openalex_data/*.csv` (recursive discovery)
- Output:
  - Intermediate CSV (retained): `data/processed/openalex_merged.csv`
  - Parquet: `data/processed/openalex_merged.parquet` (compression: Snappy)
  - Stats: `data/processed/openalex_merged_stats.json` (file count, total rows, columns summary)
- Notes:
  - Preserves all original CSV files (read-only)
  - Column union is computed and enforced; missing fields filled as empty string in CSV stage
  - CSV stage is produced with Python csv writer for stability; Parquet conversion uses DuckDB with `VARCHAR` columns
  - All text columns retained as string to avoid lossy inference
