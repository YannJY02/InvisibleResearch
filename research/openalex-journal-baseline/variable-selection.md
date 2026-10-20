# Route B variable selection

Updated October 20, 2026. INVIS-12 prepares the independent judgments agreed in the
[meeting](../../meeting-reports/2026-10-16-variable-selection-and-conferences.md).
The user subsequently selected **Route B**, then requested the complete table.
The user has now requested selection recommendations and a complete classified
report, with explanations only for difficult choices. This remains Exploratory
Analysis, not feature encoding or modelling.

The [current report source](analysis/variable-selection-report.qmd) executes in R.
Its readable HTML is in
`artifacts/variable-selection-review-2026-10-20/report/variable-selection-report.html`.
The complete [recommendation table](analysis/variable_selection_decisions.tsv)
assigns **27 yes, 7 maybe and 46 no** to the original 80 columns. These count
information-bearing source columns, not final encoded design-matrix columns.

The user explicitly retained `is_core`, `listed_in`, `topic_share`,
`host_organization_lineage`, `societies`, both Scopus outcomes and `created_date`
on October 20. These decisions replace the earlier 19/12/49 proposal.
`created_date` is when OpenAlex added the record, not when the journal was founded;
it is retained without treating it as journal age or evidence of authority.
See [OpenAlex Source attributes](https://help.openalex.org/data/sources/attributes/).

## Workbook

The local Excel file is
`artifacts/variable-selection-review-2026-10-20/outputs/01a1448c-26bc-7f42-b0ab-7515259cf126/route-b-variable-selection.xlsx`.

- `Jinyi` and `Saurabh` contain the same 80 fields in the delivered CSV's order.
  Each row has an explanation, real shortened example with its Source ID,
  value type, null/missing fraction, empty-container fraction and review considerations.
- `Jinyi` now contains an explicitly labeled AI-assisted proposal requested by
  the researcher: 27 yes, 7 maybe and 46 no. Short notes cover the seven open choices and
  a correction about `created_date`; ordinary choices have no reason entered.
- `Saurabh` retains its blank choices and reasons. Its judgment cells and formulas are
  checked against the unmodified October 16 workbook; only shared instructions
  in A4, A5 and C8 change to ask whether to retain a field for the study. The proposal is not a
  supervisor judgment or an already agreed selection.
- `Guide` defines denominators, provenance and the observed topic hierarchy.
  `Keep?` includes both predictors and outcomes. The Yes group contains 25 candidate
  predictor fields and two Scopus outcomes. Outcomes and other Scopus matching
  evidence remain outside predictor inputs. The TSV `role` column records this distinction.

The workbook and profiles are local generated outputs; Git carries the field
dictionary and builders. No collaborator message or new SURFdrive upload was sent.
This delivers the researcher-side proposal for human review. Supervisor judgment
and discussion of disagreements are still outstanding; the whole workflow is not Done.

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

No topic encoding was executed. Subfield presence is the proposed first option
to discuss, not an accepted final hierarchy choice. `topic_share` is the journal's
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

To reproduce the October 20 recommendations and rendered report:

```sh
python3 research/openalex-journal-baseline/analysis/review_variable_selection.py
node research/openalex-journal-baseline/analysis/review_variable_selection.mjs
quarto render research/openalex-journal-baseline/analysis/variable-selection-report.qmd \
  --output-dir ../artifacts/variable-selection-review-2026-10-20/report
```

The workbook creation and editing scripts use the bundled `@oai/artifact-tool` runtime; set
`ARTIFACT_NODE_MODULES` if that runtime's package directory differs. Its dependency
symlink, profile, workbook, previews and validation records remain in the named
owner-local artifact directory. Source meanings and review notes are maintained in
[the field dictionary](analysis/variable_selection_fields.tsv).

October 16 verification covered the initial blank templates. October 20 verification
covers exact 80-column classification, 27/7/46 reconciliation, ordinary reasons
remaining blank, 80 researcher recommendations, zero supervisor judgments, preservation
of the supervisor judgments, noninstruction cells and exported controls, and the rerendered R report and
affected spreadsheet views. The raw CSV hash remains identical. No model was run;
the recommendations still require human review.
