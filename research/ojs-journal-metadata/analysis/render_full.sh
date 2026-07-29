#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
artifact_dir="$analysis_dir/../artifacts/ojs_journal_enrichment"
render_source_dir="$artifact_dir/render-source-full"

mkdir -p "$render_source_dir"
cp "$analysis_dir/ojs_journal_enrichment.qmd" "$render_source_dir/"
cd "$render_source_dir"
OJS_ENRICHMENT_MODE=full quarto render ojs_journal_enrichment.qmd \
  --execute-dir "$analysis_dir" \
  --output-dir ../rendered-full

test -f "$artifact_dir/full-v7/run-metadata.json"
test -f "$artifact_dir/full-v7/pkp-ojs-multisource-enriched.parquet"
test -f "$artifact_dir/full-v7/openalex-sources.parquet"
test -f "$artifact_dir/full-v7/crossref-journals.parquet"
test -f "$artifact_dir/full-v7/pkp-openalex-disagreement-audit.csv"
test -f "$artifact_dir/full-v7/pkp-openalex-disagreement-summary.csv"
grep -q '"run_mode": "full"' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"rows": 98273' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"format": "parquet"' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"rows_per_page": 1000' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"failed_pages": 0' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"disagreement_audit"' "$artifact_dir/full-v7/run-metadata.json"
grep -q '^dimension,category,denominator_name,denominator,count,percent$' \
  "$artifact_dir/full-v7/pkp-openalex-disagreement-summary.csv"
grep -q '^identity_outcome,consistent,all_pkp_v7_rows,98273,' \
  "$artifact_dir/full-v7/pkp-openalex-disagreement-summary.csv"
grep -q '^source_status_crosstab,openalex=' \
  "$artifact_dir/full-v7/pkp-openalex-disagreement-summary.csv"
