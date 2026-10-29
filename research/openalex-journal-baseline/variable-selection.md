# Route B variable selection

The October 29 [field-preparation report](analysis/feature-preparation-report.qmd)
answers the meeting questions in English, with executed verification code and results.
It gives explicit retain/exclude/defer recommendations, with highlighted decisions and
next actions for language mapping, publication medium, population and observation date.
It checks the frozen cohort against the agreed labels without changing those labels.
The revised investigation traces the annual APC import to Butler / ScholCommLab and
verifies all 19 preprint flags against the original API responses; their coexistence
with `type=journal` is inherited from OpenAlex, not introduced by the local join.
The new registry audit includes short unrecognized language labels; a matched Crossref
example verifies that medium labels can be retrieved but cannot be decoded from ISSN digits.
The report recommends deferring a medium predictor pending a coverage audit and excluding
`created_date` from the first substantive feature set until its meaning is established.
These recommendations do not replace the shared decisions or select a final model representation.
Its version caveat also qualifies the older `created_date` explanation below:
current documentation and the preserved aggregation code differ, so the frozen
field's exact generation rule remains unverified. Neither supports journal age.

Reproduce its actual R execution and local HTML from the repository root:

```sh
quarto render research/openalex-journal-baseline/analysis/feature-preparation-report.qmd \
  --output-dir ../artifacts/feature-preparation/report
```

The rendered report, execution receipt and R session record are under this owner's
ignored `artifacts/feature-preparation/`. Official-source links and the distinction
between current documentation and frozen-data semantics are in the report.

## Agreed labels synchronized October 27, 2026

The user supplied the [shared Google Sheet](https://docs.google.com/spreadsheets/d/1SsHBfflnwDjt9yDSHdy9KFbsx5QkG0kPCEC5TJxq02Q/edit) as the version agreed at the previous meeting. On October 27, the `Labels` tab was read and exported locally. Its 80 field names and order match the earlier Route B decision table; the agreed column has **40 yes and 40 no**, including both Scopus outcome fields. A yes retains information for consideration; it does not make an outcome a predictor or define its final encoding.

The exact displayed cell values, including the four notes in the source's unnamed fourth column, are preserved in [agreed-variable-labels.csv](analysis/agreed-variable-labels.csv). The exported workbook is local at `artifacts/agreed-variable-labels-2026-10-27/route-b-variable-labels.xlsx` (SHA-256 `0f4c1a2bdf5f9ac8b89c65200009b214fe26153aba6c9d624ba819a7beae8526`). Cell values were compared with the live `Labels` range, and rows 101–1000 were empty. The Google Drive metadata returned a modified time of October 20, 2026; that timestamp does not establish the actual meeting date or explain the source's revision history.

The source's `Jinyi's label` column has 34 yes, 4 maybe and 42 no; seven of those entries differ from the earlier local researcher-side proposal. The agreed column differs from that earlier proposal on 14 fields. Both are preserved rather than reconciled by assumption. The older workbook, proposal and report below remain historical records, not the current agreed labels. Field semantics, missing-value handling, final numeric representation and outcome selection remain separate decisions.

The user also supplied the supervisor's [BERTopic documentation](https://maartengr.github.io/BERTopic/index.html) for feature-engineering preparation. It describes a modular text-topic modelling workflow; receiving the link does not establish a selected model or authorize an analysis run.

## Earlier researcher-side proposal

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
