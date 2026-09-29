# 期刊字段补全与重算简报

日期：2026-09-29。数据源：`multiobs.publicdb_openalex_2026_01_rm`。

**约定任务：明确哪些期刊字段需要重算、按什么官方依据计算，以及需要新增哪些表。**
本报告整理已执行的字段核验与后续计算方案；尚未从 BigQuery 的全部论文重算期刊指标。

当前数据库已有期刊基本信息、总发文量、总被引量、文章处理费（APC）和部分关联信息，不必全部重建。
缺少单独的期刊总量列，不等于整个数据库没有相关数据：例如年度 OA 数已在
`sources_counts_by_year.oa_works_count` 中，原 CSV 也通过 `counts_by_year_json` 保留了它。
年度数据若覆盖全部作品、每刊每年唯一且数值可靠，可以汇总得到期刊 OA 总量；
本库年度表已有异常，故建议用论文数据核验或重建，不能把这个建议写成“库中没有 OA 数据”。
应区分“直接保留、从已有汇总表推导、从论文核验或重算、补取外部属性”四种情形。

## 1. 哪些需要重算，怎样计算

**约定任务：采用可核查的官方定义与公开计算代码，避免仅按字段名称猜算法。**

OpenAlex 在[通用属性说明的 summary_stats 小节](https://help.openalex.org/data/common-attributes/#summary_stats)
建议严谨分析基于底层论文计算。本报告以官方公开
[CreateSourcesApi 代码的固定版本](https://github.com/ourresearch/openalex-walden/blob/7021748a6946c262484437b356f355d2b9e1a494/notebooks/sources/CreateSourcesApi.ipynb?plain=1)
作为具体算法依据；它是 2026-09-16 的公开实现，不是对 January 2026 数据库建库算法的证明。
下面的 BigQuery 连接和实施顺序是本项目的适配建议，并非官方提供的本库 SQL。
下文 OA 指开放获取；primary source 指作品主要发表或存放的载体，期刊作品通常对应其发表期刊。

| 字段 / 处置 | 计算方式与口径 | 需要新增的表 |
|---|---|---|
| **重建** `counts_by_year` | 按期刊与论文发表年份分组，分别统计论文数、`is_oa=true` 的论文数、累计 `cited_by_count` 之和。原年度表已有三项数值完全相等和重复记录的异常，不能只去重后继续使用 | `works` |
| **已有年度值，可汇总；本库建议核验或重建** `oa_works_count` | 现有 `sources_counts_by_year.oa_works_count` 已提供年度 OA 数。若年份覆盖完整（含无年份作品的处理）、每刊每年唯一、定义一致且值可靠，可按期刊求和；本库存在异常，建议用 `works` 中 `is_oa=true` 的作品数核验或重建。未知 OA 状态另计，不解释为 closed | 年度表已纳入；选择论文核验或重建时才需 `works` |
| **补算** `summary_stats.h_index`、`i10_index` | h-index：论文累计被引数降序排列，取“被引数不小于排名”的最大排名；i10-index：累计被引至少 10 次的论文数量 | `works` |
| **按明确参考年补算** `summary_stats.2yr_mean_citedness` | 当前公开代码对“发表年份 ≥ 参考年 T−2”的论文求累计被引数平均值；包含 T 当年，且代码未设未来年份上界。必须记录 T，报告未来年份数量，不能悄悄换成另一种窗口 | `works` |
| **补算** `topics` | 使用每篇论文的**全部主题**，按期刊×主题统计独立论文数；按数量降序取前 25 个，并列按完整主题 ID 排序。不能只用 `primary_topic_id` 代替 | `works`、`works_topics`、主题及学科字典 |
| **补算** `topic_share` | 本刊属于某主题的独立论文数 ÷ **全库有 primary source 的作品中**属于该主题的独立论文数；分母包含非期刊载体，不能先筛成 journal-only。保留 7 位小数，按份额单独取前 25 个 | 同上；额外计算全库主题分母 |
| **可推导，需对照验证** `first_publication_year`、`last_publication_year` | 按[官方字段定义](https://help.openalex.org/data/sources/attributes/#first_publication_year)取所属作品发表年份的最小值、最大值。当前公开 API 组装代码读取另一张预计算表，未在本段 SQL 中计算这两项；MIN/MAX 是基于定义的适配方案 | `works` |
| **保留并交叉核对** `works_count`、`cited_by_count` | 原 `sources` 已有；重算时同时统计作品数与累计被引总和，用于检查期刊作品集合与已有总量是否一致，先保留差异，不直接覆盖 | `works` |

这里的“论文”包括库中归属于期刊的各种 work 类型。当前公开代码没有只保留 article
或排除撤稿记录；如研究另设筛选，应另列为研究指标，不能称为 API 原值。

上表列的是本库拟采用的核验与修复路径，不表示每个指标只能从论文计算。
完整可靠的年度表也可能支持首末发表年份，以及同一窗口的“被引数总和 ÷ 作品数总和”；
后者需额外确认被引数缺失时的分母与官方平均值一致。h-index 和 i10-index 则无法仅由
年度作品总数与被引总数还原。不能把所有缺少独立列的字段统一归为“必须从 works 重算”。

**两个容易算错的地方：**当前公开实现中的年度被引量，指“某年发表的论文截至数据版本
累计被引多少次”，不是“期刊在该年收到多少次引用”；两年平均被引也不是传统 Journal
Impact Factor。[旧官方说明](https://github.com/ourresearch/openalex-docs/blob/main/api-entities/sources/source-object.md)
与当前代码在这两项上存在差异，故本方案明确选择“对照当前 Source JSON 的公开实现”，
而不把不同定义混在同一列。

## 2. 最少需要新纳入哪些表

**约定任务：保留一刊一行，只增加恢复上述指标所需的表。**

| 表 | 连接与用途 |
|---|---|
| `works` | `sources.id = works.primary_source_id`；提供 work ID、发表年份、OA 状态、累计被引数。年份缺失时，按公开代码用 `publication_date` 的年份作后备 |
| `works_topics` | `works.id = works_topics.work_id`；提供全部主题关系，按 `(work_id, topic_id)` 去重计数，不把 `score` 相加当篇数 |
| `topics` | `works_topics.topic_id = topics.id`；补主题名称及 `subfield`、`field`、`domain` 的 ID |
| `subfields`、`fields`、`domains` | 分别用 `topics.subfield/field/domain` 连接对应字典 `id`，补分类名称 |

**核心新增共 6 张表。** 其中 `topics.works_count` 的官方定义是以该主题为**主主题**的
作品数，不能直接拿它作“全部主题关系”的份额分母。
[主题定义与计数区别](https://help.openalex.org/data/topics/#works_count)

`works_primary_location` 可用于核验 `works.primary_source_id` 的映射，属于校验表；
它的 `id` 与 work ID 的一致性仍需检查。不要把 `works_locations` 中所有存放位置都当作
发表期刊。`works_counts_by_year`、`works_referenced_works` **不是上述公开实现所必需的表**；
只有另算“某年收到的引用”等不同口径时才考虑纳入。

执行前先验证 `works.id` 唯一性、期刊连接覆盖、年份及被引数缺失、主题关系重复与字典
匹配情况；字典名称与分类层级也要核对版本。引用数缺失时另报覆盖，不默认为真实零引用；
h-index 在已知引用数中无满足排名时取 0，引用数全缺失则另标未知。公式采用的空值规则也须记录。
每类指标独立汇总至一刊一行后再合并，避免主题和年份明细互相乘出重复记录。

## 3. 哪些不应靠重算补出

**约定任务：区分可以统计的指标与需要额外来源的期刊属性。**

优先从完整原始 Source JSON 或 API 补取：

- **历史与价格：**`apc_usd_by_year`、`is_in_doaj_since_year`、`oa_flip_year`、
  `is_high_oa_rate_since_year`。当前 APC 或 OA 状态不能证明过去的价格或状态。
- **名单、平台与状态：**`listed_in`、`is_core`、`is_in_scielo`、`is_ojs`、
  `is_preprint_repository`、`is_high_oa_rate`。不根据期刊名、网址或自行选定的 OA 阈值填写。
- **名称与标识：**`alternate_titles`、`ids.wikidata`。完整 `ids` 中的 OpenAlex ID、
  ISSN 可用现有列重组；固定版本公开代码将 `ids.mag` 写为 source 数字 ID 的字符串，
  该映射可保留版本依据后复现，不能把整组 `ids` 都判为缺失。

这些属性的含义见[官方 Source 字段说明](https://help.openalex.org/data/sources/attributes/)。
当前可访问的 US/EU 两库均未发现完整 Source JSON 表；维护者公开代码指向的
`multiobs.projectdb_openalex_2026_01.sources` 返回 403，尚未确认其存在状态、内容或访问权限。
具体线索见[原始快照加载代码](https://github.com/multiobs-ig-unicamp/openalex/blob/70207ac983f2a66b4b656b7b8da0fab6c8f98c0c/download_openalex.py#L199)。

## 4. 已核验的例子与下一步

**约定任务：用导师指定的 Journal of Communication（S107737141）检验解释是否成立。**

下面是已执行 UNION ALL 查询中的年度分支；结果直接来自原表，不是通过重算论文得到的：

```sql
SELECT 'year' AS kind, TO_JSON_STRING(t) AS data
FROM `multiobs.publicdb_openalex_2026_01_rm.sources_counts_by_year` AS t
WHERE source_id = 107737141 AND year IN (1951, 2024, 2025);
```

实际作业还同时读回主表、APC 和组织层级。
2024 年原表的发文量、OA 发文量、被引量均为 192，并有两条相同记录；9 月 29 日读取的
API 对应值为 52、23、456。两者版本不同，不能把全部数值差异认定为导出错误；
但原表已有的三项等值与重复，证明该异常发生在导出之前。重跑原导出 SQL 后，这本期刊
的全部 32 列与旧 CSV 一致。

当前 API 的两年平均被引可作一个小规模算术核验：

| API 年份 | 发文量 | 该批论文累计被引量 |
|---|---:|---:|
| 2024 | 52 | 456 |
| 2025 | 56 | 233 |
| 2026 | 17 | 2 |

`(456 + 233 + 2) / (52 + 56 + 17) = 5.528`，与样例 API 的
`summary_stats.2yr_mean_citedness` 相等。该算术已实际执行，支持本例采用当前公开代码
的解释；它没有验证全部期刊，也没有证明历史 BigQuery 输入能够复现今天的 API。
[样例 API](https://api.openalex.org/sources/S107737141)

建议先固定数据快照与参考年，用样例核验作品归属、去重及公式，再执行六表补算；
无法计算的原始属性另行补取。历史库重算值与当前 API 值保留各自日期和来源，
不合称一个时间点的完整快照。

本轮读取范围：官方 Common attributes、Source attributes、Work attributes、Topics 的
相关完整小节，以及上述固定版本 notebook 的完整 Source 聚合 SQL；没有把搜索摘要当作
公式依据。原始核验见 `artifacts/upstream-export-verification-2026-09-29/` 与
`artifacts/raw-source-discovery-2026-09-29/`；本报告的公式样例、来源及审阅记录在
`artifacts/field-recovery/`。它补充[现有合表交付](journal-export.md)和
[76 表连接范围](table-scope.md)，不表示新版 CSV 已完成或上传。
