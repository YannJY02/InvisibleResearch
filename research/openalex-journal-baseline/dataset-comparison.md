# January 2026 OpenAlex 数据集比较

核验日期：**2026-09-15**；对应 INVIS-6 / INVIS-7。
状态：探索性比较已完成，供人工审阅；不是最终研究快照的接受记录。

## 结论

**当前期刊分析所需的 12 张表，在 EU 与 US 版中未发现内容差异。**
两库的 76 张表全部同名、同结构、同行数、同逻辑字节数；其中 11 张
`sources*` 表及 `publishers` 进一步通过了全部行的 SHA256 内容指纹比较。
这包含重复记录，不是抽样。其余 64 张大表只核对了元数据，不能据此声称
整个 OpenAlex 数据集逐行相同。

| 数据集（项目均为 `multiobs`） | 实际位置 | 表数 | 核验结果 |
|---|---|---:|---|
| `publicdb_openalex_2026_01_eu_rm` | EU | 76 | 与 US 版元数据一致；12 张相关表内容指纹一致 |
| `publicdb_openalex_2026_01_rm` | US | 76 | 本次参考对象；全库逻辑大小 1,398,635,836,099 bytes |
| `userdb_saurabh_khanna` | US | 11 | 11 表均有指向 US 版同名表的 `cloneDefinition`；现时内容指纹也一致 |

这支持“期刊相关数据在不同区域保存了相同内容”的判断。名称中的 `eu`
对应存储位置，不能解释成欧洲期刊子集。两个公共库的构建/跨区复制历史
未取得，月份标签也不是每张表内容实际更新至该月份的证明。

**后续执行建议：沿用导师现有的 US 工作库。** 已有 11 张相关克隆表，无需
再克隆一次。若选入 `publishers`，该表尚未出现在此次读回的工作库中；
其纳入、连接规则及完整合表仍由 INVIS-7/8 承接。本次没有执行复制或合表。

## 为什么网页能查询，但此前命令报权限错误

数据所在项目和执行查询的项目可以不同。本次以同一个已登录账号实测：

| 路由 | 结果 |
|---|---|
| 作业项目 `multiobs`，US，`SELECT 1` | 失败：缺少该项目的 `bigquery.jobs.create` |
| 作业项目 `gen-lang-client-0676290976`（用户截图顶部的 YannJY），US，`SELECT 1` | 成功 |
| 同一 YannJY 作业项目，分别在 EU / US 读取 `multiobs` 的相关表 | 三个实际数据查询全部成功，见下方作业记录 |

因此，旧 `insyspo` 或本次 `multiobs` 的项目级作业失败，不等于这些表不能
通过现有 YannJY 执行项目查询。它是可用的替代执行路线，不是对原项目 IAM
修复的证明。查询计量归所选执行项目；本次没有改变默认项目、IAM、账单配置
或 MCP allowlist。现有 MCP 配置仍限定旧 `insyspo` 数据集，不能用它推断
新路线的能力。参见[访问记录](../../docs/testing/bigquery-access.md)。

## 完整内容核验范围

下表中的行数是各张原表的行数，不是全部期刊数。`sources` 仍包含其他 source
类型，研究中的 `type == 'journal'` 筛选和一刊一行约定继续适用。

| 表 | EU / US 每表行数 | EU / US 全行指纹 | 工作库与 US 原表 |
|---|---:|---|---|
| `sources` | 260,789 | 相同 | 相同 |
| `sources_apc_prices` | 48,560 | 相同 | 相同 |
| `sources_counts_by_year` | 7,076,220 | 相同 | 相同 |
| `sources_host_organization_lineage` | 510,500 | 相同 | 相同 |
| `sources_societies` | 8,914 | 相同 | 相同 |
| `publishers` | 10,703 | 相同 | 此次工作库中无此表 |
| `sources_concepts` | 0 | 相同（空表） | 相同（空表） |
| `sources_host_institution_lineage` | 0 | 相同（空表） | 相同（空表） |
| `sources_host_institution_lineage_names` | 0 | 相同（空表） | 相同（空表） |
| `sources_host_organization_lineage_names` | 0 | 相同（空表） | 相同（空表） |
| `sources_publisher_lineage` | 0 | 相同（空表） | 相同（空表） |
| `sources_publisher_lineage_names` | 0 | 相同（空表） | 相同（空表） |

每个公共库实际核验 7,915,686 行；工作库核验 7,904,983 行。公共库有 `topics`
及相关分类表，但没有 `sources_topics` 表。上述空表或缺少期刊—主题关联表是
两版共有的限制，切换 EU/US 不会补齐它们。它们不证明期刊本身不存在对应信息。

## 更节省扫描的方法

1. **先读元数据。** REST `datasets.get` / `tables.list` / `tables.get`
   取得位置、完整表清单、schema、行数、逻辑大小、streaming buffer 与克隆来源。
   两库 76/76 表一致；没有 streaming buffer。`etag` 是资源版本信息，未作为
   内容校验和。[官方 Table API](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/tables)
2. **各区域各自算内容指纹。** 只扫描研究相关表的全部列/行，按字段名构造
   稳定顺序的 `STRUCT`，以 `TO_JSON_STRING` 序列化后计算 SHA256。将行摘要
   分 256 桶，桶内排序且保留重复次数，再对桶摘要和行数生成表摘要。只下载
   少量摘要，在本地比较。[SHA256](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/hash_functions)
3. **有差异再深入。** 先定位不同的表/桶，再核对字段、ID 和重复次数。
   本次所有已核验表一致，未继续扫描论文、作者和引用等巨表。

固定字段名及类型使本次 NULL、空字符串、数值、布尔值、日期时间和字符串形式
的列表保留区别；没有将空值统一替换。脚本只接受本次检查过的平面标量类型，
遇到嵌套/原生 JSON 等结构拒绝执行，需要另行定义比较语义。
SHA256 一致是强内容证据，仍存在理论哈希碰撞，不是无碰撞的数学证明；
序列化表示比较也不等同于任意 SQL 类型的通用语义比较。

各区域查询是先后执行的。所选表的 schema、行数、字节数、更新时间和 streaming
buffer 前后均稳定，但这不是跨区域原子快照。复制时间/来源也不能单独证明
克隆后没有变化，所以工作库另做了内容核验。

当前 BigQuery 有需要额外设置与权限的 Global queries 预览功能；本次无需启用，
也未跨区迁移整表。[官方 Global queries](https://docs.cloud.google.com/bigquery/docs/global-queries)

## 导师提供的 CLONE 示例

来源是用户在本次对话转述的 Mattermost SQL；本轮没有直接读取该消息。

```sql
CREATE TABLE `multiobs.userdb_saurabh_khanna.sources_societies`
CLONE `multiobs.publicdb_openalex_2026_01_rm.sources_societies`;
```

这是单表克隆。API 已确认该目标表存在，基础表确为 US 版同名表，克隆时间为
`2026-09-15T08:19:21.703Z`，当前行数 8,914，内容指纹与原表一致。
其余 10 张工作表的克隆来源也已读回。克隆要求源与目标在同一区域；US 版与
现有工作库满足这一位置条件，EU 版不能直接克隆到该 US 数据集。克隆后两表
独立，后续变化不会自动同步。[官方克隆说明](https://docs.cloud.google.com/bigquery/docs/table-clones-intro)

## 执行与验证证据

执行时间：2026-09-15 18:18–18:20 中国时间。作业项目均为
`gen-lang-client-0676290976`；缓存关闭；先 dry run，每作业设置 512 MiB
`maximumBytesBilled`。三次合计处理 **1,088,125,789 bytes**，计费扫描
**1,089,470,464 bytes（1,039 MiB）**；这不是货币账单或免费额度使用结论。

| 对象 / 位置 | 作业 ID | 计费 bytes |
|---|---|---:|
| EU 公共库 / EU | `codex_dataset_comparison_19ff8615a9774c93abde3281a0db4347` | 363,855,872 |
| US 公共库 / US | `codex_dataset_comparison_a45bb502dd9f45d891bf5d5129e2465d` | 363,855,872 |
| 导师工作库 / US | `codex_dataset_comparison_c7d45b24eccc41c5b2a49b7af765c70c` | 361,758,720 |

工作库作业轮询曾遇到 SSL 连接中断；按保存的原作业 ID 恢复读取，未重复提交。
实际 SQL 行为检查还验证了：行顺序改变不影响指纹；总行数和唯一行集合相同、
但重复次数不同的两个表会产生不同指纹。独立复核通过。

原始元数据、SQL、dry run、完整 job/result、前后检查及摘要均保留在本地忽略目录
`artifacts/dataset-comparison-2026-01/`。脚本为
[compare_bigquery_datasets.py](analysis/compare_bigquery_datasets.py)。复现时使用新目录：

```sh
python3 research/openalex-journal-baseline/analysis/compare_bigquery_datasets.py inventory \
  --project multiobs \
  --datasets publicdb_openalex_2026_01_eu_rm publicdb_openalex_2026_01_rm userdb_saurabh_khanna \
  --output research/openalex-journal-baseline/artifacts/dataset-comparison-rerun

python3 research/openalex-journal-baseline/analysis/compare_bigquery_datasets.py fingerprint \
  --project multiobs --execution-project gen-lang-client-0676290976 \
  --datasets publicdb_openalex_2026_01_eu_rm publicdb_openalex_2026_01_rm userdb_saurabh_khanna \
  --output research/openalex-journal-baseline/artifacts/dataset-comparison-rerun
```

命令使用已有 Google CLI 登录；若 `gcloud` 不在 PATH，可传 `--gcloud` 指定路径。
`resume` 仅按已保存的同一 job ID 读取结果，不能重新提交；输入改变会拒绝恢复。
这是有扫描上限的研究相关表核验器，不是全库比较或复制工具。
