# OJS Enrichment Simplification Design

## Decision

Separate reusable data production from exploratory disagreement analysis.

The enrichment notebook produces one reusable wide master CSV with one pinned
PKP V7 row per output row. A separate analysis notebook reads that master and
performs the complete PKP–OpenAlex disagreement analysis. The analysis notebook
does not call OpenAlex or Crossref.

## Enrichment notebook

`research/ojs-journal-metadata/analysis/ojs_journal_enrichment.qmd` will:

- verify the pinned PKP V7 input and exact row identities;
- normalize checksum-valid ISSNs;
- retrieve OpenAlex and Crossref data with bounded retries, pacing, and
  resumable internal RDS checkpoints;
- preserve every PKP row and exact-ISSN match status;
- expand every returned top-level OpenAlex and Crossref field into the master,
  serializing nested or repeated values as lossless JSON cells;
- retain complete candidate records for ambiguous matches;
- write and reread one compressed wide master CSV before promotion; and
- render basic run counts plus the fixed searchable ten-row review.

The RDS caches and checkpoints are internal, ignored, and reproducible. They
are not formal data deliverables.

## Disagreement analysis notebook

`research/ojs-journal-metadata/analysis/ojs_journal_disagreement_analysis.qmd`
will read the validated wide master and preserve the existing exploratory
analysis:

- seven exact-ISSN identity outcomes;
- normalized title, ISSN-set, OJS, DOAJ, and country comparisons;
- explicit eligible denominators and source-status cross-tabulation;
- disagreement detail and summary tables; and
- the existing descriptive charts and review table.

Its outputs remain exploratory generated artifacts. The notebook reports
source-specific differences without treating either source as authoritative or
source absence as a causal measure of journal invisibility.

## Removed enrichment responsibilities

The enrichment notebook will no longer produce or validate:

- Parquet or NDJSON artifacts;
- OpenAlex or Crossref pointer catalogs;
- schema or validation manifests;
- a disagreement audit or disagreement summary;
- disagreement charts; or
- analysis-specific metadata.

## Validation

The retained public seam is a complete render plus artifact checks:

- sample render: ten source-authentic rows and complete wide source fields;
- full render: 98,273 unique PKP identities in one wide master CSV;
- analysis render: all identity and metadata summaries reconcile to the master;
- no API credentials or `admin_email` appear in outputs; and
- caches may be deleted and rebuilt without changing the formal output
  contract.
