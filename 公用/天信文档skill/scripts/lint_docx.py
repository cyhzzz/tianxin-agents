#!/usr/bin/env python3
"""
天信 docx 机械自检

查三类事：
  1. OOXML schema 顺序 —— pPr / rPr / tcPr / tblPr 子元素顺序错了，
     Word 会提示「文件已损坏」或静默丢属性。人眼看不出来，只能机械查。
  2. 占位符残留 —— {{xxx}} / TODO / ××× / 【待填】 这类没替换的模板痕迹。
  3. 文档要件 —— 页眉是否带 logo、页脚是否有页码、有无连续空段。

用法：
  python lint_docx.py 报告.docx [--strict]
退出码：0 通过；1 有阻断问题（--strict 时警告也算阻断）
"""

import argparse
import re
import sys

from docx import Document
from docx.oxml.ns import qn

ORDERS = {
    'pPr': ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
            'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
            'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE',
            'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
            'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
            'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
            'sectPr', 'pPrChange'],
    'rPr': ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike',
            'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid',
            'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz',
            'szCs', 'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign',
            'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath'],
    'tcPr': ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd',
             'noWrap', 'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark',
             'headers', 'cellIns', 'cellDel', 'cellMerge', 'tcPrChange'],
    'tblPr': ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize',
              'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd',
              'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption',
              'tblDescription', 'tblPrChange'],
}

PLACEHOLDER_RE = re.compile(
    r'\{\{[^}]*\}\}|【待填[^】]*】|TODO|TBD|×××|XXX|Lorem ipsum|待补充|待填写'
)

FORBIDDEN_COLORS = {
    '6366F1': 'Indigo 紫色（品牌禁用色）',
    '8B5CF6': '紫色（品牌禁用色）',
    'A78BFA': '紫色（品牌禁用色）',
}


def iter_elements(root):
    for el in root.iter():
        yield el


class Report:
    def __init__(self):
        self.errors = []
        self.warns = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warns.append(msg)


def check_schema_order(doc, rep):
    bad = 0
    parts = [('document', doc.element.body)]
    for i, sec in enumerate(doc.sections):
        parts.append((f'header{i}', sec.header._element))
        parts.append((f'footer{i}', sec.footer._element))
    for part_name, el in parts:
        for sub in iter_elements(el):
            tag = sub.tag.split('}')[-1] if '}' in sub.tag else ''
            if tag not in ORDERS:
                continue
            order = ORDERS[tag]
            seq = []
            for c in sub:
                ct = c.tag.split('}')[-1] if '}' in c.tag else ''
                if ct in order:
                    seq.append((order.index(ct), ct))
            idxs = [s[0] for s in seq]
            if idxs != sorted(idxs):
                bad += 1
                if bad <= 5:
                    rep.err(f'schema 顺序错：{part_name} 的 <w:{tag}> 子元素顺序 {[s[1] for s in seq]}')
    if bad > 5:
        rep.err(f'…另有 {bad - 5} 处同类顺序错误')
    if bad == 0:
        print(f'  ✓ schema 顺序：{len(parts)} 个部件全部合规')


def check_placeholders(doc, rep):
    hits = []
    for p in doc.paragraphs:
        m = PLACEHOLDER_RE.search(p.text)
        if m:
            hits.append((m.group(0), p.text[:36]))
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                m = PLACEHOLDER_RE.search(cell.text)
                if m:
                    hits.append((m.group(0), cell.text[:36]))
    if hits:
        for w, ctx in hits[:8]:
            rep.err(f'占位符残留「{w}」：{ctx}')
    else:
        print('  ✓ 占位符：无残留')


def check_requirements(doc, rep):
    sec = doc.sections[0]
    hxml = sec.header._element.xml
    fxml = sec.footer._element.xml
    has_pic = 'graphicData' in hxml or 'blip' in hxml
    has_page = 'PAGE' in fxml
    print(f'  {"✓" if has_pic else "✗"} 页眉 logo：{"有" if has_pic else "没有"}')
    print(f'  {"✓" if has_page else "✗"} 页脚页码域：{"有" if has_page else "没有"}')
    if not has_pic:
        rep.err('页眉没有 logo')
    if not has_page:
        rep.err('页脚没有页码域')


def check_blank_runs(doc, rep):
    run_start, longest, cur = 0, 0, 0
    for p in doc.paragraphs:
        if p.text.strip():
            cur = 0
        else:
            cur += 1
            longest = max(longest, cur)
    if longest >= 3:
        rep.warn(f'连续空段落 {longest} 个（可能是多余空行，也可能是刻意留白，请目视）')
    else:
        print(f'  ✓ 空段落：最长连续 {longest} 个')


def check_forbidden_colors(doc, rep):
    parts = [doc.element.xml]
    for sec in doc.sections:
        parts.append(sec.header._element.xml)
        parts.append(sec.footer._element.xml)
    xml = ''.join(parts).upper()
    found = [f'{h} {name}' for h, name in FORBIDDEN_COLORS.items() if h in xml]
    if found:
        for f in found:
            rep.err(f'使用了禁用色：{f}')
    else:
        print('  ✓ 配色：未出现禁用色')


def check_table_titles(doc, rep):
    """表格有没有题注。

    正式报告里一张没有表题的表格是硬伤：读者不知道它在说明什么、数据从哪来、
    什么口径。规范要求「**表 N　结论式标题**」在上、数据来源在下。
    紧跟在 h3/h4 小节标题下面的表可以豁免——小节标题已经交代了它是什么。
    """
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    body = doc.element.body
    prev = None
    bare, total = [], 0
    for child in body.iterchildren():
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            prev = Paragraph(child, doc).style.name
        elif tag == 'tbl':
            total += 1
            if prev not in ('天信表题', 'Heading 2', 'Heading 3'):
                bare.append(total)
            prev = 'table'
    if not total:
        return
    if not bare:
        print(f'  ✓ 表格题注：{total} 张表都有表题或紧邻小节标题')
        return
    show = '、'.join(str(i) for i in bare[:12]) + ('…' if len(bare) > 12 else '')
    rep.warn(f'{len(bare)}/{total} 张表没有题注（第 {show} 张）。'
             f'读者不知道表在说什么、数据哪来；补「**表 N　结论式标题**」+ 数据来源行')


BOX_CHARS = '┌┐└┘├┤┬┴┼│─┏┓┗┛┣┫┳┻╋━┃'


def check_code_blocks(doc, rep):
    """代码块体检。

    两件事：
      · 用制表符画的架构图，字体不是等宽就一定错位（宋体/Times 下 │ 对不上）
      · 框图这类东西本质上不该出现在正式报告里——它是「画不出来的图」的替代品。
        工具能做的只是把它排整齐，并提醒作者：这里应该是一张图或一张表。
    """
    code = [p for p in doc.paragraphs if p.style.name == '天信代码']
    if not code:
        return
    boxy = [p for p in code if any(c in p.text for c in BOX_CHARS)]
    if not boxy:
        print(f'  ✓ 代码块：{len(code)} 段（无制表符框图）')
        return

    # 等宽：样式里 ascii 字体必须是 Courier New / Consolas 一类
    st = doc.styles['天信代码']
    rpr = st.element.find(qn('w:rPr'))
    ascii_font = ''
    if rpr is not None:
        rf = rpr.find(qn('w:rFonts'))
        if rf is not None:
            ascii_font = rf.get(qn('w:ascii')) or ''
    mono = ('courier', 'consolas', 'mono', 'menlo', 'dejavu sans mono')
    if not any(m in ascii_font.lower() for m in mono):
        rep.err(f'代码块字体不是等宽（ascii={ascii_font or "未设置"}），'
                f'制表符框图一定错位')

    # 最长行宽：7.6pt Courier 约 4.56pt/字符，版心 442pt → 96 字符
    widest = max((len(p.text) for p in code), default=0)
    if widest > 96:
        rep.warn(f'代码块最长行 {widest} 字符，超出 A4 版心可容纳宽度，会被裁切')

    print(f'  ℹ 代码块：{len(code)} 段，其中 {len(boxy)} 段含制表符框图（最长 {widest} 字符）')
    rep.warn('文档含 ASCII 框图（制表符画的）。正式对外报告建议改为图片或表格——'
             '框图在 Word 里换字体、换纸张、转 PDF 都可能错位，且无法被检索')


def check_stats(doc):
    chars = sum(len(p.text) for p in doc.paragraphs)
    tables = len(doc.tables)
    figs = sum(1 for p in doc.paragraphs if p._p.xml.count('graphicData'))
    print(f'  ℹ 规模：段落 {len(doc.paragraphs)} · 表格 {tables} · 图片 {figs} · 正文 {chars} 字')


def main(path, strict=False):
    print(f'\n检查 {path}')
    doc = Document(path)
    rep = Report()
    check_schema_order(doc, rep)
    check_placeholders(doc, rep)
    check_requirements(doc, rep)
    check_blank_runs(doc, rep)
    check_forbidden_colors(doc, rep)
    check_code_blocks(doc, rep)
    check_table_titles(doc, rep)
    check_stats(doc)

    print()
    for w in rep.warns:
        print(f'  ⚠ {w}')
    for e in rep.errors:
        print(f'  ✗ {e}')
    if not rep.errors and not (strict and rep.warns):
        print('  ✅ 通过\n')
        return 0
    print(f'  ❌ {len(rep.errors)} 个错误，{len(rep.warns)} 个警告\n')
    return 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    sys.exit(main(a.path, a.strict))
