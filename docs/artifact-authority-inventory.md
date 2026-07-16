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
| `src/invisible_research/acquisition/**`, `src/invisible_research/processing/**`, `src/invisible_research/validation/**`, `.env.example`, `data/README.md`, `data/raw/sample_records_language_title_abstract.csv`, `requirements.txt`, `tests/**` | Shared Workspace | Reusable configuration, sample input, acquisition/processing/validation code, and checks. Direct module commands resolve external artifacts through `DATA_ROOT`. |
| `docs/ARTICLEINFO_DATABASE.md`, `docs/DATA_SCRIPT_MAPPING.md`, `docs/README.md`, `docs/TableRelation.png` | Shared Workspace | Describe shared data schemas and transformations rather than a single claim. |
| `research/**/README.md`, `research/**/analysis/**`, `research/**/notebooks/**` | Exploratory Analysis | Five named owners now contain the acquisition experiments, matching, variable construction, coverage, sampling, and validation work. Notebook code is retained in owner analysis commands and notebooks act as adapters. No owner has Paper Analysis authority. |
| `papers/invisible-communication-science/**` | Publication Compendium containing Exploratory Analysis | Contains the unchanged Source Authority, active slide source and theme assets, external-input verification, environment gaps, ignored legacy figures, and a governance boundary. It contains no Candidate Version or Designation Event. |
| `data/artifact-versions/**` | Shared Workspace | Four-field content-identity records reference large external inputs through portable `DATA_ROOT` locations; no large data bytes enter Git. |
| Removed tracked executed notebooks, root outputs, phase-numbered scripts, root command wrapper, obsolete config, and backup code | Generated Artifact / superseded support material | These retired forms left the active tree during owner migration and final contraction. Git history retains their exact tracked content. New regenerable reports are written to ignored owner-local `artifacts/` directories. |
| `.github/**`, `.gitignore`, `AGENTS.md`, `CITATION.cff`, `CONTEXT.md`, `README.md`, `research/README.md`, `docs/agents/**`, `docs/SECURITY_GUIDE.md`, `docs/academic-repository-structure-research.md`, `docs/issues/**`, `docs/unused-code-policy.md`, `utils.md`, `archive.md` | Administrative or support material | [GitHub Issues](agents/issue-tracker.md) is the current tracker authority. The listed paths support repository operation, governance, planning, citation, external-archive indexing, and developer documentation; they do not enter the data-to-claim chain. |
| None | Paper Analysis Candidate | No tracked analysis meets the reproducibility gate defined in `CONTEXT.md`. |
| None | Paper Analysis | No tracked joint designation record exists. |

## Post-cutover external and local-only inventory

| Paths | Git surface | Primary role | Evidence and handling consequence |
|---|---|---|---|
| `$DATA_ROOT/processed/dimensions_april2025_consolidated.csv` | External Google Drive data, registered | Shared Workspace input | 2,583,327,244 bytes, SHA-256 `9361454fd9e9c6479181dd60d98d44038aa4b346bb74654f7750345db6f27ab2`; upstream provenance remains unresolved. |
| `$DATA_ROOT/derived/**` represented by `data/artifact-versions/**` | External Google Drive data, registered | Shared derived data or Generated Artifact | Direct hashes or tracked component manifests preserve content identity and upstream Artifact Version links. Registration grants no paper authority. |
| `GoogleDrive:InvisibleResearch/archive/writing-report-legacy/` | External archive | Archive | Unique inactive text sources were copied and SHA-256 verified during the Publication Compendium migration. |
| `GoogleDrive:InvisibleResearch/archive/writing-report-human-review/` | Private external archive | Administrative or support material | Seven owner-approved files were SHA-256 verified before the duplicate local workspace was removed; see `writing-report-human-review.md`. |
| `papers/invisible-communication-science/artifacts/**` | Ignored local artifacts | Generated Artifact | Selected legacy figures support the compendium but remain non-authoritative unless Candidate Version governance records their hashes. |
| `.env`, `.vscode/**` | Ignored local files | Administrative or support material | `.env` remains local and secret; editor settings are optional. |

The retired local workspace, dependency installations, root logs, local agent
bundle, duplicates, generated outputs, lock files, and OS metadata were removed
only after selected sources and both external archives passed their checks.

## Authority gaps that block promotion

The source-authoritative R Markdown cannot yet become a Paper Analysis Candidate because:

1. its declared relative `consolidated.csv` path does not resolve to the registered external location, and `TM_WORLD_BORDERS_SIMPL-0.3.shp` remains absent;
2. the Artifact Version records the Dimensions bytes and location, but its origin, retrieval/version, and license remain unknown;
3. no R environment lockfile exists, while `pacman::p_load(...)` and WDI can change dependencies or network results;
4. only Figure 1 has an explicit `ggsave(...)`; the local images and presentation claims lack a complete executable output graph; and
5. no recorded verification run binds exact inputs, code revision, environment, tables, and figures.

Even after those gaps close, promotion would create a Paper Analysis Candidate only. Paper Analysis still requires the separate joint designation defined in `CONTEXT.md`.

## Final contraction outcome

- The Publication Compendium Source Authority, external CSV Artifact Version,
  legacy archive manifest, selected figures, and shared derived records passed
  their content checks.
- The owner approved private retention of the seven human-review files; every
  copy matched before the duplicate local workspace was removed.
- `communication_works.parquet` remains an external Generated Artifact with
  exact content identity but unresolved acquisition provenance.
