# BigQuery access verification

Observed on **2026-09-14, 23:18–23:20 Asia/Shanghai** for **INVIS-6**.
Owner: project operations. This is a dated verification record; current task
status remains in [Plane](../operations/project-management.md).

## Result and scope

Google's official CLI successfully read table metadata and one ID from each of
`authors` and `sources` in `insyspo.publicdb_openalex_2025_08_rm`. Query execution
in project `insyspo` still failed with `bigquery.jobs.create` denied. Changing
to a plugin or MCP client does not resolve that IAM denial.

The tests used the active researcher account `yann.jyal@gmail.com`, Google
Cloud SDK **559.0.0**, and bundled `bq` **2.1.28**. The executable is
`/Users/yann.jy/.local/google-cloud-sdk/bin/bq`; it is installed but not directly
on PATH. Each command explicitly selected `insyspo`, because the existing CLI
default points to another project. No default-project or IAM changes were made.

| Check | Observed result | Evidence scope |
|---|---|---|
| CLI authentication | API requests succeeded | Existing CLI login works for these requests |
| `bq show` on `authors` | Success; location `US`, 10 schema fields | Table metadata visibility |
| `bq head --max_rows=1 --selected_fields=id` on `authors` | Success; returned one ID | One selected field is readable without a query job |
| `bq ls --max_results=1000` on the dataset | Returned 75 tables, including `sources` | Listed this dataset only; no project-wide snapshot inventory |
| `bq show` on `sources` | Success; location `US`, 21 schema fields | Metadata reports 260,789 rows; this is not a filtered journal count |
| `bq head --max_rows=1 --selected_fields=id` on `sources` | Success; returned one ID | One selected field is readable without a query job |
| `SELECT 1 AS access_test`, with `maximum_bytes_billed=1` | Failed, exit code 1 | Query-job creation remains denied; no successful query job ID |

Exact query error:

```text
BigQuery error in query operation: Access Denied: Project insyspo: User does not
have bigquery.jobs.create permission in project insyspo.
```

Machine-readable command arguments, UTC timestamps, exit codes and complete
responses are retained locally under ignored
`docs/testing/artifacts/bigquery-access/`: `authors-metadata.json`,
`authors-row-preview.json`, `dataset-tables.json`, `sources-metadata.json`,
`sources-row-preview.json`, and `query-execution.json`. No credential material
was saved. These generated files are not part of the committed record.

This retest does not verify January 2026 snapshots, all fields or tables,
write access, a full extraction, or SURFdrive delivery. No IAM or service
enablement changes, plugin installation, or collaborator message was performed.

## Reproduce and release the blocker

Use the existing official CLI with an explicit execution project:

```sh
BQ_CLI=/Users/yann.jy/.local/google-cloud-sdk/bin/bq
gcloud auth list --format=json
"$BQ_CLI" --headless=true --project_id=insyspo --format=prettyjson \
  show insyspo:publicdb_openalex_2025_08_rm.sources
"$BQ_CLI" --headless=true --project_id=insyspo --format=prettyjson \
  head --max_rows=1 --selected_fields=id \
  insyspo:publicdb_openalex_2025_08_rm.sources
"$BQ_CLI" --headless=true --project_id=insyspo --location=US --format=prettyjson \
  query --use_legacy_sql=false --maximum_bytes_billed=1 \
  'SELECT 1 AS access_test'
```

The original constant-query test omitted the location flag; the reproduction
command sets `US` explicitly to match the inspected tables.

The concrete administrator request is to grant the researcher **BigQuery Job
User (`roles/bigquery.jobUser`) on project `insyspo`**, or identify an approved
execution project with that permission and an agreed billing arrangement.
The [official role definition](https://docs.cloud.google.com/bigquery/docs/access-control#bigquery.jobUser)
includes `bigquery.jobs.create`. [Table browsing](https://docs.cloud.google.com/bigquery/docs/managing-table-data#browse-table)
uses `bigquery.tables.getData`, explaining why successful previews do not prove
query-job access. This run did not inspect the underlying IAM bindings.

After an administrator reports repair, rerun the constant query, then dry-run
and execute a small read from the selected target table with an explicit byte
cap. Save the successful job ID, project, location, input table, output and
processed/billed bytes before releasing the extraction dependency. A `LIMIT`
alone is not a scan-cost cap. Snapshot selection remains INVIS-7's separate
decision. No repair or alternate execution route has yet been verified.

## Official AI access options checked on September 14

These routes use Google Cloud authentication and permissions independently of
the plan-restricted built-in BigQuery connector reported by the user. This
run exercised only `bq`; plugin and MCP compatibility below is documented,
not an installed-runtime test.

| Official route | Relevance and requirements |
|---|---|
| [BigQuery CLI, REST and client libraries](https://docs.cloud.google.com/bigquery/docs/authentication) | The current working diagnostic route. CLI credentials and Application Default Credentials (ADC) are separate; client libraries commonly use ADC. |
| [MCP Toolbox for Databases](https://docs.cloud.google.com/bigquery/docs/pre-built-tools-with-mcp-toolbox) | Google-maintained local MCP server; BigQuery prebuilt tools support stdio, ADC and `BIGQUERY_PROJECT`. Suitable for ongoing Codex access after authentication and IAM are configured. |
| [BigQuery Data Analytics plugin and skills](https://github.com/gemini-cli-extensions/bigquery-data-analytics) | Google's repository documents Codex support, skills and a Toolbox-backed MCP server. It currently labels the project beta/pre-v1.0 and requires Codex >=0.117.0. Local Codex CLI is 0.153.4, with the plugin command present. No ADC file was found at the default local path; other ADC sources were not tested. |
| [Google-hosted BigQuery MCP](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp) | Endpoint `https://bigquery.googleapis.com/mcp`. The current guide says BigQuery API enablement also enables MCP. Calls require MCP Tool User plus applicable BigQuery IAM. Listing tools alone does not require authentication and cannot validate dataset access. |

For the local plugin, the inspected README names
`bigquery-data-analytics@data-agent-kit`, whereas the current
[Google marketplace manifest](https://github.com/GoogleCloudPlatform/data-agent-kit/blob/main/.agents/plugins/marketplace.json)
registers `bigquery` at ref `0.2.1`. Resolve the actual marketplace entry before
installation; neither spelling was tested by installing in this run.

For remote MCP, Google's [authentication guide](https://docs.cloud.google.com/mcp/authenticate-mcp)
does not support Dynamic Client Registration or Client ID Metadata Documents;
do not assume automatic OAuth compatibility from generic MCP support. A bearer
token needs refresh. Query billing and IAM continue to apply to all routes.
No claim of a completely free MCP service is established here.

For the current meeting preparation, continue with the already functioning
CLI for schema inspection and permission diagnostics. A local Toolbox/plugin
can provide a persistent AI interface later, but does not unblock SQL execution
until the project permission is repaired.
