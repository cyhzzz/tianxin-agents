# 上游原文（只读）

**这里不是天信写的。** 两个外部专家包的原文原样放在这，内容一个字没改：

- **管理咨询实战专家**（`management-consulting-practitioner`，`mc-*`）——人设 + 方法论工具箱，33 份
- **企效通**（`sme-management-expert`，`sme-*`）——人设 + 中小企业经营手册，11 份

天信怎么用，写在上一层 `SKILL.md`；两者不合并。

## 两包是什么关系（用之前先看）

| 维度 | 管理咨询实战专家 `mc-*` | 企效通 `sme-*` |
|---|---|---|
| 体量 | 33 份（实务层 11 + 经典层 17 + 前沿层 2 + 总纲 3），8508 行 | 11 份，1505 行 |
| 定位 | **体系化**：11 大模块的诊断框架、设计工具、交付模板，外加经典理论源流与标杆前沿 | **落地化**：面向"人少、钱紧、时间碎"的中小企业，给可直接成文的模板、指标库、检查清单 |
| 强项 | 战略解码、组织管控、OD 变革、薪酬体系、五阶段推进；论证有出处 | 经营诊断、供应链催料、招投标合规、电商客诉、业财看板；模板能直接用 |
| 缺什么 | 对小微企业偏重，方案需裁剪 | 缺经典理论支撑与标杆论据 |
| 什么时候用 | 中大型企业、体系建设、要论证 | 中小企业、要短周期见效、要现成模板 |

两包**不同源、文件不重名**，但**能力域有重叠**（战略、人力、营销、财务都各有一套）。
**别两边都抄一遍**：先按上表选一个当主，另一个只在缺具体模板时补。

## 来源

| 项 | `management-consulting-practitioner`（管理咨询实战专家） | `sme-management-expert`（企效通） |
|---|---|---|
| 版本 | 2.0.0 | 1.0.0 |
| 作者 | 王老师（consulting@example.com） | 企效通（sme-management-expert@workbuddy.local） |
| 许可 | **包内无 `LICENSE`，`plugin.json` 无 `license` 字段** → 按「保留所有权利」处理，**仅限所内使用，不得随仓库对外分发** | 同上（无 `LICENSE`、无 `license` 字段） |
| 抓取位置 | `~/.workbuddy/plugins/marketplaces/experts/plugins/management-consulting-practitioner/` | `~/.workbuddy/plugins/marketplaces/experts/plugins/sme-management-expert/` |
| 原始下载时间 | `2026-10-31T10:03:09.325Z`（取自包内 `.downloaded_at`） | `2026-10-31T10:03:55.901Z`（同左） |
| 收录日期 | 2026-10-31 | 2026-10-31 |
| 收录方式 | 内容原样复制，未改写、未翻译、未合并；**仅重命名并去掉目录层级** | 同左 |

## 收录完整性

**管理咨询实战专家：原包 36 个文件，收 33 个。**

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `mc-0-能力总览.md` | 包级总览：能力全景、适用场景 |
| `agents/management-consulting-practitioner.md` | ✅ `mc-1-人设与能力声明.md` | 角色人设与能力声明 |
| `skills/management-consulting-craft/SKILL.md` | ✅ `mc-2-方法论工具箱总纲.md` | 三层结构说明 + **客户问题 → 文件 快速路由表** + 模块组合提示 |
| `references/01`~`11`（11 份） | ✅ `mc-3`~`mc-13` | 实务层十一大模块：战略、组织、OD、人力、制度流程、品牌营销、激励薪酬、知识管理、课程开发、业务改善、财务投资 |
| `references/19`~`35`（17 份） | ✅ `mc-14`~`mc-30` | 经典层：总库 + 16 大领域分册（战略、组织、OD、人力、激励、文化、精益、流程、制度、营销、财务、投资、行动学习、教练、知识、传记） |
| `references/36`、`37`（2 份） | ✅ `mc-31`、`mc-32` | 前沿层：科技企业实战管理库、顶级管理刊物前沿 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

**企效通：原包 14 个文件，收 11 个。**

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `sme-0-能力总览.md` | 包级总览 |
| `agents/sme-management-expert.md` | ✅ `sme-1-人设与能力声明.md` | 角色人设与能力声明 |
| `skills/sme-management-playbook/SKILL.md` | ✅ `sme-2-方法论手册总纲.md` | 能力域索引 + 通用交付原则 + 工具速查 + 制造业指标基线 |
| `references/01`~`08`（8 份） | ✅ `sme-3`~`sme-10` | 战略诊断、供应链制造、人力行政、人才领导力、法财税合规、营销销售、业财分析、知识数字化 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

## 语言与适用域（用之前必须知道）

- **两份全是中文**，直接可读。
- 面向**中国境内民营与中小企业管理咨询**，不涉及境外法域；跨境内容仅 `sme-7` 一节，涉及时仍须核当地法规。
- `mc-14`~`mc-32` 是**经典理论与他家案例**：引用理论可署名（波特、麦肯锡 7S 等），**引用案例必须脱敏**，且不得暗示是天信项目。
- `mc-31`（科技企业库）、`mc-32`（顶刊）含**未标注出版年**的前沿结论，用进正式报告前须核原始出处与时效。
- `sme-2` 末尾的**制造业财务指标基线是"经验参照值"**，不是行业统计口径；对标前须换成本地、本行业实测基线。
- 两包都**没有天信的项目案例、报价口径、客户行业经验**——这部分上游永远给不了，见 `SKILL.md` §三。

## 文件对照

### 表一　管理咨询实战专家（`mc-0`~`mc-32`，33 份）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `mc-0-能力总览.md` | `README.md` | 172 | `9739b8fe9230f360` | 先读这个，中文，建全貌 |
| `mc-1-人设与能力声明.md` | `agents/management-consulting-practitioner.md` | 277 | `c0fd9d594a2125ec` | 角色人设与能力声明 |
| `mc-2-方法论工具箱总纲.md` | `skills/management-consulting-craft/SKILL.md` | 207 | `4e6cb833f326673d` | 总纲与快速路由表 |
| `mc-3-实务-1-战略管理.md` | `skills/management-consulting-craft/references/01-strategy.md` | 339 | `99bb59795c51f7c4` | 实务层方法论/工具/模板 |
| `mc-4-实务-2-组织管理.md` | `skills/management-consulting-craft/references/02-organization.md` | 220 | `7825a3410dc82f01` | 实务层方法论/工具/模板 |
| `mc-5-实务-3-组织发展OD.md` | `skills/management-consulting-craft/references/03-od.md` | 251 | `229981152c527c9f` | 实务层方法论/工具/模板 |
| `mc-6-实务-4-人力资源.md` | `skills/management-consulting-craft/references/04-hr.md` | 271 | `0216bc71c2669e09` | 实务层方法论/工具/模板 |
| `mc-7-实务-5-制度与流程.md` | `skills/management-consulting-craft/references/05-process-system.md` | 265 | `fc0119c92d00a401` | 实务层方法论/工具/模板 |
| `mc-8-实务-6-品牌营销.md` | `skills/management-consulting-craft/references/06-brand-marketing.md` | 220 | `5d0717927f2ef0a5` | 实务层方法论/工具/模板 |
| `mc-9-实务-7-激励与薪酬.md` | `skills/management-consulting-craft/references/07-compensation.md` | 161 | `2295181f72ac7a17` | 实务层方法论/工具/模板 |
| `mc-10-实务-8-组织知识管理.md` | `skills/management-consulting-craft/references/08-knowledge.md` | 170 | `e45452fb70990389` | 实务层方法论/工具/模板 |
| `mc-11-实务-9-课程开发.md` | `skills/management-consulting-craft/references/09-curriculum.md` | 199 | `285740d29eb7faaa` | 实务层方法论/工具/模板 |
| `mc-12-实务-10-业务改善.md` | `skills/management-consulting-craft/references/10-business.md` | 180 | `8619a11a6e150020` | 实务层方法论/工具/模板 |
| `mc-13-实务-11-财务与投资管理.md` | `skills/management-consulting-craft/references/11-finance-investment.md` | 333 | `270cf1872463f9c0` | 实务层方法论/工具/模板 |
| `mc-14-经典理论总库.md` | `skills/management-consulting-craft/references/19-classics-library.md` | 179 | `3594064dce93a799` | 经典/前沿层 |
| `mc-15-战略经典.md` | `skills/management-consulting-craft/references/20-strategy-classics.md` | 232 | `cbf01c9668242b18` | 经典/前沿层 |
| `mc-16-组织与管控经典.md` | `skills/management-consulting-craft/references/21-org-classics.md` | 252 | `efb4c12efb83546c` | 经典/前沿层 |
| `mc-17-OD经典.md` | `skills/management-consulting-craft/references/22-od-classics.md` | 237 | `105e5ba0de89df20` | 经典/前沿层 |
| `mc-18-人力经典.md` | `skills/management-consulting-craft/references/23-hr-classics.md` | 205 | `1f9a37595b7c1503` | 经典/前沿层 |
| `mc-19-激励与薪酬经典.md` | `skills/management-consulting-craft/references/24-incentive-classics.md` | 328 | `f2d1039270d103eb` | 经典/前沿层 |
| `mc-20-企业文化经典.md` | `skills/management-consulting-craft/references/25-culture-classics.md` | 247 | `6e47531e106a5cec` | 经典/前沿层 |
| `mc-21-精益管理经典.md` | `skills/management-consulting-craft/references/26-lean-classics.md` | 267 | `713b945cbd8323b1` | 经典/前沿层 |
| `mc-22-流程管理经典.md` | `skills/management-consulting-craft/references/27-process-classics.md` | 302 | `214875715b43876c` | 经典/前沿层 |
| `mc-23-制度管理经典.md` | `skills/management-consulting-craft/references/28-system-classics.md` | 307 | `bf9e882469f10942` | 经典/前沿层 |
| `mc-24-品牌营销经典.md` | `skills/management-consulting-craft/references/29-marketing-classics.md` | 256 | `c3354cd17f7a4b34` | 经典/前沿层 |
| `mc-25-财务管理经典.md` | `skills/management-consulting-craft/references/30-finance-classics.md` | 327 | `2276163e6f4008a3` | 经典/前沿层 |
| `mc-26-投资与资本经典.md` | `skills/management-consulting-craft/references/31-investment-classics.md` | 251 | `76df914926f0f2d4` | 经典/前沿层 |
| `mc-27-行动学习经典.md` | `skills/management-consulting-craft/references/32-action-learning-classics.md` | 300 | `3140131c6d1b0145` | 经典/前沿层 |
| `mc-28-教练技术经典.md` | `skills/management-consulting-craft/references/33-coaching-classics.md` | 285 | `023fa4341fb78e86` | 经典/前沿层 |
| `mc-29-知识萃取与复盘经典.md` | `skills/management-consulting-craft/references/34-knowledge-classics.md` | 332 | `11cf201db4be48c5` | 经典/前沿层 |
| `mc-30-企业传记与企业家精神经典.md` | `skills/management-consulting-craft/references/35-biography-classics.md` | 338 | `251f38f2fc1b03ad` | 经典/前沿层 |
| `mc-31-科技企业实战管理库.md` | `skills/management-consulting-craft/references/36-tech-giants-classics.md` | 353 | `9723c01db252ef9b` | 经典/前沿层 |
| `mc-32-顶级管理刊物前沿.md` | `skills/management-consulting-craft/references/37-top-journals-insights.md` | 245 | `c1f3ab5620d0e8c3` | 经典/前沿层 |

### 表二　企效通（`sme-0`~`sme-10`，11 份）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `sme-0-能力总览.md` | `README.md` | 64 | `a526d74ce19b313b` | 先读这个，中文，建全貌 |
| `sme-1-人设与能力声明.md` | `agents/sme-management-expert.md` | 148 | `707ca836a4d89acc` | 角色人设与能力声明 |
| `sme-2-方法论手册总纲.md` | `skills/sme-management-playbook/SKILL.md` | 65 | `5faaf0d1056cce1b` | 总纲与能力域索引 |
| `sme-3-经营战略与诊断.md` | `skills/sme-management-playbook/references/01-strategy-and-diagnosis.md` | 111 | `03274ef64a0f960c` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-4-供应链与生产制造.md` | `skills/sme-management-playbook/references/02-supply-chain-and-manufacturing.md` | 180 | `37a1f7e150c8e78c` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-5-人力与行政.md` | `skills/sme-management-playbook/references/03-hr-and-admin.md` | 130 | `1bd769cadfc0e0e7` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-6-人才与领导力.md` | `skills/sme-management-playbook/references/04-talent-and-leadership.md` | 151 | `a9eec1fae11c9d95` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-7-法务财税合规.md` | `skills/sme-management-playbook/references/05-legal-tax-compliance.md` | 170 | `6f4083a039c30706` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-8-营销与销售.md` | `skills/sme-management-playbook/references/06-marketing-and-sales.md` | 186 | `78e9b840a6c0ae11` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-9-业财分析与经营看板.md` | `skills/sme-management-playbook/references/07-business-finance-analytics.md` | 150 | `e9e72d5e4231fc82` | 中小企业落地：框架/模板/指标库/清单 |
| `sme-10-知识与数字化.md` | `skills/sme-management-playbook/references/08-knowledge-and-digital.md` | 150 | `2ff01195dde27e9b` | 中小企业落地：框架/模板/指标库/清单 |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与此表一致。`python check.py` 第 10 项会自动核。

## 只读纪律

改一个字，`check.py` 第 10 项就报错。往这个目录塞清单外的文件，也报错。

- 天信要补、要纠、要本土化 → 写 `SKILL.md`，不要在这层加东西
- 上游本身有硬错误（理论归属错、年份错、法条过期）→ **先改对再放进来**，并在对照表记「已修正，原值 X，依据 Y」
- 上游案例是他家项目 → **原样留着 + 用法列标注**，天信案例另写在所内，不入库
