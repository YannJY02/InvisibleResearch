# Invisible Research Dataset

A relational dump of harvested OAI-PMH records and related metadata, loaded into MySQL.  
Covers 7 tables plus raw XML metadata in the `records` table.

---

## Tables & Columns

### 1. `contexts`
Stores information about each OAI-PMH “context” (data source).

| Column                  | Type / Notes                              | Example value |
|-------------------------|-------------------------------------------|---------------|
| `id`                    | Primary key                               | **1** |
| `endpoint_id`           | FK → `endpoints.id`                       | 17559 |
| `set_spec`              | OAI setSpec                               | `"KJS"` |
| `name`                  | Human-readable name                       | `"Kuwait Journal of Science"` |
| `group_id`              | Grouping ID                               | *NULL* |
| `group_order`           | Order within group                        | 0 |
| `harvested_at`          | Last harvest timestamp                    | 2024-10-15 10:31:32 |
| `sync_started_at`       | Sync start time                           | 2025-03-28 08:10:02 |
| `sync_succeeded_at`     | Sync success time                         | 2025-03-28 08:10:03 |
| `sync_failed_at`        | Sync failure time                         | *NULL* |
| `old_harvested_at`      | Previous harvest time                     | 2024-05-11 18:31:09 |
| `old_sync_succeeded_at` | Previous success time                     | 2024-10-07 09:39:43 |
| `errors`                | Total error count                         | 0 |
| `failures`              | Total failure count                       | 0 |
| `last_error`            | Last error message                        | *NULL* |
| `removed`               | Boolean flag                              | 0 |
| `disabled`              | Boolean flag                              | 0 |
| `doaj_id`               | FK → `doaj.id`                            | *NULL* |
| `created_at`            | Record creation timestamp                 | 2024-03-01 15:05:59 |
| `modified_at`           | Record last update timestamp              | 2025-03-28 08:10:03 |

---

### 2. `count_spans`
Annual summary of record counts per context.

| Column         | Notes                         | Example value |
|----------------|-------------------------------|---------------|
| `id`           | Primary key                   | **1** |
| `context_id`   | FK → `contexts.id`            | 1 |
| `year`         | Year                          | 2021 |
| `record_count` | Number of records that year   | 106 |
| `created_at`   | Creation timestamp            | 2024-03-01 15:11:19 |
| `modified_at`  | Last update timestamp         | 2024-05-11 18:31:16 |

---

### 3. `doaj`
DOAJ journal metadata.

| Column                   | Notes                          | Example value |
|--------------------------|--------------------------------|---------------|
| `id`                     | Primary key                    | **1** |
| `url`                    | Journal URL                    | `https://www.frontierspartnerships.org/journals/transplant-i` |
| `host`                   | Host/domain                    | `www.frontierspartnerships.org` |
| `print_issn`             | Print ISSN                     | *(empty)* |
| `online_issn`            | Online ISSN                    | 1432-2277 |
| `publisher`              | Publisher name                 | Frontiers Media S.A. |
| `country`                | Country                        | Switzerland |
| `country_iso`            | Country code                   | CH |
| `society`                | Society name                   | European Society for Organ Transplantation |
| `society_country`        | Society country                | Italy |
| `society_country_iso`    | Society country code           | IT |
| `created_at`             | Creation timestamp             | 2024-05-06 20:17:37 |
| `modified_at`            | Last update timestamp          | 2024-05-06 20:17:37 |

---

### 4. `endpoints`
Configuration & status of each OAI-PMH endpoint.

| Column                 | Notes                                      | Example value |
|------------------------|--------------------------------------------|---------------|
| `id`                   | Primary key                                | **17521** |
| `application`          | App identifier                             | `"ojs"` |
| `oai_url`              | Raw OAI-PMH base URL                       | `https://jurnal.unpad.ac.id/oai` |
| `oai_url_normalized`   | Normalized URL                             | `jurnal.unpad.ac.id/oai` |
| `stats_id`             | FK to stats tracking                       | 53ac0a66e3205 |
| `host`                 | Host/domain                                | `jurnal.unpad.ac.id` |
| `first_beacon`         | First successful reach timestamp           | 2020-04-30 23:59:24 |
| `last_beacon`          | Last successful reach timestamp            | 2024-09-09 18:01:27 |
| `last_oai_response`    | Time of last OAI-PMH response              | 2021-07-17 07:07:37 |
| `admin_email`          | Admin email                                | `derryadrian@unpad.ac.id` |
| `earliest_datestamp`   | Earliest record timestamp reported         | 2012-05-21 03:24:38 |
| `repository_name`      | OAI repository name                        | Jurnal Universitas Padjadjaran |
| `sync_started_at`      | Sync start time                            | 2024-10-30 02:40:58 |
| `sync_succeeded_at`    | Sync success time                          | 2024-10-06 06:15:49 |
| `sync_failed_at`       | Sync failure time                          | 2024-10-30 02:40:59 |
| `errors`               | Aggregated error count                     | 22 |
| `failures`             | Failure count                              | 1 |
| `disabled`             | Boolean flag                               | 0 |
| `last_error`           | Last error message                         | `"ListSets: Client error …"` |
| `country_tld`          | Geo info (TLD)                             | ID |
| `country_ip`           | Geo info (IP code)                         | ID |
| `created_at`           | Creation timestamp                         | 2024-03-01 14:25:45 |
| `modified_at`          | Last update timestamp                      | 2024-10-30 02:40:59 |

---

### 5. `issns`
ISSN list per context.

| Column        | Notes                   | Example value |
|---------------|-------------------------|---------------|
| `id`          | Primary key             | **3** |
| `context_id`  | FK → `contexts.id`      | 3 |
| `issn`        | ISSN string             | 2338-7823 |
| `format`      | e.g. “print” / “online” | Print |
| `marc`        | MARC tag                | io |
| `country`     | Country name            | ID |
| `url`         | Reference URL           | *NULL* |
| `created_at`  | Creation timestamp      | 2024-03-01 15:11:20 |
| `modified_at` | Last update timestamp   | 2024-03-01 15:11:20 |

---

### 6. `records`
Raw harvested records (OAI-PMH XML/JSON).

| Column        | Notes                                            | Example value |
|---------------|--------------------------------------------------|---------------|
| `id`          | Primary key                                      | **1** |
| `context_id`  | FK → `contexts.id`                               | 163757 |
| `update_date` | Last update timestamp (OAI datestamp)            | 2022-08-12 01:20:01 |
| `publish_date`| Publication date                                 | 2021-03-25 00:00:00 |
| `removed_at`  | Removal timestamp                                | *NULL* |
| `metadata`    | Raw XML/JSON payload                             | `<record xmlns=\"http://www.openarchives.org/OAI/2.0/\">…` |
| `identifier`  | Record identifier                                | 7649 |
| `created_at`  | Creation timestamp                               | 2024-05-06 16:13:59 |
| `modified_at` | Last update timestamp                            | 2024-05-08 15:44:13 |

---

### 7. `versions`
Version history for each endpoint.

| Column        | Notes                       | Example value |
|---------------|-----------------------------|---------------|
| `id`          | Primary key                 | **1** |
| `endpoint_id` | FK → `endpoints.id`         | 51961 |
| `version`     | Version string              | 3.1.1.4 |
| `date`        | Version timestamp           | 2020-09-21 08:34:50 |
| `created_at`  | Creation timestamp          | 2024-03-01 15:11:47 |
| `modified_at` | Last update timestamp       | 2024-03-01 15:11:47 |

---

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
```
## XML Tags & Example Values  


| XML Tag | Example Value                                                                                        |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `record`       | *(container element – no direct text)*                                                                         |
| `header`       | *(container – holds `identifier`, `datestamp`, `setSpec`)*                                                     |
| `identifier`   | `oai:oai.ejournal.unisba.ac.id:article/7649`                                                                   |
| `datestamp`    | `2022-08-12T01:20:01Z`                                                                                         |
| `setSpec`      | `hikmah:ART`                                                                                                   |
| `metadata`     | *(container – wraps `dc`)*                                                                                     |
| `dc`           | *(container – holds Dublin Core elements)*                                                                     |
| `title`        | `SPIRITUALITAS MASYARAKAT PERKOTAAN`                                                                           |
| `creator`      | `Afidah, Ida`                                                                                                  |
| `contributor`  | *(not present in this sample)*                                                                                 |
| `subject`      | `Learning Model, Aptitude Treatment Interaction, Learning Activities.`                                         |
| `description`  | `Masyarakat perkotaan sering diidentikan sebagai masyarakat modern, dikarenakan cara berfikir …`               |
| `publisher`    | `Universitas Islam Bandung`                                                                                    |
| `date`         | `2021-03-25`                                                                                                   |
| `type`         | `info:eu-repo/semantics/article`                                                                               |
| `format`       | `application/pdf`                                                                                              |
| `source`       | `HIKMAH : Jurnal Dakwah & Sosial; Vol 1, No 1 (2021): Jurnal Hikmah`                                            |
| `language`     | `eng`                                                                                                          |
| `relation`     | `https://ejournal.unisba.ac.id/index.php/hikmah/article/view/7649/pdf`                                         |
| `rights`       | `Copyright (c) 2021 HIKMAH`                                                                                    |

> **Note** – For container tags (`record`, `header`, `metadata`, `oai_dc:dc`) the table notes that they don’t carry literal text; the example focuses on child elements that do.