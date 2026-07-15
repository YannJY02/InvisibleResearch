# Current Artifact Role and Authority Inventory

This inventory resolves [Classify current artifacts by scholarly role and authority](https://github.com/YannJY02/InvisibleResearch/issues/46). It classified the pre-migration tree and now records the equivalent role after the Shared Workspace migration. See [`hybrid-workspace-migration.md`](hybrid-workspace-migration.md) for current commands.

## Decision

- `Writing Report/Slides/material/analyze.Rmd` has **Source Authority** for the latest researcher-supplied analysis. Its SHA-256 is `42395d4f28ddaf3d1f062d74d215e68fc93b691d47f2e6632943f976c65797b5`.
- That file is currently **Exploratory Analysis**, not a **Paper Analysis Candidate**: its declared data and shapefile paths do not exist in the repository, its R dependencies are unpinned, it makes a live WDI request, and its outputs do not have an executable dependency record.
- No current file is designated **Paper Analysis**. The repository contains no joint researcher-and-collaborator designation record.
- Tracked report files and ignored presentation files are **Generated Artifacts** or support material. Their location, filenames, and presence in Git do not give them scientific authority.
- The inventory shows one overlapping research effort, not multiple low-overlap projects. The ignored paper-facing material uses the same Invisible Communication Science domain and should remain in this repository's eventual publication layer.

## Classification rules

Each path receives one primary role based on its current evidence, not its intended future directory. Source Authority answers which duplicate source to preserve; Paper Analysis status answers whether results may support paper claims. These are separate decisions.

`Tracked` means present in Git. `Ignored` means excluded by the shared `.gitignore`. `Local-only` means excluded only by this checkout's `.git/info/exclude`, so collaborators cannot discover it from the repository.

## Tracked inventory

At classification time, the repository tracked 97 files. The role assignments below remain authoritative even where the migration changed paths.

| Paths | Primary role | Evidence and handling consequence |
|---|---|---|
| `src/invisible_research/acquisition/**`, `src/invisible_research/processing/**`, `src/invisible_research/validation/**`, `config/**`, `data/README.md`, `data/raw/sample_records_language_title_abstract.csv`, `requirements.txt`, `run_pipeline.sh`, `scripts/utils/**`, `tests/**` | Shared Workspace | Reusable configuration, sample input, acquisition/processing/validation code, runner, and checks. Owner commands resolve external artifacts through `DATA_ROOT`. |
| `docs/ARTICLEINFO_DATABASE.md`, `docs/DATA_SCRIPT_MAPPING.md`, `docs/README.md`, `docs/TableRelation.png` | Shared Workspace | Describe shared data schemas and transformations rather than a single claim. |
| Source `*.ipynb` files under `notebooks/**`, except `openalex_by_year_to_parquet.executed.ipynb`; `scripts/03_analysis/**` | Exploratory Analysis | They investigate acquisition, matching, variable construction, coverage, or validation. They have useful repeatable fragments, but no complete input/environment/output record and no collaborator designation. |
| `notebooks/02_extraction/openalex_by_year_to_parquet.executed.ipynb`, `outputs/reports/**` | Generated Artifact | The executed notebook captures a run. Ten report files name their generators in scripts/notebooks; `prestige_distribution.json` is likewise output data but has no explicit generator reference. These files are evidence about past runs, not authorized paper results. |
| `.cursor/**`, `.github/**`, `.gitignore`, `AGENTS.md`, `CITATION.cff`, `CONTEXT.md`, `README.md`, `notebooks/02_extraction/README.md`, `notebooks/03_analysis/README.md`, `scripts/05_validation/*.md`, `docs/agents/**`, `docs/PROJECT_ISSUES.md`, `docs/SECURITY_GUIDE.md`, `docs/academic-repository-structure-research.md`, `docs/issues/**`, `docs/unused-code-policy.md`, `utils.md` | Administrative or support material | Repository operation, governance, planning, citation, and developer documentation. They do not enter the data-to-claim chain. |
| `archive/**`, `archive.md`, `backup/**` | Archive | Explicit archive markers and superseded code copies; retain as history until the migration ticket decides retirement. |
| None | Paper Analysis Candidate | No tracked analysis meets the reproducibility gate defined in `CONTEXT.md`. |
| None | Paper Analysis | No tracked joint designation record exists. |

## Ignored and local-only inventory

There are no ordinary untracked files: every local-only file is covered by an ignore or exclude rule.

| Paths | Git surface | Primary role | Evidence and handling consequence |
|---|---|---|---|
| `Writing Report/Slides/material/analyze.Rmd` | Local-only | Exploratory Analysis with Source Authority | The map identifies it as content-identical to the latest researcher-supplied analysis. Preserve this exact source through migration, but do not promote it without reproducibility evidence and collaborator designation. |
| `Writing Report/Slides/material/consolidated.csv` | Local-only | Shared Workspace data input, unregistered | 2,583,327,244 bytes, 565,392 lines, SHA-256 `9361454fd9e9c6479181dd60d98d44038aa4b346bb74654f7750345db6f27ab2`. It is the only local file matching the analysis's apparent input, but the R Markdown requests `data/cs/dimensions_april2025/consolidated.csv`; no manifest connects the two. Keep outside Git and quarantine from authority until provenance is recorded. |
| `Writing Report/Slides/analyze_v2.Rmd` | Local-only | Archive | Differs from the source-authoritative file only by changing the CSV path to `here::here("consolidated.csv")`, which is also absent at that location. Treat as a superseded path experiment, not a second analysis. |
| `Writing Report/Slides/extract_stats.R` | Local-only | Exploratory Analysis | Reads an absolute `/Users/yann.jy/Downloads/...` path and produces presentation statistics; it is not independently reproducible. |
| `Writing Report/Slides/etmaal2026_presentation.Rmd`, `skeleton.Rmd`, `speaker_notes.md`, `backup_note.md`, theme/tutorial assets | Local-only | Administrative or support material / archive | Event-specific communication material built around the exploratory results. Preserve the editable sources as historical support, not as Paper Analysis. |
| `Writing Report/Slides/fig*.png`, `material/image*.png`, `etmaal2026_presentation.html`, `etmaal2026_presentation.pdf`, `etmaal2026_presentation_files/**`, `libs/**`, `material/output.md`, `material/*.pdf` | Local-only | Generated Artifact | Rendered or captured outputs. Each of the six `fig*.png` files is byte-identical to its corresponding `material/image*.png`; both PDFs are duplicated under `Writing Report/Support Doc/output/`. Keep at most one output copy per hash when migration executes. |
| `Writing Report/Report/generate_report.js`, `package.json`, `package-lock.json`, `draft/**`, `Internship Report.docx`; `Writing Report/Support Doc/activity_summary.md`, `template/**`, `chat history/**` | Local-only | Administrative or support material / archive | Internship/report production, templates, narrative notes, and a 26 MB chat screenshot. They are not analysis dependencies; privacy and retention should be checked before any publication-compendium copy. |
| `notebooks/02_extraction/data/processed/communication_works.parquet` | Ignored | Generated Artifact | A 16,000,495-byte output of the OpenAlex extraction notebook, SHA-256 `5aa1c22bbf51b59ca937a63ea25159bde79b3eeecefc4c8dd694c093df1118f5`. Keep external to Git and register provenance before reuse. |
| `logs/**` | Ignored | Generated Artifact | Two run logs mirror notebook execution and can be regenerated; they are diagnostic history, not result authority. |
| `.env`, `.vscode/**` | Ignored | Administrative or support material | Local secrets and editor settings. Keep `.env` local and never migrate its secret values; editor settings are optional. |
| `.venv/**`, `.venv_prestige/**`, `Writing Report/Report/node_modules/**` | Ignored/local-only | Deletion | Regenerable dependency installations: 18,263, 5,110, and 363 files respectively. Recreate from retained manifests after environment decisions instead of migrating these directories. |
| `.agent/**` | Ignored | Deletion | 2,092 files in a singular `.agent` bundle. No repository file references it, and the active project guidance uses `.agents/skills`; do not migrate this copy. |
| All `.DS_Store` files and `~$*.docx` Office lock files | Ignored/local-only | Deletion | Operating-system metadata and temporary lock files have no unique scholarly or operational content. |
| Duplicate image/PDF copies identified above | Local-only | Deletion | Exact SHA-256 duplicates add no evidence. Retain one chosen Generated Artifact only if a later compendium needs it. |

## Authority gaps that block promotion

The source-authoritative R Markdown cannot yet become a Paper Analysis Candidate because:

1. its declared `consolidated.csv` and `TM_WORLD_BORDERS_SIMPL-0.3.shp` paths are absent;
2. no manifest records the Dimensions extract's origin, retrieval/version, license, or checksum;
3. no R environment lockfile exists, while `pacman::p_load(...)` and WDI can change dependencies or network results;
4. only Figure 1 has an explicit `ggsave(...)`; the local images and presentation claims lack a complete executable output graph; and
5. no recorded verification run binds exact inputs, code revision, environment, tables, and figures.

Even after those gaps close, promotion would create a Paper Analysis Candidate only. Paper Analysis still requires the separate joint designation defined in `CONTEXT.md`.

## Inputs to later tickets

- Preserve `Writing Report/Slides/material/analyze.Rmd` by content hash as the source to migrate; archive `analyze_v2.Rmd` rather than merging authority by modification time.
- Treat `consolidated.csv` and `communication_works.parquet` as external bytes needing durable provenance, not as Git migration candidates.
- Do not split `Writing Report` into a separate repository: it is a paper-facing layer of the same research domain, while report templates, chat history, and internship administration remain support/archive material.
- Migration can delete regenerated environments, dependency trees, OS metadata, Office locks, and exact duplicate outputs after retained manifests and chosen source/output copies are verified.
