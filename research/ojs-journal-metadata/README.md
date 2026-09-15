# OJS Journal Metadata Enrichment

This owner investigates journal-level enrichment for PKP Beacon records. All
work here remains **Exploratory Analysis**.

## Question

How can exact ISSNs connect pinned PKP OJS records to OpenAlex Sources and
Crossref journals without dropping PKP identities?

## Referenced inputs

- PKP Beacon V7 Dataverse file `14084919`
- OpenAlex Sources
- Crossref journals

## Latest meeting follow-up

The [meeting record labelled 2026-09-14](../../meeting-reports/2026-09-14-openalex-baseline-and-access.md)
requests a review of Crossref's additional fields and rows with Crossref
information but none from OpenAlex, alongside resolution of BigQuery query
access. It provisionally favours a January 2026 snapshot and places Web of
Science/Scopus coverage comparison after that work. The report records the
owners, dependencies, and access/snapshot questions; it does not establish that
those follow-ups are complete. Its subsequent-source section records the user's
confirmed September 15 meeting at 16:00–16:30 China time and the upstream issue's
explicit journal-level baseline scope.

The [September 5 upstream direction](https://github.com/invisibleinfo/invisible-research/issues/5#issuecomment-5553748839)
calls for a new all-OpenAlex-journals baseline. Its snapshot, journal filter and
row contract are tracked separately in [Plane](../../docs/operations/project-management.md).
The implemented PKP/OJS workflow below retains its existing row-preservation
and exact-ISSN contract; its output does not complete the new baseline task.

## September 15 meeting report

Every creation, revision or re-rendering of a supervisor-facing report follows
the user's [research report requirements](../../docs/writing/research-report-requirements.md),
including the pre-delivery review. Use the agreed task, runnable code, results
and plain-language interpretation as the structure for each analysis section.

The [R/Quarto meeting report](analysis/crossref-meeting-report.qmd) follows four
immediate tasks: Crossref fields, additional matched records, empty subject
lists and a short BigQuery query test. Its field comparison retrieves and caches
Nature's complete Crossref journal and OpenAlex Source responses. Tasks 2 and 3
read the existing merged Parquet and Crossref cache. Results are calculated in R,
with the executed code available in the report.

```sh
sh research/ojs-journal-metadata/analysis/render_meeting_report.sh
```

The standalone HTML is written to
`artifacts/crossref-meeting-report/crossref-meeting-report.html`, with the query
response, seven-row example CSV and a compact run summary beside it. The `nature/`
subdirectory holds the two raw responses, retrieval time and expanded values.
R requires `arrow`, `dplyr`, `jsonlite`, `httr2`, `htmltools`, `knitr`, `rmarkdown`
and `digest`; the BigQuery
section invokes the existing authenticated `bq` CLI from R. Override its path
with `-P bq_cli:/path/to/bq` if needed. Rendering performs one constant query
with a one-byte billing cap. Nature's cached journal records are reused when
present; pass `-P refresh_nature:true` to fetch both again. No article records
or new full-cohort dataset are retrieved by this report.

The QMD expands every returned field on both sides into visible field paths,
with explanations and actual Nature values. Related fields come first; fields
without a direct counterpart follow, leaving the other source's cells blank.
Repeated lists retain expandable full values, and documented fields without a
Nature value are identified separately. R verifies the journal's title and
ISSNs agree and checks field coverage in both directions. The Nature responses
and the existing PKP merge are separate inputs; neither assumes a PKP merge
inside BigQuery.
The meeting report supersedes the broader technical report as the supervisor
presentation.

## Offline audit details

The [earlier technical record](../openalex-journal-baseline/premeeting-report.md)
records the September 14 offline audit of the existing 98,273 × 81 full-field
Parquet. Reproduce that audit without API calls from the repository root:

```sh
Rscript research/ojs-journal-metadata/analysis/premeeting_crossref_audit.R
```

Its outputs belong to `artifacts/premeeting-crossref-audit/`. This audits saved
August 3 API caches; it does not construct the separate OpenAlex-wide baseline.

## Environment

The analysis uses the package versions recorded in `analysis/renv.lock`. Restore
them once before rendering:

```bash
cd research/ojs-journal-metadata/analysis
Rscript -e 'install.packages("renv", repos="https://cloud.r-project.org")'
mkdir -p ../artifacts/ojs_journal_enrichment/renv-library
R_LIBS_USER=../artifacts/ojs_journal_enrichment/renv-library \
  Rscript -e 'renv::restore(lockfile="renv.lock", library=Sys.getenv("R_LIBS_USER"), prompt=FALSE)'
```

## Run

Render the fixed ten-row validation sample:

```bash
cd research/ojs-journal-metadata/analysis
OPENALEX_API_KEY=... ./render_sample.sh
```

Render all 98,273 PKP V7 rows:

```bash
cd research/ojs-journal-metadata/analysis
OPENALEX_API_KEY=... CROSSREF_MAILTO=you@example.org ./render_full.sh
```

The QMD downloads the PKP input when absent and verifies MD5
`3a4ad8ae1ebfcc2b991aaf55b2d82c92`. Sample mode selects ten fixed source rows.
Full mode sends the 103,017 distinct valid ISSNs to OpenAlex in groups of at
most 100 and retrieves the Crossref journal directory in 1,000-record cursor
pages. Completed OpenAlex groups and the completed Crossref directory are cached
under the ignored owner artifact directory so they can be reused.

Both modes normalize checksum-valid ISSNs, match only by exact ISSN, and retain
all PKP rows. The sample expands complete candidates for DT review. The full
master keeps candidate identities and match states compact; complete OpenAlex
and Crossref records remain in the ignored source caches.

The full deliverable is:

`artifacts/ojs_journal_enrichment/full-v7/pkp-ojs-multisource-enriched.csv.gz`

Before promotion, the QMD reads the temporary CSV back and compares every cell,
row identity, match state, and candidate set. The adjacent minimal
`run-metadata.json` records the input version/checksum and output checksum so a
downstream analysis can reject a mismatched master or OpenAlex checkpoint set;
it also records the R, Quarto, curl, and analysis-package versions. API
credentials and `admin_email` are not written to either artifact.

## Simple full-field Parquet version

The separate source in `analysis/ojs_journal_enrichment_simple_ver/` expands
the full source records into a Parquet master and a fixed ten-row sample.
Use its render entry point so the HTML also lands in its own artifact directory:

```bash
./research/ojs-journal-metadata/analysis/render_simple.sh
```

It uses the packages and source/cache requirements documented in that QMD.
The command executes the analysis and may retrieve missing source data; use it
when the task authorizes the corresponding run. Existing source caches are
reused as specified in the QMD. Its outputs and cache remain under
`artifacts/ojs_journal_enrichment_simple_ver/`, with HTML in `rendered/`.
A differing source-adjacent HTML export and its RPubs metadata were preserved
under `artifacts/ojs_journal_enrichment_simple_ver/source-adjacent-2026-09-14/`.
The prior `rendered/` report was retained unchanged; the reorganization did not
republish either export.

## Difference analysis

Run the separate offline comparison after a validated full master exists:

```bash
cd research/ojs-journal-metadata/analysis
./render_disagreement.sh
```

It makes no API requests. It writes the row-level disagreement audit and
category summary under `artifacts/ojs_journal_disagreement_analysis/` and
retains the title, ISSN, OJS, DOAJ, country, identity, and OpenAlex-by-Crossref
comparisons with their eligible denominators.

Deleting source caches causes the next run to retrieve a newer OpenAlex or
Crossref snapshot. Metadata differences are source-specific evidence, not proof
that either source is wrong. PKP country is inferred, absent DOAJ evidence is
not a negative assertion, and all results remain **Exploratory Analysis**.
