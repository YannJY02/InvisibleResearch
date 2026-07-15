# Unused Code Handling Policy

This repository maintains a clear, simple workflow to handle unused but potentially reusable code.

## Decisions
- Archived bytes live outside Git and are indexed by `archive.md`.
- No default retention period; maintainers decide deletions case-by-case.
- Notebook adapters live with their research owner under `research/*/notebooks/`.
- Flow: Maintainer flags unused code; assistant extracts reusable parts into the owning package under `src/`; assistant decides external archive vs delete for the remainder; indexes are updated.

## Workflow
1. Maintainer identifies unused code and shares paths.
2. Assistant evaluates and extracts reusable utilities into the owning package under `src/`.
3. Remaining code is either copied to the external archive or removed, relying on Git history for tracked content.
4. Update indexes: `archive.md` and `utils.md` at repo root.
5. Open/Update GitHub issues as needed with labels `archive`, `deprecation`, `tech-debt`.
6. All docs in English; follow Conventional Commits; never commit secrets.

## Index Requirements
- `archive.md`: path, source (commit/PR), purpose, last known good env, dependencies, reuse likelihood, notes.
- `utils.md`: list reusable modules under `src/invisible_research/` with 1-2 line descriptions.

## Quality Gates
- Keep utilities minimal, well-named, and documented.
- Prefer deletion plus Git history over indefinite archiving.
- Add light tests if a utility becomes widely used.
