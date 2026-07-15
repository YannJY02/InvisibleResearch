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

Question-specific analysis and notebooks are not shared capabilities; their
owner migration is tracked separately.
