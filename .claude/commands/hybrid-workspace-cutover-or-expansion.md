---
name: hybrid-workspace-cutover-or-expansion
description: Workflow command scaffold for hybrid-workspace-cutover-or-expansion in InvisibleResearch.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /hybrid-workspace-cutover-or-expansion

Use this workflow when working on **hybrid-workspace-cutover-or-expansion** in `InvisibleResearch`.

## Goal

Implements or expands a hybrid workspace seam, including updating code, scripts, documentation, and tests to support the new workspace structure.

## Common Files

- `.env.example`
- `config/env.template`
- `config/settings.py`
- `data/README.md`
- `docs/*.md`
- `scripts/02_extraction/*.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Update or add configuration files (e.g., .env.example, config/env.template, config/settings.py).
- Update or add documentation in docs/ and data/README.md.
- Modify or add scripts in scripts/02_extraction/ and scripts/05_validation/.
- Update or add code in src/invisible_research/ (especially acquisition, processing, validation modules).
- Update or add test files in tests/.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.