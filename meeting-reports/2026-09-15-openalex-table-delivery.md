# OpenAlex Table Consolidation and Delivery — Meeting Outcomes

- **Date:** 2026-09-15, as labelled in the supplied export and consistent with the previously user-confirmed meeting date; the export's 17:53 is not a verified start time
- **Status:** Communication record; Exploratory Analysis only
- **Intake reference:** `inbox/file-0fe9cb2c-a7e5-4f2a-a192-9b650f0f40b7-20260915-175829.md`
- **Intake SHA-256:** `21d7b9957fb5b8cb07e6e98e641b881984e5fd9bd8b2675f83825f2128fe1af5`

## Evidence boundary

Checked against the supplied timestamped transcript spanning 00:00–16:12.
There are substantial gaps, including 04:21–06:24 and 11:57–15:23. The original
audio, shared screen, meeting-chat SQL and calendar invitation were not supplied.
The generated summary is not independent evidence. Supervisor/researcher roles
are inferred from context, corresponding broadly to SPEAKER_00/SPEAKER_01;
turn boundaries around 06:24–06:32 and 08:54 are uncertain.
The original remains unchanged in the local-only Inbox. Personal career and
social discussion is omitted from the project record.

## Immediate deliverable

The supervisor asks for the downloaded OpenAlex tables to be combined into
**one inspectable, downloadable CSV**, naming sources, topics, APC and other
related information as examples (01:57–03:02). DuckDB and another uncertain
tool name are discussed as options; the instruction is to achieve the table
deliverable, not to mandate a specific tool or build an interactive dashboard.
The remark about Parquet concerns ease of inspection in this exchange; it is
not a general technical limitation or an instruction to discard source files.

The agreed workflow discussion is to copy the relevant OpenAlex tables into
the working database and check **missing values in each column in BigQuery**
(00:53–01:11; 03:11–03:19; 06:24–06:32). The supervisor reports posting example
copy SQL in the meeting chat; its contents and execution result are absent.
“All the tables” is recorded in this journal-metadata context, not treated as
an instruction to ingest every article/author table in OpenAlex.

At 07:35–07:51, the supervisor asks for the CSV in the **same SURFdrive folder
previously shared**, with this stage reached before discussing subsequent work
next week. No upload or remote file readback is evidenced by the transcript.

## Scope and unresolved inputs

- **Journal-level unit confirmed:** 10:00–10:41 explicitly distinguishes
  journals from individual papers. A journal's paper count can be a field;
  article-level analysis is only a possible future reviewer-driven extension.
- **Snapshot still needs exact identification:** 00:03–00:16 refers to a
  January 2026-looking OpenAlex name; 04:05–04:21 discusses three alternatives
  transcribed as EU RM, RM and RM EU. These are uncertain spoken labels, not
  verified dataset IDs or evidence that the alternatives are equivalent.
- **Implementation choices remain:** resolve the actual tables, destination,
  join keys and one-to-many aggregation rules before execution. Preserve one
  journal row and document denominators and field-specific missingness. These
  are checks from the existing [input contract](../research/openalex-journal-baseline/input-contract.md),
  not SQL or methodological details supplied by this meeting.

The existing [access record](../docs/testing/bigquery-access.md) and live Plane
comments read during intake retain the September 15 failed SQL test and prior
successful alternate core-table read. A demonstration or proposed table copy
does not prove the researcher's query-job permission is repaired. The existing
candidate core data are reusable context, not acceptance of a final snapshot
or completion of the requested combined table. No database run occurred in
this intake.

## Commercial-index follow-up

At 15:25–15:40, the supervisor explicitly undertakes to start looking into
Scopus and Web of Science access on their side, for discussion next meeting
after the table-delivery stage. Record this external responsibility within
INVIS-9; do not transfer it to the researcher or infer an account entitlement.
Access investigation can proceed alongside table preparation. Formal coverage
labelling retains its dependency on the established journal baseline.

## Action register and existing Plane mapping

Owners below are contextual role inferences, not verified speaker identities.
The [management registry](../docs/operations/project-management.json) retains
stable task keys; this intake adds sources to existing tasks.

| Existing item | Action / responsibility | Evidence | Next checkpoint and completion evidence |
|---|---|---|---|
| INVIS-6 — BigQuery access | Researcher verifies the execution route and working-database destination; supervisor/admin access responsibility remains as previously recorded | 00:53–01:11; 06:24–06:32 | Before copy/BigQuery audit; actual successful job evidence is required to release the SQL blocker |
| INVIS-7 — snapshot and row contract | Researcher records exact snapshot/table IDs and journal-row join rules; supervisor clarifies displayed alternatives as needed | 00:03–00:16; 02:45–03:02; 04:05–04:21; 10:00–10:41 | Existing September 17 internal review target; candidate selection and related-table scope remain open |
| INVIS-8 — extraction and delivery | Researcher consolidates relevant tables, reports per-column missingness, exports inspectable journal CSV and uploads to the existing SURFdrive folder | 01:57–03:19; 06:24–06:32; 07:35–07:51 | Before next discussion; September 21 remains a conditional internal target; reproducible output, row checks, missingness evidence and remote readback required |
| INVIS-9 — WoS/Scopus coverage | Supervisor investigates commercial-index access; researcher retains subsequent matching work | 15:25–15:40 | Discuss access route next meeting; existing October 1 conditional target is not a new supervisor deadline |
| INVIS-1 — management | Record follow-up meeting wording; verify the actual invitation before fixing its date | 08:10–08:30; 10:58–11:05 | “Next week”, 09:30 Amsterdam; exact date and duration unverified |

Live intake readback found INVIS-7 in **In Review**, and INVIS-6/8/9 **Blocked**.
These states and current internal dates are retained: processing the meeting
does not execute or finish the research tasks. INVIS-5's existing review state
is not acceptance evidence, and this transcript supplies no new Crossref task.
No duplicate issue is needed. The existing dependency chain 7 → 8 → 9 → 10
remains; the previously removed SQL hard dependency on all of INVIS-8 is not
reinstated merely because BigQuery was discussed. Its proposed SQL steps still
require functioning job permissions.

## Next meeting: date not established

The transcript supports **next week at 09:30 Amsterdam time** (08:10–08:30).
The supervisor reports sending an invitation (10:58–11:05); receipt and actual
calendar fields were not verified. “Next Wednesday” appears only in the
generated summary, not the supplied transcript, so no September 23 appointment,
China-time conversion or deadline is asserted. The previous user-confirmed
September 15 appointment remains historical scheduling evidence, not the next
meeting. Confirm the invitation before changing date-based reminders or targets.

## Subsequent user clarification and verification — September 15

After intake, the user reported successful manual querying of `multiobs`,
supplied a browser view and the supervisor's single-table CLONE example from
Mattermost, and requested a dataset comparison. The example identifies
`multiobs.publicdb_openalex_2026_01_rm.sources_societies` as the base and
`multiobs.userdb_saurabh_khanna.sources_societies` as the destination. This is
additional user-supplied evidence, not reconstructed meeting-chat contents.

The [subsequent live comparison](../research/openalex-journal-baseline/dataset-comparison.md)
located the EU/US public datasets and 11 existing supervisor clones, verified
their journal-related content fingerprints, and successfully queried the target
tables through the YannJY execution project. It supersedes the earlier absence
of exact identifiers and successful alternate SQL-route evidence. It does not
show that `insyspo`/`multiobs` job permissions were repaired, that final research
scope was accepted, or that the combined CSV/SURFdrive delivery is complete.

## Governance

This report supplements the [previous meeting record](2026-09-14-openalex-baseline-and-access.md)
and guides follow-up through the [Plane workflow](../docs/operations/project-management.md).
It creates no Candidate Version, Designation Event or Paper Analysis designation.
Only the privacy-safe summary and source identity enter Git/Plane; the private
transcript, personal discussion and sharing credentials remain local.


## Further user clarification: active connection and execution

Later on September 15, the user explicitly stated that the old `insyspo`
database is retired and the new `multiobs` database is the correct active source.
They requested persistent CLI/MCP scope correction, inspection of their successful
Brave public-table query, a simple Markdown verification report with evidence,
and progress on the coming week's tasks beginning with the merged journal CSV.
This clarification settles the active-project choice for this execution; the
subsequent [input contract](../research/openalex-journal-baseline/input-contract.md)
uses January 2026 US. It does not establish unavailable topics data or commercial
index access. Actual execution and delivery evidence belong to the
[journal export report](../research/openalex-journal-baseline/journal-export.md).
