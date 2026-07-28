# OJS Journal Enrichment and Analysis — Meeting Outcomes

- **Date:** 2026-07-28
- **Status:** Communication record; Exploratory Analysis only
- **Intake reference:** `inbox/file-d5a928a3-164a-4539-b4b7-eaba1d8019fa-20260728-132032.md`
- **Intake SHA-256:** `df2f49f0e3a5b1410b6dd35311039849846d84bdcedec3c26237426705d50a7e`

## Evidence boundary

This record was checked against the timestamped transcript rather than relying
on its generated summary. Speaker roles are inferred from context. The
project-relevant meeting ends at approximately 30:45; unrelated private audio
from 36:47 onward and a separate personal administrative discussion are
intentionally excluded.

Post-meeting Mattermost messages supplied after the initial record clarify the
method, script handoff, and server-run responsibilities below. Meeting-access
and audio-confirmation messages are logistical only and do not add research
decisions.

## Agreed immediate work

### 1. Run the journal enrichment at full-cohort scale

Move from the reviewed sample to the complete pinned PKP/OJS cohort using the
existing [OpenAlex and Crossref enrichment
analysis](../research/ojs-journal-metadata/analysis/ojs_journal_enrichment.qmd).
The result should:

- retain one PKP/OJS journal per row in a single wide master CSV;
- add the available OpenAlex and Crossref fields as columns rather than
  narrowing the source responses prematurely;
- preserve exact-ISSN match status, including consistent, unmatched, and
  inconsistent results, so source disagreements remain reviewable; and
- keep the PKP rows even where no external-source match is found.

The run should respect API limits. Start slowly, identify requests where the
service supports it, and pause or resume later if throttling occurs. The
researcher will make the full-cohort script ready to run, add it to the
collaborator repository's [`scripts/`
folder](https://github.com/invisibleinfo/invisible-research/tree/main/scripts),
and notify the supervisor. The supervisor will then pull the changes and run
the script on a local server.

### 2. Make the review output readable

The current rendered wide table is difficult to inspect because long fields
expand the rows. Future shared reports should use an interactive,
searchable/filterable table using the R [`DT`
package](https://rstudio.github.io/DT/) shared after the meeting, and show or
hide code according to the audience. The master CSV remains the data
deliverable.

### 3. Start the literature review from a curated seed set

The supervisor will send a small manually curated set of papers relevant to
the journal-invisibility question. The researcher will use that set as the
starting point, follow its references to discover further work, and begin an
overview or draft in parallel with the enrichment run.

Broad AI-assisted discovery may supplement this process, but it should not be
the sole starting point because its results may overrepresent preprints,
repositories, or other material prominent in model training data.

## Later analysis direction

After the enriched journal table exists, the project may examine which journal
characteristics predict whether a journal is represented in an external
index. Language was discussed as one possible predictor. The intended analysis
is exploratory rather than a preregistered confirmatory test.

The meeting clearly mentioned a simple regression approach and SHAP as
candidate ways to examine predictor importance, with value in comparing a
simple and a more advanced view. The post-meeting clarification identifies
[`BorutaShap`](https://github.com/Ekeany/Boruta-Shap) as the intended method
for exploring which journal-level features predict journal invisibility in one
or more databases. This supersedes the transcript's uncertain “Robustify”
wording.

This modelling is not part of the immediate enrichment run. The outcome,
analysis cohort, predictor set, treatment of missing identifiers, and
interpretation of source absence still need to be specified before modelling.
In particular, source absence must not yet be treated as a settled causal
measure of journal “invisibility.”

## Possible follow-on data sources

OpenAlex and Crossref are the agreed first step. Search results and journal
landing pages may later supply variables missing from public databases.
PKP–OpenAlex title discrepancies may also be summarized for PKP once their
frequency and identity evidence are checked. Neither follow-on expands the
current task.

The supervisor also shared a community-maintained [list of free LLM API
resources](https://github.com/cheahjs/free-llm-api-resources). The message
assigns no project task and does not select or authorize any provider,
credential, or research-data transfer.

## Action register

| Owner | Action | Timing or dependency |
|---|---|---|
| Researcher | Finish the full-cohort OpenAlex and Crossref script, add it to the collaborator repository's `scripts/` folder, and notify the supervisor | No fixed deadline |
| Supervisor | Pull the ready script and run it on a local server | After researcher notification |
| Researcher | Produce one wide master CSV and a readable interactive review report | With the full-cohort run |
| Supervisor | Send the curated seed-paper list | Before the literature pass expands |
| Researcher | Start the literature overview from the seed set and citation chaining | In parallel with enrichment |
| Researcher | Send a durable non-student email address for future logistics | Before the UvA address expires |
| Researcher and supervisor | Define the modelling outcome and predictor set | Before predictor modelling |

No delivery deadline or next meeting date was fixed. The supervisor explicitly
said there was no rush because of one week of travel; the researcher will
notify the supervisor when the script is ready.

## Governance

This meeting authorizes the next **Exploratory Analysis** step: a full-cohort
OpenAlex and Crossref enrichment run. It does not create a Candidate Version,
Designation Event, or Paper Analysis designation. The ambition to develop a
strong paper or target a selective journal is a direction, not evidence that
the research question, method, or publication claim has been finalized.
