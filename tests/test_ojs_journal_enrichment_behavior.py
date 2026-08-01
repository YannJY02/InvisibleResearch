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
  "deduplicate_identical_candidates",
  "serialize_json",
  "dataframe_value",
  "expand_candidate_fields",
  "normalize_issn",
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
deduplicated <- deduplicate_identical_candidates(list(
  candidate,
  candidate,
  different_candidate
))
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


def test_validation_precedes_formal_artifact_promotion():
    qmd = QMD_PATH.read_text()

    validation = qmd.index("#| label: pre-promotion-validation")
    master_promotion = qmd.index(
        "file.rename(temporary_output_path, output_path)"
    )
    metadata_promotion = qmd.index(
        "file.rename(metadata_temporary_path, metadata_path)"
    )

    assert validation < master_promotion
    assert validation < metadata_promotion
