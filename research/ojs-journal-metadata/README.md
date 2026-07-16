# OJS Journal Metadata Enrichment

This owner investigates journal-level enrichment for PKP Beacon records. All
work here remains **Exploratory Analysis**.

## PKP input decision

Use the original CSV behind `beacon.tab` in version 6.0 of [Details of
publications using software by the Public Knowledge
Project](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OCZNVY):

- Dataset DOI: `10.7910/DVN/OCZNVY`
- Released: `2025-11-21`
- Dataverse file ID: `13173372`
- Original download: [beacon.csv](https://dataverse.harvard.edu/api/access/datafile/13173372?format=original)
- MD5: `9f43fa051c7ed1cc45d8592593542011`
- V6.0 baseline: 87,170 rows and 31 columns; 86,282 rows have
  `application == "ojs"`

Pin this Artifact Version for the first pipeline. Do not silently substitute a
new annual Dataverse release.

## Provenance and scope

The upstream [OJS Journal Metadata task](https://github.com/invisibleinfo/invisible-research/issues/6)
names this Dataverse dataset as the PKP journal-level source. PKP describes the
dataset as Beacon and OAI-PMH-derived information about known public OJS, OMP,
and OPS installations; it is not a census of every journal. The accompanying
[Data Dictionary and Methodology Notes](https://dataverse.harvard.edu/api/access/datafile/5376705)
documents heuristic deduplication and country inference, plus exclusions for
unresolvable hosts, apparent test installations, and IP-address-hosted sites.
The paper connected to the dataset describes Beacon coverage and the older
2020 study cohort ([Khanna et al., 2022](https://doi.org/10.1162/qss_a_00228));
those older counts are not the V6.0 input baseline.

Harvard Dataverse ingests the source as `beacon.tab`, but its [Data Access API
documentation](https://guides.dataverse.org/en/latest/api/dataaccess.html)
states that `format=original` returns the deposited representation. For this
file that representation is `beacon.csv`. Use a CSV parser with quoted
multiline-field support; an ISSN cell may contain more than one line.

## Actual V6.0 schema

The file header, rather than the 2021 PDF alone, is authoritative for parsing:

```text
oai_url, application, version, admin_email, earliest_datestamp,
repository_name, set_spec, context_name, stats_id, total_record_count, issn,
country_marc, country_issn, country_doaj, country_tld, country_ip,
country_consolidated, best_doaj_url, last_completed_update, first_beacon,
last_beacon, last_oai_response, unresponsive_endpoint, unresponsive_context,
record_count_2020, record_count_2021, record_count_2022, record_count_2023,
record_count_2024, record_count_2025, region
```

The PDF predates V6.0 schema changes: it describes `journal_url` and `domain`,
which are absent, while several current country, DOAJ, region, and annual-count
fields are not documented there.

## Row identity

The producer defines a row by the tuple:

```text
(oai_url, repository_name, set_spec)
```

V6.0 contains no duplicate tuples. `repository_name` is blank for 24,454 OJS
rows, so blank must remain a valid tuple value rather than becoming a rejected
record. `stats_id` identifies an installation and is intentionally repeated
when one installation hosts multiple journals; ISSN is also not a row key.

## Coverage and quality profile

The following figures come from a read-only profile of the pinned original CSV
on 2026-07-16:

| Field or check | OJS result | Interpretation |
|---|---:|---|
| Rows | 86,282 | First-pipeline cohort after filtering the full file |
| `oai_url`, `set_spec`, `context_name` | 100% present | Required identity/display inputs |
| `repository_name` | 61,828 (71.7%) | Nullable part of the producer identity tuple |
| `stats_id` | 81,368 (94.3%) | Installation identifier, not journal identifier |
| `issn` | 64,773 (75.1%) | 21,509 journals need to remain unmatched or use a later fallback |
| `country_consolidated` | 78,206 (90.6%) | Inferred value; not authoritative publisher location |
| `best_doaj_url` | 6,226 (7.2%) | Sparse supporting identifier |

Across the full file, all 64,785 non-empty ISSN cells contained only
checksum-valid `NNNN-NNNN`/`NNNN-NNNX` tokens; 29,038 rows contained multiple
newline-separated ISSNs. All annual counts were non-negative integers and all
non-empty documented timestamp fields parsed successfully. These observations
describe V6.0, not guarantees for later releases.

Country fields are inferred in priority order from ISSN/MARC, top-level domain,
and IP geolocation. The methodology warns that this can reflect hosting-server
location. Deduplication is heuristic, and repeated values in individual fields
may remain. Unresponsive rows are present in `beacon.csv`; the stricter
reachability and five-items-per-year rules documented for PKP's map do not
define this pipeline's input cohort.

## Minimum runnable input contract

1. Fetch the pinned original file, verify the MD5, and keep it under
   `DATA_ROOT`; do not commit the dataset.
2. Parse UTF-8 CSV with quoted multiline fields. Require at least
   `oai_url`, `application`, `repository_name`, `set_spec`, `context_name`,
   `stats_id`, `issn`, `last_beacon`, `last_oai_response`,
   `unresponsive_endpoint`, and `unresponsive_context`; pass through other
   source columns.
3. Filter `application` case-insensitively to `ojs`. Require non-empty
   `oai_url`, `set_spec`, and `context_name`. Allow blank `repository_name`,
   `stats_id`, ISSN, and country fields.
4. Assert uniqueness of `(oai_url, repository_name, set_spec)` after preserving
   blanks as empty strings. Do not deduplicate on ISSN or `stats_id`.
5. Split ISSNs on line breaks, normalize case and hyphenation, and validate the
   ISSN checksum. Invalid or absent ISSNs are match-status values, not reasons
   to drop a journal.
6. Enrichment must be a left join from the 86,282-row OJS cohort, preserving
   unmatched and unresponsive rows and recording match route and ambiguity.
7. Keep `admin_email` in the restricted raw input only; exclude it from joined
   artifacts and reports unless a later task establishes a specific need.
8. Treat a new Dataverse release as a new Artifact Version: re-profile its
   schema, row count, identity uniqueness, identifier coverage, and checksum
   before changing the pinned input.

This contract is sufficient for the OpenAlex Sources investigation. It does not
choose fallback title matching, define an active-journal analysis cohort, or
implement the enrichment pipeline.
