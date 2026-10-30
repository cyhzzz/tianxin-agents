#!/usr/bin/env python3
"""
天信 Agents 仓库自检。

每次改完目录结构、加完技能、改完文档，跑一遍：

    python check.py            # 全量检查
    python check.py --quiet    # 只报错误

查九项。都是「人眼扫一遍必漏、而且不报错」的错：

  1–2. 链接与路径引用断没断
       Markdown 链接，以及正文用反引号写的路径（如 `references/01-xxx.md`）。
       后者比链接更隐蔽——它不是链接，渲染出来就是一行字，点不了也测不出。

       判据是「git ls-files 里有没有」，不是「磁盘上有没有」。
       区别很要紧：本仓库工作区里有一堆被 gitignore 的文件（含密钥的
       push-secrets.json、官网源码、宣传片），扫磁盘的话这些引用在本地
       全都"解析得到"，在别人 clone 出来的仓库里全是断链。

  3.   专家包 plugin.json 声明的技能仓库里有没有、有没有重复声明、
       tags/quickPrompts 各 3 个、描述 40–50 字、人设 frontmatter 是否同步
  4–5. 每个 SKILL.md 的 name / description 全不全；安装名会不会撞车
  6.   .gitignore 有没有行尾注释（不支持，会让整条规则静默失效）
  7.   文档里硬编码的技能数量、有没有分层重构前的失效命令
  8.   每个 SKILL.md 末尾有没有「反馈与改进」节（PR 回传机制的触发器）
  9.   待处理改进/ 里的提案有没有放成死目录（超过 30 天提醒）

不依赖任何第三方库。Python 3.8+。
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# 递归扫描时整棵跳过的目录（按目录名匹配）
SKIP_DIRS = {
    '.git', '.workbuddy', 'node_modules', '__pycache__',
    '天信宣传片', 'tianxin-cpa-website-gh-pages', '培训',
}

# 按「相对根目录的完整路径」额外跳过。根目录的 天信文档skill/ 是移动时被
# 文件锁卡住留下的旧壳（已 gitignore），但 公用/天信文档skill/ 是正式目录——
# 只按目录名跳过会把后者一起误伤。
SKIP_PATHS = {'天信文档skill'}

# 文档里 extension → 视为「路径引用」的反引号内容
PATH_EXT = ('.md', '.py', '.json', '.js', '.sh', '.png', '.jpg', '.jpeg', '.css', '.yaml', '.yml')

# 装在 ~/.workbuddy/skills 下的产物，不该被仓库追踪
PRODUCED_EXT = {'.docx', '.pdf', '.xlsx'}

C_ERR, C_WARN, C_OK, C_DIM, C_BOLD, C_OFF = (
    ('\033[31m', '\033[33m', '\033[32m', '\033[2m', '\033[1m', '\033[0m')
    if sys.stdout.isatty() else ('', '', '', '', '', ''))


class Rep:
    def __init__(self, quiet=False):
        self.errors, self.warns, self.quiet = [], [], quiet

    def err(self, msg):
        self.errors.append(msg)
        print(f'  {C_ERR}✗{C_OFF} {msg}')

    def warn(self, msg):
        self.warns.append(msg)
        if not self.quiet:
            print(f'  {C_WARN}⚠{C_OFF} {msg}')

    def ok(self, msg):
        if not self.quiet:
            print(f'  {C_OK}✓{C_OFF} {msg}')

    def info(self, msg):
        if not self.quiet:
            print(f'    {C_DIM}{msg}{C_OFF}')


def hr(title=''):
    print(f'\n{C_BOLD}{title}{C_OFF}' if title else '')


# ── 基础遍历 ─────────────────────────────────────────────

def walk_files(root=HERE, exts=None):
    """返回 [(绝对路径, 相对路径)]"""
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith('.')]
        dns[:] = [d for d in dns
                  if os.path.relpath(os.path.join(dp, d), root)
                  .replace(os.sep, '/') not in SKIP_PATHS]
        for fn in fns:
            if exts and not fn.endswith(exts):
                continue
            abs_p = os.path.join(dp, fn)
            out.append((abs_p, os.path.relpath(abs_p, root).replace(os.sep, '/')))
    return sorted(out, key=lambda x: x[1])


def find_skills():
    """[(安装名, 相对目录)]，安装名取 SKILL.md frontmatter 的 name"""
    items = []
    for dp, dns, fns in os.walk(HERE):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith('.')]
        dns[:] = [d for d in dns
                  if os.path.relpath(os.path.join(dp, d), HERE)
                  .replace(os.sep, '/') not in SKIP_PATHS]
        if 'SKILL.md' not in fns:
            continue
        fm = read_frontmatter(os.path.join(dp, 'SKILL.md'))
        name = (fm.get('name') or '').strip() or os.path.basename(dp)
        items.append((name, os.path.relpath(dp, HERE).replace(os.sep, '/')))
        dns[:] = []
    return sorted(items, key=lambda x: x[1])


def read_frontmatter(path):
    """读 --- 包裹的 YAML frontmatter。只支持 key: value，够用即可。"""
    try:
        with open(path, encoding='utf-8') as f:
            head = f.read(4000)
    except OSError:
        return {}
    m = re.match(r'^---\s*\n(.*?)\n---\s*(\n|$)', head, re.S)
    if not m:
        return {}
    fm, key, buf = {}, None, []
    for line in m.group(1).split('\n'):
        if re.match(r'^[A-Za-z_][\w-]*\s*:', line):
            if key:
                fm[key] = ' '.join(buf).strip()
            key = line.split(':', 1)[0].strip()
            val = line.split(':', 1)[1].strip()
            # YAML 块标量指示符（> | >- |-）不是内容，后续缩进行才是
            buf = [] if val in ('>', '|', '>-', '|-', '>+', '|+') else [val]
        elif key and (line.startswith((' ', '\t')) or not line.strip()):
            buf.append(line.strip())
    if key:
        fm[key] = ' '.join(buf).strip()
    return fm


# ── 1 & 2. 链接与路径引用 ─────────────────────────────────

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
TICK_RE = re.compile(r'`([^`\n]+)`')

# 通用文件名：写在根文档和 docs/ 里时指的是「每个技能都有这么个文件」这个概念，
# 不是指某个具体文件。这类不算断链。
GENERIC = {'SKILL.md', 'plugin.json', 'install.py', 'check.py', 'contribute.py',
           'README.md', 'AGENTS.md', 'START-HERE.md', 'CONTRIBUTING.md', 'LICENSE'}
CONCEPT_FILES = {'README.md', 'START-HERE.md', 'AGENTS.md', 'docs'}
_ALL_FILES = None


def all_files_cache():
    """仓库里**会被别人 clone 到**的文件的相对路径。

    用 `git ls-files` 而不是扫磁盘。这个区别要紧：本机的仓库工作区里有
    一堆被 .gitignore 排除的文件（宣传片、官网源码、push-secrets.json），
    扫磁盘的话，指向它们的引用在本地"解析得到"，在别人 clone 出来的
    仓库里却不存在——自检会在我这台机器上全过，在别人那边报断链。
    检查标准必须是"仓库里有什么"，不是"我磁盘上有什么"。
    """
    global _ALL_FILES
    if _ALL_FILES is not None:
        return _ALL_FILES
    out = set()
    r = subprocess.run(['git', 'ls-files', '-z'], cwd=HERE,
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0 and r.stdout.strip():
        out = {x for x in r.stdout.split('\0') if x}
    else:
        for dp, dns, fns in os.walk(HERE):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith('.')]
            dns[:] = [d for d in dns
                      if os.path.relpath(os.path.join(dp, d), HERE)
                      .replace(os.sep, '/') not in SKIP_PATHS]
            for fn in fns:
                out.add(os.path.relpath(os.path.join(dp, fn), HERE).replace(os.sep, '/'))
    _ALL_FILES = out
    return _ALL_FILES


def resolve(target, src_rel):
    """把 target 解析成仓库内的相对路径；解析不了返回 None。

    文档散在各层（根、docs/、references/、assets/），写引用时参照系不统一，
    所以要按多个基准试：相对自己 → 相对自己目录的上一层 → 相对仓库根。
    有人喜欢从仓库根写全路径，有人喜欢只写文件名，两种都得认。

    最后兜一层「后缀匹配」：跨业务线的引用（审计的 SKILL.md 引
    `cards/audit-core.md`）只写了片段路径，靠逐层基准算不出来，
    但它在仓库里是唯一的，应该认。
    """
    if not target:
        return None
    # 仓库外的路径与 URL 不归这里管。返回 '' 表示「跳过」，None 才是「断链」。
    if target.startswith(('http://', 'https://', 'mailto:', '#', '<')):
        return ''
    if target.startswith(('~/', '/', '../')):
        return ''
    # 通配符与模板占位符（<项目>、{日期}）无法静态校验
    if '*' in target or '{' in target or '<' in target or '>' in target:
        return ''
    target = target.split('#')[0].lstrip('./')
    if not target:
        return ''

    bases = [os.path.dirname(src_rel)]
    if os.path.dirname(src_rel):
        bases.append(os.path.dirname(os.path.dirname(src_rel)))
    bases.append('')
    # 判据必须与 all_files_cache 一致：只认仓库里的文件，不认磁盘上的。
    # 混用两套标准会让含密钥的本地配置（push-secrets.json 这种）在我这儿
    # "解析得到"、在别人 clone 出来的仓库里却是断链——自检本地全过，别人报错。
    cache = all_files_cache()
    for b in bases:
        cand = os.path.normpath(os.path.join(b, target)).replace(os.sep, '/')
        if cand in cache:
            return cand
        # 指向目录的链接（[docs/](docs/)）是合法的——git 只记录文件，
        # 所以这里认「目录下有被跟踪的文件」而不是「目录在缓存里」
        d = os.path.join(HERE, cand)
        if os.path.isdir(d) and any(
                os.path.relpath(os.path.join(dp, fn), HERE).replace(os.sep, '/') in cache
                for dp, dns, fns in os.walk(d) for fn in fns):
            return cand

    # 兜底：仓库内唯一后缀匹配（限含目录分隔符的片段路径）
    if '/' in target:
        hits = [r for r in all_files_cache() if r.endswith('/' + target)]
        if len(hits) == 1:
            return hits[0]
    return None


def is_conceptual(rel, tk):
    """这一处引用是不是「泛指」而非指向具体文件。

    规则：带目录的按路径查；裸的通用文件名（SKILL.md、plugin.json 这种）
    只有在本目录里真存在时才算引用，否则就是泛指——
    模板和文档里常写「见 SKILL.md 第 X 节」，那说的是任何一份 SKILL.md。
    """
    name = tk.split('/')[-1]
    if name not in GENERIC:
        return False
    if '/' in tk:
        return False
    return not os.path.exists(os.path.join(HERE, os.path.dirname(rel), name))


def check_references(rep):
    """查 Markdown 链接 + 反引号里的路径引用"""
    files = walk_files(exts=('.md',))
    n_links = n_ticks = 0
    broken = {}

    for abs_p, rel in files:
        text = open(abs_p, encoding='utf-8').read()

        # 1) Markdown 链接
        for label, target in LINK_RE.findall(text):
            if target.startswith(('http://', 'https://', 'mailto:')):
                continue
            # 教 Markdown 写法用的示例（(路径)、(url) 这类），没有扩展名也没有目录
            if '.' not in target and '/' not in target:
                continue
            n_links += 1
            r = resolve(target, rel)
            if r is None and not target.startswith('#'):
                broken.setdefault(rel, []).append(f'链接 [{label[:24]}]({target})')

        # 2) 反引号路径引用
        for tk in TICK_RE.findall(text):
            tk = tk.strip()
            if not tk.endswith(PATH_EXT):
                continue
            # 只认像路径的：含目录分隔符，或是通用文件名
            if '/' not in tk and tk not in GENERIC:
                continue
            # 根文档 / docs 里写的通用文件名是泛指，不是断链
            if is_conceptual(rel, tk):
                continue
            r = resolve(tk, rel)
            if r is None:
                broken.setdefault(rel, []).append(f'路径引用 `{tk}`')
            elif r:
                n_ticks += 1

    for rel in sorted(broken):
        rep.err(f'{rel}')
        for b in broken[rel]:
            rep.info(b)
    if not broken:
        rep.ok(f'链接与路径引用：{n_links} 个链接 + {n_ticks} 处路径引用，全部指向真实文件')


# ── 3. 专家包一致性 ───────────────────────────────────────

def check_expert(rep):
    pj_path = os.path.join(HERE, '专家', 'plugin.json')
    if not os.path.isfile(pj_path):
        rep.err('缺 专家/plugin.json')
        return
    pj = json.load(open(pj_path, encoding='utf-8'))
    declared = pj.get('skills', [])

    # 重复声明
    dup = {x for x in declared if declared.count(x) > 1}
    if dup:
        rep.err(f'plugin.json 里重复声明：{dup}。WorkBuddy 不报错，但会复制两遍')
    else:
        rep.ok(f'plugin.json 声明 {len(declared)} 个技能，无重复')

    # 声明的仓库里有没有
    pool = dict(find_skills())
    for e in declared:
        n = e.rstrip('/').split('/')[-1]
        if n not in pool:
            rep.err(f'plugin.json 声明了「{n}」，仓库里找不到')

    # 仓库里有但没声明（升级提示，非错误）
    missing = set(pool) - {e.rstrip('/').split('/')[-1] for e in declared}
    if missing:
        rep.warn(f'仓库里有但专家没挂：{sorted(missing)}（有意的话忽略）')

    # 元数据合规：校验器要求 tags / quickPrompts 各 3 个，描述 40–50 字
    if len(pj.get('tags', [])) != 3:
        rep.err(f"tags 必须恰好 3 个，当前 {len(pj.get('tags', []))}")
    if len(pj.get('quickPrompts', [])) != 3:
        rep.err(f"quickPrompts 必须恰好 3 个，当前 {len(pj.get('quickPrompts', []))}")
    zh = pj.get('displayDescription', {}).get('zh', '')
    if not (40 <= len(zh) <= 50):
        rep.err(f'displayDescription.zh 需 40–50 字，当前 {len(zh)} 字')

    # 人设 frontmatter 的 skills 与 plugin.json 是否一致
    ag_dir = os.path.join(HERE, '专家', 'agents')
    for fn in sorted(os.listdir(ag_dir)) if os.path.isdir(ag_dir) else []:
        fm = read_frontmatter(os.path.join(ag_dir, fn))
        declared_names = {e.rstrip('/').split('/')[-1] for e in declared}
        raw = (fm.get('skills') or '').strip().strip('[]')
        got = {x.strip() for x in re.split(r'[,，、]', raw) if x.strip()}
        if got and got != declared_names:
            rep.err(f'agents/{fn} 的 skills 与 plugin.json 不一致\n'
                    f'      人设: {sorted(got)}\n      声明: {sorted(declared_names)}')


# ── 4 & 5. 技能元数据 ────────────────────────────────────

def check_skills(rep):
    items = find_skills()
    if not items:
        rep.err('仓库里一个技能都没有')
        return

    for name, rel in items:
        md = os.path.join(HERE, rel, 'SKILL.md')
        fm = read_frontmatter(md)
        parts = []
        if not (fm.get('name') or '').strip():
            rep.err(f'{rel}：frontmatter 缺 name')
        if not (fm.get('description') or '').strip():
            rep.err(f'{rel}：frontmatter 缺 description（缺了不会被自动触发）')
        nref = len(os.listdir(os.path.join(HERE, rel, 'references'))) \
            if os.path.isdir(os.path.join(HERE, rel, 'references')) else 0
        nscr = len([x for x in os.listdir(os.path.join(HERE, rel, 'scripts'))
                    if x.endswith(('.py', '.js'))]) \
            if os.path.isdir(os.path.join(HERE, rel, 'scripts')) else 0
        if nref:
            parts.append(f'{nref} 份 references')
        if nscr:
            parts.append(f'{nscr} 个脚本')
        rep.ok(f'{name}  {C_DIM}{rel}' + ((' · ' + ' · '.join(parts)) if parts else '') + C_OFF)

    # 安装名撞车
    by_name = {}
    for name, rel in items:
        by_name.setdefault(name, []).append(rel)
    for name, rels in by_name.items():
        if len(rels) > 1:
            rep.err(f'安装名「{name}」被 {len(rels)} 个目录占用：{rels}。装到同一处会互相覆盖')

    # 源目录名重复（不同业务线用了同名目录）
    by_dir = {}
    for _, rel in items:
        b = rel.split('/')[-1]
        by_dir.setdefault(b, []).append(rel)
    for b, rels in by_dir.items():
        if len(rels) > 1:
            rep.warn(f'源目录名「{b}」重复：{rels}（安装名不同则无害）')

    return items


# ── 6. gitignore 有效性 ──────────────────────────────────

def check_gitignore(rep):
    gi = os.path.join(HERE, '.gitignore')
    if not os.path.isfile(gi):
        rep.err('缺 .gitignore')
        return

    # gitignore 不支持行尾注释：整行会被当成模式的一部分，规则静默失效
    bad = []
    for i, line in enumerate(open(gi, encoding='utf-8'), 1):
        s = line.rstrip('\n')
        if s.lstrip().startswith('#') or not s.strip():
            continue
        if '#' in s:
            bad.append((i, s.strip()))
    if bad:
        for i, s in bad:
            rep.err(f'.gitignore 第 {i} 行有行尾注释，该条规则从未生效：{s}')
    else:
        rep.ok('.gitignore 无行尾注释（行尾注释会让整条规则失效）')

    # 该忽略却仍存在的产物文件
    prod = [rel for _, rel in walk_files()
            if os.path.splitext(rel)[1] in PRODUCED_EXT
            and '/examples/' not in rel and '/assets/' not in rel]
    if prod:
        rep.warn(f'{len(prod)} 个产物文件在仓库工作区：{prod[:4]}'
                 f'{"…" if len(prod) > 4 else ""}（应确认已 gitignore）')


# ── 7. 文档与实际的一致性 ─────────────────────────────────

def check_docs(rep, skills):
    n_skill = len(skills)
    names = {n for n, _ in skills}

    # 硬编码的技能数量
    stale = []
    for abs_p, rel in walk_files(exts=('.md',)):
        if rel.startswith('天信文档skill/'):
            continue
        text = open(abs_p, encoding='utf-8').read()
        for m in re.finditer(r'共\s*([一二三四五六七八九十])个技能', text):
            cn = m.group(1)
            want = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}[cn]
            if want != n_skill:
                line = text[:m.start()].count('\n') + 1
                stale.append(f'{rel}:{line} 写「{cn}个技能」，实际 {n_skill} 个')
    if stale:
        for s in stale:
            rep.err(s)
    else:
        rep.ok(f'文档里的技能数量与实际一致（{n_skill} 个）')

    # 失效的分层前命令
    dead = []
    for abs_p, rel in walk_files(exts=('.md',)):
        if rel.startswith('天信文档skill/'):
            continue
        text = open(abs_p, encoding='utf-8').read()
        for pat, why in [
            (r'cp\s+-r\s+skills/\*', '仓库已无 skills/ 目录（技能按业务线分层）'),
            (r'cp\s+expert/', '专家源目录已改名 专家/'),
        ]:
            for m in re.finditer(pat, text):
                line = text[:m.start()].count('\n') + 1
                dead.append(f'{rel}:{line} 失效命令「{m.group(0)}」——{why}')
    if dead:
        for d in dead:
            rep.err(d)
    else:
        rep.ok('无分层重构前的失效命令（cp -r skills/* 、cp expert/）')

    # 业务线 README 是否存在
    for line in ['审计', '税务', '代理记账', '企业咨询', '评估造价']:
        d = os.path.join(HERE, line)
        if not os.path.isdir(d):
            rep.err(f'缺业务线目录 {line}/')
        elif not os.path.isfile(os.path.join(d, 'README.md')):
            rep.warn(f'{line}/ 缺 README.md（待建说明）')


# ── 8. 反馈触发器 ───────────────────────────────────────

def check_feedback_block(rep, skills):
    """每个 SKILL.md 末尾都得有「反馈与改进」那一节。

    那是 PR 回传机制的触发器：装出去的是副本，AI 读不到仓库里的
    CONTRIBUTING.md，只有跟着副本走的 SKILL.md 才看得见。
    新建技能忘了加这一节，机制就断了——而且没有任何报错。
    """
    missing = []
    for name, rel in skills:
        txt = open(os.path.join(HERE, rel, 'SKILL.md'), encoding='utf-8').read()
        if '## 反馈与改进' not in txt:
            missing.append(rel)
        elif 'cyhzzz/tianxin-agents' not in txt:
            missing.append(rel + '（缺仓库地址）')
    if missing:
        for m in missing:
            rep.err(f'{m} 末尾缺「反馈与改进」节，改进回传机制在这里是断的')
    else:
        rep.ok(f'{len(skills)} 个技能都带改进回传触发器')


# ── 9. 待处理提案 ───────────────────────────────────────

def check_inbox(rep):
    """待处理提案有没有放成死目录。

    提案是以 PR 形式进来的，所以不会悄悄堆积——PR 有通知。
    真正的风险是**PR 合并了、提案文件却留在目录里没删**，
    以及提案多了以后看不出哪些是新的。
    """
    d = os.path.join(HERE, '待处理改进')
    files = []
    if os.path.isdir(d):
        files = sorted(f for f in os.listdir(d) if f != 'README.md')
    if not files:
        rep.ok('待处理改进/ 是空的（没有未消化的提案）')
        return

    from datetime import datetime as _dt
    stale = []
    for f in files:
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', f)
        if not m:
            continue
        try:
            age = (_dt.now().date() - _dt(*(int(x) for x in m.groups())).date()).days
        except ValueError:
            continue
        if age >= 30:
            stale.append((age, f))

    if stale:
        for age, f in sorted(stale, reverse=True):
            rep.warn(f'提案搁了 {age} 天：待处理改进/{f}')
        rep.warn(f'{len(stale)} 份提案超过 30 天没处理。放着不管这个目录就死了——'
                 f'提的人看不到回音，后来的人更不想提。'
                 f'采纳就改到技能里并删掉文件，不采纳就删掉并在 PR 里说明理由。')
    else:
        rep.ok(f'待处理改进/ 有 {len(files)} 份提案，都没超期')


# ── main ────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='天信 Agents 仓库自检')
    ap.add_argument('--quiet', action='store_true', help='只报错误')
    a = ap.parse_args()
    rep = Rep(a.quiet)

    print(f'{C_BOLD}天信 Agents 仓库自检{C_OFF}  {HERE}')

    hr('1–2. 链接与路径引用')
    check_references(rep)

    hr('3. 专家包一致性')
    check_expert(rep)

    hr('4–5. 技能元数据')
    skills = check_skills(rep)

    hr('6. .gitignore 有效性')
    check_gitignore(rep)

    hr('7. 文档与实际一致性')
    check_docs(rep, skills or [])

    hr('8. 改进回传触发器')
    check_feedback_block(rep, skills or [])

    hr('9. 待处理提案')
    check_inbox(rep)

    hr()
    if rep.errors:
        print(f'{C_ERR}{len(rep.errors)} 个错误{C_OFF}'
              + (f'，{len(rep.warns)} 个提醒' if rep.warns else ''))
        return 1
    print(f'{C_OK}全部通过{C_OFF}'
          + (f'，{len(rep.warns)} 个提醒' if rep.warns else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
