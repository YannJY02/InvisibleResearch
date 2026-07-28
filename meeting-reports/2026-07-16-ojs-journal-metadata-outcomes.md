# OJS Journal Metadata Enrichment — Meeting Outcomes

- **Date:** 2026-07-16
- **Status:** Communication record; no Paper Analysis designation
- **Intake reference:** `inbox/2026_7_16_en_1.md`
- **Intake SHA-256:** `455cbe0bab472ae2a7529e45aa8857a5e91f5d9ea5338eeb7954b1786445ec8b`

## Agreed immediate goal

Produce a wide table with one OJS journal per row, using ISSN as the matching
identifier and adding available OpenAlex source metadata as columns. The
meeting described eventual enrichment from other sources, including Dimensions
and Web of Science, as a longer-term direction rather than the immediate task.

## First implementation step

1. Write one Python function that accepts an ISSN and returns the available
   OpenAlex metadata for the matched journal in a one-row form.
2. Include useful source fields such as journal title, publisher, topics, and
   citation-related measures where OpenAlex supplies them.
3. Test the function on a sample of about 10 journals and share the script for
   review before any full-cohort run.
4. Handle journals with multiple ISSNs by trying each identifier. If multiple
   ISSNs match, verify that they resolve consistently rather than silently
   selecting one result.
5. After the sample output is accepted, the collaborator can run the script on
   a server; a local full-cohort run is not required first.

The existing exploratory work established OpenAlex presence or absence. The
next step is to extract and join the returned OpenAlex variables, not merely
repeat the coverage check.

## Post-meeting sample review

Mattermost follow-up through 2026-07-21 expanded the reviewed sample to
OpenAlex and Crossref and added the following requirements before a
full-cohort run:

- Do not assume `per_page=100` makes an OpenAlex response complete. Check that
  `meta$count <= per_page`; if it is larger, retrieve every page or stop with an
  explicit incomplete-response result rather than silently dropping matches.
- Retain all available information returned by OpenAlex and Crossref before
  narrowing fields for presentation.
- Follow the polite-pool rules for both services and use pacing, retry, and
  backoff so throttling or IP blocks do not become silent missing values. The
  [`ratelimit`](https://github.com/tomasbasham/ratelimit) tool was shared as an
  optional way to insert sleeps and retries, not as a required project
  dependency.
- Share the sample result as CSV because the wide tibble did not render
  readably on RPubs.

The supervisor said the overall logic looked good, subject to reviewing a small
sample of the generated CSV before scaling. The researcher subsequently sent
the CSV in the supplied message thread. That submission is not, by itself,
evidence of final sample acceptance; the later [2026-07-28 meeting
record](2026-07-28-ojs-enrichment-next-steps.md) captures the subsequent
full-cohort decision and server handoff.

The follow-up also reported that a new version of the [PKP Dataverse
dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OCZNVY)
had been posted that week. The message does not identify its exact Artifact
Version, checksum, schema, or cohort size, so it does not silently replace the
pinned input. Those properties require verification and an explicit input
decision before use.

## Parallel literature task

Literature discovery may proceed in parallel with the code. It should remain
open to competing explanations rather than collect only studies that support a
preferred hypothesis.

For each potentially relevant study, add one GitHub issue comment containing:

- a short account of what the study did;
- why it may be relevant to the project; and
- a link to the paper.

The meeting did not request a full literature-review draft. Suggested discovery
venues included the source paper's references and interdisciplinary journals
such as *Science*, *Nature Human Behaviour*, *PNAS*, and *Science Advances*.

## Coordination

- There was no fixed delivery deadline or urgency; correctness and respectful
  API use take priority over finishing the full run quickly.
- Progress should be shared when the sample function and review CSV are ready.
- Questions and the next meeting time should be coordinated over Mattermost.
- This record summarizes instructions communicated in the meeting. It does not
  create a Candidate Version, Designation Event, or Paper Analysis designation.
