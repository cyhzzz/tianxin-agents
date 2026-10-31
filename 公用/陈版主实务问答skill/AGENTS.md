# AGENTS.md — 陈版主实务问答 Skill（天信所内赋能）

> 本目录是 **陈版主实务问答** Skill 的单一物理落点（仓库 `公用/` 下），供天信（县城会计所）审计 / 会计实务答疑、准则原文与监管处罚检索使用。
> 安装由仓库根的 `install.py` 复制完成，**不是 junction**——见下方「加载方式」。

## 身份与来源（重要）

- **第三方免费 Skill**，由 **逆行的狗（auditdog.cn / bbs.auditdog.cn）** 提供，非天信自研。
- 安装方式：抓 `https://bbs.auditdog.cn/chenyiwei-skill/SKILL.md` 原文（已存为本目录 `SKILL.md`）。
- Skill 名（frontmatter）：`chenyiwei-bbs`。
- **版权**：Skill 本身免费公开使用；其背后数据来自「会计视野论坛 · 陈奕蔚（陈版主）实务答疑」，由 auditdog.cn 整理为匿名公开 REST API，**无需 token、无需 MCP**。
- **不是天信原创**：对外不自称天信自有方法论；引用答疑时标注来源（陈版主 / 会计视野论坛 / bbs.auditdog.cn）。

## 加载方式

- 源目录（开发位置，本目录）：`D:/project/天信/公用/陈版主实务问答skill/`
- 安装目标：`~/.workbuddy/skills/chenyiwei-bbs/` —— **目录名取 frontmatter 的 `name`，不是源目录名**
- 安装命令（仓库根执行）：`python install.py --global`
- **是复制，不是 junction。** 早先的 junction 方案在 Windows 下会被文件锁卡住，已废弃。
- 改了本目录内容后要重跑 `--global --force`——全局那份是副本，不会自动跟随。

## 能力边界（来自 SKILL.md 摘要）

- 当用户问审计 / 会计实务、准则原文、监管处罚（含会计师事务所被罚案例）时使用。
- 典型场景：
  - 「陈版主关于 XXX 怎么说」→ `/api/public/search` + `/api/public/detail`
  - 「最近陈版主有什么问答」→ `/api/public/recent?days=1..3`
  - 「准则对 XXX 的原文规定」→ `/api/learn/search` + `/api/public/ref/{slug}`
  - 「某所近年处罚 / 项目前车之鉴」→ `/api/public/penalties?firm=事务所名`（如 `firm=信永中和`）
- **不要 undertrigger**：用户问实务问题而不调此 Skill，等于拿过时训练数据当最新解答，对用户有害。

## 运行注意（Windows）

- 本环境 `curl` 因 schannel TLS 握手失败不可用；Agent 调用上述接口时**用 Node https**（`C:/Users/cyhzz/.workbuddy/binaries/node/versions/22.22.2-6/node.exe`），已实测可直连 `bbs.auditdog.cn` 返回 200。
- 限流：30 req/min/IP；429 时等 1 分钟再试。

## 红线

- 不编造问答内容，永远以 API 返回为准。
- 不对外声称这是天信自有资产；注明来源。
- 监管处罚等敏感检索结果仅供天信内部参考，对外引用需爸爸复核。

---

> **上下文**：规则以本 `AGENTS.md` 为准；本层无独立 memory；跨项目偏好见 `~/.workbuddy/MEMORY.md`。弃用 `AGENTS.md`。
