# BigQuery CLI 与 MCP 连接

**当前数据源是 `multiobs`。** 2026-09-15 已更新持久配置，并通过 CLI 和
MCP stdio 分别查询公共库、导师工作库成功。验证步骤和作业证据见
[访问验证记录](../testing/bigquery-access.md)。

## 当前配置

[仓库配置](../../config/bigquery-toolbox.yaml)由 Google MCP Toolbox
**v1.10.0** 的 CLI `invoke` 和 Codex 的 `bigquery_research` 共用。

| 用途 | 配置 |
|---|---|
| 数据所在项目 | `multiobs` |
| 当前公共数据集 | `multiobs.publicdb_openalex_2026_01_rm` |
| 导师工作数据集 | `multiobs.userdb_saurabh_khanna` |
| 查询作业执行项目 | `gen-lang-client-0676290976`（YannJY） |
| 执行区域 | `US` |
| SQL 范围 | 上述两个数据集；`readOnly: true`、`writeMode: blocked` |
| 每次查询上限 | 512 MiB（536,870,912 bytes），最多返回 100 行 |

**数据位置和作业执行位置是两项设置。** SQL 中完整表名决定读哪个库；
执行项目负责创建查询作业。执行项目使用 YannJY，不会把数据来源改成 YannJY。
Toolbox 的元数据工具接受单独的 `project` 参数；这里应填写 `multiobs`。
这是 v1.10.0 的[数据源](https://github.com/googleapis/mcp-toolbox/blob/v1.10.0/internal/sources/bigquery/bigquery.go)
和[元数据工具](https://github.com/googleapis/mcp-toolbox/blob/v1.10.0/internal/tools/bigquery/bigquerygettableinfo/bigquerygettableinfo.go)
支持的跨项目用法，且已经实际验证。

## 直接使用

在仓库根目录执行。查看当前允许的数据集：

```sh
/Users/yann.jy/.local/share/mcp-toolbox/v1.10.0/toolbox \
  invoke list_dataset_ids '{}' --config config/bigquery-toolbox.yaml
```

查看公共库的表结构；换成 `userdb_saurabh_khanna` 即查看导师工作库：

```sh
/Users/yann.jy/.local/share/mcp-toolbox/v1.10.0/toolbox \
  invoke get_table_info \
  '{"project":"multiobs","dataset":"publicdb_openalex_2026_01_rm","table":"sources"}' \
  --config config/bigquery-toolbox.yaml
```

查询前先检查扫描量：

```sh
/Users/yann.jy/.local/share/mcp-toolbox/v1.10.0/toolbox \
  invoke execute_sql \
  '{"sql":"SELECT id, display_name FROM `multiobs.publicdb_openalex_2026_01_rm.sources` LIMIT 1","dry_run":true}' \
  --config config/bigquery-toolbox.yaml
```

确认扫描量在上限内，再将 `dry_run` 改为 `false` 执行。所有 SQL 使用完整的
`multiobs.dataset.table` 表名。`list_dataset_ids` 返回配置中的允许列表，
并非账户全部可见数据库。100 行是工具返回上限；完整 CSV 使用
[期刊基线工作流](../../research/openalex-journal-baseline/README.md)。

原生 `bq` 也可以使用同一个执行项目，下面的显式参数不依赖全局默认值：

```sh
/Users/yann.jy/.local/google-cloud-sdk/bin/bq \
  --project_id=gen-lang-client-0676290976 --location=US --format=prettyjson \
  query --use_legacy_sql=false --maximum_bytes_billed=536870912 --dry_run \
  'SELECT id, display_name FROM `multiobs.publicdb_openalex_2026_01_rm.sources` LIMIT 1'
```

原生 `bq` 不读取 Toolbox YAML；上述允许列表和只读限制只由 Toolbox 实施。

## Codex 与验证边界

本机 `.codex/config.toml` 的 `bigquery_research` 已指向上述仓库 YAML；
`codex mcp get bigquery_research --json` 读回确认。新启动的 Toolbox 进程
已通过 MCP `initialize`、`tools/list`、表列表、dry run 和真实查询验证。
这证明配置和 MCP 服务可用。本次对话的工具目录尚未出现 BigQuery 命名空间，
不能声称已经在当前对话内热加载；当前可直接使用上面的 CLI。

每种方式分别查询了公共库和导师工作库，共四个成功作业；逐个通过 `bq show -j`
读回 `DONE`、实际引用表及扫描量。原始响应、SQL、配置哈希和作业信息保存在
本地 `docs/testing/artifacts/bigquery-current-connection/`。每个作业实际扫描
12,620,845 bytes、计费 13 MiB，均使用配置中的 512 MiB 上限。

认证继续使用现有 ADC / Google CLI 登录；没有修改全局 gcloud 设置、IAM、
服务启用状态或云端数据。旧诊断保留在[访问验证记录](../testing/bigquery-access.md)
的历史部分，不作为当前连接状态。
