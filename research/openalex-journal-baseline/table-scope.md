# 期刊合表范围：76 张表怎样关联、哪些信息需要补充

日期：2026-09-25。对应 INVIS-7；这是范围与连接审计，建议尚未变成新的全量导出。

## 1. 本次任务与结论

**约定任务：梳理整个数据集的表与期刊之间的关系，再确定直接保留、汇总和暂缓的内容。**

“每行代表一本期刊”与“只能读取 sources 表”是不同要求。论文、作者和机构数据可以先
按期刊汇总，再合入一刊一行的文件。反过来，把所有能连接的记录直接摊开，并不能得到
一份含义明确的期刊表。

本轮实时读取 `multiobs.publicdb_openalex_2026_01_rm` 的表清单和全部 schema，
确认 **76 张表、14 张空表**。表名、schema、元数据行数、逻辑字节数和修改时间均与
9 月 15 日保存的记录一致；这不是全表逐值比对，也不证明构建时的快照完全同步。

当前 [SQL](analysis/export_journal_table.sql) 读取 **12 张表：11 张 sources 家族表，加 publishers 主表**。
其余 64 张已经逐项列入[完整范围清单](analysis/table_scope_rules.csv)，不是全部应该直接拼接的 64 类期刊属性。
清单包含每张表的用途、连接路径、实际字段、处理建议和未验证之处。
清单优先级分为：已在 CSV 中 existing（12 表）、优先补充或核对 next（11）、
可选研究扩展 optional（20）、辅助字典/参考 reference（21）、路径或数据缺口 blocked（12）。
这些是处理建议，不是五类数据质量等级；空表也可能已作为空列表包含在 existing 中。

### 老师明确说了什么

[9 月 15 日会议记录](../../meeting-reports/2026-09-15-openalex-table-delivery.md)对应原始转录：

- 00:16 先查看 sources；02:45–03:02 讨论主题、APC、机构等相关信息和单个可查看 CSV。
- 06:24–06:32 说复制“all tables”，但没有逐项列出这句话覆盖的表。
- 10:00–10:18 确认目前研究期刊；10:41 说未来可能“instead of sources ... download articles”。

因此，以 sources 为中心有上下文支持，但“老师只允许 sources 前缀”没有依据。
通过论文补主题是本轮为解决缺口提出的方法；作者指标也是建议，不能写成老师已经指定。
本轮授权是把这些边界梳理清楚，不将某个年份窗口或作者指标冒充已接受的研究设计。

## 2. 所有表分成哪些用途

**约定任务：每张表都有交代，不按名称前缀提前排除。**

| 表家族 | 表数 | 描述什么 | 建议怎样进入期刊数据 |
|---|---:|---|---|
| sources | 11 | 期刊等出版载体及直接关联信息 | 保留期刊基础列；关联列表单独整理后接回 |
| publishers | 7 | 出版者 | 补充精确匹配出版者的属性、国家、层级；全局业绩不能改称期刊业绩 |
| institutions | 5 | 机构 | 区分期刊主办机构与在该刊发表的作者机构；后者须经过论文署名关系 |
| authors | 5 | 作者身份和整体履历 | 可由该刊论文得到作者名单/数量；作者全局发文量不等于该刊发文量 |
| works | 20 | 论文及其署名、主题、位置、引用等 | 定义期刊论文范围，独立汇总主题/作者/机构等；不把所有明细直接摊成期刊行 |
| topics | 4 | 主题名称及说明等 | 通过论文主题补充期刊主题分布 |
| subfields | 5 | 子学科字典及关系 | 解释已匹配主题的上级分类 |
| fields | 5 | 学科字典及关系 | 同上；不能把整个字典都分配给每本期刊 |
| domains | 5 | 大学科领域字典及关系 | 同上；`siblings` 是分类之间的关系，不是期刊归属 |
| concepts | 4 | 另一套概念分类及关系 | 有概念关系才能连接；不可直接等同 topics |
| funders | 5 | 资助者 | `works_grants` 空，当前缺期刊论文到资助者的有效桥梁，保留缺口 |
| **合计** | **76** | | |

`source` 指成果发表或存放的载体，例如期刊、会议系列、仓库；`type='journal'`
才是其中的期刊子集。`work` 是一项学术成果，`author` 是作者。
这些定义见 [OpenAlex Sources](https://help.openalex.org/data/sources/) 和
[Works](https://help.openalex.org/data/works/attributes/)。官方当前 API 定义用于解释概念，
本地关系库的实际字段和可用性仍以本次 schema 为准。

## 3. 表怎样连接：先找到关系，再决定一行怎么表示

**约定任务：说明可执行的连接路径，以及哪些字段不能直接相加。**

### A. 直接属于期刊的信息

```text
sources.id
  ├── sources_*.source_id → 年度、APC、学会等
  └── host_organization 的 P 编号 → publishers.id → 出版者补充表
```

十张 source 子表各自先按 source_id 整理成一个列表，再 LEFT JOIN 回母表。
不要同时直接展开年份、币种、学会，避免一条记录被其他关系重复组合。
机构 I 编号与出版者 P 编号必须分开解析；学会名称和 URL 不能擅自当作机构主键。

### B. 经论文找到主题和 domain

```text
sources.id = works.primary_source_id
works.primary_topic_id = topics.id
topics.subfield = subfields.id
 topics.field   = fields.id
 topics.domain  = domains.id
```

再按 source_id 汇总，就能形成“这本期刊的论文主要分布在哪些主题/学科”。
这说明 domain 可以进入期刊表；不要求最终每行变成论文。

建议先采用主主题路线：每篇符合范围的论文最多贡献一个主要主题，同时保留没有主题的论文数。
`works_topics` 则允许多主题；若用每篇论文的所有主题，百分比之和可能超过 100%，两种口径不可混称。
全量前还要核对主表 `primary_topic_id` 与 `works_primary_topic` 的一致性、唯一性和覆盖。

`concepts` 与 topics 分开处理。`sources_concepts` 为空并不代表该刊没有主题；
改走论文主题路径可能补充信息，但这得到的是论文汇总结果，不是原生期刊主题字段的恢复。

### C. 经论文找到作者与发表机构

```text
sources.id = works.primary_source_id
works.id = works_authorships.work_id
works_authorships.author_id = authors.id

works.id = works_authorships_affiliations.work_id
works_authorships_affiliations.institution_id = institutions.id
```

可用的期刊指标包括指定时期的不同作者数、不同发表机构数或机构国家分布。
要先明确按论文、作者还是署名计数；一位作者的多个机构不能不加说明地重复计数。
作者目前的机构（last_known_institution）不等于论文发表时机构。

建议用一张经验证的署名表作主路径，其余署名表达用于补字段或核对；
`works_authorships*` 四张表不能全都并列连接，否则同一署名可能重复。
作者、机构、出版者的全局 `works_count` / `cited_by_count` 可以作为实体属性，
不能改名或相加后当作“这本期刊的发文量/引用量”。

### D. 需要先验证的键和断点

- `authors_ids`、`works_ids` 没有 author_id/work_id；要验证 openalex 编号的格式后转换，不能拿 MAG 编号代替。
- `works_primary_location`、`works_biblio` 等使用通用列名 `id`；不能仅凭名字就断言与 works.id 一一对应。
- `works.primary_source_id` 与 `works_primary_location.source_id` 是待核对的两套表示；
  `works_locations` 包含多个存放位置，不能替代唯一发表来源。
- 分类的 `siblings`、`ancestors` 是分类之间的关系；顺着它们展开，不代表期刊同时属于全部兄弟分类。
- `works_grants` 有字段但零行。资助者字典再完整，也不能由此知道哪本期刊的论文受其资助。
- `publishers_counts_by_year` 的真实列名是 `works_coun`；`publishers_roles` 缺少 related_role_id。
  完整清单记录这些差异，不按理想表结构生成连接。

所有 76 张表均未声明主外键约束。字段存在是结构依据，仍要用数据检查唯一性、空值和匹配率。

## 4. 本轮怎样验证

**约定任务：给建议留下可复查证据，不把画出的关系当作已经完成的全量合并。**

[审计脚本](analysis/audit_table_scope.py)实时获取元数据；
[范围规则](analysis/table_scope_rules.csv)是人工审阅的解释，脚本检查它恰好覆盖所有表、没有重复表、引用字段真实存在。
然后从 works 的四个位置各预览最多 100 行，只把这些行的 ID 放进小查询，连接 sources 和主题字典。
示例不是随机抽样，不能据此估算全库覆盖率。完整结果和作业记录留在本地。

复现新观察（须使用新输出目录；外部查询先 dry run、每个作业上限 512 MiB）：

```sh
python3 research/openalex-journal-baseline/analysis/audit_table_scope.py \
  --output research/openalex-journal-baseline/artifacts/table-scope-new-run \
  --collect --probe \
  --previous research/openalex-journal-baseline/artifacts/dataset-comparison-2026-01/publicdb_openalex_2026_01_rm-metadata.json
```

使用本次已保存证据重新生成完整清单和可读 HTML（不发起新云端查询）：

```sh
python3 research/openalex-journal-baseline/analysis/audit_table_scope.py \
  --output research/openalex-journal-baseline/artifacts/table-scope-2026-09-25 \
  --previous research/openalex-journal-baseline/artifacts/dataset-comparison-2026-01/publicdb_openalex_2026_01_rm-metadata.json \
  --render
```

可读产物为该目录中的 `table-scope.html`，含本文和全部 76 表的逐项说明。
新观察应先更新并审阅本文，再重新渲染，不能把旧报告数字当新执行结果。

元数据调用为 tables.list/get，预览使用 [tabledata.list](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/tabledata/list)。
全量作者/论文表没有被扫描合并，原始 CSV 没有改写。本轮实例只核验期刊—主题—学科路线，
作者、机构、通用 id 和全体外键覆盖仍是后续检查项。

### 实际结果：连接路线可以走通

本轮从四个位置读到 **400 条 works 记录**，其中 **100 条**匹配到
`type=journal` 的 source，**98 条**继续匹配到了主题。其余两条保留主题缺失。
起初仅查看第一个位置的 100 条记录，没有匹配到期刊；增加位置后才得到下面实例，
说明默认预览顺序不能当作全库随机样本。两个查询合计计费扫描 **100 MiB**，不是全库扫描。

| 实际字段 | 读到的值 | 含义 |
|---|---|---|
| work_id | 282818013 | 这篇论文 |
| source_id / journal | 147586446 / Archives of Cardiovascular Diseases Supplements | 该论文的主要发表来源，类型为期刊 |
| primary_topic_id / topic | 10217 / Cardiac electrophysiology and arrhythmias | 该论文的主要主题 |
| subfield | 2705 / Cardiology and Cardiovascular Medicine | 所属子学科 |
| field | 27 / Medicine | 所属学科 |
| domain | 4 / Health Sciences | 所属大领域 |

这个例子证明“期刊 → 论文 → 主题 → domain”有实际匹配，**不证明整本期刊只属于这个主题**。
对整刊分类须汇总其规定范围内的论文，保留分布和缺失；不能用一篇论文替代整刊。
实例作业：`codex_journal_scope_offsets_1d66b1c8b435412f81b2a9325c21b368`；检查时状态 DONE。


本地证据统一在 `artifacts/table-scope-2026-09-25/`：`metadata.json`、`collection.json`、
`summary.json`、`table-inventory.csv`、预览 JSON、`scope_offsets/` 下的 SQL、dry run 与作业，
以及 `scope-offsets-result.json`。元数据总逻辑大小约 1.40 TB，不是本轮扫描量。

## 5. 建议怎样补充，什么暂时不塞进 CSV

**约定任务：给出有顺序的补充建议，并明确它与已交付文件的差别。**

1. **保留当前原始交付。** 它是 12 张输入表的可追溯合并结果；来源重复仍须保留记录，
   新的统计表另定去重规则。把“原始明细保留”和“指标如何计算”分开。
2. **优先补主题/学科分布。** 这是会议明确提到且现有文件缺少的信息。
   建议依据论文的 primary source 与 primary topic，并呈现主题缺失数；先验证全量键与覆盖，再计算指标。
3. **补直接实体说明。** 精确 P 编号连接出版者国家、层级等可用信息；
   若存在可靠 I 编号再补主办机构，不能拿作者所属机构充当主办机构。
4. **作者与发表机构作为可选扩展。** 可以合入，但先选出研究要用的指标和时期。
   表名不构成纳入理由，作者履历、原始署名文本、摘要、全部引用边和所有 sibling 分类不直接塞进主 CSV。
5. **关系明细与字典仍有位置。** 需要复查时保留关联明细和分类字典；主 CSV 仍一刊一行。
   本次没有删除未纳入的表，也没有将未纳入等同于“没有价值”。

### 进入下一轮全量补表前，需要明确的计算口径

| 决定 | 本轮建议 | 原因 |
|---|---|---|
| 哪些论文归属于某刊 | 优先 primary_source_id；核验备用表示 | 所有 location 会混入存放版本/仓库 |
| 统计哪些年份和作品类型 | 按后续研究问题确定；同时保存 publication_year/type | 不能擅自只选近五年或只选 article 来改变基线 |
| 主要主题还是全部主题 | 首先主主题；其他作为另列分析 | 分母和份额解释更清楚 |
| 缺失怎样表达 | 保留未知数和匹配覆盖；不填成零 | 缺关系不等于没有作者/主题/资助 |
| 作者/机构指标 | 先明确是否需要以及计数单位 | 可连接不等于会议已指定；防同作者/同机构重复 |

**本轮完成的是完整范围清单、连接方案与有限实例验证。现有 CSV 尚未扩展到作者、
论文推导主题或 domain，不能声称“76 张表已经全部合进文件”。**
