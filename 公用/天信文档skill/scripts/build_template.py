#!/usr/bin/env python3
"""
天信文档模板生成器 —— 产出空壳 docx（只有页面设置 / 页眉页脚 / 样式，无正文）

为什么要空壳模板：
  1. 页眉 logo、页脚页码域只写一次，后续所有文档从模板出发，不会各写各的。
  2. 样式定义集中在 docx 里，爸爸可以在 Word 中直接改样式，脚本不用动。
  3. 与申万那套「Document(TEMPLATE) 打开 + 清空正文 + 保留 sectPr」的做法同源，
     但天信不用整页背景图（复印发灰、扫描 OCR 差、双面透背）。

用法：
  python build_template.py [--format report|gongwen] [--out 路径]
"""

import argparse
import os
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_helpers import (  # noqa: E402
    add_paragraph_border, insert_ordered, set_rfonts,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')
LOGO = os.path.join(ASSETS, 'brand', 'logo-horizontal-color.png')

# ── 品牌色 ────────────────────────────────────────────────
LOGO_NAVY = RGBColor(0x1D, 0x3A, 0x5E)   # logo 文字实测色
BRAND_NAVY = RGBColor(0x00, 0x33, 0x8D)
MUTED = RGBColor(0x52, 0x52, 0x52)
BORDER_GREY = RGBColor(0xE0, 0xE0, 0xE0)

# ── 两套版式参数 ──────────────────────────────────────────
FORMATS = {
    # 咨询报告 / 尽调报告：宋体正文，气口松，适合长文阅读
    'report': dict(
        margin=(25, 25, 28, 26),           # 上 下 左 右 mm
        body_ea='宋体', body_ascii='Times New Roman',
        body_pt=10.5, line=1.75, first_line_chars=200, body_after=3,
        h1_ea='黑体', h1_pt=18, h1_before=18, h1_after=10,
        h2_ea='黑体', h2_pt=14, h2_before=14, h2_after=6,
        h3_ea='黑体', h3_pt=11.5, h3_before=10, h3_after=4,
        title_ea='黑体', title_pt=24,
        table_pt=9, caption_pt=8,
    ),
    # 公文：GB/T 9704-2023，仿宋三号，固定行距 28 磅
    'gongwen': dict(
        margin=(37, 35, 28, 26),
        body_ea='仿宋_GB2312', body_ascii='Times New Roman',
        body_pt=16, line=28, first_line_chars=200, line_rule='exact', body_after=0,
        h1_ea='黑体', h1_pt=16, h1_before=0, h1_after=0,
        h2_ea='楷体_GB2312', h2_pt=16, h2_before=0, h2_after=0,
        h3_ea='仿宋_GB2312', h3_pt=16, h3_before=0, h3_after=0,
        title_ea='方正小标宋简体', title_pt=22,
        table_pt=14, caption_pt=14,
    ),
}


def style_font(style, eastasia, ascii_font, pt, bold=False, color=None, italic=False):
    rpr = style.element.get_or_add_rPr()
    set_rfonts(rpr, eastasia, ascii_font)
    style.font.size = Pt(pt)
    style.font.bold = bold
    style.font.italic = italic
    if color is not None:
        style.font.color.rgb = color


def style_para(style, align=None, before=0, after=0, line=None,
               first_line_chars=0, keep_with_next=False, rule='auto'):
    pf = style.paragraph_format
    if align is not None:
        style.paragraph_format.alignment = align
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if line is not None:
        if rule == 'exact':
            pf.line_spacing = Pt(line)
        else:
            pf.line_spacing = line
    if keep_with_next:
        pf.keep_with_next = True

    ppr = style.element.get_or_add_pPr()
    for old in ppr.findall(qn('w:ind')):
        ppr.remove(old)
    if first_line_chars:
        ind = OxmlElement('w:ind')
        ind.set(qn('w:firstLineChars'), str(first_line_chars))
        # 兜底值：2 字符 = 2 × 字号（twips = pt × 20）
        ind.set(qn('w:firstLine'), str(int(2 * pt_of(style) * 20)))
        insert_ordered(ppr, ind, 'pPr')


def shade_para_style(style, fill):
    """段落样式级底纹，用于代码块这类需要整片灰底的样式"""
    ppr = style.element.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    insert_ordered(ppr, shd, 'pPr')


def pt_of(style):
    try:
        return style.font.size.pt
    except Exception:
        return 10.5


def add_page_field(paragraph, size_pt, color):
    """插入 PAGE 域，包在 — — 之间"""
    def run_with(text=None):
        r = paragraph.add_run(text or '')
        r.font.size = Pt(size_pt)
        r.font.color.rgb = color
        r.font.name = 'Times New Roman'
        rpr = r._r.get_or_add_rPr()
        set_rfonts(rpr, '宋体', 'Times New Roman')
        return r

    run_with('— ')
    r = paragraph.add_run()
    r.font.size = Pt(size_pt)
    r.font.color.rgb = color
    rpr = r._r.get_or_add_rPr()
    set_rfonts(rpr, '宋体', 'Times New Roman')

    begin = OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve'); instr.text = ' PAGE '
    sep = OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'), 'separate')
    txt = OxmlElement('w:t'); txt.text = '1'
    end = OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'), 'end')
    for el in (begin, instr, sep, txt, end):
        r._r.append(el)
    run_with(' —')


def build(fmt='report', out=None):
    cfg = FORMATS[fmt]
    doc = Document()

    # ── 页面 ────────────────────────────────────────────
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    top, bottom, left, right = cfg['margin']
    sec.top_margin, sec.bottom_margin = Mm(top), Mm(bottom)
    sec.left_margin, sec.right_margin = Mm(left), Mm(right)
    sec.header_distance, sec.footer_distance = Mm(12), Mm(12)

    # ── 样式 ────────────────────────────────────────────
    normal = doc.styles['Normal']
    style_font(normal, cfg['body_ea'], cfg['body_ascii'], cfg['body_pt'])
    normal.font.color.rgb = RGBColor(0x16, 0x16, 0x16)
    style_para(normal, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
               before=0, after=cfg['body_after'], line=cfg['line'],
               first_line_chars=cfg['first_line_chars'],
               rule=cfg.get('line_rule', 'auto'))

    h1 = doc.styles['Heading 1']
    style_font(h1, cfg['h1_ea'], cfg['body_ascii'], cfg['h1_pt'], color=RGBColor(0x16, 0x16, 0x16))
    style_para(h1, align=WD_ALIGN_PARAGRAPH.LEFT, before=cfg['h1_before'],
               after=cfg['h1_after'], line=1.35, keep_with_next=True)

    h2 = doc.styles['Heading 2']
    style_font(h2, cfg['h2_ea'], cfg['body_ascii'], cfg['h2_pt'], color=RGBColor(0x16, 0x16, 0x16))
    style_para(h2, align=WD_ALIGN_PARAGRAPH.LEFT, before=cfg['h2_before'],
               after=cfg['h2_after'], line=1.35, keep_with_next=True)

    h3 = doc.styles['Heading 3']
    style_font(h3, cfg['h3_ea'], cfg['body_ascii'], cfg['h3_pt'], color=RGBColor(0x16, 0x16, 0x16))
    style_para(h3, align=WD_ALIGN_PARAGRAPH.LEFT, before=cfg['h3_before'],
               after=cfg['h3_after'], line=1.35, keep_with_next=True)

    title = doc.styles['Title']
    style_font(title, cfg['title_ea'], cfg['body_ascii'], cfg['title_pt'],
               color=RGBColor(0x1D, 0x3A, 0x5E))
    style_para(title, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=18, line=1.3)

    # 自定义样式
    cap = doc.styles.add_style('天信图注', WD_STYLE_TYPE.PARAGRAPH)
    cap.base_style = normal
    style_font(cap, cfg['body_ea'], cfg['body_ascii'], cfg['caption_pt'], color=MUTED)
    style_para(cap, align=WD_ALIGN_PARAGRAPH.LEFT, before=3, after=10, line=1.4)

    src = doc.styles.add_style('天信来源', WD_STYLE_TYPE.PARAGRAPH)
    src.base_style = normal
    style_font(src, cfg['body_ea'], cfg['body_ascii'], cfg['caption_pt'], color=MUTED)
    style_para(src, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=10, line=1.4)

    tcap = doc.styles.add_style('天信表题', WD_STYLE_TYPE.PARAGRAPH)
    tcap.base_style = normal
    style_font(tcap, cfg['body_ea'], cfg['body_ascii'], cfg['table_pt'],
               bold=True, color=RGBColor(0x1D, 0x3A, 0x5E))
    style_para(tcap, align=WD_ALIGN_PARAGRAPH.LEFT, before=8, after=4, line=1.4,
               keep_with_next=True)

    # 表格内文字样式（不缩进、不两端对齐）
    tcell = doc.styles.add_style('天信表格文字', WD_STYLE_TYPE.PARAGRAPH)
    tcell.base_style = normal
    style_font(tcell, cfg['body_ea'], cfg['body_ascii'], cfg['table_pt'])
    style_para(tcell, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=0, line=1.45)

    # 代码 / ASCII 架构图：西文等宽 + 中文全角，固定行距保证框线连得上。
    # 用宋体而不是等线，是因为宋体汉字正好两个半角宽，与 ┌─┐ 这类制表符的
    # 宽度假设一致；换成正文字体，框线立刻错位。
    code_pt = cfg['table_pt'] - 1
    code = doc.styles.add_style('天信代码', WD_STYLE_TYPE.PARAGRAPH)
    code.base_style = normal
    style_font(code, '宋体', 'Courier New', code_pt, color=RGBColor(0x16, 0x16, 0x16))
    # 行距必须贴着字号（1.05 倍），不能给固定值：行距一大，制表符 │ 就在
    # 行与行之间断开，整个架构图散成一堆虚线。
    style_para(code, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=0,
               line=round(code_pt * 1.05, 1), rule='exact')
    ppr = code.element.get_or_add_pPr()
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), '454')          # 0.8cm，灰底不贴版心边
    ind.set(qn('w:firstLine'), '0')
    ind.set(qn('w:firstLineChars'), '0')  # 不写这句会继承正文的 2 字符首行缩进
    insert_ordered(ppr, ind, 'pPr')
    shade_para_style(code, 'F7F7F7')

    # ── 页眉 ────────────────────────────────────────────
    header = sec.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.text = ''
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(6)
    hp.paragraph_format.line_spacing = 1.0

    usable = Mm(210 - left - right)
    hp.paragraph_format.tab_stops.add_tab_stop(usable, WD_TAB_ALIGNMENT.RIGHT)

    run = hp.add_run()
    run.add_picture(LOGO, width=Mm(40))

    tab = hp.add_run('\t')
    tab.font.size = Pt(8)

    docno = hp.add_run('天信咨字〔2026〕第 000 号')
    docno.font.size = Pt(8)
    docno.font.color.rgb = MUTED
    rpr = docno._r.get_or_add_rPr()
    set_rfonts(rpr, '宋体', 'Times New Roman')

    add_paragraph_border(hp, edge='bottom', color='1D3A5E', sz=4, space=4)

    # ── 页脚 ────────────────────────────────────────────
    footer = sec.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.text = ''
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_field(fp, 8, MUTED)

    # ── 文档属性 ────────────────────────────────────────
    doc.core_properties.title = '天台天信会计师事务所 · 文档模板'
    doc.core_properties.author = '天台天信会计师事务所'

    out = out or os.path.join(ASSETS, f'tianxin-{fmt}.docx')
    doc.save(out)
    print(f'✅ 模板已生成：{out}')
    print(f'   版式：{fmt}  边距：上{top}/下{bottom}/左{left}/右{right} mm')
    print(f'   正文：{cfg["body_ea"]} {cfg["body_pt"]}pt  行距 {cfg["line"]}')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--format', default='report', choices=list(FORMATS))
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    build(a.format, a.out)
