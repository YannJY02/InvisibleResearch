# 两套期刊母体与语言、Scopus 数据

更新：2026-10-01。用户已明确要求两套路线均实际执行、各自保留，供导师选择。
这是 Exploratory Analysis 的两个比较版本；原始 BigQuery 母体与此前已接受的交付不被替换。

用户随后明确要求先检查再上传，后续远端交付已停止。本轮本地产物已完成，供用户检查。
A 的新 CSV 与 Source JSONL 在叫停前已上传并通过全部远端字节校验；B、说明、清单与报告
保持本地。此前旧版交付不受影响。

## 本轮已执行结果

| 指标 | A：BigQuery 基准 | B：当前 API 基准 |
|---|---:|---:|
| 最终期刊记录行数 | 209,799 | 207,602 |
| CSV 列数（含语言、Scopus） | 112 | 80 |
| 完整 Source 属性列 | 45 | 45 |
| 当前 Source 对象可用行 | 192,673（含 8,371 未确认候选） | 207,602 |
| 当前 Source 对象不可用行 | 17,126 | 0 |
| 去重 Works 总数 | 162,743,925 | 169,803,759 |
| 未知语言 Works | 1,516,967 | 3,756,815 |
| 没有 Works 的期刊 | 16,554 | 11,392 |
| Scopus 名录唯一匹配 | 41,509 | 40,088 |
| Scopus 有效号码、参考名录未匹配 | 101,051 | 117,209 |
| Scopus 号码／身份未知 | 67,239 | 50,305 |
| 唯一明确 Active Journal | 28,634 | 28,360 |

A 有 16,270 行共享某一当前 OpenAlex 身份，原始行分别保留。
Scopus Source ID 被多个母体行使用的身份数为 A 2,078、B 75，未自动认定为合并。
A 的当前 type 可能与 historical_type 不同；历史期刊母体不会被当前类型变更静默缩减。

BigQuery 全局去重核验 527,656,513 原始 Works 行，51,395,157 个重复 ID 均无
Source／语言／XPAC 冲突。唯一缺失 Work ID 分组不属于期刊母体。
一次实际查询处理 10,134,278,760 bytes、计费 10,134,487,040 bytes，
按 USD6.25/TiB 约 USD0.05761，未扣月度免费额度。表元数据前后稳定，
不是数据库事务快照证明。

B 完整 Sources 下载 1,043 页；全部语言分组 222 个代码、3,132 页；
当前全部 ID 的独立分母核验 2,077 批，逐刊零不一致、无需修补。
保存响应计费单位 USD0.696；账户当日免费用量 USD0.7051，剩余 USD0.2949，
prepaid 余额 0，未购买额度。实际 API 取数区间为 UTC 07:44:26–08:18:13
（上海 15:44:26–16:18:13）。不下载全 Works 快照。

完整 Source 字段 CSV 反解、原始 JSONL、语言计数与占比以及 Scopus 匹配后原列／行顺序
均经过全量读回。Scopus 匹配边界的六项测试通过。模型未运行。

本地入口为 owner 下的
`artifacts/two-route-delivery-2026-10-01/`：两套最终文件分别在
`route-a-bigquery/`、`route-b-api/`，共用字段说明和清单位于目录内，
比较 HTML 位于 `comparison/two-route-comparison.html`。
取数回执分别保存在 `two-route-bigquery-language-2026-10-01/`、
`two-route-current-api-2026-10-01/`；Scopus 原列保持与匹配摘要在
`two-route-scopus-2026-10-01/`。

**约定任务：**每套保留一条期刊记录一行、完整 OpenAlex Source 属性、该刊全部可用
Works 的语言计数与占比，以及同一 Scopus 名录的匹配证据。

## 两套路线

| 内容 | A：BigQuery 基准 | B：当前 API 基准 |
|---|---|---|
| 母体 | 原始 209,799 个 BigQuery journal ID，顺序和行数保持不变 | API 独立枚举 `type:journal`，不要求先有 ISSN 或旧 ID |
| Source 属性 | 复用 9 月 30 日完整对象；旧 ID 404 项附 ISSN 查询的当前候选 | 本轮完整分页对象，不使用删减字段的 `select` |
| 身份 | 旧 ID 是行 ID，当前 ID 与补充候选另列；候选不等于已确认的历史合并 | 当前 API Source ID 是行 ID |
| 语言来源 | `multiobs.publicdb_openalex_2026_01_rm.works` 的旧 primary Source ID | 当前 API `corpus=all` 的 `primary_location.source.id` 分组 |
| 时间与类型 | 全部可用年份、全部 Work 类型、包含所有 XPAC 状态 | 全部可用年份、全部 Work 类型、包含 XPAC |
| Scopus | 同一 August 2026 官方公开工作簿，精确有效 ISSN 匹配 | 同一工作簿、同一匹配规则 |

A 是历史 Works 与有获取日期的当前 Source 属性组成的版本，不能称为同一快照。
B 的两部分均来自本轮 API，但分页获取是一个时间区间，不能称为数据库事务快照。
语言分组另经当前全部期刊 ID 的独立分母核验（不再使用 Source type 筛选），防止
论文内旧类型造成遗漏；不一致的期刊按 ID 重新获取全部语言。API 类型分组中的
17 个已返回 404 的旧 Source、463 Works 作为母体外诊断保留，不混入当前期刊母体。
两套都表示各自 OpenAlex 数据中的期刊记录和可用论文，不表示现实中全球全部期刊或全部论文。

## 行与语言定义

`route_row_id` 唯一识别一行。A 中即使多个旧行对应同一当前候选，也不合并这些行，
并用 `resolved_identity_row_count` 显示重复身份；语言始终按该行自己的旧 ID 归属，
不把候选刊全部 Works 的语言比例复制给旧行。

`language_counts_json` 保存各语言及 `__unknown__` 的完整计数。
`language_proportions_json` 的分母是该刊全部去重 Works，包括未知语言，非空期刊的所有
占比合计为 1。`language_known_proportions_json` 另提供仅已知语言的分母。
`language_unknown_share` 单列未知比例。没有 Works 的期刊计数为 0，占比为真正的
null，分布为空对象；不存在语言字段不会被推断成 English。

两套均将大小写变体统一为小写；原始语言代码与原始分组回执保留在各自语言取数目录。
这里的语言是 OpenAlex 的论文元数据，不能直接解释为期刊官方声明的出版语言。
同一 Work 只按主要发表 Source 归属，不重复计入它的所有其他 locations。

## Source 与 Scopus 缺失规则

A 的 `source_identity_status` 区分 `same_id`、`issn_candidate_unconfirmed` 和
`not_found`。取不到 API 对象的原始期刊仍保留全部历史列；当前属性是缺失，不能当作
0、false 或期刊不存在。原始 32 列以 `historical_` 前缀完整保留，包括原文件的空值编码。

Scopus 对同 ID 行使用有效历史／当前号码的并集；未确认的 ISSN 候选只使用双方共有的
支持号码；API 不可用的行仍用历史号码；B 使用当前 API 号码。实际使用集合与规则分别
列在 `scopus_match_issn_json`、`scopus_identifier_policy`，供审计。

`scopus_membership_in_reference` 表示这版参考名录里的收录状态，
`scopus_active_journal_in_reference` 表示唯一明确 Active Journal 条目。
无有效号码、多候选或身份未知保持空值；有效号码没有匹配只表示不在这版名录中，
不表示从未被 Scopus 收录。待收录表单独记录。Scopus 自带语言列不作为 OpenAlex 语言
特征，避免把标签来源信息混入待预测特征。这些字段尚不是已选定的模型因变量。

## 重跑入口与产物

代码位于本 owner 的 `analysis/`；所有数据、回执和报告输出位于各自命名的忽略目录。

```sh
python3 research/openalex-journal-baseline/analysis/aggregate_journal_languages_bigquery.py \
  --output research/openalex-journal-baseline/artifacts/two-route-bigquery-language-new-run

uv run --with requests --with orjson python -B \
  research/openalex-journal-baseline/analysis/collect_current_journal_route.py \
  --output research/openalex-journal-baseline/artifacts/two-route-current-api-new-run

uv run --with requests --with orjson python -B \
  research/openalex-journal-baseline/analysis/build_dual_route_datasets.py \
  --route A --input research/openalex-journal-baseline/artifacts/two-route-bigquery-language-new-run \
  --output research/openalex-journal-baseline/artifacts/two-route-delivery-new-run/route-a-bigquery

uv run --with openpyxl python -B \
  research/openalex-journal-baseline/analysis/match_dual_route_scopus.py \
  --input research/openalex-journal-baseline/artifacts/two-route-delivery-new-run/route-a-bigquery/journals.pre-scopus.csv.gz \
  --route route-a --id-field route_row_id --issn-fields scopus_match_issn_json \
  --output research/openalex-journal-baseline/artifacts/two-route-scopus-new-run
```

B 使用同一 builder 的 `--route B` 和 API 目录，然后执行相同 matcher。
A 固定复用已验证的原始 Source 与 ISSN 补查目录；重跑新母体需重新明确这些输入。
取数作业逐步保存回执；已有完整结果不被静默覆盖。BigQuery 每次提交前执行 dry run，
本轮上限 64 GiB；API 使用现有免费额度并保存分组／分页以支持恢复，不自动购买额度。

最终比较报告的可执行源文件为 [two-route-comparison.qmd](analysis/two-route-comparison.qmd)。
该 QMD 的 R 代码已实际执行，HTML 已生成并在浏览器检查：母体、语言与 Scopus 数值
与完成回执一致，同一期刊的全部 45 个属性、获取时间及列表子字段可阅读和展开。
最终文件的字节数与 SHA-256 记录在本地交付清单；完整读回核验及成本见上文。
后续数据、说明、清单和报告上传等待用户检查后的明确指示。
