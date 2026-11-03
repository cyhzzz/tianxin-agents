# AGENTS.md — 天信日报skill（天台天信会计师事务所 · 所内赋能子项目）

> 本目录是天信「所内赋能」的一个独立子项目：**天信每日行业与商机日报** Skill。
> 它服务事务所自身（行业情报 + 商机捕捉 + 每日推送），**不对应某个付费客户**，归 `运营/`。

---

## 1. 项目身份

- **性质**：WorkBuddy Skill（自动化情报采集 + 三通道推送），是天信内部日常运营工具。
- **归属**：`运营/`（所内赋能），非 `企业咨询/`（客户项目）。
- **物理位置**：`D:/project/天信/运营/天信日报skill/`（仓库内相对路径 `运营/天信日报skill/`）。
- **加载方式**：由仓库根的 `install.py` **复制**到 `~/.workbuddy/skills/tianxin-daily-brief/`
 （目录名取 frontmatter 的 `name`）。**是复制，不是 junction**——早先的 junction 方案在
 Windows 下会被文件锁卡住，已废弃。改了本目录内容后要重跑 `--global --force` 才生效。
- **版本控制 / 双仓发布**：本目录随 `cyhzzz/tianxin-agents` 仓库走（本目录不再有独立 `.git`），**同时镜像发布到独立仓 `cyhzzz/tianxin-daily-brief`**（作为日报线上发布仓 / 每日产出归档）。
  - 改了本目录内容后两件事都要做：① 提交 `tianxin-agents`；② 跑 `./sync-daily-brief.sh` 把 skill 子树镜像到本地 `tianxin-daily-brief` 克隆并推送 GitHub（脚本位置见本目录 `sync-daily-brief.sh`）。
  - 本地 daily-brief 克隆位置：`D:/project/tianxin-daily-brief/`（脚本按 `仓库根/../tianxin-daily-brief` 定位，不存在会自动克隆）。
  - ⚠️ 同步**只覆盖 skill 代码**（SKILL.md / references / templates / assets / examples），**不碰** daily-brief 仓里的根级 `tianxin-dashboard.html`、`日报-*.md` 与 `daily/` 产出——那些由日报生成流程另写，避免覆盖某天归档。

---

## 2. 权威源（单一真相）

| 文件 | 作用 |
|------|------|
| `SKILL.md` | 技能定义、生成流程、自检清单（**生成日报的唯一流程入口**） |
| `AGENTS.md`（本文件） | 项目规范、目录结构、红线、协作约定 |
| `references/推送规范.md` | 推送三通道（5G 消息 / 微信服务号 / 邮件）的唯一权威，含约束、格式、排错 |
| `references/招标商机处理规范.md` | 商机加工范式 + 核验门禁（§〇之二）+ 辐射区规则（§〇之三）+ 事故复盘与已知陷阱 |
| `references/信源清单.md` | 信源本体 + 附录 A 辐射区信源 + 附录 B 有效性自评（含两库入围资质核实结论） |
| `references/信源扩充与PR流程.md` | 信源如何演进：验证 → 改清单 → 自测 → 提 PR（含 agent 边界） |
| `references/反爬与渲染页抓取.md` | **正文取不到时的升级链路**（接口直取 / Playwright / agent-browser / 内置浏览器） |
| `references/push-notify.js` | 推送执行助手（含 `buildWechatBoard` 服务号专用重排版） |
| `references/check-dashboard.js` | 机械自检（日期、占位、商机核验门禁、服务号可生成等 7 项） |
| `templates/dashboard-template.html` | 只含结构与 `{{占位符}}`，零真实内容（防过拟合） |
| `daily/{日期}.html` / `.md` / `latest.html` | 当日产出 |
| `assets/tianxin-logo.svg` | 官网红色印章 logo，**逐字节复制**，严禁任何修改 |

---

## 3. 目录结构

```
天信日报skill/
├── SKILL.md                  # 权威·流程入口
├── AGENTS.md                 # 本文件
├── assets/tianxin-logo.svg   # 官网红章（原样引用）
├── templates/                # 模板（仅占位符，无内容）
├── daily/                    # 每日产出（html + md + latest.html）
├── examples/                 # 样例看板（与模板/产出分目录）
├── references/               # 推送规范、推送助手、自检脚本、信源清单
└── （无独立 .git）            # 随 cyhzzz/tianxin-agents 仓库版本控制
```

---

## 4. 红线（继承全局 + 本项目硬性）

- **天信品牌规范**（全局 §4.2；权威源是仓库里「天信文档与报告」技能的 00-品牌规范，但本技能装到全局后读不到那份文件（本报技的 references 里也没有），所以硬规则直接列在这里，不依赖它）：0 圆角、navy `#00338D` + 亮蓝 `#0F62FE` + 金 `#B8860B`、Noto Sans SC；禁渐变 hero / 堆叠金条 / 虚线金框 / emoji / 紫 / 暖米底。
- **演示文案两禁**（全局 §4.1）：① 数据口径差异不上界面（含糊化即可）；② 内部规划/流程文案不上界面。
- **logo**：只允许逐字节复制官网 `tianxin-logo.svg`，严禁重绘 / 精简 / 改色（可加浅色底衬或反白以适应深底）。
- **不编造**：不虚构内部数据、不给 ROI 承诺；检索不到写"未检索到"。**正文取不到 ≠ 可以放弃核验**——字段抓不到时必须按 `references/反爬与渲染页抓取.md` 逐级升级，全部失败才允许判「无法核验」。
- **入围资质红线（2026-11-03 核实）**：绍兴库 `2025-12-0006`（65 家）**天信未入围**；宁波库 `NBZFCG2025077K` **未能确证入围**。宁海/新昌/嵊州三县商机一律标「不可承接·需先入库」，不计入可承接机会统计（详见 `references/信源清单.md` 附录 A2/A4）。
- **推送纪律**：短信只发纯文本（≤420 字要点版），绝不可把 HTML 塞进 `txt` 通道；服务号因注入容器带 `pre-line` 且禁用 `<style>`，须用 `buildWechatBoard` 全内联单列重排，不可直接复用桌面看板。
- **GitHub Pages 路线已证伪**（云端无写凭据 + 构建延迟致链接 404），日报一律不依赖外链，全文走短信 / 邮件 / 服务号。

---

## 5. 日常运行

```bash
# 1) 取系统日期，生成当日看板（先 daily 后推送）
node references/check-dashboard.js daily/{日期}.html     # 机械自检 7 项（含商机核验门禁）
node references/push-notify.js "天信每日日报 · {日期}" "daily/{日期}.html"   # 三通道实推
```

- 凭证：`PUSHPLUS_TOKEN` 环境变量优先；否则 `push-secrets.json`（本目录，`.gitignore` 已排除，绝不入库）。
- 改动推送逻辑：**先改 `references/推送规范.md`，再改 `push-notify.js`**。

---

> **上下文**：规则以本 `AGENTS.md` 为准；本层无独立 memory；跨项目偏好见 `~/.workbuddy/MEMORY.md`。弃用 `CLAUDE.md`。
