# Current Artifact Role and Authority Inventory

This inventory resolves [Classify current artifacts by scholarly role and authority](https://github.com/YannJY02/InvisibleResearch/issues/46). It classified the pre-migration tree and now records the equivalent roles after the Shared Workspace, research-owner, and Publication Compendium migrations. See [`hybrid-workspace-migration.md`](hybrid-workspace-migration.md) for current commands.

## Decision

- `papers/invisible-communication-science/analysis/analyze.Rmd` has **Source Authority** for the latest researcher-supplied analysis. Its unchanged SHA-256 is `42395d4f28ddaf3d1f062d74d215e68fc93b691d47f2e6632943f976c65797b5`.
- That file is currently **Exploratory Analysis**, not a **Paper Analysis Candidate**: its declared data and shapefile paths do not exist in the repository, its R dependencies are unpinned, it makes a live WDI request, and its outputs do not have an executable dependency record.
- No current file is designated **Paper Analysis**. The repository contains no joint researcher-and-collaborator designation record.
- Tracked source files and ignored presentation figures remain **Exploratory Analysis**, **Generated Artifacts**, or support material. Their location, filenames, and presence in Git do not give them scientific authority.
- The inventory shows one overlapping research effort, not multiple low-overlap projects. Selected paper-facing material now resides in this repository's Invisible Communication Science Publication Compendium.

## Classification rules

Each path receives one primary role based on its current evidence, not its intended future directory. Source Authority answers which duplicate source to preserve; Paper Analysis status answers whether results may support paper claims. These are separate decisions.

`Tracked` means present in Git. `Ignored` means excluded by the shared `.gitignore`. `Local-only` means excluded only by this checkout's `.git/info/exclude`, so collaborators cannot discover it from the repository.

## Tracked inventory

At classification time, the repository tracked 97 files. The role assignments below remain authoritative even where the migration changed paths.

| Paths | Primary role | Evidence and handling consequence |
|---|---|---|
| `src/invisible_research/acquisition/**`, `src/invisible_research/processing/**`, `src/invisible_research/validation/**`, `config/**`, `data/README.md`, `data/raw/sample_records_language_title_abstract.csv`, `requirements.txt`, `run_pipeline.sh`, `scripts/utils/**`, `tests/**` | Shared Workspace | Reusable configuration, sample input, acquisition/processing/validation code, runner, and checks. Owner commands resolve external artifacts through `DATA_ROOT`. |
| `docs/ARTICLEINFO_DATABASE.md`, `docs/DATA_SCRIPT_MAPPING.md`, `docs/README.md`, `docs/TableRelation.png` | Shared Workspace | Describe shared data schemas and transformations rather than a single claim. |
| `research/**/README.md`, `research/**/analysis/**`, `research/**/notebooks/**` | Exploratory Analysis | Five named owners now contain the acquisition experiments, matching, variable construction, coverage, sampling, and validation work. Notebook code is retained in owner analysis commands and notebooks act as adapters. No owner has Paper Analysis authority. |
| `papers/invisible-communication-science/**` | Publication Compendium containing Exploratory Analysis | Contains the unchanged Source Authority, active slide source and theme assets, external-input verification, environment gaps, ignored legacy figures, and a governance boundary. It contains no Candidate Version or Designation Event. |
| `data/artifact-versions/**` | Shared Workspace | Four-field content-identity records reference large external inputs through portable `DATA_ROOT` locations; no large data bytes enter Git. |
| Removed tracked `openalex_by_year_to_parquet.executed.ipynb` and `outputs/reports/**` | Generated Artifact | These run products left the active tree in the owner migration; Git history retains them. New regenerable reports are written to ignored owner-local `artifacts/` directories. |
| `.cursor/**`, `.github/**`, `.gitignore`, `AGENTS.md`, `CITATION.cff`, `CONTEXT.md`, `README.md`, `research/README.md`, `scripts/05_validation/*.md`, `docs/agents/**`, `docs/PROJECT_ISSUES.md`, `docs/SECURITY_GUIDE.md`, `docs/academic-repository-structure-research.md`, `docs/issues/**`, `docs/unused-code-policy.md`, `utils.md` | Administrative or support material | Repository operation, governance, planning, citation, and developer documentation. They do not enter the data-to-claim chain. |
| `archive/**`, `archive.md`, `backup/**` | Archive | Explicit archive markers and superseded code copies; retain as history until the migration ticket decides retirement. |
| None | Paper Analysis Candidate | No tracked analysis meets the reproducibility gate defined in `CONTEXT.md`. |
| None | Paper Analysis | No tracked joint designation record exists. |

## Ignored and local-only inventory

There are no ordinary untracked files: every local-only file is covered by an ignore or exclude rule.

| Paths | Git surface | Primary role | Evidence and handling consequence |
|---|---|---|---|
| `Writing Report/Slides/material/analyze.Rmd` | Local-only original | Exploratory Analysis with Source Authority | Copied byte-for-byte to the Publication Compendium and verified at the recorded hash. The original remains untouched pending final contraction. |
| `$DATA_ROOT/processed/dimensions_april2025_consolidated.csv` | External Google Drive data | Shared Workspace data input, registered | 2,583,327,244 bytes, 565,392 lines, SHA-256 `9361454fd9e9c6479181dd60d98d44038aa4b346bb74654f7750345db6f27ab2`. The Artifact Version records its current location and the unresolved Dimensions provenance. The unchanged local original remains in `Writing Report` until final review. |
| `Writing Report/Slides/analyze_v2.Rmd` | Local-only original and verified external archive copy | Archive | Differs from the source-authoritative file only by changing the CSV path to `here::here("consolidated.csv")`, which is also absent at that location. The verified copy is under `GoogleDrive:InvisibleResearch/archive/writing-report-legacy/`. |
| `Writing Report/Slides/extract_stats.R` | Local-only | Exploratory Analysis | Reads an absolute `/Users/yann.jy/Downloads/...` path and produces presentation statistics; it is not independently reproducible. |
| `papers/invisible-communication-science/manuscript/etmaal2026_presentation.Rmd` and required theme assets | Tracked Publication Compendium | Administrative or support material | Active editable slide source migrated with figure references routed to ignored local artifacts. It remains based on exploratory results, not Paper Analysis. |
| `Writing Report/Slides/skeleton.Rmd`, `speaker_notes.md`, `backup_note.md`, tutorial and inactive report text sources | Local-only originals and verified external archive copies | Archive | Unique inactive text sources were copied to `GoogleDrive:InvisibleResearch/archive/writing-report-legacy/` and verified by SHA-256. Originals remain untouched. |
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

1. its declared relative `consolidated.csv` path does not resolve to the registered external location, and `TM_WORLD_BORDERS_SIMPL-0.3.shp` remains absent;
2. the Artifact Version records the Dimensions bytes and location, but its origin, retrieval/version, and license remain unknown;
3. no R environment lockfile exists, while `pacman::p_load(...)` and WDI can change dependencies or network results;
4. only Figure 1 has an explicit `ggsave(...)`; the local images and presentation claims lack a complete executable output graph; and
5. no recorded verification run binds exact inputs, code revision, environment, tables, and figures.

Even after those gaps close, promotion would create a Paper Analysis Candidate only. Paper Analysis still requires the separate joint designation defined in `CONTEXT.md`.

## Inputs to the final contraction ticket

- Re-verify the Publication Compendium Source Authority, external CSV Artifact Version, external archive manifest, and ignored figure copies before touching the local originals.
- Keep the administrative/private items in [`writing-report-human-review.md`](writing-report-human-review.md) until the user decides their retention or deletion.
- Retire `Writing Report/` only after that human review; directory migration has not authorized automatic deletion.
- `communication_works.parquet` remains an external Generated Artifact needing provenance before reuse.
