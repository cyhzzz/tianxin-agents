# AGENTS.md — 天信实务知识库 Skill

> 本目录是「天信实务知识库」Skill 的物理落点，与「陈版主实务问答 Skill」同级，供天信审计 / 会计 / 税务实务检索与系统化判断。
> WorkBuddy 通过 junction 加载，真实文件在 `天信本身/天信实务知识库skill/`。

## 结构

- `SKILL.md` — 12 张能力卡索引 + 使用方式 + 红线。
- `cards/` — 12 张能力卡（六节：核心理念 / 判断直觉 / 准则依据 / 天信场景 / 演练输出 / 关联卡）。
- Skill 名（frontmatter）：`tianxin-shiwu-kb`。

## 加载方式

- 物理目录：`D:/AIproject/爸爸/天信本身/天信实务知识库skill/`
- 加载 junction：`D:/AIproject/爸爸/.workbuddy/skills/天信实务知识库skill` → 指向上述物理目录
- **勿删除该 junction**，否则 WorkBuddy 无法加载此 Skill（与 天信日报skill / 陈版主实务问答skill 同理）。

## 边界

- 本知识库为天信**内部编译**的实务参考，**不对外发布、不转售**；涉及监管处罚等敏感内容，对外引用须经合伙人复核。
- 卡内数据为公开监管处罚汇总 / 公开准则提炼，非特指任何第三方专有内容。
- 新增或修订卡：直接在 `cards/` 增改，并在 `SKILL.md` 表格登记；保持六节结构一致。
- 不替代注册会计师职业判断，重大疑难按执业准则与所内复核流程处理。

---

> **上下文**：规则以本 `AGENTS.md` 为准；本层无独立 memory；跨项目偏好见 `~/.workbuddy/MEMORY.md`。弃用 `CLAUDE.md`。
