# Writing Report Human Review List

The Publication Compendium migration copied selected active sources and
verified archival sources without modifying the original local-only
`Writing Report/` tree. The following administrative, private, copyrighted, or
ambiguous material is left untouched pending human review:

| Local path | Why human review is required |
|---|---|
| `Writing Report/Report/Internship Report.docx` | Administrative report with potentially private content. |
| `Writing Report/Support Doc/chat history/history.png` | Raw chat screenshot; do not normalize or relocate automatically. |
| `Writing Report/Support Doc/template/` | Administrative templates and Office documents; retention is not a research decision. |
| `Writing Report/Slides/material/*.pdf` | Generated or potentially copyrighted paper/presentation bytes; duplicate copies also exist under `Support Doc/output/`. |
| `Writing Report/Support Doc/output/` | Duplicate generated PDFs and OS metadata. |
| `Writing Report/Report/package-lock.json` | Regenerable lock file for inactive report tooling. |
| `Writing Report/Report/node_modules/` | Regenerable dependency installation. |
| all `~$*.docx` and `.DS_Store` files | Temporary lock files and OS metadata. |

No item on this list has been deleted, moved, renamed, or scientifically
authorized by the migration.
