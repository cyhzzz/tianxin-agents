#!/usr/bin/env python3
"""
docx XML 助手 —— 所有元素按 OOXML schema 顺序插入

为什么需要这个文件：
  Word 对 <w:pPr> / <w:rPr> / <w:tcPr> / <w:tblPr> 的子元素顺序是强校验的。
  直接 parent.append(elm) 把 pBdr / shd / tcBorders 塞到末尾，如果该元素
  后面还有 jc / spacing / lang / tblLook，顺序就错了 —— Word 会提示
  「文件已损坏，是否修复」，或者静默丢掉这个属性。
  python-docx 只对常用元素提供了 get_or_add_*，边框和底纹没有，
  所以这里按官方 schema 的 _tag_seq 自己实现有序插入。
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ── schema 顺序（摘自 ECMA-376 / python-docx CT_*._tag_seq）──

ORDER_PPR = [
    'pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl',
    'numPr', 'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens',
    'kinsoku', 'wordWrap', 'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN',
    'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind', 'contextualSpacing',
    'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
    'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange',
]

ORDER_RPR = [
    'rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike',
    'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish',
    'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight',
    'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang',
    'eastAsianLayout', 'specVanish', 'oMath',
]

ORDER_TCPR = [
    'cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap',
    'tcMar', 'textDirection', 'tcFitText', 'vAlign', 'hideMark', 'headers',
    'cellIns', 'cellDel', 'cellMerge', 'tcPrChange',
]

ORDER_TBLPR = [
    'tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize',
    'tblStyleColBandSize', 'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders',
    'shd', 'tblLayout', 'tblCellMar', 'tblLook', 'tblCaption', 'tblDescription',
    'tblPrChange',
]

# 行属性。tblHeader 的次序在 trHeight 之后、tblCellSpacing 之前——
# 插错位置 Word 会认为文件损坏。
ORDER_TRPR = [
    'cnfStyle', 'divId', 'gridBefore', 'gridAfter', 'wBefore', 'wAfter',
    'cantSplit', 'trHeight', 'tblHeader', 'tblCellSpacing', 'jc', 'hidden',
    'ins', 'del', 'trPrChange',
]

ORDERS = {
    'pPr': ORDER_PPR,
    'rPr': ORDER_RPR,
    'tcPr': ORDER_TCPR,
    'tblPr': ORDER_TBLPR,
    'trPr': ORDER_TRPR,
}


def insert_ordered(parent, elm, order_key):
    """把 elm 插到 parent 中符合 schema 顺序的位置；同名旧元素先删掉"""
    order = ORDERS[order_key]
    local = elm.tag.split('}')[1]
    for old in parent.findall(qn(f'w:{local}')):
        parent.remove(old)
    idx = order.index(local)
    successors = tuple(f'w:{t}' for t in order[idx + 1:])
    parent.insert_element_before(elm, *successors)
    return elm


# ── 段落 ─────────────────────────────────────────────────

def add_paragraph_border(paragraph, edge='bottom', color='1D3A5E', sz=4, space=4):
    """段落边框。sz 单位 1/8 pt：4 = 0.5pt，8 = 1pt，12 = 1.5pt"""
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = ppr.find(qn('w:pBdr'))
    if pbdr is None:
        pbdr = insert_ordered(ppr, OxmlElement('w:pBdr'), 'pPr')
    el = OxmlElement(f'w:{edge}')
    el.set(qn('w:val'), 'single')
    el.set(qn('w:sz'), str(sz))
    el.set(qn('w:space'), str(space))
    el.set(qn('w:color'), color)
    pbdr.append(el)


# ── 底纹 ─────────────────────────────────────────────────

def shade_run(run, fill):
    rpr = run._r.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    insert_ordered(rpr, shd, 'rPr')


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    insert_ordered(tcpr, shd, 'tcPr')


# ── 表格 ─────────────────────────────────────────────────

def set_cell_borders(cell, **edges):
    """edges: bottom=('single', 4, '1D3A5E')"""
    tcpr = cell._tc.get_or_add_tcPr()
    borders = tcpr.find(qn('w:tcBorders'))
    if borders is None:
        borders = insert_ordered(tcpr, OxmlElement('w:tcBorders'), 'tcPr')
    for edge, (val, sz, color) in edges.items():
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), val)
        el.set(qn('w:sz'), str(sz))
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), color)
        borders.append(el)


def set_table_three_line(table, color='1D3A5E'):
    """三线表：表格上下各 1pt，其余无线；表头下由调用方加 0.5pt"""
    tbl = table._tbl
    tblpr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{edge}')
        if edge in ('top', 'bottom'):
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), '8')
            el.set(qn('w:color'), color)
        else:
            el.set(qn('w:val'), 'none')
            el.set(qn('w:sz'), '0')
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), 'auto')
        borders.append(el)
    insert_ordered(tblpr, borders, 'tblPr')


def repeat_table_header(table, rows=1):
    """表头跨页重复。

    长表格（风险清单、产区对照、问题列表）一跨页，续页上那半截没有表头，
    读者就不知道每列是什么。这是最典型的「作者在自己电脑上看不出来」的错——
    作者看到的是 Word 里滚动时表头也没了，但他知道列的含义，读者不知道。
    """
    for row in table.rows[:rows]:
        trpr = row._tr.get_or_add_trPr()
        el = OxmlElement('w:tblHeader')
        el.set(qn('w:val'), 'true')
        insert_ordered(trpr, el, 'trPr')


def keep_row_together(table, rows=None):
    """禁止表格行内部跨页拆断。rows=None 表示全部行。

    默认不开：内容多的行被整体推到下一页，会在上一页留出更大的空白，
    得失要按具体文档权衡。表头行建议开。
    """
    for row in (table.rows if rows is None else [table.rows[i] for i in rows]):
        trpr = row._tr.get_or_add_trPr()
        el = OxmlElement('w:cantSplit')
        el.set(qn('w:val'), 'true')
        insert_ordered(trpr, el, 'trPr')


# ── 字体 ─────────────────────────────────────────────────

def set_rfonts(rpr, eastasia, ascii_font):
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = insert_ordered(rpr, OxmlElement('w:rFonts'), 'rPr')
    rf.set(qn('w:ascii'), ascii_font)
    rf.set(qn('w:hAnsi'), ascii_font)
    rf.set(qn('w:eastAsia'), eastasia)
    rf.set(qn('w:cs'), ascii_font)
