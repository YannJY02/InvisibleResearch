# Hybrid Workspace Migration

The migration branch owns reusable behavior under `src/invisible_research/`.
The numbered acquisition, processing, and validation code paths remain available
on `main` until the final cutover; `run_pipeline.sh` is the temporary command
adapter during the verification window.

Set `DATA_ROOT` to the external data directory before running a command:

```bash
export DATA_ROOT=/path/to/invisible-research-data
```

| Capability | Command |
|---|---|
| Database staging | `./run_pipeline.sh database-stage` |
| Database sample | `./run_pipeline.sh database-sample` |
| Database extraction | `./run_pipeline.sh database-extract` |
| OpenAlex download | `./run_pipeline.sh openalex-download` |
| OpenAlex merge | `./run_pipeline.sh openalex-merge` |
| LLM author processing | `./run_pipeline.sh author-names-llm` |
| Rule-based author processing | `./run_pipeline.sh author-names-rules` |
| Title language detection | `./run_pipeline.sh title-language` |
| Validation suite | `./run_pipeline.sh validation` |

## Exploratory Analysis owners

| Owner | Canonical command or adapter |
|---|---|
| Article metadata conversion | `research/article-metadata-conversion/analysis/convert_article_info.py` |
| Author-name sampling | `research/author-name-sampling/analysis/sample_creators.py` |
| Dimensions dataset construction | `research/dimensions-dataset-construction/analysis/merge_dimensions.py` |
| OpenAlex dataset construction | `research/openalex-dataset-construction/analysis/openalex_to_parquet.py` |
| SCImago/OpenAlex coverage | `research/scimago-openalex-coverage/analysis/coverage.py` |

Each owner README records its question, referenced inputs, and complete run
commands. Notebook files are presentation/exploration adapters over the owner
analysis commands. Regenerable reports are written to ignored owner-local
`artifacts/` directories; the prior tracked reports and executed notebook are
retained only in Git history.
