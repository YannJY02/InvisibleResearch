#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
enrichment_artifact_dir="$analysis_dir/../artifacts/ojs_journal_enrichment"
artifact_dir="$analysis_dir/../artifacts/ojs_journal_disagreement_analysis"
render_source_dir="$artifact_dir/render-source"
export R_LIBS_USER="$enrichment_artifact_dir/renv-library"

test -d "$R_LIBS_USER" || {
  echo "Restore the enrichment R environment before this analysis." >&2
  exit 1
}
mkdir -p "$render_source_dir"
cp "$analysis_dir/ojs_journal_disagreement_analysis.qmd" "$render_source_dir/"
cd "$render_source_dir"
quarto render ojs_journal_disagreement_analysis.qmd \
  --execute-dir "$analysis_dir" \
  --output-dir ../rendered

audit="$artifact_dir/pkp-openalex-disagreement-audit.csv.gz"
summary="$artifact_dir/pkp-openalex-disagreement-summary.csv"
test -f "$audit"
test -f "$summary"
gzip -t "$audit"
grep -q '^dimension,category,denominator_name,denominator,count,percent$' "$summary"
grep -q '^identity_outcome,consistent,all_pkp_v7_rows,98273,' "$summary"
grep -q '^source_status_crosstab,openalex=' "$summary"
