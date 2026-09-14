# Repository guidance

## Context and workflows

- Read supporting docs when relevant to the task:
  - Project vocabulary or architectural decisions: [domain guidance](docs/agents/domain.md).
  - Project and issue work: [Plane workflow](docs/agents/issue-tracker.md) and [project management](docs/operations/project-management.md). Read the linked Plane task and source updates before starting, sync meaningful progress and blockers as they occur, and record verified delivery after commit/push. This applies to future tasks in this workspace. The upstream GitHub issue collection is read-only; do not synchronize or modify it.
  - Triage: [canonical labels](docs/agents/triage-labels.md): `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
  - Creating, importing, or reorganizing documents: [document governance](docs/governance/document-governance.md). Choose the owner, role, and filename before writing; update the existing canonical document and links where appropriate.
  - Writing or revising formal prose: [writing requirements](docs/writing/requirements.md) and the target's requirements index. Apply applicable source-backed requirements without waiting for the user to repeat them.
  - Material gaps in a prompt or conflicting requirements: [task intake and MATT routing](docs/agents/task-intake.md). Investigate facts, suggest a resolution, and clarify consequential decisions; proceed on routine choices.

## Academic analysis code

In `research/**`, `papers/**/analysis/**`, QMD/Rmd files, and notebooks:

- Prioritize methodological clarity, readability, and reproducibility. Reuse established repository, R, and Quarto patterns; keep the implementation focused on the research question.
- Treat working analysis code as potentially precision-tuned. Make the smallest justified change, preserve unrelated structure and wording, and explain methodological, reproducibility, correctness, or maintenance reasons for rewrites.
- Add abstractions, infrastructure, or defensive code only when justified by the method or data risk. Retain proportionate safeguards at external-input, data-loss, security, and other trust boundaries, including shared `src/**` code, data-writing code, and full-cohort pipelines.
- Put every pipeline's generated outputs, caches, intermediate files, reports, and profiles in its own named subdirectory beneath the nearest ignored `artifacts/` directory. Keep outputs out of the shared artifact root and other pipelines' directories.

## Completion

- Complete the requested deliverable and verification appropriate to its risk. When execution or rendering is part of the task, inspect the result and fix in-scope failures before handing it back.
- After document changes, run `PYTHONPATH=src python3 -m invisible_research.document_governance check` and fix in-scope placement, naming, or link failures. The pre-commit hook and CI check the committed document snapshot automatically.
- Stage only the task's changes, commit, and push the current branch. Preserve unrelated existing changes. Report any blocker, including a failed commit or push.
