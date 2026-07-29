# Issue 73: Strict OpenAlex coverage profile TDD evidence

## Source and journeys

- Source: GitHub issue [#73](https://github.com/YannJY02/InvisibleResearch/issues/73).
- As a research collaborator, I can inspect Strict OpenAlex Coverage across
  PKP-inferred country, observable activity, Beacon observation duration, and
  PKP-side DOAJ evidence without changing the 64,773-row Valid-ISSN OJS Cohort.
- As a maintainer, I can regenerate the profile from existing joined evidence,
  without OpenAlex requests, and verify the cohort, outcome, grouping, privacy,
  and Exploratory Analysis boundaries with `--check`.

The production implementation was already merged through child issues
[#74](https://github.com/YannJY02/InvisibleResearch/issues/74) and
[#75](https://github.com/YannJY02/InvisibleResearch/issues/75). This parent
verification reuses that accepted implementation instead of creating a second
pipeline.

## RED checkpoint

The existing joined CSV and coverage report were copied into this worktree's
ignored `research/ojs-journal-metadata/artifacts/enrich_openalex/` directory.
The joined CSV has MD5 `051937a2f0266ceaf5f78e3e3b96be21`.

| Stage | Command | Result |
|---|---|---|
| RED | `python3 research/ojs-journal-metadata/analysis/enrich_openalex.py --check` | Exit 1 at the intended output boundary: `FileNotFoundError: strict-openalex-coverage-profile-summary.json` |
| GREEN | `env -u OPENALEX_API_KEY python3 research/ojs-journal-metadata/analysis/enrich_openalex.py --profile` followed by the same `--check` command | PASS: `PKP–OpenAlex pipeline check passed`; generation recorded zero OpenAlex API requests |

No OpenAlex request was made. The joined CSV checksum remained unchanged after
generation.

## Test specification

| # | What is guaranteed | Test target | Result |
|---|---|---|---|
| 1 | Identifier Availability reconciles 86,282 OJS rows to 64,773 valid, 21,509 missing, and zero invalid ISSNs | `enrich_openalex.py --check` | PASS |
| 2 | The primary cohort reconciles to 49,877 unique, 190 ambiguous, and 14,706 unmatched exact-ISSN outcomes | `enrich_openalex.py --check` | PASS |
| 3 | Country, activity, Beacon duration, and PKP DOAJ dimensions each preserve all 64,773 cohort rows and outcome totals | `enrich_openalex.py --check` | PASS |
| 4 | The tidy output reports group denominators, all three outcome counts, Strict OpenAlex Coverage, and 95% Wilson intervals | `enrich_openalex.py --check` | PASS |
| 5 | The profile records zero OpenAlex requests, excludes `admin_email`, counts no title-only candidate, and remains Exploratory Analysis | `enrich_openalex.py --check` | PASS |

The generated summary reports Strict OpenAlex Coverage of 77.002763% over the
Valid-ISSN OJS Cohort, with a 95% Wilson interval of
76.677095%–77.325229%. It separately retains the accepted 57.807% figure over
all OJS rows for reconciliation with the existing coverage report.

## Final verification

- `black --check research/ojs-journal-metadata/analysis/enrich_openalex.py`:
  PASS.
- `flake8 --ignore=E203,E501,W503
  research/ojs-journal-metadata/analysis/enrich_openalex.py`: PASS.
- `python3 -m compileall -q src
  research/ojs-journal-metadata/analysis`: PASS.
- Profile generation followed by `--check`: PASS.
- Branch coverage across `--profile` and `--check`: 51% (272 of 482
  statements reached, with branch measurement enabled). The uncovered code is
  primarily the live acquisition path that this issue must not call.
- `uv run --with pytest --with pandas --with pyarrow pytest -q`: 25 passed,
  with two baseline failures in exploratory-owner and publication-compendium
  inventory tests. This branch changes only this evidence document, so it does
  not alter either failing contract.

The broader legacy `src/` tree is not Black- or Flake8-clean, while the
issue-owned analysis command passes both checks. No static typechecker is
configured; `compileall` is the available repository-wide syntax check.
Standards/Spec review remains pending.
