# Repository guidance

## Context and workflows

- Read supporting docs when relevant to the task:
  - Project vocabulary or architectural decisions: [domain guidance](docs/agents/domain.md).
  - Issue work: [GitHub workflow](docs/agents/issue-tracker.md). External pull requests are not a triage request surface.
  - Triage: [canonical labels](docs/agents/triage-labels.md): `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.

## Academic analysis code

In `research/**`, `papers/**/analysis/**`, QMD/Rmd files, and notebooks:

- Prioritize methodological clarity, readability, and reproducibility. Reuse established repository, R, and Quarto patterns; keep the implementation focused on the research question.
- Treat working analysis code as potentially precision-tuned. Make the smallest justified change, preserve unrelated structure and wording, and explain methodological, reproducibility, correctness, or maintenance reasons for rewrites.
- Add abstractions, infrastructure, or defensive code only when justified by the method or data risk. Retain proportionate safeguards at external-input, data-loss, security, and other trust boundaries, including shared `src/**` code, data-writing code, and full-cohort pipelines.
- Put every pipeline's generated outputs, caches, intermediate files, reports, and profiles in its own named subdirectory beneath the nearest ignored `artifacts/` directory. Keep outputs out of the shared artifact root and other pipelines' directories.

## Completion

- Complete the requested deliverable and verification appropriate to its risk. When execution or rendering is part of the task, inspect the result and fix in-scope failures before handing it back.
- Stage only the task's changes, commit, and push the current branch. Preserve unrelated existing changes. Report any blocker, including a failed commit or push.
