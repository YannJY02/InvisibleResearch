# BigQuery access from Codex

Use the existing official `bq` CLI for direct diagnostics and Google MCP
Toolbox for the project's persistent AI interface. Current access evidence
and the administrator request are in the
[verification record](../testing/bigquery-access.md). INVIS-6 remains blocked
until an actual query succeeds after the project permission is repaired.

## Installed configuration

The user authorized this setup on **2026-09-14**. Google Toolbox **v1.10.0**
is installed at `/Users/yann.jy/.local/share/mcp-toolbox/v1.10.0/toolbox`.
Its macOS arm64 SHA-256 matches the
[official release](https://github.com/googleapis/mcp-toolbox/releases/tag/v1.10.0):

```text
c994f06781462abba4171cb4844776c45605e391c57dc96adb3e130c81b53825
```

The repository-owned [Toolbox configuration](../../config/bigquery-toolbox.yaml)
uses v1.10.0's flat YAML format and these settings:

- Execution project `insyspo`, location `US`.
- Dataset allowlist: `insyspo.publicdb_openalex_2025_08_rm`.
- `readOnly: true` and `writeMode: blocked` for SELECT queries.
- Maximum bytes billed per query: **104,857,600 bytes (100 MiB)**.
- Maximum returned rows: **100**; this is separate from the scan cap.
- Five tools: `get_dataset_info`, `get_table_info`, `list_dataset_ids`,
  `list_table_ids`, and `execute_sql`.

The allowlist is the scope of the current access diagnostic. It does not
select the research snapshot; INVIS-7 still owns that decision. Do not expand
the dataset scope or raise the cap simply to make a failed query run.

The machine-local `.codex/config.toml` registers `bigquery_research` with the
absolute executable and YAML paths, `--config` and `--stdio`, a 30-second
startup timeout, and a 60-second tool timeout. It is ignored through Git's
local exclude file because those paths belong to this checkout. Global Codex
MCP configuration was not changed. Codex supports
[project-scoped MCP settings](https://developers.openai.com/codex/mcp/)
for trusted projects; `codex mcp get bigquery_research --json` reads this entry.

Reload MCP servers in Codex, or restart the application after saving work,
to load the new server into an already-running conversation. The installation
run verified the same configured executable over MCP stdio directly; the
existing conversation did not hot-load its tool namespace.

## Authentication and use

The official Google ADC OAuth flow completed, and Google's userinfo endpoint
confirmed `yann.jyal@gmail.com`. ADC lives outside the repository at its
standard user path. The existing `gcloud`/`bq` login and default project were
preserved. No quota project was assigned to ADC; query execution explicitly
targets `insyspo`. Diagnose a future quota-project error separately rather
than assigning another billing project implicitly.

To read the current schema directly through the installed Toolbox:

```sh
/Users/yann.jy/.local/share/mcp-toolbox/v1.10.0/toolbox \
  invoke get_table_info '{"table":"sources"}' \
  --config config/bigquery-toolbox.yaml
```

In Codex, ask to inspect the `sources` schema or list tables through
`bigquery_research`. Before a data query, request an `execute_sql` dry run and
check its estimate. `list_dataset_ids` returns the configured allowlist; it
is not a live inventory of every dataset the account can access.

The current MCP constant-query test fails during Toolbox's mandatory dry run
with `bigquery.jobs.create` denied. An installed server and successful
metadata reads do not release this permission blocker. No SQL write test was
executed, and the billing cap has not been exercised by a successful query.

This configuration uses only the BigQuery API and ADC. It enables no Gemini,
Vertex AI, Dataplex, telemetry exporter, or standalone HTTP service. Refer to
Google's [BigQuery source implementation](https://github.com/googleapis/mcp-toolbox/blob/v1.10.0/internal/sources/bigquery/bigquery.go)
and [SQL tool implementation](https://github.com/googleapis/mcp-toolbox/blob/v1.10.0/internal/tools/bigquery/bigqueryexecutesql/bigqueryexecutesql.go)
for the versioned enforcement behavior.
