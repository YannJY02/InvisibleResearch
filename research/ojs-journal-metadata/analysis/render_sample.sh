#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
artifact_dir="$analysis_dir/../artifacts/ojs_journal_enrichment"
render_source_dir="$artifact_dir/render-source"

mkdir -p "$render_source_dir"
cp "$analysis_dir/ojs_journal_enrichment.qmd" "$render_source_dir/"
cd "$render_source_dir"
exec quarto render ojs_journal_enrichment.qmd \
  --execute-dir "$analysis_dir" \
  --output-dir ../rendered
