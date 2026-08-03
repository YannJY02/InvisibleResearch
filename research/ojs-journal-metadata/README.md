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
