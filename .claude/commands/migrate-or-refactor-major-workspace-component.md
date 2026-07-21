---
name: migrate-or-refactor-major-workspace-component
description: Workflow command scaffold for migrate-or-refactor-major-workspace-component in InvisibleResearch.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /migrate-or-refactor-major-workspace-component

Use this workflow when working on **migrate-or-refactor-major-workspace-component** in `InvisibleResearch`.

## Goal

Migrates or refactors a major workspace component (e.g., shared capabilities, exploratory analysis, publication compendium) across code, documentation, notebooks, and tests.

## Common Files

- `README.md`
- `data/README.md`
- `docs/*.md`
- `notebooks/**/*.ipynb`
- `research/**/README.md`
- `research/**/*.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Update or add multiple README.md files across root, data, docs, research, and submodules.
- Modify or add scripts in scripts/ or src/invisible_research/ subdirectories.
- Update or add Jupyter notebooks in notebooks/ or research/*/notebooks/.
- Update or add documentation in docs/ and research/*/README.md.
- Update or add test files in tests/.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.