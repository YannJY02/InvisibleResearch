# Route B variable selection

Updated October 16, 2026. INVIS-12 prepares the independent judgments agreed in the
[meeting](../../meeting-reports/2026-10-16-variable-selection-and-conferences.md).
The user subsequently selected **Route B**, then requested the complete table.
This is workbook preparation for Exploratory Analysis, not feature encoding or modelling.

## Workbook

The local Excel file is
`artifacts/variable-selection-2026-10-16/outputs/01a1448c-26bc-7f42-b0ab-7515259cf126/route-b-variable-selection.xlsx`.

- `Jinyi` and `Saurabh` contain the same 80 fields in the delivered CSV's order.
  Each row has an explanation, real shortened example with its Source ID,
  value type, null/missing fraction, empty-container fraction and review considerations.
- Both `Predictor?` and reason columns start blank. The dropdown offers
  `yes`, `no`, `maybe`; the completed-field counter counts those choices.
  Reviewers complete their own sheets before comparing judgments.
- `Guide` defines denominators, provenance and the observed topic hierarchy.
  Candidate outcomes and Scopus matching evidence remain outside predictor inputs.
  The final outcome choice is separate from the predictor judgments.

The workbook and profiles are local generated outputs; Git carries the field
dictionary and builders. No collaborator message or new SURFdrive upload was sent.
INVIS-12 remains in progress because both independent judgments and their discussion
are still outstanding.

## Input and observed scope

The input is the unchanged [Route B delivery](dual-route-delivery.md):
`openalex-route-b-api-2026-10-01-journals.csv.gz`, **207,602 rows × 80 columns**.
Compressed SHA-256:
`46376a4fb026936c221c466ecf0fd3c2ab373eed1722ed7bad69a88ca4715724`.

The full CSV was streamed to check column order, row widths, unique row IDs,
missing/empty buckets, and topic IDs and hierarchy. Each field's bucket counts
reconcile to 207,602 rows. Null/missing includes raw `\M`, `\N`, and an empty
string; `[]` and `{}` are counted separately. Zero and false remain populated.
API attribute types come from the delivered Source-object type inventory;
other types describe observed CSV tokens, not inferred substantive meanings.

`topics` and `topic_share` each have **11,852 empty lists** and **195,750 nonempty
lists**. Each list independently contains up to 25 entries. Each has 4,516 topic
IDs, 252 subfield IDs, 26 field IDs and 4 domain IDs across the observed cohort.
No observed ID has conflicting names or multiple immediate parents. The two lists
can contain different topics; their union reaches 49 IDs in a row. These are
returned-list observations, not an exhaustive classification of every Work.

No topic hierarchy or encoding was selected. `topic_share` is the journal's
contribution to a topic across all primary sources, not that topic's share within
the journal. The [existing method discussion](model-data-structure.md#53-三种数量不能混用)
records the denominator. Current [Source attributes](https://help.openalex.org/data/sources/attributes/)
and [topic documentation](https://help.openalex.org/data/topics/) were checked on
October 16; live definitions do not silently replace the frozen October 1 data.

## Reproduce

Run from the repository root with the already delivered input present:

```sh
python3 research/openalex-journal-baseline/analysis/profile_variable_selection.py
node research/openalex-journal-baseline/analysis/build_variable_selection.mjs
```

The workbook builder uses the bundled `@oai/artifact-tool` runtime; set
`ARTIFACT_NODE_MODULES` if that runtime's package directory differs. Its dependency
symlink, profile, workbook, previews and validation records remain in the named
owner-local artifact directory. Source meanings and review notes are maintained in
[the field dictionary](analysis/variable_selection_fields.tsv).

Verification includes exact coverage of the source's 80 columns, identical review
templates, blank judgments and reasons, dropdown and frozen-pane preservation in
the exported XLSX, progress-counter checks for three choices and restored blanks,
and visual inspection of the three sheets and the detailed topic rows. No model
was run and no final human variable judgments were assigned.
