# Hybrid Workspace Migration Record

The migration consolidated reusable behavior under `src/invisible_research/`.
The temporary root `run_pipeline.sh` adapter and phase-numbered directories were
verified during the migration window and then removed. Git history preserves
their exact pre-cutover form.

Set `DATA_ROOT` to the external data directory before running a command:

```bash
export DATA_ROOT=/path/to/invisible-research-data
```

| Capability | Command |
|---|---|
| Database staging | `bash src/invisible_research/acquisition/database_stage.bash` |
| Database sample | `PYTHONPATH=src python -m invisible_research.acquisition.database_sample` |
| Database extraction | `PYTHONPATH=src python -m invisible_research.acquisition.database_extract` |
| OpenAlex download | `PYTHONPATH=src python -m invisible_research.acquisition.openalex_download` |
| OpenAlex merge | `PYTHONPATH=src python -m invisible_research.acquisition.openalex_merge` |
| LLM author processing | `PYTHONPATH=src python -m invisible_research.processing.author_names_llm` |
| Rule-based author processing | `PYTHONPATH=src python -m invisible_research.processing.author_names_rules` |
| Title language detection | `PYTHONPATH=src python -m invisible_research.processing.title_language` |
| Validation suite | `PYTHONPATH=src python -m invisible_research.validation.start` |

The external lifecycle directory was renamed from `final/` to `derived/` only
after each retained file's Google Drive content checksum, byte size, and stable
item ID were recorded before and after the move. The machine-readable evidence
is [`data-lifecycle-cutover.json`](data-lifecycle-cutover.json).

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
in `GoogleDrive:InvisibleResearch/archive/writing-report-legacy/`. After explicit
owner approval, seven administrative, private, or potentially copyrighted files
were hash-verified under `GoogleDrive:InvisibleResearch/archive/writing-report-human-review/`
and the duplicate local-only workspace was removed. The decision record is
[`writing-report-human-review.md`](writing-report-human-review.md).

## Intake Inbox

`inbox/` is the visible local-only Intake Inbox. Raw contents are ignored and
non-authoritative. Only privacy-safe summaries, hashes, and stable references
may become tracked communication records after review.
