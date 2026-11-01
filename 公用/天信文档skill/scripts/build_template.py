#!/usr/bin/env python3
"""
天信文档模板生成器 —— 产出空壳 docx（只有页面设置 / 页眉页脚 / 样式，无正文）

为什么要空壳模板：
  1. 页眉 logo、页脚页码域只写一次，后续所有文档从模板出发，不会各写各的。
  2. 样式定义集中在 docx 里，出稿人可以在 Word 中直接改样式，脚本不用动。
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
from check_fonts import resolve as resolve_font, scan_fonts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')
LOGO = os.path.join(ASSETS, 'brand', 'logo-horizontal-color.png')

# 公文字体的规范名与兼容名。字只能写一个名字，Word 没有 CSS 那种降级链，
# 所以选哪个必须由「本机装了哪个」决定，不能拍脑袋。
FONT_GW = {
    'body_gb': ['仿宋_GB2312', 'FangSong_GB2312'],
    'body_compat': ['仿宋', 'FangSong'],
    'sub_gb': ['楷体_GB2312', 'KaiTi_GB2312'],
    'sub_compat': ['楷体', 'KaiTi'],
    'title': ['方正小标宋简体', 'FZXiaoBiaoSong-B05S'],
    'title_mid': ['华文中宋', 'STZhongsong'],
    'title_compat': ['宋体', 'SimSun'],
}

# ── 品牌色 ────────────────────────────────────────────────
LOGO_NAVY = RGBColor(0x1D, 0x3A, 0x5E)   # logo 文字实测色
BRAND_NAVY = RGBColor(0x00, 0x33, 0x8D)
MUTED = RGBColor(0x52, 0x52, 0x52)
BORDER_GREY = RGBColor(0xE0, 0xE0, 0xE0)

# ── 三套版式参数 ──────────────────────────────────────────
#
# 一张表管三档，差别只在参数，不在流程。选错档的代价不是难看，是「该正式的不正式、
# 该轻量的太重」——所以判据写在 SKILL.md「Word 分两档」一节，这里只管落地。
#
# 字体名的一个硬事实（2026-11-01 实测）：本机与 Win7+ 只有「仿宋 / 楷体 / 黑体 / 宋体」，
# **没有**「仿宋_GB2312 / 楷体_GB2312 / 方正小标宋简体」。写 _GB2312 名会静默回退成
# 宋体，正文立刻不像公文。所以默认写通用名，要严格 GB2312 字库的场合用 --gb2312。
FORMATS = {
    # ① 过程稿：写作与复核过程中用。只求看得清、改得动，不承担品牌与出版要求。
    #    无 logo 页眉、无报告编号、无目录——那些是交付物才有的东西。
    'plain': dict(
        margin=(25, 25, 25, 25),           # 上 下 左 右 mm，四边对称
        body_ea='宋体', body_ascii='Times New Roman',
        body_pt=11, line=1.5, first_line_chars=200, body_after=2,
        h1_ea='黑体', h1_pt=15, h1_before=14, h1_after=6,
        h2_ea='黑体', h2_pt=13, h2_before=10, h2_after=4,
        h3_ea='黑体', h3_pt=11.5, h3_before=8, h3_after=2,
        title_ea='黑体', title_pt=20,
        table_pt=10, caption_pt=9,
        header_style='none', footer_style='simple', title_align='left',
        heading_indent=False,
    ),
    # ② 咨询报告 / 尽调报告：对外交付的咨询类报告。宋体正文，气口松，适合长文阅读。
    'report': dict(
        margin=(25, 25, 28, 26),           # 左侧多 2mm 是装订边
        body_ea='宋体', body_ascii='Times New Roman',
        body_pt=10.5, line=1.75, first_line_chars=200, body_after=3,
        h1_ea='黑体', h1_pt=18, h1_before=18, h1_after=10,
        h2_ea='黑体', h2_pt=14, h2_before=14, h2_after=6,
        h3_ea='黑体', h3_pt=11.5, h3_before=10, h3_after=4,
        title_ea='黑体', title_pt=24,
        table_pt=9, caption_pt=8,
        caption_brand=True, caption_bold=True,
        header_style='brand', footer_style='brand', title_align='left',
        heading_indent=False,
    ),
    # ③ 正式公文：GB/T 9704-2012。对外正式行文、报主管部门、需归档的法定文书外壳。
    #    版心 156×225mm、22 行 × 28 字、正文三号仿宋固定 28 磅——这四个数是硬约束，
    #    改一个就不是公文了（依据见 references/12-公文排版规格.md）。
    'gongwen': dict(
        margin=(37, 35, 28, 26),
        body_ea='仿宋', body_ascii='Times New Roman',
        body_pt=16, line=28, first_line_chars=200, line_rule='exact', body_after=0,
        h1_ea='黑体', h1_pt=16, h1_before=0, h1_after=0,
        h2_ea='楷体', h2_pt=16, h2_before=0, h2_after=0,
        h3_ea='仿宋', h3_pt=16, h3_before=0, h3_after=0,
        title_ea='方正小标宋简体', title_pt=22,
        title_line=28, title_line_exact=True, title_after=28,
        table_pt=14, caption_pt=14,
        caption_brand=False, caption_bold=False, caption_center=True,
        caption_before=0, caption_after=0, caption_line=28, caption_line_exact=True,
        header_style='none', footer_style='gongwen', title_align='center',
        # 公文层次序数是正文的一部分，不是独立标题：一律首行缩进 2 字、
        # 与其他正文同一固定行距，段前段后为 0。
        heading_indent=True, heading_line=28,
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


def _pick(avail, candidates, default=None):
    for n in candidates:
        if n in avail:
            return n
    return default


def autodetect_fonts(cfg, gb2312=None):
    """公文写哪个字体名，按本机实际装了什么来定。

    为什么必须探测而不是写死：Word 的 `w:rFonts` 只能给**一个**名字，没有 CSS
    那种降级链。写「仿宋_GB2312」而机器没这个字库 → 静默回退宋体（不报错，
    打印出来才发现）；写「仿宋」而在坚持 GB2312 的机关环境 → 对方看到的是
    另一套字形。两种都不算错，但必须知道自己在哪一种。

    探测优先级：
      正文  仿宋_GB2312（规范名）→ 仿宋（兼容名）
      二级  楷体_GB2312（规范名）→ 楷体（兼容名）
      标题  方正小标宋简体 → 华文中宋 → 宋体

    gb2312=True / False 可强制走规范名 / 兼容名，不受探测影响。
    """
    avail = scan_fonts()
    cfg = dict(cfg)
    tiers = {}

    def choose(key_gb, key_compat):
        if gb2312 is True:
            return FONT_GW[key_gb][0], 'forced'
        if gb2312 is False:
            return _pick(avail, FONT_GW[key_compat], FONT_GW[key_compat][0]), 'forced'
        gb = _pick(avail, FONT_GW[key_gb])
        if gb:
            return gb, 'gb'
        return _pick(avail, FONT_GW[key_compat], FONT_GW[key_compat][0]), 'compat'

    cfg['body_ea'], tiers['正文'] = choose('body_gb', 'body_compat')
    cfg['h2_ea'], tiers['二级标题'] = choose('sub_gb', 'sub_compat')
    # 三四级标题跟正文同一字体
    cfg['h3_ea'] = cfg['body_ea']

    title = _pick(avail, FONT_GW['title'])
    if title:
        tiers['标题'] = 'gb'
    else:
        title = _pick(avail, FONT_GW['title_mid'])
        tiers['标题'] = 'mid' if title else 'compat'
        if not title:
            title = _pick(avail, FONT_GW['title_compat'], '宋体')
    cfg['title_ea'] = title
    return cfg, tiers


def build(fmt='report', out=None, gb2312=None, title_font=None):
    cfg = dict(FORMATS[fmt])
    tiers = None

    # 公文字体按本机字体走「规范名 → 兼容名」；report / plain 用宋体，无需探测。
    if fmt == 'gongwen':
        cfg, tiers = autodetect_fonts(cfg, gb2312)

    # 方正小标宋是商业字体，多数机器没有。没有时 Word 静默回退成宋体
    # （字重偏粗、字面偏大），标题会「看起来对了但不像公文」。要保底就指定宋体。
    if title_font:
        cfg['title_ea'] = title_font

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

    # 标题层级：report / plain 用倍率行距各自成段；gongwen 跟正文同一固定行距 +
    # 首行缩进 2 字（GB/T 9704 §7.3.3.2 的层次序数就是正文段落）。
    h_line = cfg.get('heading_line', 1.35)
    h_rule = 'exact' if cfg.get('heading_line') else 'auto'
    h_indent = cfg['first_line_chars'] if cfg.get('heading_indent') else 0

    h1 = doc.styles['Heading 1']
    style_font(h1, cfg['h1_ea'], cfg['body_ascii'], cfg['h1_pt'], color=RGBColor(0x16, 0x16, 0x16))
    style_para(h1, align=WD_ALIGN_PARAGRAPH.LEFT, before=cfg['h1_before'],
               after=cfg['h1_after'], line=h_line, rule=h_rule,
               first_line_chars=h_indent, keep_with_next=True)

    h2 = doc.styles['Heading 2']
    style_font(h2, cfg['h2_ea'], cfg['body_ascii'], cfg['h2_pt'], color=RGBColor(0x16, 0x16, 0x16))
    style_para(h2, align=WD_ALIGN_PARAGRAPH.LEFT, before=cfg['h2_before'],
               after=cfg['h2_after'], line=h_line, rule=h_rule,
               first_line_chars=h_indent, keep_with_next=True)

    h3 = doc.styles['Heading 3']
    style_font(h3, cfg['h3_ea'], cfg['body_ascii'], cfg['h3_pt'], color=RGBColor(0x16, 0x16, 0x16))
    style_para(h3, align=WD_ALIGN_PARAGRAPH.LEFT, before=cfg['h3_before'],
               after=cfg['h3_after'], line=h_line, rule=h_rule,
               first_line_chars=h_indent, keep_with_next=True)

    title = doc.styles['Title']
    style_font(title, cfg['title_ea'], cfg['body_ascii'], cfg['title_pt'],
               color=RGBColor(0x1D, 0x3A, 0x5E) if cfg.get('title_align') != 'center'
               else RGBColor(0x00, 0x00, 0x00))
    title_align = (WD_ALIGN_PARAGRAPH.CENTER if cfg.get('title_align') == 'center'
                   else WD_ALIGN_PARAGRAPH.LEFT)
    style_para(title, align=title_align, before=0,
               after=cfg.get('title_after', 18), line=cfg.get('title_line', 1.3),
               rule='exact' if cfg.get('title_line_exact') else 'auto')

    # 自定义样式
    # 图注 / 来源 / 表题：report 轨用深蓝加粗做视觉锚点；公文与过程稿一律纯黑，
    # 公文里彩色字属排版错误（复印后成灰块），过程稿则根本不需要装饰。
    cap_color = (RGBColor(0x1D, 0x3A, 0x5E) if cfg.get('caption_brand')
                 else RGBColor(0x16, 0x16, 0x16))
    cap_align = (WD_ALIGN_PARAGRAPH.CENTER if cfg.get('caption_center')
                 else WD_ALIGN_PARAGRAPH.LEFT)

    cap = doc.styles.add_style('天信图注', WD_STYLE_TYPE.PARAGRAPH)
    cap.base_style = normal
    style_font(cap, cfg['body_ea'], cfg['body_ascii'], cfg['caption_pt'],
               color=cap_color if cfg.get('caption_brand') else MUTED)
    style_para(cap, align=cap_align, before=cfg.get('caption_before', 3),
               after=cfg.get('caption_after', 10), line=cfg.get('caption_line', 1.4),
               rule='exact' if cfg.get('caption_line_exact') else 'auto')

    src = doc.styles.add_style('天信来源', WD_STYLE_TYPE.PARAGRAPH)
    src.base_style = normal
    style_font(src, cfg['body_ea'], cfg['body_ascii'], cfg['caption_pt'],
               color=MUTED if cfg.get('caption_brand') else cap_color)
    style_para(src, align=cap_align, before=0,
               after=cfg.get('caption_after', 10), line=cfg.get('caption_line', 1.4),
               rule='exact' if cfg.get('caption_line_exact') else 'auto')

    tcap = doc.styles.add_style('天信表题', WD_STYLE_TYPE.PARAGRAPH)
    tcap.base_style = normal
    style_font(tcap, cfg['body_ea'], cfg['body_ascii'], cfg['table_pt'],
               bold=cfg.get('caption_bold', True), color=cap_color)
    style_para(tcap, align=cap_align, before=cfg.get('caption_before', 8),
               after=cfg.get('caption_after', 4), line=cfg.get('caption_line', 1.4),
               rule='exact' if cfg.get('caption_line_exact') else 'auto',
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
    # brand：logo + 报告编号 + 深蓝细线（咨询报告轨）
    # none ：公文与过程稿都不带 logo。公文每页只有页码——红色版头属于「发文机关
    #        标志」，是首页要素，由红头模板负责，不能塞进页眉每页重复。
    header = sec.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0]
    hp.text = ''
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(6)
    hp.paragraph_format.line_spacing = 1.0

    if cfg.get('header_style', 'brand') == 'brand':
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
    # brand  ：8pt 灰、居中，跟页眉同一套视觉语言
    # simple ：过程稿只要个页码，别的不需要
    # gongwen：宋体四号「— N —」，单页右、双页左（GB/T 9704 §7.3.5）
    footer = sec.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.text = ''
    fstyle = cfg.get('footer_style', 'brand')

    if fstyle == 'gongwen':
        # 奇偶页页码位置不同，靠 settings.xml 的 evenAndOddHeaders 开关；
        # python-docx 开关一开，section.even_page_footer 才不是 default 的副本。
        doc.settings.odd_and_even_pages_header_footer = True
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_page_field(fp, 14, RGBColor(0x00, 0x00, 0x00))
        efp = sec.even_page_footer.paragraphs[0]
        efp.text = ''
        efp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_page_field(efp, 14, RGBColor(0x00, 0x00, 0x00))
    else:
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if fstyle == 'simple':
            add_page_field(fp, 9, MUTED)
        else:
            add_page_field(fp, 8, MUTED)

    # ── 文档属性 ────────────────────────────────────────
    doc.core_properties.title = '天台天信会计师事务所 · 文档模板'
    doc.core_properties.author = '天台天信会计师事务所'

    out = out or os.path.join(ASSETS, f'tianxin-{fmt}.docx')
    doc.save(out)
    print(f'✅ 模板已生成：{out}')
    print(f'   版式：{fmt}  边距：上{top}/下{bottom}/左{left}/右{right} mm')
    print(f'   正文：{cfg["body_ea"]} {cfg["body_pt"]}pt  行距 {cfg["line"]}')
    print(f'   标题：{cfg["title_ea"]} {cfg["title_pt"]}pt  页眉 {cfg.get("header_style")}  页脚 {cfg.get("footer_style")}')
    if fmt == 'gongwen' and tiers:
        label = {'gb': '规范字体', 'mid': '降级（华文中宋）', 'compat': '降级（兼容名）',
                 'forced': '按参数强制'}
        for k, v in tiers.items():
            print(f'   {k}: {cfg["body_ea"] if k == "正文" else cfg["title_ea"] if k == "标题" else cfg["h2_ea"]}'
                  f'  [{label.get(v, v)}]')
        if tiers.get('标题') != 'gb':
            print('   ⚠ 没装方正小标宋简体：Word 会回退成宋体，版式仍合规但字面偏方。')
            print('     要规范版式：把该字体放进 assets/fonts/（脚本自动注册），'
                  '或在装了它的机器上打开。')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--format', default='report', choices=list(FORMATS),
                    help='plain 过程稿 / report 咨询报告 / gongwen 正式公文')
    ap.add_argument('--out', default=None)
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--gb2312', dest='gb', action='store_true', default=None,
                   help='强制用 _GB2312 规范字体名（旧政务环境）')
    g.add_argument('--compat', dest='gb', action='store_false',
                   help='强制用通用字体名（仿宋 / 楷体），不探测 GB2312 字库')
    ap.add_argument('--title-font', default=None,
                    help='覆盖标题字体，如「宋体」保底')
    a = ap.parse_args()
    build(a.format, a.out, gb2312=a.gb, title_font=a.title_font)
