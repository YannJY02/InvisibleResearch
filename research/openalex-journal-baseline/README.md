# OpenAlex Journal Baseline

This owner builds an **Exploratory Analysis** of all journal-type OpenAlex
Sources. It is independent of the PKP/OJS starting cohort. The active input is
the user-selected January 2026 US dataset in `multiobs`; this remains Exploratory Analysis, not Paper Analysis.

- [Current BigQuery journal export](journal-export.md): merged CSV, missingness,
  connection verification, delivery evidence and the coming week's tasks.
- [Full table scope and join routes](table-scope.md): September 25 audit of all
  76 tables, existing CSV coverage, actual topic-path example and proposed additions.
- [Earlier Crossref supervisor report](../ojs-journal-metadata/analysis/crossref-meeting-report.qmd):
  R-executed field comparison, additional records, missing subjects and query test.
- [Earlier technical record](premeeting-report.md): access
  evidence, completed offline audit, candidate extraction, index matching,
  literature overview and outstanding dependencies; this broader record is not
  the September 15 presentation.
- [Input contract](input-contract.md): source identity, journal denominator,
  candidate versions, relational-table scope and missing-value rules.
- [January 2026 dataset comparison](dataset-comparison.md): 76-table EU/US
  metadata comparison, full-row fingerprints for 12 journal-related tables,
  11 verified existing clones, and the working cross-project query route.
- [September 15 meeting outcomes](../../meeting-reports/2026-09-15-openalex-table-delivery.md):
  combined journal CSV, per-column missingness, existing SURFdrive destination
  and supervisor-led commercial-index access follow-up.
- [BigQuery access record](../../docs/testing/bigquery-access.md) and
  [official MCP setup](../../docs/operations/bigquery-mcp.md).

## Reproduce the current merged journal CSV

The GoogleSQL performs the merge in BigQuery; Python only submits bounded jobs,
downloads paginated results and verifies the CSV. Choose a new output directory:

```sh
python3 research/openalex-journal-baseline/analysis/export_journal_table.py \
  --gcloud /Users/yann.jy/.local/google-cloud-sdk/bin/gcloud \
  --output research/openalex-journal-baseline/artifacts/journal-export-new-run
```

The [SQL](analysis/export_journal_table.sql) uses the current public US dataset,
21 core columns, 10 child-table JSON columns and an exact publisher association.
CSV uses `\N` for SQL NULL, empty cells for actual empty strings and `[]` for
no child rows. A complete `manifest.json` records audit jobs, counts and hashes.
Saved jobs are reused on retry; an uncertain POST is never automatically replayed.
Source jobs have a 512 MiB cap; auditing the larger JSON result has a separate
2 GiB cap. Every submitted query first passes a dry run.

## Historical September 14 core-table read

The following command documents the completed old `insyspo` candidate read;
it is not the active connection or current delivery.

Requires Python 3 standard library, Google Cloud CLI and an already authorized
Application Default Credentials identity. The reader invokes the official
BigQuery REST `tabledata.list` method; it creates no SQL query job. It requires
table metadata and data permissions and supports the inspected scalar schema.

From the repository root, choose a **new** output directory for each read:

```sh
python3 research/openalex-journal-baseline/analysis/read_bigquery_sources.py \
  --project insyspo --dataset publicdb_openalex_2025_08_rm \
  --output research/openalex-journal-baseline/artifacts/bigquery-tabledata-2025-08
```

The completed September 14 run already occupies that directory; the command
intentionally refuses to overwrite it. Retrieval failures retain `.partial` files. Completion requires a valid
`manifest.json` and matching output hashes, not final filenames alone; a failure
during finalization can leave renamed files without a complete manifest. There is no automatic credential refresh or
resume; a failed read requires inspection before a new run directory is used.

`sources.jsonl.gz` preserves all scalar fields and null/empty-string distinctions.
`journals.csv.gz` selects exact `type == "journal"`, retaining all 21 columns.
CSV represents null as an empty cell, so use JSONL for missingness audits.
`manifest.json` records source/journal counts, hashes, pagination and metadata
stability before and after reading. These checks do not establish transactionally
consistent snapshot isolation if the upstream table changes during a read.

## Match the official Scopus reference

The matching script and its actual command, reference version, row-preservation
checks and output semantics are described in the [report](premeeting-report.md).
It requires Python with `pandas` and `openpyxl`. Keep the downloaded workbook,
source-row candidates, labels and summaries under
`artifacts/scopus-2026-08/`. An absent exact match means absent from that supplied
reference, not proof of never having been indexed. Do not turn unavailable WoS
labels or missing ISSNs into negative outcomes.

## Verification and delivery

The report records actual runs and their limits. Generated inputs, outputs,
rendered HTML and delivery bundles stay in this owner's ignored `artifacts/`
subdirectories. A Git push publishes scripts and report prose, not those local
data files; SURFdrive delivery requires a known destination and remote readback.

Render the report and build the local portable bundle after those outputs exist:

```sh
python3 research/openalex-journal-baseline/analysis/render_premeeting_report.py
```

The **HTML report**（本地产物：`artifacts/premeeting-report/premeeting-report.html`） and
**report/data ZIP**（本地产物：`artifacts/premeeting-report/premeeting-report-and-data.zip`）
include local data and cited audit evidence. The original Scopus workbook and
PKP master are not included. All bundle members have a recorded SHA-256; the
renderer rewrites repository note links to GitHub and data links into the bundle.
