# 上游包收录说明（绩效评价线）

> 收录日期：2026-11-01。三个包均从本机专家库 `~/.workbuddy/plugins/marketplaces/experts/plugins/` 原样复制，**内容一字未改**，只改文件名与层级。

## 一、来源

| 包 | 原目录 | 原始下载时间 | 许可 |
|---|---|---|---|
| 项目后评价专家 | `post-evaluation-expert` | 2026-10-31T23:37:46Z | 无 LICENSE，保留所有权利（仅所内使用） |
| 政府项目验收与绩效评价顾问（裴慎行） | `pangzi-gov-acceptance-advisor` | 2026-10-31T23:37:36Z | 无 LICENSE，保留所有权利（仅所内使用） |
| 注册会计师审计专家（v2.0.0） | `cpa-auditor` | 2026-10-31T23:37:29Z | 无 LICENSE，保留所有权利（仅所内使用） |

## 二、收录完整性

| 包 | 原包文件数 | 已收 | 跳过 | 跳过原因 |
|---|---|---|---|---|
| post-evaluation-expert | 5 | 2 | 3 | `avatars/expert.png`、`.codebuddy-plugin/plugin.json`、`.downloaded_at` |
| pangzi-gov-acceptance-advisor | 6 | 3 | 3 | 同上 |
| cpa-auditor | 14 | 3 | 11 | 同上 3 项；另 `references/02~09`（清产核资/专项鉴证/竣工决算/二级复核/报告起草/报价投标/汇报PPT/科研经费）属**审计线**内容，不归本线，故未收 |

**说明**：cpa-auditor 是一份跨九条业务的资深注册会计师包，本线只收它的**绩效评价能力**（README 能力地图 + `references/01-绩效评价` + agents 人设）。其余 8 份方法论属审计线，若要收，应在审计线单独立项，不混进本线。

## 三、文件名对照

| 上游文件 | 原文件 |
|---|---|
| `posteval-0-包级总览.md` | `post-evaluation-expert/README.md` |
| `posteval-1-项目后评价专家.md` | `post-evaluation-expert/agents/post-evaluation-expert.md` |
| `govacc-0-包级总览.md` | `pangzi-gov-acceptance-advisor/README.md` |
| `govacc-1-政府项目验收与绩效评价顾问.md` | `pangzi-gov-acceptance-advisor/agents/gov-acceptance-advisor.md` |
| `govacc-2-政府项目验收与绩效自评打法包.md` | `pangzi-gov-acceptance-advisor/skills/gov-acceptance-playbook/SKILL.md`（原文件名 `SKILL.md`，已改名避免混淆） |
| `cpaaud-0-包级总览.md` | `cpa-auditor/README.md` |
| `cpaaud-1-绩效评价方法论.md` | `cpa-auditor/references/01-绩效评价.md` |
| `cpaaud-2-注册会计师审计专家.md` | `cpa-auditor/agents/cpa-auditor.md` |

## 四、校验和与用法

| `文件` | `上游原名` | 行数 | `sha256前16位` | 用法 |
|---|---|---|---|---|
| `cpaaud-0-包级总览.md` | `cpa-auditor/README.md` | 62 | `9218b01577adde3e` | 能力地图、9 条工作纪律、报价口径 |
| `cpaaud-1-绩效评价方法论.md` | `cpa-auditor/references/01-绩效评价.md` | 81 | `d6cd1fc1601d0976` | **先读**：法规文号、四维权重、指标体系七步、评分表、报告提纲、抽评加分点 |
| `cpaaud-2-注册会计师审计专家.md` | `cpa-auditor/agents/cpa-auditor.md` | 113 | `d931216d876161f6` | 人设与绩效评价全流程 |
| `govacc-0-包级总览.md` | `pangzi-gov-acceptance-advisor/README.md` | 6 | `9a7692543ccc7a2b` | 包级总览 |
| `govacc-1-政府项目验收与绩效评价顾问.md` | `pangzi-gov-acceptance-advisor/agents/gov-acceptance-advisor.md` | 106 | `6501d7e7ec0b202f` | 政府项目验收、绩效自评、退回意见整改 |
| `govacc-2-政府项目验收与绩效自评打法包.md` | `pangzi-gov-acceptance-advisor/skills/gov-acceptance-playbook/SKILL.md` | 26 | `76047e56024b51e7` | 三份底稿、指标台账七列、资金四对照、自评四维 |
| `posteval-0-包级总览.md` | `post-evaluation-expert/README.md` | 5 | `cc7e0599a57deeb7` | 包级总览 |
| `posteval-1-项目后评价专家.md` | `post-evaluation-expert/agents/post-evaluation-expert.md` | 641 | `dd328f0c9b7af4b8` | 四维一体、四阶段工作法、13 项方法、成功度定级 |

## 五、用法（按需求分派）

| 要什么 | 读哪份 |
|---|---|
| **预算绩效评价的法规文号、四维指标与权重、指标体系设计七步、评分表结构、报告提纲、抽评加分点** | `cpaaud-1-绩效评价方法论.md`（81 行，最贴题，**先读它**） |
| 政府项目验收、绩效自评、指标台账、退回意见整改 | `govacc-1` + `govacc-2` |
| 项目后评价（四维一体、四阶段工作法、13 项方法、成功度定级） | `posteval-1` |
| 事务所整体能力地图、工作纪律、报价口径 | `cpaaud-0` / `cpaaud-2` |

**只读**：改一个字或往里加文件，仓库自检第 10 项会报校验和不符。要补要改，改 SKILL.md 或 `references/`。
