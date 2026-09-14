# Document Governance

This policy governs documents created or maintained in InvisibleResearch.
Use it when creating, importing, moving, or renaming documents. Choose the
owner and role before writing; update the existing canonical document when
the request changes that same subject.

## Placement and naming

| Role | Destination and naming |
|---|---|
| Repository entry points | Root `README.md`, `AGENTS.md`, and `CONTEXT.md` only |
| Shared data descriptions | `docs/data/<short-topic>.md`; figures beside the description |
| Governance and agent instructions | `docs/governance/<short-topic>.md` or `docs/agents/<short-topic>.md` |
| Setup and shared operations | `docs/operations/<short-topic>.md` |
| Writing guidance | `docs/writing/<short-topic>.md` |
| Issue-linked research or implementation notes | `docs/issues/YYYY-MM-DD-<short-topic>.md`; Plane is the current task tracker |
| Design plans | `docs/plans/YYYY-MM-DD-<short-topic>.md` |
| Recorded verification | `docs/testing/<short-topic>.md`; state the observation date and scope |
| Historical migration and retention records | `docs/history/<short-topic>.md` or `.json`; preserve recorded evidence |
| Architectural decisions | `docs/adr/YYYY-MM-DD-<short-topic>.md`, with explicit decision status |
| Research-specific notes | `research/<owner>/<short-topic>.md`; methods and notebooks remain in `analysis/` and `notebooks/` |
| Publication prose and presentations | `papers/<paper>/manuscript/<short-topic>.md` or the owner's established source format |
| Literature notes | `papers/<paper>/literature/<first-author>-<year>-<short-title>.md` |
| Applicable external writing requirements | `papers/<paper>/requirements/README.md` indexes the source, version, scope, and extracted rules; approved source copies live in `requirements/sources/` |
| Supervisor or group meeting summary | `meeting-reports/YYYY-MM-DD-<short-topic>.md`, linked from its README |
| Raw private input | Local-only `inbox/`; retain original names and bytes |
| Generated output, caches, render or publishing state | The owner's ignored `artifacts/<pipeline>/` directory; meeting exports use `meeting-reports/artifacts/<report-stem>/` |

Use lowercase words joined by hyphens for new prose filenames. Use the event
date for meeting reports and the creation date for issue notes and plans.
Update the same file for revisions; use Git history instead of `final`, `v2`,
or duplicate dated copies of current guidance. Established executable-source
names and immutable original-source names retain their existing conventions.

Keep a document near the work it governs. A research note belongs to its owner,
even when Markdown could also fit under `docs/`. A source document is evidence;
its extracted writing guidance is a separate document linking back to it.
The machine-readable path rules are [document-rules.json](document-rules.json).

## Authority and maintenance

- Preserve source facts, accepted decisions, drafts, and historical records as
  distinct roles. A newer file or a directory move does not grant scientific
  authority; [CONTEXT.md](../../CONTEXT.md) governs that distinction.
- Routine placement, filename, link, and index repairs are authorized as part
  of document work. Move a generated file only when its role and owner are
  clear, preserve its bytes, and update its rendering destination.
- Keep original inbox material, recorded source hashes, and historical
  before/after paths intact. Identify uncertain ownership or conflicting
  substantive decisions instead of silently choosing one. A missing external
  source is an evidence gap, not permission to reconstruct its contents.
- Update the nearest index and incoming links during moves. Mark outdated
  plans and run records with their scope and point to current owner guidance.
  Do not rewrite old results to look current.

## Automatic checks

From the repository root:

```sh
PYTHONPATH=src python3 -m invisible_research.document_governance check
```

The check covers tracked and nonignored untracked document paths, naming,
required governance entry points, local links in Markdown/QMD/Rmd prose, and protected source
hashes. It also looks for misplaced generated reports inside research analysis
and publication manuscript directories, including ignored files there. It
does not inspect private inbox contents, external datasets, or all ignored
storage. Document meaning, external-source applicability, and scientific
quality still require agent or human review.
JSON is checked as documentation only in documentation, provenance, and
publication-governance directories; application configuration and test fixtures
remain governed by their code tests.

The local pre-commit hook blocks an invalid staged snapshot; unstaged fixes
cannot make a bad staged document pass. It also reports working-tree findings,
including ignored exports, without blocking unrelated uncommitted work.
GitHub Actions runs the same check on pushes
and pull requests. Install the versioned hook in a new clone with:

```sh
git config --local core.hooksPath .githooks
```

Inspect existing hooks before installing so another workflow is not replaced.
On document creation or editing, run the working-tree check before delivery
and repair in-scope failures. Hooks and CI report violations; they do not
move files or edit prose in the background. They run on their events, not
while an idle checkout is untouched. Local checks can be bypassed explicitly;
CI failure is visible but branch protection is a separate repository setting.

## Writing and task intake

For writing, use [requirements.md](../writing/requirements.md) before drafting
and during review, even when the user does not repeat the requirements.
For an ambiguity that could materially change the answer, method, authority,
or acceptance criteria, use [task intake](../agents/task-intake.md). Routine
formatting choices do not need a requirements interview.
