#!/usr/bin/env python3
"""
Markdown → 天信演示 deck（单文件 HTML，横向翻页）

一页一个结论。用 `---` 分页，`##` 是页标题（写成结论句，不是「经营情况分析」）。

页型自动判断：
  · 第一页                    → 封面
  · 只有标题、没有正文         → 章节幕
  · 含 :::kpi 块              → 数据页（大数字）
  · 含表格                    → 表格页
  · 含 > 引用且无其他内容      → 金句页
  · 其余                      → 要点页

:::kpi 语法（每行「值 | 标签」）：
  :::kpi
  4,820 万元 | 营业收入
  21.4% | 毛利率
  :::

用法：
  python md2deck.py --input 汇报.md --output 汇报-deck.html \
      [--docno "天信咨字〔2026〕第 012 号"] [--marks]
"""

import argparse
import base64
import html
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from md2docx import parse_blocks  # noqa: E402
from md2web import inline  # noqa: E402
import chart  # noqa: E402

SKILL = os.path.dirname(HERE)
CSS = os.path.join(SKILL, 'assets', 'deck.css')
LOGO = os.path.join(SKILL, 'assets', 'brand', 'logo-horizontal-color.png')
SEAL = os.path.join(SKILL, 'assets', 'brand', 'seal-mark-color.png')


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


def split_pages(md):
    """按 --- 切页，保留原始文本片段（:::kpi 块需要原始行）"""
    pages, cur = [], []
    for line in md.splitlines():
        if re.fullmatch(r'\s*---\s*', line):
            pages.append('\n'.join(cur)); cur = []
        else:
            cur.append(line)
    pages.append('\n'.join(cur))
    return [p for p in pages if p.strip()]


KPI_RE = re.compile(r':::kpi\s*\n(.*?)\n:::', re.S)


def parse_page(text, marks, charts=None):
    """返回 (页型, 标题, 内容 HTML, 页面附加信息)"""
    kpis = []
    def _take(m):
        rows = []
        for line in m.group(1).strip().splitlines():
            if '|' not in line:
                continue
            v, k = line.split('|', 1)
            rows.append((v.strip(), k.strip()))
        kpis.extend(rows)
        return ''
    body_text = KPI_RE.sub(_take, text)

    blocks = parse_blocks(body_text)
    h1 = next((p for k, p in blocks if k == 'h1'), None)
    h2 = next((p for k, p in blocks if k == 'h2'), None)
    title = h1 or h2 or ''
    rest = [(k, p) for k, p in blocks if k not in ('h1', 'h2')]

    has_table = any(k == 'table' for k, _ in rest)
    has_quote = any(k == 'quote' for k, _ in rest)
    n_rest = len([1 for k, _ in rest if k in ('p', 'list', 'table', 'quote', 'image')])

    if h1 and not h2:
        kind = 'cover'
    elif kpis:
        kind = 'kpi'
    elif n_rest == 0:
        kind = 'section'
    elif has_quote and n_rest <= 2:
        kind = 'quote'
    else:
        kind = 'content'

    return kind, title, rest, kpis


def render_rest(rest, marks, charts=None):
    out = []
    i = 0
    while i < len(rest):
        k, p = rest[i]
        if k == 'p':
            mm = re.fullmatch(r'@@CHART_(\d+)@@', p.strip())
            if mm and charts is not None:
                out.append(chart.to_html(charts.get(int(mm.group(1))), 'deck'))
            else:
                out.append(f'<p>{inline(p, marks)}</p>')
        elif k == 'list':
            items = []
            for lvl, marker, text in p:
                items.append(f'<li>{inline(text, marks)}</li>')
            tag = 'ol' if p and re.match(r'\d+', p[0][1]) else 'ul'
            out.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
        elif k == 'h3':
            out.append(f'<p><strong>{esc(p)}</strong></p>')
        elif k == 'h4':
            out.append(f'<p><strong>{esc(p)}</strong></p>')
        elif k == 'quote':
            out.append(f'<blockquote>{inline(p, marks)}</blockquote>')
        elif k == 'code':
            lang, body = p
            cls = f' class="language-{esc(lang)}"' if lang else ''
            out.append(f'<pre class="code-block"><code{cls}>'
                       f'{html.escape(body, quote=False)}</code></pre>')
        elif k == 'hr':
            out.append('<hr>')
        elif k == 'table':
            header, rows = p
            th = ''.join(f'<th>{inline(c, False)}</th>' for c in header)
            tb = ''.join('<tr>' + ''.join(f'<td>{inline(c, marks)}</td>' for c in r) + '</tr>'
                         for r in rows)
            out.append(f'<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>')
        elif k == 'source':
            out.append(f'<div class="table-note">{inline(p, False)}</div>')
        elif k == 'caption':
            out.append(f'<p class="table-note">{inline(p, False)}</p>')
        elif k == 'image':
            alt, path = p
            if os.path.exists(path):
                out.append(f'<figure><img src="{data_uri(path)}" alt="{esc(alt)}" '
                           f'style="max-width:100%;max-height:40vh;display:block">'
                           f'{"<figcaption class=table-note>" + esc(alt) + "</figcaption>" if alt else ""}</figure>')
        i += 1
    return '\n'.join(out)


JS = r"""
(function () {
  var track = document.querySelector('.track');
  var slides = [].slice.call(document.querySelectorAll('.slide'));
  var bar = document.querySelector('.hud-bar');
  var hint = document.querySelector('.hint');
  var index = document.querySelector('.index');
  var grid = document.querySelector('.index-grid');
  var i = 0, lastWheel = 0;

  function go(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    track.style.transform = 'translateX(' + (-i * 100) + '%)';
    bar.style.width = ((i + 1) / slides.length * 100) + '%';
  }

  function toggleIndex(show) {
    index.classList.toggle('show', show === undefined ? !index.classList.contains('show') : show);
  }

  // 索引格子
  slides.forEach(function (s, n) {
    var d = document.createElement('div');
    d.className = 'index-item';
    var t = s.getAttribute('data-title') || '(无标题)';
    d.innerHTML = '<span class="n">' + String(n + 1).padStart(2, '0') + '</span><b>' + t + '</b>';
    d.addEventListener('click', function () { go(n); toggleIndex(false); });
    grid.appendChild(d);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { toggleIndex(); return; }
    if (index.classList.contains('show')) return;
    if (['ArrowRight', 'PageDown', ' '].indexOf(e.key) >= 0) { e.preventDefault(); go(i + 1); }
    if (['ArrowLeft', 'PageUp'].indexOf(e.key) >= 0) { e.preventDefault(); go(i - 1); }
    if (e.key === 'Home') go(0);
    if (e.key === 'End') go(slides.length - 1);
  });

  window.addEventListener('wheel', function (e) {
    if (index.classList.contains('show')) return;
    var now = Date.now();
    if (now - lastWheel < 520) return;
    if (Math.abs(e.deltaY) < 12) return;
    lastWheel = now;
    go(i + (e.deltaY > 0 ? 1 : -1));
  }, { passive: true });

  var sx = 0, sy = 0;
  document.addEventListener('touchstart', function (e) {
    sx = e.touches[0].clientX; sy = e.touches[0].clientY;
  }, { passive: true });
  document.addEventListener('touchend', function (e) {
    var dx = e.changedTouches[0].clientX - sx;
    var dy = e.changedTouches[0].clientY - sy;
    if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy)) go(i + (dx < 0 ? 1 : -1));
  }, { passive: true });

  index.addEventListener('click', function (e) {
    if (e.target === index) toggleIndex(false);
  });

  setTimeout(function () { if (hint) hint.classList.add('hide'); }, 3200);
  go(0);
})();
"""


def build(md_text, docno=None, marks=False, css_text=None):
    md_text, charts = chart.extract(md_text)
    pages = split_pages(md_text)
    out, titles = [], []
    for n, ptext in enumerate(pages):
        kind, title, rest, kpis = parse_page(ptext, marks, charts)
        titles.append(title or f'第 {n + 1} 页')

        body = render_rest(rest, marks, charts)
        if kpis:
            cells = ''.join(
                f'<div class="kpi"><div class="v">{esc(v)}</div><div class="k">{esc(k)}</div></div>'
                for v, k in kpis)
            body = f'<div class="kpi-row">{cells}</div>' + body

        if kind == 'cover':
            sub = ''.join(f'<div>{inline(p, marks)}</div>' for k, p in rest if k == 'p')
            slide = f'''<section class="slide cover" data-title="{esc(title)}">
  <img class="seal" src="{data_uri(SEAL)}" alt="">
  <div class="org">天台天信会计师事务所</div>
  <div class="org-en">Tianxin Certified Public Accountants</div>
  <h1>{esc(title)}</h1>
  <div class="sub">{sub}</div>
  <div class="rule"></div>
</section>'''
        elif kind == 'section':
            slide = f'''<section class="slide section-slide" data-title="{esc(title)}">
  <div class="num">{n + 1:02d}</div>
  <h2>{esc(title)}</h2>
</section>'''
        else:
            cls = 'slide quote-slide' if kind == 'quote' else 'slide'
            foot = (f'<div class="slide-foot"><span>天台天信会计师事务所</span>'
                    f'<span class="no">{n + 1:02d} / {len(pages):02d}</span></div>')
            slide = f'''<section class="{cls}" data-title="{esc(title)}">
  <h2 class="slide-title">{esc(title)}</h2>
  <div class="slide-body">{body}</div>
  {foot}
</section>'''
        out.append(slide)

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titles[0] if titles else '天信演示')}</title>
<style>
{css_text}
</style>
</head>
<body>
<div class="stage">
  <div class="deck">
    <div class="track">
{''.join(out)}
    </div>
  </div>
</div>
<div class="hud"><div class="hud-bar"></div></div>
<div class="hint">← → 翻页　ESC 索引</div>
<div class="index">
  <h3>索引　共 {len(pages)} 页</h3>
  <div class="index-grid"></div>
</div>
<script>{JS}</script>
</body>
</html>'''


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--docno', default=None)
    ap.add_argument('--marks', action='store_true')
    a = ap.parse_args()

    with open(a.input, encoding='utf-8') as f:
        md = f.read()
    with open(CSS, encoding='utf-8') as f:
        css = f.read()

    out = build(md, a.docno, a.marks, css)
    with open(a.output, 'w', encoding='utf-8') as f:
        f.write(out)
    kb = len(out.encode('utf-8')) / 1024
    n = out.count('<section class="slide')
    print(f'✅ {a.output}  ({kb:.0f} KB, 单文件)')
    print(f'   共 {n} 页 · 标记底色 {"开" if a.marks else "关"}')
