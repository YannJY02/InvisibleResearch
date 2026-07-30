# OJS Journal Disagreement Analysis

Status: **Exploratory Analysis**.

## Question

What source-specific identity and metadata differences appear when the
validated PKP V7 journal master is compared with exact-ISSN OpenAlex and
Crossref evidence?

## Referenced inputs

- `research/ojs-journal-metadata/artifacts/ojs_journal_enrichment/full-v7/pkp-ojs-multisource-enriched.csv.gz`
- The R environment recorded by
  `research/ojs-journal-metadata/analysis/renv.lock`

The analysis reads the validated wide master only. It does not call either
metadata API.

## Run

First produce the full master, then render the offline analysis:

```bash
research/ojs-journal-metadata/analysis/render_full.sh
research/ojs-journal-disagreement-analysis/analysis/render_disagreement.sh
```

The second command reuses the enrichment owner's restored R library as a
read-only dependency and fails clearly if that environment is absent.
Generated audit, summary, and HTML files remain under the ignored
`research/ojs-journal-disagreement-analysis/artifacts/ojs_journal_disagreement_analysis/`
directory. Differences are descriptive source evidence, not proof that either
source is wrong.
