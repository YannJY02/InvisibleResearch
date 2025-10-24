# Unused Code Handling Policy

This repository maintains a clear, simple workflow to handle unused but potentially reusable code.

## Decisions
- An `archive/` directory exists at repo root for short-to-mid term storage.
- No default retention period; maintainers decide deletions case-by-case.
- No special handling for notebooks; `notebooks/` will be removed after migrations.
- Flow: Maintainer flags unused code; assistant extracts reusable parts into `scripts/utils/`; assistant decides archive vs delete for remainder; indexes updated.

## Workflow
1. Maintainer identifies unused code and shares paths.
2. Assistant evaluates and extracts reusable utilities into `scripts/utils/`.
3. Remaining code is either placed in `archive/` (if potentially useful soon) or removed (relying on Git history).
4. Update indexes: `archive.md` and `utils.md` at repo root.
5. Open/Update GitHub issues as needed with labels `archive`, `deprecation`, `tech-debt`.
6. All docs in English; follow Conventional Commits; never commit secrets.

## Index Requirements
- `archive.md`: path, source (commit/PR), purpose, last known good env, dependencies, reuse likelihood, notes.
- `utils.md`: list reusable modules under `scripts/utils/` with 1-2 line descriptions.

## Quality Gates
- Keep utilities minimal, well-named, and documented.
- Prefer deletion plus Git history over indefinite archiving.
- Add light tests if a utility becomes widely used.

