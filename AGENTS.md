## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues. External pull requests are not a triage request surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the canonical `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix` vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context layout. See `docs/agents/domain.md`.

### Task completion

After completing a task or ticket, commit the task's changes and push the current branch. Stage only files related to that task; never include unrelated existing changes. If the commit or push fails, report the reason.
