#!/usr/bin/env python3
"""
Markdown → 天信 A4 报告（单文件 HTML）

与 md2docx 共用同一套 Markdown 解析器（parse_blocks），两条轨道的输入约定
必须完全一致 —— 否则作者要为不同出口写两版稿子，早晚会漂。

产出是**单文件 HTML**：CSS 内联、logo base64 内嵌，可以直接发链接、丢进
浏览器、Ctrl+P 存 PDF，不依赖任何外部资源。

用法：
  python md2html.py --input 报告.md --output 报告.html \
      [--docno "天信咨字〔2026〕第 012 号"] [--cover] [--marks]
"""

import argparse
import base64
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from md2docx import parse_blocks  # noqa: E402  两条轨道共用同一套解析
import chart  # noqa: E402

SKILL = os.path.dirname(HERE)
CSS = os.path.join(SKILL, 'assets', 'report.css')
LOGO = os.path.join(SKILL, 'assets', 'brand', 'logo-horizontal-color.png')
SEAL = os.path.join(SKILL, 'assets', 'brand', 'seal-mark-color.png')

MARK_CLASS = {'事实': 'mark-fact', '行业': 'mark-industry', '推演': 'mark-infer'}


def data_uri(path):
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
            'svg': 'image/svg+xml'}.get(ext, 'image/png')
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode('ascii')


def esc(t):
    """转义 + 换行处理。

    两种换行来源：
      · 引用块和代码块里的真换行 \n
      · 表格单元格、引用块里手写的 <br>（写 SWOT、并列清单时几乎必用）
    在 HTML 里两者都是 <br>。不处理的话 <br> 会以字面文字印在纸上。
    """
    t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I)
    t = html.escape(t, quote=False)
    return t.replace('\n', '<br>')


def inline(text, marks=False):
    """**加粗** + 三级标记"""
    out = []
    for part in re.split(r'(\*\*[^*]+\*\*)', text):
        if not part:
            continue
        bold = part.startswith('**') and part.endswith('**') and len(part) > 4
        seg = part[2:-2] if bold else part
        if marks and re.search(r'【(事实|行业|推演)】', seg):
            for ch in re.split(r'(【(?:事实|行业|推演)】)', seg):
                if not ch:
                    continue
                m = re.fullmatch(r'【(事实|行业|推演)】', ch)
                if m:
                    out.append(f'<span class="mark {MARK_CLASS[m.group(1)]}">{esc(ch)}</span>')
                else:
                    out.append(f'<strong>{esc(ch)}</strong>' if bold else esc(ch))
            continue
        out.append(f'<strong>{esc(seg)}</strong>' if bold else esc(seg))
    return ''.join(out)


def render_block(kind, payload, marks, charts=None):
    if kind == 'h1':
        return ''  # 文档标题单独处理
    if kind == 'h2':
        return f'<h2>{esc(payload)}</h2>'
    if kind == 'h3':
        return f'<h3>{esc(payload)}</h3>'
    if kind == 'h4':
        return f'<h4>{esc(payload)}</h4>'
    if kind == 'p':
        m = re.fullmatch(r'@@CHART_(\d+)@@', payload.strip())
        if m and charts is not None:
            return chart.to_html(charts.get(int(m.group(1))), 'report')
        return f'<p>{inline(payload, marks)}</p>'
    if kind == 'quote':
        return f'<blockquote><p>{inline(payload, marks)}</p></blockquote>'
    if kind == 'code':
        lang, body = payload
        # 代码块内保留原始换行与空格，不能走 esc（它会把 \n 变成 <br>）
        cls = f' class="language-{esc(lang)}"' if lang else ''
        return f'<pre class="code-block"><code{cls}>{html.escape(body, quote=False)}</code></pre>'
    if kind == 'hr':
        return '<hr>'
    if kind == 'list':
        items = []
        for lvl, marker, text in payload:
            ordered = bool(re.match(r'\d+', marker))
            style = f' style="margin-left:{lvl * 14}pt"'
            items.append(f'<li{style}>{inline(text, marks)}</li>')
        if payload and re.match(r'\d+', payload[0][1]):
            return '<ol>' + ''.join(items) + '</ol>'
        return '<ul>' + ''.join(items) + '</ul>'
    if kind == 'caption':
        return f'<p class="table-title">{inline(payload, False)}</p>'
    if kind == 'source':
        return f'<p class="table-source">{inline(payload, False)}</p>'
    if kind == 'table':
        header, rows = payload
        th = ''.join(f'<th>{inline(c, False)}</th>' for c in header)
        body = ''.join('<tr>' + ''.join(f'<td>{inline(c, marks)}</td>' for c in r) + '</tr>'
                       for r in rows)
        return f'<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'
    if kind == 'image':
        alt, path = payload
        if not os.path.exists(path):
            return f'<p class="table-source">［缺图：{esc(alt or path)}］</p>'
        return (f'<figure><img src="{data_uri(path)}" alt="{esc(alt)}">'
                f'{"<figcaption>" + esc(alt) + "</figcaption>" if alt else ""}</figure>')
    return ''


USABLE_PT = 442          # A4 版心宽度 156mm


def fit_font_pt(text, max_pt, min_pt=14.0):
    """按字数把标题缩到一行放得下（中文 1 字宽、西文 0.55）"""
    units = sum(0.55 if ord(c) < 0x2E80 else 1.0 for c in text)
    if units <= 0:
        return max_pt
    return max(min_pt, min(max_pt, USABLE_PT / units))


def extract_date(md):
    """从正文里找报告日期。

    封面日期不能取「今天」——报告是 6 月编的，10 月才排版，
    封面就会印成 10 月，客户一眼看出不对。这是真实项目里立刻暴露的错。
    """
    pat = (r'(?:编制日期|报告日期|出具日期|日\s*期)[^\d\n]{0,6}'
           r'(\d{4})\s*[年\-./]\s*(\d{1,2})')
    m = re.search(pat, md)
    if m:
        return f'{m.group(1)} 年 {int(m.group(2))} 月'
    m = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月', md)
    if m:
        return f'{m.group(1)} 年 {int(m.group(2))} 月'
    from datetime import datetime
    return datetime.now().strftime('%Y 年 %m 月')


def auto_chapter_break(blocks, md_text):
    """要不要每章另起一页。

    正式报告（十几章、几万字）按章另起是对的，也是行业惯例；
    但 1,000 字的短报告照此办理，会变成「每页只有一小段 + 大片空白」，
    比连排难看十倍。所以按体量自动判断，再用参数强制覆盖。
    """
    n_h2 = sum(1 for k, _ in blocks if k == 'h2')
    return n_h2 >= 6 and len(md_text) >= 8000


def build(md_text, docno=None, cover=False, marks=False, css_text=None, date=None,
          chapter_break=None):
    md_text, charts = chart.extract(md_text)
    blocks = parse_blocks(md_text)
    title = next((p for k, p in blocks if k == 'h1'), '')

    # 按 h2（章）切 chapter：每章另起一页。
    #
    # 早先是按 `---` 切，但真实报告里 `---` 几乎总是章与章之间的分隔线，
    # 一旦正文里还有别的 `---`（比如附录前的落款分隔），就会凭空多出半页空白。
    # 章的分页理由应当来自「这一章开始了」，而不是「这里有一条横线」。
    if chapter_break is None:
        chapter_break = auto_chapter_break(blocks, md_text)
    chapters, cur = [], []
    for k, p in blocks:
        if k == 'pagebreak':
            chapters.append(cur); cur = []
        elif k == 'h1':
            continue
        elif chapter_break and k == 'h2' and any(x[0] == 'h2' for x in cur):
            # 只有当前片里已经有章标题时才切——文档抬头（标题、机密栏、委托方）
            # 应当跟正文第一页待在一起，不该独占一页只写三行。
            chapters.append(cur)
            cur = [(k, p)]
        else:
            cur.append((k, p))
    if cur:
        chapters.append(cur)

    parts = []
    for idx, blocks_in in enumerate(chapters):
        # 表题 + 表格 + 来源 包成一个不可拆块
        buf, i = [], 0
        while i < len(blocks_in):
            k, p = blocks_in[i]
            if k == 'caption':
                inner = render_block(k, p, marks, charts)
                j = i + 1
                while j < len(blocks_in) and blocks_in[j][0] == 'table':
                    inner += render_block(blocks_in[j][0], blocks_in[j][1], marks, charts); j += 1
                while j < len(blocks_in) and blocks_in[j][0] == 'source':
                    inner += render_block(blocks_in[j][0], blocks_in[j][1], marks, charts); j += 1
                buf.append(f'<div class="table-block">{inner}</div>')
                i = j
                continue
            buf.append(render_block(k, p, marks, charts))
            i += 1
        cls = 'chapter' + (' first' if idx == 0 else '')
        parts.append(f'<section class="{cls}">{"".join(buf)}</section>')

    head = f'''<header class="page-head">
  <img src="{data_uri(LOGO)}" alt="天台天信会计师事务所">
  <span>{esc(docno or '')}</span>
</header>'''

    cover_html = ''
    if cover:
        date_str = date or extract_date(md_text)
        title_pt = fit_font_pt(title or '', 27, 19)
        cover_html = f'''<section class="cover">
  <div class="cover-top">
    <img class="seal" src="{data_uri(SEAL)}" alt="">
    <div class="cn">天台天信会计师事务所</div>
    <div class="en">Tianxin Certified Public Accountants</div>
  </div>
  <div class="cover-mid">
    <div class="cover-title" style="font-size:{title_pt:.1f}pt">{esc(title or '')}</div>
  </div>
  <div class="cover-bottom">
    <div class="gold-rule"></div>
    <div class="docno">{esc(docno or '')}</div>
    <div class="date">{date_str}</div>
  </div>
</section>'''

    doc_pt = fit_font_pt(title or '', 24, 17)
    title_html = (f'<h1 class="doc-title" style="font-size:{doc_pt:.1f}pt">{esc(title)}</h1>'
                  if title else '')

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title or '天信报告')}</title>
<style>
{css_text}
</style>
</head>
<body>
{head}
<div class="doc">
{cover_html}
{title_html}
<div class="body">
{''.join(parts)}
</div>
</div>
</body>
</html>'''


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--docno', default=None)
    ap.add_argument('--cover', action='store_true')
    ap.add_argument('--marks', action='store_true')
    ap.add_argument('--date', default=None,
                    help='封面日期（如 "2026 年 6 月"）。不给则从正文抓「编制日期」')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--chapter-break', dest='cb', action='store_true', default=None,
                   help='强制每章另起一页（默认按体量自动判断：≥6 章且 ≥8000 字）')
    g.add_argument('--no-chapter-break', dest='cb', action='store_false',
                   help='强制连续排版，不按章分页')
    a = ap.parse_args()

    with open(a.input, encoding='utf-8') as f:
        md = f.read()
    with open(CSS, encoding='utf-8') as f:
        css = f.read()

    out = build(md, a.docno, a.cover, a.marks, css, date=a.date, chapter_break=a.cb)
    with open(a.output, 'w', encoding='utf-8') as f:
        f.write(out)
    kb = len(out.encode('utf-8')) / 1024
    print(f'✅ {a.output}  ({kb:.0f} KB, 单文件)')
    print(f'   封面 {"开" if a.cover else "关"} · 标记底色 {"开" if a.marks else "关"} · 章节 {out.count("<section class=\"chapter")}')
