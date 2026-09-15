# 会前研究准备报告：BigQuery 权限、替代数据与任务进展

> 展示入口已于 2026-09-15 调整为[由 R 实际运行的简短会议报告](../ojs-journal-metadata/analysis/crossref-meeting-report.qmd)。
> 本页保留先前的技术核验和后续方向记录，不再作为本次导师会议的展示稿。

数据与权限核验：2026-09-14；报告整理及 WoS 补充检查：2026-09-15。时区：Asia/Shanghai。面向 2026-09-15 16:00–16:30 会议。
所有者：`openalex-journal-baseline`；状态：**Exploratory Analysis**。
本报告整合 INVIS-5 至 INVIS-11 的实际证据，不把可运行代码、候选数据或准备稿等同于正式研究完成。

## 1. 当前可以做什么

**你在 `userdb_yann_jyal` 的数据集 ACL 中是 OWNER，但在 `insyspo` 项目下仍不能运行 SQL。**
指定这个默认数据集后，最小查询 `SELECT 1` 仍被拒绝，缺少的是项目级
`bigquery.jobs.create`。数据集拥有者身份与创建查询作业的权限属于不同层级。

其余工作可以继续，而且已经实际执行了两条路线：一是离线审计此前合并的 PKP/OJS
数据；二是通过 Google 官方 `tabledata.list` 读取已有权限的 OpenAlex 实体表，在本地
筛选和匹配。后一条使用现有的表读取权限，不需要创建查询作业。
[官方表数据读取说明](https://docs.cloud.google.com/bigquery/docs/managing-table-data#browse-table)。

已完成的新读取包含 **260,789 条 source、209,799 条 journal、全部 21 个核心字段**。
因此，无须等 SQL 权限修复才能准备会议、核对字段或制作候选 Scopus 匹配数据。
但最终快照、关联表范围、WoS 名录、SURFdrive 目的地及导师种子文献仍各有独立缺口。

| 计划项 | 本次已交付 | 尚未完成 / 本次判断 |
|---|---|---|
| INVIS-5 Crossref 增量 | 98,273 × 81 全量离线审计、7 个严格增量实例、字段用途、真实空值与版本证据 | 会前范围可供人工审阅 |
| INVIS-6 访问 | 账号／数据集角色复测、精确 SQL 错误、全表替代读取及独立读回 | 替代路线可审阅；SQL IAM 仍待管理员处理 |
| INVIS-7 快照与行约定 | 两个可见候选差异清单、可重现的 journal 定义和关联表约定 | 可供审阅；January 2026 与第三候选未定位，最终版本未定 |
| INVIS-8 全期刊元数据与 SURFdrive | August 2025 核心期刊表已在本地完整取得 | 关联表提取／最终快照／远端交付未完成 |
| INVIS-9 Scopus / WoS 标签 | 官方 Scopus August 2026 名录精确匹配、全行保留 | WoS 参照未取得；跨年度、类型和历史覆盖需确认 |
| INVIS-10 BorutaSHAP | 特征可用性审查及可执行的研究顺序 | 未拟合模型；不能以未知或历史未列出作为确定负例 |
| INVIS-11 文献 overview | 18 篇既有笔记盘点及下文探索性概述 | 未确认导师种子接收，未完成新一轮种子引用链 |

## 2. 权限复测的证据

本次使用已有 Google Cloud CLI 及已完成授权的 ADC，账号为研究者本人。
没有修改 Google 项目默认设置、IAM、计费或云端数据。

| 检查 | 实际结果 | 可以证明的范围 |
|---|---|---|
| `bq show --dataset insyspo:userdb_yann_jyal` | 成功，US；本账号 ACL role=OWNER | 数据集角色和元数据可见 |
| 列出 `userdb_yann_jyal` 表 | 命令成功，返回零张表 | 当时该账号没有列到表；没有目标表可验证其具体行读取 |
| 在该默认数据集执行常量 SQL | 失败，`bigquery.jobs.create` denied | `insyspo` 不能创建查询作业 |
| 读取 August 2025 sources | 27 页完整成功 | 该实体表全部核心列可读，不代表其他表均可读 |
| 写入、建表、删除 | 未执行 | 不声称已验证实际写权限 |

正确的最小 SQL 复测命令：

```sh
/Users/yann.jy/.local/google-cloud-sdk/bin/bq \
  --headless=true --project_id=insyspo \
  --dataset_id=insyspo:userdb_yann_jyal --location=US --format=prettyjson \
  query --use_legacy_sql=false --maximum_bytes_billed=1 \
  'SELECT 1 AS access_test'
```

2026-09-14 23:39:08 中国时间，该命令 exit 1：

```text
Access Denied: Project insyspo: User does not have bigquery.jobs.create permission in project insyspo.
```

原始命令／输出保留在 `docs/testing/artifacts/bigquery-access/userdb-query.json`。
初次误用 CLI flag 的失败另存 `userdb-query-cli-flag-error.json`，未当作权限证据。
管理员仍可授予 `roles/bigquery.jobUser`，或提供已授权且计费安排明确的执行项目；本次
未向他人发送权限请求。官方 MCP/CLI/API 使用相同底层 IAM，单独换客户端不能修复 SQL。
完整历史与复现见[访问记录](../../docs/testing/bigquery-access.md)。

## 3. 旧合并数据：Crossref 带来了什么

### 3.1 母体、来源与保存一致性

已有 `simple_ver` 全量 Parquet 为 **98,273 行 × 81 列**：19 个 PKP 原字段、
38 个 OpenAlex 顶层字段、11 个 Crossref 顶层字段、13 个派生／匹配证据字段。
98,273 个 PKP 行身份和全部 19 个原始字段均保持一致。
该母体起点是 PKP Beacon V7，不是全部 OpenAlex 期刊。

有效 ISSN 行为 **72,084**；无有效 ISSN 的 **26,189** 行在两个来源均为
`not_attempted`，必须保留为独立状态。OpenAlex 唯一匹配 54,347 行，Crossref 唯一匹配
52,630 行。下表中的单位均为 **PKP 行**，不是已消除同刊重复的全球期刊数。

| OpenAlex 状态 | Crossref unique | Crossref ambiguous | Crossref unmatched | Crossref not_attempted |
|---|---:|---:|---:|---:|
| unique | 52,519 | 347 | 1,481 | 0 |
| ambiguous | 104 | 93 | 1 | 0 |
| unmatched | **7** | 0 | 17,532 | 0 |
| not_attempted | 0 | 0 | 0 | 26,189 |

严格“Crossref 有唯一记录而 OpenAlex 未匹配”的只有 **7 行**，占全部 PKP 行
0.0071%、有效 ISSN 行 0.0097%。另有 **104 行**是 OpenAlex 歧义、Crossref 唯一；
它们不能混入“OpenAlex 没有信息”。未匹配也不证明数据库中绝对不存在记录，只说明
保存的标识符匹配没有找到候选。

Crossref 原始目录缓存记录获取于 **2026-08-03 03:14:42 UTC**，168,907 个目录记录。
OpenAlex 共 1,031 个批次；首末批缓存的记录时间分别为当日 01:54:09 和 02:42:08 UTC。
这些是 API 缓存来源，**不是 January 2026 BigQuery 快照**。本次没有重取它们。
两个 expanded 缓存的所有对应字段与 Parquet 逐格值和类型一致（忽略 R 向量 names），
并且 source key 与原始目录／批次缓存 MD5 关系一致。

### 3.2 七个可展示的具体实例

以下是保存快照中的 Crossref 标题与 DOI 总数；这是匹配实例，尚未作人工身份裁决。

| Crossref 标题 | 匹配候选 ISSN 集合 | total-dois |
|---|---|---:|
| Usrotuna Journal of Islamic Family Law | 3089-1272 | 5 |
| Saqifah Jurnal Hukum Ekonomi Syariah | 2548-4974, 3048-2844 | 32 |
| JBMP Jurnal Bhakti Muhammadiyah Papua | 3124-1522 | 20 |
| Research Journal of Human and Social Aspects | 3006-9696, 3006-970X | 7 |
| Collection of Scientific Papers | 2720-8257 | 25 |
| Stout in Agriculture and Animal Science | 2979-2835 | 2 |
| African Journal of Multidisciplinary Research and Reviews | 3142-5917, 3142-5925 | 1 |

全部七条的 `backfile-dois` 均为 0，当前 DOI 数大于 0。对它们不能把 backfile 覆盖率 0
解释成“旧文献元数据质量为零”：其旧文献分母本身为零。实例完整的 PKP 行号、原标题、
OAI 地址、匹配状态与 Crossref URL 保留在
**实例 CSV**（本地产物：`../ojs-journal-metadata/artifacts/premeeting-crossref-audit/crossref-only-examples.csv`）。

### 3.3 字段的增量价值

| Crossref 字段 | 可以提供的增量 | 解释限制 |
|---|---|---|
| `counts` | DOI 登记总量、current/backfile 分布 | 不等于实际发文总量或 OpenAlex works_count |
| `breakdowns` | 按 issued year 的 DOI 数量 | 不是获取日期；缺少年份不能自动补零 |
| `coverage` / `coverage-type` | 摘要、参考文献、ORCID、机构、资助、许可等元数据存在比例 | 两种表示有重叠；先查分母，再选一种规范表示 |
| `flags` | 特定登记信息是否存在 | false 是观测值；不是质量评分 |
| `issn-type` | 区分印刷和电子 ISSN | 作为身份核验辅助，不单凭它裁决匹配 |
| `ISSN` / `title` / `publisher` | 保留来源身份与名称差异，补充七个实例 | 不覆盖掉 OpenAlex 的独立原值 |
| `subjects` | 当前无可用分类信息 | 52,630 个唯一匹配行全部为 `[]` |
| `last-status-check-time` | 目录摘要状态检查来源证据 | 不是发表日、获取日或 BigQuery 版本 |

这里的“coverage”指登记元数据完整性，而非某索引收录期刊比例。
Crossref 的 current 窗口是响应对应年份及前两年；解释本地快照时依据响应时间，
不能把它随今天日期滚动。参照
[Crossref Participation Reports](https://www.crossref.org/documentation/reports/participation-reports/)。

### 3.4 空 list、NA、零值的实际检查

在 Crossref 唯一匹配的 52,630 行中，`subjects` 没有 R NA，但全部为字符串 `[]`。
原目录对应对象确为 R `list()`。因此“非 NA 率 100%”完全不代表有学科信息。
这解决了当前文件的真实空列表解释；由于会议画面中的那一格没有名字，不能确认
它就是当时被问到的具体单元格。

该分母中 `current-dois=0` 有 6,273 行、`backfile-dois=0` 有 8,905 行、
`total-dois=0` 有 184 行。应保留零值及其分母，不用 NA 一概替换。
另有两个 `openalex_country_code="NA"` 是 Namibia：Journal of the Namibia Scientific
Society 和 JULACE: Journal of the University of Namibia Language Centre。
全局将字符串 `"NA"` 改成缺失，会破坏真实国家代码。

完整 **81 列字段审计**（本地产物：`../ojs-journal-metadata/artifacts/premeeting-crossref-audit/field-audit.csv`）、
**空值实例**（本地产物：`../ojs-journal-metadata/artifacts/premeeting-crossref-audit/empty-value-examples.csv`）
和**缓存来源证据**（本地产物：`../ojs-journal-metadata/artifacts/premeeting-crossref-audit/input-provenance.csv`）
已生成。全量 Parquet SHA-256：
`51adfc1aae72ff1fd6a967c67f820bf4bb60a3f065bd72e41de194841fc3725d`。

## 4. 新母体：已完成的直接读取与数据限制

已读取 `insyspo.publicdb_openalex_2025_08_rm.sources` 的全部 21 列。
读取时段为 2026-09-14 23:42:50–23:47:27 中国时间。

| source 类型 | 行数 |
|---|---:|
| journal | **209,799** |
| ebook platform | 28,966 |
| conference | 10,939 |
| book series | 6,978 |
| repository | 3,979 |
| other | 120 |
| null 类型 | 6 |
| metadata | 2 |
| 合计 | **260,789** |

没有按 ISSN、OA、DOAJ 或发文量删去期刊行。独立读回验证了 260,789 个 source ID 和
209,799 个 journal ID 的唯一性，并比较了 journal 子集全部 **4,405,779 个字段值**。
前后表元数据的 numRows、numBytes、lastModifiedTime 和 schema 一致，27 页累计正确，
输出哈希与 manifest 一致。这些是完整读取证据，不保证并发更新下的事务快照隔离。
[官方分页语义](https://docs.cloud.google.com/bigquery/docs/paging-results)。

以 209,799 条 journal 为分母，关键字段缺失如下：

| 核心字段 | null 行数 | 原始空字符串行数 |
|---|---:|---:|
| `issn` | 70,349 | 0 |
| `issn_l` | 70,356 | 0 |
| `country_code` | 102,604 | 0 |
| `publisher` | 88,593 | 2 |
| `publisher_id` | 209,798 | 0 |
| `host_organization` | 146,769 | 0 |
| `apc_usd` | 185,506 | 0 |
| `homepage_url` | 133,383 | 1 |

`publisher_id` 的 209,798 个 null 尤其值得先核对构建逻辑。存在 publisher 文本而
缺少该键的行不能随意补出版者实体。CSV 将 1,353,621 个 null 单元格和 3 个原始空字符串
单元格均输出为空白；完整 JSONL 保留差别，缺失值统计据此计算。

本账号能看见 March 2025 和 August 2025 两个 OpenAlex dataset，sources 分别有
260,812 与 260,789 行、同为 21 列。没有在当前账号／项目的可见清单找到 January 2026
或第三候选。候选差异、12 张相关表的行数、JOIN 约束与待确认项见
[输入约定](input-contract.md)。其中两张 institution lineage 表为空，两张 publisher
lineage 表各 1 行；子表缺口不能当作真实否定属性。

当前数据是完整 **sources 核心表** 的期刊子集，尚未包含概念、年度计数、学会等关联表
全部内容；也不能以这份2025年候选冒充最终接受的2026年母体。

## 5. Scopus 已执行匹配，WoS 保留未知

### 5.1 参照文件和方法

已从 [Elsevier 官方入口](https://www.elsevier.com/products/scopus/content)取得
[August 2026 source list](https://downloads.ctfassets.net/o78em1y1w4i4/7xtaTxNiNcWRTeZkV86eNy/69cf2d506c905dc299531fdc93049dbb/ext_list_Aug_2026.xlsx)，
26,628,716 字节，SHA-256
`11e81f686401c89fbef28de31d1880388bb7122f35c89e09db6e1848237e9afb`。
主表实际 49,009 个唯一 Source ID，其中 Journal 45,393、Book Series 2,823、Trade Journal
793；Active 32,173、Inactive 16,836。

候选参照使用主表、1,163 行停收补表和 1,031 行带 profile 的 serial conference 表，
保留 worksheet／原行号／Source ID／原始状态／类型／ISSN／覆盖期／停收证据。
905 行 Accepted Titles 单独作为 pending，不作为已经收录。
其余一次性会议列表无 ISSN，不用于期刊标识符匹配。

OpenAlex `issn` 按实际 JSON 数组解析，与 `issn_l` 的有效 ISSN 取并集；校验大小写、
连字符和 ISSN 校验位后做精确交集。无标题模糊匹配，不任取多个候选的第一条。
相同 Scopus Source ID 的多来源行合并为同一候选证据；缺少 ID 的条目保留来源行键。

### 5.2 实际结果与分母

| 状态 | OpenAlex journal 行数 | 含义 |
|---|---:|---|
| `matched_active` | 28,784 | 唯一候选，主表明确 Active |
| `matched_inactive` | 11,934 | 唯一候选，主表明确 Inactive |
| `matched_multiple` | 78 | 多个候选身份，保留全部 |
| `matched_status_unknown` | 261 | 唯一候选但状态未注明 |
| `not_listed_in_reference` | 98,393 | 有有效 ISSN，但参照候选中未匹配 |
| `no_valid_issn` | 70,349 | 无有效 ISSN，不能判断收录 |
| 合计 | **209,799** | 原母体全部保留 |

139,450 行具有有效 ISSN，70,349 行没有；66 行含有至少一个无效 ISSN，但仍有可用
有效标识符。共有 **41,057 行**取得某种参照候选，占全期刊母体 19.57%、有效 ISSN 行
29.44%。这些是跨类型候选匹配率，不是已经裁决的 Scopus 期刊收录率。

仅保留 `Source Type=Journal` 候选时，另一列独立状态为：

| 严格 Journal 状态 | OpenAlex journal 行数 |
|---|---:|
| 唯一 Active | 28,440 |
| 唯一 Inactive | 11,619 |
| 多候选 | 77 |
| 有效 ISSN、无 Journal 候选 | 99,314 |
| 无有效 ISSN | 70,349 |
| 合计 | 209,799 |

严格以参照 `Source Type=Journal` 判断，有 **40,136 行**含 Journal 候选，其中
**28,497 行**含明确 Active 的 Journal 候选；这两个指标允许存在多个候选，不能等同于
已裁决的唯一匹配。916 行只有明确非 Journal 类型候选，应作为分类差异核查。
213 行未匹配候选、但匹配 Accepted Titles，仅表示待加入。78 行多候选需要核对
身份和标题变更，1 行候选缺少 Source ID。另有 293 个 Scopus 候选标识对应多个 OpenAlex 行，仍按原母体保留，未自动合并。全部原始 21 列、行顺序、209,799 个唯一 ID
在写出后逐格读回保持一致。

参照工作簿的 More Info. Medline 明确说明 Source List 并非所有历史 serial 的完整名录，
部分 pre-1996 inactive、少量／零散内容的 title 等不在列表。因此 `not_listed_in_reference`
**不能改写为“从未收录 Scopus”**。OpenAlex 2025-08 与 Scopus 2026-08 又相隔一年，
当前结果只能用于跨时点的候选比较，不能声称同年覆盖率或预测“新收录”。
原始 workbook 本地保留为来源证据，未另行公开转载。

输出：**全期刊 Scopus 候选数据**（本地产物：`artifacts/scopus-2026-08/openalex-journals-scopus-candidates.csv.gz`），
**来源及校验摘要**（本地产物：`artifacts/scopus-2026-08/summary.json`），
**具体匹配实例**（本地产物：`artifacts/scopus-2026-08/findings.md`）。

### 5.3 WoS 的实际缺口

Clarivate 2026-03-06 更新的[官方说明](https://webofscience.zendesk.com/hc/en-us/articles/44444401541521-Collection-Development-Tools)
将 SCIE、SSCI、AHCI、ESCI 完整名录下载列在具备 Web of Science Core Collection 访问的
使用情景下。公开期刊查询入口不等于已取得完整可下载参照。
本次对[官方下载入口](https://www.webofscience.com/wos/mjl/collection-list-downloads)的网页抓取
返回 403；in-app 浏览器导航一度超时，随后标签列表确认已跳到 Clarivate 登录页。
再检查 Chrome 时，浏览器连接连续失败，新标签尚未创建，未能判断其已有登录。
**这些都不是账号无机构订阅的证明**。当前没有取得完整名录，也没有确认你的机构登录是否可用。

已向用户询问是否有可用的机构订阅登录；本次不把 WoS 状态填成 0，也不用 DOI、DOAJ、
OpenAlex `is_core` 或第三方评分代替 WoS 收录标签。获得合法参照后，可沿用 ISSN
校验／全行保留原则，并分开保存各 collection 的结果。

## 6. 现在能否开始 BorutaSHAP

可以准备分析约定，但当前不足以报告有效的收录预测结果。旧 OJS 数据可以检验字段
解析与缺失值处理，却不能充当新全 OpenAlex 母体；新的 Scopus 结果也尚未定义可靠
的研究标签。没有运行训练或生成虚构模型排名。

建议按以下顺序实施，作为待审阅的方法提案：

1. **确定结果定义与时点。** 先区分“名录匹配”“当前 active 收录”“曾经收录”和“未来首次收录”；最后一种需要起点、终点及历史状态，不可由两份不同年文件直接推导。
2. **固定分析分母。** 将缺 ISSN、候选歧义、参照范围不完整和确定负例分开。保留全母体流程图，报告进入模型与排除部分的字段差异。
3. **审核特征。** 国家、规模、OA／DOAJ、APC、组织等只作候选因素。语言／学科目前未从核心表完整取得；publisher_id 极稀疏，不能直接建成无出版者指标。将同义 coverage 表示和高度派生变量去重。
4. **避免信息泄漏。** 预测任务的特征必须来自结果之前；不使用商业索引自身的状态、标识符和由结果生成的字段。横截面引用量／规模可能与收录双向关联，最多支持描述或预测，不能解释为收录原因。
5. **在训练折内做处理与选择。** 缺失处理、编码、BorutaSHAP 筛选仅在训练部分拟合；按出版者／期刊身份检查跨折泄漏，视实际结构选择分组或时间外验证。先建立简单基准，再比较复杂模型。
6. **报告稳定性而非只给排名。** 在独立验证数据上报告分类表现、校准与不确定性，并检查不同随机种子／分组下的特征选择稳定性。SHAP 解释模型贡献，不证明因果或歧视。

以上是本项目的方法建议；当前尚未执行上述模型验证，INVIS-10 不应标记完成。

## 7. 文献：无需 BigQuery 也能完成的会前概述

此次核查了 **18 篇既有 Literature Evidence Notes**，不是重新逐篇获取和阅读原文。
各笔记记录了 DOI、Zotero 标识、阅读时间与范围；Khanna 为 2026-07-16，其余为
2026-07-20。已有材料可支撑下列探索性 overview；未证明这 18 篇就是导师待发送的种子。

学术不可见性需要区分数据库收录、引用传播、评价认可和社会使用。Khanna 等以 2020 年 25,671 种活跃 OJS 期刊为起点，发现常用选择性索引仅覆盖其中一部分，说明从索引出发统计学术出版会遗漏大量活动；但这是特定平台与年份的描述性证据，不能直接视为全球期刊普查或不公正筛选的因果证明。[笔记](../../papers/invisible-communication-science/literature/khanna-2022-recalibrating-scholarly-publishing.md)／[原文 DOI](https://doi.org/10.1162/qss_a_00228)（原文第 2、6 节，尤其表 3）。

一条解释路径是评价制度把收录转化为声望。Alperin 与 Rozemblum 对墨西哥和哥伦比亚 2016 年政策的分析指出，索引和引用分区成为期刊等级门槛，但未检验政策造成的投稿或语言变化。Vera-Baceta 等则显示，WoS 与 Scopus 的语言覆盖差异随学科而改变；数据库内英语占比不能回答某种语言的全部研究有多大概率被收录。[Alperin 笔记](../../papers/invisible-communication-science/literature/alperin-2017-visibilidad-calidad.md)／[DOI](https://doi.org/10.17533/udea.rib.v40n3a04)（第 2.4 节、表 1）；[Vera-Baceta 笔记](../../papers/invisible-communication-science/literature/vera-baceta-2019-web-of-science-scopus-language-coverage.md)／[DOI](https://doi.org/10.1007/s11192-019-03264-z)（手稿第 4–8 页）。

另一条路径是出版基础设施与资源。Bosman 等发现，钻石开放获取期刊在标识符、保存和机器可读元数据方面存在整合缺口，资源与技术能力可能影响进入索引的机会；其横断面和自报资料不能分离这些因素的因果作用。同时，Krawczyk 与 Kulczycki 记录了开放获取和掠夺性出版在论述中的混同，而 Grudniewicz 等的共识定义要求关注具体出版行为。资源不足、开放获取或未被收录本身均不能确立期刊诚信判断。[Bosman 笔记](../../papers/invisible-communication-science/literature/bosman-2021-oa-diamond-journals-study.md)／[DOI](https://doi.org/10.5281/zenodo.4558704)（第 53–74、98–103 页）；[Krawczyk 笔记](../../papers/invisible-communication-science/literature/krawczyk-2021-open-access-predatory.md)／[DOI](https://doi.org/10.1016/j.acalib.2020.102271)（表 4–5、讨论）；[Grudniewicz 笔记](../../papers/invisible-communication-science/literature/grudniewicz-2019-predatory-journal-definition.md)／[DOI](https://doi.org/10.1038/d41586-019-03759-y)（第 211–212 页）。

声望和累积优势提供跨层次的解释参照。Tomkins 等在一次会议审稿实验中观察到，身份可见条件下，知名作者或机构更易获得正面建议；这不是最终录用结果。Bol 等的资助门槛研究与 Traag 等的复制研究表明，早期资助和后续机会有关，而再次申请是不可忽略的路径。由此推到期刊收录，只能形成待检验假设，不能把个人层面的效应直接移植给期刊。[Tomkins 笔记](../../papers/invisible-communication-science/literature/tomkins-2017-reviewer-bias.md)／[DOI](https://doi.org/10.1073/pnas.1707323114)（表 2–3）；[Bol 笔记](../../papers/invisible-communication-science/literature/bol-2018-matthew-effect-science-funding.md)／[DOI](https://doi.org/10.1073/pnas.1719557115)（图 1）；[Traag 笔记](../../papers/invisible-communication-science/literature/traag-2025-matthew-effect-replication.md)／[所读版本 DOI](https://doi.org/10.7554/eLife.109042.1)（图 3、讨论）。

还须保留内容、时间和计量口径的竞争解释。Wang 等发现，组合新颖性与早期和长期引用的关联不同；Evans 的参考文献选择收窄与 Larivière 等的论文队列获引分散，也因观察单位和窗口不同而可以共存。因此，低引用不等于低价值，引用不均也不能单独识别排斥机制。[Wang 笔记](../../papers/invisible-communication-science/literature/wang-2017-bias-against-novelty.md)／[DOI](https://doi.org/10.1016/j.respol.2017.06.006)（表 4–5）；[Evans 笔记](../../papers/invisible-communication-science/literature/evans-2008-electronic-publication-narrowing.md)／[DOI](https://doi.org/10.1126/science.1150473)（图 2）；[Larivière 笔记](../../papers/invisible-communication-science/literature/lariviere-2009-decline-citation-concentration.md)／[DOI](https://doi.org/10.1002/asi.21011)（图 1–3）。

对当前研究的暂定启示是：先把结果限定为特定快照下的期刊索引匹配状态，再考察地区、语言、学科、期刊规模和元数据完整性等候选因素。比较时还须统一分母，并区分缺少标识符、检索失败和确定未匹配。已有 OJS 合并数据可帮助检查字段与假设的可操作性；它仍是平台起点的探索材料，不能替代全 OpenAlex 期刊母体，也不能凭预测关联证明歧视、质量差异或去殖民化进展。以上是本项目的解释与方法建议。


阅读边界：Evans 的补充材料没有取得；Traag 笔记依据 Reviewed Preprint v1，本次未查新。
7 月 20 日旧审计的 17 篇截止记录保留原貌，不能因今天存在第 18 篇而改写过去进度。
已有 Khanna→Alperin/Bosman、Bol↔Traag、Evans↔Larivière 等引用关联，可在收到并确认
导师种子后继续核对。种子接收和新引用链仍未完成，因此 INVIS-11 保留这一阻塞。

## 8. 可复现产物、交付与下一步

代码可从仓库根目录运行：

```sh
# 仅审计已有缓存；不调用 API
Rscript research/ojs-journal-metadata/analysis/premeeting_crossref_audit.R

# 已完成读取的原命令；再次运行须换一个新的 output 目录
python3 research/openalex-journal-baseline/analysis/read_bigquery_sources.py \
  --project insyspo --dataset publicdb_openalex_2025_08_rm \
  --output research/openalex-journal-baseline/artifacts/bigquery-tabledata-2025-08

# Python 需 pandas/openpyxl，复用已下载官方 workbook
python3 research/openalex-journal-baseline/analysis/match_scopus.py
```

实际 Scopus 运行使用 `/Users/yann.jy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`（已具备 pandas/openpyxl）；系统 Python
不一定包含这些库。读取脚本使用标准库和已授权 gcloud ADC；不将 token 写入报告或数据。
只有有效 manifest 且输出哈希一致才认定读取完成。SQL job 没有成功创建，故不存在
可报告的成功 query job ID 或扫描账单验证；本次采用无需 SQL 的官方表读取方式。

| 本地产物 | 作用 |
|---|---|
| **完整 sources JSONL**（本地产物：`artifacts/bigquery-tabledata-2025-08/sources.jsonl.gz`） | 260,789 行全部核心列，保留 null 语义 |
| **journal CSV**（本地产物：`artifacts/bigquery-tabledata-2025-08/journals.csv.gz`） | 209,799 行候选基线 |
| **读取 manifest**（本地产物：`artifacts/bigquery-tabledata-2025-08/manifest.json`） / **独立核验**（本地产物：`artifacts/bigquery-tabledata-2025-08/readback-verification.json`） | 版本、分页、计数、SHA-256、逐格比较 |
| **Scopus 候选输出**（本地产物：`artifacts/scopus-2026-08/openalex-journals-scopus-candidates.csv.gz`） | 母体原始列与匹配证据 |
| **Crossref 审计摘要**（本地产物：`../ojs-journal-metadata/artifacts/premeeting-crossref-audit/summary.json`） | 旧数据完整分母和状态对照 |
| [输入约定](input-contract.md) | 快照、字段、行和 JOIN 边界 |

关键数据 SHA-256：

```text
sources.jsonl.gz
7f94970200c6602ded6e8432c6a340339a914bef2a720b10a5840f2da78f839a
journals.csv.gz
4e805a5f00a93e84da1c748b049df0dc7ae1710aac2afaf8487a01fee1fcfe90
openalex-journals-scopus-candidates.csv.gz
e78df4d801c0b91790b4cd5037fbae9ccb92763250c75b4391484923655f4d72
```

数据、原始证据与渲染件位于各 owner 的 ignored artifacts 目录；提交／推送代码和
报告不代表这些数据已在远端交付。尚未得到 SURFdrive 文件夹链接，本机已检查的同步
目录也未出现 SURFdrive，因此没有上传到猜测目的地。本次先完成本地材料与可读报告，并打包为约 50 MB 的本地 ZIP；包内含两份 HTML、核心数据与已引用审计证据，未包含完整 Scopus 原始工作簿或旧 PKP 原表。

交付检查已完成：HTML 的中文段落与任务表经浏览器实际显示核验，报告及输入约定共 13 张表、79 个链接；本地文件链接和目录锚点无缺失。数据包的 17 个内容文件逐一核对大小与 SHA-256，并通过 ZIP CRC 及包内内容哈希检查。读取和匹配脚本均有独立代码／产物审查，未发现影响本次结论的问题。文档治理检查通过。Plane 中 INVIS-5 与 INVIS-7 可提交人工审阅；INVIS-6 保留 SQL 权限阻塞，并记录核心表替代路线已成功，其余任务保留各自依赖。

会前最少需要明确的外部事项是：接受哪个快照、January 2026 的确切位置及相关表范围；
WoS 机构登录或有版本的完整名录；SURFdrive 接收文件夹；导师种子来源。
SQL 权限可并行请管理员处理，不再阻断已验证的核心表替代读取。
后续对远端数据交付必须回读文件名、大小和可下载内容；对新名录匹配须保留版本与
状态证据。以上缺口未解除前，不宣称完整基线、双索引标签、模型和远端交付全部完成。
