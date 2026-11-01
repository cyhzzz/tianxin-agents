#!/usr/bin/env python3
"""
天信办公专家 · 安装器

不带参数跑就是默认装法（推荐，九成人用这个）：

    python install.py                            ① 全部技能装到本机全局
                                                 ② 检测到 WorkBuddy 就顺手装成「天信办公专家」
                                                 ③ 提示要不要开日报定时任务

其余模式，一次只用一个：

    python install.py --list                     看仓库里有什么
    python install.py --global                   只装技能（不碰专家）
    python install.py --project /path/to/dir     装到某个项目目录
    python install.py --expert                   只装成 WorkBuddy 专家（一个专家挂全部技能）
    python install.py --verify                   检查装好了没有

可选：
    --target workbuddy|claude-code|<路径>   指定目标平台（默认自动探测）
    --force                                 覆盖已存在的同名技能 / 专家
    --only tianxin-daily-brief              只装某一个
    --no-expert                             默认动作里跳过专家安装
    --no-daily                              默认动作里不再提示日报定时任务
    --yes                                   无人值守：不问，直接按默认走

不依赖任何第三方库。Python 3.8+。
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERT_SRC = os.path.join(HERE, '专家')
EXPERT_NAME = 'tianxin-office-expert'

# 各 agent 的用户级 skills 目录，按探测优先级排列
TARGETS = {
    'workbuddy': ('~/.workbuddy/skills', 'WorkBuddy'),
    'claude-code': ('~/.claude/skills', 'Claude Code'),
    'codex': ('~/.codex/skills', 'Codex CLI'),
    'gemini': ('~/.gemini/skills', 'Gemini CLI'),
    'opencode': ('~/.config/opencode/skills', 'OpenCode'),
}

C_BOLD, C_DIM, C_OK, C_WARN, C_ERR, C_OFF = (
    ('\033[1m', '\033[2m', '\033[32m', '\033[33m', '\033[31m', '\033[0m')
    if sys.stdout.isatty() else ('', '', '', '', '', '')
)


# ── 基础 ──────────────────────────────────────────────────

def out(msg=''):
    print(msg)


def hr():
    out(C_DIM + '─' * 62 + C_OFF)


def die(msg, code=1):
    out(f'{C_ERR}✗ {msg}{C_OFF}')
    sys.exit(code)


def expand(p):
    return os.path.expanduser(os.path.expandvars(p))


# 这些目录不是技能仓库的一部分，递归扫描时整棵跳过
NON_SKILL_DIRS = {
    'docs', '专家', '培训', '天信宣传片',
    'tianxin-cpa-website-gh-pages', 'node_modules',
    # 第三方原文。里面的 SKILL.md 是上游包的子技能，不是天信的技能，
    # 绝不能被当成独立技能装出去。它跟着所属业务线技能整体复制即可。
    '上游',
}


def list_skill_dirs():
    """递归扫描仓库里带 SKILL.md 的目录。

    仓库按业务线分层（公用/ 审计/ 税务/ 代理记账/ 企业咨询/ 资产评估/ 运营/），
    技能散在这些目录下，所以必须递归。

    返回 [(安装名, 绝对路径, 相对路径)]。
    安装名取 SKILL.md 的 name —— 源目录叫「天信文档skill」，装出来的必须是
    「天信文档与报告」，否则技能名跟 frontmatter 对不上，触发会出问题。
    """
    items = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs
                   if d not in NON_SKILL_DIRS and not d.startswith(('.', '_'))]
        if 'SKILL.md' not in files:
            continue
        md = os.path.join(root, 'SKILL.md')
        fm = read_frontmatter(md)
        base = os.path.basename(root)
        install_name = (fm.get('name') or '').strip() or base.removesuffix('skill')
        items.append((install_name, root, os.path.relpath(root, HERE).replace(os.sep, '/')))
        dirs[:] = []          # 技能内部不会再嵌技能
    return sorted(items, key=lambda x: x[2])


def read_frontmatter(skill_md):
    """极简 YAML frontmatter 读取：只取顶层 key: value，够用且不引依赖"""
    with open(skill_md, encoding='utf-8') as f:
        text = f.read()
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.S)
    if not m:
        return {}
    fm, key, buf = {}, None, []
    for line in m.group(1).split('\n'):
        if re.match(r'^[A-Za-z_][\w-]*\s*:', line):
            if key:
                fm[key] = ' '.join(buf).strip()
            key = line.split(':', 1)[0].strip()
            val = line.split(':', 1)[1].strip()
            # YAML 块标量指示符（> / | / >- / |-）不是内容，后续缩进行才是
            buf = [] if val in ('>', '|', '>-', '|-', '>+', '|+') else [val]
        elif key and line.strip():
            buf.append(line.strip())
    if key:
        fm[key] = ' '.join(buf).strip()
    return fm


def walk_stats(path):
    """(文件数, 总字节)"""
    n = b = 0
    for dp, _, fns in os.walk(path):
        for fn in fns:
            n += 1
            try:
                b += os.path.getsize(os.path.join(dp, fn))
            except OSError:
                pass
    return n, b


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.0f} {unit}' if unit == 'B' else f'{n:.1f} {unit}'
        n /= 1024


# ── 目标目录探测 ───────────────────────────────────────────

def detect_user_skills_dir():
    """返回 (路径, 平台名)，探测不到返回 (None, None)"""
    for key, (p, label) in TARGETS.items():
        full = expand(p)
        if os.path.isdir(full):
            # 统一成反斜杠，否则打印出来是 C:\Users\x/.workbuddy/skills 这种半拉子
            return os.path.normpath(full), label
    return None, None


def resolve_target(args, want_global=True):
    """决定装到哪：--target 优先，其次 --project，最后自动探测"""
    if args.target:
        t = args.target
        if t in TARGETS:
            base = expand(TARGETS[t][0])
            return base, TARGETS[t][1]
        # 当成路径
        base = expand(t)
        if not want_global:
            base = os.path.join(base, '.workbuddy', 'skills')
        return base, '自定义路径'

    if not want_global and args.project:
        return os.path.join(expand(args.project), '.workbuddy', 'skills'), '项目级'

    base, label = detect_user_skills_dir()
    if base:
        return base, label
    return None, None


# ── 安装 ──────────────────────────────────────────────────

def same_tree(a, b):
    """两边是否完全一致（文件名 + 内容）。用来区分「已是最新」和「装了旧版」。"""
    def snap(root):
        items = {}
        for dirpath, _, files in os.walk(root):
            for fn in files:
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, root).replace(os.sep, '/')
                try:
                    with open(p, 'rb') as f:
                        items[rel] = hashlib.sha1(f.read()).hexdigest()
                except OSError:
                    items[rel] = '?'
        return items
    return snap(a) == snap(b)


def copy_skills(dest, force=False, only=None):
    """把 skills/* 复制到 dest。

    返回 (新装, 已是最新, 有待更新, 覆盖)。
    「已存在」分两种：内容一样（跳过，不用吭声）和内容不一样（旧版，要提示覆盖）——
    早先不分青红皂白一律跳过，结果用户 clone 了新仓库重跑一遍，看到的还是旧技能。
    """
    os.makedirs(dest, exist_ok=True)
    installed, uptodate, outdated, replaced = [], [], [], []

    for name, src, _ in list_skill_dirs():
        if only and name != only:
            continue
        target = os.path.join(dest, name)
        existed = os.path.isdir(target)
        if existed and not force:
            if same_tree(src, target):
                uptodate.append(name)
            else:
                outdated.append(name)
            continue
        if existed:
            shutil.rmtree(target)
            replaced.append(name)
        shutil.copytree(src, target)
        if not existed:
            installed.append(name)
    return installed, uptodate, outdated, replaced


def write_manifest(dest, names):
    """在目标目录留一份来源说明，避免以后忘了这批技能从哪来"""
    # 清单从仓库实时生成，不写死——业务线加了技能，这里跟着变
    rows = []
    for name, path, src in list_skill_dirs():
        fm = read_frontmatter(os.path.join(path, 'SKILL.md'))
        desc = re.sub(r'\s+', ' ', fm.get('description', ''))
        # description 首句就是「是什么」，取到第一个句号为止
        brief = re.split(r'[。；]', desc)[0][:40] if desc else ''
        rows.append(f'| `{name}` | {src} | {brief} |')

    lines = [
        '# 天信办公专家 · 技能清单',
        '',
        '本目录下的技能来自 https://github.com/cyhzzz/tianxin-agents',
        '**不要在这里直接改**——下次同步会覆盖。要改回仓库改，再重新安装。',
        '',
        '| 安装名 | 仓库位置 | 作用 |',
        '|---|---|---|',
        *rows,
        '',
        f'安装时间：{__import__("datetime").datetime.now():%Y-%m-%d %H:%M}',
        f'本次安装：{"、".join(names) if names else "（无新增）"}',
        '',
        '## 更新',
        '',
        '```bash',
        'cd tianxin-agents && git pull',
        'python install.py --force      # 默认装法：全局技能 + 专家（WorkBuddy）',
        '```',
    ]
    with open(os.path.join(dest, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


# ── 各模式 ────────────────────────────────────────────────

def cmd_list():
    items = list_skill_dirs()
    out()
    out(f'{C_BOLD}仓库里的技能{C_OFF}  ({len(items)} 个)')
    hr()
    for name, path, src_name in items:
        fm = read_frontmatter(os.path.join(path, 'SKILL.md'))
        nfiles, nbytes = walk_stats(path)
        refs = len([d for d in os.listdir(path)
                    if os.path.isdir(os.path.join(path, d)) and d == 'references'])
        out(f'{C_BOLD}{name}{C_OFF}  {C_DIM}← {src_name}/{C_OFF}')
        out(f'  {C_DIM}id{C_OFF}      {fm.get("name", "(缺 name)")}')
        out(f'  {C_DIM}规模{C_OFF}    {nfiles} 个文件 · {human(nbytes)}')
        desc = fm.get('description', '(缺 description，技能不会被自动触发)')
        desc = re.sub(r'\s+', ' ', desc)
        out(f'  {C_DIM}触发{C_OFF}    {desc[:150]}{"…" if len(desc) > 150 else ""}')
        out()

    base, label = detect_user_skills_dir()
    out(f'{C_BOLD}本机环境{C_OFF}')
    hr()
    if base:
        out(f'  探测到 {label}：{base}')
        out(f'  {C_DIM}方式一（--global）会装到这里{C_OFF}')
    else:
        out(f'  {C_WARN}没探测到已知的 skill 目录{C_OFF}')
        out('  可以用 --target 指定，或走方式二（--expert）')
    out(f'  Python {sys.version.split()[0]}  ·  {sys.executable}')
    out()


def cmd_install(args, global_scope, tail=True):
    """装技能。tail=False 时不打「下一步」，留给调用方统一收尾。返回 (装入数, 跳过数, 目标目录)"""
    dest, label = resolve_target(args, want_global=global_scope)
    if not dest:
        die('没找到可装的目录。用 --target 指定，例如 --target ~/.workbuddy/skills')

    scope = '本机全局' if global_scope else f'项目级（{expand(args.project)}）'
    out()
    out(f'{C_BOLD}安装到{C_OFF}  {os.path.normpath(dest)}')
    out(f'{C_DIM}范围：{scope} · 平台：{label}{C_OFF}')
    hr()

    installed, uptodate, outdated, replaced = copy_skills(
        dest, force=args.force, only=args.only)

    for n in installed:
        out(f'  {C_OK}✓{C_OFF} 装入  {n}')
    for n in replaced:
        out(f'  {C_OK}✓{C_OFF} 覆盖  {n}')
    if uptodate:
        # 内容一致的不逐个刷屏，一行带过
        out(f'  {C_DIM}· 已是最新  {len(uptodate)} 个：{"、".join(uptodate)}{C_OFF}')
    for n in outdated:
        out(f'  {C_WARN}↑{C_OFF} 待更新  {n}  {C_DIM}（仓库版本已变，加 --force 覆盖）{C_OFF}')

    if not (installed or replaced):
        out()
        if outdated:
            out(f'{C_WARN}已装的是旧版，本次没有覆盖（保护你本地的改动）。{C_OFF}')
            out(f'{C_DIM}要升级：python install.py --force{C_OFF}')
        elif uptodate:
            out(f'{C_OK}全部 {len(uptodate)} 个技能都已是最新，不用重装。{C_OFF}')
        else:
            out(f'{C_WARN}没有可装的技能。{C_OFF}')
        return 0, len(uptodate), len(outdated), dest

    write_manifest(dest, installed + replaced)
    n_total = len(installed) + len(replaced)

    if not tail:
        # 汇总由调用方统一打，这里不再重复一遍「装好了」
        return n_total, len(uptodate), len(outdated), dest

    out()
    hr()
    out(f'{C_OK}装好了{C_OFF}  {n_total} 个技能')

    out()
    out(f'{C_BOLD}下一步{C_OFF}')
    if global_scope:
        out('  重启对话或新开会话，技能才会被加载')
        out('  然后说一句试试：「用天信文档规范，把这篇 Markdown 出一份 Word」')
    else:
        out(f'  在这个目录下开对话，技能才会生效：cd {expand(args.project)}')
        out('  说一句试试：「用天信文档规范，把这篇 Markdown 出一份 Word」')
    out()
    out(f'{C_DIM}验收：python install.py --verify{" --project " + expand(args.project) if not global_scope else ""}{C_OFF}')
    out()
    return len(installed) + len(replaced), len(uptodate), len(outdated), dest


def expert_plugins_dir():
    """WorkBuddy 自定义专家的存放目录"""
    cfg = os.environ.get('WORKBUDDY_CONFIG_DIR') or os.path.expanduser('~/.workbuddy')
    return os.path.join(cfg, 'plugins', 'marketplaces', 'my-experts', 'plugins')


def register_in_marketplace(expert_dir):
    """把专家写进同级的 marketplace.json —— 不写这一步，WorkBuddy 里看不到"""
    plugins_dir = os.path.dirname(expert_dir)
    market_dir = os.path.join(plugins_dir, '..', '.codebuddy-plugin')
    market_file = os.path.normpath(os.path.join(market_dir, 'marketplace.json'))

    with open(os.path.join(expert_dir, '.codebuddy-plugin', 'plugin.json'), encoding='utf-8') as f:
        pj = json.load(f)

    entry = {
        'name': pj['name'],
        'source': f'./plugins/{os.path.basename(expert_dir)}',
        'description': pj.get('description', ''),
        'version': pj.get('version', '1.0.0'),
    }

    if os.path.isfile(market_file):
        with open(market_file, encoding='utf-8') as f:
            data = json.load(f)
    else:
        os.makedirs(os.path.dirname(market_file), exist_ok=True)
        data = {'name': 'my-experts',
                'description': 'my-experts marketplace (auto-generated)',
                'plugins': []}

    plugins = data.setdefault('plugins', [])
    for i, p in enumerate(plugins):
        if p.get('name') == entry['name']:
            plugins[i] = entry
            break
    else:
        plugins.append(entry)

    with open(market_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return market_file


def cmd_expert(args, tail=True):
    """装成 WorkBuddy 专家。tail=False 时只装不说怎么用，返回 (是否装上, 专家目录)"""
    src_meta = os.path.join(EXPERT_SRC, 'plugin.json')
    if not os.path.isfile(src_meta):
        die(f'找不到专家包：{EXPERT_SRC}')

    plugins_dir = expand(args.target) if args.target else expert_plugins_dir()
    dest = os.path.normpath(os.path.join(plugins_dir, EXPERT_NAME))

    out()
    out(f'{C_BOLD}装成 WorkBuddy 专家{C_OFF}')
    out(f'{C_DIM}一个专家「天信办公专家」，下面挂仓库里的全部技能{C_OFF}')
    out(f'  目标：{dest}')
    hr()

    # 注意：专家目录里的 .created-by-session 是平台自己维护的登记信息，
    # 由 WorkBuddy 在会话里创建/清理，我们既不该复制也不该补写——
    # 实测手写一个进去，几秒内就被平台删掉，白费劲。
    if os.path.isdir(dest) and not args.force:
        out(f'  {C_WARN}·{C_OFF} 专家目录已存在，只做增量覆盖（加 --force 全量重装）')

    # 1) 元数据
    meta_dest = os.path.join(dest, '.codebuddy-plugin')
    os.makedirs(meta_dest, exist_ok=True)
    shutil.copy2(src_meta, os.path.join(meta_dest, 'plugin.json'))
    out(f'  {C_OK}✓{C_OFF} plugin.json')

    # 2) 人设与头像（专家校验器还要求有 README，一起带上）
    for sub in ('agents', 'avatars'):
        s = os.path.join(EXPERT_SRC, sub)
        if os.path.isdir(s):
            d = os.path.join(dest, sub)
            os.makedirs(d, exist_ok=True)
            for fn in os.listdir(s):
                shutil.copy2(os.path.join(s, fn), os.path.join(d, fn))
            out(f'  {C_OK}✓{C_OFF} {sub}/  {C_DIM}{len(os.listdir(s))} 个文件{C_OFF}')

    readme = os.path.join(EXPERT_SRC, 'README.md')
    if os.path.isfile(readme):
        shutil.copy2(readme, os.path.join(dest, 'README.md'))
        out(f'  {C_OK}✓{C_OFF} README.md')

    # 3) 技能：**只装 plugin.json 声明的那几个**。
    #    仓库按业务线分了 seven 个目录，全装会把还没做完的线也塞进专家。
    with open(src_meta, encoding='utf-8') as f:
        declared = json.load(f).get('skills', [])
    if not declared:
        die('plugin.json 没有声明任何 skills')

    pool = {name: src for name, src, _ in list_skill_dirs()}
    skills_dest = os.path.join(dest, 'skills')
    if args.force and os.path.isdir(skills_dest):
        shutil.rmtree(skills_dest)      # 不清场，改名过的技能会留成僵尸目录
    os.makedirs(skills_dest, exist_ok=True)

    n_skill, missing = 0, []
    for entry in declared:
        name = entry.rstrip('/').split('/')[-1]
        if args.only and name != args.only:
            continue
        src = pool.get(name)
        if not src:
            missing.append(name)
            continue
        d = os.path.join(skills_dest, name)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(src, d)
        n_skill += 1

    if missing:
        out(f'  {C_ERR}✗{C_OFF} plugin.json 声明了但仓库里找不到：{"、".join(missing)}')
        die('检查 expert/plugin.json 的 skills 路径，或补建对应技能')

    out(f'  {C_OK}✓{C_OFF} skills/  {C_DIM}{n_skill} 个技能{C_OFF}')
    if args.only:
        out(f'  {C_WARN}⚠{C_OFF} 只装了 {args.only}，专家的人设会引用其余技能，'
            f'完整安装去掉 --only')

    # 4) 注册
    try:
        mf = register_in_marketplace(dest)
        out(f'  {C_OK}✓{C_OFF} 已注册到 {C_DIM}{mf}{C_OFF}')
    except Exception as e:
        out(f'  {C_WARN}⚠{C_OFF} 自动注册失败：{e}')
        out(f'{C_DIM}    可在 WorkBuddy 的「专家中心 → 我的专家」里手动加载{C_OFF}')

    # 5) 这一步没别的了：.created-by-session 归平台管，不去碰

    if not tail:
        return True, dest

    out()
    hr()
    out(f'{C_OK}装好了{C_OFF}')

    out()
    out(f'{C_BOLD}怎么用{C_OFF}')
    out('  打开 WorkBuddy → 左侧「专家」→ 我的专家 → 选「天信办公专家」')
    # 技能清单从 plugin.json 读，不写死——业务线会一直加
    names = [e.rstrip('/').split('/')[-1] for e in declared]
    out(f'  它自带 {len(names)} 个技能：{"、".join(names)}')
    out()
    out(f'{C_DIM}如果专家中心里没看到，重启 WorkBuddy 再进一次。{C_OFF}')
    out()
    return True, dest


def find_duplicate_skills(dest):
    """找出同一个 name 装在多个目录名下的情形。

    安装名取 SKILL.md 的 frontmatter name，但历史版本可能用中文目录名装过
    （天信日报 / tianxin-daily-brief）。改过名之后旧目录不会自动消失，
    结果是同一个技能两份，触发词重复，行为不可预期。
    """
    by_name = {}
    for entry in os.listdir(dest):
        d = os.path.join(dest, entry)
        md = os.path.join(d, 'SKILL.md')
        if os.path.isdir(d) and os.path.isfile(md):
            n = (read_frontmatter(md).get('name') or '').strip()
            if n:
                by_name.setdefault(n, []).append(entry)
    return {n: ds for n, ds in by_name.items() if len(ds) > 1}


def cmd_verify(args):
    dest, label = resolve_target(args, want_global=not args.project)
    out()
    out(f'{C_BOLD}验收{C_OFF}  {dest or "(未确定目录)"}')
    hr()

    ok = 0
    total = 0
    src_names = [n for n, _, _ in list_skill_dirs()]
    for name in src_names:
        if args.only and name != args.only:
            continue
        total += 1
        d = os.path.join(dest, name) if dest else None
        md = os.path.join(d, 'SKILL.md') if d else None

        if not d or not os.path.isdir(d):
            out(f'  {C_ERR}✗{C_OFF} {name}  {C_DIM}目录不存在{C_OFF}')
            continue
        if not os.path.isfile(md):
            out(f'  {C_ERR}✗{C_OFF} {name}  {C_DIM}缺 SKILL.md{C_OFF}')
            continue
        fm = read_frontmatter(md)
        if not fm.get('name'):
            out(f'  {C_ERR}✗{C_OFF} {name}  {C_DIM}frontmatter 缺 name{C_OFF}')
            continue
        if not fm.get('description'):
            out(f'  {C_WARN}⚠{C_OFF} {name}  {C_DIM}缺 description —— 装上了但不会被自动触发{C_OFF}')
            ok += 1
            continue

        notes = []
        nref = os.path.join(d, 'references')
        if os.path.isdir(nref):
            notes.append(f'{len(os.listdir(nref))} 份 references')
        nscripts = os.path.join(d, 'scripts')
        if os.path.isdir(nscripts):
            notes.append(f'{len([x for x in os.listdir(nscripts) if x.endswith((".py", ".js"))])} 个脚本')
        ncards = os.path.join(d, 'cards')
        if os.path.isdir(ncards):
            notes.append(f'{len(os.listdir(ncards))} 张能力卡')
        extra = (' · ' + ' · '.join(notes)) if notes else ''
        out(f'  {C_OK}✓{C_OFF} {name}  {C_DIM}{fm["name"]}{extra}{C_OFF}')
        ok += 1

    # 同名技能装了两份：历史改名留下的僵尸目录
    dup = find_duplicate_skills(dest) if dest and os.path.isdir(dest) else {}
    if dup:
        out()
        for n, dirs in dup.items():
            out(f'  {C_WARN}⚠{C_OFF} 技能 {n} 装了 {len(dirs)} 份：{C_DIM}{"、".join(dirs)}{C_OFF}')
        out(f'  {C_DIM}  同一技能两份会让触发词重复。保留与 name 同名的那个，其余移走。{C_OFF}')

    # 顺手看一眼专家包（装没装都报一声）。
    # 查项目目录时跳过：专家是全局装的，跟某个项目目录无关，
    # 在这里报只会让人以为「这个项目里也装了个专家」。
    out()
    exp_dir = os.path.join(expert_plugins_dir(), EXPERT_NAME)
    if args.project:
        out(f'{C_DIM}· 专家包是全局装的，与项目目录无关，此处不检查{C_OFF}')
    elif os.path.isdir(exp_dir):
        pj = os.path.join(exp_dir, '.codebuddy-plugin', 'plugin.json')
        nsk = 0
        sd = os.path.join(exp_dir, 'skills')
        if os.path.isdir(sd):
            nsk = len([d for d in os.listdir(sd) if os.path.isdir(os.path.join(sd, d))])
        out(f'  {C_OK}✓{C_OFF} 专家包 天信办公专家  '
            f'{C_DIM}{nsk} 个技能 · {"元数据就位" if os.path.isfile(pj) else "缺 plugin.json"}{C_OFF}')
    elif not args.project:
        out(f'  {C_DIM}· 未安装 WorkBuddy 专家（需要的话跑 --expert）{C_OFF}')

    out()
    hr()
    if ok == total:
        out(f'{C_OK}全部就位{C_OFF}  {ok}/{total}')
        out()
        out(f'{C_BOLD}但文件在 ≠ 能用。{C_OFF}做一次真实触发：')
        out('  新开一个会话，说「用天信文档规范，把这篇 Markdown 出一份 Word」')
        out('  没反应，多半是 SKILL.md 里 description 的触发词没覆盖到用户的原话。')
        out()
        return 0
    out(f'{C_ERR}{total - ok} 个没装好{C_OFF}  {ok}/{total}')
    out(f'{C_DIM}重跑安装：python install.py --global --force{C_OFF}')
    out()
    return 1


# ── 默认装法（不带参数） ──────────────────────────────────

DAILY_PROMPT = ('抓取今天的天信每日行业与商机日报：审计行业热点，以及台州天台及浙江范围内的'
                '财务咨询、代理记账、审计选聘、会计服务采购商机，按 tianxin-daily-brief 技能的'
                '信源清单与筛选逻辑出日报正文和 HTML 看板。')


def detect_workbuddy():
    """本机是不是 WorkBuddy：先看技能目录探测到谁，再看配置目录在不在"""
    base, label = detect_user_skills_dir()
    if label == 'WorkBuddy':
        return True
    cfg = os.environ.get('WORKBUDDY_CONFIG_DIR') or os.path.expanduser('~/.workbuddy')
    return os.path.isdir(cfg)


def daily_brief_tip(args, wb=True):
    """装完提醒一句：日报要不要每天自动跑。不替用户建，建不建由人定。"""
    if args.no_daily:
        return
    out()
    hr()
    out(f'{C_BOLD}还剩一件：日报要不要每天自己跑{C_OFF}')
    out('  「天信日报」技能不会自己醒——它需要一个定时任务，到点把这句话送进去：')
    out(f'  {C_DIM}{DAILY_PROMPT}{C_OFF}')
    out()
    if wb:
        out(f'  建法：在这个会话里说一句「每天早上 8:00 生成天信日报」即可；')
        out(f'        也可以左侧「自动化」→ 新建 → 每天 08:00 → 粘贴上面这句。')
    else:
        out(f'  当前环境不是 WorkBuddy，没有内置定时任务：用系统的定时执行（cron / 任务计划）')
        out(f'  每天 08:00 把上面这句交给你的 agent，或者到点自己说一句「出今天的日报」。')
    out(f'  {C_DIM}不建也能用：想看的当天说一句「出今天的日报」，跑得一模一样。{C_OFF}')

    if args.yes or not (sys.stdin and sys.stdin.isatty()):
        out()
        out(f'{C_DIM}（无人值守模式，不询问。要建就照上面的建法操作。）{C_OFF}')
        return
    out()
    try:
        ans = input('  现在就想试？(y/N) ').strip().lower()
    except (EOFError, KeyboardInterrupt):
        out()
        return
    if ans in ('y', 'yes', '是', '要', '好'):
        out()
        out(f'  {C_OK}好{C_OFF} 复制这一句给 WorkBuddy，它会自己把定时任务建起来：')
        out(f'  {C_BOLD}每天早上 8:00 生成天信日报{C_OFF}')
        out(f'  {C_DIM}建完在「自动化」里能看到，第一次跑完记得核一眼信源抓没抓全。{C_OFF}')
        out()
    else:
        out(f'  {C_DIM}好，先不建。随时可以说「每天早上 8:00 生成天信日报」。{C_OFF}')
        out()


def cmd_default(args):
    """不带参数时的动作：全部技能装全局 → WorkBuddy 下加装专家 → 提示日报定时任务"""
    wb = detect_workbuddy()
    base, label = detect_user_skills_dir()

    out()
    out(f'{C_BOLD}默认装法{C_OFF}')
    if wb:
        out(f'  {C_DIM}① 全部技能 → 本机全局   ② 再装成「天信办公专家」   ③ 问一句日报定时任务{C_OFF}')
    else:
        out(f'  {C_DIM}① 全部技能 → 本机全局（{label or "未探测到平台"}）'
            f'   ② 这里不是 WorkBuddy，跳过专家{C_OFF}')

    n_inst, n_up, n_od, dest = cmd_install(args, global_scope=True, tail=False)

    expert_dir = None
    if wb and not args.no_expert:
        out()
        _, expert_dir = cmd_expert(args, tail=False)

    out()
    hr()
    out(f'{C_OK}装完了{C_OFF}')
    tail_txt = f'{n_inst} 个新装 · {n_up} 个已是最新'
    if n_od:
        tail_txt += f' · {n_od} 个待更新'
    out(f'  {C_BOLD}技能{C_OFF}  {tail_txt}  {C_DIM}→ {os.path.normpath(dest)}{C_OFF}')
    if n_od:
        out(f'  {C_WARN}仓库里有 {n_od} 个技能内容变了，本次按「不覆盖本地改动」跳过；'
            f'要升级跑 python install.py --force{C_OFF}')
    if expert_dir:
        out(f'  {C_BOLD}专家{C_OFF}  天信办公专家  {C_DIM}→ {expert_dir}{C_OFF}')
    elif wb:
        out(f'  {C_BOLD}专家{C_OFF}  {C_DIM}本次跳过（--no-expert）{C_OFF}')
    else:
        out(f'  {C_BOLD}专家{C_OFF}  {C_DIM}未装：没检测到 WorkBuddy，专家只在 WorkBuddy 里有意义{C_OFF}')

    out()
    out(f'{C_BOLD}下一步{C_OFF}')
    out('  1. 新开一个会话，技能才会被加载')
    out('  2. 说一句试试：「用天信文档规范，把这篇 Markdown 出一份 Word」')
    if expert_dir:
        out('  3. 左侧「专家」→ 我的专家 → 选「天信办公专家」，六条业务线的作业都在里面')
    out(f'{C_DIM}  验收：python install.py --verify{C_OFF}')
    out()

    daily_brief_tip(args, wb=wb)


# ── 入口 ──────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='天信办公专家安装器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='不写模式就是默认装法：全部技能装全局 → WorkBuddy 环境再加装专家 → 提示日报定时任务。\n'
               '例子：\n'
               '  python install.py                      默认：全局技能 + 专家 + 日报提示\n'
               '  python install.py --global             只装技能，不碰专家\n'
               '  python install.py --expert             只装成 WorkBuddy 专家\n'
               '  python install.py --project D:/客户/某某尽调项目\n'
               '  python install.py --list               先看有什么\n'
               '  python install.py --verify             验收',
    )
    g = ap.add_mutually_exclusive_group(required=False)
    g.add_argument('--list', action='store_true', help='看仓库里有什么、装到哪')
    g.add_argument('--global', dest='global_scope', action='store_true',
                   help='只装到本机全局（不装专家）。什么都不写时走默认装法')
    g.add_argument('--project', metavar='DIR', help='装到某个项目目录')
    g.add_argument('--expert', action='store_true',
                   help='只装成 WorkBuddy 专家：一个专家挂 plugin.json 声明的全部技能')
    # --verify 单独放：它要能配合 --project / --target 用
    ap.add_argument('--verify', action='store_true',
                    help='检查装好了没有（可配 --project 指定目录）')

    ap.add_argument('--target', help='指定平台或目录（workbuddy / claude-code / 自定义路径）')
    ap.add_argument('--only', help='只处理某一个技能（写 frontmatter 里的 name）')
    ap.add_argument('--force', action='store_true', help='覆盖已存在的同名技能')
    ap.add_argument('--no-expert', dest='no_expert', action='store_true',
                    help='默认装法里跳过专家安装（只想装技能时用）')
    ap.add_argument('--no-daily', dest='no_daily', action='store_true',
                    help='默认装法里不再提示日报定时任务')
    ap.add_argument('--yes', action='store_true',
                    help='无人值守：不询问，直接按默认走（脚本 / CI 里用）')

    args = ap.parse_args()

    # Windows 控制台默认 GBK，中文技能名会乱码
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # 没给任何模式 = 默认装法：技能装全局 + WorkBuddy 下加装专家 + 日报提示。
    # 早先这里是「只装全局」。实测下来九成人要的就是「全都装上」，还要第三样
    # （日报定时任务）却根本不知道有——所以默认一路装到底，再问一句日报。
    # 想只装技能的人用 --global，想只装专家的人用 --expert，都还在。
    if not any([args.list, args.global_scope, args.project, args.expert, args.verify]):
        cmd_default(args)
    elif args.verify:
        sys.exit(cmd_verify(args))
    elif args.list:
        cmd_list()
    elif args.global_scope:
        cmd_install(args, global_scope=True)
    elif args.project:
        if not os.path.isdir(expand(args.project)):
            die(f'目录不存在：{expand(args.project)}')
        cmd_install(args, global_scope=False)
    elif args.expert:
        cmd_expert(args)


if __name__ == '__main__':
    main()
