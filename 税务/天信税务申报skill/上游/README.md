# 上游原文（只读）

**这里不是天信写的。** 是上游专家包的能力原文，**5 个文件**原样收录、内容一字未改——来源是 `tax-advisor-expert`（银橙税务师）。

> **只收有源可核对的。** 本目录每份文件都必须能在本机原包里找到同一份原文、`sha256` 一致。
> 找不到源包、无法核对的，一律不入库——收了也证明不了它是原文。这条规矩在 2026-10-31 执行过一次（见文末「已移除的上游包」）。

**税率表不在这里。** 银橙本身不含税率表（只在范例里出现个别比率），税率唯一源是天信原创的 `references/01-税率与优惠速查.md`。

## 来源

| 项 | 内容 |
|---|---|
| 上游包 | `tax-advisor-expert`（专家市场显示名：**银橙AI**·银橙税务师，CPA + CTA） |
| 版本 | 1.0.0 |
| 作者 | chung（yincheng@yinchengai.cn） |
| 许可 | **包内无 LICENSE，`plugin.json` 无 license 字段** → 保留所有权利，**仅限所内使用** |
| 抓取位置 | `~/.workbuddy/plugins/marketplaces/experts/plugins/tax-advisor-expert/` |
| 原始下载时间 | `2026-10-31T09:14:35.597Z`（取自包内 `.downloaded_at`） |
| 收录日期 | 2026-10-31 |
| 收录方式 | 原样复制，仅重命名、去层级 |

> ⚠ **合规提示**：上游没有 LICENSE，法律上属"保留所有权利"。本目录**仅供天信所内使用**，
> 不得对外分发、不得随技能公开发布。代账线的 `finance` 包是 Apache-2.0，可以随仓库外发——
> 两个上游的法律状态不一样，别混。

## 收录完整性：原包 8 个文件，收 5 个

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `taxadv-0-能力总览.md` | 包级总览：六类咨询、四类响应模式、所需资料、输出规范 |
| `agents/tax-advisor-expert.md` | ✅ `taxadv-1-人设与能力声明.md` | 能力主体：财税一体定位 + 六类咨询方向 + 四模式判定 + 四类报告结构 + 红线 |
| `skills/tax-report/SKILL.md` | ✅ `taxadv-2-报告生成技能.md` | Word 报告成文：三类报告章节结构 + 内容 JSON 定义 + python-docx 脚本用法 |
| `skills/tax-report/references/tax-checklists.md` | ✅ `taxadv-3-分税种核查清单.md` | 分税种核查清单 + 汇算调整项目表结构 + 常见风险点 |
| `skills/tax-report/scripts/build_tax_report.py` | ✅ `taxadv-4-报告生成脚本.py` | python-docx 生成器（封面/多级标题/表格边框/页脚页码），字段类型错误跳过并汇总 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像，与能力无关 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

## 文件对照

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `taxadv-0-能力总览.md` | `README.md` | 93 | `733a104e85bd4c25` | 先读，建全貌 |
| `taxadv-1-人设与能力声明.md` | `agents/tax-advisor-expert.md` | 130 | `491643b536423de5` | **直接可用**，财税一体 + 四模式 + 红线 |
| `taxadv-2-报告生成技能.md` | `skills/tax-report/SKILL.md` | 156 | `43996625431c6543` | 三类报告章节结构 + JSON 定义；脚本用法见 `taxadv-4` |
| `taxadv-3-分税种核查清单.md` | `skills/tax-report/references/tax-checklists.md` | 129 | `acf7bde8449aa5cd` | 分税种核查 + 汇算调整项 + 风险点 |
| `taxadv-4-报告生成脚本.py` | `skills/tax-report/scripts/build_tax_report.py` | 379 | `949aeddec24c39aa` | `python taxadv-4-报告生成脚本.py <content.json> <out.docx>`，需 `pip install python-docx` |

校验：`sha256sum <文件> | cut -c1-16`。

## 银橙能干什么、不能干什么

| 能用 | 说明 |
|---|---|
| 财税一体分析 | 一笔业务同时给会计处理与税务处理，并顺查税务风险点 |
| 四类响应模式 | 按其人设的判定规则选作答深度，不用每次重讲背景 |
| 分税种核查清单 | 申报前逐税种过一遍，含汇算调整项目表结构与常见风险点 |
| Word 税务报告成文 | 合规审查 / 专业报告 / 汇算清缴三类章节结构 + python-docx 脚本 |

| 不能指望 | 缺口在哪 |
|---|---|
| 税率、征收率、扣除限额 | 银橙不含税率表 → `references/01`（每条带文号与期限） |
| 表间勾稽逐项校验、申报前自查 | 无 → `references/03` |
| 风险指标的算法与阈值 | 无 → `references/04` |
| 异常发票的处置路径 | 仅有一般提示 → `references/05` |

## 已移除的上游包：`tax-compliance-team`（2026-10-31 删除）

**情况**：这条线原先还收过另一个包 `tax-compliance-team`（企业税务合规团队：1 个组长 + 5 个专员 + 税引擎）的 9 份原文（`tax-0` ~ `tax-8`，含科目表、各税种计算要点、六阶段分工）。

**为什么删**：**源包已不在本机**（`~/.workbuddy/plugins/marketplaces/experts/plugins/tax-compliance-team/` 不存在，全盘也搜不到），无法与原始字节比对。按"只收有源可核对的"这条规矩，9 份全部移出仓库——**留着一份证明不了出处的原文，比没有更糟**。

**影响**：

- 能力路由里原先指向 `tax-2`（税种计算要点）、`tax-6`（合规报告结构）、`tax-8`（会计科目表）、`tax-1`（六阶段分工）的条目已一并删除，`SKILL.md` 与业务线 `README.md` 已同步。
- **会计科目表目前在本线没有上游依据**。建账、开明细科目时按会计准则与客户行业惯例处理；若要回填依据，重新下载 `tax-compliance-team` 后按 `AGENTS.md` §3.1 重收，并在本文件补回校验表。
- **知识没有丢**：原包税率表当时被判定不如天信 `references/01` 而未收录，比对中发现的 7 处口径问题（加计抵减已到期、留抵退税 60% 公式作废、证券交易印花税 0.05%、财产保险印花税千分之一、小规模征收率、《增值税法》2026 施行、优惠期限与文号）**已全部并入 `references/01`，每条带文号与执行期限**。以 `references/01` 为准，不需要原来的包。

**如需恢复**：重新下载该包 → 逐份 `sha256` 与源文件核对 → 按 §3.1 平铺命名 → 在本文件补回收录完整性与文件对照表 → 更新 `SKILL.md` 路由。

## 只读纪律

改一个字，`check.py` 第 10 项就报错（校验和对不上）。往这个目录塞新文件，也报错。

要补、要纠 → 写 `references/` 下的天信原创篇，或改 `SKILL.md`。
上游本身发现新错误 → 先改对上游、再回填上表（`taxadv` 目前未发现硬错误），或直接写进 `references/` 并在此标注。
