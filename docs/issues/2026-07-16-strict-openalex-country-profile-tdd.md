# Issue 74 TDD evidence

## Source and journeys

The guarantees were derived from [issue #74](https://github.com/YannJY02/InvisibleResearch/issues/74) and its parent, issue #73; no separate plan file was used.

- As a research collaborator, I can inspect Strict OpenAlex Coverage for every PKP-inferred country group, including missing country, without treating the field as authoritative publisher location.
- As a maintainer, I can regenerate the local profile without OpenAlex requests and use the existing `--check` command to verify cohort, reconciliation, privacy, match-route, and Exploratory Analysis boundaries.

## Task report

| Stage | Commit | Command | Evidence |
|---|---|---|---|
| RED | `388c351` | `python3 research/ojs-journal-metadata/analysis/enrich_openalex.py --check` | Exit 1 at the intended boundary: `FileNotFoundError: strict-openalex-coverage-profile-summary.json` |
| GREEN | `d7e6adb` | `python3 research/ojs-journal-metadata/analysis/enrich_openalex.py --profile && python3 research/ojs-journal-metadata/analysis/enrich_openalex.py --check` | Exit 0: the summary reported 64,773 cohort rows, 49,877 unique, 190 ambiguous, 14,706 unmatched, 161 country groups, and zero API requests; the check printed `PKP–OpenAlex pipeline check passed` |
| Review RED | `f8ae712` | `python3 research/ojs-journal-metadata/analysis/enrich_openalex.py --check` | Exit 1 at the strengthened contract: `KeyError: identifier_availability` |
| Review GREEN | `8132231` | Profile generation followed by the same `--check` | PASS: per-country outcome counts, Wilson values, and the 86,282-row Identifier Availability split reconcile independently |
| Final CLI verification | `8132231` | `black --check ...`; `flake8 --ignore=E203,E501,W503 ...`; `python3 -m compileall -q src research/ojs-journal-metadata/analysis`; profile generation; `--check` | PASS |

## Test specification

| # | What is guaranteed | Test target | Type | Result |
|---|---|---|---|---|
| 1 | The profile uses exactly the 64,773-row Valid-ISSN OJS Cohort and reconciles to accepted unique, ambiguous, and unmatched totals | `enrich_openalex.py --check` | End to end | PASS |
| 2 | Each country group is exclusive and all groups collectively exhaust the cohort | `enrich_openalex.py --check` | End to end | PASS |
| 3 | Each row reports denominator, three outcome counts, strict coverage percentage, and bounded 95% Wilson interval | `enrich_openalex.py --check` | End to end | PASS |
| 4 | Missing PKP-inferred country remains an explicit 1,196-row group and the summary carries the location caveat | `enrich_openalex.py --check` | End to end | PASS |
| 5 | Only exact-ISSN unique matches count as Strict OpenAlex Coverage; provisional title coverage remains zero | `enrich_openalex.py --check` | End to end | PASS |
| 6 | Profile generation needs no API key, records zero OpenAlex requests, excludes `admin_email`, and remains Exploratory Analysis | `enrich_openalex.py --profile`; `enrich_openalex.py --check` | Integration | PASS |

## Coverage and known gaps

`coverage run --branch` across `--profile` and `--check` reported 47% for the combined 440-statement enrichment/profile script. The uncovered lines are primarily the existing full OpenAlex API acquisition path, which this issue must not call; the governing spec requires the current end-to-end check instead of a second test framework. The repository has no configured coverage threshold.

The full `pytest -q` run reported 25 passed and two failures already present at starting commit `9f088a8`: the exploratory-owner inventory predates `ojs-journal-metadata`, and the publication-compendium allowlist omits the already-tracked Khanna literature note. Neither baseline contract was changed for issue #74. Static typecheckers are not installed; Black, Black-compatible Flake8, `py_compile`, and `compileall` passed.

If the two TDD checkpoint commits are later squashed, preserve this RED/GREEN summary in the merge record.
