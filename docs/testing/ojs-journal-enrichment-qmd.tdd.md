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

As a researcher starting from a clean checkout, I can run the documented sample
render once, acquire and verify PKP V7 inside the ignored owner artifact area,
and inspect a fixed ten-row exact-ISSN enrichment without `DATA_ROOT`.

### Task report

| Stage | Commit | Command | Evidence |
|---|---|---|---|
| RED | `e869248` | `quarto render ojs_journal_enrichment.qmd --output-dir ../artifacts/ojs_journal_enrichment/tdd-red` | Exit 1 at the intended contract boundary: `exists("pkp_version") is not TRUE`. |
| GREEN | `214d0d7` plus the final follow-up commit | `quarto render ojs_journal_enrichment.qmd --output-dir ../artifacts/ojs_journal_enrichment/rendered` | PASS: V7 input and source caches were reused, the contract passed, and the report was written under the ignored artifact directory. |
| Clean acquisition | final follow-up commit | The same render in a temporary clean clone with no artifacts | PASS: the download path acquired the checksum-verified 28.4 MB V7 file, first-run source caches reported `reused: false`, and the complete render passed. The control-flow run served the already checksum-verified official file locally because Harvard Dataverse throttled repeated verification downloads after the initial official acquisition. |
| Repository regression | final follow-up commit | `uv run --with pytest --with pandas --with pyarrow pytest` | 25 passed; two unrelated baseline failures remained. Both failures reproduce at starting commit `03e3b83`. |

### Test specification

| # | What is guaranteed | Test target | Type | Result |
|---|---|---|---|---|
| 1 | Missing V7 input is downloaded into the owner artifact directory and must match official MD5 `3a4ad8ae1ebfcc2b991aaf55b2d82c92` before use | Complete sample render, `packages-and-paths` | End to end | PASS |
| 2 | V7 has the pinned 19-column schema, 98,273 unique source rows, 72,084 valid-identifier rows, 26,189 literal-`NA` missing-identifier rows, and 103,017 distinct valid ISSNs | Complete sample render, `load-sample` | Contract | PASS |
| 3 | The fixed ten rows come directly from V7 and cover consistent, unmatched, partial-identifier, not-attempted, and inconsistent OpenAlex behavior | Complete sample render, `contract-check` | Integration | PASS |
| 4 | OpenAlex and Crossref use the shared normalization, exact matching, candidate deduplication, field expansion, and serialization functions | Complete sample render, `contract-check` | Integration | PASS |
| 5 | The master retains ten PKP rows, every discovered top-level source field, and lossless candidate JSON | Complete sample render, `contract-check` | Contract | PASS |
| 6 | Run metadata records R, Quarto, curl, and package versions without API-key or Crossref-contact fields | Complete sample render, `run-metadata.json` contract | Privacy | PASS |

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
