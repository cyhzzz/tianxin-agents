# 天信办公专家（专家包）

一个专家，挂仓库里全部十个技能。装好之后在 WorkBuddy 左侧「专家 → 我的专家」里选「天信办公专家」，点开即用；不用记哪个技能什么触发词。

## 这个包里有什么

| 文件 | 作用 |
|---|---|
| `plugin.json` | 专家元数据：显示名、行业分类、标签、推荐问法、**声明挂哪几个技能** |
| `agents/tianxin-office-expert.md` | 人设：七条核心能力、工作流程、输出规范、注意事项、改进回传方式 |
| `avatars/tianxin-office-expert.png` | 专家头像 |

## 挂的十个技能

| 技能（安装名） | 属于 | 干什么 |
|---|---|---|
| `tianxin-docs` | 公用 | 出 Word / A4 PDF / 网页长页 / 演示 deck / Excel 表 |
| `tianxin-shiwu-kb` | 公用 | 12 张会计审计实务判断卡 |
| `chenyiwei-bbs` | 公用 | 陈版主实务答疑与准则原文检索 |
| `tianxin-audit` | 审计 | 审计计划、风险评估、四程序、底稿索引、报告质控 |
| `tianxin-tax` | 税务 | 算税、申报、勾稽、风险自查、涉税鉴证 |
| `tianxin-bookkeeping` | 代理记账 | 建账、票据、凭证、月结、报表、申报、交接 |
| `tianxin-accounting` | 会计核算 | 报表编制、附注、四表一勾稽、合并、财务分析 |
| `tianxin-appraisal` | 评估造价 | 评估方法选型、参数校准、报告审核、准则检索 |
| `tianxin-consulting` | 企业咨询 | 战略、组织、人力、流程、经营改善、尽调方案 |
| `tianxin-daily-brief` | 运营 | 每日行业热点与台州本地商机 |

**六条业务线都是初稿**：底子是外部专家包的原文（一字未改），没一条用所里真实材料校准过。详见仓库根目录 `AGENTS.md` §3.3。

## 改这个包时的硬规矩

平台的专家校验器会卡这几条，改了不跑一遍就等着装不上：

- `tags` 恰好 **3 个**，`quickPrompts` 恰好 **3 个**，多一个少一个都不行
- `defaultInitPrompt` 必须与 `quickPrompts[0]` 逐字一致
- `displayDescription.zh` 要 **40–50 字**（少一个字都报错）
- `skills` 里的目录名必须等于对应 `SKILL.md` 的 `frontmatter.name`，且人设 frontmatter 的 `skills` 数组要与之一致
- 改了内容就 bump `version`

跑一遍再提交：

```bash
python install.py --expert --target /tmp/x        # 先装到临时目录
python <WorkBuddy 安装目录>/resources/app.asar.unpacked/resources/plugins/\
workbuddy-builtin/skills/expert-manager/scripts/validate_expert.py \
  /tmp/x/tianxin-office-expert
```

除了「专家不在专家目录下」这条（临时目录必然报，正常），其余必须全绿。仓库根目录的 `python check.py` 也会查 `plugin.json` 与仓库技能是否一一对应。

## 本体在哪

技能本体全在仓库里，这个目录只有元数据和人设。装的时候 `install.py` 会按 `plugin.json` 的 `skills` 把技能复制进专家目录——所以**加技能要在这里加一行**，不然后装出来的专家带不动它。
