#!/usr/bin/env python3
"""
公文与文档字体探测 —— 查明「规范要求用哪个、本机实际有哪个、最后会落到哪个」

为什么要有这个脚本：
  公文字体是个三层问题，混在一起就说不清。
    ① 规范层：GB/T 9704 要求标题小标宋、正文仿宋、二级标题楷体；
    ② 字库层：规范名常写成「仿宋_GB2312」，但那是 Win7 前的旧字库名，
       Win7+ 只有「仿宋」（simfang.ttf）。写了旧名 Word 会**静默**回退成宋体；
    ③ 分发层：方正小标宋是商业字体，GB2312 字库版权归中易，都不能随仓库分发。
  所以仓库里不放字体文件，只放「怎么找、找到用什么、找不到退到哪」。

三种字体来源，按优先级：
  1. assets/fonts/          使用者自己合法取得的字体（放进来就自动用，不入库）
  2. 系统字体目录            C:/Windows/Fonts 与用户字体目录
  3. CSS / Word 的降级链     最后兜底，通常是宋体

用法：
  python scripts/check_fonts.py            # 打印对照表
  python scripts/check_fonts.py --json     # 供其它脚本调用
  python scripts/check_fonts.py --copy-hint  # 缺字体时打印放置说明
"""

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')
FONT_DIR = os.path.join(ASSETS, 'fonts')

# 公文与文档需要的字体，按「规范名 → 常见别名 → 保底」排。
# prefer 里第一个是国标/行业文档里写的名字，实际能不能用要靠探测。
SPEC = [
    {
        'role': '标题（小标宋）',
        'prefer': ['方正小标宋简体', 'FZXiaoBiaoSong-B05S', 'FZXBSJW--GB1-0'],
        'fallback': ['华文中宋', 'STZhongsong', '宋体', 'SimSun'],
        'note': '国标指定小标宋体。商业字体，本机通常没有；缺则退华文中宋→宋体。',
    },
    {
        'role': '正文（仿宋）',
        'prefer': ['仿宋_GB2312', 'FangSong_GB2312'],
        'fallback': ['仿宋', 'FangSong', '华文仿宋', 'STFangsong'],
        'note': 'Win7+ 系统只有「仿宋」，_GB2312 名会静默回退成宋体。',
    },
    {
        'role': '二级标题（楷体）',
        'prefer': ['楷体_GB2312', 'KaiTi_GB2312'],
        'fallback': ['楷体', 'KaiTi', '华文楷体', 'STKaiti'],
        'note': '同上，_GB2312 是旧字库名。',
    },
    {
        'role': '一级标题（黑体）',
        'prefer': ['黑体', 'SimHei'],
        'fallback': ['微软雅黑', 'Microsoft YaHei'],
        'note': '黑体没有 GB2312 版，写「黑体_GB2312」反而回退。',
    },
    {
        'role': '页码 / 数字',
        'prefer': ['宋体', 'SimSun'],
        'fallback': ['华文宋体', 'STSong', 'serif'],
        'note': '页码宋体四号；数字随正文字体。',
    },
]


def font_dirs():
    dirs = [FONT_DIR]
    for d in (os.environ.get('WINDIR', 'C:/Windows') + '/Fonts',
              os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts')):
        dirs.append(d)
    return [d for d in dirs if os.path.isdir(d)]


def _font_families(path):
    """读 name 表，返回该字体所有语言下的族名，中文排前面。

    为什么不用 PIL 的 getname()：它只返回第一个（通常英文）。Word 的
    w:rFonts 与 CSS 认的都是族名，中英文是同一字体的两条 name 记录，
    但用中文名写进 docx，人工核对时才能一眼看出写对了没有。
    """
    import struct
    try:
        with open(path, 'rb') as f:
            head = f.read(65536)
            if len(head) < 12:
                return []
            num = struct.unpack('>H', head[4:6])[0]
            off = length = None
            for i in range(num):
                p = 12 + i * 16
                if p + 16 > len(head):
                    break
                if head[p:p + 4] == b'name':
                    off = struct.unpack('>I', head[p + 8:p + 12])[0]
                    length = struct.unpack('>I', head[p + 12:p + 16])[0]
                    break
            if not off or not length:
                return []
            f.seek(off)
            blk = f.read(length)
        if len(blk) < 6:
            return []
        count = struct.unpack('>H', blk[2:4])[0]
        str_off = struct.unpack('>H', blk[4:6])[0]
        zh, other = [], []
        for i in range(count):
            p = 6 + i * 12
            if p + 12 > len(blk):
                break
            pid, _eid, lid, nid, ln, so = struct.unpack('>HHHHHH', blk[p:p + 12])
            if nid != 1:
                continue
            raw = blk[str_off + so:str_off + so + ln]
            try:
                s = raw.decode('utf-16-be') if pid == 3 else raw.decode('latin-1')
            except Exception:
                continue
            if s and s not in (zh + other):
                (zh if lid in (0x0804, 0x0404, 0x0C04, 0x1004) else other).append(s)
        return zh + other
    except Exception:
        return []


def scan_fonts():
    """扫字体目录，建「所有语言的族名 → 文件路径」映射。

    用 name 表而不是文件名：同族字体在不同机器上文件名各异（simfang.ttf /
    STFANGSO.TTF / 仿宋.ttf），族名才是 Word 与 CSS 认的东西。
    assets/fonts/ 里的优先——使用者自己放进去的字体应当盖过系统里的同名旧版。
    """
    found = {}
    for d in font_dirs():
        for path in glob.glob(os.path.join(d, '*')):
            if os.path.splitext(path)[1].lower() not in ('.ttf', '.ttc', '.otf'):
                continue
            fams = _font_families(path)
            if not fams:
                try:
                    from PIL import ImageFont
                    fams = [ImageFont.truetype(path, 12).getname()[0]]
                except Exception:
                    continue
            for fam in fams:
                if fam:
                    found.setdefault(fam, path)
    return found


def resolve(available, spec):
    """按 prefer → fallback 顺序找第一个本机真有的族名。"""
    for name in spec['prefer']:
        if name in available:
            return name, 'prefer'
    for name in spec['fallback']:
        if name in available:
            return name, 'fallback'
    return None, 'none'


def report(available, as_json=False):
    rows = []
    for spec in SPEC:
        got, tier = resolve(available, spec)
        rows.append({
            'role': spec['role'],
            'prefer': spec['prefer'][0],
            'got': got,
            'tier': tier,
            'note': spec['note'],
            'path': available.get(got) if got else None,
        })

    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return rows

    print('\n公文字体探测')
    print('=' * 78)
    for r in rows:
        mark = {'prefer': '✓ 规范名', 'fallback': '↓ 已降级', 'none': '✗ 缺失'}[r['tier']]
        got = r['got'] or '（无可用）'
        print(f"{r['role']:16s} 规范名 {r['prefer']:16s} → 实际 {got:18s} {mark}")
        if r['tier'] == 'fallback':
            print(f"{'':18s}  {r['note']}")
    print('=' * 78)

    miss = [r for r in rows if r['tier'] != 'prefer']
    if miss:
        print(f'\n{len(miss)} 项没拿到规范字体。这不影响出稿——降级链已生效，')
        print('只是版式与「装了字体的机器上打开」会有可见差别。')
        print('\n想拿到规范版式，两个办法（都不需要改代码）：')
        print(f'  ① 把合法取得的字体文件放进 {FONT_DIR}')
        print('     —— 脚本会自动注册，Word 与 PDF 都跟着用；该目录已在 .gitignore，不入库。')
        print('  ② 在装了这些字体的机器上打开 / 出 PDF。')
        print('\n字体名与文件名的对应关系见 references/12-公文排版规格.md 第三节。')
    else:
        print('\n全部规范字体就位。')
    return rows


def font_face_css():
    """为 assets/fonts 里的字体生成 @font-face，供 PDF 轨注入。

    只在使用者自己放了字体时才有内容。族名固定成 TX-Gongwen-*，与
    gongwen.css 字体栈的第一位对齐——没有对应文件时这些族名不匹配任何东西，
    CSS 自动落到后面的系统字体，不报错也不用改样式。
    """
    if not os.path.isdir(FONT_DIR):
        return ''
    rules = []
    for path in sorted(glob.glob(os.path.join(FONT_DIR, '*'))):
        if os.path.splitext(path)[1].lower() not in ('.ttf', '.otf'):
            continue
        fams = _font_families(path)
        if not fams:
            continue
        joined = ' '.join(fams)
        # 按族名判断往哪个槽位放：小标宋当标题，仿宋当正文，楷体当二级标题
        slot = None
        if '小标宋' in joined or 'XiaoBiaoSong' in joined or 'XBS' in joined.upper():
            slot = 'Title'
        elif '仿宋' in joined or 'FangSong' in joined:
            slot = 'Body'
        elif '楷' in joined or 'Kai' in joined:
            slot = 'Sub'
        if not slot:
            continue
        uri = 'file:///' + path.replace('\\', '/')
        rules.append(
            f"@font-face {{ font-family: 'TX-Gongwen-{slot}'; "
            f"src: url('{uri}'); font-display: block; }}")
    return '\n'.join(rules)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--copy-hint', action='store_true')
    a = ap.parse_args()
    avail = scan_fonts()
    report(avail, as_json=a.json)
    if a.copy_hint and not os.path.isdir(FONT_DIR):
        os.makedirs(FONT_DIR, exist_ok=True)
        print(f'\n已建目录：{FONT_DIR}')
