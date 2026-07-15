# Archive Index

Catalog of archived code for future reference.

Format per entry:
- Path
- Source (commit/PR)
- Purpose
- Last known good (env/tooling)
- Dependencies
- Reuse likelihood
- Notes

Entries:

## Google Drive Writing Report legacy archive

- Path: `GoogleDrive:InvisibleResearch/archive/writing-report-legacy/`
- Source: selected unique inactive text sources from local-only `Writing Report/`, copied during ticket #54; exact source paths are in `docs/writing-report-archive-manifest.json`.
- Purpose: preserve superseded analysis variants, execution history, presentation support, and inactive report source without importing the full private workspace into Git.
- Last known good (env/tooling): mixed historical state; the R transcript identifies R 4.5.2 and partial package versions but no clean end-to-end run, while the Node report tooling has no retained verified run.
- Dependencies: partial R/CRAN packages documented in the Publication Compendium environment note; inactive report sources reference the archived `package.json` but exclude `node_modules` and `package-lock.json`.
- Reuse likelihood: low; retain primarily for audit and possible recovery of text sources.
- Notes: every manifest entry was copied and verified against its source SHA-256; `manifest.json` is also stored at the archive root. Original administrative and private material remains untouched under `Writing Report/` pending `docs/writing-report-human-review.md`.
