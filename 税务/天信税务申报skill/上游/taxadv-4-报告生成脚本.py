#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""税务报告 Word 生成器

用法:
    python build_tax_report.py <content.json> <output.docx>

content.json 结构见 skill 的 SKILL.md「三、内容 JSON 结构」。
适用于税务合规审查报告、税务专业报告、年度企业所得税汇算清缴报告。
仅依赖 python-docx: pip install python-docx

退出码: 0 成功 / 1 参数或数据错误 / 2 缺少依赖
"""

import json
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:
    sys.stderr.write("缺少依赖 python-docx，请先执行: pip install python-docx\n")
    sys.exit(2)


HEI = "黑体"
SONG = "宋体"
LATIN = "Times New Roman"
GRAY = RGBColor(0x59, 0x59, 0x59)
CENTER = WD_ALIGN_PARAGRAPH.CENTER


class ReportError(Exception):
    """可预期的生成失败（读写异常等），由 main 转成友好提示，不输出 traceback。"""


# 生成过程中收集的数据问题（字段类型错误、缺失等），最后统一汇总提示。
# 由 main() 在每次运行开始时清空，避免多次调用累积。
ISSUES = []


def _issue(message):
    ISSUES.append(message)


def _text(value):
    """统一文本化：None 输出空串，避免报告里出现字面的 "None"。"""
    return "" if value is None else str(value)


def _preview(value, limit=30):
    """截断后的值预览，用于警告信息定位问题数据。"""
    text = _text(value).replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"


def _list_field(container, key, where):
    """安全取数组字段：非数组会被忽略并记录问题，避免逐字符迭代或直接崩溃。"""
    value = container.get(key)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    _issue("%s 的 %s 应为数组，已忽略：%s" % (where, key, _preview(value)))
    return []


def _as_level(value):
    """章节层级安全转换：非法值回退到 1，避免 int(None) 之类直接崩溃。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def set_font(run, cn_font=SONG, size=12.0, bold=False, color=None):
    """设置中英文字体，中文走 eastAsia。"""
    run.font.name = LATIN
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cn_font)
    rfonts.set(qn("w:ascii"), LATIN)
    rfonts.set(qn("w:hAnsi"), LATIN)


def add_para(doc, text, cn_font=SONG, size=12.0, bold=False, align=None,
             indent_chars=2, space_before=0, space_after=6, line_spacing=1.5,
             color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = line_spacing
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if indent_chars:
        pf.first_line_indent = Pt(size * indent_chars)
    if align is not None:
        p.alignment = align
    run = p.add_run(_text(text))
    set_font(run, cn_font, size, bold, color)
    return p


def add_section_heading(doc, text, level=1):
    size = 15.0 if level == 1 else 13.0
    return add_para(doc, text, cn_font=HEI, size=size, bold=True,
                    align=None, indent_chars=0, space_before=14, space_after=8,
                    line_spacing=1.5)


def add_table(doc, headers, rows):
    headers = [_text(h) for h in headers]
    if not headers:
        _issue("跳过一个无表头的表格（headers 缺失或为空），该表格内容未输出")
        return None

    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, head in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = CENTER
        p.paragraph_format.space_after = Pt(2)
        set_font(p.add_run(head), HEI, 10.5, True)

    for row in rows:
        if not isinstance(row, (list, tuple)):
            _issue("跳过格式错误的表格行（应为数组）：%s" % _preview(row))
            continue
        if len(row) > len(headers):
            _issue("表格行有 %d 个单元格，多于表头的 %d 列，多余内容已忽略：%s"
                   % (len(row), len(headers), _preview(row[0])))
        cells = table.add_row().cells
        for i in range(len(headers)):
            value = _text(row[i]) if i < len(row) else ""
            p = cells[i].paragraphs[0]
            p.alignment = CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(2)
            set_font(p.add_run(value), SONG, 10.5)

    add_para(doc, "", indent_chars=0, space_after=0, line_spacing=1.0)
    return table


def add_page_number_footer(doc):
    for section in doc.sections:
        footer = section.footer
        if footer.paragraphs:
            p = footer.paragraphs[0]
            if p.runs:
                # 该 footer 已写过页码（分节继承或重复调用），跳过以避免重复"第 X 页"
                continue
        else:
            p = footer.add_paragraph()
        p.alignment = CENTER
        set_font(p.add_run("第 "), SONG, 9)

        run = p.add_run()
        set_font(run, SONG, 9)
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = "PAGE"
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        run._element.append(begin)
        run._element.append(instr)
        run._element.append(end)

        set_font(p.add_run(" 页"), SONG, 9)


def setup_document(doc):
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.18)
        section.right_margin = Cm(3.18)

    try:
        normal = doc.styles["Normal"]
    except KeyError:
        _issue("文档模板缺少 Normal 样式，跳过默认字体设置")
        return
    normal.font.name = LATIN
    normal.font.size = Pt(12)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), SONG)
    rfonts.set(qn("w:ascii"), LATIN)
    rfonts.set(qn("w:hAnsi"), LATIN)


def build_cover(doc, data):
    for _ in range(4):
        add_para(doc, "", indent_chars=0, space_after=0, line_spacing=1.0)

    title = str(data.get("title") or "涉税事项报告")
    add_para(doc, title, cn_font=HEI, size=22, bold=True, align=CENTER,
             indent_chars=0, space_after=16, line_spacing=1.5)

    subtitle = data.get("subtitle")
    if subtitle:
        add_para(doc, subtitle, cn_font=SONG, size=14, align=CENTER,
                 indent_chars=0, space_after=10, line_spacing=1.5)

    for _ in range(2):
        add_para(doc, "", indent_chars=0, space_after=0, line_spacing=1.0)

    meta = data.get("meta")
    if meta is None:
        meta = {}
    elif not isinstance(meta, dict):
        _issue("meta 应为对象（键值对），已忽略：%s" % _preview(meta))
        meta = {}
    for key, value in meta.items():
        add_para(doc, "%s：%s" % (_text(key), _text(value)), cn_font=SONG, size=12,
                 align=CENTER, indent_chars=0, space_after=6, line_spacing=1.5)

    disclaimer = data.get("disclaimer")
    if disclaimer:
        add_para(doc, "", indent_chars=0, space_after=0, line_spacing=1.0)
        add_para(doc, disclaimer, cn_font=SONG, size=10.5, align=None,
                 indent_chars=0, space_after=6, line_spacing=1.4, color=GRAY)

    doc.add_page_break()


def build_sections(doc, sections):
    for index, section in enumerate(sections, 1):
        if not isinstance(section, dict):
            _issue("跳过第 %d 个章节（应为对象）：%s" % (index, _preview(section)))
            continue

        where = "第 %d 章" % index
        heading = section.get("heading")
        if heading:
            add_section_heading(doc, heading, _as_level(section.get("level", 1)))

        for para in _list_field(section, "paragraphs", where):
            add_para(doc, para)

        for table in _list_field(section, "tables", where):
            if not isinstance(table, dict):
                _issue("%s 中的一个表格不是对象，已跳过：%s" % (where, _preview(table)))
                continue
            if table.get("title"):
                add_para(doc, table["title"], cn_font=HEI, size=10.5, bold=True,
                         align=CENTER, indent_chars=0, space_before=6,
                         space_after=4, line_spacing=1.3)
            add_table(doc, _list_field(table, "headers", where),
                      _list_field(table, "rows", where))

        for item in _list_field(section, "bullets", where):
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing = 1.5
            pf.space_after = Pt(4)
            pf.left_indent = Pt(12)
            set_font(p.add_run("· " + _text(item)), SONG, 12)


def build(data, out_path):
    doc = Document()
    setup_document(doc)
    build_cover(doc, data)
    build_sections(doc, _list_field(data, "sections", "文档"))
    add_page_number_footer(doc)

    out_path = Path(out_path)
    if out_path.is_dir():
        raise ReportError("输出路径是目录而不是文件：%s" % out_path)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(out_path))
    except IsADirectoryError:
        raise ReportError("输出路径是目录而不是文件：%s" % out_path)
    except PermissionError:
        raise ReportError("输出文件被占用或无写入权限，请先关闭已打开的同名 Word 文档：%s" % out_path)
    except OSError as exc:
        raise ReportError("写入报告失败：%s（%s）" % (out_path, exc))
    return out_path


def _patch_stream_encoding():
    """避免中文符号（❌ / ⚠️）在 GBK 终端下写入 stderr 抛 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main():
    _patch_stream_encoding()
    ISSUES.clear()

    if len(sys.argv) != 3:
        sys.stderr.write("用法: python build_dd_report.py <content.json> <output.docx>\n")
        sys.exit(1)

    content_path, out_path = sys.argv[1], sys.argv[2]

    content_file = Path(content_path)
    # Windows 下对目录调用 read_text 抛的是 PermissionError，先显式判定以给出准确提示
    if content_file.is_dir():
        sys.stderr.write("❌ 内容路径是目录而不是文件: %s\n" % content_path)
        sys.exit(1)

    try:
        raw = content_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.stderr.write("❌ 内容文件不存在: %s\n" % content_path)
        sys.exit(1)
    except IsADirectoryError:
        sys.stderr.write("❌ 内容路径是目录而不是文件: %s\n" % content_path)
        sys.exit(1)
    except UnicodeDecodeError:
        sys.stderr.write("❌ 内容文件不是 UTF-8 编码，请另存为 UTF-8 后重试: %s\n" % content_path)
        sys.exit(1)
    except PermissionError:
        sys.stderr.write("❌ 没有读取权限: %s\n" % content_path)
        sys.exit(1)
    except OSError as exc:
        sys.stderr.write("❌ 读取内容文件失败: %s（%s）\n" % (content_path, exc))
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write("❌ 内容文件 JSON 格式错误: %s\n" % exc)
        sys.exit(1)

    if not isinstance(data, dict):
        sys.stderr.write("❌ 内容文件顶层必须是 JSON 对象（{...}），当前为 %s\n"
                         % type(data).__name__)
        sys.exit(1)

    if not data.get("sections"):
        sys.stderr.write("⚠️  警告: sections 为空，将只生成封面页\n")

    try:
        result = build(data, out_path)
    except ReportError as exc:
        sys.stderr.write("❌ %s\n" % exc)
        sys.exit(1)

    size_kb = result.stat().st_size / 1024
    print("✅ 报告已生成: %s (%.1f KB, %d 个章节)"
          % (result, size_kb, len(_list_field(data, "sections", "文档"))))

    if ISSUES:
        sys.stderr.write("⚠️  生成过程中发现 %d 处数据问题（已按可用信息尽力生成）：\n" % len(ISSUES))
        for item in ISSUES[:10]:
            sys.stderr.write("   - %s\n" % item)
        if len(ISSUES) > 10:
            sys.stderr.write("   - ...另有 %d 处同类问题\n" % (len(ISSUES) - 10))


if __name__ == "__main__":
    main()
