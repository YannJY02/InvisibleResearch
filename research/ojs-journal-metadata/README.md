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

## OpenAlex Sources enrichment decision

This decision was checked against the current OpenAlex documentation and API on
2026-07-16. OpenAlex [`Sources`](https://developers.openalex.org/api-reference/sources)
include journals, repositories, conferences, and other hosting venues, so a
Source is a candidate journal record until its `type` is checked.

### Fields to retain

The first joined artifact should flatten the following analysis-ready fields
and keep the selected API response as an ignored raw cache so nested fields can
be revisited without another request:

| Purpose | OpenAlex fields |
|---|---|
| Identity and joining | `id`, `display_name`, `alternate_titles`, `issn_l`, `issn`, `type`, `ids` |
| Host and location | `host_organization`, `host_organization_name`, `host_organization_lineage`, `country_code`, `homepage_url` |
| Access and indexing | `is_oa`, `is_in_doaj`, `is_ojs`, `is_core`, `is_high_oa_rate`, `is_high_oa_rate_since_year`, `is_in_doaj_since_year`, `is_in_scielo`, `oa_flip_year` |
| Scale and impact | `works_count`, `oa_works_count`, `cited_by_count`, `summary_stats`, `first_publication_year`, `last_publication_year`, `counts_by_year` |
| APC and topical context | `apc_prices`, `apc_usd`, `topics`, `topic_share`, `societies` |
| Refresh provenance | `created_date`, `updated_date`, `works_api_url` plus the pipeline retrieval timestamp |

Use [`select`](https://developers.openalex.org/guides/selecting-fields) to limit
responses, but select whole top-level objects such as `summary_stats` and
`counts_by_year`; OpenAlex does not allow selecting their nested members. Keep
nested lists in the raw cache and flatten only the scalar fields needed by the
first coverage report. Missing keys and nulls remain missing rather than being
coerced to zero or `false`.

These fields have different meanings and dates. `country_code` is OpenAlex's
source association and must not overwrite PKP's inferred
`country_consolidated`. Counts and citation metrics are current OpenAlex
aggregates, not values as of the 2025 PKP release. Likewise, `is_ojs`, `is_oa`,
and `is_in_doaj` are enrichment variables, not join requirements or validation
of PKP provenance.

### Matching routes

1. Reuse the existing ISSN normalization shape in
   `research/scimago-openalex-coverage/analysis/coverage.py`, adding the checksum
   enforcement already required by the input contract. Deduplicate valid input
   tokens before any requests.
2. Make exact ISSN the mandatory route. Query
   `GET /sources?filter=issn:<issn>|...&per_page=100` in batches of at most 100
   tokens and join locally against every returned Source's full `issn` array.
   Do not add `type:journal` to the request: retain non-journal candidates so a
   type mismatch is visible rather than silently becoming "not found".
3. Treat all candidates across all ISSNs on one PKP row as a set. One journal
   Source ID is a unique ISSN match; zero is unresolved; more than one Source ID
   or conflicting IDs from different input ISSNs is ambiguous. Record every
   input token, matched token, candidate ID, candidate type, and rejection
   reason. The documented singleton form
   `GET /sources/issn:<issn>` is useful for spot checks and recovery, but not as
   the bulk route.
4. Title fallback is optional and budget-bounded, never implicit. For an
   unresolved row, call `GET /sources?search=<context_name>&filter=type:journal`
   only when the run was given an explicit title-search limit. Compare the
   input title with `display_name` and `alternate_titles` using the repository's
   existing punctuation/whitespace-insensitive title normalization. Accept no
   fuzzy relevance result automatically.
5. A title search with one normalized-exact candidate in the complete returned
   result set is a **provisional title candidate**, not an ISSN-equivalent
   match. Record hostname and country agreement as review evidence. Zero exact
   candidates is unresolved; multiple exact candidates is ambiguous. If the
   API reports more results than the run is allowed to retrieve, classify the
   row as not fully searched rather than claiming uniqueness.

The current input has 93,589 distinct ISSN tokens across 64,773 OJS rows. The
ISSN stage therefore needs at most 936 list/filter calls at 100 tokens per
batch, approximately USD 0.0936 at the documented list price. In contrast,
searching all 21,509 OJS rows with missing ISSNs would cost at least USD 21.509
before searching ISSN-not-found rows, so an unbounded title fallback is not a
runnable default.

### Live sample

The deterministic sample was the first 12 OJS rows with non-empty ISSNs in the
pinned V6.0 CSV: 22 distinct tokens produced 11 Sources in one batch filter.
Eleven PKP rows had a unique Source and both ISSNs on multi-ISSN rows converged
on the same Source. `Sintesa: Jurnal Ilmu Pendidikan` (`2085-7063`) had no
Source; the prefixed singleton route returned HTTP 404 and the title search
returned zero results.

Three of the 11 unique ISSN matches reported `is_ojs=false`, including Kuwait
Journal of Science, which shows why `is_ojs` cannot be a match predicate. The
missing-ISSN title checks also exposed the fallback boundary:

| PKP title | Search results | Normalized-exact candidates | Outcome |
|---|---:|---:|---|
| `Journal of Polymer & Composites` | 2 | 1 | provisional title candidate |
| `Lekovite Sirovine` | 1 | 1 | provisional title candidate |
| `Journal of Public Health` | 318 | at least 4 in the first 100 | ambiguous; do not auto-match |

This is a route check, not a coverage estimate for all 86,282 OJS rows.

### API and coverage contract

Require `OPENALEX_API_KEY` for the full run, never log it, use a 30-second
timeout, and follow the current [authentication and pricing](https://developers.openalex.org/api-reference/authentication)
rules. OpenAlex allows 100 OR values per filter, `per_page=100`, and at most 100
requests per second. Record response cost and rate-limit headers. Follow 301
redirects; treat 404 as not found; retry 429 and 5xx responses with bounded
exponential backoff as described by the [error guidance](https://developers.openalex.org/api-reference/errors).
If any later route pages beyond 10,000 results, use the documented
[cursor protocol](https://developers.openalex.org/guides/page-through-results)
rather than basic page numbers.

The joined artifact must retain all 86,282 PKP OJS rows and add separate
provenance columns rather than one overloaded match flag:

- `identifier_status`: valid, missing, or invalid input ISSN
- `match_route`: ISSN, title, or none
- `match_status`: unique, provisional, ambiguous, unmatched, not attempted, or API error
- input and matched ISSNs, candidate count and IDs, selected Source ID, title
  evidence, hostname/country agreement, retrieval timestamp, and OpenAlex
  `updated_date`

The coverage report must show row preservation; input ISSN availability; unique,
ambiguous, unmatched, not-attempted, and API-error counts by route; strict ISSN
coverage separately from provisional title coverage; OpenAlex field null rates;
`is_ojs` and country disagreements; request count, cost, retries, and failures.
It must also list every ambiguous and unmatched row for review. No title-only
candidate may be folded into strict ISSN coverage.

## Run the exploratory pipeline

Keep the pinned input under the external data root, then run the exact-ISSN
pipeline and its single output check:

```bash
export DATA_ROOT=/path/to/invisible-research-data
mkdir -p "$DATA_ROOT/raw/pkp-beacon-v6"
curl -fL 'https://dataverse.harvard.edu/api/access/datafile/13173372?format=original' \
  -o "$DATA_ROOT/raw/pkp-beacon-v6/beacon.csv"

OPENALEX_API_KEY=... python research/ojs-journal-metadata/analysis/enrich_openalex.py
python research/ojs-journal-metadata/analysis/enrich_openalex.py --profile
python research/ojs-journal-metadata/analysis/enrich_openalex.py --check
```

The script verifies the pinned MD5 and row baseline before requesting OpenAlex.
It writes the joined CSV, every non-unique row for review, the JSON coverage
report, and resumable selected-response cache under this owner's ignored
`artifacts/` directory. `--profile` reads those local outputs without making API
requests and writes one tidy four-dimension profile plus its machine-readable
summary in the same ignored directory. The four independently calculated
dimensions are PKP-inferred country, observable 2025 PKP record count, Beacon
observation duration as of 2026-07-16, and PKP-side DOAJ evidence. Missing
groups remain explicit in the grouping definitions, and every observed group
reports outcome counts and a 95% Wilson interval over the same Valid-ISSN OJS
Cohort. These are descriptive metadata: country is not authoritative publisher
location, record count is not an active-journal classification, Beacon duration
is not journal age since founding, and absent PKP DOAJ evidence is only “Not
observed.” The profile remains Exploratory Analysis, and the minimum run does
not attempt title matching.
