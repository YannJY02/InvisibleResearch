# 10 月 13 日导师对话：会面与 Scopus 特征工程

**约定任务：**将最新导师对话中的明确行动、反馈及会面安排接入已有项目任务；本次只做来源整理。

## 来源与读取范围

2026-10-16 读取用户提供的 Mattermost Appshot，并在桌面应用中核对 Saurabh 私聊的
10 月 13 日消息。展开并读完邀约线程的 4 条回复、Route B 讨论的 1 条回复、
特征工程讨论的 1 条回复。消息日期和时刻沿用界面显示，显示时区未独立核实。
本次不是完整聊天导出，也未读取日历邀请、执行模型或核验所分享软件的可用性。
只保留项目相关转述和永久链接，不复制私人原文或附件。

## 会面安排

**约定任务：**简短讨论如何把数据列转成可供机器学习使用的数值特征。

[老师 10 月 13 日 20:34 的邀约](https://mattermost.invisible.info/invisible-information-lab/pl/mhrjp6538jnpmf4e1ygi4x1ouw)
先提出讨论下一步。[研究者 21:20](https://mattermost.invisible.info/invisible-information-lab/pl/h7iazyxiupbsiy9brtqw4ai8ky)
提议下周一或周二；[老师 21:26](https://mattermost.invisible.info/invisible-information-lab/pl/nga6yh3isbfafke9fkk4xp4kqy)
说若仍准备 ICA，最好本周简短碰面，否则下周也可以。
[研究者 21:29](https://mattermost.invisible.info/invisible-information-lab/pl/etosgf9fwtf4j8sh71pzkn53ic)
确认仍想准备 ICA，且本周只有周五有空；
[老师 21:35](https://mattermost.invisible.info/invisible-information-lab/pl/xxwgrfujif8q8mushepx5qnqow)
表示会发周五邀请，讨论把列转成数值特征。

按消息日期推算，双方约定的是 **2026-10-16（周五）**。具体时间、时区及日历邀请
是否已发出仍未核实。“几分钟”是老师的口头预期，不写成固定会议时长。
此前 9 月 29 日记录的“下周”以及本线程最初的下周一／二提议不再作为最新安排。
本次没有核实 ICA 截止日期，也没有新增分析完成日期。

## 数据反馈与下一步

**约定任务：**清理期刊数据列，形成数值特征，研究哪些特征可预测 Scopus 收录。

| 来源 | 明确内容 | 对已有工作的含义 |
|---|---|---|
| [Saurabh 20:34](https://mattermost.invisible.info/invisible-information-lab/pl/mhrjp6538jnpmf4e1ygi4x1ouw) | 肯定这次数据工作并提出讨论下一步 | 是导师反馈；未逐项验收全部字段或宣布相关任务全部完成 |
| [Saurabh 21:13](https://mattermost.invisible.info/invisible-information-lab/pl/z67wpb94rbydmfa3p6s7ok6h4c) | 两套数据的关键指标相近 | 对比反馈；本次没有重算指标 |
| [Saurabh 21:15](https://mattermost.invisible.info/invisible-information-lab/pl/tq5riqta3bycmj5qyz6npshybo)；[Jinyi 21:23 回复](https://mattermost.invisible.info/invisible-information-lab/pl/igdmx5r44fgj7yjh4gd86g43jw) | 老师认为 Route B 歧义较少，可能因匹配更新；研究者赞同并提到直接使用 API | 原因是讨论中的判断，尚未正式选定 Route B 为唯一分析母体 |
| Saurabh 21:16–21:18；[21:18 消息及线程](https://mattermost.invisible.info/invisible-information-lab/pl/9mqymr3jxfbh8pji9zk1ucnd9c) | 预测“匹配到 Scopus 来源”的 1／0 状态；先清理列为数值特征，再用于 Boruta／SHAP 一类方法；举出 0／1 和 z 分数 | 明确了特征工程行动和预测目标方向；未确定每列编码、未知标签规则或最终学习器 |
| [Jinyi 21:34 回复](https://mattermost.invisible.info/invisible-information-lab/pl/ikbsehyug3g65ms1h84wiudiae) | 表达对语言、国家等特征与收录预测关系的初步理解 | 是理解反馈，不能当作特征表或分析已完成 |
| [Saurabh 21:25](https://mattermost.invisible.info/invisible-information-lab/pl/mjx1sntefinamk4wcge8zr47pe) | 分享 Ekeany/Boruta-Shap 作为一种可参考方法 | 保存[原链接](https://github.com/Ekeany/Boruta-Shap)；不代表已安装、运行或接受为唯一方案 |

## 既有任务映射与会面待定事项

沿用[两套数据交付记录](../../research/openalex-journal-baseline/dual-route-delivery.md)，不重复取数或建任务。

| 既有事项 | 本次补充 | 后续核对点 |
|---|---|---|
| INVIS-7：快照与行定义 | A／B 指标相近及 B 歧义较少的讨论 | 明确用于分析的母体；老师未作正式版本选择 |
| INVIS-8：期刊数据与 SURFdrive 交付 | 新增导师肯定及讨论下一步的反馈 | 保留此前交付证据和原人审范围，不把泛化认可替代全部验收 |
| INVIS-9：收录标记 | 明确本阶段关注 Scopus 匹配 1／0 | 决定参考名录成员还是 Active Journal 为目标；无有效 ISSN、歧义、身份未知仍须单独处理 |
| INVIS-10：Boruta／SHAP | 补充数值特征清理和讨论任务；附老师分享的方法链接 | 明确字段编码、缺失值、标签与特征边界，然后执行分析 |

**会面需要澄清：**使用哪套数据、0／1 的精确定义及未知样本的处理、
语言／国家／主题等列如何转成数值。现有交付保留未知和歧义状态，不能仅因二元预测
方向就把全部空值填成 0。Scopus 来源字段用于标签与审计，不作为待预测特征；
这一防止泄漏的边界来自既有数据说明，不冒充本次老师已确认的决定。
本次不选编码方案、不拟合模型，不把特征预测解释为因果作用。

## 同步状态

2026-10-16 本地来源记录与任务映射已整理。Plane MCP 返回 OAuth authorization required，
无法读取当前任务或写入并读回；已将带消息 ID 的同步项保留在本地管理队列。
任务状态、日期、分配和依赖没有远端变更；旧 Plane 快照仅作定位，不代表当前状态。
恢复授权后先读当前事项及评论，按来源键去重补充反馈／行动和本次提交证据，再核对
管理交付的人审状态，不提前把 INVIS-10 标记为执行中或完成。
