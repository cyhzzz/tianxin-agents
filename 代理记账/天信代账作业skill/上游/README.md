# 上游原文（只读）

**这里不是天信写的。** 是三个外部专家包的原文，原样放在这，内容一个字没改。
天信怎么用它们，写在上一层 `SKILL.md`；两者不合并。

| 来源 | 包 | 定位 | 收几个文件 |
|---|---|---|---|
| 记账账 · 财务会计专家 | `finance` | 日常账务作业底本（凭证 / 核对 / 报表 / 差异 / 结账） | 9 + 许可 |
| 东纳荣 · 代理记账与工商顾问 | `bookkeeping-agency-advisor` | 代账主战场 + 工商注册变更注销 + 异常处理 + 资质 | 1 |
| 飞猫 · 代账顾问 | `flycatsoft-dai-zhang-gu-wen` | 代账客户月度资料催收 | 2 |

## 来源

| 项 | 记账账 finance | 东纳荣 | 飞猫 |
|---|---|---|---|
| 版本 | 1.0.0 | 1.0.0 | 1.0.0 |
| 作者 | CodeBuddy Teams | 东纳荣企服（Simon319@sina.cn） | 飞猫软件（support@flycatsoft.cn） |
| 许可 | **Apache License 2.0**（保留 `LICENSE-finance.txt`）；`plugin.json` license 为空，以文件为准 | **无 LICENSE、无 license 字段** → 保留所有权利 | **无 LICENSE、无 license 字段** → 保留所有权利 |
| 抓取位置 | `~/.workbuddy/plugins/marketplaces/experts/plugins/finance/` | 同目录 `bookkeeping-agency-advisor/` | 同目录 `flycatsoft-dai-zhang-gu-wen/` |
| 原始下载时间 | `2026-10-30T13:39:04Z` | `2026-10-31T09:20:39.262Z` | `2026-10-31T09:15:54.362Z` |
| 收录日期 | 2026-10-31 | 2026-10-31 | 2026-10-31 |
| 收录方式 | 原样复制，仅重命名、去层级 | 同左 | 同左 |

> **许可提示**：东纳荣、飞猫两包无许可证文件，按「保留所有权利」处理，**仅限所内使用，不得随仓库对外分发**。finance 是 Apache-2.0，可再分发但须保留 `LICENSE-finance.txt`。

## 收录完整性

### 记账账 finance：原包 13 个文件，收 10 个

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `finance-0-能力总览.md` | 包级中文总览：5 个场景、每技能定位、数据输入方式、5 类最佳实践 |
| `LICENSE` | ✅ `LICENSE-finance.txt` | 许可原文，再分发必须留 |
| `agents/finance-accounting-expert.md` | ✅ `finance-1-人设与能力声明.md` | 角色与边界 |
| `skills/` 下 7 个 `SKILL.md` | ✅ `finance-2` ~ `finance-8` | 能力本体 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据，不影响能力；license 字段为空与 LICENSE 矛盾 |
| `rules/finance_rules.md` | ❌ | 平台注入的场景提示（"请充分利用本插件" + 通用原则），收进来会让 AI 以为在调市场插件 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

### 东纳荣 bookkeeping-agency-advisor：原包 4 个文件，收 1 个

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `agents/bookkeeping-agency-advisor.md` | ✅ `dnr-0-人设与能力声明.md` | **本包无独立 README**，agents 即"总览 + 能力"：6 大能力（代账报税 / 工商 / 初创合规 / 资质 / 异常处理 / 升级识别）+ 五步 SOP + 安全边界 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像，与能力无关 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

### 飞猫 flycatsoft-dai-zhang-gu-wen：原包 6 个文件，收 2 个

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `flycat-0-能力总览.md` | 包级总览：覆盖领域、场景列表、核心价值 |
| `agents/flycatsoft-dai-zhang-gu-wen.md` | ✅ `flycat-1-人设与能力声明.md` | 能力：代账客户月度资料催收（催收清单 + 三档催收消息 + 逾期提示）+ 合规边界 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png`、`avatars/.gitkeep` | ❌ | 头像与占位文件 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

## 文件对照（原名 → 这里 → 行数 → 校验和 → 用法）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `finance-0-能力总览.md` | finance/`README.md` | 170 | `d19fadba68738277` | **先读这个**。中文，5 个场景走法与最佳实践 |
| `finance-1-人设与能力声明.md` | finance/`agents/finance-accounting-expert.md` | 56 | `67bc53cbea79e7c9` | **直接可用**，中文，角色与边界 |
| `finance-2-总流程.md` | finance/`skills/finance-workflows/SKILL.md` | 743 | `4078b20c7043483b` | 可用；SOX 合规测试一节不适用 |
| `finance-3-凭证编制.md` | finance/`skills/journal-entry-prep/SKILL.md` | 185 | `40fd4cf722cb9625` | **直接可用**，含审批矩阵、复核清单、常见错误自查 |
| `finance-4-账户核对.md` | finance/`skills/reconciliation/SKILL.md` | 174 | `3412ddd23f36ab61` | **直接可用**，无美式特有内容 |
| `finance-5-财务报表.md` | finance/`skills/financial-statements/SKILL.md` | 261 | `430a41aeec6d2839` | **仅方法论**。报表格式是 ASC 842 / 606，天信按中国格式出 |
| `finance-6-差异分析.md` | finance/`skills/variance-analysis/SKILL.md` | 265 | `ebfe7448e7c0c2eb` | **直接可用** |
| `finance-7-月末结账.md` | finance/`skills/close-management/SKILL.md` | 220 | `7901f839cba33956` | 可用；时点按中国申报期调整 |
| `finance-8-鉴证配合.md` | finance/`skills/audit-support/SKILL.md` | 373 | `4592b5d4153a707e` | **仅方法论**。整篇 SOX 404 |
| `LICENSE-finance.txt` | finance/`LICENSE` | 202 | `cfc7749b96f63bd3` | 许可原文，必须留 |
| `dnr-0-人设与能力声明.md` | 东纳荣/`agents/bookkeeping-agency-advisor.md` | 123 | `beb0cc2c2c069ccb` | **直接可用**，中文。代账报税 / 工商 / 初创合规 / 资质 / 异常处理 / 升级识别 |
| `flycat-0-能力总览.md` | 飞猫/`README.md` | 51 | `11d69548e001750a` | 中文，包级总览 |
| `flycat-1-人设与能力声明.md` | 飞猫/`agents/flycatsoft-dai-zhang-gu-wen.md` | 56 | `89353f4111af419b` | 直接可用。资料催收清单 + 三档催收消息 + 逾期提示 |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与此表一致。`python check.py` 第 10 项会自动核。

## 语言与适用域（用之前必须知道）

- **finance**：US GAAP / SOX 语境，除 `finance-0`、`finance-1` 外全英文；增值税、申报、发票、工商命中数为 0。
- **东纳荣**：中文，中国实务，直接可用；偏"高频刚需事务"（注册/变更/注销/异常/资质），与天信县城所业务对口。
- **飞猫**：中文，只覆盖"资料催收"一事，**能力窄**，当催收话术模板用即可，别指望它做账。

## 只读纪律

改一个字，`check.py` 第 10 项就报错。往这个目录塞清单外的文件，也报错。

- 天信要补、要纠、要本土化 → 写 `SKILL.md`，不要在这层加东西
- 上游本身有硬错误（政策过期、数字错）→ **先改对再放进来**，并在上表记「已修正，原值 X，依据文号 Y」
- 上游是别国准则体系（SOX、US GAAP）→ **原样留着 + 用法列标注**
