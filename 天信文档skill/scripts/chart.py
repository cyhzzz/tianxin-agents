#!/usr/bin/env python3
"""
天信图表库 —— 纯 Python 生成内联 SVG

不依赖 matplotlib：输出小、能直接内联进单文件 HTML、每个像素都可控。
matplotlib 的默认样式（图例框、去不掉的边距、字体回退）反而要花更多代码去对抗。

内置了 08-图表规范.md 里的三条硬规则，不靠作者自觉：
  · Y 轴永远从零开始（需要截断时必须显式传 truncate=True 并在图注里说明）
  · 负值画在零线下方，不是零高度
  · 一组数据不给成对柱

用法（在 Markdown 里）：
  :::chart bar
  caption: 木制工艺品占收入的 64.7%
  unit: 万元
  | 木制工艺品 | 3120 |
  | 竹藤制品 | 980 |
  :::

支持：bar（横条）/ column（竖柱）/ line（折线）/ grouped（成对柱）
"""

import html
import math
import re

# ── 配色（与 report.css / web.css 一致）──────────────────
NAVY = '#1D3A5E'
NAVY_LIGHT = '#5B7CA6'
GOLD = '#B8860B'
DANGER = '#DA1E28'
GRID = '#E8E8E8'
AXIS = '#C9C9C9'
TEXT = '#525252'
FG = '#161616'
FILL_MUTED = '#D9D9D9'

FONT = "'Noto Sans SC','Microsoft YaHei','PingFang SC',sans-serif"

# 估算中文字宽：一个汉字 ≈ 1em，一个西文字符 ≈ 0.55em
def _tw(s, size):
    n_cjk = sum(1 for ch in s if ord(ch) > 0x2E80)
    n_other = len(s) - n_cjk
    return n_cjk * size + n_other * size * 0.55


def _fmt(v, unit=''):
    """数值格式化：千分位，最多两位小数，负号用真正的减号"""
    if isinstance(v, str):
        return v
    av = abs(v)
    if av >= 1000:
        s = f'{av:,.0f}' if av == int(av) else f'{av:,.2f}'
    elif av >= 10:
        s = f'{av:.0f}' if av == int(av) else f'{av:.1f}'
    else:
        s = f'{av:.2f}'.rstrip('0').rstrip('.') if av != int(av) else f'{av:.0f}'
    return ('−' if v < 0 else '') + s + (unit or '')


def _nice_ticks(vmin, vmax, n=4):
    """取整刻度。返回 (ticks, lo, hi)"""
    if vmax == vmin:
        vmax = vmin + 1 if vmin >= 0 else vmin + abs(vmin) * 0.5 + 1
    span = vmax - vmin
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if step >= raw:
            break
    lo = math.floor(vmin / step) * step
    hi = math.ceil(vmax / step) * step
    ticks = []
    v = lo
    while v <= hi + step * 0.001:
        ticks.append(round(v, 10))
        v += step
    return ticks, lo, hi


def _svg_open(w, h):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" '
            f'style="font-variant-numeric:tabular-nums">')


def _empty(w=680, h=120, msg='无数据'):
    return (f'{_svg_open(w, h)}<text x="{w/2}" y="{h/2}" text-anchor="middle" '
            f'font-size="13" fill="{TEXT}">{msg}</text></svg>')


# ── 横条 ─────────────────────────────────────────────────

def bar(rows, unit='', w=680, highlight=None, value_inside=False):
    rows = [(str(k), float(v)) for k, v in rows if str(k) != '']
    if not rows:
        return _empty()

    pad_l = max(_tw(k, 13) for k, _ in rows) + 18
    pad_l = min(max(pad_l, 70), w * 0.38)
    pad_r = 78
    bar_h, gap = 30, 14
    top, bot = 12, 16
    h = top + len(rows) * bar_h + (len(rows) - 1) * gap + bot

    vmax = max(v for _, v in rows)
    vmin = min(0, min(v for _, v in rows))
    ticks, lo, hi = _nice_ticks(vmin, vmax, 4)
    plot_w = w - pad_l - pad_r

    def x(v):
        return pad_l + (v - lo) / (hi - lo) * plot_w

    out = [_svg_open(w, h)]

    # 竖向网格
    for t in ticks:
        gx = x(t)
        out.append(f'<line x1="{gx:.1f}" y1="{top-4}" x2="{gx:.1f}" y2="{h-bot}" '
                   f'stroke="{GRID}" stroke-width="1"/>')

    # 零线（有负值时才显眼）
    if vmin < 0:
        zx = x(0)
        out.append(f'<line x1="{zx:.1f}" y1="{top-4}" x2="{zx:.1f}" y2="{h-bot}" '
                   f'stroke="{AXIS}" stroke-width="1.4"/>')

    for i, (k, v) in enumerate(rows):
        y = top + i * (bar_h + gap)
        x0, x1 = (x(0), x(v)) if v >= 0 else (x(v), x(0))
        color = GOLD if (highlight and k == highlight) else (DANGER if v < 0 else NAVY)
        out.append(f'<rect x="{x0:.1f}" y="{y}" width="{max(x1-x0, 1.5):.1f}" '
                   f'height="{bar_h}" fill="{color}"/>')
        # 类别名
        out.append(f'<text x="{pad_l-10}" y="{y+bar_h/2+4.5:.1f}" text-anchor="end" '
                   f'font-size="12.5" fill="{FG}">{html.escape(k)}</text>')
        # 数值
        label = _fmt(v, unit)
        if v >= 0:
            out.append(f'<text x="{x1+8:.1f}" y="{y+bar_h/2+4.5:.1f}" font-size="12.5" '
                       f'fill="{FG if not highlight or k != highlight else GOLD}">{label}</text>')
        else:
            out.append(f'<text x="{x0-8:.1f}" y="{y+bar_h/2+4.5:.1f}" text-anchor="end" '
                       f'font-size="12.5" fill="{DANGER}">{label}</text>')

    out.append('</svg>')
    return ''.join(out)


# ── 竖柱 ─────────────────────────────────────────────────

def column(rows, unit='', w=680, h=None, highlight=None, color=None, truncate=False):
    rows = [(str(k), float(v)) for k, v in rows if str(k) != '']
    if not rows:
        return _empty()
    h = h or 300
    pad_l, pad_r = 56, 16
    pad_t, pad_b = 22, 40
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    vmax = max(v for _, v in rows)
    vmin = min(v for _, v in rows)
    if truncate and vmin > 0:
        # 轴从数据附近起算，不是从零。下方会画断裂标记。
        _, _, hi = _nice_ticks(vmin, vmax, 3)
        ticks, lo, hi = _nice_ticks(vmin * 0.92, vmax, 3)
        lo = max(lo, 0)
        ticks = [t for t in ticks if t >= lo]
        if lo not in ticks:
            ticks = [lo] + ticks
    else:
        ticks, lo, hi = _nice_ticks(min(0, vmin), vmax, 4)

    def y(v):
        return pad_t + (hi - v) / (hi - lo) * plot_h

    out = [_svg_open(w, h)]

    for t in ticks:
        gy = y(t)
        out.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w-pad_r}" y2="{gy:.1f}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pad_l-8}" y="{gy+4:.1f}" text-anchor="end" font-size="11" '
                   f'fill="{TEXT}">{_fmt(t)}</text>')

    base = y(0) if lo <= 0 <= hi else y(lo)
    out.append(f'<line x1="{pad_l}" y1="{base:.1f}" x2="{w-pad_r}" y2="{base:.1f}" '
               f'stroke="{AXIS}" stroke-width="1.2"/>')

    # 截断标记：轴底画一道折线，避免读者误以为从零开始
    if truncate and lo > 0:
        yy = pad_t + plot_h
        out.append(f'<path d="M{pad_l-13},{yy-4} l5,5 l5,-5" fill="none" '
                   f'stroke="{DANGER}" stroke-width="1.3"/>')
        # 文字放右上角，避免和 Y 轴刻度挤在一起
        out.append(f'<text x="{w-pad_r}" y="{pad_t-8}" text-anchor="end" font-size="10" '
                   f'fill="{DANGER}">纵轴自 {_fmt(lo)} 起，未从零开始</text>')

    n = len(rows)
    slot = plot_w / n
    bw = min(slot * 0.52, 56)
    for i, (k, v) in enumerate(rows):
        cx = pad_l + slot * (i + 0.5)
        y0, y1 = (y(v), base) if v >= 0 else (base, y(v))
        c = color or (GOLD if (highlight and k == highlight) else (DANGER if v < 0 else NAVY))
        out.append(f'<rect x="{cx-bw/2:.1f}" y="{y0:.1f}" width="{bw:.1f}" '
                   f'height="{max(y1-y0,1.5):.1f}" fill="{c}"/>')
        ty = y0 - 6 if v >= 0 else y1 + 14
        out.append(f'<text x="{cx:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="11.5" '
                   f'fill="{FG}">{_fmt(v, unit)}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-pad_b+18}" text-anchor="middle" font-size="11.5" '
                   f'fill="{TEXT}">{html.escape(k)}</text>')

    out.append('</svg>')
    return ''.join(out)


# ── 折线 ─────────────────────────────────────────────────

def line(series, w=680, h=None, unit='', area=False):
    """series: [(name, [(x_label, value), ...]), ...]"""
    if not series:
        return _empty()
    h = h or 300
    pad_l, pad_r, pad_t, pad_b = 56, 24, 24, 40
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    allv = [v for _, pts in series for _, v in pts]
    if not allv:
        return _empty()

    # 量级差检测：不同量纲的指标画一根轴，小量级那条会被压成贴底的直线。
    # 双 Y 轴是更糟的解法（能拼出任意相关性），正确做法是拆图或指数化。
    warn = ''
    if len(series) > 1:
        spans = []
        for _, pts in series:
            vs = [v for _, v in pts]
            spans.append(max(vs) - min(vs) if len(vs) > 1 else 0)
        nz = [x for x in spans if x > 0]
        if len(nz) > 1 and max(nz) > 5 * min(nz):
            warn = ('两个系列量级相差 %.0f 倍，建议拆成两张图或指数化（基期=100）'
                    % (max(nz) / min(nz)))
    ticks, lo, hi = _nice_ticks(min(0, min(allv)), max(allv), 4)
    if warn:
        pad_t += 16
    xs = [p[0] for p in series[0][1]]
    n = max(len(xs) - 1, 1)

    def X(i):
        return pad_l + plot_w * (i / n if n else 0)

    def Y(v):
        return pad_t + (hi - v) / (hi - lo) * plot_h

    out = [_svg_open(w, h)]
    if warn:
        out.append(f'<text x="{pad_l}" y="12" font-size="10.5" fill="{DANGER}">'
                   f'{warn}</text>')

    for t in ticks:
        gy = Y(t)
        out.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w-pad_r}" y2="{gy:.1f}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pad_l-8}" y="{gy+4:.1f}" text-anchor="end" font-size="11" '
                   f'fill="{TEXT}">{_fmt(t)}</text>')

    for i, lab in enumerate(xs):
        out.append(f'<text x="{X(i):.1f}" y="{h-pad_b+18}" text-anchor="middle" font-size="11.5" '
                   f'fill="{TEXT}">{html.escape(str(lab))}</text>')

    palette = [NAVY, GOLD, NAVY_LIGHT, DANGER]
    for si, (name, pts) in enumerate(series):
        c = palette[si % len(palette)]
        d = ' '.join(f'{"M" if i == 0 else "L"}{X(i):.1f},{Y(v):.1f}'
                     for i, (_, v) in enumerate(pts))
        if area:
            d2 = d + f' L{X(len(pts)-1):.1f},{Y(lo):.1f} L{X(0):.1f},{Y(lo):.1f} Z'
            out.append(f'<path d="{d2}" fill="{c}" opacity="0.08"/>')
        out.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2" '
                   f'stroke-linejoin="round" stroke-linecap="round"/>')
        for i, (_, v) in enumerate(pts):
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3" fill="#fff" '
                       f'stroke="{c}" stroke-width="2"/>')
        # 末端标数值（08 规范：名字和数字一次给全）
        last_v = pts[-1][1]
        out.append(f'<text x="{X(len(pts)-1)+8:.1f}" y="{Y(last_v)+4:.1f}" font-size="11.5" '
                   f'fill="{c}" font-weight="500">{_fmt(last_v, unit)}</text>')

    # 多系列时图上方给极简键（纯圆点 + 文字，无图例框）
    if len(series) > 1:
        x = pad_l
        for si, (name, _) in enumerate(series):
            c = palette[si % len(palette)]
            out.append(f'<circle cx="{x+4}" cy="{pad_t-10}" r="4" fill="{c}"/>')
            out.append(f'<text x="{x+14}" y="{pad_t-6}" font-size="11.5" fill="{TEXT}">'
                       f'{html.escape(name)}</text>')
            x += _tw(name, 11.5) + 34

    out.append('</svg>')
    return ''.join(out)


# ── 成对柱 ───────────────────────────────────────────────

def grouped(rows, names, w=680, h=None, unit=''):
    """rows: [(label, v1, v2), ...]；names: (系列1名, 系列2名)"""
    rows = [r for r in rows if r and r[0] != '']
    if not rows:
        return _empty()
    h = h or 300
    pad_l, pad_r, pad_t, pad_b = 56, 16, 34, 44
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    allv = [float(v) for r in rows for v in r[1:3]]
    ticks, lo, hi = _nice_ticks(min(0, min(allv)), max(allv), 4)

    def Y(v):
        return pad_t + (hi - v) / (hi - lo) * plot_h

    out = [_svg_open(w, h)]
    for t in ticks:
        gy = Y(t)
        out.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w-pad_r}" y2="{gy:.1f}" '
                   f'stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{pad_l-8}" y="{gy+4:.1f}" text-anchor="end" font-size="11" '
                   f'fill="{TEXT}">{_fmt(t)}</text>')

    base = Y(0)
    out.append(f'<line x1="{pad_l}" y1="{base:.1f}" x2="{w-pad_r}" y2="{base:.1f}" '
               f'stroke="{AXIS}" stroke-width="1.2"/>')

    # 键：纯几何点 + 文字，无框
    colors = [NAVY, GOLD]
    x = pad_l
    for i, nm in enumerate(names[:2]):
        out.append(f'<circle cx="{x+4}" cy="{pad_t-16}" r="4" fill="{colors[i]}"/>')
        out.append(f'<text x="{x+14}" y="{pad_t-12}" font-size="11.5" fill="{TEXT}">'
                   f'{html.escape(nm)}</text>')
        x += _tw(nm, 11.5) + 30

    slot = plot_w / len(rows)
    bw = min(slot * 0.28, 34)
    for i, r in enumerate(rows):
        cx = pad_l + slot * (i + 0.5)
        for j in range(2):
            v = float(r[j + 1])
            bx = cx - bw - 2 if j == 0 else cx + 2
            y0, y1 = (Y(v), base) if v >= 0 else (base, Y(v))
            out.append(f'<rect x="{bx:.1f}" y="{y0:.1f}" width="{bw:.1f}" '
                       f'height="{max(y1-y0,1.5):.1f}" fill="{colors[j]}"/>')
            ty = y0 - 5 if v >= 0 else y1 + 13
            out.append(f'<text x="{bx+bw/2:.1f}" y="{ty:.1f}" text-anchor="middle" '
                       f'font-size="10.5" fill="{FG}">{_fmt(v, unit)}</text>')
        out.append(f'<text x="{cx:.1f}" y="{h-pad_b+20}" text-anchor="middle" font-size="11.5" '
                   f'fill="{TEXT}">{html.escape(str(r[0]))}</text>')

    out.append('</svg>')
    return ''.join(out)


# ── Markdown 块解析 ──────────────────────────────────────

CHART_RE = re.compile(r':::chart\s+(\w+)\s*\n(.*?)\n:::', re.S)

CHART_KINDS = ('bar', 'column', 'line', 'grouped')


def _parse_block(body):
    """解析图表块：头部 key: value + Markdown 表格"""
    meta, rows, series = {}, [], []
    lines = body.splitlines()
    i = 0
    in_table = False
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.lstrip().startswith('|'):
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
                i += 1
                continue
            rows.append(cells)
            in_table = True
            i += 1
            continue
        m = re.match(r'^([a-zA-Z_]+)\s*:\s*(.+)$', ln)
        if m and not in_table:
            meta[m.group(1).lower()] = m.group(2).strip()
        i += 1
    return meta, rows


def _numeric_rows(rows, ncol=2):
    """跳过非数字行（作者常顺手写表头，不该因此报错）"""
    out = []
    for r in rows:
        if len(r) < ncol:
            continue
        try:
            vals = [float(str(c).replace(',', '').replace('−', '-')) for c in r[1:ncol]]
        except ValueError:
            continue
        out.append((r[0], *vals))
    return out


def build(kind, body):
    """返回 SVG 字符串"""
    meta, rows = _parse_block(body)
    unit = meta.get('unit', '')
    hl = meta.get('highlight')
    w = int(meta.get('width', 680))
    h = int(meta['height']) if 'height' in meta else None

    try:
        if kind == 'bar':
            return bar(_numeric_rows(rows, 2), unit=unit, w=w, highlight=hl)
        if kind == 'column':
            return column(_numeric_rows(rows, 2), unit=unit, w=w, h=h, highlight=hl,
                          truncate=str(meta.get('truncate', '')).lower() in ('1', 'true', 'yes'))
        if kind == 'line':
            if not rows:
                return _empty()
            head = rows[0] if len(rows[0]) > 1 and not _isnum(rows[0][1]) else None
            body_rows = [r for r in (rows[1:] if head else rows) if len(r) >= 2]
            if not body_rows:
                return _empty()
            labels = [r[0] for r in body_rows]
            nseries = len(body_rows[0]) - 1
            sers = []
            for j in range(nseries):
                nm = head[j + 1] if head and j + 1 < len(head) else f'系列{j+1}'
                pts = [(labels[i], float(body_rows[i][j + 1].replace(',', '').replace('−', '-')))
                       for i in range(len(body_rows)) if len(body_rows[i]) > j + 1]
                sers.append((nm, pts))
            return line(sers, w=w, h=h, unit=unit, area=bool(meta.get('area')))
        if kind == 'grouped':
            names = (meta.get('series1', '本期'), meta.get('series2', '上期'))
            return grouped(_numeric_rows(rows, 3), names, w=w, h=h, unit=unit)
    except (ValueError, IndexError) as e:
        return _empty(msg=f'图表数据有误：{e}')
    return _empty(msg=f'不支持的图型：{kind}')


def _isnum(s):
    try:
        float(str(s).replace(',', ''))
        return True
    except ValueError:
        return False




# ── 与三条 HTML 轨道对接 ─────────────────────────────────

def build_block(kind, body):
    """返回 {svg, caption, source}，供渲染器包装"""
    meta, _ = _parse_block(body)
    return {
        'svg': build(kind, body),
        'caption': meta.get('caption', ''),
        'source': meta.get('source', ''),
        'unit': meta.get('unit', ''),
    }


def to_html(item, variant='report'):
    """包装成 HTML。variant 决定 class 名，样式在各自 css 里"""
    if not item:
        return ''
    cap = (f'<div class="chart-caption">{html.escape(item["caption"])}</div>'
           if item['caption'] else '')
    src = (f'<div class="chart-source">{html.escape(item["source"])}</div>'
           if item['source'] else '')
    return f'<figure class="chart chart-{variant}">{cap}{item["svg"]}{src}</figure>'


def extract(md):
    """把 :::chart 块抽出来换成占位符，返回 (新 md, {序号: item})"""
    charts = {}

    def _sub(m):
        idx = len(charts)
        kind = m.group(1).lower()
        if kind in CHART_KINDS:
            charts[idx] = build_block(kind, m.group(2))
        else:
            charts[idx] = {'svg': _empty(msg=f'未知图型 {kind}'), 'caption': '', 'source': ''}
        return f'@@CHART_{idx}@@'

    return CHART_RE.sub(_sub, md), charts
