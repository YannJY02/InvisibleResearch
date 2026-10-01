# 不依赖旧 ISSN／ID 的 OpenAlex 获取方案

日期：2026-10-01，追加 BigQuery 扫描成本与分层 ISSN 实测后修订。
性质：获取方案建议与有限范围实测，保留当时观察范围。后续用户已明确授权两条路线
均实际执行，见[两套完整期刊数据交付](dual-route-delivery.md)；原已接受母体不被替换，
模型分析仍未启动。

**约定任务：**比较 BigQuery 合并、旧 ISSN／ID 补取和直接 OpenAlex 获取，
推荐能服务期刊 Scopus 收录预测的可执行路线，并核验接口、字段、成本与资源限制。

## 建议及研究范围

考虑用户追加的语言聚合、成本及现有数据复用要求，建议改为 **已有 BigQuery 期刊母体与
Works 云端聚合为主，复用已取得的 Source API 属性，用 ISSN 补查 ID 失败项，再匹配
导师提供的公开 Scopus 名录**。不重新下载全 Works，也不以“必须有 ISSN”缩小母体。
本建议面向当前横截面探索；这里是一条 OpenAlex Source ID 一行，不声称覆盖全球实际所有期刊。

BigQuery 派生统计保留历史 Source ID 和数据版本，API 属性保留当前 ID 与获取日期，
二者不能称为同版。优先在已有 BigQuery 数据范围内定义主分析的时间窗、语言和主题指标；
当前 API 属性作为有明确日期的补充数据。它们能否共同进入最终模型仍取决于目标标签和
时间口径，未来首次收录预测不能直接使用收录后的当前属性。严格同版且需要完整 API 对象
结构时，应换用同一官方 Sources／Works 快照或核验可用的同版 BigQuery 数据，而非只换匹配键。

| 路线 | 适用性与选择理由 |
|---|---|
| 固定 BigQuery 版本内合并、重算 | 适合研究那个历史版本；需核验建库来源与聚合定义。单一历史版本本身不是错误，但不能声称等于当前 API |
| 旧 ISSN／ISSN-L 请求当前 API | 适合补查失败项；全母体有 70,349 条无有效号码，不能用这条路线替代所有 ID 获取 |
| 旧 Source ID 请求当前 API | 已取得 184,302 对象，宜复用；25,497 个失败项需另留状态／候选，不能只分析成功子集 |
| 当前 Source API 直接列举 | 适合改研究当前全期刊母体；Source 列举便宜，但旧 BigQuery Works 不自动变成该母体的同期论文数据 |
| **BigQuery 聚合＋已有 API＋ISSN 补查** | **本轮推荐**；减少下载与重复请求，保留无号码记录，显式记录历史／实时版本及候选身份 |
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

## 追加：BigQuery 与 ISSN 的成本比较

**约定任务：**先估算成本，再用旧 BigQuery ISSN 小试；同时核对公开 Scopus 名录，
重新比较哪条路线最适合现有期刊研究。

### BigQuery 语言聚合的实际扫描估算

本轮重新读取的 `multiobs.publicdb_openalex_2026_01_rm.works` 有 `id`、
`primary_source_id`、`language`、`publication_year`、`is_xpac` 等所需列，
527,656,513 行，整张表逻辑大小 166,480,820,797 bytes；没有分区或聚簇。
整张表大小、官方全库压缩包大小和实际查询扫描量是不同数量。

以下 SQL 已实际 dry run，未执行聚合。2020–2024 和排除 XPAC 是成本示例，
不是已接受的研究窗口；`COUNT(DISTINCT id)` 避免同组重复 work 行，跨组的身份／语言
冲突仍须另外核验，空字符串与 null 在正式管线中应明确规范。

```sql
SELECT w.primary_source_id AS source_id, w.language,
       COUNT(DISTINCT w.id) AS n_works
FROM `multiobs.publicdb_openalex_2026_01_rm.works` AS w
JOIN `multiobs.publicdb_openalex_2026_01_rm.sources` AS s
  ON w.primary_source_id = s.id
WHERE s.type = 'journal'
  AND w.publication_year BETWEEN 2020 AND 2024
  AND COALESCE(w.is_xpac, FALSE) = FALSE
GROUP BY source_id, w.language
```

dry run 精确估计 **14,112,759,264 bytes = 13.14 GiB**。按美国区
[按需查询每 TiB 6.25 美元](https://cloud.google.com/bigquery/pricing?authuser=1)
计算，约 **0.0802 美元**，未扣每月免费额度，也未包括额外审计、存储或其他查询。
本次没有核验该计费账号本月额度余额，不能保证正式作业账单为零。
这张非分区表即使仅筛一本期刊，也可能扫描同一批列，不能把 LIMIT／少量结果当作低扫描量。

现有 MCP 每个执行作业上限 512 MiB，低于本查询估算，因此本轮只进行了 dry run。
正式聚合应通过有明确扫描上限的专用导出流程执行，不能把 dry run 成功说成已取得语言表。
只下载聚合后的期刊×语言表，不需把全 Works 搬到本机。
SQL、原始 dry-run 配置／统计和价格换算在下述小试的同一产物目录。

### ISSN 小试先估算、后执行

[分层小试脚本](analysis/probe_historical_issns.py)读取已接受的旧 CSV，核对原哈希，
固定随机种子 20261001，分三层各抽 100 条；分别查询每条记录的全部去重有效 ISSN／ISSN-L。
无号码层只作离线覆盖检查，不发无效请求。旧 404 子集此前已做过号码补查，
复用其经对象哈希验证的回执；本轮新增的是原 ID 成功层的 ISSN 对照，未全量重复查全部号码。

```sh
uv run --with requests python -B \
  research/openalex-journal-baseline/analysis/probe_historical_issns.py \
  --baseline research/openalex-journal-baseline/artifacts/journal-export-2026-01/openalex-journals-2026-01.csv \
  --prior-retry research/openalex-journal-baseline/artifacts/source-retry-2026-10-01 \
  --output research/openalex-journal-baseline/artifacts/issn-stratified-probe-new-run
```

此命令先离线保存 `plan.json`，不调用 API；查看计划后，以同一命令加 `--execute` 执行。
本轮计划记录 276 个去重号码，124 个已有有效回执、152 个需新增单刊查询，
最多为新增查询预留 456 次尝试。官方单刊查询免费，执行前 `/rate-limit` 也确认单刊费用为 0。
实际执行为 152 次单刊请求，无重试；前后免费额度使用量均为 0.003 美元，没有购买额度。

| 分层 | 旧母体记录数 | 小试实际结果 |
|---|---:|---|
| ID 成功且有有效 ISSN | 131,079 | 100 条均回到同一 Source ID |
| ID 为 404 且有有效 ISSN | 8,371 | 100 条均得到不同当前 ID 候选，复用已验证回执 |
| 无有效 ISSN | 70,349 | 100 条均无法走 ISSN 路线；未发请求 |

276 个号码响应均为成功，查询号码均在返回对象的有效 ISSN 集合内。
这是等额分层的接口与身份对照，不能把三组简单平均为全母体匹配率，
也不能把号码候选自动认证成历史合并。既有全量 404 号码审计仍是该失败子集的覆盖证据。
全部旧母体仅 **139,450／209,799 = 66.47%** 有有效 ISSN；
无号码记录中仍有 **53,223** 条此前 ID 查询成功，所以只用 ISSN 会丢掉可获取的数据。

全母体去重有效号码有 209,776 个。逐号码单刊查询费用为 0，但仍需网络和限速时间；
若按此前 20 次／秒的设置，单是发起这些查询就约 2.9 小时，未含失败、退避及处理。
以每批最多 100 号码的列表路线估算，基础约 2,098 批、0.2098 美元额度，
还需考虑返回多页与复核；它并不会因此解决无号码覆盖或历史／当前属性日期差异。
已成功下载的对象没有理由全量再查，优先复用。

执行证据在 `artifacts/issn-stratified-probe-2026-10-01/`：`plan.json` 为事前计划，
`summary.json` 保存分层结果与逐号码来源，`checkpoints/issn/` 是新增响应回执，
`issn-candidates/` 是本轮实际对象；引用的旧回执保留原路径和获取日期。
输入原文件与已接受数据包均未改写。

### Scopus 公开名录的当前访问证据

本轮读回[导师 GitHub #5 评论](https://github.com/invisibleinfo/invisible-research/issues/5#issuecomment-5553748839)，
确认其提供的是[August 2026 公开 Source 名录](https://downloads.ctfassets.net/o78em1y1w4i4/7xtaTxNiNcWRTeZkV86eNy/69cf2d506c905dc299531fdc93049dbb/ext_list_Aug_2026.xlsx)。
[Elsevier 官方入口](https://www.elsevier.com/products/scopus/content)当前仍指向同一文件。
匿名 HEAD 返回 200、32-byte Range GET 返回 206，并核验 XLSX／ZIP 签名和 26,628,716 bytes
总长度；ETag／Last-Modified 与本地 September 14 下载回执相同。
本轮重新计算本地工作簿 SHA-256，与固定哈希一致：
`11e81f686401c89fbef28de31d1880388bb7122f35c89e09db6e1848237e9afb`。
不重复下载完整工作簿；它位于 `artifacts/scopus-2026-08/`。

真实表头包括 ISSN、EISSN、Active or Inactive、Coverage、Source Type、title history 等。
这个公开版本的名录匹配没有订阅／凭据阻碍；WoS 全名单与 Scopus 论文级订阅 API 是其他范围。
主表有 49,009 个 Scopus ID，其中 Journal 45,393；Accepted Titles 属于待收录，不能当成已收录。
应明确目标是“此版本名录出现”还是“Active Journal”，保留 Inactive、未知和歧义。
有效标识符未出现在给定版本的名单，可以用于严格定义的名单成员目标，
不能据此断言从未被 Scopus 收录。名录中的 `Article Language in Source` 仅覆盖其收录来源，
不能拿来替代全母体语言特征，否则会产生与目标有关的缺失／信息泄漏。

### 本轮选择的解释

BigQuery 云端聚合的优势是把已有大表计算成小结果，费用与本地传输都可控；
完整 API 属性已有大量缓存，ISSN 能补查身份变化。因此本轮优先复用这三项成果，
不重复进行整套下载。号码是关联证据，不是版本修复工具。

保留历史 Source ID → 当前候选 ID 的交叉表；多个旧 ID 指向同一候选时不能直接相加
旧语言比例，候选身份、去重与合并规则需先审查。对应不了的期刊保留未知状态，
不能静默删除或填 0。若最后选择当前 API 的全部期刊作为研究母体，则必须报告旧 Works
对该新母体的覆盖缺口，或改用同期 Works；不能将“可用旧库连接”当作“当前全覆盖”。

`same_id` 与 `different_id_candidate` 分别保留。后者的当前 Source 统计可能属于合并后的
对象，不能直接填回一个旧 ID 的属性行。取数审计保留全部旧记录，不代表这些记录已是
独立期刊观察；主分析应先固定身份裁决和可分析样本，候选对应另作审查／敏感性分析。
共享当前 Source／Scopus 身份的记录还需按身份关系分组切分训练／测试集，避免相同
属性或标签跨集泄漏。当前 API 属性如果晚于目标状态日期，也不能仅靠记录日期就消除
预测泄漏；主分析优先使用时间口径合适的历史变量。
