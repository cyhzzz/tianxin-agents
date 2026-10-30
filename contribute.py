#!/usr/bin/env python3
"""
天信 Agents · 改进回传工具

别人装了仓库里的技能，用着用着发现问题或改好了东西——这个脚本负责把它变成 PR。

三种用法：

    python contribute.py --check <提案文件>            只验证格式，不提交
    python contribute.py --proposal <提案文件>          把提案提交成 PR
    python contribute.py --from-installed <技能目录>    装好的技能副本改过了，把差异提交成 PR
    python contribute.py --list                        看仓库里待处理的提案

## 两种回传路径，区别很大

**--proposal**：你发现了问题，但没直接改文件。交的是一份「该改什么」的说明，
落到 `待处理改进/`，由合伙人核实后改。适合政策类、拿不准的判断类。

**--from-installed**：你已经把 `~/.workbuddy/skills/天信代账作业/` 里的文件直接改好了
（这是常见情况——AI 在会话里顺手就把技能文件改了）。这个模式把改过的文件
复制回仓库对应位置，产生的 PR 是**可以逐行 review 的真实改动**。

后者价值高得多。所以 SKILL.md 里引导 AI：**能改就直接改文件，然后用这个模式回传**；
改不了（政策拿不准、超出权限）才走 --proposal。

## 依赖

需要 `git`，开 PR 需要 `gh`（没有 gh 会提示手工推送的命令）。
不依赖任何第三方 Python 库。Python 3.8+。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = 'cyhzzz/tianxin-agents'
INBOX = '待处理改进'

C_ERR, C_WARN, C_OK, C_DIM, C_BOLD, C_OFF = (
    ('\033[31m', '\033[33m', '\033[32m', '\033[2m', '\033[1m', '\033[0m')
    if sys.stdout.isatty() else ('', '', '', '', '', ''))

# 提案必填字段。前两个是底线——只有说清「原来是什么」「应该是什么」才可执行。
REQUIRED = ['技能', '位置']
KEY_FIELDS = ['现在怎么写的', '应该是']
TYPES = ['内容有误', '政策过期', '缺能力', '表述不清', '其他']


def out(s=''):
    print(s)


def ask(prompt):
    """问一句。没有 stdin 时（管道、CI）按「否」处理，不要崩。"""
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        out()
        return 'n'


def die(msg, hint=None):
    out(f'\n{C_ERR}✗ {msg}{C_OFF}')
    if hint:
        out(f'{C_DIM}  {hint}{C_OFF}')
    sys.exit(1)


def run(cmd, capture=True, check=False):
    r = subprocess.run(cmd, shell=True, cwd=HERE,
                       capture_output=capture, text=True,
                       encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        die(f'命令失败：{cmd}', (r.stderr or r.stdout or '').strip()[:300])
    return r


def slug(text, fallback='proposal'):
    """分支名/文件名用的安全片段。中文会被过滤掉，所以兜底要给默认值。"""
    s = re.sub(r'[^\w-]+', '-', text.lower(), flags=re.UNICODE)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    # 保留中文（git 支持），只去掉分支名里真正危险的字符
    cn = re.sub(r'[^\w\u4e00-\u9fff-]+', '-', text)
    cn = re.sub(r'-{2,}', '-', cn).strip('-')
    return (cn or s or fallback)[:40]


# ── 前置检查 ─────────────────────────────────────────────

def preflight():
    if not os.path.isfile(os.path.join(HERE, 'install.py')):
        die('必须在仓库根目录运行（找得到 install.py 的那一层）')
    if run('git rev-parse --is-inside-work-tree').returncode != 0:
        die('当前目录不是 git 仓库')
    dirty = run('git status --porcelain').stdout.strip()
    if dirty:
        out(f'{C_WARN}⚠ 工作区有未提交的改动，它们会一起进入这个分支：{C_OFF}')
        for line in dirty.split('\n')[:5]:
            out(f'{C_DIM}    {line}{C_OFF}')
        if ask('    继续？(y/N) ') != 'y':
            die('已取消。先 git stash 或提交掉再跑')
    return run('git rev-parse --abbrev-ref HEAD').stdout.strip()


def ensure_gh():
    return shutil.which('gh') is not None and \
        run('gh auth status').returncode == 0


# ── 提案验证 ─────────────────────────────────────────────

def parse_proposal(path):
    """抽出提案里的关键字段。宽容解析：表格行、标题行、`**字段**：值` 都认。"""
    if not os.path.isfile(path):
        die(f'找不到提案文件：{path}')
    text = open(path, encoding='utf-8').read()
    fields = {}
    for m in re.finditer(r'^\s*\|?\s*\*{0,2}(技能|类型|位置|提交人|日期)\*{0,2}\s*\|?\s*[：:]?\s*\|?\s*(.*?)\s*\|?\s*$',
                         text, re.M):
        k, v = m.group(1), m.group(2).strip()
        if v and v not in ('（填 frontmatter 的 name，如 `天信代账作业`）',
                           '（可选）', '（`references/03-xxx.md` 第 N 行，或 `SKILL.md` 第 X 节）'):
            fields.setdefault(k, v)
    has_now = bool(re.search(r'现在怎么写的', text))
    has_should = bool(re.search(r'应该是', text))
    return fields, has_now, has_should, text


def check_proposal(path):
    fields, has_now, has_should, text = parse_proposal(path)
    problems = []
    for k in REQUIRED:
        if not fields.get(k):
            problems.append(f'缺「{k}」')
    if not has_now or not has_should:
        problems.append('缺「现在怎么写的 / 应该是」这两栏——提案的用处全在这里')

    typ = fields.get('类型', '')
    if typ and not any(t in typ for t in TYPES):
        problems.append(f'「类型」应填其中之一：{" / ".join(TYPES)}')

    # 政策类必须有文号
    if typ and '政策' in typ and not re.search(r'(财税|总局|税务总局|财政部|公告|令|法)\s*[〔\[（(]?\s*\d{4}', text):
        problems.append('政策类提案要给文号（财税〔xxxx〕xx 号 之类），否则无法核实')

    # 脱敏：公开仓库
    for pat, what in [(r'\d{15,}', '疑似身份证/税号'), (r'1[3-9]\d{9}', '疑似手机号')]:
        if re.search(pat, text):
            problems.append(f'{what}——这是公开仓库，提案里不要带客户信息')

    out(f'{C_BOLD}提案检查{C_OFF}  {os.path.basename(path)}')
    for k in ('技能', '类型', '位置', '提交人'):
        if fields.get(k):
            out(f'  {k}: {fields[k]}')
    out(f'  现在怎么写的: {"✓" if has_now else "✗"}   应该是: {"✓" if has_should else "✗"}')
    out()
    if problems:
        for p in problems:
            out(f'  {C_ERR}✗{C_OFF} {p}')
        return False
    out(f'  {C_OK}✓ 格式通过{C_OFF}')
    return True


# ── 提交 ─────────────────────────────────────────────────

def finish(branch, title, body_file=None, push=True):
    """提交、推送、开 PR"""
    run('git add -A')
    r = subprocess.run(['git', 'commit', '-q', '-m', title], cwd=HERE,
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        die('提交失败（可能没有实际改动）', (r.stderr or r.stdout or '')[:200])

    out(f'  {C_OK}✓{C_OFF} 已提交到分支 {branch}')

    if not push:
        return
    remotes = run('git remote').stdout.split()
    if not remotes:
        out(f'{C_WARN}⚠{C_OFF} 没有 remote，添加：git remote add origin git@github.com:{REPO}.git')
        return
    p = subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=HERE,
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode != 0:
        out(f'{C_ERR}✗{C_OFF} 推送失败')
        out(f'{C_DIM}{(p.stderr or p.stdout or "")[:400]}{C_OFF}')
        out(f'\n  手工推送：git push -u origin {branch}')
        return
    out(f'  {C_OK}✓{C_OFF} 已推送')

    if not ensure_gh():
        out(f'\n{C_DIM}没装 gh 或未登录。手工开 PR：{C_OFF}')
        out(f'  https://github.com/{REPO}/compare/{branch}?expand=1')
        return
    pr = subprocess.run(
        ['gh', 'pr', 'create', '--repo', REPO, '--base', 'master',
         '--head', branch, '--title', title, '--body', body_file and open(body_file, encoding='utf-8').read() or title],
        cwd=HERE, capture_output=True, text=True, encoding='utf-8')
    if pr.returncode == 0:
        out(f'  {C_OK}✓{C_OFF} PR 已创建：{pr.stdout.strip()}')
    else:
        out(f'{C_WARN}⚠{C_OFF} 开 PR 失败，去这里手工开：')
        out(f'  https://github.com/{REPO}/compare/{branch}?expand=1')


def cmd_proposal(args):
    if not check_proposal(args.proposal):
        if not args.force:
            die('提案格式不对。确认内容没问题就加 --force')
        out(f'{C_WARN}⚠ 已 --force，忽略格式问题{C_OFF}')

    fields, _, _, text = parse_proposal(args.proposal)
    skill = fields.get('技能', '未指名技能')
    typ = fields.get('类型', '其他')
    date = datetime.now().strftime('%Y-%m-%d')
    base = preflight()
    branch = f'improve/{date}-{slug(skill)}-{slug(typ)}'

    dest_rel = os.path.join(INBOX, f'{date}-{slug(skill)}-{slug(typ)}.md')
    dest = os.path.join(HERE, dest_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    text = text if text.lstrip().startswith('#') else f'# 改进提案：{skill} · {typ}\n\n' + text
    if 'date:' not in text:
        text += f'\n\n---\n\n- 提交日期：{date}\n- 来源：外部贡献\n'
    open(dest, 'w', encoding='utf-8').write(text)

    out(f'\n{C_BOLD}提交提案{C_OFF}')
    out(f'  写入 {dest_rel}')
    run(f'git checkout -q -B {branch}')
    finish(branch, f'改进提案：{skill} · {typ}（{date}）', body_file=dest)


def cmd_from_installed(args):
    """把装好的技能副本的改动复制回仓库"""
    src = os.path.abspath(args.from_installed)
    if not os.path.isdir(src):
        die(f'不是目录：{src}')

    sys.path.insert(0, HERE)
    from check import find_skills           # 复用仓库里的技能索引
    pool = {name: rel for name, rel in find_skills()}
    name = os.path.basename(src.rstrip(os.sep + '/'))
    if name not in pool:
        die(f'「{name}」不在仓库的技能清单里',
            f'这里要传**安装后的目录名**（SKILL.md 里 name 的值），不是源目录名。'
            f'仓库里有：{sorted(pool)}')

    repo_rel = pool[name]
    repo_dir = os.path.join(HERE, repo_rel)
    out(f'{C_BOLD}比对{C_OFF}')
    out(f'  装好的副本：{src}')
    out(f'  仓库位置：  {repo_rel}')

    changed = []
    for dp, dns, fns in os.walk(src):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__', 'node_modules')]
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, src).replace(os.sep, '/')
            tgt = os.path.join(repo_dir, rel)
            if not os.path.isfile(tgt):
                changed.append(('新增', rel))
                continue
            try:
                a = open(p, 'rb').read()
                b = open(tgt, 'rb').read()
            except OSError:
                continue
            if a != b:
                changed.append(('修改', rel))

    if not changed:
        out(f'\n{C_WARN}副本与仓库完全一致，没有可回传的改动{C_OFF}')
        return 0

    out(f'\n{C_BOLD}{len(changed)} 处改动{C_OFF}')
    for kind, rel in changed[:20]:
        out(f'  {kind}  {rel}')
    if len(changed) > 20:
        out(f'  … 还有 {len(changed) - 20} 处')

    # 副本里不能带运行产物
    junk = [r for _, r in changed
            if r.endswith(('.docx', '.pdf', '.xlsx', '.png', '.jpg')) or '/daily/' in r]
    if junk:
        out(f'\n{C_WARN}⚠ 这些是运行产物，不会回传：{C_OFF}')
        for r in junk[:6]:
            out(f'    {r}')
        changed = [c for c in changed if c[1] not in junk]
        if not changed:
            die('去掉产物后没有可回传的内容')

    if not args.yes:
        if ask('\n  把这些改动写回仓库并提交？(y/N) ') != 'y':
            die('已取消')

    base = preflight()
    branch = f'improve/{datetime.now():%Y-%m-%d}-{slug(name)}'
    run(f'git checkout -q -B {branch}')
    for _, rel in changed:
        shutil.copyfile(os.path.join(src, rel), os.path.join(repo_dir, rel))
    out(f'\n{C_BOLD}写回仓库{C_OFF}')
    finish(branch, f'改进：{name}（来自安装副本的 {len(changed)} 处改动）')


def cmd_list(args):
    d = os.path.join(HERE, INBOX)
    if not os.path.isdir(d):
        out(f'{C_DIM}暂无待处理提案{C_OFF}')
        return 0
    fs = sorted(f for f in os.listdir(d) if f != 'README.md')   # 目录说明不是提案
    if not fs:
        out(f'{C_DIM}暂无待处理提案{C_OFF}')
        return 0
    out(f'{C_BOLD}{INBOX}/ 共 {len(fs)} 份{C_OFF}')
    for f in fs:
        p = os.path.join(d, f)
        txt = open(p, encoding='utf-8').read()
        skill = (re.search(r'\|\s*技能\s*\|\s*(.+?)\s*\|', txt) or [None, '?'])[1]
        typ = (re.search(r'\|\s*类型\s*\|\s*(.+?)\s*\|', txt) or [None, '?'])[1]
        out(f'  {skill:<16} {typ:<10} {f}')
    return 0


def main():
    ap = argparse.ArgumentParser(
        description='天信 Agents 改进回传',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--proposal', metavar='FILE', help='把提案文件提交成 PR')
    g.add_argument('--from-installed', metavar='DIR', help='把装好的技能副本的改动提交成 PR')
    g.add_argument('--list', action='store_true', help='列出待处理提案')
    g.add_argument('--check', metavar='FILE', help='只检查提案格式，不提交')
    ap.add_argument('--force', action='store_true', help='忽略格式问题强行提交')
    ap.add_argument('--yes', '-y', action='store_true', help='不询问直接执行')
    a = ap.parse_args()

    if a.check:
        return 0 if check_proposal(a.check) else 1
    if a.list:
        return cmd_list(a)
    if a.proposal:
        cmd_proposal(a)
    elif a.from_installed:
        cmd_from_installed(a)
    return 0


if __name__ == '__main__':
    sys.exit(main())
