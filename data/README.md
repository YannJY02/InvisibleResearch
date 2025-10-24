# Data Folder Structure Documentation

## 📁 Folder Classification

### `raw/` - Raw Data (Read-only)
- **sample_records_language_title_abstract.csv**: Language detection sample data (14KB)
- **database.sql.gz**: Complete database dump file (20GB+)
- **Note**: Files in this folder should not be modified to maintain data integrity

### `processed/` - Intermediate Processing Results
- **data_for_analysis.parquet**: Main analysis dataset (~19GB)
  - Contains all Dublin Core fields
  - Extracted from MySQL database
- **creator_sample.parquet**: Author field sample data (50KB)
  - Test samples for LLM processing
- **name_clean.parquet**: Author names cleaned by traditional methods (~380MB)
  - Processed using nameparser library
- **openalex_merged.csv**: Intermediate unioned CSV kept for traceability, source for the Parquet.
- **openalex_merged.parquet**: Merged OpenAlex works CSVs (Snappy) generated from `raw/openalex_data/*.csv` via `scripts/02_extraction/merge_openalex_csv_to_parquet.py`. See `data/processed/openalex_merged_stats.json` for counts & schema notes.
 - **dimension_merged.csv**: Intermediate unioned CSV for Dimensions publications (2000–2025), kept for traceability. Source: `raw/dimensions_cs/publications_*.csv`.
 - **dimension_merged.parquet**: Parquet converted via DuckDB from `dimension_merged.csv` (Snappy). Produced by `notebooks/02_extraction/merge_dimension_2000_2025.ipynb`.
 - **dimension_data_for_analysis.parquet**: Analysis-ready dataset derived by `notebooks/04_processing/dimension_create_variables.ipynb` from `dimension_merged.parquet`. Columns are ordered by conceptual blocks for clarity: [invisibility (with `times_cited`, `date`), geographic/institutional (`research_org_*`), topical (`concepts*`), disciplinary (`issn`, `isbn`, `disciplinary`), OA (`open_access`), controls (`document_type`, `type`, `authors_count`, `reference_ids`, `referenced_pubs`)]. The notebook prints QA summaries (missingness, key constraints, identifier format sanity) and writes only this final file.

### `final/` - Final Analysis Results
- **creator_sample_clean.parquet**: Author data processed by LLM (92KB)
  - Contains original author names, cleaned names, institutional information
- **title_pred_lang.parquet**: Title language prediction results (~1.8GB)
  - Language labels predicted using GlotLID model

## 🔄 Data Flow

```
raw/sample_records_language_title_abstract.csv
    ↓ (scripts/01_setup/read_database.py)
raw/database.sql.gz → MySQL Database
    ↓ (scripts/02_extraction/data_for_analysis_to_parquet.py)
processed/data_for_analysis.parquet
    ↓ (scripts/03_analysis/test_LLM_name_detect_parquet.py)
processed/creator_sample.parquet
    ↓ (scripts/04_processing/LLM_name_detect.py)
final/creator_sample_clean.parquet

processed/data_for_analysis.parquet
    ↓ (scripts/04_processing/result_GlotLID.py)
final/title_pred_lang.parquet

processed/dimension_merged.parquet
    ↓ (notebooks/04_processing/dimension_create_variables.ipynb)
processed/dimension_data_for_analysis.parquet
```

## 📊 Data Statistics

- **Total Records**: ~20 million academic records
- **Language Coverage**: 100+ languages
- **Time Span**: 2000-2024
- **Sources**: 7000+ OAI-PMH endpoints

## ⚠️ Important Notes

1. **Large File Processing**: Main data files exceed 19GB, requiring streaming processing
2. **Version Control**: Large data files are excluded in .gitignore
3. **Backup Strategy**: Important result files should be backed up regularly
4. **Access Permissions**: Raw database dumps may contain sensitive information

## 📋 Detailed Script-Data Mapping

For complete information about which scripts process which data files, see: [`../docs/DATA_SCRIPT_MAPPING.md`](../docs/DATA_SCRIPT_MAPPING.md)
