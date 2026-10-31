# 上游原文（只读）

**这里不是天信写的。** 两个外部专家包的原文原样放在这，内容一个字没改：

- **业小勤**（`asset-appraiser`）——角色人设与能力声明，2 份
- **热火集工具站**（`asset-valuation-expert`）——人设 + 一整套准则、法规、方法、模板，94 份

天信怎么用，写在上一层 `SKILL.md`；两者不合并。

## 两包是什么关系（用之前先看）

| 维度 | 业小勤 `appraiser-*` | 热火集 `appraise-*` |
|---|---|---|
| 体量 | 2 份 / 327 行 | 94 份（其中准则原文 59 份） |
| 强项 | 角色口吻、11 项能力全貌、价值类型与参数要点、审核负面清单 | **报告审核**（监管问询维度前置 + 五类依据时效核查 + 28 类科目逐项核查）+ 准则法规全文 + 报告模板 |
| 缺什么 | 没有知识库，没有准则原文 | — |
| 什么时候用 | 定角色、讲方法论全貌、口头答疑 | 查准则原文、核依据时效、审报告、套模板 |

两包**不同源、文件不重名不重复**（一个是 1.0.0 的单人设包，一个是 1.0.2 的带库包）。
**要角色口吻用 `appraiser-1`，要依据、清单、模板用 `appraise-*`。**

## 来源

| 项 | `asset-appraiser`（业小勤） | `asset-valuation-expert`（热火集工具站） |
|---|---|---|
| 版本 | 1.0.0 | 1.0.2 |
| 作者 | WorkBuddy User | 热火集工具站（88031225@qq.com） |
| 许可 | **包内无 `LICENSE`，`plugin.json` 无 `license` 字段** → 按「保留所有权利」处理，**仅限所内使用，不得随仓库对外分发** | 同上（无 `LICENSE`、无 `license` 字段） |
| 抓取位置 | `~/.workbuddy/plugins/marketplaces/experts/plugins/asset-appraiser/` | `~/.workbuddy/plugins/marketplaces/experts/plugins/asset-valuation-expert/` |
| 原始下载时间 | `2026-10-31T09:17:04.484Z`（取自包内 `.downloaded_at`） | `2026-10-31T10:05:16.080Z`（同左） |
| 收录日期 | 2026-10-31 | 2026-10-31 |
| 收录方式 | 内容原样复制，未改写、未翻译、未合并；**仅重命名并去掉目录层级** | 同左 |

## 收录完整性

**业小勤：原包 7 个文件，收 2 个。**

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `appraiser-0-能力总览.md` | 包级总览：四科体系、11 项功能、执业判断锚点 |
| `agents/asset-appraiser.md` | ✅ `appraiser-1-人设与能力声明.md` | **能力主体**：11 项能力 + 四科知识体系 + 价值类型体系 + 准则名录 + 参数要点 + 测算表骨架 + 报告审核负面清单 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png` | ❌ | 头像 |
| `avatars/.gitkeep` | ❌ | 占位文件 |
| `.created-by-session` | ❌ | 平台生成标记 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

**热火集：原包 98 个文件，收 94 个。**

| 原包文件 | 收了没 | 说明 |
|---|---|---|
| `README.md` | ✅ `appraise-0-能力总览.md` | 包级总览：定位（审核视角）、10 项功能、知识库构成、时效陷阱 |
| `agents/asset-valuation-expert.md` | ✅ `appraise-1-人设与能力声明.md` | 角色人设与能力声明 |
| `skills/appraisal-knowledge-base/SKILL.md` | ✅ `appraise-2-知识库总纲.md` | 知识库总纲与检索路由 |
| `skills/appraisal-knowledge-base/references/`（顶层 16 份） | ✅ `appraise-3`~`appraise-18` | 准则法规检索表、报告骨架、审核清单、方法参数、资产基础法、监管问询、案例先例 |
| `references/准则原文/`（59 份） | ✅ `appraise-19`~`appraise-77` | 中评协准则全文：基本准则、职业道德、程序性 6、实体性 7、评估指南 4、指导意见 15、专家指引 1–17 号、风险提示问答、操作指引、准则术语 |
| `references/法规制度/`（8 份） | ✅ `appraise-78`~`appraise-85` | 涉国资法律法规、国资管理问题回复、地方性文件、司法文件、证券相关文件、深圳国资委 |
| `references/地方协会文件/`（2 份） | ✅ `appraise-86`~`appraise-87` | 地方评协实务答疑汇总 |
| `references/实务口径/`（2 份） | ✅ `appraise-88`~`appraise-89` | 1.16 补充资料正文与登记索引 |
| `templates/valuation-report-template.md` | ✅ `appraise-90-评估报告模板.md` | 报告主模板（声明七条 + 十五节 + 出具前自检） |
| `templates/opinion-style-examples/`（3 份 docx） | ✅ `appraise-91`~`appraise-93` | 真实审核意见格式参考：单一主体股权 / 多主体公司 / 单项资产 |
| `.codebuddy-plugin/plugin.json` | ❌ | 包元数据 |
| `avatars/expert.png`、`avatars/.gitkeep` | ❌ | 头像与占位 |
| `.downloaded_at` | ❌ | 时间戳，已记入上表 |

> ⚠️ **上游 README 提到但包里没有的**：`templates/clean-examples/`（干净版报告书 docx、评估说明 docx、成本法申报表 xlsx、市场法计算表 xlsx、收益法明细表 xlsx，共 5 件）。原包**实际未附带**，所以收不到——不是我们漏收。要这几份得回头找上游作者。

## 语言与适用域（用之前必须知道）

- **两份全是中文**，直接可读。
- 覆盖的是**资产评估**（三大方法、企业价值、单项资产、无形资产、矿业权、司法处置、国资备案、财务报告目的），**不含工程造价咨询**。造价业务本线仍空，见 `SKILL.md` §三。
- **时效陷阱（上游自己写明的）**：中评协〔2026〕5/6/7 号（程序 / 质控 / 职业道德）2026 年 7 月印发，但**自 2027-01-01 起施行**；**2026 年内的报告仍应引旧文号**〔2018〕36 号 /〔2017〕46 号 /〔2017〕30 号。判断"现行有效"看**施行日**，不看发布年。原文见 `appraise-6-时效日历-发布日与施行日.md`、`appraise-7-新规速查-2025-2026.md`。
- 地方口径是**广州、深圳**国资与地方评协，天信在浙江台州，**须替换为浙江省及当地口径**。原文原样留着，在此标注。
- `appraise-19` 起的准则原文是**全文照录**，引用时取原文原话，不要转述；`appraise-78`~`appraise-89` 是法规与口径汇编，**合计约 5 MB**（单份 `appraise-86` 就 1.9 MB / 15465 行），**按需检索，不要整篇读**。

## 文件对照

### 表一　角色与总纲

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `appraiser-0-能力总览.md` | `README.md` | 70 | `8c3f66ae48fc1853` | 先读这个，中文，建全貌 |
| `appraiser-1-人设与能力声明.md` | `agents/asset-appraiser.md` | 257 | `2ea49eb597c71080` | 能力主体：准则名录 / 价值类型 / 参数 / 测算表骨架 / 审核清单 |
| `appraise-0-能力总览.md` | `README.md` | 96 | `b13beebfd59bfdd6` | 先读这个，中文，建全貌 |
| `appraise-1-人设与能力声明.md` | `agents/asset-valuation-expert.md` | 96 | `5863b3ee7f663564` | 角色人设与能力声明 |
| `appraise-2-知识库总纲.md` | `skills/appraisal-knowledge-base/SKILL.md` | 88 | `7d3981a6e67c8460` | 知识库总纲与路由 |

### 表二　方法论与清单（`appraise-3`~`appraise-18`）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `appraise-3-准则法规与检索.md` | `skills/appraisal-knowledge-base/references/standards-and-regulations.md` | 361 | `123771165fd1fb71` | 方法论/清单 |
| `appraise-4-准则索引.md` | `skills/appraisal-knowledge-base/references/standards-index.md` | 375 | `2833b66883ba66cb` | 方法论/清单 |
| `appraise-5-准则速查矩阵.md` | `skills/appraisal-knowledge-base/references/standards-quick-matrix.md` | 248 | `7da5712cd3dbd0e8` | 方法论/清单 |
| `appraise-6-时效日历-发布日与施行日.md` | `skills/appraisal-knowledge-base/references/时效日历_发布日与施行日.md` | 86 | `e74408fc90441831` | 方法论/清单 |
| `appraise-7-新规速查-2025-2026.md` | `skills/appraisal-knowledge-base/references/新规速查_2025-2026.md` | 103 | `188abeea1cb9d4b6` | 方法论/清单 |
| `appraise-8-准则发布通知一览.md` | `skills/appraisal-knowledge-base/references/准则发布通知一览.md` | 75 | `e34a4caf2d4c63db` | 方法论/清单 |
| `appraise-9-IVS国际准则对照.md` | `skills/appraisal-knowledge-base/references/IVS对照.md` | 178 | `dc877d65f34e1b3a` | 方法论/清单 |
| `appraise-10-报告要素与结构.md` | `skills/appraisal-knowledge-base/references/report-outline.md` | 126 | `d0aceece90422c7e` | 方法论/清单 |
| `appraise-11-报告审核清单.md` | `skills/appraisal-knowledge-base/references/review-checklist.md` | 188 | `fe68f07802e6bb21` | 方法论/清单 |
| `appraise-12-通用审核规则.md` | `skills/appraisal-knowledge-base/references/general-audit-rules.md` | 209 | `aa089b1be70570e1` | 方法论/清单 |
| `appraise-13-矿业权评估审核.md` | `skills/appraisal-knowledge-base/references/mining-rights-audit.md` | 89 | `db80ab08e65fb062` | 方法论/清单 |
| `appraise-14-方法参数与折现率.md` | `skills/appraisal-knowledge-base/references/method-parameters.md` | 142 | `f099ed0eacf57f5e` | 方法论/清单 |
| `appraise-15-资产基础法指南.md` | `skills/appraisal-knowledge-base/references/asset-based-guide.md` | 210 | `5aff8de9fa887734` | 方法论/清单 |
| `appraise-16-案例先例.md` | `skills/appraisal-knowledge-base/references/case-precedents.md` | 83 | `c4a9ddd778da5111` | 方法论/清单 |
| `appraise-17-真实报告语料基准.md` | `skills/appraisal-knowledge-base/references/real-report-benchmarks.md` | 88 | `af31625c05827280` | 方法论/清单 |
| `appraise-18-监管问询高频点.md` | `skills/appraisal-knowledge-base/references/inquiry-focus-points.md` | 85 | `560713a330138fd6` | 方法论/清单 |

### 表三　准则原文（`appraise-19`~`appraise-77`，59 份全文）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `appraise-19-准则-01基本准则-资产评估基本准则.md` | `skills/appraisal-knowledge-base/references/准则原文/01基本准则_资产评估基本准则.md` | 150 | `4cfaea5c9858aecd` | 准则原文，引用前核现行有效 |
| `appraise-20-准则-02职业道德-资产评估职业道德准则.md` | `skills/appraisal-knowledge-base/references/准则原文/02职业道德_资产评估职业道德准则.md` | 151 | `b63018492073d102` | 准则原文，引用前核现行有效 |
| `appraise-21-准则-03程序性-资产评估执业准则——利用专家工作及相关报告.md` | `skills/appraisal-knowledge-base/references/准则原文/03程序性_资产评估执业准则——利用专家工作及相关报告.md` | 139 | `2d0c6298fd836672` | 准则原文，引用前核现行有效 |
| `appraise-22-准则-03程序性-资产评估执业准则——资产评估委托合同.md` | `skills/appraisal-knowledge-base/references/准则原文/03程序性_资产评估执业准则——资产评估委托合同.md` | 115 | `f90c8be96aa3f6e2` | 准则原文，引用前核现行有效 |
| `appraise-23-准则-03程序性-资产评估执业准则——资产评估报告.md` | `skills/appraisal-knowledge-base/references/准则原文/03程序性_资产评估执业准则——资产评估报告.md` | 175 | `94aade9ad29a81d7` | 准则原文，引用前核现行有效 |
| `appraise-24-准则-03程序性-资产评估执业准则——资产评估方法.md` | `skills/appraisal-knowledge-base/references/准则原文/03程序性_资产评估执业准则——资产评估方法.md` | 138 | `9a518780691a665a` | 准则原文，引用前核现行有效 |
| `appraise-25-准则-03程序性-资产评估执业准则——资产评估档案.md` | `skills/appraisal-knowledge-base/references/准则原文/03程序性_资产评估执业准则——资产评估档案.md` | 89 | `4e15f55c8bef5dfe` | 准则原文，引用前核现行有效 |
| `appraise-26-准则-03程序性-资产评估执业准则——资产评估程序.md` | `skills/appraisal-knowledge-base/references/准则原文/03程序性_资产评估执业准则——资产评估程序.md` | 146 | `f62a0abcccae3bf1` | 准则原文，引用前核现行有效 |
| `appraise-27-准则-04实体性-资产评估执业准则——不动产.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——不动产.md` | 160 | `89f6a1829904ab63` | 准则原文，引用前核现行有效 |
| `appraise-28-准则-04实体性-资产评估执业准则——企业价值.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——企业价值.md` | 263 | `5e1467b93afcfa47` | 准则原文，引用前核现行有效 |
| `appraise-29-准则-04实体性-资产评估执业准则——无形资产.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——无形资产.md` | 130 | `998bf0096f1c9214` | 准则原文，引用前核现行有效 |
| `appraise-30-准则-04实体性-资产评估执业准则——机器设备.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——机器设备.md` | 113 | `f0c7abca8f99e09c` | 准则原文，引用前核现行有效 |
| `appraise-31-准则-04实体性-资产评估执业准则——森林资源资产.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——森林资源资产.md` | 103 | `715915cb1eac8e34` | 准则原文，引用前核现行有效 |
| `appraise-32-准则-04实体性-资产评估执业准则——珠宝首饰.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——珠宝首饰.md` | 120 | `83da3bc804f62593` | 准则原文，引用前核现行有效 |
| `appraise-33-准则-04实体性-资产评估执业准则——知识产权.md` | `skills/appraisal-knowledge-base/references/准则原文/04实体性_资产评估执业准则——知识产权.md` | 231 | `8749b12d05e0ae15` | 准则原文，引用前核现行有效 |
| `appraise-34-准则-05评估指南-以财务报告为目的的评估指南.md` | `skills/appraisal-knowledge-base/references/准则原文/05评估指南_以财务报告为目的的评估指南.md` | 177 | `c316b0b26117e763` | 准则原文，引用前核现行有效 |
| `appraise-35-准则-05评估指南-企业国有资产评估报告指南.md` | `skills/appraisal-knowledge-base/references/准则原文/05评估指南_企业国有资产评估报告指南.md` | 1059 | `872bc6ec37e266de` | 准则原文，引用前核现行有效 |
| `appraise-36-准则-05评估指南-资产评估机构业务质量控制指南.md` | `skills/appraisal-knowledge-base/references/准则原文/05评估指南_资产评估机构业务质量控制指南.md` | 375 | `66fd032d690b1d7d` | 准则原文，引用前核现行有效 |
| `appraise-37-准则-05评估指南-金融企业国有资产评估报告指南.md` | `skills/appraisal-knowledge-base/references/准则原文/05评估指南_金融企业国有资产评估报告指南.md` | 1109 | `7a943109357be512` | 准则原文，引用前核现行有效 |
| `appraise-38-准则-06指导意见-专利资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_专利资产评估指导意见.md` | 166 | `bbe798ce1082c969` | 准则原文，引用前核现行有效 |
| `appraise-39-准则-06指导意见-人民法院委托司法执行财产处置资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_人民法院委托司法执行财产处置资产评估指导意见.md` | 169 | `651cc6bbba58eefd` | 准则原文，引用前核现行有效 |
| `appraise-40-准则-06指导意见-企业并购投资价值评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_企业并购投资价值评估指导意见.md` | 232 | `aa535aa5549c6cc8` | 准则原文，引用前核现行有效 |
| `appraise-41-准则-06指导意见-体育无形资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_体育无形资产评估指导意见.md` | 436 | `b0e634ebceb1553a` | 准则原文，引用前核现行有效 |
| `appraise-42-准则-06指导意见-关键核心技术资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_关键核心技术资产评估指导意见.md` | 302 | `1f18b36fc86b0298` | 准则原文，引用前核现行有效 |
| `appraise-43-准则-06指导意见-商标资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_商标资产评估指导意见.md` | 150 | `88474ea7614562c2` | 准则原文，引用前核现行有效 |
| `appraise-44-准则-06指导意见-实物期权评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_实物期权评估指导意见.md` | 251 | `3f1165ef3372ead0` | 准则原文，引用前核现行有效 |
| `appraise-45-准则-06指导意见-投资性房地产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_投资性房地产评估指导意见.md` | 124 | `0970b91b2faebb01` | 准则原文，引用前核现行有效 |
| `appraise-46-准则-06指导意见-数据资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_数据资产评估指导意见.md` | 383 | `6d61dc98fe5c8db8` | 准则原文，引用前核现行有效 |
| `appraise-47-准则-06指导意见-文化企业无形资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_文化企业无形资产评估指导意见.md` | 432 | `bf7f2447fccbf4ff` | 准则原文，引用前核现行有效 |
| `appraise-48-准则-06指导意见-珠宝首饰评估程序指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_珠宝首饰评估程序指导意见.md` | 198 | `47e1291f3c78d895` | 准则原文，引用前核现行有效 |
| `appraise-49-准则-06指导意见-著作权资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_著作权资产评估指导意见.md` | 168 | `b2b3bb13df4d4b1c` | 准则原文，引用前核现行有效 |
| `appraise-50-准则-06指导意见-资产评估价值类型指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_资产评估价值类型指导意见.md` | 92 | `4a66f8c87a37c086` | 准则原文，引用前核现行有效 |
| `appraise-51-准则-06指导意见-资产评估对象法律权属指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_资产评估对象法律权属指导意见.md` | 49 | `81155c8ef11cc1a1` | 准则原文，引用前核现行有效 |
| `appraise-52-准则-06指导意见-金融不良资产评估指导意见.md` | `skills/appraisal-knowledge-base/references/准则原文/06指导意见_金融不良资产评估指导意见.md` | 107 | `56bf221ff197e98e` | 准则原文，引用前核现行有效 |
| `appraise-53-准则-07专家指引-资产评估专家指引第10号——在新冠肺炎疫情期间合理履行资产评估程序.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第10号——在新冠肺炎疫情期间合理履行资产评估程序.md` | 86 | `7b53a9c80eecf4a2` | 准则原文，引用前核现行有效 |
| `appraise-54-准则-07专家指引-资产评估专家指引第11号——商誉减值测试评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第11号——商誉减值测试评估.md` | 210 | `88f1b8833a53f6d4` | 准则原文，引用前核现行有效 |
| `appraise-55-准则-07专家指引-资产评估专家指引第12号——收益法评估企业价值中折现率的测算.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第12号——收益法评估企业价值中折现率的测算.md` | 142 | `413db4c023167e96` | 准则原文，引用前核现行有效 |
| `appraise-56-准则-07专家指引-资产评估专家指引第13号——境外并购资产评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第13号——境外并购资产评估.md` | 720 | `d15b650e5878de2f` | 准则原文，引用前核现行有效 |
| `appraise-57-准则-07专家指引-资产评估专家指引第14号——科创企业资产评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第14号——科创企业资产评估.md` | 581 | `2d5a31bbb6e01a72` | 准则原文，引用前核现行有效 |
| `appraise-58-准则-07专家指引-资产评估专家指引第15号——知识产权侵权损害评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第15号——知识产权侵权损害评估.md` | 187 | `bbc999232c0901bd` | 准则原文，引用前核现行有效 |
| `appraise-59-准则-07专家指引-资产评估专家指引第16号——计算机软件著作权资产评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第16号——计算机软件著作权资产评估.md` | 292 | `1b80e65d9edd6f97` | 准则原文，引用前核现行有效 |
| `appraise-60-准则-07专家指引-资产评估专家指引第17号——碳资产评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第17号——碳资产评估.md` | 284 | `bd9a2c0e9f2d99f5` | 准则原文，引用前核现行有效 |
| `appraise-61-准则-07专家指引-资产评估专家指引第1号——金融企业评估中应关注的金融监管指标.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第1号——金融企业评估中应关注的金融监管指标.md` | 844 | `ffa8657ad489e13c` | 准则原文，引用前核现行有效 |
| `appraise-62-准则-07专家指引-资产评估专家指引第2号——金融企业首次公开发行上市资产评估方法选用.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第2号——金融企业首次公开发行上市资产评估方法选用.md` | 412 | `bba3af48abea50b6` | 准则原文，引用前核现行有效 |
| `appraise-63-准则-07专家指引-资产评估专家指引第3号——金融企业收益法评估模型与参数确定.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第3号——金融企业收益法评估模型与参数确定.md` | 666 | `5b97153722581e40` | 准则原文，引用前核现行有效 |
| `appraise-64-准则-07专家指引-资产评估专家指引第4号——金融企业市场法评估模型与参数确定.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第4号——金融企业市场法评估模型与参数确定.md` | 159 | `5d4343b590ca8e00` | 准则原文，引用前核现行有效 |
| `appraise-65-准则-07专家指引-资产评估专家指引第5号——寿险公司内部精算报告及价值评估中的利用.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第5号——寿险公司内部精算报告及价值评估中的利用.md` | 674 | `73d7d9f246b72f0d` | 准则原文，引用前核现行有效 |
| `appraise-66-准则-07专家指引-资产评估专家指引第6号——上市公司重大资产重组评估报告披露.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第6号——上市公司重大资产重组评估报告披露.md` | 127 | `df7f61d5054b4a91` | 准则原文，引用前核现行有效 |
| `appraise-67-准则-07专家指引-资产评估专家指引第7号——中小评估机构业务质量控制.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第7号——中小评估机构业务质量控制.md` | 368 | `f358f735ee1f3547` | 准则原文，引用前核现行有效 |
| `appraise-68-准则-07专家指引-资产评估专家指引第8号——资产评估中的核查验证.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第8号——资产评估中的核查验证.md` | 238 | `62118dc567997d65` | 准则原文，引用前核现行有效 |
| `appraise-69-准则-07专家指引-资产评估专家指引第9号——数据资产评估.md` | `skills/appraisal-knowledge-base/references/准则原文/07专家指引_资产评估专家指引第9号——数据资产评估.md` | 337 | `4abe8821470b6d3f` | 准则原文，引用前核现行有效 |
| `appraise-70-准则-08风险提示问答-中国资产评估协会关于实际执行中遇到的问题的解答.md` | `skills/appraisal-knowledge-base/references/准则原文/08风险提示问答_中国资产评估协会关于实际执行中遇到的问题的解答.md` | 116 | `33afb35dec0f45a6` | 准则原文，引用前核现行有效 |
| `appraise-71-准则-08风险提示问答-关注企业商誉减值测试评估业务风险的提示.md` | `skills/appraisal-knowledge-base/references/准则原文/08风险提示问答_关注企业商誉减值测试评估业务风险的提示.md` | 60 | `0e05fcad4b014214` | 准则原文，引用前核现行有效 |
| `appraise-72-准则-08风险提示问答-资产评估机构从事交易类证券评估业务风险提示.md` | `skills/appraisal-knowledge-base/references/准则原文/08风险提示问答_资产评估机构从事交易类证券评估业务风险提示.md` | 424 | `9c38b58596bef322` | 准则原文，引用前核现行有效 |
| `appraise-73-准则-08风险提示问答-资产评估机构从事财报类证券评估业务风险提示.md` | `skills/appraisal-knowledge-base/references/准则原文/08风险提示问答_资产评估机构从事财报类证券评估业务风险提示.md` | 525 | `f4543b73ec7be071` | 准则原文，引用前核现行有效 |
| `appraise-74-准则-09操作指引-PPP项目资产评估及相关咨询业务操作指引.md` | `skills/appraisal-knowledge-base/references/准则原文/09操作指引_PPP项目资产评估及相关咨询业务操作指引.md` | 4121 | `d1132dfdd1ae9d92` | 准则原文，引用前核现行有效 |
| `appraise-75-准则-09操作指引-资产评估机构开展预算绩效管理相关业务操作指引.md` | `skills/appraisal-knowledge-base/references/准则原文/09操作指引_资产评估机构开展预算绩效管理相关业务操作指引.md` | 1554 | `04fb557c5f9bf00c` | 准则原文，引用前核现行有效 |
| `appraise-76-准则-09操作指引-道路运输物流企业授信额度评估咨询操作指引（试行）.md` | `skills/appraisal-knowledge-base/references/准则原文/09操作指引_道路运输物流企业授信额度评估咨询操作指引（试行）.md` | 265 | `f52d9ded8987ef64` | 准则原文，引用前核现行有效 |
| `appraise-77-准则-10准则术语-资产评估准则术语 2020.md` | `skills/appraisal-knowledge-base/references/准则原文/10准则术语_资产评估准则术语 2020.md` | 376 | `98a8b9195d76b5f2` | 准则原文，引用前核现行有效 |

### 表四　法规·地方·实务·模板（`appraise-78`~`appraise-93`）

| 这里 | 上游原名 | 行数 | sha256 前 16 位 | 用法 |
|---|---|---|---|---|
| `appraise-78-法规制度-00-法规制度总索引.md` | `skills/appraisal-knowledge-base/references/法规制度/00_法规制度总索引.md` | 97 | `f5da1898ccf9e1ac` | 法规全文，引用前核现行有效 |
| `appraise-79-法规制度-01-涉国资法律法规-涉国资法律法规-正文.md` | `skills/appraisal-knowledge-base/references/法规制度/01_涉国资法律法规/涉国资法律法规_正文.md` | 15511 | `b341adeb64de221a` | 法规全文，引用前核现行有效 |
| `appraise-80-法规制度-02-国资管理问题回复-00-索引.md` | `skills/appraisal-knowledge-base/references/法规制度/02_国资管理问题回复/00_索引.md` | 34 | `89910042406e1a12` | 法规全文，引用前核现行有效 |
| `appraise-81-法规制度-02-国资管理问题回复-回复汇总.md` | `skills/appraisal-knowledge-base/references/法规制度/02_国资管理问题回复/回复汇总.md` | 507 | `1665dc05dac653a0` | 法规全文，引用前核现行有效 |
| `appraise-82-法规制度-03-地方性文件-地方性文件-正文.md` | `skills/appraisal-knowledge-base/references/法规制度/03_地方性文件/地方性文件_正文.md` | 3087 | `b5bc50f297cdc2ee` | 法规全文，引用前核现行有效 |
| `appraise-83-法规制度-04-司法文件-司法文件-正文.md` | `skills/appraisal-knowledge-base/references/法规制度/04_司法文件/司法文件_正文.md` | 1843 | `b2165ede85c747b7` | 法规全文，引用前核现行有效 |
| `appraise-84-法规制度-05-证券相关文件-证券相关文件-正文.md` | `skills/appraisal-knowledge-base/references/法规制度/05_证券相关文件/证券相关文件_正文.md` | 1187 | `f6d2e58109d5cb6d` | 法规全文，引用前核现行有效 |
| `appraise-85-法规制度-06-深圳国资委-深圳国资委相关文件-正文.md` | `skills/appraisal-knowledge-base/references/法规制度/06_深圳国资委/深圳国资委相关文件_正文.md` | 1253 | `e9a7f55b36e535a7` | 法规全文，引用前核现行有效 |
| `appraise-86-地方协会文件-00-登记索引.md` | `skills/appraisal-knowledge-base/references/地方协会文件/00_登记索引.md` | 117 | `d456ec253a17eddb` | 地方口径，非浙江/台州 |
| `appraise-87-地方协会文件-01-汇总.md` | `skills/appraisal-knowledge-base/references/地方协会文件/01_汇总.md` | 15465 | `2f4cdf7302230e1b` | 地方口径，非浙江/台州 |
| `appraise-88-实务口径-1.16补充资料-00-正文.md` | `skills/appraisal-knowledge-base/references/实务口径/1.16补充资料/00_正文.md` | 7994 | `a3429863c77024cf` | 实务口径汇编，体量大按需检索 |
| `appraise-89-实务口径-1.16补充资料-00-登记索引.md` | `skills/appraisal-knowledge-base/references/实务口径/1.16补充资料/00_登记索引.md` | 44 | `da45e83c000fc354` | 实务口径汇编，体量大按需检索 |
| `appraise-90-评估报告模板.md` | `templates/valuation-report-template.md` | 174 | `db76bfd78c28e1c9` | 报告骨架，直接套用 |
| `appraise-91-审核意见格式-单一主体股权.docx` | `templates/opinion-style-examples/2026-0666西安金融有限公司 初审意见-单一主体股权项目审核意见格式参考.docx` | 61 | `7ca80ad19917893c` | 真实审核意见格式参考 |
| `appraise-92-审核意见格式-多主体公司.docx` | `templates/opinion-style-examples/2026-1314北京热火股份有限公司 初审意见-多主体公司审核意见格式参考.docx` | 77 | `a3cac9798b235bbe` | 真实审核意见格式参考 |
| `appraise-93-审核意见格式-单项资产.docx` | `templates/opinion-style-examples/2026-9999中国神州科技有限公司设备租金项目 初审意见-单项资产审核意见格式参考.docx` | 62 | `0396103ee2700f9d` | 真实审核意见格式参考 |

核对是否被改过：`sha256sum <文件> | cut -c1-16` 应与此表一致。`python check.py` 第 10 项会自动核。
程序化取某一类：`ls | grep '^appraise-\(19\|2[0-9]\)'`（准则原文开头），或直接按上表序号定位。

## 只读纪律

改一个字，`check.py` 第 10 项就报错。往这个目录塞清单外的文件，也报错。

- 天信要补、要纠、要本土化 → 写 `SKILL.md`，不要在这层加东西
- 上游本身有硬错误（准则过期、文号错）→ **先改对再放进来**，并在对照表记「已修正，原值 X，依据文号 Y」
- 上游是别地口径（广州 / 深圳国资）→ **原样留着 + 用法列标注**，天信按浙江 / 台州口径另写
