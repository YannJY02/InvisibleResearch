## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues. External pull requests are not a triage request surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the canonical `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix` vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context layout. See `docs/agents/domain.md`.

### Academic analysis code

For future code generation in `research/**`, `papers/**/analysis/**`, QMD/Rmd files, and notebooks, write Academic Analysis Code: prioritize methodological clarity, readability, and reproducibility; reuse established repository, R, and Quarto patterns; and implement the smallest code that answers the research question. Do not add speculative abstractions, custom infrastructure, or production-grade defensive code unless the method or data risk requires it. Keep proportionate checks at external-input, data-loss, security, and other trust boundaries. Shared code in `src/**`, data-writing code, and full-cohort pipelines retain safeguards appropriate to their role.

### Task completion

After completing a task or ticket, commit the task's changes and push the current branch. Stage only files related to that task; never include unrelated existing changes. If the commit or push fails, report the reason.
