# OpenAlex 全期刊基线输入约定

记录日期：2026-09-14；当前输入更新：**2026-09-15**。所有者：`openalex-journal-baseline`。对应 INVIS-7。
状态：用户已明确改用新 `multiobs`；本轮期刊合并采用 January 2026 US 公共库。
这是探索性数据交付，不代表索引定义或后续模型设计已获接受。

**2026-09-25 范围澄清：**下面的 12 表规则记录的是已执行导出，不是老师明确限定的
全部研究范围。用户要求梳理全部表后，[76 表范围审计](table-scope.md)补充了经论文
到主题、作者、机构的路径。一刊一行不排除使用论文数据作汇总；新指标、年份与分母
仍是建议，尚未写入现有 CSV。缺少 sources_topics 不代表不能通过论文主题补充分类。

## 当前输入与合并约定

用户会后明确指出旧 `insyspo` 已停用，并要求沿用新 `multiobs`、合并期刊表导出 CSV。
[会议记录](../../meeting-reports/2026-09-15-openalex-table-delivery.md)保留该澄清来源；
[交付报告](journal-export.md)记录实际结果、文件和本周安排。

| 项目 | 当前采用的规则 |
|---|---|
| 输入 | `multiobs.publicdb_openalex_2026_01_rm`，US；全部关联表来自同一数据集 |
| 作业项目 | `gen-lang-client-0676290976`（YannJY），US |
| 工作库 | `multiobs.userdb_saurabh_khanna` 的 11 张既有克隆已核验；本次直接查询公共源表，无需重复复制 |
| 观察单位 | `sources.type = 'journal'`；一个非空唯一 Source ID 一行，209,799 行 |
| 核心范围 | 保留 sources 全部 21 字段；不因缺 ISSN、OA 状态或低发文量删行 |
| 一对多信息 | 10 张 sources 子表各按 source_id 聚合成 JSON 列，再 LEFT JOIN；保留全部记录及重复次数 |
| 年份 | counts_by_year 保留所有已存年份，按年份排序；不在此次导出中选择窗口或计算跨年总量 |
| 出版者 | 从 host_organization 的完整 OpenAlex P URL 提取数值 ID，与 publishers.id 精确关联；先核验 publishers.id 唯一；不按名称猜测 |
| 空值 | CSV 用 `\N` 表示 SQL NULL，空字符串仍为空字符串；原值若与标记冲突则失败；JSON 内保留原 null |
| 无子记录 | JSON `[]` 表示该来源没有匹配子行；另记录整张子表为空的情况，不能解释为现实中无关系 |
| 核验 | 合并前后 ID 集合摘要及行数相同；各子表匹配行数、覆盖期刊数与 JSON 数量一致；逐列云端/本地缺失计数一致；重新解析 CSV；记录 SHA256 |

[EU/US 比较](dataset-comparison.md)已核验两库各 76 张表的同名、同 schema、同行数和同大小；
12 张相关表进一步通过全行内容指纹比较。其余 64 张未比较行内容。
本轮检查各输入表的前后元数据稳定；数据集名不证明原始构建时间，也不构成跨作业原子快照。

`sources_concepts` 等六张子表为空；没有 `sources_topics`。这两点在交付中显式保留，
不混入旧 August 的关联行数，也不把 topics 分类表当作期刊—主题映射。
`publisher_id` 在期刊中仅 1 行非空，因此不用它作为覆盖充分的连接键；已核验的
host_organization P ID 有 63,030 行，63,016 行能精确匹配 publishers，14 行没有对应记录。
四张非空子表的原始行数均为按完整记录去重后数量的两倍；本次导出保留重复，
后续数值汇总必须明确去重规则，不能直接累加重复子行。详见交付报告的全文件核验。

## September 14 已落实的候选行定义

| 项目 | 当前约定与实测 |
|---|---|
| 执行候选 | `insyspo.publicdb_openalex_2025_08_rm.sources`，位置 `US`，实体表 |
| 读取方式 | 官方 REST `tabledata.list`，27 页；不提交 SQL job |
| 原表分母 | 260,789 行，260,789 个非空唯一 `id` |
| 期刊筛选 | 严格 `type == "journal"`，209,799 行；不加 OA、DOAJ、活跃度或 ISSN 过滤 |
| 观察单位 | 一条 OpenAlex Source ID；不把来源数称为全球实际期刊数 |
| 行键与去重 | `id`；重复/空 ID 使读取失败，不静默去重或按标题合并 |
| 核心字段 | 实测 `sources` 的全部 21 列；字段名称、类型与模式由 metadata-before.json 固定 |
| 无 ISSN 行 | 保留在母体；索引匹配单独标记，不赋值为未收录 |
| ISSN 处理 | 从原 `issn` 及 `issn_l` 提取、规范化、校验校验位；保留原字段和各候选匹配证据 |
| 一对多匹配 | 保留全部候选；区分多个来源行与多个 Source ID，不任取第一条 |
| 缺失值 | JSONL 保留 null、空字符串、0、false；CSV 的空单元格不能用于分辨 null 与空字符串 |
| 读取完整性 | 总行数、每页 totalRows、ID 唯一性、分页前进、前后 schema/numRows/numBytes/lastModifiedTime 一致 |
| 版本证据 | 保存前后元数据、时间、分页清单、文件 SHA-256；数据集名称不是原始快照来源证明 |

OpenAlex 的 [Source 定义](https://help.openalex.org/data/sources/attributes/)
区分 journal、repository 等类型；`works_count` 是 OpenAlex 收到的作品数量，
不能等同于期刊实际全部发文量。`is_core` 即使在其他来源中出现，也不等于 WoS 收录。

## September 14 候选版本差异清单（历史范围）

本账号在 `insyspo` 列出 16 个可见 dataset，只看到两个 OpenAlex 快照 dataset。
这不证明其他项目或未授权区域不存在 January 2026 或会议中的第三个候选。

| 候选 | sources 行数 | 逻辑字节数 | 位置 / 列数 | 当前证据 |
|---|---:|---:|---|---|
| `publicdb_openalex_2025_03_rm` | 260,812 | 65,022,907 | US / 21 | metadata 可读；未全量下载或比较行值 |
| `publicdb_openalex_2025_08_rm` | 260,789 | 65,224,109 | US / 21 | 核心表已完整读取和筛选 |
| January 2026 暂选 | 未知 | 未知 | 未知 | 未取得精确项目、dataset、table 和构建说明 |
| 会议第三个候选 | 未知 | 未知 | 未知 | 身份未确认，不能编造版本差异 |

March/August 的字段结构一致，行数净差为 −23。这只说明计数变化，不能解释新增、
删除、合并、类型变更或字段修正，更不能认定较新月份的数据质量更高。
August 是当前可见的较晚候选，**本次用它验证可行性，没有替导师锁定研究版本**。

## September 14 关联表清单与 JOIN 约束（历史范围）

已读取以下 12 张表的元数据；除 `sources` 外，未提取其全量行。
完整 schema 与行数位于 `artifacts/schema-inventory/tables.json`。

| 表 | 元数据行数 | 用途 / 当前限制 |
|---|---:|---|
| sources | 260,789 | 已读取的核心母表 |
| publishers | 10,741 | 出版者属性；sources.publisher_id 几乎全空，连接键需核对 |
| sources_apc_prices | 37,697 | 多币种 APC，先按 source_id 聚合或保留列表 |
| sources_concepts | 2,720,252 | source–concept 多对多；不是自动等同最新 topics 分类 |
| sources_counts_by_year | 2,170,357 | 年度产出与引用，需固定年份窗口 |
| sources_host_institution_lineage | 0 | 空表需构建来源解释 |
| sources_host_institution_lineage_names | 0 | 同上 |
| sources_host_organization_lineage | 83,985 | 多层级关系，需固定组织层级 |
| sources_host_organization_lineage_names | 83,985 | 名称辅助核对，不能以同样行数推断逐行一一对应 |
| sources_publisher_lineage | 1 | 异常稀疏，暂不作完整血缘信息 |
| sources_publisher_lineage_names | 1 | 同上 |
| sources_societies | 4,484 | 学会关系，可能一对多 |

每张子表须在同一选定快照下单独固定身份与字段，先检查键、重复和覆盖率，再按
source_id 形成单行列表或经说明的聚合字段后 LEFT JOIN。每次合并应断言母表 ID 集合
与行数不变；缺少子表记录与空数组、零计数保持不同。不得把直接一对多 JOIN 后的
行数当作期刊数，也不能因现有表为空而推断期刊没有机构或出版者。

是否补充 topics、语言、出版者关系及其他指标，取决于接受的快照和研究问题；本次
21 列核心表**未完成“全部相关元数据”交付**。未确认的字段不应以同名猜测填补。

## 索引与模型仍需明确的决定

1. 当前输入已按用户选择切至 January 2026 US。仍需解释构建时间含义及缺失的主题映射，不能由月份标签推断每张表更新进度。
2. 此次合并范围及完整年份已固定如上。用于后续分析的年份窗口、主题补充及空表处理仍需随研究问题明确。
3. 固定索引定义：Scopus 主表 `Journal`、是否纳入 Trade Journal、是否区分 active/inactive；WoS 是 SCIE、SSCI、AHCI、ESCI 哪些集合。
4. 固定参照日期。已有 Scopus August 2026 参照与当前 January 2026 输入不同期；此前 August 2025 匹配是历史候选，不能直接作为本次收录标签。
5. 商业索引未知、无有效 ISSN、歧义分别编码；建立可验证的正负例定义后才启动 BorutaSHAP。

这些索引和模型决定仍待审阅；当前可复现的交付是上文固定输入的期刊合并表。
