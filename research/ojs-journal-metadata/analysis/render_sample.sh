#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
artifact_dir="$analysis_dir/../artifacts/ojs_journal_enrichment"
render_source_dir="$artifact_dir/render-source"
export R_LIBS_USER="$artifact_dir/renv-library"

mkdir -p "$render_source_dir" "$R_LIBS_USER"
cp "$analysis_dir/ojs_journal_enrichment.qmd" "$render_source_dir/"
cd "$render_source_dir"
exec env OJS_ENRICHMENT_MODE=sample quarto render ojs_journal_enrichment.qmd \
  --execute-dir "$analysis_dir" \
  --output-dir ../rendered
