# 上游原文 · finance 1.0.0

> **本目录是第三方原文，只读。** 一个字都不要改。
> 天信要补充、纠正、本土化，一律写到 `references/01~13` 去，不动这里。

## 一、来源

| 项 | 内容 |
|---|---|
| 上游包名 | `finance`（专家市场显示名：**记账账**·财务会计专家） |
| 版本 | 1.0.0 |
| 作者 | CodeBuddy Teams |
| 许可 | Apache License 2.0（可再分发，须保留 `LICENSE` 与版权声明） |
| 抓取自 | `~/.workbuddy/plugins/marketplaces/experts/plugins/finance/`（WorkBuddy 专家市场已下载副本） |
| 抓取日期 | 2026-10-31 |
| 抓取方式 | 文件级原样复制（`shutil.copy2`，保留时间戳），未做任何改写、翻译、合并 |

## 二、为什么原样收原文，而不是"融合蒸馏"

天信代账线最初把这 7 个能力压缩改写成了 13 篇中文 reference（合计 498 行）。
回头核对上游原文：**2221 行**。压缩过程丢掉了 78% 的内容——具体丢的是审批矩阵、
复核清单、常见错误自查、流程分支条件这类"不出现在日常口语里、但真正决定做对做错"的部分。

例：上游 `journal-entry-prep` 有「Review and Approval Workflows」（审批矩阵 + 复核清单）
和「Common Errors to Check For」（常见错误自查）两整节，天信版 31 行里一个字都没有。

**所以：原文进来当字典查，天信适配层管"在这个所里怎么用"。两层不合并。**

## 三、收录清单（10 个文件）

| 文件 | 行数 | sha256 前 16 位 |
|---|---|---|
| `LICENSE` | 202 | `cfc7749b96f63bd3` |
| `README.md` | 170 | `d19fadba68738277` |
| `agents/finance-accounting-expert.md` | 56 | `67bc53cbea79e7c9` |
| `skills/audit-support/SKILL.md` | 373 | `4592b5d4153a707e` |
| `skills/close-management/SKILL.md` | 220 | `7901f839cba33956` |
| `skills/finance-workflows/SKILL.md` | 743 | `4078b20c7043483b` |
| `skills/financial-statements/SKILL.md` | 261 | `430a41aeec6d2839` |
| `skills/journal-entry-prep/SKILL.md` | 185 | `40fd4cf722cb9625` |
| `skills/reconciliation/SKILL.md` | 174 | `3412ddd23f36ab61` |
| `skills/variance-analysis/SKILL.md` | 265 | `ebfe7448e7c0c2eb` |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与上表一致。

**未收录的两项**（不影响能力完整性）：

- `rules/finance_rules.md` —— 平台注入的场景提示（`alwaysApply: true`，内容是"你可以使用 finance 插件"的广告 + 能力索引）。不是能力，拷进来反而会让 AI 误以为自己在调用市场插件。
- `avatars/*.png` —— 专家形象图，11M 里绝大多数体积在这。专属于专家包，与技能能力无关。

## 四、逐文件适用性（**读之前先看这张表**）

上游是**美式准则体系**（US GAAP / SOX 404）语境写的。天信是县城所代账，适用中国企业会计准则
（CAS）与《小企业会计准则》。所以原文不是"能不能用"，是"当什么用"。

| 上游文件 | 在天信怎么用 | 注意 |
|---|---|---|
| `agents/finance-accounting-expert.md` | **直接可用** | 中文，专家能力声明与边界，适合当天信代账岗的角色底稿 |
| `skills/journal-entry-prep` | 直接可用（方法论） | 分录类型、单据要求、审批矩阵、常见错误四节都适用；科目名与审批层级按天信口径替换 |
| `skills/reconciliation` | 直接可用（方法论） | 银行/往来/存货/科目间四类对账思路通用，无美式特有内容 |
| `skills/variance-analysis` | 直接可用（方法论） | 差异分解与 waterfall 思路通用 |
| `skills/close-management` | 直接可用（方法论） | 结账 checklist 编排通用；时点按中国纳税申报期调整 |
| `skills/finance-workflows` | **部分可用** | 5 大流程骨架可用；其中 SOX 合规测试一节中国所不适用 |
| `skills/financial-statements` | **仅方法论参考** | 报表格式是美式（ASC 842 租赁 / ASC 606 收入 / ASC 350 无形）。**天信出报表一律按中国格式**，见 `references/06-财务报表.md` |
| `skills/audit-support` | **仅方法论参考** | 整篇是 SOX 404 内控测试。中国所对应的是《企业内部控制基本规范》及配套指引，概念不对应，别直接套用语 |

> 一句话纪律：**格式、准则、科目、报表口径以 `references/01~13` 为准；原文只回答"这一步还有哪些情形我没考虑到"。**

## 五、以后要加别的上游包

同一套做法，新增 `references/上游/<包名>-<版本>/`，每包一份本文件（`SOURCE.md`），
至少写清：来源、版本、许可、抓取方式、收录清单与校验和、逐文件适用性。

**绝不做的三件事**：改原文、把原文翻译成中文覆盖、把原文和适配层合并成一篇。
