#!/usr/bin/env Rscript
# Offline audit of one existing PKP V7 enrichment snapshot. No network calls.
# Run from the repository root: Rscript research/ojs-journal-metadata/analysis/premeeting_crossref_audit.R
suppressPackageStartupMessages({
  library(arrow)
  library(dplyr)
  library(jsonlite)
  library(readr)
  library(tibble)
})

owner <- "research/ojs-journal-metadata"
input_dir <- file.path(owner, "artifacts/ojs_journal_enrichment_simple_ver")
shared_dir <- file.path(owner, "artifacts/ojs_journal_enrichment/full-v7")
out <- file.path(owner, "artifacts/premeeting-crossref-audit")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
input_file <- file.path(input_dir, "pkp-ojs-multisource-enriched-simple_ver.parquet")
qmd <- file.path(owner, "analysis/ojs_journal_enrichment_simple_ver/ojs_journal_enrichment_simple_ver.qmd")
pkp_file <- file.path(input_dir, "input/beacon.csv")
cr_file <- file.path(shared_dir, "crossref-journals.rds")
stamp <- function(x) format(x, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
fingerprint <- function(path) {
  info <- file.info(path)
  tibble(path, bytes = info$size, mtime_utc = stamp(info$mtime),
         md5 = unname(tools::md5sum(path)),
         sha256 = digest::digest(file = path, algo = "sha256"))
}
message("Reading the saved full-cohort Parquet and verifying PKP row preservation.")
x <- read_parquet(input_file)
pkp <- read_csv(pkp_file, col_types = cols(.default = col_character()),
                na = character(), show_col_types = FALSE)
stopifnot(unname(tools::md5sum(pkp_file)) == "3a4ad8ae1ebfcc2b991aaf55b2d82c92",
          nrow(x) == nrow(pkp), !"admin_email" %in% names(x),
          all(vapply(names(pkp), function(n) identical(x[[n]], pkp[[n]]), logical(1))))
source_fields <- list()
cache_checks <- list()
source_keys <- list()
for (s in c("openalex", "crossref")) {
  path <- file.path(input_dir, paste0(s, "-expanded.rds"))
  z <- readRDS(path)
  data <- if (is.data.frame(z)) z else z$data
  source_keys[[s]] <- if (is.data.frame(z)) NA_character_ else z$source_key
  # R's cached vectors retain candidate-position names; Parquet does not encode
  # those vector names. Compare all cell values and types after removing names.
  matches <- vapply(names(data), function(n) identical(unname(x[[n]]), unname(data[[n]])), logical(1))
  stopifnot(nrow(data) == nrow(x), all(matches))
  source_fields[[s]] <- setdiff(names(data), paste0(s, "_candidates__json"))
  cache_checks[[s]] <- list(rows = nrow(data), columns = ncol(data),
                           identical_columns = sum(matches),
                           source_key_characters = if (is.data.frame(z)) 0L else nchar(z$source_key),
                           source_key_sha256 = if (is.data.frame(z)) NA_character_ else
                             digest::digest(z$source_key, algo = "sha256"),
                           comparison = "Exact cell values and types, excluding R vector names",
                           source_key_matches_raw_cache_md5 = if (s == "crossref")
                             identical(z$source_key, unname(tools::md5sum(cr_file))) else NA)
  rm(z, data)
}
message("Tabulating source match states and field-specific missing representations.")
valid <- x$identifier_status == "valid"
oa_unique <- x$openalex_match_status == "unique"
cr_unique <- x$crossref_match_status == "unique"
cr_only <- x$openalex_match_status == "unmatched" & cr_unique
stopifnot(all((x$openalex_match_status == "not_attempted") == !valid),
          all((x$crossref_match_status == "not_attempted") == !valid),
          identical(x$openalex_input_issns, x$crossref_input_issns))
for (s in c("openalex", "crossref")) {
  st <- x[[paste0(s, "_match_status")]]
  n <- x[[paste0(s, "_candidate_count")]]
  stopifnot(all(n[st %in% c("not_attempted", "unmatched")] == 0),
            all(n[st == "unique"] == 1), all(n[st == "ambiguous"] > 1))
}
status <- x |> count(openalex_match_status, crossref_match_status, name = "rows") |>
  mutate(pct_all_pkp_rows = 100 * rows / nrow(x),
         pct_valid_issn_rows = ifelse(openalex_match_status == "not_attempted", NA_real_,
                                      100 * rows / sum(valid)))
write_csv(status, file.path(out, "match-status-cross-tab.csv"))

empty_examples <- list()
audit <- lapply(names(x), function(n) {
  v <- x[[n]]
  source <- if (n %in% names(pkp)) "PKP V7 original" else if
    (n %in% source_fields$openalex) "OpenAlex top-level source field" else if
    (n %in% source_fields$crossref) "Crossref top-level source field" else "Derived match evidence"
  applicable <- if (n %in% source_fields$openalex) oa_unique else if
    (n %in% source_fields$crossref) cr_unique else if
    (n == "openalex_candidates__json") x$openalex_match_status == "ambiguous" else if
    (n == "crossref_candidates__json") x$crossref_match_status == "ambiguous" else rep(TRUE, nrow(x))
  states <- list(r_na = is.na(v),
    empty_string = if (is.character(v)) !is.na(v) & v == "" else rep(FALSE, length(v)),
    string_empty_array = if (is.character(v)) !is.na(v) & v == "[]" else rep(FALSE, length(v)),
    string_na = if (is.character(v)) !is.na(v) & v == "NA" else rep(FALSE, length(v)),
    string_null = if (is.character(v)) !is.na(v) & v == "null" else rep(FALSE, length(v)))
  for (kind in names(states)) {
    i <- which(states[[kind]])
    if (length(i)) {
      # Prefer a matched-row example when the field has its own source record.
      eligible <- i[applicable[i]]
      i <- if (length(eligible)) eligible[[1]] else i[[1]]
      empty_examples[[length(empty_examples) + 1L]] <<- tibble(
        field = n, representation = kind, pkp_row_number = i,
        context_name = x$context_name[[i]], issn = x$issn[[i]],
        openalex_match_status = x$openalex_match_status[[i]],
        crossref_match_status = x$crossref_match_status[[i]],
        raw_value = if (is.na(v[[i]])) "<R NA>" else as.character(v[[i]]))
    }
  }
  recommendation <- if (n == "openalex_country_code") {
    "Keep literal NA as Namibia's country code; only actual NA is missing."
  } else if (n == "crossref_subjects") {
    "Treat [] as no supplied subject for a derived subject-availability variable; preserve raw [] and distinguish unmatched/ambiguous."
  } else if (n %in% c("openalex_alternate_titles", "openalex_societies", "openalex_host_organization_lineage")) {
    "[] is an empty reported collection; use a separate availability flag, and never infer non-existence or failed matching."
  } else if (n %in% c("openalex_apc_prices", "openalex_apc_usd", "openalex_apc_usd_by_year")) {
    "Missing/empty APC evidence is unknown, not a zero fee; retain observed numeric zero."
  } else if (n %in% c("openalex_topics", "openalex_topic_share", "openalex_counts_by_year")) {
    "[] supplies no entries; preserve it and mark the derived classification/time series unavailable, not all-zero."
  } else if (grepl("candidates__json$", n)) {
    "NA is expected outside ambiguous matches; it is not absence of a source record."
  } else if (source == "PKP V7 original") {
    "Preserve raw strings; blank/NA sentinels need field-specific interpretation before derived recoding."
  } else if (source == "Derived match evidence") {
    "Interpret zero/blank from match status; do not treat not_attempted or ambiguous as unmatched."
  } else {
    "Distinguish unavailable record from missing field within unique matches; preserve numeric 0 and logical FALSE."
  }
  tibble(field = n, source, storage_class = paste(class(v), collapse = ";"),
    total_rows = length(v), applicable_rows = sum(applicable),
    r_na_all_rows = sum(states$r_na), r_na_applicable_rows = sum(states$r_na & applicable),
    pct_r_na_applicable = 100 * sum(states$r_na & applicable) / sum(applicable),
    empty_string_rows = sum(states$empty_string),
    string_empty_array_rows = sum(states$string_empty_array),
    string_na_rows = sum(states$string_na), string_null_rows = sum(states$string_null),
    numeric_zero_rows = if (is.numeric(v)) sum(v == 0, na.rm = TRUE) else NA_integer_,
    logical_false_rows = if (is.logical(v)) sum(!v, na.rm = TRUE) else NA_integer_,
    recommended_treatment = recommendation)
}) |> bind_rows()
write_csv(audit, file.path(out, "field-audit.csv"))
write_csv(bind_rows(empty_examples), file.path(out, "empty-value-examples.csv"))

# Parse each distinct saved JSON counts object once, then map back to PKP rows.
json_counts <- unique(x$crossref_counts[cr_unique])
parsed_counts <- lapply(json_counts, fromJSON)
doi_counts <- bind_rows(parsed_counts)
stopifnot(nrow(doi_counts) == length(json_counts), !anyNA(doi_counts),
          all(doi_counts$`current-dois` + doi_counts$`backfile-dois` == doi_counts$`total-dois`))
row_counts <- doi_counts[match(x$crossref_counts[cr_unique], json_counts), ]
period_zero <- colSums(row_counts == 0)
example_cols <- c("context_name", "issn", "oai_url", "repository_name", "set_spec",
                  "country", "identifier_status", "openalex_match_status", "openalex_candidate_count",
                  "crossref_match_status", "crossref_candidate_count", "crossref_candidate_issn_sets",
                  "crossref_title", "crossref_publisher", "crossref_counts")
examples <- x[cr_only, example_cols] |>
  mutate(pkp_row_number = which(cr_only),
         crossref_journal_url = paste0("https://api.crossref.org/journals/",
           vapply(strsplit(x$crossref_matched_issns[cr_only], "|", fixed = TRUE), `[`, character(1), 1L)))
# URLs are review locators only; no endpoint is queried by this audit.
write_csv(examples, file.path(out, "crossref-only-examples.csv"))
ambiguous_examples <- x[x$openalex_match_status == "ambiguous" & cr_unique,
                       c(example_cols, "openalex_candidate_ids")]
write_csv(ambiguous_examples, file.path(out, "crossref-with-ambiguous-openalex.csv"))

contribution <- tribble(
  ~field, ~incremental_use, ~interpretation_limit,
  "crossref_counts", "Priority: DOI deposit totals and current/backfile counts, separate from OpenAlex indexed works.", "Not journal article output, citations, or quality; periods follow the saved Crossref response.",
  "crossref_breakdowns", "Priority: DOI counts by issued year for deposit/output-history comparison.", "Issued year is not retrieval/deposit year; missing years are not automatically zero.",
  "crossref_coverage", "Priority if needed: availability of abstracts, references, ORCID, affiliation, funder, license and links in deposits.", "A zero is an observed value. If the associated DOI denominator is zero, a coverage rate needs a separate not-applicable flag.",
  "crossref_coverage-type", "Alternative to coverage: all/current/backfile nested views of deposit completeness.", "Overlaps coverage; select one documented representation for modeling instead of duplicate predictors.",
  "crossref_flags", "Optional: deposition-presence flags for infrastructure characterization.", "FALSE is observed; these are not quality assessments and may overlap coverage/count features.",
  "crossref_issn-type", "Identity audit: distinguish print/electronic ISSNs beyond OpenAlex's ISSN set.", "A typed ISSN is matching evidence, not a guarantee that a PKP row is correctly identified.",
  "crossref_ISSN", "Retain for reproducible Crossref identity linkage and disagreement checks.", "Overlaps OpenAlex ISSNs; preserve both source-specific values.",
  "crossref_title", "Retain for title disagreement and the seven Crossref-only rows.", "Usually overlaps OpenAlex display name; title similarity was not used to match.",
  "crossref_publisher", "Retain for publisher/host-organization disagreement and Crossref-only descriptions.", "Crossref publisher and OpenAlex host organization need not represent identical entities.",
  "crossref_subjects", "No classification information in this snapshot: every unique-match row has [].", "Treat as unavailable subject information, not evidence of no subject; do not fit an all-empty predictor.",
  "crossref_last-status-check-time", "Provenance: journal-summary status-check time.", "Not publication date, acquisition timestamp, or BigQuery snapshot version.")
stopifnot(setequal(contribution$field, source_fields$crossref))
write_csv(contribution, file.path(out, "crossref-field-contribution.csv"))

message("Recording source provenance and checking the raw empty-list example.")
cr <- readRDS(cr_file)
stopifnot(is.list(cr$journals), length(cr$journals) == cr$total_results)
first_example <- which(cr_only)[[1]]
example_issn <- x$crossref_matched_issns[[first_example]]
raw_pos <- which(vapply(cr$journals, function(j) example_issn %in% j$ISSN, logical(1)))
stopifnot(length(raw_pos) == 1L)
raw_journal <- cr$journals[[raw_pos]]
raw_empty_example <- list(
  pkp_row_number = first_example, input_issn = example_issn, crossref_title = raw_journal$title,
  raw_cache_record_number = raw_pos, raw_field = "subjects",
  raw_r_type = typeof(raw_journal$subjects), raw_r_class = class(raw_journal$subjects),
  raw_length = length(raw_journal$subjects),
  expanded_value = x$crossref_subjects[[first_example]],
  crossref_counts = raw_journal$counts)
stopifnot(is.list(raw_journal$subjects), length(raw_journal$subjects) == 0L,
          x$crossref_subjects[[first_example]] == "[]")
write_json(raw_empty_example, file.path(out, "raw-empty-list-example.json"), pretty = TRUE, auto_unbox = TRUE)
cr_provenance <- list(retrieved_at = cr$retrieved_at, total_results = cr$total_results,
                      actual_records = length(cr$journals))
rm(cr)

batches <- sort(list.files(file.path(shared_dir, "openalex-batches"), pattern = "\\.rds$", full.names = TRUE))
# The batch manifest fingerprints all files. Retrieval timestamps below are boundary samples,
# not a claim that every batch was downloaded within the same period.
batch_manifest <- bind_rows(lapply(batches, fingerprint))
cache_checks$openalex$source_key_matches_concatenated_batch_md5 <-
  identical(source_keys$openalex, paste(batch_manifest$md5, collapse = ""))
stopifnot(cache_checks$openalex$source_key_matches_concatenated_batch_md5,
          cache_checks$crossref$source_key_matches_raw_cache_md5)
write_csv(batch_manifest, file.path(out, "openalex-batch-manifest.csv"))
boundary_batches <- lapply(batches[c(1, length(batches))], function(path) {
  b <- readRDS(path)
  list(path = path, retrieved_at = b$retrieved_at, requested_issns = length(b$issns), source_records = length(b$sources))
})
provenance <- bind_rows(lapply(c(input_file, pkp_file, qmd, cr_file,
  file.path(input_dir, "openalex-expanded.rds"), file.path(input_dir, "crossref-expanded.rds"),
  file.path(shared_dir, "run-metadata.json")), fingerprint))
write_csv(provenance, file.path(out, "input-provenance.csv"))
stable_identity <- paste(x$oai_url, x$repository_name, x$set_spec, sep = "\r")
summary <- list(
  audit_time_utc = stamp(Sys.time()), scope = "Offline PKP V7 full-cohort enrichment; not an OpenAlex-wide or BigQuery snapshot audit",
  network_requests = 0L, rows = nrow(x), columns = ncol(x), pkp_original_columns = ncol(pkp),
  distinct_pkp_row_identities = length(unique(stable_identity)),
  field_groups = list(pkp = ncol(pkp), derived = ncol(x) - ncol(pkp) - sum(lengths(source_fields)),
                       openalex_top_level = length(source_fields$openalex), crossref_top_level = length(source_fields$crossref)),
  valid_issn_rows = sum(valid), no_valid_issn_rows = sum(!valid),
  identifier_status = x |> count(identifier_status, name = "rows"),
  openalex_status = x |> count(openalex_match_status, name = "rows"),
  crossref_status = x |> count(crossref_match_status, name = "rows"),
  cross_tab = status, crossref_only = list(rows = sum(cr_only),
    pct_all_pkp_rows = 100 * mean(cr_only), pct_valid_issn_rows = 100 * sum(cr_only) / sum(valid),
    pct_openalex_unmatched = 100 * sum(cr_only) / sum(x$openalex_match_status == "unmatched"),
    distinct_crossref_issn_sets = n_distinct(x$crossref_candidate_issn_sets[cr_only])),
  crossref_unique_with_openalex_ambiguous = sum(cr_unique & x$openalex_match_status == "ambiguous"),
  crossref_unique_with_openalex_not_attempted = sum(cr_unique & x$openalex_match_status == "not_attempted"),
  crossref_unique_rows = sum(cr_unique), crossref_subjects_empty_array_rows = sum(x$crossref_subjects == "[]", na.rm = TRUE),
  doi_count_zero_rows_among_crossref_unique = as.list(period_zero),
  expanded_cache_identity_checks = cache_checks, pkp_all_original_columns_identical = TRUE,
  crossref_acquisition = cr_provenance, openalex_batch_count = length(batches),
  openalex_retrieval_boundary_samples = boundary_batches,
  provenance_limit = "File mtimes are filesystem evidence, not acquisition dates. Cached API data are not the January 2026 BigQuery snapshot. Expanded cache values were compared exactly with all corresponding Parquet columns; the original retrieval/matching pipeline was not rerun.",
  runtime = list(R = R.version.string, arrow = as.character(packageVersion("arrow")), jsonlite = as.character(packageVersion("jsonlite"))))
write_json(summary, file.path(out, "summary.json"), pretty = TRUE, auto_unbox = TRUE, na = "null")

lines <- c(
  "# Offline Crossref contribution audit", "",
  sprintf("Generated %s from the existing full-cohort Parquet, with zero API calls.", summary$audit_time_utc), "",
  sprintf("The table has %s PKP V7 rows and %s columns: %s unchanged PKP columns, %s OpenAlex top-level fields, %s Crossref top-level fields, and %s derived evidence columns (including candidate JSON).", nrow(x), ncol(x), ncol(pkp), length(source_fields$openalex), length(source_fields$crossref), summary$field_groups$derived),
  "This is the PKP cohort with OpenAlex/Crossref enrichment; it does not complete the separately requested all-OpenAlex-journals baseline.", "",
  "## Matching result and denominators", "",
  sprintf("%s rows have a valid ISSN. %s have no valid ISSN and were not attempted in either source; they cannot be labelled unmatched.", sum(valid), sum(!valid)),
  sprintf("Crossref unique + OpenAlex unmatched: %s PKP rows (%.5f%% of all PKP rows; %.5f%% of valid-ISSN rows; %.5f%% of OpenAlex-unmatched rows). These are the strict Crossref-only cases in this saved lookup result, not proof of absence from every OpenAlex release.", sum(cr_only), 100 * mean(cr_only), 100 * sum(cr_only) / sum(valid), 100 * sum(cr_only) / sum(x$openalex_match_status == "unmatched")),
  sprintf("An additional %s Crossref-unique rows have ambiguous OpenAlex matches; OpenAlex has candidates for those rows, so they are not Crossref-only. No Crossref-unique row is OpenAlex not_attempted.", summary$crossref_unique_with_openalex_ambiguous),
  "All nonzero cells and both denominators are in match-status-cross-tab.csv. All seven strict cases have source ISSNs, titles, publishers, stable PKP locators and saved DOI counts in crossref-only-examples.csv.", "",
  "## Crossref's incremental information", "",
  "The observed Crossref source schema has 11 top-level fields, not 21. Counts, issued-year breakdowns and deposit-completeness metrics provide information distinct from OpenAlex indexed works. Typed ISSNs support identity checks; titles/publishers/ISSNs retain disagreement evidence. Coverage and coverage-type overlap, so both need not become model predictors. All original fields remain unchanged.",
  "Crossref DOI counts measure its registered/deposited records, not all journal articles or citations. Observed zeros and FALSE values remain data. When a current/backfile count is zero, the associated coverage number cannot support a period-specific completeness-rate interpretation without a denominator flag.",
  sprintf("Among %s Crossref-unique PKP rows, current-dois = 0 in %s, backfile-dois = 0 in %s and total-dois = 0 in %s. These are PKP-row counts and may repeat the same Crossref journal.", sum(cr_unique), period_zero[["current-dois"]], period_zero[["backfile-dois"]], period_zero[["total-dois"]]),
  "Field-by-field uses and limits are in crossref-field-contribution.csv.", "",
  "## Empty values", "",
  sprintf("Every Crossref-unique row (%s) contains the string [] in crossref_subjects. The raw directory record for ISSN %s has an actual empty R list; the expanded string preserves that empty array. See raw-empty-list-example.json.", sum(cr_unique), example_issn),
  "For a derived subject-availability variable this is no supplied classification. Keep the raw value and distinguish it from a missing source match. Empty APC data do not establish a free journal; empty topic lists do not establish zero topics; empty candidate JSON outside ambiguous matches is expected.",
  "Actual R NA, empty strings, literal NA and [] are counted separately for every column in field-audit.csv. openalex_country_code contains literal NA as the Namibia code: a blanket string-NA-to-missing operation would corrupt it. Concrete row-level examples are in empty-value-examples.csv.", "",
  "## Provenance and validation", "",
  "All 19 PKP source columns match the pinned V7 input exactly, and all 39 OpenAlex / 12 Crossref expanded-cache columns have exactly the same cell values and types as Parquet after removing R vector names. Both expanded-cache source keys match their original source-cache hashes. Candidate counts agree with the four match states; not_attempted agrees with no-valid-ISSN rows; parsed DOI current + backfile counts equal total counts.",
  sprintf("The Crossref cache records acquisition at %s and %s directory records. The OpenAlex manifest fingerprints %s cached batches; the summary reports retrieval timestamps sampled from the first and last batches only.", cr_provenance$retrieved_at, cr_provenance$actual_records, length(batches)),
  "input-provenance.csv records hashes, sizes and UTC mtimes. The QMD's current version is fingerprinted; its acquisition code was not run. Cache/file timestamps do not make these data the preferred January 2026 BigQuery snapshot, and no output from a different cohort was merged into the counts.", "",
  "Reproduce from repository root: Rscript research/ojs-journal-metadata/analysis/premeeting_crossref_audit.R"
)
writeLines(lines, file.path(out, "findings.md"))
message("Audit complete: ", out)
