# InvisibleResearch Project Management

Plane owns current tasks, assignment, dependencies, dates, and progress. The
user established this workflow on 2026-09-14 for this and future tasks in the
workspace. [AGENTS.md](../../AGENTS.md) makes it part of task startup and delivery.
The [registry](project-management.json) stores project, task, source and automation
identifiers; it is mapping and planning provenance, not a competing status tracker.

## Project and source boundaries

- Plane project: **InvisibleResearch**, identifier **INVIS**, UUID
  `0624dddb-fd32-4c90-870b-921183e73676`; timezone **Asia/Shanghai**.
- Sources: real [meeting actions](../../meeting-reports/README.md), selected
  repository issues/comments, project-related Mattermost exchanges with the
  supervisor, and explicit user instructions. Each Plane task
  links its source and acceptance criteria. New observations alone do not
  authorize invented tasks or automatic research execution.
- Monitor [invisibleinfo/invisible-research issues](https://github.com/invisibleinfo/invisible-research/issues)
  with **GET only**. Collect the issue list, comments including edits, assignment
  events, state, labels, milestones and timestamps across every available page.
  Exclude PRs. Do not mirror the issue collection, enable an integration, or
  write upstream. This differs from the local `YannJY02/InvisibleResearch` remote.
- Upload only project-safe summaries, links, metadata and evidence references.
  Raw Inbox material stays unchanged and ignored; no audio, private transcript,
  credential, meeting-access link, or personal administrative detail enters Plane.
- Saurabh's source assignments and meeting responsibilities are recorded in
  descriptions. Only Yann currently has a matching human Plane member; do not
  invent an account, invite a collaborator, or silently transfer their work.

## Current phase and historical cut

The latest substantive pivot is the [2026-09-05 comment on upstream #5,
edited September 8](https://github.com/invisibleinfo/invisible-research/issues/5#issuecomment-5553748839):
use all OpenAlex **journals** as the baseline, extract metadata to SURFdrive,
compare WoS/Scopus inclusion by ISSN, then investigate predictors with
Boruta/SHAP. This source settles the journal-level unit left ambiguous by the
recent transcript alone. Snapshot, journal filter, row identity and matching
rules still need explicit implementation choices and evidence.

Selected foundations from the July 16/28 meetings are backfilled, rather than
the whole earlier backlog:

| Plane item | Historical scope and evidence |
|---|---|
| INVIS-2 | Ten-row enrichment sample; [July 18 result and checked source task](https://github.com/invisibleinfo/invisible-research/issues/6#issuecomment-5010060289). Fixed matching-case sample, not representative random sampling. |
| INVIS-3 | Local PKP V7 full enrichment and interactive review; [July 29 delivery](https://github.com/YannJY02/InvisibleResearch/issues/98#issuecomment-5113777503), merged PR #103, later August improvements. August Mattermost delivery/feedback evidence is recorded below; this is not the new OpenAlex-wide extraction. |
| INVIS-4 | Initial 18-note conceptual literature evidence set and counter-explanation audit; [July 22 accepted closure](https://github.com/YannJY02/InvisibleResearch/issues/76#issuecomment-5041986142). This is not a literature-review draft. |

Historical completion dates belong in the evidence narrative. Plane's newly
created `completed_at` is the import time, not an invented historical timestamp.
The July script handoff/server run and supervisor seed-paper receipt have no
completion evidence. Preserve those gaps in the history page; do not restart
the old API run simply because the handoff is unconfirmed. Seed-based writing
remains the parallel carryover task INVIS-11.

## Mattermost source intake

On 2026-09-14 the user added project-related Mattermost exchanges with the
supervisor as a potential task source and background source. Record author,
message date, permalink, action or decision, and evidence scope. Explicit project
actions can support a task after deduplication; background, discussion, shared
articles and status reports normally supplement an existing task. Do not turn
social conversation, a suggestion, or an unsent composer draft into an assignment.

Use available authorized read-only access or user-supplied excerpts/Appshots.
State the actual coverage; the current collector does not poll Mattermost.
Do not claim complete chat history or automatic Mattermost monitoring. Preserve
message IDs for deduplication and attribute reported completion separately from
supervisor feedback and independent artifact verification. Attachment presence
is not knowledge of its contents. Store only project-safe paraphrases and source
references; omit private unrelated conversation and token-bearing sharing links.
This source authorization does not authorize sending messages.

### Evidence supplied on September 14

Source: user-provided Mattermost Appshot captured at 2026-09-14T15:06:39.083Z,
including its visible accessibility text. Dates below follow that supplied UI;
message timezone was not independently established. Permalinks were supplied in
the Appshot, not independently fetched from the server in this intake.

- **INVIS-3 — historical delivery:** [August 15 report message](https://mattermost.invisible.info/invisible-information-lab/pl/qb5de3uzi3fgbpfn9aqra9sb9r)
  shows Jinyi shared an RPubs report and described a full PKP-data version.
  The visible conversation includes a QMD attachment. [Saurabh's August 15 reply](https://mattermost.invisible.info/invisible-information-lab/pl/wmgw3hmfh3rk5rff5tjnqa1zee)
  says only the QMD was visible in SURFdrive and asks whether parquet upload
  finished. [Jinyi's August 16 message](https://mattermost.invisible.info/invisible-information-lab/pl/o7r8wjnc8pdnup7tgr6y3r149a)
  reports successful re-upload. [Saurabh's August 27 feedback](https://mattermost.invisible.info/invisible-information-lab/pl/5ggjckon8p817egctrf6h9cnky)
  describes the preceding work as useful and proposes discussing next steps.
  This adds actual sharing, self-reported upload and supervisor feedback evidence
  to the earlier local-only audit. It does not independently verify the remote
  parquet contents, a collaborator-repository handoff or a server execution.
  INVIS-3 remains historically Done in its accepted local-delivery scope;
  INVIS-8's new OpenAlex-wide delivery remains separate.
- **INVIS-5 — prior field explanation:** [Jinyi's September 8 message](https://mattermost.invisible.info/invisible-information-lab/pl/nawjj4usqby5zns9y6rakxba6w)
  already explains Crossref's DOI registration counts/yearly breakdowns and
  metadata provision/completeness indicators (abstracts, references, affiliations,
  ORCID, funding, licences), relative to OpenAlex fields in the existing dataset.
  This is a communicated finding to reuse, not a newly verified schema comparison.
  [The later message](https://mattermost.invisible.info/invisible-information-lab/pl/r6tpz8eya38cjdwi5xjx1qr1ao)
  contains two screenshot attachments; their contents have not been inspected.
  INVIS-5 remains Todo for the remaining sourced counts/examples, denominator,
  version evidence and field-specific missingness checks. Do not redo the sent
  explanation as though no prior work existed, or mark the whole task complete.

## September 15 meeting intake and current follow-up

The [new meeting record](../../meeting-reports/2026-09-15-openalex-table-delivery.md)
adds source-backed requirements to existing INVIS-6/7/8/9: identify the displayed
snapshot alternatives, consolidate relevant journal metadata into one inspectable
CSV, check per-column missingness with the discussed BigQuery route, and deliver
to the previously shared SURFdrive folder. The supervisor will investigate
Scopus/WoS access. Journal-level analysis is explicit; article-level work remains
only a possible future extension. Tool names discussed are options.

The transcript does not verify SQL repair, a completed table copy/upload, final
snapshot acceptance, or acceptance of earlier Crossref work. Live Plane readback
retains INVIS-7 in In Review and INVIS-6/8/9 Blocked. The current native chain is
INVIS-7 → INVIS-8 → INVIS-9 → INVIS-10; the earlier successful alternate core read
already removed the hard SQL dependency for all of INVIS-8. BigQuery copy/audit
steps still need actual successful job evidence. Existing internal dates remain
planning targets, including the conditional September 21 delivery target.

**Next meeting:** the supplied transcript says next week at **09:30 Amsterdam**,
and reports an invitation sent. Exact date, duration and receipt are unverified;
Wednesday appears only in the generated summary. Confirm the invitation before
setting a date or changing reminders. The September 15 appointment below is
historical user-confirmed scheduling evidence, not the next meeting.

## Previous meeting and initial schedule

The user confirmed **2026-09-15, 16:00–16:30 China time** in this task. This
supersedes the transcript's 13:00 Amsterdam wording. The internal preparation
checkpoint is **15:00 China time**. Connected Gmail, Outlook and the primary
Google Calendar searches did not locate the invitation; the user confirmation
is the scheduling authority. It does not establish the date of the older
meeting in the imported recording.

The dates below are an initial internal plan, not supervisor-promised deadlines.
The meeting's “10–20 days” is a rough estimate. Replan in Plane when dependencies
change and record why; do not silently roll dates forward or claim success.

| Item | Initial checkpoint/target | Dependency and outcome |
|---|---|---|
| INVIS-1 — management setup | September 15 before meeting | Source-backed tasks, history, live readback, persistent workflow and monitoring; In Review after delivery. |
| INVIS-5 — Crossref increment | September 15, 15:00 internal checkpoint | Reuse existing comparisons; readable field increment, OA-empty/CR-present cases, denominators, and specific missing-value handling. |
| INVIS-6 — BigQuery access | September 15 before meeting | Diagnostic/status checkpoint, not an assurance of administrator repair. Unblock only with actual bounded query evidence or an explicitly selected alternative execution route. |
| INVIS-7 — snapshot/row contract | September 17 | Define the OpenAlex-wide input, version and journal filter; schema planning may proceed alongside access work. |
| INVIS-8 — extract and SURFdrive delivery | September 21, conditional | Blocked by INVIS-6 and INVIS-7. Verify both complete output and remote file; old PKP CSV cannot satisfy it. |
| INVIS-9 — commercial coverage | October 1, conditional | Formal labelling follows INVIS-8. Access-route research can proceed in parallel. Record versions and distinct unmatched/error/missing-identifier states. |
| INVIS-10 — feature modelling | Estimate after coverage review | Blocked by INVIS-9, held in Backlog; no unsupported completion date. |
| INVIS-11 — seed-based overview | September 22 status checkpoint | Confirm seed receipt, then scope and schedule the draft; old evidence notes do not settle this dependency. |

## Progress updates during every task

1. Read this workflow, the registry and the current linked Plane record with
   dependencies, assignees, dates, description and relevant comments. Check
   Git status and incoming source changes; preserve unrelated edits.
2. Reuse the existing source/action mapping. For a new task, name the real
   source, action, owner, dependency, acceptance and date basis. Use a stable
   `external_source=invisible-research-intake` and action-specific `external_id`.
   Search all current and archived project items before creating; one source
   issue can yield several distinct actions, but never a wholesale issue mirror.
3. Move to In Progress only when work starts. At meaningful findings, changed
   scope, dependency blocks, date risk and delivery, update Plane immediately
   and read it back. Comments state the change, evidence, remaining work and
   next checkpoint. Do not publish repetitive no-change comments or fabricate
   percentages, elapsed work or human acceptance.
4. Use Blocked with a named cause, responsible party and release condition.
   Todo is executable upcoming work; Backlog is deferred. For new agent
   delivery, verify, commit and push repository changes, then post evidence and
   move to In Review. Done requires actual acceptance/closure evidence; the
   historical backfill uses its original evidence, not the act of importing.
5. Update the affected dependencies, dates and project overview when material
   progress changes the plan. Newer human Plane edits take precedence over the
   registry's initial dates. Do not erase them in a bulk update.

Plane setup can partially succeed even when a tool returns an error. In the
initial run, project creation reported HTTP 400 although the project existed
on readback. Read the current remote objects before retrying any ambiguous
write. Reconcile by ID and source key; never blindly create a duplicate.

## Hourly source and schedule monitoring

The thread heartbeat runs every hour while available. Active task progress is
updated at the events above; hourly polling covers idle source/schedule changes.
It is not a webhook and cannot guarantee wall-clock freshness while the host,
scheduler, network or credentials are unavailable. The heartbeat performs
management and source intake, not unrequested data runs or new research writing.

Use the existing authenticated Plane MCP. If its tools are not initially exposed,
discover the configured `plane` server through MCP resource listing, then search
the available tool metadata again. Do not reinstall or change credentials or
global approval settings to work around discovery.

Run from the repository root:

```sh
PYTHONPATH=src python3 -m invisible_research.project_intake collect
```

All outputs stay in ignored `docs/operations/artifacts/project-management/`:

- `github-snapshot.json`: last successful all-issue/comment/event read, including
  locally retained GitHub bodies and their SHA-256 identities so an observed
  intermediate edit remains recoverable. Inbox/report originals have only
  hashes; their text is not retained. This ignored evidence is not an issue-set
  mirror in Plane or a cloud index. Coverage and collection time are recorded.
- `change-summary.json`: latest attempt, changed/new/unavailable records,
  assignments, edited comments and outstanding change IDs. A failed read keeps
  the last good baseline. Unavailable is not proof of deletion.
- `pending/<change-id>.json`: durable observations awaiting reconciliation.
  An unchanged later collection must not erase an undelivered change.
- `acknowledged/<change-id>.json`: processed observations retained for audit.
- `plane-snapshot.json`: current project/task/state/relation/page readback with
  UTC collection time; keep project metadata and safe summaries only.
- `monitor-state.json`: last run, successful source collection, successful Plane
  reconciliation, pending failures and the last notified finding fingerprints.

Each heartbeat reads all pending observations, not just the newest diff. Inspect
the captured GitHub body and current source using read-only calls, or inspect
the local original for Inbox changes. Hashes alone cannot explain content;
hash-only legacy observations must be marked as content-unrecoverable if the
source has since changed. Polling cannot capture edits that occur wholly between
observations. Preserve changed-vs-new assignment and
the exact commenter/action attribution. Match to the current Plane item or
history/source page; collect unrelated or inactive source updates without
inventing a task. Reconcile edited deadlines or assignments against the source
and user instructions, not by blindly mirroring upstream values.

Only after the affected Plane writes have been read back, or a documented
no-action decision has been saved for an irrelevant change, acknowledge that
specific observation:

```sh
PYTHONPATH=src python3 -m invisible_research.project_intake acknowledge --change-id <change-id>
```

Before each run's acknowledgement, record the change ID, source review decision,
affected Plane IDs, readback time and any remaining issues in `monitor-state.json`.
Do not acknowledge incomplete collection, failed reconciliation or unknown
write results. An idempotent acknowledgement archives only the named observation.

Read current Plane work items, states, dependencies and dates with all pages.
Check upcoming checkpoints within 24 hours, overdue tasks, dependency/date
conflicts, new blocks and fresh human changes. Preserve explicit acceptance and
human scope decisions. A task in review is not a failed implementation merely
because acceptance is outstanding; record review delay separately.

Notify only for meaningful source/progress changes, delivery, new actionable
schedule risks, sync failures or required user decisions. Deduplicate findings
against `monitor-state.json`; unchanged known blockers should not trigger the
same reminder every hour. Never describe an unrun heartbeat as a passed live
check. Update this workflow and registry if the user changes these rules.

## Validation

For collector changes, run its behavioural tests and a bounded live collection.
For documentation changes, run the repository document-governance check.
Before delivery, read back the current Plane project, tasks, dependencies and
pages, verify the source/task mapping, and confirm Git push. Raw data pipeline
execution is outside this management setup's validation scope.
