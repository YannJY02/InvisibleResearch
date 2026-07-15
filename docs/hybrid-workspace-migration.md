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

## Publication Compendium

The active paper-facing material is under
`papers/invisible-communication-science/`. The Source Authority R Markdown
retains SHA-256
`42395d4f28ddaf3d1f062d74d215e68fc93b691d47f2e6632943f976c65797b5`.
Its large CSV input remains external and is referenced by
`data/artifact-versions/dimensions-april2025-consolidated.json`.

```bash
DATA_ROOT=/path/to/InvisibleResearch/data PYTHONPATH=src \
  python papers/invisible-communication-science/analysis/verify_inputs.py
```

This verifies content identity only. It does not create a Paper Analysis
Candidate or Designation Event. Unique inactive text sources were hash-verified
in `GoogleDrive:InvisibleResearch/archive/writing-report-legacy/`; administrative
and private material remains untouched on the human-review list.

## Intake Inbox

`inbox/` is the visible local-only Intake Inbox. Raw contents are ignored and
non-authoritative. Only privacy-safe summaries, hashes, and stable references
may become tracked communication records after review.
