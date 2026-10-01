# 不依赖旧 ISSN／ID 的 OpenAlex 获取方案

日期：2026-10-01。性质：获取方案建议与有限范围实测；尚未更换已接受的研究母体，
没有启动全量新下载或模型分析。

**约定任务：**比较 BigQuery 合并、旧 ISSN／ID 补取和直接 OpenAlex 获取，
推荐能服务期刊 Scopus 收录预测的可执行路线，并核验接口、字段、成本与资源限制。

## 建议及研究范围

建议以 **当前 Source API 直接列举的 journal 为新母体，保存完整响应，再从 Works API
取得所需汇总，最后连接有版本的 Scopus 名录**。旧 BigQuery 清单用于历史对照，
不作为新母体的入场条件。这里是一条 OpenAlex Source ID 一行，不声称覆盖全球实际所有期刊。
本建议以当前横截面探索为目标；严格同一发布日期的 Sources／Works 分析应改用同一官方快照。

| 路线 | 适用性与选择理由 |
|---|---|
| 固定 BigQuery 版本内合并、重算 | 适合研究那个历史版本；需核验建库来源与聚合定义。单一历史版本本身不是错误，但不能声称等于当前 API |
| 旧 ISSN／ISSN-L 请求当前 API | 适合身份补查；历史号码缺失或对应变化使它不适合发现当前全集 |
| 旧 Source ID 请求当前 API | 适合固定旧母体的纵向审计；成功子集遗漏当前清单新增或旧表没有的身份，并保留大量 404 |
| **当前 Source API 直接列举** | **推荐用于本轮当前期刊母体与探索**；无旧清单匹配前置条件，接口已实际成功；仍需分页核验和保存版本 |
| 同一官方快照的 Sources＋Works | 严格同版研究的较佳路线；资源需求与实时性不同，本机不能直接存放完整 Works |

研究用途依据[模型用途与合并规则](model-data-structure.md)：预测期刊 Scopus visibility，
候选特征包括国家、学科、OA／APC、产出、引用与发表语言。API 能提供标准 Source 指标，
但研究自行定义的年份窗口、语言比例、主题表示仍要计算，不能由“完整 JSON”代替。

## 可重跑的最小核验

[实测脚本](analysis/probe_direct_acquisition.py)不读 BigQuery 或旧 ID 清单。
它读取三页完整 Source 对象、官方快照清单及一个小分区，并核验论文语言汇总。
凭据通过现有环境／本地 `.env` 读取，只发往 OpenAlex；不写入回执或 Git。
每次指定新的、所属 owner 下的产物目录：

```sh
uv run --with requests python \
  research/openalex-journal-baseline/analysis/probe_direct_acquisition.py \
  --output research/openalex-journal-baseline/artifacts/direct-acquisition-probe-new-run
```

Source 列举的请求为：

```text
GET https://api.openalex.org/sources?filter=type:journal&per_page=100&cursor=*
```

不加 `has_issn`、DOAJ、OA、活跃度筛选，也不使用删减字段的 `select`。
下一页使用响应的 `meta.next_cursor`，按[官方分页规则](https://help.openalex.org/api/paging/)
直到终点。100 是正式支持的单页大小；普通 page 分页只能取前 10,000 条。

## 本轮实际结果

2026-10-01 上海时间 13:00–13:01 的最后一次完整核验产物在
`artifacts/direct-acquisition-probe-2026-10-01-verified/`。其中 `probe-summary.json`
记录请求、HTTP 状态、字节数、哈希、时间和核验范围。

| 核验项 | 实际观察 | 能支持的判断 |
|---|---|---|
| 当前 journal 总数 | 三页均报告 207,602 | 直接列举无需先提供期刊 ID／ISSN |
| 三页对象 | 300 个不同 ID，均为 journal；每个 39 个顶层字段 | 游标前进、页面未重复、完整对象可直接取得；不是全量下载证明 |
| 官方 Sources JSONL 清单 | 2026-09-23；256,981 个全部类型 Source，196 文件，333,123,776 压缩 bytes | 可以只下载 Sources；不需连带下载所有 Works |
| 小快照分区 | 699,521 bytes，505 对象；字节数与对象数符合清单 | 匿名下载和 gzip／JSONL 读取已执行 |
| 同一个期刊的字段集合 | 快照与当前单刊 API 都有 39 个顶层字段，无单侧字段 | 该例快照保留 Source 对象结构；不同日期的值不要求相同 |
| 官方 Works JSONL 清单 | 同为 2026-09-23；476,196,327 Works；659,026,072,445 压缩 bytes | 全 Works 约 659 GB，不能把 Sources 的小体量推广到 Works |
| Journal of Communication 语言例 | 2020–2024 共 255 Works；English 255；含未知的分组总数等于总数，终止页已检查 | 论文语言汇总可由 API 完成；这个窗口只是实测例，不是已接受的分析窗口 |
| English 按发表期刊分组 | 首页 100 个 Source；Journal of Proteomics 986 Works，经独立该刊查询得到同值 | 批量取得“语言×期刊”计数的路线可执行；尚未遍历全部语言／期刊 |
| 缺失语言按发表期刊分组 | `language:null` 返回 509,044 Works 的计数；首页 100 组；Pediatric Nursing 25，经独立查询得到同值 | 缺失语言可单独保留；尚未遍历全部分组 |

Sources 清单前后内容一致，两个实体清单内部文件记录数和字节数之和均与总值相符。
以上是本次请求及内容检查，不是全量新母体完整性或模型可用性认证。
官方[快照说明](https://help.openalex.org/access/snapshot/)介绍 JSONL／Parquet、实体分目录及结构；
实际发布日期以本次 manifest 和 `RELEASE_NOTES.txt` 为准，不能根据计划发行日猜测。

历史对照来自已核验的[完整 Source 与重试记录](source-api-csv.md)：旧母体 209,799，
成功 184,302，404 为 **25,497**。两轮全量重试仍全部 404；17,126 个旧失败记录没有有效
历史 ISSN。号码补查得到的多数当前候选已经在成功集内。因而不能把失败都称为“ID 修改”，
也不能把候选直接加回原母体；直接列举新母体是另一项分析版本。

## 从期刊对象到研究特征

1. **期刊层原始数据。** 保存全部 Source 字段、ISSN 集合、获取时间及原始响应。
   Source 标准统计沿用返回值，不从旧库重建后假装同版。
2. **论文层汇总。** 固定年份、Work 类型和 corpus，按 `primary_location.source.id`
   归刊。语言可以先列出完整语言分组，再逐语言筛选 Works、按发表 Source 分组并翻页；
   未知语言单独查询、保留计数。这样取得的是计数表，无需下载每篇论文。
   当前分组接口只提供单维聚合；两维结果由明确的过滤＋分组组合取得。
   实测已核验 English 和缺失语言首页及独立计数；全语言穷尽、全量分母对账
   与实际请求预算仍需在生产采集前完成，不能把本例写成已完成的全部语言数据。
   `language` 是 OpenAlex 提供的语言标记，本轮没有核对论文全文的实际语言。
3. **主题范围。** 完整 Source 响应的 `topics`／`topic_share` 不等于全部主题分布。
   当前固定公开聚合代码各取 top 25；若研究需要完整学科比例，应按 Works 的
   `primary_topic` 或全部 `topics` 聚合，并明确单一主主题或多重归属口径。
   Source `topic_share` 是对全库该主题的贡献份额，不是刊内比例。
4. **外部结果标签。** Scopus 名录仍是外部输入；OpenAlex API 不会自动消除跨库匹配。
   用新母体的全部有效 ISSN 匹配，保留 Active／Inactive、版本、歧义和未知。
   无 ISSN 或匹配失败不能统一编码为 0。直接表达结果或用于构建结果的字段不进入 X。
5. **时间解释。** 当前属性与同期名录可支持横截面关联／分类探索；预测未来首次收录
   需要收录前的属性、历史标签和时间切分。Boruta／SHAP 的重要性不证明因果。

## 成本、空间和全量验收

按[官方费用](https://help.openalex.org/access/example-costs/)，普通列表调用每次
0.0001 美元，免费 key 每天 1 美元。当计数为 207,602、每页 100 时，Source 主分页约
2,077 次，含终止页约 2,078 次，约 **0.2078 美元的额度**，未含重试和审计。
这是预算估计，不是已执行账单；免费额度剩余量仍须开跑前核验。
Works 汇总的成本取决于实际“期刊×语言”分组量，不能沿用 Source 的 0.21 美元估计。
逐刊单独查询的请求量会更高；优先实测批量分组再决定预算，不自行购买额度。

本机这轮空间检查只有约 **0.5–0.6 GiB** 可用；此前原始 JSON＋未压缩 CSV 各需数 GB。
因此全量新采集应先使用有足够空间的外接盘／工作环境，或落实流式压缩与远端存储。
当前接口已验证，但本机原有“逐刊 JSON＋未压缩 CSV”落盘方式受空间阻碍，不能直接开跑。
完整 Works 快照还需数百 GB 的压缩存储与处理资源；只为语言统计不推荐走这条路线。

API 的记录持续更新：同一个服务并不提供整个游标遍历的事务快照。
保存获取区间和原始对象可重现本地结果，但不能声称所有字段来自同一瞬间。
全量验收至少核对分页结束、ID 唯一性与类型、开始／结束计数、字段保留及哈希；
计数相等也不能单独证明集合不变。论文汇总与期刊母表不一致的 ID 应记录并复核，
不能静默丢弃或填 0。若必须严格同版，使用同一 release 的 Sources 与 Works，
下载前后核对 manifest 并冻结本地副本，按[同步说明](https://help.openalex.org/access/sync/)
处理分区和更新。不要将旧 BigQuery Works 与当前 Source 属性连接后称为同版数据。

官方 [CLI](https://help.openalex.org/access/cli/)目前主要提供 Works 元数据和内容下载；
不应把安装它等同于已经具备全 Source 获取或研究特征表。公开代码有助于核对字段计算，
重新运行整个 OpenAlex 建库项目不是本任务最短路径。
