import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
QMD_PATH = (
    PROJECT_ROOT
    / "research"
    / "ojs-journal-metadata"
    / "analysis"
    / "ojs_journal_enrichment.qmd"
)


def run_r_contract(contract: str) -> None:
    bootstrap = r'''
qmd_path <- Sys.getenv("OJS_ENRICHMENT_QMD")
purl_path <- tempfile(fileext = ".R")
on.exit(unlink(purl_path), add = TRUE)
knitr::purl(qmd_path, output = purl_path, quiet = TRUE)

library(dplyr)
library(purrr)
library(tibble)

wanted <- c(
  "classify_status",
  "deduplicate_candidates",
  "serialize_json",
  "dataframe_value",
  "expand_candidate_fields",
  "fetch_crossref_directory",
  "fetch_openalex_batch",
  "normalize_issn",
  "normalize_issn_set",
  "promote_artifact_pair",
  "read_rds_or_null",
  "save_rds_atomic",
  "source_issns"
)
for (expression in parse(file = purl_path)) {
  if (
    is.call(expression) &&
      identical(as.character(expression[[1]]), "<-") &&
      is.symbol(expression[[2]]) &&
      as.character(expression[[2]]) %in% wanted
  ) {
    eval(expression, envir = .GlobalEnv)
  }
}
'''
    environment = os.environ.copy()
    environment["OJS_ENRICHMENT_QMD"] = str(QMD_PATH)
    result = subprocess.run(
        ["Rscript", "-e", bootstrap + contract],
        cwd=QMD_PATH.parent,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_matching_helpers_preserve_mechanical_candidate_states():
    run_r_contract(
        r'''
stopifnot(
  classify_status(character(), character()) == "not_attempted",
  classify_status("2307-4108", character()) == "unmatched",
  classify_status("2307-4108", "candidate-1") == "unique",
  classify_status(
    "2307-4108",
    c("candidate-1", "candidate-2")
  ) == "ambiguous"
)

candidate <- list(
  title = "Same journal",
  ISSN = list("2307-4108", "2307-4116")
)
different_candidate <- list(
  title = "Different journal",
  ISSN = list("2307-4108")
)
deduplicated <- deduplicate_candidates(
  list(candidate, candidate, different_candidate),
  serialize_json
)$candidates
stopifnot(
  length(deduplicated) == 2L,
  identical(dataframe_value(list()), "[]")
)

matches <- list(list(
  candidates = list(
    list(id = "candidate-1"),
    list(id = "candidate-2")
  )
))
expanded <- expand_candidate_fields(matches, "source", "id")
stopifnot(
  is.na(expanded$source_id[[1]]),
  length(jsonlite::fromJSON(
    expanded$source_candidates__json[[1]],
    simplifyVector = FALSE
  )) == 2L
)

source <- list(
  issn = list("2307-4108"),
  issn_l = "2307-4116"
)
stopifnot(identical(source_issns(source), "2307-4108"))
'''
    )


def test_rds_cache_reader_handles_missing_corrupt_and_valid_files():
    run_r_contract(
        r'''
path <- tempfile()
on.exit(unlink(path), add = TRUE)
stopifnot(is.null(read_rds_or_null(path)))
writeLines("not an RDS file", path)
stopifnot(is.null(read_rds_or_null(path)))
saveRDS(list(valid = TRUE), path)
stopifnot(isTRUE(read_rds_or_null(path)$valid))
'''
    )


def test_minimal_pagination_reconciles_source_results():
    run_r_contract(
        r'''
openalex_calls <- 0L
fetch_openalex_page <- function(issns, cursor) {
  openalex_calls <<- openalex_calls + 1L
  if (openalex_calls == 1L) {
    return(list(
      results = list(list(id = "source-1")),
      meta = list(count = 2L, next_cursor = "next")
    ))
  }
  list(
    results = list(list(id = "source-2")),
    meta = list(count = 2L, next_cursor = NULL)
  )
}
stopifnot(
  length(fetch_openalex_batch("2307-4108")) == 2L,
  openalex_calls == 2L
)

crossref_mailto <- "researcher@example.org"
crossref_page_dir <- tempfile()
dir.create(crossref_page_dir)
on.exit(unlink(crossref_page_dir, recursive = TRUE), add = TRUE)
crossref_calls <- 0L
fetch_crossref_page <- function(cursor, mailto) {
  crossref_calls <<- crossref_calls + 1L
  if (crossref_calls == 1L) {
    return(list(
      items = replicate(1000L, list(ISSN = list("2307-4108")), simplify = FALSE),
      `total-results` = 1001L,
      `next-cursor` = "next"
    ))
  }
  stop("throttled")
}
stopifnot(
  inherits(try(fetch_crossref_directory(), silent = TRUE), "try-error"),
  crossref_calls == 2L
)

crossref_calls <- 0L
fetch_crossref_page <- function(cursor, mailto) {
  crossref_calls <<- crossref_calls + 1L
  list(
    items = list(list(ISSN = list("2307-4116"))),
    `total-results` = 1001L,
    `next-cursor` = NULL
  )
}
directory <- fetch_crossref_directory()
stopifnot(
  length(directory$journals) == 1001L,
  directory$total_results == 1001L,
  crossref_calls == 1L
)

unlink(crossref_page_dir, recursive = TRUE)
dir.create(crossref_page_dir)
crossref_calls <- 0L
repeated_page <- replicate(
  1000L,
  list(ISSN = list("2307-4108")),
  simplify = FALSE
)
fetch_crossref_page <- function(cursor, mailto) {
  crossref_calls <<- crossref_calls + 1L
  list(
    items = repeated_page,
    `total-results` = 3000L,
    `next-cursor` = "same"
  )
}
stopifnot(inherits(try(fetch_crossref_directory(), silent = TRUE), "try-error"))
'''
    )


def test_validation_precedes_formal_artifact_promotion():
    qmd = QMD_PATH.read_text()

    validation = qmd.index("#| label: pre-promotion-validation")
    promotion = qmd.index(
        "promote_artifact_pair(\n"
        "  c(temporary_output_path, metadata_temporary_path)"
    )

    assert validation < promotion


def test_artifact_pair_promotion_restores_previous_outputs():
    run_r_contract(
        r'''
directory <- tempfile()
dir.create(directory)
on.exit(unlink(directory, recursive = TRUE), add = TRUE)

temporary_master <- file.path(directory, "master.tmp")
missing_metadata <- file.path(directory, "missing-metadata.tmp")
master <- file.path(directory, "master.csv")
metadata <- file.path(directory, "metadata.json")
writeLines("new master", temporary_master)
writeLines("old master", master)
writeLines("old metadata", metadata)

result <- try(
  promote_artifact_pair(
    c(temporary_master, missing_metadata),
    c(master, metadata)
  ),
  silent = TRUE
)
stopifnot(
  inherits(result, "try-error"),
  readLines(master) == "old master",
  readLines(metadata) == "old metadata"
)
'''
    )
