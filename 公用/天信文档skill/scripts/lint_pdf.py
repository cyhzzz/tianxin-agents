#!/usr/bin/env python3
"""
PDF 机械自检 —— 查人眼抽查最容易漏掉的三件事

1. **半页空白**。一章内容太少、或者分页符用错位置，会在页底留出一大片白。
   抽看几页根本发现不了，而排版缺陷不是均匀分布的，它集中在最复杂的页。
   做法：每页渲成灰度图，算非白像素占比，低于阈值直接报页码。

2. **页码断档**。封面不编号、正文从 1 起是正常的；但出现「— 1 —」两次
   就说明合并或分页出了问题。

3. **图片丢失**。MD 里写了图、转换时路径不对，PDF 上就是一块空白。
   检查每页是否有图片对象。

用法：
  python lint_pdf.py 报告.pdf [--min-ink 0.06] [--allow-no-page-number 1]
退出码：0 通过；1 有问题
"""

import argparse
import re
import sys

import pymupdf


def page_ink(page, dpi=72):
    """非白像素占比。文字页一般 8%–25%，半页空白会掉到 3% 以下。"""
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    data = pix.samples
    total = len(data)
    if not total:
        return 0.0
    non_white = sum(1 for b in data if b < 240)
    return non_white / total


def content_fill(page, head_mm=45, foot_mm=25):
    """正文区里内容实际占的高度比例（0–1），排除页眉页脚。

    墨水占比会把「表格页」误判成空页——一张三线表全是白底和细线，
    墨水量天然低，但内容占满整页。所以要量「排到哪儿了」，不是「涂了多少」。
    """
    H = page.rect.height
    pt = 72 / 25.4
    lo, hi = head_mm * pt, H - foot_mm * pt
    ys = [b[3] for b in page.get_text('blocks') if b[1] >= lo and b[3] <= hi]
    for img in page.get_image_info():
        bb = img['bbox']
        if bb[1] >= lo and bb[3] <= hi:
            ys.append(bb[3])
    if not ys:
        return 0.0
    return max(0.0, min(1.0, (max(ys) - lo) / (hi - lo)))


def starts_with_chapter(page, min_size=15):
    """这一页的头一行是不是章标题（字号明显大于正文）"""
    blocks = sorted(page.get_text('dict')['blocks'], key=lambda b: b['bbox'][1])
    for b in blocks:
        if b.get('type') != 0:
            continue
        for line in b.get('lines', []):
            for span in line.get('spans', []):
                if span.get('text', '').strip():
                    return span.get('size', 0) >= min_size
    return False


class _Rep:
    """把 main 里的 issues/warns 两个列表包成 check_* 函数能用的接口"""
    def __init__(self, issues, warns):
        self.issues, self.warns = issues, warns
    def err(self, m): self.issues.append(m)
    def warn(self, m): self.warns.append(m)


def check_header_align(doc, rep):
    """页眉必须与版心对齐：logo 左缘 = 正文左缘，编号右缘 = 细线右缘。

    这条是踩坑换来的：headerTemplate 的容器从纸张边缘起算，logo 会默认顶到 0mm，
    而正文在 28mm —— 差 28mm，肉眼在小图上看不出来，印出来一眼就歪。
    """
    if doc.page_count < 2:
        return
    pg = doc[1]
    mm = 72 / 25.4

    logo_x0 = None
    for info in pg.get_image_info():
        logo_x0 = info['bbox'][0] / mm
        break

    body_x0 = None
    for blk in pg.get_text('blocks'):
        if blk[4].strip() and blk[0] / mm < 40:
            body_x0 = blk[0] / mm
            break

    rule_x1 = None
    for d in pg.get_drawings():
        r = d['rect']
        if r.width / mm > 100:          # 页眉那条横贯版心的细线
            rule_x1 = r.x1 / mm
            break

    no_x1 = None
    for blk in pg.get_text('blocks'):
        txt = blk[4]
        if ('号' in txt and len(txt) < 30) or '天信' in txt and '字' in txt:
            no_x1 = blk[2] / mm
            break

    if logo_x0 is None or body_x0 is None:
        rep.warn('页眉对齐：找不到 logo 或正文，跳过')
        return

    d1 = abs(logo_x0 - body_x0)
    print(f'  页眉 logo 左缘 {logo_x0:.1f}mm vs 正文左缘 {body_x0:.1f}mm（差 {d1:.1f}mm）')
    if d1 > 0.5:
        rep.err(f'页眉 logo 没有与正文左边距对齐，偏 {d1:.1f}mm')

    if rule_x1 is not None and no_x1 is not None:
        d2 = abs(rule_x1 - no_x1)
        print(f'  编号右缘 {no_x1:.1f}mm vs 细线右端 {rule_x1:.1f}mm（差 {d2:.1f}mm）')
        if d2 > 0.5:
            rep.warn(f'编号与页眉细线右端不对齐，差 {d2:.1f}mm')


def main(path, min_ink=0.06, skip_pages=0):
    doc = pymupdf.open(path)
    n = doc.page_count
    print(f'\n检查 {path}  ({n} 页)')

    issues, warns = [], []

    # 页码
    nums = []
    for i, page in enumerate(doc):
        txt = page.get_text() or ''
        m = re.search(r'—\s*(\d+)\s*—', txt)
        nums.append(int(m.group(1)) if m else None)

    body = [v for v in nums[skip_pages:] if v is not None]
    if body:
        expected = list(range(1, len(body) + 1))
        if body != expected:
            issues.append(f'页码不连续：实际 {body}，应为 {expected}')
        else:
            print(f'  ✓ 页码：正文 {len(body)} 页连续（1 → {body[-1]}）')
    if skip_pages and any(v is not None for v in nums[:skip_pages]):
        warns.append(f'封面/前置页出现了页码：{nums[:skip_pages]}')

    # 版面填充率：量「正文区排到哪儿了」，不量「涂了多少墨」。
    #
    # 墨水占比对表格密集的报告完全失效——一张三线表几乎全白，墨水量 3%，
    # 但内容占满一页。早先按墨水判，一份 26,000 字 / 41 张表的尽调报告
    # 被报出 22 页「偏空」，全是误报。
    #
    # 另外，章末页偏空是排版结果而不是错误：正式报告每章另起一页，
    # 最后一页写到一半是正常的。判据要能认出「这一页后面就是下一章」。
    print('  逐页内容填充率（正文区）：')
    thin, chapter_tail, last = [], [], n - 1
    for i, page in enumerate(doc):
        fill = content_fill(page)
        flag = ''
        is_tail = (i < last) and starts_with_chapter(doc[i + 1])
        if i >= skip_pages and fill < 0.35:
            if i == last:
                flag = '  ← 末页，内容自然收尾'
            elif is_tail:
                chapter_tail.append(i + 1)
                flag = '  ← 章末页（下一页是章标题）'
            elif fill < 0.12:
                thin.append(i + 1)
                flag = '  ← 几乎没有内容'
            else:
                chapter_tail.append(i + 1)
                flag = '  ← 偏空'
        print(f'    p{i+1:<2} {fill*100:5.0f}%{flag}')
    if thin:
        issues.append(f'以下页几乎没有内容（分页切得太碎）：{thin}')
    if chapter_tail:
        warns.append(f'章末页偏空（每章另起页的必然结果，非错误）：{chapter_tail}')

    # 页眉对齐
    check_header_align(doc, _Rep(issues, warns))

    # 图片
    no_img = []
    for i, page in enumerate(doc):
        if not page.get_images():
            no_img.append(i + 1)
    if no_img:
        warns.append(f'无图片的页：{no_img}（正文页通常如此，封面页无图要留意）')

    print()
    for w in warns:
        print(f'  ⚠ {w}')
    for e in issues:
        print(f'  ✗ {e}')
    if not issues:
        print('  ✅ 通过\n')
        return 0
    print(f'  ❌ {len(issues)} 个问题\n')
    return 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--min-ink', type=float, default=0.06)
    ap.add_argument('--skip-pages', type=int, default=1,
                    help='前置页数（封面/目录），这些页不做墨水量与页码检查')
    a = ap.parse_args()
    sys.exit(main(a.path, a.min_ink, a.skip_pages))
