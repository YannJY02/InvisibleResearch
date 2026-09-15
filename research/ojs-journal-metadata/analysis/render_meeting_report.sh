#!/bin/sh
set -eu

analysis_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
artifact_dir="$analysis_dir/../artifacts/crossref-meeting-report"
mkdir -p "$artifact_dir"
cp "$analysis_dir/crossref-meeting-report.qmd" \
  "$analysis_dir/crossref-meeting-report.css" \
  "$analysis_dir/crossref-field-notes.csv" "$artifact_dir/"
exec quarto render "$artifact_dir/crossref-meeting-report.qmd" \
  --execute-dir "$analysis_dir" "$@"
