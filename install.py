#!/usr/bin/env python3
"""
天信办公专家 · 安装器

四种用法，一次只用一个：

    python install.py --list                     看仓库里有什么
    python install.py --global                   装到本机所有对话可用
    python install.py --project /path/to/dir     装到某个项目目录
    python install.py --expert                   装成 WorkBuddy 专家（一个专家挂四个技能）
    python install.py --verify                   检查装好了没有

可选：
    --target workbuddy|claude-code|<路径>   指定目标平台（默认自动探测）
    --force                                 覆盖已存在的同名技能 / 专家
    --only 天信日报                         只装某一个

不依赖任何第三方库。Python 3.8+。
"""

import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXPERT_SRC = os.path.join(HERE, 'expert')
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


# 仓库根下这些目录不是技能，扫描时跳过
NON_SKILL_DIRS = {
    'docs', 'expert', '培训', '天信宣传片',
    'tianxin-cpa-website-gh-pages', '.git', '.workbuddy',
}


def list_skill_dirs():
    """扫描仓库根下带 SKILL.md 的目录。

    返回 [(安装名, 绝对路径, 源目录名)]。
    安装名取 SKILL.md 的 name —— 源目录叫「天信文档skill」，装出来的必须是
    「天信文档与报告」，否则技能名跟 frontmatter 对不上，触发会出问题。
    """
    items = []
    for name in sorted(os.listdir(HERE)):
        if name in NON_SKILL_DIRS or name.startswith(('.', '_')):
            continue
        p = os.path.join(HERE, name)
        md = os.path.join(p, 'SKILL.md')
        if not (os.path.isdir(p) and os.path.isfile(md)):
            continue
        fm = read_frontmatter(md)
        install_name = (fm.get('name') or '').strip() or name.removesuffix('skill')
        items.append((install_name, p, name))
    return items


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
            return full, label
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

def copy_skills(dest, force=False, only=None):
    """把 skills/* 复制到 dest。返回 (已装, 跳过, 覆盖)"""
    os.makedirs(dest, exist_ok=True)
    installed, skipped, replaced = [], [], []

    for name, src, _ in list_skill_dirs():
        if only and name != only:
            continue
        target = os.path.join(dest, name)
        existed = os.path.isdir(target)
        if existed and not force:
            skipped.append(name)
            continue
        if existed:
            shutil.rmtree(target)
            replaced.append(name)
        shutil.copytree(src, target)
        if not existed:
            installed.append(name)
    return installed, skipped, replaced


def write_manifest(dest, names):
    """在目标目录留一份来源说明，避免以后忘了这批技能从哪来"""
    lines = [
        '# 天信办公专家 · 技能清单',
        '',
        '本目录下的技能来自 https://github.com/cyhzzz/tianxin-skills',
        '**不要在这里直接改**——下次同步会覆盖。要改回仓库改，再重新安装。',
        '',
        '| 技能 | 作用 |',
        '|---|---|',
        '| 天信文档与报告 | Word / A4 PDF / 网页长页 / 演示 deck 四轨出版 |',
        '| 天信日报 | 每日行业热点与本地商机情报 |',
        '| 天信实务知识库 | 12 张会计审计实务判断卡 |',
        '| 陈版主实务问答 | 视野论坛实务答疑与准则原文检索 |',
        '',
        f'安装时间：{__import__("datetime").datetime.now():%Y-%m-%d %H:%M}',
        f'本次安装：{"、".join(names) if names else "（无新增）"}',
        '',
        '## 更新',
        '',
        '```bash',
        'cd tianxin-skills && git pull',
        'python install.py --global --force      # 或 --project <本目录>',
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


def cmd_install(args, global_scope):
    dest, label = resolve_target(args, want_global=global_scope)
    if not dest:
        die('没找到可装的目录。用 --target 指定，例如 --target ~/.workbuddy/skills')

    scope = '本机全局' if global_scope else f'项目级（{expand(args.project)}）'
    out()
    out(f'{C_BOLD}安装到{C_OFF}  {dest}')
    out(f'{C_DIM}范围：{scope} · 平台：{label}{C_OFF}')
    hr()

    installed, skipped, replaced = copy_skills(dest, force=args.force, only=args.only)

    for n in installed:
        out(f'  {C_OK}✓{C_OFF} 装入  {n}')
    for n in replaced:
        out(f'  {C_OK}✓{C_OFF} 覆盖  {n}')
    for n in skipped:
        out(f'  {C_WARN}·{C_OFF} 跳过  {n}  {C_DIM}（已存在，要覆盖加 --force）{C_OFF}')

    if not (installed or replaced):
        out()
        out(f'{C_WARN}没有任何技能被写入。{C_OFF}')
        if skipped:
            out(f'{C_DIM}四个技能都已存在。确认是旧版就重跑并加 --force。{C_OFF}')
        return

    write_manifest(dest, installed + replaced)

    out()
    hr()
    out(f'{C_OK}装好了{C_OFF}  {len(installed) + len(replaced)} 个技能')
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


def cmd_expert(args):
    src_meta = os.path.join(EXPERT_SRC, 'plugin.json')
    if not os.path.isfile(src_meta):
        die(f'找不到专家包：{EXPERT_SRC}')

    plugins_dir = expand(args.target) if args.target else expert_plugins_dir()
    dest = os.path.join(plugins_dir, EXPERT_NAME)

    out()
    out(f'{C_BOLD}装成 WorkBuddy 专家{C_OFF}')
    out(f'{C_DIM}一个专家「天信办公专家」，下面挂四个技能{C_OFF}')
    out(f'  目标：{dest}')
    hr()

    if os.path.isdir(dest) and not args.force:
        out(f'  {C_WARN}·{C_OFF} 专家目录已存在，只做增量覆盖（加 --force 全量重装）')

    # 1) 元数据
    meta_dest = os.path.join(dest, '.codebuddy-plugin')
    os.makedirs(meta_dest, exist_ok=True)
    shutil.copy2(src_meta, os.path.join(meta_dest, 'plugin.json'))
    out(f'  {C_OK}✓{C_OFF} plugin.json')

    # 2) 人设与头像
    for sub in ('agents', 'avatars'):
        s = os.path.join(EXPERT_SRC, sub)
        if os.path.isdir(s):
            d = os.path.join(dest, sub)
            os.makedirs(d, exist_ok=True)
            for fn in os.listdir(s):
                shutil.copy2(os.path.join(s, fn), os.path.join(d, fn))
            out(f'  {C_OK}✓{C_OFF} {sub}/  {C_DIM}{len(os.listdir(s))} 个文件{C_OFF}')

    # 3) 技能
    skills_dest = os.path.join(dest, 'skills')
    os.makedirs(skills_dest, exist_ok=True)
    n_skill = 0
    for name, s, _ in list_skill_dirs():
        if args.only and name != args.only:
            continue
        d = os.path.join(skills_dest, name)
        if os.path.isdir(d):
            shutil.rmtree(d)
        shutil.copytree(s, d)
        n_skill += 1
    out(f'  {C_OK}✓{C_OFF} skills/  {C_DIM}{n_skill} 个技能{C_OFF}')

    # 4) 注册
    try:
        mf = register_in_marketplace(dest)
        out(f'  {C_OK}✓{C_OFF} 已注册到 {C_DIM}{mf}{C_OFF}')
    except Exception as e:
        out(f'  {C_WARN}⚠{C_OFF} 自动注册失败：{e}')
        out(f'{C_DIM}    可在 WorkBuddy 的「专家中心 → 我的专家」里手动加载{C_OFF}')

    out()
    hr()
    out(f'{C_OK}装好了{C_OFF}')
    out()
    out(f'{C_BOLD}怎么用{C_OFF}')
    out('  打开 WorkBuddy → 左侧「专家」→ 我的专家 → 选「天信办公专家」')
    out('  它自带四个技能：文档与报告、实务知识库、陈版主问答、每日日报')
    out()
    out(f'{C_DIM}如果专家中心里没看到，重启 WorkBuddy 再进一次。{C_OFF}')
    out()


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

    # 顺手看一眼专家包（装没装都报一声）
    exp_dir = os.path.join(expert_plugins_dir(), EXPERT_NAME)
    out()
    if os.path.isdir(exp_dir):
        pj = os.path.join(exp_dir, '.codebuddy-plugin', 'plugin.json')
        nsk = 0
        sd = os.path.join(exp_dir, 'skills')
        if os.path.isdir(sd):
            nsk = len([d for d in os.listdir(sd) if os.path.isdir(os.path.join(sd, d))])
        out(f'  {C_OK}✓{C_OFF} 专家包 天信办公专家  '
            f'{C_DIM}{nsk} 个技能 · {"元数据就位" if os.path.isfile(pj) else "缺 plugin.json"}{C_OFF}')
    else:
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


# ── 入口 ──────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='天信办公专家安装器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='一次只用一个模式。例子：\n'
               '  python install.py --list\n'
               '  python install.py --global\n'
               '  python install.py --project D:/客户/正山堂\n'
               '  python install.py --expert\n'
               '  python install.py --verify',
    )
    g = ap.add_mutually_exclusive_group(required=False)
    g.add_argument('--list', action='store_true', help='看仓库里有什么、装到哪')
    g.add_argument('--global', dest='global_scope', action='store_true', help='装到本机全局')
    g.add_argument('--project', metavar='DIR', help='装到某个项目目录')
    g.add_argument('--expert', action='store_true',
                   help='装成 WorkBuddy 专家：一个专家挂四个技能')
    # --verify 单独放：它要能配合 --project / --target 用
    ap.add_argument('--verify', action='store_true',
                    help='检查装好了没有（可配 --project 指定目录）')

    ap.add_argument('--target', help='指定平台或目录（workbuddy / claude-code / 自定义路径）')
    ap.add_argument('--only', help='只处理某一个技能')
    ap.add_argument('--force', action='store_true', help='覆盖已存在的同名技能')

    args = ap.parse_args()

    # Windows 控制台默认 GBK，中文技能名会乱码
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    if not any([args.list, args.global_scope, args.project, args.expert, args.verify]):
        ap.error('至少给一个模式：--list / --global / --project / --expert / --verify')

    if args.verify:
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
