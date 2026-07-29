# OJS journal enrichment QMD: TDD evidence

Date: 2026-07-17

## Contract

The implementation follows the 2026-07-16 meeting outcome and the agreed
extension of `invisibleinfo/invisible-research#6` (OJS Journal Metadata). It
must:

1. start from source-authentic PKP/OJS rows;
2. match every valid ISSN against OpenAlex and Crossref;
3. verify whether multiple ISSNs resolve consistently;
4. retain all returned top-level source fields before presenting a selected
   review table;
5. preserve one output row per PKP/OJS row; and
6. use the same functions for a purposive 10-row validation sample and the
   complete pinned Beacon cohort.

The sample is deliberately non-representative. It validates the execution and
merge branches; it does not estimate full-cohort coverage.

## RED

Command:

Prerequisite: `OPENALEX_API_KEY` is set in the environment or the
repository-root `.env` file.

```sh
red_dir=$(mktemp -d)
quarto render research/ojs-journal-metadata/analysis/ojs_journal_enrichment.qmd \
  --output-dir "$red_dir"
```

Expected and observed failure before the fixture and implementation existed:

```text
file.exists(fixture_path) is not TRUE
```

Checkpoint commit: `51d0c4b` (`test(ojs): add multisource QMD RED contract`).

## GREEN

The same render command completed successfully after implementation. The
generated sample CSV contained 10 PKP/OJS rows and 89 columns. Its match states
covered:

- `consistent` in OpenAlex and Crossref;
- `unmatched` in OpenAlex and Crossref;
- `inconsistent` in OpenAlex; and
- `not_attempted` for a row without an ISSN.

The sample render reported no OpenAlex or Crossref API errors. The QMD's own
contract checks also verified one-row-per-input preservation, complete
candidate-record JSON for ambiguous matches, and the presence of every
discovered, namespaced top-level source field.

## Full-mode input check

The pinned PKP Beacon V6 file was read without calling either metadata API. Its
MD5 was `9f43fa051c7ed1cc45d8592593542011`, with 87,170 total rows and 86,282 OJS
rows. This validates the full-mode input path, checksum, cohort filter, and row
count contract.

The full API run was intentionally not executed. This V6 evidence is historical;
the explanatory QMD does not expose full mode.

## Issue #99: PKP V7 local reproduction

Source: [issue #99](https://github.com/YannJY02/InvisibleResearch/issues/99)
and parent PRD [#98](https://github.com/YannJY02/InvisibleResearch/issues/98).
No separate plan file was used.

### User journey

As a researcher starting from a clean checkout, I can run the documented
Journal Enrichment Sample render once, acquire and verify PKP V7 inside the
ignored owner artifact area, and inspect a fixed ten-row exact-ISSN enrichment
without `DATA_ROOT`.

### Task report

| Stage | Commit | Command | Evidence |
|---|---|---|---|
| RED | `e869248` | `quarto render ojs_journal_enrichment.qmd --output-dir ../artifacts/ojs_journal_enrichment/tdd-red` | Exit 1 at the intended contract boundary: `exists("pkp_version") is not TRUE`. |
| GREEN | `214d0d7` plus the final follow-up commit | `./render_sample.sh` | PASS: V7 input and source caches were reused, the contract passed, and the report was written under the ignored artifact directory without cleaning legacy generated files. |
| Clean acquisition | final follow-up commit | The same render in a temporary clean clone with no artifacts | PASS: the download path acquired the checksum-verified 28.4 MB V7 file, first-run source caches reported `reused: false`, and the complete render passed. The control-flow run served the already checksum-verified official file locally because Harvard Dataverse throttled repeated verification downloads after the initial official acquisition. |
| Repository regression | final follow-up commit | `uv run --with pytest --with pandas --with pyarrow pytest` | 25 passed; two unrelated baseline failures remained. Both failures reproduce at starting commit `03e3b83`. |

### Test specification

| # | What is guaranteed | Test target | Type | Result |
|---|---|---|---|---|
| 1 | Missing V7 input is downloaded into the owner artifact directory and must match official MD5 `3a4ad8ae1ebfcc2b991aaf55b2d82c92` before use | Complete Journal Enrichment Sample render, `packages-and-paths` | End to end | PASS |
| 2 | V7 has the pinned 19-column schema, 98,273 unique source rows, 72,084 valid-identifier rows, 26,189 literal-`NA` missing-identifier rows, and 103,017 distinct valid ISSNs | Complete Journal Enrichment Sample render, `load-sample` | Contract | PASS |
| 3 | The fixed ten rows come directly from V7 and cover consistent, unmatched, partial-identifier, not-attempted, and inconsistent OpenAlex behavior | Complete Journal Enrichment Sample render, `contract-check` | Integration | PASS |
| 4 | OpenAlex and Crossref use the shared normalization, exact matching, candidate deduplication, field expansion, and serialization functions | Complete Journal Enrichment Sample render, `contract-check` | Integration | PASS |
| 5 | The master retains ten PKP rows, every discovered top-level source field, and lossless candidate JSON | Complete Journal Enrichment Sample render, `contract-check` | Contract | PASS |
| 6 | Run metadata records R, Quarto, curl, and package versions without API-key or Crossref-contact fields | Complete Journal Enrichment Sample render, `run-metadata.json` contract | Privacy | PASS |

### Coverage and known gaps

The agreed public seam is the complete QMD render, so no separate function-level
coverage framework was added. The resulting master has 10 rows and 115 columns.
The package-install branch was not forced because all required packages were
already installed; the setup chunk computes the missing set and passes only
that set to base `install.packages()`.

The repository failures are unchanged baseline debt:

- `test_all_exploratory_notebooks_have_named_owner_contracts` expects a
  `## Question` section that this owner already lacked at `03e3b83`.
- `test_publication_compendium_contains_only_selected_active_sources` has an
  allowlist that already excludes tracked literature notes at `03e3b83`.

If the checkpoint commits are later squashed, preserve this RED/GREEN summary
in the merge record.

## Issue #100: resumable V7 OpenAlex full cohort

Source: [issue #100](https://github.com/YannJY02/InvisibleResearch/issues/100)
and parent PRD [#98](https://github.com/YannJY02/InvisibleResearch/issues/98).
No separate plan file was used.

### User journey

As a researcher, I can explicitly start a resumable V7 OpenAlex run, preserve
all PKP identities and exact-ISSN outcomes, and inspect a compact Parquet master
whose candidate IDs resolve to complete checkpointed Source responses.

### Task report

| Stage | Commit | Command | Evidence |
|---|---|---|---|
| RED | `640497e` | `./render_full.sh` | The existing notebook rendered only sample mode, then the full contract exited 1 because `full-v7/run-metadata.json` did not exist. |
| Sample GREEN | `1da2cfe` | `./render_sample.sh` | PASS: the fixed ten-case OpenAlex/Crossref contract remained unchanged. |
| Full GREEN | `1da2cfe` | `./render_full.sh` | PASS: 1,031 V7 checkpoints were reused, both Parquet files passed row/schema checks, and the report rendered. |
| Python check | `1da2cfe` | `python3 -m py_compile analysis/ndjson_to_parquet.py` | PASS. |

### Test specification

| # | What is guaranteed | Test target | Type | Result |
|---|---|---|---|---|
| 1 | Normal sample rendering cannot activate full mode; full mode is a separate command | `render_sample.sh`, `render_full.sh` | Contract | PASS |
| 2 | 103,017 valid ISSNs are split into 1,031 batches of at most 100 with 200-row cursor pages | Complete full render, `contract-check` | Integration | PASS |
| 3 | Every complete checkpoint is tied to PKP V7 MD5 and its exact ISSN batch and is safely reusable | Complete full render after interrupted acquisition | Recovery | PASS |
| 4 | API failures remain separate from unmatched rows and the qualified run has no unresolved failures | Full run metadata and `contract-check` | Contract | PASS |
| 5 | Reading the final Parquet files back yields the exact pinned set of 98,273 PKP identities, reconciled status counts, 54,520 unique Source IDs, and the exact Source-to-checkpoint mapping | PyArrow post-write validator and `contract-check` | Contract | PASS |
| 6 | Complete Source responses remain in V7 checkpoints and the catalog indexes every Source ID to one checkpoint while recording all 37 observed top-level fields | Source catalog, schema manifest, and `contract-check` | Reconciliation | PASS |
| 7 | Credentials and contact configuration are absent from metadata and generated columns | Complete full render, `contract-check` | Privacy | PASS |

### Full-run evidence and resource adjustment

The qualified run produced a 98,273-row, 25-column master Parquet file
(7.8 MB) and a 54,520-row Source-to-checkpoint catalog (293 KB). Statuses
reconciled to 54,286 consistent, 221 inconsistent, 17,577 unmatched, and
26,189 not attempted.

An initial wide-CSV design was stopped after real execution showed excessive
CPU, memory, and repeated JSON serialization. The approved Parquet adjustment
keeps candidate IDs in the master and complete Source responses in their V7
checkpoints instead of duplicating large JSON per PKP row. Temporary NDJSON
staging files are removed only after PyArrow verifies Parquet row counts and
schemas.

## Issue #101: resumable Crossref journal directory

Source: [issue #101](https://github.com/YannJY02/InvisibleResearch/issues/101)
and parent PRD [#98](https://github.com/YannJY02/InvisibleResearch/issues/98).
No separate plan file was used. The user-approved resource adjustment extends
the compact Parquet master and checkpoint catalogs instead of restoring a wide
CSV with repeated source JSON.

### User journey

As a researcher, I can provide a Crossref contact email only to the full-run
process, resume a polite complete-directory retrieval, and inspect exact-ISSN
Crossref outcomes whose candidate keys resolve to lossless page checkpoints.

### Task report

| Stage | Commit | Command | Evidence |
|---|---|---|---|
| RED | `f3684f9` | `CROSSREF_MAILTO=... ./render_full.sh` | The #100 notebook completed its full render, then the new contract exited 1 because the multisource master and Crossref catalog did not exist. |
| Missing-contact check | `8a544c9` | `env -u CROSSREF_MAILTO ./render_full.sh` | Exit 1 in `packages-and-paths`: full mode required a contact email before retrieval. |
| Sample GREEN | `8a544c9` | `./render_sample.sh` | PASS: the fixed ten-case sample rendered with no full-mode contact requirement. |
| Full GREEN | `8a544c9` | `CROSSREF_MAILTO=... ./render_full.sh` | PASS: 169 Crossref pages and all 1,031 OpenAlex batches were reused, three Parquet files reconciled, and the HTML report rendered. |
| Review fix | `e283b37` | `CROSSREF_MAILTO=... ./render_full.sh` | PASS: pagination stayed bounded by `total-results`; every Crossref pointer and checkpoint key reconciled in R; Python independently rebuilt and matched every master candidate set. |
| Syntax | `8a544c9` | `python3 -m py_compile analysis/ndjson_to_parquet.py`; QMD code extraction plus R `parse()` | PASS. |
| Repository regression | `8a544c9` | `uv run --with pytest --with pandas --with pyarrow pytest` | 25 passed; the same two baseline failures recorded for #99 remained. |

### Test specification

| # | What is guaranteed | Test target | Type | Result |
|---|---|---|---|---|
| 1 | Full mode rejects a missing or malformed process contact before source retrieval | `packages-and-paths` and missing-contact render | Privacy/preflight | PASS |
| 2 | Crossref retrieval uses one sequential 1,000-row cursor stream with bounded retries, explicit failures, and a delay below the polite-pool limit | `perform_crossref_page`, `fetch_crossref_directory`, full metadata | Integration | PASS |
| 3 | Each completed page is saved atomically and reused by page index, cursor, page size, status, and item count | Interrupted first run plus complete rerun | Recovery | PASS |
| 4 | The short final page and the sum of all 169 page counts reconcile exactly to Crossref `total-results` 168,654 | Full render `contract-check` | Pagination | PASS |
| 5 | Checksum-valid normalized ISSNs are matched locally; 137,473 unique ISSN sets remain in the catalog and distinct sets remain distinct candidates | Crossref catalog and full render `contract-check` | Identity | PASS |
| 6 | The 98,273-row master preserves all PKP identities and separate Crossref consistent, inconsistent, unmatched, and not-attempted states | PyArrow validator and `contract-check` | Contract | PASS |
| 7 | Candidate keys in the master resolve to a checkpoint file and record index while all 11 observed top-level fields remain in lossless checkpoints | Crossref catalog/schema and PyArrow validator | Reconciliation | PASS |
| 8 | The configured contact does not appear in metadata, checkpoints, or any Parquet artifact | Full artifact byte scan and metadata contract | Privacy | PASS |

### Coverage and known gaps

The agreed executable seam is the complete QMD render, so no separate
line-coverage framework was added. The qualified master has 98,273 rows and 30
columns (9.3 MB); the Crossref catalog has 137,473 rows and three pointer
columns (1.0 MB). Crossref statuses reconcile to 52,656 consistent, 374
inconsistent, 19,054 unmatched, and 26,189 not attempted rows.

The two repository-suite failures remain unchanged baseline debt: the owner
README already lacked `## Question`, and the publication-compendium allowlist
already excluded tracked literature notes before #101.

## Issue #102: PKP–OpenAlex disagreement audit

Source: [issue #102](https://github.com/YannJY02/InvisibleResearch/issues/102)
and parent PRD [#98](https://github.com/YannJY02/InvisibleResearch/issues/98).
No separate plan file was used. The user-approved resource adjustment remains
authoritative: compact Parquet master and source/checkpoint catalogs are the
fact layer; the audit CSV does not duplicate long source JSON.

### User journey

As a researcher, I can render the fixed V7 sample or complete 98,273-row
cohort, inspect denominator-explicit identity and metadata disagreements, trace
every aggregate to a compact audit row, and review three descriptive visuals
and the fixed ten-row interactive table without changing the evidence or
authority boundaries.

### Task report

| Stage | Commit | Command | Evidence |
|---|---|---|---|
| RED | `4c57e54` | `CROSSREF_MAILTO=... ./render_full.sh` | The existing QMD and #101 artifacts passed, then the shell contract exited 1 because `pkp-openalex-disagreement-audit.csv` did not exist. |
| Sample GREEN | `ba66fb4` | `./render_sample.sh` | PASS: the ten fixed rows reconciled to six consistent, one partial-agreement, one conflicting-ID, one unmatched, and one no-valid-ISSN outcome; all report widgets rendered. |
| Full GREEN | `ba66fb4` | `CROSSREF_MAILTO=... ./render_full.sh` | PASS: all 98,273 rows reconciled, all 1,031 OpenAlex batches and 169 Crossref pages were reused, zero API failures remained, and the complete report rendered. |
| Independent CSV check | `ba66fb4` | Python `csv`/`Counter` reconciliation of the generated audit and summary | PASS: identity, five metadata dimensions, the source-status cross-tab, and 98,273 unique PKP identities matched independently. |
| Syntax | `ba66fb4` | QMD code extraction plus R `parse()`; `sh -n`; `python3 -m py_compile analysis/ndjson_to_parquet.py` | PASS. |
| Repository regression | `ba66fb4` | `uv run --with pytest --with pandas --with pyarrow pytest` | 25 passed; the same two pre-existing failures recorded for #101 remained. |
| Dual review | `58c966a...ba66fb4` | Parallel Standards and Spec reviews | PASS on both axes with zero findings. |

### Test specification

| # | What is guaranteed | Test target | Type | Result |
|---|---|---|---|---|
| 1 | Every PKP row has exactly one of seven identity outcomes, including zero-count API error, and identity counts sum to the mode's cohort | Complete render, `contract-check`, and summary CSV | Classification | PASS |
| 2 | Title, ISSN-set, OJS, DOAJ, and country comparisons each use the same 54,153-row identity-matched OpenAlex-journal denominator in the full run | Full render and summary reconciliation | Denominator | PASS |
| 3 | DOAJ and country fields retain source-specific caveats; absent evidence is not converted into a negative assertion | Report prose, audit vocabulary, and metadata chart | Evidence boundary | PASS |
| 4 | The compact audit preserves all 98,273 PKP identities, excludes long JSON and `admin_email`, and independently reconciles to the summary | Full audit CSV and independent CSV check | Auditability/privacy | PASS |
| 5 | OpenAlex and Crossref states remain separate in a complete cross-tab whose counts sum to all 98,273 rows | Summary CSV, heatmap, and `contract-check` | Reconciliation | PASS |
| 6 | The report includes count/percentage identity and metadata bar charts, a count/percentage heatmap, and the fixed searchable, filterable, paginated, horizontally scrollable ten-row table | Complete sample and full renders | End to end | PASS |
| 7 | Input, master, catalogs, audit, and summary checksums; retrieval windows; cache/retry summaries; and runtime/package versions are recorded without API keys or process contact configuration | `run-metadata.json` and `contract-check` | Provenance/privacy | PASS |
| 8 | Complete source objects remain in lossless checkpoints and resolve through compact catalogs instead of being repeated in the master or audit CSV | Full artifact contract and dual review | Resource/audit design | PASS |

### Full-run evidence and known gaps

The qualified full audit has 98,273 rows, 31 compact columns, and no long JSON.
It records 53,615 consistent identities, 538 partial ISSN agreements, 221
conflicting Source-ID cases, 133 non-journal Sources, 17,577 valid-ISSN
unmatched rows, 26,189 rows without a valid ISSN, and zero API errors. The
54-row summary records explicit denominators and occupies less than 5 KB; the
audit CSV is approximately 40.4 MB.

The agreed public seam remains the complete notebook render, so no separate
line-coverage framework was added. The repository suite still has the same two
baseline failures: this owner lacked `## Question` before #102, and the
publication-compendium allowlist already excluded tracked literature notes.
These unrelated governance changes remain outside #102.
