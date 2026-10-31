# 上游原文（只读）

**这里不是天信写的。** 是两个审计专家包的原文，原样放在这，内容一个字没改。
天信怎么用，写在上一层 `SKILL.md`；两者不合并。

| 来源 | 包 | 强在 | 收几个文件 |
|---|---|---|---|
| 热火集工具站 · 注册会计师 | `cpa` | 底稿 → 审计报告成文（槽位解析、意见判定、文号核查、监管问询自查） | 9 |
| 审小助 · AI 审计大师 | `senior-audit-expert` | 准则研判、舞弊风险、TB 批量钩稽、Excel/Python 数据自动化 | 2 |

## 来源

| 项 | cpa | senior-audit-expert |
|---|---|---|
| 显示名 | 热火集工具站（注册会计师） | AI 审计大师（审小助 Audie） |
| 版本 | 1.0.1（README 版本记录）/ plugin.json 写 1.0.0 | 1.3.3 |
| 作者 | WorkBuddy User | WorkBuddy User |
| 许可 | **无 LICENSE、无 license 字段** → 保留所有权利，**仅限所内使用** | 同左 |
| 抓取位置 | `~/.workbuddy/plugins/marketplaces/experts/plugins/cpa/` | 同目录 `senior-audit-expert/` |
| 原始下载时间 | `2026-10-31T09:16:10.887Z` | `2026-10-31T09:16:25.465Z` |
| 收录日期 | 2026-10-31 | 2026-10-31 |
| 收录方式 | 原样复制，仅重命名、去层级 | 同左 |

> **许可提示**：两包均无许可证文件，按「保留所有权利」处理，**仅限所内使用，不得随仓库对外分发**。

## 收录完整性

### cpa：原包 12 个文件，收 9 个

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `cpa-0-能力总览.md` | 包级总览：定位、功能 8 条、知识库 6 份 references 说明、版本记录 |
| `agents/cpa.md` | ✅ `cpa-1-人设与能力声明.md` | 人设：撰写视角、与审核型专家的分工、边界 |
| `skills/audit-writing-knowledge-base/SKILL.md` | ✅ `cpa-2-报告撰写知识库.md` | 知识库入口与使用方法 |
| `skills/.../references/working-paper-to-report.md` | ✅ `cpa-3-底稿到报告主流程.md` | 承接清单、模板槽位解析、数据映射、交付前勾稽 |
| `skills/.../references/report-outline.md` | ✅ `cpa-4-报告要素与结构.md` | 十项要素（CSA 1501）、意见类型（1502）、KAM（1504）、强调/其他事项（1503）、持续经营（1324） |
| `skills/.../references/standards-and-regulations.md` | ✅ `cpa-5-准则法规与查询渠道.md` | 官方查询渠道、审计依据写法 A/B、法律与准则清单、时效核查 |
| `skills/.../references/method-parameters.md` | ✅ `cpa-6-重要性与审计参数.md` | 重要性水平、风险模型、控制测试与实质性程序、函证/监盘/抽样 |
| `skills/.../references/inquiry-focus-points.md` | ✅ `cpa-7-监管问询高频点.md` | 536 份问询函蒸馏的关注维度与前置核查清单 |
| `skills/.../references/audit-report-benchmarks.md` | ✅ `cpa-8-真实报告语料基准.md` | 27 份真实报告语料蒸馏的经验基准 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像，与能力无关 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

> **语料不在包里**：cpa 的 README 提到「27 份真实报告语料 + 536 份问询函」，但**原包只带蒸馏后的 6 份 references，不带原始语料**。别以为收了原文就有那 563 份。

### senior-audit-expert：原包 5 个文件，收 2 个

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `senioraudit-0-能力总览.md` | 包级总览：能做什么 8 条、输出规范、注意事项 |
| `agents/senior-audit-expert.md` | ✅ `senioraudit-1-人设与能力声明.md` | 人设：准则体系 / 舞弊 / 行业要点 / 总额净额 / TB 钩稽 / Excel+Python |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

## 文件对照（原名 → 这里 → 行数 → 校验和 → 用法）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `cpa-0-能力总览.md` | cpa/`README.md` | 81 | `95cedf64a31d04db` | **先读这个**，中文，建全貌 |
| `cpa-1-人设与能力声明.md` | cpa/`agents/cpa.md` | 86 | `4748851ff7fc9bf6` | 中文，撰写视角与边界 |
| `cpa-2-报告撰写知识库.md` | cpa/`skills/.../SKILL.md` | 56 | `45f62ffebddd51fd` | 知识库入口 |
| `cpa-3-底稿到报告主流程.md` | cpa/`.../working-paper-to-report.md` | 119 | `1acb445b3da50704` | **直接可用**，承接→槽位→映射→勾稽 |
| `cpa-4-报告要素与结构.md` | cpa/`.../report-outline.md` | 112 | `e1fdc60413f263d1` | **直接可用**，要素/意见/KAM/持续经营 |
| `cpa-5-准则法规与查询渠道.md` | cpa/`.../standards-and-regulations.md` | 222 | `57a266b5d0659b1d` | **直接可用**，文号核查看这份 |
| `cpa-6-重要性与审计参数.md` | cpa/`.../method-parameters.md` | 108 | `ab8aee0532205a19` | 重要性、风险模型、抽样 |
| `cpa-7-监管问询高频点.md` | cpa/`.../inquiry-focus-points.md` | 130 | `6714e9788ba03f85` | 监管高频点前置自查 |
| `cpa-8-真实报告语料基准.md` | cpa/`.../audit-report-benchmarks.md` | 84 | `a1b612ffe4339e51` | 经验锚，非正式依据 |
| `senioraudit-0-能力总览.md` | senior/`README.md` | 108 | `066869469c57e862` | 先读，建全貌 |
| `senioraudit-1-人设与能力声明.md` | senior/`agents/senior-audit-expert.md` | 61 | `5a725cfe40df94cd` | **直接可用**，准则/舞弊/TB/自动化 |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与此表一致。`python check.py` 第 10 项会自动核。

## 语言与适用域（用之前必须知道）

- **cpa**：中文，中国准则体系，直接可用。
- **senior-audit-expert**：中文，但覆盖 **CAS / HKFRS / IFRS** 三套体系，并含港股/A 股监管差异。**天信做境内业务，HKFRS/IFRS 部分原样留着、只当跨境参考，不要套到境内报告**。
- 两份都**不是天信真实底稿的提炼**，与 `references/` 的通用框架一样，用前拿所里实际底稿对一遍。

## 只读纪律

改一个字，`check.py` 第 10 项就报错。往这个目录塞清单外的文件，也报错。

- 天信要补、要纠、要本土化 → 写 `SKILL.md` 或 `references/`，不要在这层加东西
- 上游本身有硬错误（政策过期、数字错）→ **先改对再放进来**，并在上表记「已修正，原值 X，依据文号 Y」
- 上游是别国准则体系（HKFRS/IFRS）→ **原样留着 + 用法列标注**
