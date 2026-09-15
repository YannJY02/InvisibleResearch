# BigQuery access verification

## 当前连接：multiobs（2026-09-15 会后）

用户已明确旧 insyspo 停用。持久 [Toolbox 配置](../../config/bigquery-toolbox.yaml)
现在允许 `multiobs.publicdb_openalex_2026_01_rm` 和 `multiobs.userdb_saurabh_khanna`；
执行项目为 `gen-lang-client-0676290976`，US。两套概念分别是“数据在哪里”与
“查询作业在哪里执行”，无需把作业项目设成 multiobs 才能读取其公共表。

CLI `toolbox invoke` 和真实 MCP stdio 都分别成功查询上述公共库/工作库；四个作业
已读回 DONE，每个扫描 12,620,845 bytes。旧 insyspo 范围在该配置中已被拒绝。
本轮没有改云端 IAM；本机 gcloud 默认项目本来就是 YannJY，无需再改。

| 通路 | 公共库成功作业 | 工作库成功作业 |
|---|---|---|
| CLI invoke | `LmSk0jxaVQjbnjYi50pQJy6v5dj` | `dwAoJK1JlmRkgE9Yqn3bxawBEMf` |
| MCP stdio | `ASFaP5yiBq7gNOLOc40iqiNN572` | `FBtISQjE2rEmGsulVXLjKEJ4R4H` |

当前对话工具列表没有热加载 BigQuery 命名空间；这不影响已经验证可执行的 CLI 和
MCP stdio。日常启动方式见[操作说明](../operations/bigquery-mcp.md)。完整本地证据：
`artifacts/bigquery-current-connection/summary.json` 及同目录 job-readback.json。

同时实际查看了用户的 Brave 页面，并从 BigQuery API 读回同一作业
`job_sbBLOCwefAD87ma1eYc4trWpKPEE`：公共 authors 查询 DONE、10 行、执行项目 YannJY、US。
没有重跑这个较大的 authors 查询。其日志位于期刊导出证据目录，见[简明报告](../../research/openalex-journal-baseline/journal-export.md)。

## 历史访问诊断（以下均保留当时范围）

Observed on **2026-09-14, 23:18–23:20 Asia/Shanghai** for **INVIS-6**.
Owner: project operations. This is a dated verification record; current task
status remains in [Plane](../operations/project-management.md).

**此前成功路线 (2026-09-15, 18:18–18:20 China time):** using
`gen-lang-client-0676290976` (the YannJY project selected in the user's supplied
browser view) as the job project, actual region-local queries on
`multiobs.publicdb_openalex_2026_01_eu_rm`,
`multiobs.publicdb_openalex_2026_01_rm` and `multiobs.userdb_saurabh_khanna`
all succeeded. The [dataset comparison](../../research/openalex-journal-baseline/dataset-comparison.md)
records job IDs, regions, scan caps, full results and verification. Direct
job creation in `multiobs` still failed for `bigquery.jobs.create`; no IAM
repair is claimed. The existing `insyspo` failure below remains historical
evidence for that execution project, not a blocker on the working new route.
No default project, IAM or MCP allowlist was changed.

**Earlier query test (2026-09-15, before meeting):** the
[R/Quarto meeting report](../../research/ojs-journal-metadata/analysis/crossref-meeting-report.qmd)
executed `SELECT 1 AS access_test` through `bq` from R; it still failed for
missing `bigquery.jobs.create` in `insyspo`. This was the premeeting supervisor
presentation. The September 14 23:39–23:52 tests below confirmed dataset OWNER
and completed a full official `tabledata.list` read of the candidate sources
table; see the final section and the
[earlier technical record](../../research/openalex-journal-baseline/premeeting-report.md).

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

## Historical reproduction of the old-project blocker

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
initial diagnostic exercised only `bq`; the later setup and MCP runtime
validation are recorded in the final section below.

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

## Subsequent authorized MCP setup — September 14, 23:30

After the user accepted the recommended setup, Google Toolbox v1.10.0 was
installed from the official macOS arm64 binary and its SHA-256 was checked
against the release. ADC authorization completed; a fresh Google userinfo
response confirmed the researcher account. The project-scoped Codex server
`bigquery_research` uses the committed
[restricted configuration](../../config/bigquery-toolbox.yaml).
See [operating instructions](../operations/bigquery-mcp.md) for paths and limits.

The following checks were executed, with full responses retained locally in
`artifacts/bigquery-access/mcp-tools.json` and `mcp-runtime.json`:

| Runtime check | Observed result |
|---|---|
| `codex mcp get bigquery_research --json` | Parsed the enabled project-scoped server with the intended executable/configuration paths |
| MCP stdio `initialize` and `tools/list` | Successful protocol handshake; exactly five configured tools, all with `readOnlyHint: true` |
| MCP `get_table_info`, `table=sources` | Successfully returned the expected table ID and 21 schema fields |
| MCP `get_table_info` with synthetic dataset `outside_access_scope` | Rejected because the dataset is outside the configured allowlist |
| MCP `execute_sql`, `SELECT 1 AS access_test`, `dry_run=false` | Failed during the server's initial dry run: HTTP 403, missing `bigquery.jobs.create` on `insyspo` |
| Existing conversation's server discovery | Reported unknown MCP server; configuration requires reload before this conversation exposes its tools |

The cost cap, SELECT-only configuration and tool annotations were inspected;
no successful query or write-rejection experiment establishes their full
runtime behavior while query-job permission is missing. The successful
metadata call and failed boundary test do establish functioning ADC, MCP
transport, table-metadata access and the tested metadata allowlist check.

Administrator request prepared for the existing supervisor workflow, **not sent**:

> I retested BigQuery using Google's official CLI and MCP Toolbox. My account
> can read the authors and sources metadata and preview one ID from each table
> in insyspo.publicdb_openalex_2025_08_rm, but SELECT 1 fails with
> bigquery.jobs.create denied on project insyspo. Could the administrator grant
> yann.jyal@gmail.com BigQuery Job User (roles/bigquery.jobUser) on insyspo, or
> confirm the approved project for running and billing these queries? I will
> rerun a bounded read after the permission is updated.

## User dataset and complete alternate read — September 14, 23:39–23:52

The user asked whether `userdb_yann_jyal` changes the permission result and
authorized other means, including saved merged data, to continue the planned
work. Fresh `bq show --dataset` succeeded and returned an explicit OWNER entry
for the researcher account. The dataset is in `US`; its table listing succeeded
with no tables returned. No write test was performed.

The corrected constant-query test explicitly selected that default dataset:

```sh
/Users/yann.jy/.local/google-cloud-sdk/bin/bq \
  --headless=true --project_id=insyspo \
  --dataset_id=insyspo:userdb_yann_jyal --location=US --format=prettyjson \
  query --use_legacy_sql=false --maximum_bytes_billed=1 \
  'SELECT 1 AS access_test'
```

It failed with the same `bigquery.jobs.create` denial at
`2026-09-14T15:39:08.798359Z`, exit 1. Dataset ownership does not grant the missing
project job permission. Raw dataset metadata, table listing and command output
are local under `artifacts/bigquery-access/`; `userdb-query.json` contains the
correct test, while `userdb-query-cli-flag-error.json` preserves a preceding
invalid-flag attempt that is not permission evidence.

An authorized alternate route then succeeded: the official REST
[`tabledata.list`](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/tabledata/list)
method read all 260,789 records of
`insyspo.publicdb_openalex_2025_08_rm.sources` in 27 pages, without a SQL job.
The [reader](../../research/openalex-journal-baseline/analysis/read_bigquery_sources.py)
decoded all 21 scalar fields and retained the 209,799 exact `type == journal`
rows locally. Before/after schema, numRows, numBytes and lastModifiedTime were
identical. Independent readback verified IDs, all 4,405,779 journal field values,
page totals and both file hashes. This is complete-read evidence for this table,
not transactional snapshot isolation or proof that every related table is readable.

The valid manifest, raw JSONL, journal CSV and independent verification are in
`research/openalex-journal-baseline/artifacts/bigquery-tabledata-2025-08/`.
CSV merges null and original empty strings into empty cells; JSONL preserves
their distinction. Completion requires a valid manifest and matching hashes,
not just final filenames. No credentials were retained in artifacts.

A fresh project inventory listed 16 visible datasets, with OpenAlex candidates
March 2025 and August 2025. January 2026 and the third meeting candidate were not
identified in that account/project scope. A
[candidate input contract](../../research/openalex-journal-baseline/input-contract.md)
records these limits and the inspected related-table schemas. The alternate read
releases the core-table extraction's dependence on SQL access. It does not repair
IAM, confirm the final scientific snapshot, complete related metadata or verify
SURFdrive delivery.
