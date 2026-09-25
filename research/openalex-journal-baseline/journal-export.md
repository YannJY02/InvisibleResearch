# OpenAlex 期刊合表、连接验证与本周任务

更新：2026-09-15；INVIS-6 / 7 / 8。探索性数据交付。

**2026-09-25 范围补充：**本文记录的是 12 张输入表的原始合并交付；并非全部
76 张表已整合。新的[完整范围与连接审计](table-scope.md)解释了如何经论文补充
主题、学科、作者或机构信息，以及各项建议的证据边界。原 CSV 保持不变。

## 1. 使用正确的新库

**约定任务：把日常连接切到 multiobs，并确认公共库可以直接查询。**

已修改持久连接并完成实测：

| 用途 | 当前配置 / 结果 |
|---|---|
| 数据源 | `multiobs.publicdb_openalex_2026_01_rm`（US） |
| 导师工作库 | `multiobs.userdb_saurabh_khanna`（US），11 张既有克隆已核验 |
| 查询执行项目 | `gen-lang-client-0676290976`（YannJY），US |
| CLI / MCP | 两种通路均成功查询公共库和工作库；不再限定旧 insyspo |
| Brave 核对 | 用户已打开的公共 authors 查询已完成，API 读回同一作业也确认 10 行 |

数据在 multiobs，查询作业在 YannJY 执行，两者可以不同。公共表可以直接读取；
不是必须先复制到工作库。旧库权限错误不再作为本轮工作的阻塞。
[配置与最小执行命令](../../docs/operations/bigquery-mcp.md)；[四个实测作业](../../docs/testing/bigquery-access.md)。

用户的原始查询：

```sql
SELECT * FROM `multiobs.publicdb_openalex_2026_01_rm.authors` LIMIT 10
```

该作业 ID 为 `job_sbBLOCwefAD87ma1eYc4trWpKPEE`，US，DONE。只读回现有结果，没有重跑。

## 2. 将期刊相关表合并成一个 CSV

**约定任务：合并 sources、APC、年度记录等相关信息，检查逐列缺失，导出一刊一行的表。**

完整执行的 [GoogleSQL](analysis/export_journal_table.sql) 在 BigQuery 合并；
[导出脚本](analysis/export_journal_table.py) 下载和核验结果。复现入口：

```sh
python3 research/openalex-journal-baseline/analysis/export_journal_table.py \
  --gcloud /Users/yann.jy/.local/google-cloud-sdk/bin/gcloud \
  --output research/openalex-journal-baseline/artifacts/journal-export-2026-01
```

此目录对应本次执行；已有完整 manifest 时重跑须换新目录。

### 合并方式与已核验输入

母表只筛选 `type = 'journal'`，保留 **209,799 个非空、唯一 Source ID**。
保留原有 21 列，加上 10 个关联表列表列和 1 个出版者记录列，合计 32 列。
年度、币种、学会关系可能有多条；先分别按 source_id 整理为 JSON 列表，再合并，
因此不会把同一期刊重复展开成多行。全部年份和重复来源记录均保留。

| 关联信息 | 匹配的来源记录数 | 覆盖期刊数 |
|---|---:|---:|
| 年度记录 | 5,671,354 | 193,743 |
| APC 多币种价格 | 48,530 | 11,223 |
| 学会 | 8,910 | 3,780 |
| 组织层级 | 387,490 | 193,745 |
| 出版者属性 | 10,379 个不同出版者 | 63,016 |

出版者通过 `host_organization` 中完整的 OpenAlex P ID 精确连接。
63,030 个期刊有该 ID，其中 14 个在 publishers 表没有对应记录，保留为空。
没有按出版者名字近似匹配。

**发现来源子表有重复记录。** 全文件核验如下：

| 子表 | 保留的原始行数 | 按全部字段去重后 |
|---|---:|---:|
| 年度记录 | 5,671,354 | 2,835,677 |
| APC | 48,530 | 24,265 |
| 学会 | 8,910 | 4,455 |
| 组织层级 | 387,490 | 193,745 |

这四类记录总数都是去重后的两倍。CSV 保留原始记录以便追溯；后续计算年度发文量、
APC 或关系数量时，应先明确去重规则，不能直接把这些子行相加。

### 缺失值怎么读

- CSV 的 `\N` 是数据库 NULL；空字符串仍为空字符串；`0`、`false` 原样保留。
- JSON 列里的 `[]` 是没有匹配子记录；JSON 对象内部的 `null` 仍保留。
- `sources_concepts` 等六张子表全空，而且没有 `sources_topics`，因此当前文件不能提供期刊主题分类。切换 EU/US 不能补齐这一缺口。

| 核心字段 | NULL 数 / 209,799 | 另有空字符串 |
|---|---:|---:|
| issn | 70,349 | 0 |
| issn_l | 70,356 | 0 |
| homepage_url | 133,383 | 1 |
| country_code | 102,604 | 0 |
| apc_usd | 185,506 | 0 |
| publisher | 88,593 | 2 |

这些是字段缺失，不等于没有 ISSN、没有 APC 或没有出版者。所有期刊均保留。
完整的 32 列缺失计数由 BigQuery 计算，再与下载内容逐列核对；原子表字段也保存了各自分母与 NULL/空字符串计数。

### 文件与验证

已完整导出并重新解析核验：**209,799 行 × 32 列，732,279,676 bytes（约 732 MB）**。
合并前后的期刊 ID 集合一致，各子表记录数及覆盖期刊数一致，云端与本地逐列
NULL、空字符串和空列表计数一致，12 张输入表前后元数据稳定。独立复核还逐一核对了所有子字段的缺失计数、出版者完整记录及文件哈希。

本地文件统一位于 `research/openalex-journal-baseline/artifacts/journal-export-2026-01/`：

| 文件 | 内容 |
|---|---|
| `openalex-journals-2026-01.csv` | 完整合并表 |
| `column-missingness.csv` | 32 列缺失值计数 |
| `source-field-missingness.csv` | 61 个原子字段缺失值计数 |
| `openalex-journals-2026-01-field-guide.md` | 字段与空值说明 |
| `manifest.json` | 执行作业、行数、文件哈希 |
| `independent-validation.json` | 全文件独立复核及重复记录数量 |

CSV SHA256：`7c555e0a926510d0efb4c97847c75a45709ff4b3eba6aa37fa84e164d76aca48`。
**已上传到导师原共享 SURFdrive 的 Data 文件夹。** CSV、字段说明、两份缺失清单
和执行 manifest 共 5 个文件均已远端读回。大 CSV 分 175 个区块完整读取，再按
字节顺序计算整份 SHA256，与本地完全一致；读取前后的远端版本标识和大小一致。
没有覆盖原有文件或重复上传 CSV。

远端证据：`research/openalex-journal-baseline/artifacts/surfdrive-delivery/` 下的
`openalex-journals-2026-01.csv.upload.json` 和 `openalex-journals-2026-01.csv.range-readback.json`；
其余四个文件各有对应的 `.upload.json`。共享令牌仅保存在本机私有文件中。

合并作业：`codex_journal_export_d22d6c52e8eb4791931d1b80830c5f50`。
最终缺失审计：`codex_journal_missingness_3f5a74ccbe9644d896a48cd899cea8f3`。
本轮导出管线四个成功作业累计计费扫描 1,394,606,080 bytes（约 1.30 GiB）。

## 3. 两个 January 2026 库有没有差异

**约定任务：用较少扫描判断 EU/US 是否有数据差异，并留下证据。**

先核对 76 张表的清单、结构、行数、大小，再对本轮所需的 12 张表全部行计算内容指纹。
结果：这 12 张表的指纹全部一致；导师工作库的 11 张克隆也一致。
其余 64 张大表只比较元数据，尚未逐行验证。详见[比较方法与作业证据](dataset-comparison.md)。

## 4. 接下来一周（9 月 15–22 日）

**约定任务：先交付期刊表，再推进会议约定的后续工作。**

| 顺序 | 任务 | 本次进展 / 下一步 |
|---|---|---|
| 1 | 修正连接（INVIS-6） | 持久配置、CLI、MCP 与 Brave 证据已核验 |
| 2 | 固定输入与行规则（INVIS-7） | 按用户指示采用新 multiobs US；一刊一行和关联规则已落实；9/17 审阅子表重复及主题缺口 |
| 3 | 合表、缺失检查、CSV、SURFdrive（INVIS-8） | 已完成合表、全部检查、CSV 上传和完整远端哈希核验，转入审阅；9/21 检查反馈 |
| 4 | Scopus / WoS 访问与收录标记（INVIS-9） | 导师先调查访问途径；取得有版本的参照后，用本次基线做 ISSN 匹配，单独保留无标识符和歧义 |
| 5 | 种子文献与综述（INVIS-11，原有并行任务） | 9/22 核对导师种子是否收到，随后推进引用链与草稿；已有笔记不代替种子确认 |

Boruta/SHAP 在收录标记可靠后继续，当前不提前建模。以上日期是内部安排；
下次会议只核实到“下周、阿姆斯特丹 09:30”，具体日期以邀请为准。

## 验证证据入口

本地证据位于 `artifacts/journal-export-2026-01/`：原始 SQL、dry run、job JSON、
源表前后元数据、合并前行数与 ID 摘要、逐列缺失计数、导出 manifest。
连接证据另在 `docs/testing/artifacts/bigquery-current-connection/`。
生成的数据和日志不提交 Git；仓库提交保存脚本、SQL 和报告，SURFdrive 文件单独验收。

分页下载使用 [BigQuery getQueryResults](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/jobs/getQueryResults)，
关联列表使用 [ARRAY_AGG](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/aggregate_functions)。
源表查询每项上限 512 MiB；序列化后较大的结果缺失审计上限 2 GiB，均先 dry run。
