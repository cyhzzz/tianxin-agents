# START HERE · 给 AI 的执行说明书

你现在被要求启用这个仓库。这份文件告诉你**怎么一步步落地**。

不要先向用户长篇解释这个仓库是什么——他想用，不想听课。
按下面四步走，每步做完说一句结果，遇到选择就问。

---

## 你要完成的事

把仓库里的技能目录，按用户选的方式装到某个地方，然后验证能用。

三种方式选一种，**由用户决定，不由你决定**。

---

## 第 0 步 · 摸清环境（不要跳过）

**前提：所有命令都在仓库根目录执行**（就是含 `install.py` 和 `START-HERE.md` 的那一层）。
clone 之后通常要 `cd tianxin-agents`。不在根目录，`find .` 和 `python install.py` 都会找不到东西。

先确认三件事，再动手：

```bash
pwd                      # 必须能看到 install.py。看不到就 cd 到仓库根
ls install.py
python --version         # 或 python3 --version；没有 Python 就记下来
# 技能散在业务线目录下，要递归找（根目录直接 ls 是找不到的）
find . -name SKILL.md -not -path './.git/*' | sort    # 应看到六条
```

同时查一下这台机器上已有的 skill 目录：

```bash
ls -d ~/.workbuddy/skills 2>/dev/null
ls -d ~/.claude/skills 2>/dev/null
ls -d .workbuddy/skills 2>/dev/null
```

| 查到什么 | 说明 |
|---|---|
| `~/.workbuddy/skills` 存在 | 用户在 WorkBuddy，方式一装这里 |
| `~/.claude/skills` 存在 | 用户在 Claude Code，方式一装这里 |
| 只有 `~/.cursor` | Cursor 不认 skill 目录，也不支持 WorkBuddy 专家 → **方式三**，装成 `.cursor/rules/` |
| 都没有 | 别猜，问用户「你平时用哪个 AI 工具」 |

**如果没有 Python**：不要卡住。三种方式全都有手工版，见下面各节末尾的「手工版」。

---

## 第 1 步 · 让用户看清有什么（一句话就够）

先看清仓库的分层，再报给用户。**不要展开讲原理**：

```
仓库分三层，共六个技能：

公用能力（三条，跨业务线都用）
1. 天信文档与报告 —— 出 Word / PDF / 网页报告和演示，带天信品牌格式
2. 天信实务知识库 —— 12 张会计审计实务判断卡
3. 陈版主实务问答 —— 检索视野论坛的实务答疑和准则原文

业务线（五条，已建两条）
4. 天信审计底稿 —— 审计计划 / 风险评估 / 四程序 / 抽样 / 报告质控 / 底稿索引
5. 天信税务申报 —— 算税 / 申报 / 勾稽 / 风险自查 / 发票审查
   代理记账、企业咨询、评估造价三条线仍是骨架，
   要建什么、缺什么材料，见各自目录下的 README.md

运营（一条）
6. 天信日报 —— 每日行业与商机情报
```

**报完补一句**：五条业务线里建好了审计和税务。审计那份的底稿格式是通用框架，还没用所里真实底稿换过；代理记账、企业咨询、评估造价三条线是空的。这不是漏装，是还没建。

---

## 第 2 步 · 让用户三选一（必须问，不能替他选）

用下面这段问，把三个选项原样给出来：

> 这三个装法选一个：
>
> **一、全局技能** —— 装到本机所有对话都能用。适合你平时都用同一个 AI 工具。
> 　　装到：`~/.workbuddy/skills/`（或你这台机器上对应的用户级目录）
>
> **二、专家包** —— 装成一个 WorkBuddy 专家「天信办公专家」，`plugin.json` 声明的技能都挂在它下面。
> 　　装到：`~/.workbuddy/plugins/marketplaces/my-experts/plugins/`
> 　　适合想要固定入口、不想记技能触发词的人。代价：只对 WorkBuddy 有效。
>
> **三、项目级** —— 装进某个具体项目的目录，只在那里面生效。
> 　　适合给某个客户单独配一套。你告诉我要装进哪个目录。
>
> 你选哪个？

用户回答之后再看第 3 步对应的小节。**如果用户说「你看着办」**，按这个顺序判断：

- 用户用的是 WorkBuddy，且说过想要「一个入口」「打开就能用」 → 选方式二
- 有 `~/.workbuddy/skills` 或 `~/.claude/skills` → 选方式一
- 用户提到了某个具体项目/客户名 → 选方式三
- **用户用的不是 WorkBuddy** → 方式二不可用，选方式一或方式三，并说明原因

---

## 第 3 步 · 执行

### 方式一 · 全局技能

```bash
python install.py --global
```

它会做三件事：把技能目录复制到用户级 skills 目录、跳过已存在的同名技能（除非加 `--force`）、逐个校验 `SKILL.md` 的 frontmatter。

注意安装后的目录名取自 `SKILL.md` 的 `name`，不是源目录名——`天信文档skill/` 装出来是 `天信文档与报告/`。

装完必须重启对话或新开一个会话，技能才会被加载。

**手工版**（没有 Python 时）：

技能散在业务线目录下，**没有一个统一的 `skills/` 目录**，所以要逐个复制，且**目标目录名要改成 `SKILL.md` 里的 `name`**：

```bash
mkdir -p ~/.workbuddy/skills
cp -r 公用/天信文档skill         ~/.workbuddy/skills/天信文档与报告
cp -r 公用/天信实务知识库skill    ~/.workbuddy/skills/tianxin-shiwu-kb
cp -r 公用/陈版主实务问答skill    ~/.workbuddy/skills/chenyiwei-bbs
cp -r 审计/天信审计底稿           ~/.workbuddy/skills/天信审计底稿
cp -r 税务/天信税务申报skill      ~/.workbuddy/skills/天信税务申报
cp -r 运营/天信日报skill          ~/.workbuddy/skills/tianxin-daily-brief
```

不方便手抄就用这一条，它会自己读 `name`：

```bash
find . -name SKILL.md -not -path './.git/*' | while read -r f; do
  n=$(sed -n 's/^name: *//p' "$f" | head -1)
  cp -r "$(dirname "$f")" "$HOME/.workbuddy/skills/$n"
done
```

然后把每个技能的 `SKILL.md` 打开看一眼，frontmatter 里 `name:` 和 `description:` 两行必须在。缺了 description，技能不会被自动触发。

---

### 方式二 · 专家包（WorkBuddy 专家）

这是把技能打包成**一个带人设的专家**，装进 WorkBuddy 的专家目录。装完用户在左侧「专家 → 我的专家」里选「天信办公专家」，点开即用。

```bash
python install.py --expert
```

它做四件事：建专家目录 → 写 `plugin.json` → 复制人设与头像 → 把 `plugin.json` 声明的技能复制进去 → 注册到 `marketplace.json`。

**注册那步最关键**。不写 `marketplace.json`，专家目录建得再完整，WorkBuddy 里也看不到。

装完你要告诉用户：

> 打开 WorkBuddy → 左侧「专家」→ 我的专家 → 选「天信办公专家」。
> 如果没看到，重启 WorkBuddy 再进一次。

**只在 WorkBuddy 上有效**。如果用户用的是 Claude Code、Cursor 或其他 agent，方式二不适用——直接跳到方式一或方式三，并说明原因，不要硬装。

**手工版**（没有 Python 时）：把 `expert/plugin.json`、`expert/agents/*.md`、`expert/avatars/*.png` 复制到 `~/.workbuddy/plugins/marketplaces/my-experts/plugins/tianxin-office-expert/` 对应位置，再把技能目录复制进该目录的 `skills/`，最后手工在 `~/.workbuddy/plugins/marketplaces/my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组里加一条。详细步骤见 `docs/03-专家包安装.md`。

---

### 方式三 · 项目级

先确认目录：

```bash
ls /path/to/项目
```

**不要不经确认就往别人的目录里写东西。** 看清目录里有什么，再问一句「装进这个目录对吗」。

```bash
python install.py --project /path/to/项目
```

它会在 `<项目>/.workbuddy/skills/` 下建技能目录，并在 `<项目>/.workbuddy/skills/README.md` 写一份清单，说明这些技能从哪来、怎么更新。

如果项目里已经有 `.workbuddy/skills/`，它会**追加**而不是覆盖，遇到同名技能默认跳过。

**手工版**：

```bash
P=/path/to/项目
mkdir -p "$P/.workbuddy/skills"
cp -r 公用/天信文档skill         "$P/.workbuddy/skills/天信文档与报告"
cp -r 公用/天信实务知识库skill    "$P/.workbuddy/skills/tianxin-shiwu-kb"
cp -r 公用/陈版主实务问答skill    "$P/.workbuddy/skills/chenyiwei-bbs"
cp -r 审计/天信审计底稿           "$P/.workbuddy/skills/天信审计底稿"
cp -r 税务/天信税务申报skill      "$P/.workbuddy/skills/天信税务申报"
cp -r 运营/天信日报skill          "$P/.workbuddy/skills/tianxin-daily-brief"
```

---

## 第 4 步 · 验收（不能省）

```bash
python install.py --verify
```

它会逐个报告：目录在不在、`SKILL.md` 在不在、frontmatter 的 name/description 能不能解析、技能自带的脚本依赖是否满足。

看到六个对勾才算装完（下面是一台已装好的机器上的真实输出）：

```
  ✓ tianxin-shiwu-kb  tianxin-shiwu-kb · 12 张能力卡
  ✓ 天信文档与报告  天信文档与报告 · 10 份 references · 11 个脚本
  ✓ chenyiwei-bbs  chenyiwei-bbs
  ✓ 天信审计底稿  天信审计底稿 · 7 份 references
  ✓ 天信税务申报  天信税务申报 · 5 份 references
  ✓ tianxin-daily-brief  tianxin-daily-brief · 8 份 references
```

如果有 `⚠ 技能 xxx 装了 2 份`，说明之前用别的目录名装过，移走多余的那份。

**然后做一次真实触发**，不要只看文件在不在：

- 装的是全局/项目级 → 新开一个会话，说「用天信文档规范，帮我把这篇 Markdown 出一份 Word」
- 装的是专家模式 → 把 system prompt 粘进去，问「天信的事务报告一般分几类」

技能如果没被触发，九成是 `description` 里的触发词没覆盖到用户的原话。回去补触发词，不要改工作流。

---

## 常见卡点

**`python` 不是内部或外部命令**
Windows 上试 `py -3`；或者直接走各节的手工版，全程只需要 `cp` 和文本编辑器。

**权限错误**
目标目录可能在受保护位置。装全局时不要用 `sudo`——skills 目录应该在用户 home 下，不需要提权。

**中文路径乱码**
Windows 的 cmd 对中文支持差。用 PowerShell 或 Git Bash；`install.py` 内部已按 UTF-8 读写，问题通常出在终端显示而非实际文件。

**装完 AI 还是不理我**
检查 `SKILL.md` 的 frontmatter：`name` 和 `description` 缺一不可。`description` 里要包含用户可能说的原话（「尽调报告」「审计报告格式」「陈版主」这类），而不只是功能描述。

**同名技能已存在**
说明之前装过。先 `diff` 一下新旧 `SKILL.md`，确认是不是旧版，再决定 `--force` 覆盖还是先备份。

---

## 红线

- **不要替用户选装法**。三种的代价不同，只有他知道自己要什么。
- **不要往没确认的目录里写**。方式三尤其。
- **不要假装装成功**。`--verify` 没过就说没过，错了就说哪里错。
- **不要改技能内容**。装的是发布版。用户要改是另一件事，改完得回仓库维护，不然下次 `git pull` 就冲掉了。
