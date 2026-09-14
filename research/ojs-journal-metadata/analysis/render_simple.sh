#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
artifact_dir="$analysis_dir/../artifacts/ojs_journal_enrichment_simple_ver"
mkdir -p "$artifact_dir/rendered"
exec quarto render \
  "$analysis_dir/ojs_journal_enrichment_simple_ver/ojs_journal_enrichment_simple_ver.qmd" \
  --output-dir "$artifact_dir/rendered"
