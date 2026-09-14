# Document Governance Verification

Date: 2026-09-14. Scope: InvisibleResearch only. This record documents the
governance installation and relocation checks; it is not research execution
evidence or a scientific designation.

## Relocation audit

| Previous path | Current path |
|---|---|
| `docs/ARTICLEINFO_DATABASE.md` | `docs/data/articleinfo-database.md` |
| `docs/DATA_SCRIPT_MAPPING.md` | `docs/data/data-script-mapping.md` |
| `docs/TableRelation.png` | `docs/data/table-relations.png` |
| `docs/SECURITY_GUIDE.md` | `docs/operations/security-guide.md` |
| `docs/unused-code-policy.md` | `docs/governance/unused-code-policy.md` |
| `docs/academic-repository-structure-research.md` | `docs/governance/repository-structure-research.md` |
| `docs/artifact-authority-inventory.md` | `docs/governance/artifact-authority-inventory.md` |
| `docs/data-to-claim-dependency-graph.md` | `docs/governance/data-to-claim-dependency-graph.md` |
| `docs/literature-evidence-note-spec.md` | `docs/writing/literature-evidence-note-spec.md` |
| `docs/hybrid-workspace-migration.md` | `docs/history/hybrid-workspace-migration.md` |
| `docs/writing-report-human-review.md` | `docs/history/writing-report-human-review.md` |
| `docs/data-lifecycle-cutover.json` | `docs/history/data-lifecycle-cutover.json` |
| `docs/writing-report-archive-manifest.json` | `docs/history/writing-report-archive-manifest.json` |
| `archive.md` | `docs/history/archive-index.md` |
| `utils.md` | `docs/operations/utility-index.md` |
| `docs/testing/ojs-journal-enrichment-qmd.tdd.md` | `docs/testing/ojs-journal-enrichment-qmd-tdd.md` |
| `docs/README.md` | `docs/data/pkp-database-schema.md` |

The former database README also contained Dimensions workflow notes. They
were retained in `docs/history/dimensions-workflow-notes.md`, explicitly marked
as historical, while `docs/README.md` became the role-based navigation entry.
Old OJS plans and verification records now identify their historical scope
and point to current owner instructions. Incoming local links were updated.

## Generated and protected material

- The meeting HTML moved to the ignored
  `meeting-reports/artifacts/2026-07-16-ojs-journal-metadata/` directory.
- The source-adjacent simple-version HTML and RPubs deployment metadata moved
  together to `research/ojs-journal-metadata/artifacts/ojs_journal_enrichment_simple_ver/source-adjacent-2026-09-14/`.
  That HTML differed from the report already in `rendered/`; both were retained.
- Moved exports and deployment metadata were compared byte-for-byte by SHA-256.
  No remote publication was changed. The new `render_simple.sh` places future
  HTML under the existing pipeline artifact directory.
- The paper analysis source and both historical JSON manifests retained their
  SHA-256 values. Original inbox files, external archives, and data manifests
  were not edited. Protected hashes are recorded in the machine-readable rules.

## Verification and limits

- The working-tree document check passed for placement, naming, local links,
  required entries, protected hashes, and bounded generated-output discovery.
- Disposable-repository tests exercise both valid and invalid documents,
  staged versus unstaged content and rules, reference links, preserved bytes,
  external symlinks, and ignored render/deployment-state detection.
- A tiny Markdown fixture was rendered with installed Quarto; the generated
  HTML appeared only in the requested ignored artifact directory and contained
  the expected heading. This validates output routing without rerunning the
  research pipelines or contacting their data APIs.
- Publication-compendium and workspace-boundary regression tests were run.
  The prior inventory test was updated to recognize the already established
  Literature Evidence Note role while retaining its strict core source set.
- The PR template now asks for relevant checks actually performed, instead of
  requiring every documentation change to claim research-wide validation.

School and venue writing rules are unconfirmed in this project; see
[writing requirements](../writing/requirements.md). Historical template names
alone were not promoted to current requirements. Semantic classification and
requirements applicability remain review tasks; the automatic check cannot
prove either. Remote CI run status is available in GitHub Actions rather than
being inferred from this local record.
