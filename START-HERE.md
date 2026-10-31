# START HERE · 给 AI 的执行说明书

你现在被要求启用这个仓库。这份文件告诉你**怎么一步步落地**。

不要先向用户长篇解释这个仓库是什么——他想用，不想听课。
按下面四步走，每步做完说一句结果，遇到选择就问。

---

## 你要完成的事

把仓库里的技能目录装好，然后验证能用。

**默认是方式一（装到本机全局）**，直接执行就行，不用先问用户。
另外两种（专家包、项目级）在检测到对应信号时才换，见第 2 步。

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
find . -name SKILL.md -not -path './.git/*' | sort    # 应看到十条
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
仓库分三层，共十个技能：

公用能力（三条，跨业务线都用）
1. 天信文档与报告 —— 出 Word / PDF / 网页报告、演示和 **Excel 表**（底稿/勾稽/抽样/测算），带天信品牌格式
2. 天信实务知识库 —— 12 张会计审计实务判断卡
3. 陈版主实务问答 —— 检索视野论坛的实务答疑和准则原文

业务线（六条，技能均已建，状态一律为初稿）
4. 天信审计底稿 —— 审计计划 / 风险评估 / 四程序 / 抽样 / 报告质控 / 底稿索引
5. 天信税务申报 —— 算税 / 申报 / 勾稽 / 风险自查 / 发票审查
6. 天信代账作业 —— 建账 / 票据 / 凭证 / 月结 / 报表 / 申报 / 交接（弹性编排）
7. 天信会计核算 —— 凭证复核 / 报表 / 附注 / 合并 / 会计政策 / 财务分析（会计师团队）
8. 天信评估造价 —— 三大评估方法 / 价值类型 / 参数 / 现场核查 / 报告审核 / 准则原文检索（工程造价待建）
9. 天信企业咨询 —— 战略 / 组织 / 人力 / 制度流程 / 品牌营销 / 经营改善 / 中小企业经营诊断（管理建议，不做鉴证结论）

运营（一条）
10. 天信日报 —— 每日行业与商机情报
```

**报完补一句**：六条业务线现在都建好了——审计、税务、代理记账、会计核算、评估造价、企业咨询。还空着的是**工程造价咨询**（评估造价线只收了资产评估两个包）和**审计底稿的真实格式**（现在是通用框架，还没用所里真实底稿换过）。这不是漏装，是还没材料。

---

## 第 2 步 · 默认装全局（另外两种按需换）

**不要问「你想装哪种」，直接开装。**

九成的人就是要装到全局——所有目录、所有对话都能用，这是默认选择。
`install.py` 不给任何参数时就是它：

```bash
python install.py
```

早先这里要求先问用户三选一，实测下来是个坏流程：多数人被问到「你想装哪种」
只会回一句「随便 / 你看着办」，白卡一道。默认给最通用的，想换的人自己会说。

装完告诉用户：

> 已装到本机全局，任何目录、任何对话都能用。
>
> 另外两种，需要的话随时换：
> - `python install.py --expert` —— 装成 WorkBuddy 专家「天信办公专家」，
>   左侧「专家 → 我的专家」里点开即用。**只对 WorkBuddy 有效**
> - `python install.py --project <目录>` —— 只装进某个项目，
>   适合给一个客户单独配一套，不干扰其他项目

**什么时候别用默认**，主动换掉：

| 看到什么 | 换成 |
|---|---|
| 用户一开始就说了「装成专家」「装进我那个项目」 | 按他说的来，别多问 |
| 环境只探到 `~/.cursor`（Cursor 不认 skill 目录） | 方式三，装成 `.cursor/rules/` |
| 用户明确说不想让其他项目的对话也受影响 | 方式三 |
| 用户要的是固定入口、不想记触发词 | 方式二 |

**唯一必须停下来问的情况**：完全探不到用户级 skills 目录，也不知道用户用什么
AI 工具。这时问一句「你平时用哪个 AI 工具」，别猜——装错目录比多问一句麻烦得多。

---

## 第 3 步 · 执行

### 方式一 · 全局技能（默认）

```bash
python install.py              # 不给参数就是它；--global 是等价的显式写法
```

它会做三件事：把技能目录复制到用户级 skills 目录、跳过已存在的同名技能（除非加 `--force`）、逐个校验 `SKILL.md` 的 frontmatter。

注意安装后的目录名取自 `SKILL.md` 的 `name`，不是源目录名——`天信文档skill/` 装出来是 `天信文档与报告/`。

装完必须重启对话或新开一个会话，技能才会被加载。

**手工版**（没有 Python 时）：

技能散在业务线目录下，**没有一个统一的 `skills/` 目录**，所以要逐个复制，且**目标目录名要改成 `SKILL.md` 里的 `name`**：

```bash
mkdir -p ~/.workbuddy/skills
cp -r 公用/天信文档skill         ~/.workbuddy/skills/tianxin-docs
cp -r 公用/天信实务知识库skill    ~/.workbuddy/skills/tianxin-shiwu-kb
cp -r 公用/陈版主实务问答skill    ~/.workbuddy/skills/chenyiwei-bbs
cp -r 审计/天信审计底稿           ~/.workbuddy/skills/tianxin-audit
cp -r 税务/天信税务申报skill      ~/.workbuddy/skills/tianxin-tax
cp -r 代理记账/天信代账作业skill   ~/.workbuddy/skills/tianxin-bookkeeping
cp -r 会计核算/天信会计核算skill   ~/.workbuddy/skills/tianxin-accounting
cp -r 评估造价/天信评估造价skill   ~/.workbuddy/skills/tianxin-appraisal
cp -r 企业咨询/天信企业咨询skill   ~/.workbuddy/skills/tianxin-consulting
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

**手工版**（没有 Python 时）：把 `专家/plugin.json`、`专家/agents/*.md`、`专家/avatars/*.png` 复制到 `~/.workbuddy/plugins/marketplaces/my-experts/plugins/tianxin-office-expert/` 对应位置，再把技能目录复制进该目录的 `skills/`，最后手工在 `~/.workbuddy/plugins/marketplaces/my-experts/.codebuddy-plugin/marketplace.json` 的 `plugins` 数组里加一条。详细步骤见 `docs/03-专家包安装.md`。

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
cp -r 公用/天信文档skill         "$P/.workbuddy/skills/tianxin-docs"
cp -r 公用/天信实务知识库skill    "$P/.workbuddy/skills/tianxin-shiwu-kb"
cp -r 公用/陈版主实务问答skill    "$P/.workbuddy/skills/chenyiwei-bbs"
cp -r 审计/天信审计底稿           "$P/.workbuddy/skills/tianxin-audit"
cp -r 税务/天信税务申报skill      "$P/.workbuddy/skills/tianxin-tax"
cp -r 运营/天信日报skill          "$P/.workbuddy/skills/tianxin-daily-brief"
```

---

## 第 4 步 · 验收（不能省）

```bash
python install.py --verify
```

它会逐个报告：目录在不在、`SKILL.md` 在不在、frontmatter 的 name/description 能不能解析、技能自带的脚本依赖是否满足。

看到十个对勾才算装完（下面是一台已装好的机器上的真实输出）：

```
  ✓ tianxin-shiwu-kb  tianxin-shiwu-kb · 12 张能力卡
  ✓ 天信文档与报告  天信文档与报告 · 11 份 references · 12 个脚本
  ✓ chenyiwei-bbs  chenyiwei-bbs
  ✓ 天信审计底稿  天信审计底稿 · 7 份 references
  ✓ 天信税务申报  天信税务申报 · 5 份 references
  ✓ 天信代账作业  天信代账作业 · 13 份 references
  ✓ 天信会计核算  天信会计核算
  ✓ 天信评估造价  天信评估造价
  ✓ 天信企业咨询  天信企业咨询
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
