# 上游原文（只读）

**这里不是天信写的。** 是平台「记账账」财务会计专家的全部能力，原样放在这，一个字没改。
天信怎么用写在上层 `references/01~13`，两者不合并。

## 来源

| 项 | 内容 |
|---|---|
| 上游包 | `finance`（专家市场显示名：**记账账**·财务会计专家） |
| 版本 | 1.0.0 |
| 作者 | CodeBuddy Teams |
| 许可 | Apache License 2.0（可再分发，须保留 `LICENSE-finance.txt`） |
| 抓取自 | `~/.workbuddy/plugins/marketplaces/experts/plugins/finance/` |
| 抓取日期 | 2026-10-31 |
| 抓取方式 | 文件原样复制，内容未做任何改写、翻译、合并；**仅重命名并去掉目录层级**（见下表） |

## 为什么原样收

最初的做法是"读懂再写一篇中文"，7 个能力模块 2221 行压成 498 行，压掉 78%。
丢的是审批矩阵、复核清单、常见错误自查——不出现在日常口语里，但决定一笔分录做对还是做错。

所以原文进来当字典查。**要改天信的做法，改 `references/`，别改这里。**

## 文件对照（原名 → 这里 → 在天信怎么用）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `finance-1-人设与能力声明.md` | `agents/finance-accounting-expert.md` | 56 | `67bc53cbea79e7c9` | **直接可用**，中文，角色与边界 |
| `finance-2-总流程.md` | `skills/finance-workflows/SKILL.md` | 743 | `4078b20c7043483b` | 可用；其中 SOX 合规测试一节不适用 |
| `finance-3-凭证编制.md` | `skills/journal-entry-prep/SKILL.md` | 185 | `40fd4cf722cb9625` | **直接可用**，含审批矩阵与常见错误自查 |
| `finance-4-账户核对.md` | `skills/reconciliation/SKILL.md` | 174 | `3412ddd23f36ab61` | **直接可用**，无美式特有内容 |
| `finance-5-财务报表.md` | `skills/financial-statements/SKILL.md` | 261 | `430a41aeec6d2839` | **仅方法论**，报表格式是 ASC 842/606，天信按中国格式出 |
| `finance-6-差异分析.md` | `skills/variance-analysis/SKILL.md` | 265 | `ebfe7448e7c0c2eb` | **直接可用** |
| `finance-7-月末结账.md` | `skills/close-management/SKILL.md` | 220 | `7901f839cba33956` | 可用；时点按中国申报期调整 |
| `finance-8-鉴证配合.md` | `skills/audit-support/SKILL.md` | 373 | `4592b5d4153a707e` | **仅方法论**，整篇 SOX 404，中国所对应内控规范 |
| `LICENSE-finance.txt` | `LICENSE` | 202 | `cfc7749b96f63bd3` | 许可原文，必须留 |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与上表一致。`python check.py` 第 10 项会自动核。

**未收录**（不影响能力完整性）：

- `rules/finance_rules.md` —— 平台注入的场景提示（"你可以使用 finance 插件"的广告）。不是能力，拷进来会让 AI 误以为在调市场插件。
- `avatars/*.png` —— 专家形象图，占了整个包 11M 的体积，与能力无关。

## 只读纪律

改一个字，`check.py` 第 10 项就报错。往这个目录塞新文件，也报错。

- 天信要补、要纠、要本土化 → 写 `references/01~13`
- 上游本身有硬错误（政策过期、数字错）→ **先改对再放进来**，并在上表记"已修正，原值 X，依据文号 Y"
- 上游是别国准则体系（SOX、US GAAP）→ **原样留着 + 上表标注**，硬改成中式就不再是原文，以后也没法跟上游比对
