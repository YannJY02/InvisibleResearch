#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
artifact_dir="$analysis_dir/../artifacts/ojs_journal_enrichment"
render_source_dir="$artifact_dir/render-source-full"
export R_LIBS_USER="$artifact_dir/renv-library"

mkdir -p "$render_source_dir" "$R_LIBS_USER"
cp "$analysis_dir/ojs_journal_enrichment.qmd" "$render_source_dir/"
cd "$render_source_dir"
OJS_ENRICHMENT_MODE=full quarto render ojs_journal_enrichment.qmd \
  --execute-dir "$analysis_dir" \
  --output-dir ../rendered-full

test -f "$artifact_dir/full-v7/run-metadata.json"
test -f "$artifact_dir/full-v7/pkp-ojs-multisource-enriched.csv.gz"
gzip -t "$artifact_dir/full-v7/pkp-ojs-multisource-enriched.csv.gz"
grep -q '"run_mode": "full"' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"rows": 98273' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"format": "csv.gz"' "$artifact_dir/full-v7/run-metadata.json"
grep -q '"rows_per_page": 1000' "$artifact_dir/full-v7/run-metadata.json"
