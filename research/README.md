# Exploratory Analysis Owners

Each directory below owns one current research question or dataset experiment.
All lanes remain **Exploratory Analysis**; directory placement does not make an
analysis eligible for paper claims.

| Owner | Question or experiment |
|---|---|
| `article-metadata-conversion` | Can the ArticleInfo CSV be converted to Parquet without losing its useful schema? |
| `author-name-sampling` | What author-field patterns need inspection before name processing? |
| `dimensions-dataset-construction` | How can yearly Dimensions exports be merged and turned into analysis variables? |
| [feature-selection-explainer](feature-selection-explainer/README.md) | How do Boruta selection and SHAP attribution differ? Interactive teaching examples only. |
| `openalex-dataset-construction` | Can Communication works be acquired and converted without row or token loss? |
| [openalex-journal-baseline](openalex-journal-baseline/README.md) | Can all journal-type Sources form a reproducible baseline for index matching? |
| `ojs-journal-metadata` | How can PKP journal records be enriched without losing unmatched or ambiguous journals? |
| `scimago-openalex-coverage` | Which SCImago Communication sources are represented in OpenAlex? |

Teaching demonstrations are separate from empirical research:
[feature engineering](feature-engineering-explainer/README.md) uses synthetic
apartments to explain transformations interactively.

Set `DATA_ROOT` to the external data directory before using an owner command.
Regenerable owner outputs go under that owner's ignored `artifacts/` directory;
large shared inputs and derived datasets remain outside Git under `DATA_ROOT`.
