#!/usr/bin/env python3
"""
Markdown → 天信网页长页报告（单文件 HTML，滚动阅读）

与 md2html 的分工：
  · md2html  → A4 分页，给打印/PDF
  · md2web   → 网页原生，给「发个链接让对方在手机/电脑上读」

两者共用同一套 Markdown 解析（parse_blocks），作者只写一份稿子。

用法：
  python md2web.py --input 报告.md --output 报告-web.html \
      [--docno "天信咨字〔2026〕第 012 号"] [--marks] [--no-toc]
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
import chart  # noqa: E402

SKILL = os.path.dirname(HERE)
CSS = os.path.join(SKILL, 'assets', 'web.css')
LOGO = os.path.join(SKILL, 'assets', 'brand', 'logo-horizontal-color.png')

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


def render_blocks(blocks, marks, toc, charts=None):
    out = []
    buf, i = [], 0
    while i < len(blocks):
        kind, payload = blocks[i]

        if kind == 'h2':
            sid = f'sec-{len(toc) + 1}'
            toc.append((sid, payload))
            out.append(f'<h2 id="{sid}">{esc(payload)}</h2>')
            i += 1
            continue

        if kind == 'caption':
            inner = f'<p class="table-title">{inline(payload, False)}</p>'
            j = i + 1
            while j < len(blocks) and blocks[j][0] == 'table':
                inner += render_table(blocks[j][1], marks)
                j += 1
            while j < len(blocks) and blocks[j][0] == 'source':
                inner += f'<p class="table-source">{inline(blocks[j][1], False)}</p>'
                j += 1
            out.append(f'<div class="table-block">{inner}</div>')
            i = j
            continue

        if kind == 'table':
            out.append(f'<div class="table-block">{render_table(payload, marks)}</div>')
            i += 1
            continue

        if kind == 'h1':
            i += 1
            continue

        out.append(render_one(kind, payload, marks, charts))
        i += 1
    return '\n'.join(x for x in out if x)


def render_table(payload, marks):
    header, rows = payload
    th = ''.join(f'<th>{inline(c, False)}</th>' for c in header)
    body = ''.join('<tr>' + ''.join(f'<td>{inline(c, marks)}</td>' for c in r) + '</tr>'
                   for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def render_one(kind, payload, marks, charts=None):
    if kind == 'h3':
        return f'<h3>{esc(payload)}</h3>'
    if kind == 'h4':
        return f'<h4>{esc(payload)}</h4>'
    if kind == 'p':
        m = re.fullmatch(r'@@CHART_(\d+)@@', payload.strip())
        if m and charts is not None:
            return chart.to_html(charts.get(int(m.group(1))), 'web')
        return f'<p>{inline(payload, marks)}</p>'
    if kind == 'quote':
        return f'<blockquote><p>{inline(payload, marks)}</p></blockquote>'
    if kind == 'code':
        lang, body = payload
        cls = f' class="language-{esc(lang)}"' if lang else ''
        return f'<pre class="code-block"><code{cls}>{html.escape(body, quote=False)}</code></pre>'
    if kind == 'hr':
        return '<hr>'
    if kind == 'list':
        items = []
        for lvl, marker, text in payload:
            style = f' style="margin-left:{lvl * 18}px"' if lvl else ''
            items.append(f'<li{style}>{inline(text, marks)}</li>')
        tag = 'ol' if payload and re.match(r'\d+', payload[0][1]) else 'ul'
        return f'<{tag}>' + ''.join(items) + f'</{tag}>'
    if kind == 'source':
        return f'<p class="table-source">{inline(payload, False)}</p>'
    if kind == 'image':
        alt, path = payload
        if not os.path.exists(path):
            return f'<p class="table-source">［缺图：{esc(alt or path)}］</p>'
        cap = f'<figcaption>{esc(alt)}</figcaption>' if alt else ''
        return f'<figure><img src="{data_uri(path)}" alt="{esc(alt)}" loading="lazy">{cap}</figure>'
    return ''


JS = r"""
(function () {
  var bar = document.querySelector('.progress');
  var top = document.querySelector('.to-top');
  var links = [].slice.call(document.querySelectorAll('.toc a'));
  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });

  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? h.scrollTop / max : 0;
    if (bar) bar.style.width = (p * 100).toFixed(1) + '%';
    if (top) top.classList.toggle('show', h.scrollTop > 700);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (top) top.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  if (links.length && 'IntersectionObserver' in window) {
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          if (current) current.classList.remove('active');
          var a = map[e.target.id];
          if (a) { a.classList.add('active'); current = a; }
        }
      });
    }, { rootMargin: '-88px 0px -72% 0px', threshold: 0 });
    document.querySelectorAll('.content h2[id]').forEach(function (h) { io.observe(h); });
  }
})();
"""


def build(md_text, docno=None, marks=False, toc_on=True, css_text=None):
    md_text, charts = chart.extract(md_text)
    blocks = parse_blocks(md_text)
    title = next((p for k, p in blocks if k == 'h1'), '')
    toc = []
    body = render_blocks([b for b in blocks if b[0] != 'pagebreak'], marks, toc, charts)

    nav = ''
    if toc_on and len(toc) > 1:
        items = ''.join(f'<a href="#{sid}">{esc(t)}</a>' for sid, t in toc)
        nav = f'<aside class="toc"><div class="toc-title">目录</div><nav>{items}</nav></aside>'

    meta_bits = []
    if docno:
        meta_bits.append(esc(docno))
    meta_bits.append(datetime.now().strftime('%Y 年 %m 月'))
    meta = ' · '.join(meta_bits)

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title or '天信报告')}</title>
<meta name="generator" content="天信文档与报告 skill">
<style>
{css_text}
</style>
</head>
<body>

<header class="topbar">
  <div class="topbar-inner">
    <img src="{data_uri(LOGO)}" alt="天台天信会计师事务所">
    <span class="docno">{esc(docno or '')}</span>
  </div>
  <div class="progress"></div>
</header>

<div class="layout">
  {nav}
  <main class="content">
    <h1 class="doc-title">{esc(title)}</h1>
    <div class="doc-meta">{meta}</div>
    {body}
  </main>
</div>

<footer class="doc-footer">
  <span>天台天信会计师事务所　TIANXIN CERTIFIED PUBLIC ACCOUNTANTS</span>
  <span>{esc(docno or '')}</span>
</footer>

<button class="to-top" aria-label="回到顶部">↑</button>
<script>{JS}</script>
</body>
</html>'''


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--docno', default=None)
    ap.add_argument('--marks', action='store_true')
    ap.add_argument('--no-toc', action='store_true')
    a = ap.parse_args()

    with open(a.input, encoding='utf-8') as f:
        md = f.read()
    with open(CSS, encoding='utf-8') as f:
        css = f.read()

    out = build(md, a.docno, a.marks, not a.no_toc, css)
    with open(a.output, 'w', encoding='utf-8') as f:
        f.write(out)
    kb = len(out.encode('utf-8')) / 1024
    n = out.count('<h2 id=')
    print(f'✅ {a.output}  ({kb:.0f} KB, 单文件)')
    print(f'   章节 {n} · 目录 {"有" if not a.no_toc else "无"} · 标记底色 {"开" if a.marks else "关"}')
