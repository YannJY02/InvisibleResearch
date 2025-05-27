# Invisible Research Dataset

A relational dump of harvested OAI-PMH records and related metadata, loaded into MySQL.  
Covers 7 tables plus raw XML metadata in the `records` table.

---

## Tables & Columns

### 1. `contexts`
Stores information about each OAI‐PMH “context” (data source).

| Column                  | Type / Notes                              |
|-------------------------|--------------------------------------------|
| `id`                    | Primary key                                |
| `endpoint_id`           | FK → `endpoints.id`                        |
| `set_spec`              | OAI setSpec                               |
| `name`                  | Human-readable name                        |
| `group_id`              | Grouping ID                               |
| `group_order`           | Order within group                        |
| `harvested_at`          | Last harvest timestamp                    |
| `sync_started_at`       | Sync start time                           |
| `sync_succeeded_at`     | Sync success time                         |
| `sync_failed_at`        | Sync failure time                         |
| `old_harvested_at`      | Previous harvest time                     |
| `old_sync_succeeded_at` | Previous success time                     |
| `errors`                | Total error count                         |
| `failures`              | Total failure count                       |
| `last_error`            | Last error message                        |
| `removed`               | Boolean flag                              |
| `disabled`              | Boolean flag                              |
| `doaj_id`               | FK → `doaj.id` (optional DOAJ link)        |
| `created_at`            | Record creation timestamp                 |
| `modified_at`           | Record last update timestamp              |

---

### 2. `count_spans`
Annual summary of record counts per context.

| Column         | Notes                         |
|----------------|-------------------------------|
| `id`           | Primary key                   |
| `context_id`   | FK → `contexts.id`            |
| `year`         | Year                          |
| `record_count` | Number of records that year   |
| `created_at`   | Creation timestamp            |
| `modified_at`  | Last update timestamp         |


### 3. `doaj`
DOAJ journal metadata.

| Column                   | Notes                          |
|--------------------------|--------------------------------|
| `id`                     | Primary key                    |
| `url`                    | Journal URL                    |
| `host`                   | Host/domain                    |
| `print_issn`             | Print ISSN                     |
| `online_issn`            | Online ISSN                    |
| `publisher`              | Publisher name                 |
| `country`                | Country                        |
| `country_iso`            | Country code                   |
| `society`                | Society name                   |
| `society_country`        | Society country                |
| `society_country_iso`    | Society country code           |
| `created_at`             | Creation timestamp             |
| `modified_at`            | Last update timestamp          |


### 4. `endpoints`
Configuration & status of each OAI-PMH endpoint.

| Column                 | Notes                                      |
|------------------------|--------------------------------------------|
| `id`                   | Primary key                                |
| `application`          | App identifier                             |
| `oai_url`              | Raw OAI-PMH base URL                       |
| `oai_url_normalized`   | Normalized URL                             |
| `stats_id`             | FK to stats tracking                       |
| `host`                 | Host/domain                                |
| `first_beacon`         | First successful reach timestamp           |
| `last_beacon`          | Last successful reach timestamp            |
| `last_oai_response`    | Duration of last OAI-PMH response          |
| `admin_email`          | Admin email                                |
| `earliest_datestamp`   | Earliest record timestamp reported         |
| `repository_name`      | OAI repository name                        |
| `sync_started_at`      | Sync start time                            |
| `sync_succeeded_at`    | Sync success time                          |
| `sync_failed_at`       | Sync failure time                          |
| `errors`, `failures`   | Aggregated error/failure counts            |
| `last_error`           | Last error message                         |
| `disabled`             | Boolean flag                               |
| `country_tld`, `country_ip` | Geo info                           |
| `created_at`, `modified_at`   | Timestamps                        |


### 5. `issns`
ISSN list per context.

| Column        | Notes                   |
|---------------|-------------------------|
| `id`          | Primary key             |
| `context_id`  | FK → `contexts.id`      |
| `issn`        | ISSN string             |
| `format`      | e.g. “print” / “online” |
| `marc`        | MARC tag                |
| `country`     | Country name            |
| `url`         | Reference URL           |
| `created_at`  | Creation timestamp      |
| `modified_at` | Last update timestamp   |


### 6. `records`
Raw harvested records (OAI-PMH XML/JSON).

| Column        | Notes                                            |
|---------------|--------------------------------------------------|
| `id`          | Primary key                                      |
| `context_id`  | FK → `contexts.id`                               |
| `update_date` | Last update timestamp (OAI datestamp)            |
| `publish_date`| Publication date                                 |
| `removed_at`  | Removal timestamp                                |
| `metadata`    | Raw XML/JSON payload                             |
| `identifier`  | Record identifier                                |
| `created_at`  | Creation timestamp                               |
| `modified_at` | Last update timestamp                            |


### 7. `versions`
Version history for each endpoint.

| Column        | Notes                       |
|---------------|-----------------------------|
| `id`          | Primary key                 |
| `endpoint_id` | FK → `endpoints.id`         |
| `version`     | Version string              |
| `date`        | Version timestamp           |
| `created_at`  | Creation timestamp          |
| `modified_at` | Last update timestamp       |


## XML Metadata Tags

In the first sample of 5 records, we found these unique XML element tags:

```text
OAI-PMH Tags (OAI/2.0 namespace):
  - record, header, metadata, identifier, datestamp, setSpec
  - oai_dc:dc  (container for Dublin Core)

Dublin Core Tags (http://purl.org/dc/elements/1.1/):
  - title, creator, contributor, subject*, description, publisher
  - date, type, format, identifier, source
  - rights, language, relation

*note: subject did not appear in the first 5 samples but is a standard Dublin Core element.

⸻
