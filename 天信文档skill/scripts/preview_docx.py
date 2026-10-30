#!/usr/bin/env python3
"""
docx 近似预览 —— 把生成好的 Word 文档渲染成 A4 HTML，供自查版式

注意：这不是 Word 的真实渲染，只是按 docx 里的样式参数（字号/行距/间距）
      还原一份近似版式，用来检查层级比例、表格观感、留白是否失衡。
      最终效果仍以 Word 打开为准。

用法：
  python preview_docx.py 报告.docx [--out 预览.html]
"""

import argparse
import base64
import os
import sys

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

# 样式 → CSS（对应 build_template.py 的 report 版式）
# 注意：这些字符串会塞进 <p style="...">，属性值里只能用单引号，
# 一旦出现双引号，浏览器会在那里截断整个 style，页面上就全成了默认样式。
SANS = "'Microsoft YaHei','SimHei',sans-serif"
SERIF = "SimSun,'Songti SC',serif"
STYLE_CSS = {
    'Title':      f"font-family:{SANS};font-size:24pt;font-weight:600;color:#1D3A5E;line-height:1.3;margin:0 0 16pt;",
    'Heading 1':  f"font-family:{SANS};font-size:18pt;font-weight:500;color:#161616;line-height:1.35;margin:18pt 0 10pt;",
    'Heading 2':  f"font-family:{SANS};font-size:14pt;font-weight:500;color:#161616;line-height:1.35;margin:14pt 0 6pt;",
    'Heading 3':  f"font-family:{SANS};font-size:11.5pt;font-weight:500;color:#161616;line-height:1.35;margin:10pt 0 4pt;",
    'Normal':     f"font-family:{SERIF};font-size:10.5pt;line-height:1.75;color:#161616;text-align:justify;text-indent:2em;margin:0 0 3pt;",
    '天信表题':    "font-family:SimSun,serif;font-size:9pt;font-weight:700;color:#1D3A5E;line-height:1.4;margin:8pt 0 4pt;text-indent:0;",
    '天信来源':    "font-family:SimSun,serif;font-size:8pt;color:#525252;line-height:1.4;margin:4pt 0 10pt;text-indent:0;",
    '天信图注':    "font-family:SimSun,serif;font-size:8pt;color:#525252;line-height:1.4;margin:3pt 0 10pt;text-indent:0;text-align:center;",
    '天信表格文字': "font-family:SimSun,serif;font-size:9pt;line-height:1.45;text-indent:0;margin:0;",
    '天信代码':    "font-family:'Courier New',SimSun,monospace;font-size:8pt;line-height:1.05;"
                   "background:#F7F7F7;text-indent:0;margin:0;padding-left:0.8cm;white-space:pre;",
}


def run_html(run):
    txt = run.text
    if not txt:
        return ''
    esc = (txt.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
              .replace('\n', '<br>'))
    style = ''
    if run.bold:
        style += 'font-weight:700;'
    # 段落里显式设过的字号要照搬，否则预览会拿样式的默认字号糊弄人：
    # 主标题按字数收了字号（24 → 22.5pt）才一行放得下，预览若按 24pt 画
    # 就会假报「标题断成两行」。
    if run.font.size is not None:
        style += f'font-size:{run.font.size.pt:g}pt;'
    rpr = run._r.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
    if rpr is not None:
        shd = rpr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
        if shd is not None:
            fill = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
            if fill:
                style += f'background:#{fill};padding:0 .15em;'
    return f'<span style="{style}">{esc}</span>' if style else esc


def para_html(p):
    name = p.style.name
    css = STYLE_CSS.get(name, STYLE_CSS['Normal'])
    inner = ''.join(run_html(r) for r in p.runs)
    ppr = p._p.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
    if not inner.strip():
        # 代码块的空行要占位，否则架构图的纵向间距会塌掉
        if name == '天信代码':
            return f'<p style="{css}">&nbsp;</p>'
        # 只有下边框、没有文字 = 分隔线
        if ppr is not None and ppr.find(
                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pBdr') is not None:
            return f'<p style="{css}border-bottom:0.5pt solid #D9D9D9;"></p>'
        return ''
    # 引用块左边框
    if ppr is not None and ppr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pBdr') is not None:
        css += 'border-left:1.5pt solid #E0E0E0;padding-left:8pt;margin-left:6pt;text-indent:0;'
    if p.paragraph_format.left_indent:
        css += f'padding-left:{p.paragraph_format.left_indent.pt:.0f}pt;text-indent:0;'
    return f'<p style="{css}">{inner}</p>'


def table_html(t):
    head = t.rows[0]
    body = t.rows[1:]
    css_tbl = ('width:100%;border-collapse:collapse;margin:0 0 4pt;'
               'border-top:1pt solid #1D3A5E;border-bottom:1pt solid #1D3A5E;font-family:SimSun,serif;')
    h = ''.join(
        f'<th style="font-size:9pt;font-weight:700;text-align:left;padding:4pt 6pt;'
        f'background:#F4F4F4;border-bottom:0.5pt solid #1D3A5E;">{c.text}</th>'
        for c in head.cells)
    rows = ''
    for r in body:
        cells = ''.join(
            f'<td style="font-size:9pt;padding:4pt 6pt;vertical-align:top;">{c.text}</td>'
            for c in r.cells)
        rows += f'<tr>{cells}</tr>'
    return f'<table style="{css_tbl}"><thead><tr>{h}</tr></thead><tbody>{rows}</tbody></table>'


def data_uri(path):
    """图片转 base64 内嵌。用 file:// 引用，页面一旦被托管到 http 就会被浏览器拦掉"""
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'svg': 'image/svg+xml', 'gif': 'image/gif'}.get(ext, 'image/png')
    with open(path, 'rb') as f:
        payload = base64.b64encode(f.read()).decode('ascii')
    return f'data:{mime};base64,{payload}'


def build_html(docx_path, out_path):
    doc = Document(docx_path)
    sec = doc.sections[0]
    body_parts = []
    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            html = para_html(Paragraph(child, doc))
            if html:
                body_parts.append(html)
        elif tag == 'tbl':
            body_parts.append(table_html(Table(child, doc)))

    # 页眉页脚
    hdr = doc.sections[0].header.paragraphs[0].text.strip()
    logo = os.path.join(SKILL, 'assets', 'brand', 'logo-horizontal-color.png')
    logo_uri = data_uri(logo) if os.path.exists(logo) else ''

    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>预览 · {os.path.basename(docx_path)}</title>
<style>
  @page {{ size: A4; margin: 0; }}
  body {{ margin:0; background:#8a8a8a; font-family:SimSun,serif; }}
  .sheet {{ width:210mm; min-height:297mm; background:#fff; margin:0 auto;
            padding:{sec.top_margin.mm:.0f}mm {sec.right_margin.mm:.0f}mm {sec.bottom_margin.mm:.0f}mm {sec.left_margin.mm:.0f}mm;
            box-sizing:border-box; position:relative; }}
  .hdr {{ display:flex; align-items:flex-end; justify-content:space-between;
          border-bottom:0.5pt solid #1D3A5E; padding-bottom:4pt; margin-bottom:8mm;
          position:absolute; left:{sec.left_margin.mm:.0f}mm; right:{sec.right_margin.mm:.0f}mm; top:{sec.header_distance.mm:.0f}mm; }}
  .hdr img {{ width:40mm; }}
  .hdr .no {{ font-size:8pt; color:#525252; font-family:SimSun,serif; }}
  .ftr {{ position:absolute; bottom:{sec.footer_distance.mm:.0f}mm; left:0; right:0;
          text-align:center; font-size:8pt; color:#525252; }}
  .content {{ }}
</style></head>
<body>
<div class="sheet">
  <div class="hdr"><img src="{logo_uri}"><span class="no">{hdr.lstrip()}</span></div>
  <div class="content">
    {''.join(body_parts)}
  </div>
  <div class="ftr">— 1 —</div>
</div>
</body></html>'''

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ 预览已生成：{out_path}')
    return out_path


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.path)[0] + '-预览.html'
    build_html(a.path, out)
