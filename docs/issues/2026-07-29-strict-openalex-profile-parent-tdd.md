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

No OpenAlex request was made. The GREEN and final verification evidence will be
added after the profile is generated from these local inputs.
