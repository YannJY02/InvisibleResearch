# Data and Command Mapping

Set `DATA_ROOT` to the external InvisibleResearch data directory and expose the
shared package before running a command:

```bash
export DATA_ROOT=/path/to/InvisibleResearch/data
export PYTHONPATH=src
# Required only for database commands:
export MYSQL_URI=mysql+pymysql://user:password@host/database
```

## Shared Workspace

| Capability | Input | Output | Command |
|---|---|---|---|
| Database staging | `$DATA_ROOT/database.sql.gz` | Local MySQL database | `bash src/invisible_research/acquisition/database_stage.bash` |
| Database sample | Local MySQL database | `$DATA_ROOT/raw/sample_records_language_title_abstract.csv` | `python -m invisible_research.acquisition.database_sample` |
| Database extraction | Local MySQL database | `$DATA_ROOT/processed/data_for_analysis.parquet` | `python -m invisible_research.acquisition.database_extract` |
| OpenAlex download | OpenAlex API | `$DATA_ROOT/raw/openalex_communication/*.jsonl` | `python -m invisible_research.acquisition.openalex_download` |
| OpenAlex CSV merge | `$DATA_ROOT/raw/openalex_data/**/*.csv` | `$DATA_ROOT/processed/openalex_merged.parquet` | `python -m invisible_research.acquisition.openalex_merge` |
| Rule-based author processing | `$DATA_ROOT/processed/data_for_analysis.parquet` | `$DATA_ROOT/processed/name_clean.parquet` | `python -m invisible_research.processing.author_names_rules` |
| LLM author processing | `$DATA_ROOT/processed/creator_sample.parquet` | `$DATA_ROOT/derived/creator_sample_clean_v2.parquet` | `python -m invisible_research.processing.author_names_llm` |
| Title language detection | `$DATA_ROOT/processed/data_for_analysis.parquet` | `$DATA_ROOT/derived/title_pred_lang.parquet` | `python -m invisible_research.processing.title_language` |
| Validation | Author sample and derived LLM output | `$DATA_ROOT/validation/` | `python -m invisible_research.validation.start` |

## Exploratory Analysis owners

Question-specific analysis lives under `research/<owner>/`. Each owner README
is the authority for its inputs, analysis command, notebook adapter, and ignored
regenerable artifacts. Shared modules do not own paper claims.

## Publication Compendium

Paper-facing sources live under `papers/invisible-communication-science/`.
Placement in that directory grants no scientific authority. The compendium
README identifies Source Authority, external Artifact Versions, and the
separate Candidate Version and Designation Event gates.

## External data lifecycle

- `raw/`: immutable acquired inputs.
- `processed/`: cleaned or normalized intermediate data.
- `derived/`: results produced from processed inputs.
- `validation/`: human validation state, reports, and backups.

Large data bytes remain outside Git. Portable four-field content identities
are tracked under `data/artifact-versions/` when an external artifact needs a
stable repository reference.
