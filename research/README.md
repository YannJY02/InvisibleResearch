# Exploratory Analysis Owners

Each directory below owns one current research question or dataset experiment.
All lanes remain **Exploratory Analysis**; directory placement does not make an
analysis eligible for paper claims.

| Owner | Question or experiment |
|---|---|
| `article-metadata-conversion` | Can the ArticleInfo CSV be converted to Parquet without losing its useful schema? |
| `author-name-sampling` | What author-field patterns need inspection before name processing? |
| `dimensions-dataset-construction` | How can yearly Dimensions exports be merged and turned into analysis variables? |
| `openalex-dataset-construction` | Can Communication works be acquired and converted without row or token loss? |
| `ojs-journal-metadata` | How can PKP journal records be enriched without losing unmatched or ambiguous journals? |
| `scimago-openalex-coverage` | Which SCImago Communication sources are represented in OpenAlex? |

Set `DATA_ROOT` to the external data directory before using an owner command.
Regenerable owner outputs go under that owner's ignored `artifacts/` directory;
large shared inputs and derived datasets remain outside Git under `DATA_ROOT`.
