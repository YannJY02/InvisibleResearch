# Issue tracker: Plane

Plane is the current task tracker for InvisibleResearch, following the user's
2026-09-14 instruction. Use the [project workflow](../operations/project-management.md)
and [source-to-task registry](../operations/project-management.json).
This supersedes the former GitHub issue-management default for future work here.

## Start, progress, and delivery

- Read the current Plane record, dependencies, assignment, dates, and linked
  evidence before work. Check incoming meeting and upstream issue changes.
- Map new authorized work to an existing task first. Create a task only from a
  real meeting action, repository issue/comment, explicit project action in
  Mattermost with the supervisor, or explicit user instruction;
  retain the exact source and a stable deduplication key. Do not turn ideas,
  missing evidence, or status observations into invented assignments.
- Set In Progress when execution actually begins. Update the task at meaningful
  findings, blockers, scope/date changes, and delivery, without waiting for the
  end of the conversation. Each update states what changed, evidence, remaining
  work, and the next checkpoint. Read back writes.
- For repository changes, preserve unrelated work, verify, commit, and push.
  Then record the commit and actual checks in Plane and use In Review for human
  acceptance. Historical completed work may be backfilled as Done when the
  original closure/acceptance and deliverable evidence support that exact scope.
- Native Plane comments, descriptions, assignment, dates, and dependency links
  are the current progress record. Local registry dates are initial planning
  provenance, not an instruction to overwrite newer Plane edits.

## Mattermost is an action and background source

Use the [Mattermost intake rules](../operations/project-management.md#mattermost-source-intake)
for supervisor exchanges. Attribute author/date/permalink and distinguish an
explicit action from background, reported completion and acceptance. Reuse the
existing task first. User-provided Appshots are bounded evidence; unread
attachments and unsent drafts do not establish facts or assignments. The GitHub
collector does not automatically poll Mattermost. Read-only collection does not
authorize sending messages.

## GitHub is a collection source

Monitor `invisibleinfo/invisible-research` issues, including closed issues,
comments (including edits), assignments/unassignments, labels, milestones, and
status changes. Use the explicit repository; the local Git remote is a different
repository. The collector follows all pages and excludes pull requests.

Only collect and interpret source changes. Do not create an issue-set mirror,
turn on a GitHub–Plane integration, or write comments, labels, state, assignment,
or other changes to the upstream repository. A selected source action can
support a Plane task, but its status is evaluated independently against delivery
and acceptance evidence. Closed source issues do not complete all their checklist
items in Plane. An assigned source issue is not authority to start every task
inside it without checking scope and dependencies.

Read-only source commands include:

```sh
gh issue view 5 --repo invisibleinfo/invisible-research --comments
PYTHONPATH=src python3 -m invisible_research.project_intake collect
```

Existing local GitHub issues and merged PRs remain historical evidence. Do not
mass-close, migrate, or mirror them. The user's commit/push agreement for this
repository remains in force. Sending messages to collaborators, including
Mattermost/email, still needs corresponding explicit authorization.

## Triage and recurring checks

The [triage vocabulary](triage-labels.md) remains useful for classifying intake;
it does not authorize writing those labels upstream. Keep accepted task scope
and actual assignees distinct from inferred speaker roles.

During active work, publish meaningful progress immediately. During idle time,
the configured heartbeat checks source changes, Plane changes and
schedule risks. This is polling, not a webhook or a guarantee while the host or
credentials are unavailable. A failed collection/sync retains pending evidence;
never claim a successful sync from a scheduler configuration alone.
