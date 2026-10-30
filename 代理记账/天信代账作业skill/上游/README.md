# 上游原文（只读）

**这里不是天信写的。** 是平台「记账账」财务会计专家的全部能力，原样放在这，内容一个字没改。
天信怎么用它，写在上一层 `SKILL.md`；两者不合并。

## 来源

| 项 | 内容 |
|---|---|
| 上游包 | `finance`（专家市场显示名：**记账账**·财务会计专家） |
| 版本 | 1.0.0 |
| 作者 | CodeBuddy Teams |
| 许可 | `LICENSE` 文件是 **Apache License 2.0**（可再分发，须保留 `LICENSE-finance.txt`）；但 `plugin.json` 的 `license` 字段是空字符串。以文件为准，元数据未填 |
| 抓取位置 | `~/.workbuddy/plugins/marketplaces/experts/plugins/finance/` |
| 原始下载时间 | `2026-10-30T13:39:04Z`（取自包内 `.downloaded_at`） |
| 收录日期 | 2026-10-31 |
| 收录方式 | 内容原样复制，未改写、未翻译、未合并；**仅重命名并去掉目录层级**（见下表） |

## 收录完整性：原包 13 个文件，收 10 个

查过一遍原包全清单，逐项交代，避免"以为收全了"：

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `finance-0-能力总览.md` | **曾漏收，2026-10-31 补**。包级中文总览：5 个场景走法、每技能一句话定位、数据输入方式、5 类最佳实践各 5 条 |
| `LICENSE` | ✅ `LICENSE-finance.txt` | 许可原文，再分发必须留 |
| `agents/finance-accounting-expert.md` | ✅ `finance-1-人设与能力声明.md` | 角色与边界 |
| `skills/` 下 7 个 `SKILL.md` | ✅ `finance-2` ~ `finance-8` | 能力本体 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据（name / version / skills 声明 / agentName）。不影响能力，且其 `license` 字段为空，与 LICENSE 文件矛盾，收录反而会误导许可判断 |
| `rules/finance_rules.md` | ❌ | 平台注入的场景提示（`alwaysApply: true`）。正文是「你已选择 Finance 场景，**请尽可能充分利用本插件**」+ 7 条通用原则。收进来会让 AI 以为在调市场插件，而不是读本地文件。**它不是纯广告，但也不是能力** |
| `.downloaded_at` | ❌ | 时间戳，已记入上表「原始下载时间」 |

> 本包**没有 `avatars/`**。145K 全部是文本。（税务包有 7 张头像共 10.5M，那是另一个包的情况，别混。）

## 文件对照（原名 → 这里 → 行数 → 校验和 → 用法）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `finance-0-能力总览.md` | `README.md` | 170 | `d19fadba68738277` | **先读这个**。中文，含 5 个场景的走法与最佳实践，最适合快速建立全貌 |
| `finance-1-人设与能力声明.md` | `agents/finance-accounting-expert.md` | 56 | `67bc53cbea79e7c9` | **直接可用**，中文，角色与边界 |
| `finance-2-总流程.md` | `skills/finance-workflows/SKILL.md` | 743 | `4078b20c7043483b` | 可用；其中 SOX 合规测试一节不适用 |
| `finance-3-凭证编制.md` | `skills/journal-entry-prep/SKILL.md` | 185 | `40fd4cf722cb9625` | **直接可用**，含审批矩阵、复核清单、常见错误自查 |
| `finance-4-账户核对.md` | `skills/reconciliation/SKILL.md` | 174 | `3412ddd23f36ab61` | **直接可用**，无美式特有内容 |
| `finance-5-财务报表.md` | `skills/financial-statements/SKILL.md` | 261 | `430a41aeec6d2839` | **仅方法论**。报表格式是 ASC 842 / 606，天信按中国格式出 |
| `finance-6-差异分析.md` | `skills/variance-analysis/SKILL.md` | 265 | `ebfe7448e7c0c2eb` | **直接可用** |
| `finance-7-月末结账.md` | `skills/close-management/SKILL.md` | 220 | `7901f839cba33956` | 可用；时点按中国申报期调整 |
| `finance-8-鉴证配合.md` | `skills/audit-support/SKILL.md` | 373 | `4592b5d4153a707e` | **仅方法论**。整篇 SOX 404，中国所对应的是内控规范 |
| `LICENSE-finance.txt` | `LICENSE` | 202 | `cfc7749b96f63bd3` | 许可原文，必须留 |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与此表一致。`python check.py` 第 10 项会自动核。

## 语言与适用域（用之前必须知道）

- **除 `finance-0` 和 `finance-1` 外，其余 7 个文件全是英文**。AI 读没问题，所里员工读起来费劲。
- 整套是 **US GAAP / SOX 语境**：ASC 842 租赁、ASC 606 收入、SOX 404 内控测试，中国所都没有对应概念。
- **完全没有中国内容**：增值税、纳税申报、申报期、发票、工商、印花税、企业所得税，命中数均为 0。
  所以这些事**不能指望上游**，只能靠 `SKILL.md` 里的天信做法。

## 只读纪律

改一个字，`check.py` 第 10 项就报错。往这个目录塞清单外的文件，也报错。

- 天信要补、要纠、要本土化 → 写 `SKILL.md`，不要在这层加东西
- 上游本身有硬错误（政策过期、数字错）→ **先改对再放进来**，并在上表记「已修正，原值 X，依据文号 Y」
- 上游是别国准则体系（SOX、US GAAP）→ **原样留着 + 用法列标注**。硬改成中式就不再是原文，以后也没法跟上游比对
