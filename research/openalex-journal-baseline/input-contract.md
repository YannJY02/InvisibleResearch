# OpenAlex 全期刊基线输入约定

记录日期：2026-09-14；候选定位更新：2026-09-15。所有者：`openalex-journal-baseline`。对应 INVIS-7。
状态：**可复现的探索性候选约定，供人工审阅；最终快照尚未确认**。
上游要求见[来源评论](https://github.com/invisibleinfo/invisible-research/issues/5#issuecomment-5553748839)
和[会议记录](../../meeting-reports/2026-09-14-openalex-baseline-and-access.md)。

## September 15 更新：已定位 January 2026 并验证查询路线

[最新比较](dataset-comparison.md)已定位 `multiobs` 中的 January 2026 EU/US
两库：各 76 表，表清单、schema、行数和逻辑大小一致。11 张 `sources*` 表与
`publishers` 的完整行 SHA256 指纹也一致。导师 US 工作库已有 11 张相应克隆，
当前内容已核验。`sources` 为 260,789 行，仍须按 journal 类型筛选。

执行项目采用用户页面所选的 `gen-lang-client-0676290976`，分别在 EU/US
成功查询 `multiobs` 目标数据；直接在 `multiobs` 创建作业仍失败。已有查询
路线不再依赖 `insyspo` 作业权限修复。建议后续沿用 US 工作库，最终快照接受、
字段关联和空表处理仍待审阅；下方保留 September 14 候选的历史执行证据。

January 2026 中 `sources_concepts` 等六张关联表为空，没有 `sources_topics`。
不能把 August 的关联表行数与 January 混用，也不能从 topics 分类表存在推断
期刊—主题映射已齐备。EU/US 内容一致不证明其本身没有缺失或时间混杂。

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

## 关联表范围与 JOIN 约束

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

## 索引与模型的待审阅决定

1. 确认研究快照。January 2026 的两个公共库和导师克隆现已定位并比较；仍需接受实际版本及确认构建时间含义，不能由月份标签推断每张表更新进度。
2. 明确“全部元数据”的关联表范围和时间窗口，解释稀疏关系表与 publisher_id。
3. 固定索引定义：Scopus 主表 `Journal`、是否纳入 Trade Journal、是否区分 active/inactive；WoS 是 SCIE、SSCI、AHCI、ESCI 哪些集合。
4. 固定参照日期。当前 Scopus August 2026 和 OpenAlex August 2025 不同期；只能报告跨时点匹配，不能称同年覆盖率或新收录预测。
5. 商业索引未知、无有效 ISSN、歧义分别编码；建立可验证的正负例定义后才启动 BorutaSHAP。

这些决定保留为待审阅项；当前可重现的是已读取候选及其精确匹配，不是最终研究设计。
