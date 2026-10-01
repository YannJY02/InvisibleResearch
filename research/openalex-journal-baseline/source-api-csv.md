# 完整 Source JSON 与合并 CSV

更新：2026-10-01；INVIS-8。9 月 30 日取数、CSV、本地压缩及 SURFdrive 完整字节校验已完成，
用户已通过原交付。下述追加核验独立保存，原文件和接受记录保留。

**约定任务：**按已有期刊清单取得完整 OpenAlex Source JSON，再生成一刊一行的 CSV；
暂不导入 PostgreSQL，并尽量缩短处理和传输时间。原始 JSON 保留，CSV 是本轮明确选择的输出。

## 输入与取数

母表是 January 2026 的 `multiobs.publicdb_openalex_2026_01_rm.sources`，筛选
`type = 'journal'`，共 209,799 个非空唯一 ID。使用[已核验的母表](journal-export.md)
提取 ID，不重新扫描 BigQuery；原 CSV 的 SHA-256 为
`7c555e0a926510d0efb4c97847c75a45709ff4b3eba6aa37fa84e164d76aca48`。
数字 ID 规范为 `https://openalex.org/S{id}`，保留输入顺序。

[采集脚本](analysis/collect_source_metadata.py)每次以 `ids.openalex` 查询最多 100 个 ID，
不使用删减字段的 `select`。多连接复用 HTTP 会话；每个对象独立保存到
`sources/S{id}.json`。批次结果按实际返回 ID 匹配，未返回的 ID 再用单刊接口补查。
成功、重定向、404 和请求失败分别记录，失败不被当成空值或零。

这是 **2026-09-30 读取的实时 Source 属性，套用 January 2026 的期刊清单**，
不是新的 January 2026 属性快照，也不涵盖之后新增的全部期刊。每行保留获取时间和
返回的 ID；重定向不会自动合并两个原始 ID。Source 对象仍有其[公开主题列表的覆盖边界](model-data-structure.md#52-完整响应有覆盖边界)。

实际试跑确认 `S107737141` 的单刊与批量响应对象逐值一致，均为 39 个顶层属性。
前 100 个输入中有 10 个被批量结果省略，单刊补查均为 404；这是样例核验，最终覆盖以全量结果为准。
现有 API key 的免费额度通过 `/rate-limit` 核验，单刊请求免费、列表请求每次使用
0.0001 美元的免费额度。[官方认证说明](https://help.openalex.org/api/authentication/)和
[费用示例](https://help.openalex.org/access/example-costs/)说明批量上限与计费方式。
本轮不购买额度，凭据不进入数据包或 Git。

## CSV 如何保留全部信息

`sources.csv` 每个输入 ID 固定一行。前四列为 `source_id`、`resolved_id`、
`fetch_status`、`fetched_at`；后续列取全部成功响应的字段并集。

| 内容 | 保存方式 |
|---|---|
| 数值、布尔与普通文字 | 数值、`true`／`false`、原文字 |
| 普通对象 | 展开为点号字段，如 `summary_stats.h_index`、`ids.openalex` |
| 主题、年度、ISSN 等列表 | 完整紧凑 JSON 单元格；不按位置拆列、不增加期刊行 |
| 未返回的属性 | `\M` |
| JSON `null` | `\N` |
| 真正的空字符串、空列表、空对象 | 空单元格、`[]`、`{}` |
| 与标记或 JSON 值容易混淆的字符串 | `\S` 后接 JSON 字符串，以便准确恢复原类型 |

字段名本身的点号和反斜杠会转义。类型、空值约定与逐列状态计数保存在 `manifest.json`。
CSV 的标准双引号规则保留列表内的逗号、引号及文字换行；不能按逗号或文本行数检查记录数。

转换按原始 ID 顺序逐个读取 JSON。字段并集来自下载清单，因此不用先把全部 JSON
重新扫描一遍。写出后完整读回 CSV，检查每个 ID、行宽、全部字段与原对象的一致性，
并保存字节数、SHA-256 和阶段耗时。

这些是可恢复完整对象的 CSV 数据，不代表主题、语言和 Scopus 标签已完成模型编码。
后续特征设计沿用[模型用途与合并规则](model-data-structure.md)，不能直接把任意 JSON 字符串当成数值特征。

## 复现与续跑

本轮所有本地产物在 `artifacts/source-api-2026-09-30/`，输入与取数版本写入
`input-provenance.json`。需要 `requests`；安装 `orjson` 可加快解析，未安装时使用标准库。
凭据从环境变量或本地 `.env` 读取；请求使用认证头。

```sh
python research/openalex-journal-baseline/analysis/collect_source_metadata.py \
  --ids research/openalex-journal-baseline/artifacts/source-api-2026-09-30/source-ids.txt \
  --output research/openalex-journal-baseline/artifacts/source-api-2026-09-30 \
  --workers 48 --requests-per-second 25 --max-list-requests 9000
```

同目录、同 ID 清单可续跑；已完成的批次复用，失败项补抓。改变母体或批次契约须用新目录。
只转换已下载对象可加 `--convert-only`；只下载可加 `--no-convert`。
`manifest.status = complete` 且全部读回检查通过才表示可交付；`partial` 不表示完成。

[打包脚本](analysis/package_source_metadata.py)将 CSV 压缩为 `.csv.gz`，将逐刊 JSON
目录及批次清单打包为 ZIP，保留原文件名和目录结构。压缩级别为 1，减少 CPU 时间和传输量；
压缩 CSV 解开后仍是同一份 CSV。只包含明确的数据与来源清单，不包含运行环境或私有目的地配置。
SURFdrive 沿用既有目的地，验证必须读回远端完整字节并核对哈希。

```sh
python research/openalex-journal-baseline/analysis/package_source_metadata.py \
  --run research/openalex-journal-baseline/artifacts/source-api-2026-09-30 \
  --csv sources.csv --prefix openalex-sources-2026-09-30
```

每个原始 JSON 在打包读取时与采集回执的字节数和 SHA-256 比较。ZIP 完整读回检验
成员集合、CRC 和字节数；压缩 CSV 完整解压后核对原 CSV 哈希。只有
`delivery/delivery-manifest.json` 的 `complete` 才表示打包成功。

## 本轮结果

| 核验项 | 实际结果 |
|---|---|
| 输入及 CSV 行数 | 209,799；ID 非空唯一、顺序一致 |
| 完整 Source 对象 | 184,302 个 JSON，3,396,264,330 bytes |
| 单刊确认 404 | 25,497；CSV 保留 `not_found` 行 |
| 未解决的请求错误 | 0 |
| CSV | 49 列，3,635,058,275 bytes，约 3.64 GB |
| 字段与数组检查 | 全部对象可恢复；1,726,255 个数组单元格验证通过 |
| CSV 压缩版 | 337,425,936 bytes，约 337 MB；完整解压哈希一致 |
| JSON ZIP | 485,341,234 bytes，184,302 个 Source JSON 及 2,103 个配套成员 |
| 取数实际墙上时间 | 18 分 35 秒，包含限流后的续跑 |
| CSV 写入 | 114.878 秒 |
| CSV 全量读回 | 48.173 秒 |
| 转换过程总耗时 | 166.857 秒，约 2 分 47 秒 |
| 打包与压缩内容读回 | 85.883 秒 |
| API 使用 | 消耗 0.2179 美元的当日免费额度；未购买额度 |

CSV SHA-256：`6145f66ee198ee0117026a91725ce73e7622794257cfb7c8e2a650c4e695bb92`。
压缩 CSV：`c8a444ae90af615ec9afdd8152bcd6e5b07c955f7d3e8343d93b15b0234c17f6`。
JSON ZIP：`29a6198f0c0e750511340c33171a3a51819c8a3239063319f96dac06b39b54fa`。

CSV 中 25,497 个 404 行只保留检索身份与状态，不能作为指标为零的期刊参与模型。
有效响应中另有 10,371 个 `topics = []`；空列表和未找到 Source 是不同状态。
取数时间为 04:06:56–04:25:31 UTC，逐行获取时间随表交付。

`delivery/` 已生成 `openalex-sources-2026-09-30.csv.gz`、
`openalex-sources-2026-09-30-json.zip`，以及面向接收者的 manifest 和字段说明。
四个文件均已上传既有 SURFdrive Data 文件夹，PUT 返回 201，并完整读回核对字节数和 SHA-256。
压缩 CSV 分 81 个区块、JSON ZIP 分 116 个区块读取，以固定 ETag 的条件请求锁定版本，
按字节顺序计算整份哈希；读取前后的 ETag 和文件长度一致，远端哈希与上述本地哈希相同。
manifest 与字段说明也已完整读回匹配。最后一个数据包于 05:04:28 UTC 完成核验。

远端回执在 `delivery/` 下的各文件 `*.upload.json`，数据包另有
`*.range-readback.json`，四文件汇总为 `remote-verification.json`。
接收者可解压 `.csv.gz` 得到完整 CSV；原逐刊 JSON 和获取回执在 ZIP 内。

采集与打包共 20 项行为测试通过，独立审查发现的打包来源一致性和损坏文件恢复问题均已修复，
最终复核通过。全量 CSV、压缩 CSV 和 JSON ZIP 的检查来自本次实际数据，不以测试夹具代替。

## 指定 Source 的逐列对照

2026-09-30 09:11:34 UTC，重新读取用户指定的
[Journal of Communication（S107737141）](https://api.openalex.org/sources/S107737141)，
HTTP 200；与已保存的原始 JSON 和 CSV 第 10,734 条数据记录独立对照。
本次不调用采集脚本的展开或解码函数，而按字段路径及已声明的 CSV 编码检查实际数据。

| 核验项 | 实际结果 |
|---|---|
| API 顶层字段 | 39 个，全部保留 |
| CSV 数据列 | 45 列；缺少 API 字段的列为 0，多余数据列为 0 |
| CSV 采集记录列 | `source_id`、`resolved_id`、`fetch_status`、`fetched_at`，共 4 列 |
| CSV 总列数 | 49 = 39 − 2 + 5 + 3 + 4 |
| 实时 API 与已保存 JSON | 响应字节 SHA-256 相同，逐值无变化 |
| CSV 与 JSON | 全部 45 个数据列的值与类型一致，可恢复完整对象 |

列数增加来自两个对象的展开，其余 37 个顶层字段仍对应同名列：

| API 对象 | 对应 CSV 列 |
|---|---|
| `ids` | `ids.openalex`、`ids.issn_l`、`ids.issn`、`ids.mag`、`ids.wikidata` |
| `summary_stats` | `summary_stats.2yr_mean_citedness`、`summary_stats.h_index`、`summary_stats.i10_index` |

因此 CSV 没有单独名为 `ids` 或 `summary_stats` 的列，但它们的所有子字段均在表内。
所有列表完整保留在相应单元格，不只核对长度，还逐值核对内部对象与类型：

| 列表列 | API / 原 JSON / CSV 的元素数 |
|---|---|
| `topics`、`topic_share` | 各 25 / 25 / 25 |
| `counts_by_year` | 76 / 76 / 76 |
| `apc_usd_by_year`、`listed_in` | 各 5 / 5 / 5 |
| `issn`、`ids.issn`、`host_organization_lineage` | 各 2 / 2 / 2 |
| `apc_prices` | 1 / 1 / 1 |
| `societies`、`alternate_titles` | 各 0 / 0 / 0，真实空列表保留 |

本次证据在 `artifacts/source-column-audit-2026-09-30/`：`live-source.json` 是实际
API 响应，`csv-row.json` 是实际行，`column-check.csv` 逐项列出 45 个数据列的检查，
`audit.json` 记录字段集合、数组数量、哈希及检查范围；`audit.py` 保留检查方法。
API 与原 JSON 的 SHA-256 均为
`69f2bf9b87852478f79971537f17f7579058392b10a866abd54ecdc78a966af2`。

这是对指定期刊的实时 API 对照；其余期刊仍以本轮全量 CSV 读回及对象恢复检查为证据，
没有重新请求全部期刊。API 本身的公开主题覆盖边界也不因转换完整而消失。

## 404 全量重试与版本核验

2026-10-01 用户追加授权：全量重试原来的 25,497 个 404，判断网络、ISSN／ID 对应和
BigQuery 与实时 API 版本差异。[R 报告源文件](analysis/source-retry-report.qmd)
按实际回执生成全量结果、相同 ISSN 案例和同口径类型计数。
追加产物位于独立的 `artifacts/source-retry-2026-10-01/`，不替换原 CSV 或 SURFdrive 文件。

[重试脚本](analysis/retry_source_metadata.py)对旧 ID 执行两轮分开的单刊查询，
记录每次 HTTP 响应、连接错误、重定向和时间；429、5xx 与连接失败退避重试。
随后对持续 404 的旧记录查询全部去重有效 ISSN-L 与 ISSN，不只取列表第一项。
第一轮成功的对象不再重复获取；所有未成功对象进入第二轮。
续跑核验原输入哈希、ID 顺序和成功 JSON 哈希，不能把另一个母体的缓存混用。

身份核验保留三类 CSV：每个旧 ID 一行的 `source-retry-status.csv`、每个号码一行的
`issn-lookups.csv`，以及保留一对多／多对一关系的 `old-source-candidates.csv`。
候选表记录当前 ID 是否已经出现在原成功数据中；按 ISSN 查到对象不自动认证历史合并。
独立保存的完整候选对象可用于人工确认后补充数据，不能据此直接删除原始行或覆盖原身份。

两轮全量单刊实测已分别得到 25,497 个 404，旧 ID 恢复成功为 0，未解决请求错误为 0。
两轮后独立查询已知有效的 `S107737141` 均返回 200。这个结果明显削弱短暂网络故障作为
主要解释，支持“旧 ID 在当前版本不可访问”；它不逐条证明永久删除或确认合并。

版本核验确认：旧 `sources` 表有 260,789 条全部类型记录、209,799 条 journal，
2026-10-01 03:32 UTC 的 API 分别有 257,210 和 207,602 条；journal 净差为 −2,197，
不是旧 ID 404 的数量。旧全表 `updated_date` 与 `updated` 逐行相同，最大值
2025-08-22；Source 表创建于 2026-03-18，最后修改于 2026-04-16。
这些值分别是记录更新时间和存储操作时间，不证明快照提取日期；库名 January 2026
不能独自证明属性版本。[版本核验脚本](analysis/audit_source_versions.py)
保留只读查询、dry-run、API 计数及原始导出哈希的复核入口。

原已交付 3.64 GB CSV 单次流式读回，SHA-256 仍一致；184,302 个成功对象的实际类型为
184,289 个 journal 和 13 个 repository，resolved ID 无重复。类型重分类已经出现，
但不能把与今天 API 的数量差当作准确新增数。原 404 中 8,371 个有至少一个有效 ISSN，
17,126 个没有，后者不能用 ISSN 路径确定去向。

旧清单内 ISSN 共享诊断只找到 4 个原 404 与成功旧记录共享号码；其余 8,367 个有号码的
旧 404 在旧清单中没有同号其他记录。Detail 与韩国营养期刊两个案例的当前候选 ID
本来就存在于旧期刊清单中，但其旧 ISSN-L／ISSN 都为空；当前已有关联号码，创建日期
等属性也有变化。不能把这种跨版本匹配直接称为新增替代 ID，或用旧表同号重复解释全部 404。

官方 [Source 说明](https://help.openalex.org/data/sources/)支持按 ISSN-L 归并版次，
但 [同步说明](https://help.openalex.org/access/sync/)称移除／合并旧 ID 返回 404，
[单对象说明](https://help.openalex.org/api/get-single-entities/)仍称合并返回 301。
现行说明存在冲突，应以实际响应和逐条证据为准。43 个官方历史 Source 合并文件有
9,311 条映射，末批日期 2025-08-26，只覆盖本轮 2 个旧 ID；其中一组不同日期的映射
方向反转，不能当作一直有效的当前 ID 对照。Works 删除或 Core／XPAC 口径不能替代
Source 的历史身份记录。

追加结果已全部完成并验证：

| 核验项 | 2026-10-01 实际结果 |
|---|---|
| 两轮旧 ID 重试 | 各 25,497 个，均为 404；间隔中位数约 23.11 分钟 |
| 已解决的暂时异常 | 5 次 429、11 次连接异常；未解决请求错误为 0 |
| 去重历史 ISSN 查询 | 10,473 次，10,472 成功、1 个 404 |
| 有有效 ISSN 的旧记录 | 8,371 个均得到单一当前候选，归为 8,082 个不同当前 ID |
| 与原成功数据重叠 | 8,278 个旧 ID 指向 7,990 个已有当前 ID |
| 原期刊清单外的候选 | 93 个旧 ID 指向 92 个当前 ID，其中 91 个 journal、1 个 repository |
| 没有有效历史 ISSN | 17,126 个；不能整体判定永久删除或合并 |
| ISSN 对应冲突 | 0 个多候选旧 ID；查询号码与响应 ISSN 集合不一致为 0 |
| 官方历史合并目标 | 2 个目标：1 个 200、1 个 404，日期反转记录保留 |
| 回执与成功 JSON | 61,469 条回执完整读回，成功对象哈希全部匹配 |
| 身份状态 CSV | 25,497×13；ISSN 查询 CSV 10,473×7；候选对应 CSV 10,473×14 |
| 完整补查属性 CSV | 8,083×49，173,967,365 bytes；8,082 journal、1 repository |
| 属性 CSV 全量还原 | 全部字段、类型、顺序一致；79,900 个数组单元格验证通过 |
| 属性 CSV 转换 | 写入 9.802 秒，完整读回 2.188 秒 |
| 实际 API 额度 | 全量重试及号码查询均为免费单刊；版本计数仅用 0.0003 美元当日免费额度 |

补查 CSV 包含 8,082 个 ISSN 候选及另外 1 个成功的历史映射目标，并不替换原接受 CSV。
[导出脚本](analysis/export_source_retry_candidates.py)按当前 ID 选择实际获取时间最新的响应，
保存所有观察和选择依据，再使用原转换器执行完整对象还原。派生 JSON 全部使用 APFS
写时复制并逐个核对哈希，文件互不影响；没有使用硬链接或删除原交付数据。
补查 CSV SHA-256 为
`cea9c2e501eef1d6490649d453e969492dc0397111fe68639719dc548b09c21b`。

结果最支持旧库 ID／属性与当前 API 版本和身份对应不一致，而非短暂网络故障解释整批失败。
有效 ISSN 子集中的大多数候选已经在原成功数据中；无号码子集的逐条消失机制仍未确认。
当前证据不能把 25,497 个旧 ID 一律认定为删除、合并或新建替代记录。

29 项行为测试通过；已修复续跑时跨轮响应覆盖和缺少原检查点导致范围缩小的问题。
本轮最新代码再次完成回执、JSON、CSV 内容／顺序及原输入哈希验证；原交付完整 CSV
也已独立流式核验。R 报告为实际运行和页面检查后的
`artifacts/source-retry-2026-10-01/report/source-retry-report.html`，
表格覆盖全量结果、旧／当前同 ID 属性、类型口径与时间证据。
