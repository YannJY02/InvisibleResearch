# OpenAlex Baseline, Crossref Contribution, and BigQuery Access — Meeting Outcomes

- **Date:** 2026-09-14, as labelled in the imported record; actual meeting date is unverified
- **Status:** Communication record; Exploratory Analysis only
- **Intake reference:** `inbox/file-3a9cf8d4-10b4-4882-81a9-97a6966fb9cc-20260914-193836.md`
- **Intake SHA-256:** `f85d4a024b6bf364458deaa88ddd8661d7fc4f5001c6b50c101b8a41ab1bcedd`

## Evidence boundary

This report was checked against the supplied timestamped transcript, covering
00:42–34:39 of a record labelled 34:45 long. The transcript has gaps and uncertain
speaker attribution; the original audio and calendar invitation were not
available in this intake. Researcher and supervisor roles below are inferred
from context. The generated summary is an aid, not independent corroboration.
The original file remains unchanged in the local-only Inbox.

The export labels the meeting 14 September, but the closing discussion says
“15th next Tuesday” and refers to an invitation for “next week” (33:08–34:23).
The transcript alone cannot settle those dates. The follow-up schedule was
subsequently confirmed by the user below; the original meeting date remains
unverified. This report uses the supplied date for filing.

## Agreed immediate work

### 1. Assess Crossref's contribution alongside an OpenAlex baseline

The supervisor describes OpenAlex as the baseline and asks which Crossref
variables exist and are needed (00:42–02:56; 08:34–08:41). The title is discussed
as already available, while DOI-count information may be useful (06:06–07:43).
This calls for a field-level assessment of overlap and additional information;
it does not establish that every Crossref field is redundant or should be
removed from the retained source data.

A specific requested check is to identify rows with Crossref information but
no OpenAlex information (07:51–08:29). The meeting reports no count or completed
result. For implementation, distinguish an unmatched source record from a
matched record with empty fields, an ambiguous identity match, or a lookup
that was not attempted. The existing [journal enrichment and disagreement
analysis](../research/ojs-journal-metadata/README.md) provides the relevant
workflow; its results were not rerun or revalidated during this intake.

At 06:21–06:29, the supervisor suggests that the displayed empty list and missing
value should both be treated as missing in the data, while separating this
from the field-selection question. The transcript does not identify the exact
column or establish a universal recoding rule. Preserve the raw representation
and decide any analytical normalization for the specific field after inspection.

“OpenAlex as baseline” is recorded as the meeting's direction. It does not
specify a replacement cohort, row key, or denominator. The existing PKP/OJS
row-preservation contract and [Strict OpenAlex Coverage](../CONTEXT.md) definition
remain the implemented reference until those methodological choices are explicit.

### 2. Resolve BigQuery query access and identify the intended snapshot

BigQuery is discussed as a route to query and extract available tables instead
of spending days on API retrieval (10:16–10:39). Sources are central; concepts,
publisher information, and other related tables should be inspected for need
(13:48–14:21; 23:45–24:01). No extraction query or completed export is supplied.

The supervisor provisionally suggests the January 2026 snapshot and may ask
the data administrators how three displayed alternatives differ
(19:24–19:47). Earlier remarks mention differing field counts (13:40–13:48),
whereas the later alternatives appear to have the same fields. Their exact
identifiers and equivalence are unresolved. January 2026 is a preference, not
a pinned input Artifact Version.

Access remains unresolved in the evidence:

- The researcher reports being able to read at 22:54, followed by a supervisor
  remark about writing; this exchange does not verify write access.
- At 24:40 the researcher explicitly says the query can be opened but not run.
  The adjacent success/failure wording at 24:59 has uncertain attribution.
- At 26:46 the supervisor reports being unable to edit permissions on the
  resource. A public-resource message at 26:56 does not prove that the
  researcher's query job can execute.
- At 27:29–27:39 the supervisor asks for an error screenshot in Mattermost so
  the administrators can investigate. The transcript supplies no evidence
  that the screenshot was sent or permissions were subsequently repaired.

The immediate arrangement is for the researcher to provide the screenshot
and the supervisor to contact the administrators. If access cannot be resolved,
the supervisor could run a supplied query; this is explicitly a fallback,
not the selected next step (34:23–34:39). No IAM change or database operation
was performed as part of processing this record.

## Subsequent commercial-index comparison

After the preceding work, the supervisor proposes checking which records are
represented in Web of Science and Scopus (31:02–32:01). The transcript says
“which one” without settling the unit of comparison; the project context is
journal-level, but the generated summary's article-level wording is not enough
to establish a switch to individual publications. Confirm the unit, cohort,
index collection, snapshot, and matching rule before implementation.

“Ten twenty days” is tentative planning language, with possible library help,
not a fixed delivery deadline or confirmed access window (31:46–32:01).
The [July source assessment](../research/ojs-journal-metadata/follow-on-source-assessment.md)
retains its historical scope. This meeting adds a coverage-comparison direction;
it does not select a commercial API, establish entitlement, or request JCR or
Scopus metrics. The access route still needs to be determined for that question.

## Action register

These are follow-ups recorded from the meeting, not completion claims or
newly created tracker issues. Owners are inferred from the exchange.

| Owner | Action | Timing or dependency | Evidence |
|---|---|---|---|
| Researcher | Review Crossref fields for overlap and useful additions to OpenAlex | Report columns and findings at the next meeting | 02:13–02:56; 34:23 |
| Researcher | Identify rows with Crossref information and no OpenAlex information, distinguishing match status from field missingness | Alongside the field review; no result supplied | 07:51–08:29 |
| Researcher | Inspect the displayed empty-list/missing-value case and document field-specific treatment | Before analytical recoding | 06:21–06:29 |
| Researcher | Send the BigQuery error screenshot to the supervisor through Mattermost | Needed for access escalation; sending is not evidenced | 27:29–27:39 |
| Supervisor | Ask the administrators to resolve the researcher's query-execution access | After receiving diagnostic evidence | 26:46–27:39 |
| Supervisor, with researcher | Clarify the three snapshot alternatives and record the selected dataset/table identifiers | January 2026 is provisional; before extraction | 19:24–19:47 |
| Researcher and supervisor | Define and investigate Web of Science/Scopus coverage comparison | After the preceding work; tentative 10–20-day estimate | 31:02–32:01 |
| Researcher and supervisor | Prepare for the next meeting | User subsequently confirmed September 15, 16:00–16:30 China time; see source clarification below | 33:08–34:23; user confirmation on September 14 |

## Subsequent source clarification — 2026-09-14

During project-management intake, the user explicitly confirmed the next meeting
as **2026-09-15, 16:00–16:30 China time**. This supersedes the transcript's
13:00 Amsterdam wording. An internal preparation checkpoint is 15:00 China
time. Searches in the connected Gmail, Outlook and primary Google Calendar did
not locate the invitation; the user's confirmation supplies the scheduling
authority without establishing the original recording's meeting date.

The [supervisor's September 5 comment on upstream issue #5, edited September 8](https://github.com/invisibleinfo/invisible-research/issues/5#issuecomment-5553748839)
was also read directly. It specifies **all OpenAlex journals** as the next
baseline, a metadata file on SURFdrive, journal-row ISSN checks against Web of
Science and Scopus, then Boruta/SHAP predictor analysis. This resolves the
transcript-only ambiguity about the comparison unit and broad baseline scope.
The exact snapshot, journal filter, row key and matching contract still need
implementation decisions. The existing PKP pipeline remains a historical
foundation; its output is not the new OpenAlex-wide baseline.

The [Plane management workflow](../docs/operations/project-management.md) now
tracks these source-backed actions, their dependencies and current progress.
The earlier sections preserve what the transcript itself supported; this
supplement records the additional sources rather than attributing them to the
recorded conversation.

## Governance

This communication updates the exploratory work direction following the
[July meeting](2026-07-28-ojs-enrichment-next-steps.md). It creates no Candidate
Version, Designation Event, or Paper Analysis designation. The suggestions
about database roles, alternative query execution, and commercial-index access
are recorded discussion, not verified permissions or completed operations.
