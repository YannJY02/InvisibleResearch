script_arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
repo_root <- dirname(dirname(normalizePath(sub("^--file=", "", script_arg))))
qmd <- readLines(file.path(
  repo_root,
  "research",
  "ojs-journal-metadata",
  "analysis",
  "ojs_journal_enrichment.qmd"
))
start <- grep("#| label: packages-and-paths", qmd, fixed = TRUE) + 1L
end <- start - 2L + which(qmd[start:length(qmd)] == "```")[[1]]
setup <- qmd[start:end]

run_setup <- function(process_key = NULL, env_lines = "OTHER_SETTING=1") {
  inherited_env <- Sys.getenv()
  sandbox <- tempfile("ojs-env-check-")
  analysis_dir <- file.path(
    sandbox,
    "research",
    "ojs-journal-metadata",
    "analysis"
  )
  dir.create(analysis_dir, recursive = TRUE)
  writeLines(env_lines, file.path(sandbox, ".env"))
  old_wd <- setwd(analysis_dir)
  on.exit({
    setwd(old_wd)
    unlink(sandbox, recursive = TRUE)
    Sys.unsetenv(setdiff(names(Sys.getenv()), names(inherited_env)))
    do.call(Sys.setenv, as.list(inherited_env))
  })

  Sys.unsetenv(c("OPENALEX_API_KEY", "DOTENV_ONLY"))
  Sys.setenv(DATA_ROOT = "from-process")
  if (!is.null(process_key)) Sys.setenv(OPENALEX_API_KEY = process_key)
  error <- tryCatch(
    {
      suppressPackageStartupMessages(eval(
        parse(text = setup),
        envir = new.env(parent = globalenv())
      ))
      NULL
    },
    error = conditionMessage
  )
  list(
    error = error,
    key = Sys.getenv("OPENALEX_API_KEY"),
    data_root = Sys.getenv("DATA_ROOT"),
    dotenv_only = Sys.getenv("DOTENV_ONLY")
  )
}

fallback <- run_setup(env_lines = c(
  "OPENALEX_API_KEY=from-dot-env",
  "DATA_ROOT=from-dot-env",
  "DOTENV_ONLY=from-dot-env"
))
stopifnot(
  is.null(fallback$error),
  fallback$key == "from-dot-env",
  fallback$data_root == "from-process",
  fallback$dotenv_only == ""
)

exported <- run_setup(
  process_key = "from-process",
  env_lines = "OPENALEX_API_KEY=from-dot-env"
)
stopifnot(is.null(exported$error), exported$key == "from-process")

missing <- run_setup()
stopifnot(
  missing$error == "Set OPENALEX_API_KEY before running this notebook."
)

cat("PASS: .env fallback, process precedence, and missing-key guard\n")
