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

Prerequisite: `OPENALEX_API_KEY` is set in the environment.

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

The full API run was intentionally not executed. Full mode remains available
through `OJS_ENRICHMENT_MODE=full` and requires `DATA_ROOT`,
`OPENALEX_API_KEY`, and `CROSSREF_MAILTO`.
