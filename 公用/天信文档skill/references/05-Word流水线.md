# Word 流水线：模板结构、实现细节、踩过的坑

## 为什么是「空壳模板 + 脚本填内容」

三条路都试过：

| 做法 | 问题 |
|---|---|
| `pandoc --reference-doc` | 页眉图片经常丢，依赖 pandoc 版本 |
| 拆包 → 改 XML → 打包 | `header1.xml.rels` 关系文件极易断链，图片锚定手工拼太脆 |
| `python-docx` 从零建文档 | 页眉页脚每次都要重写，样式散在代码里，改一次改十处 |

现在的做法：**先用脚本造一个空壳 docx（只有页面设置 + 页眉页脚 + 样式定义，正文为空），之后每份文档都从这个壳出发 —— 打开它、清空正文、保留 sectPr、往里写内容。**

好处是页眉 logo、页脚页码域、字号行距全在 docx 里，爸爸可以在 Word 里直接改样式，脚本一行不用动。样式改了之后所有新文档自动跟着变。

## 模板里有什么

三档一字排开，差别只在参数（`build_template.py` 的 `FORMATS`），流程完全一样。
参数全表见 `12-公文排版规格.md` 第七节，这里只说实现。

### 页面

| 档 | 上/下/左/右（mm） | 版心 |
|---|---|---|
| `plain` | 25/25/25/25 | 四边对称，过程稿不需要装订边 |
| `report` | 25/25/28/26 | 左多 2mm 是装订边 |
| `gongwen` | **37/35/28/26** | 156×225mm，GB/T 9704 §6.1 |

**公文那组不能改成「差不多」**：上 37 下 35 决定每页 22 行，左 28 右 26 决定每行
28 字，四个数一起构成版心 156×225。改一个，行数字数立刻不对。

### 样式表

| 样式名 | plain | report | gongwen |
|---|---|---|---|
| `Title` | 黑体 20pt 左 | 黑体 24pt 左 | **方正小标宋 22pt 居中** |
| `Heading 1` | 黑体 15pt | 黑体 18pt | **黑体 16pt + 缩进 2 字** |
| `Heading 2` | 黑体 13pt | 黑体 14pt | **楷体 16pt + 缩进 2 字** |
| `Heading 3` | 黑体 11.5pt | 黑体 11.5pt | 仿宋 16pt + 缩进 2 字 |
| `Normal` | 宋体 11pt / 1.5 | 宋体 10.5pt / 1.75 | **仿宋 16pt / 固定 28 磅** |
| `天信表题` | 宋体 10pt 黑 左 | 宋体 9pt 深蓝加粗 左 | **仿宋 14pt 黑 居中** |
| `天信来源` | 宋体 9pt 左 | 宋体 8pt 灰 左 | 仿宋 14pt 左 |
| `天信表格文字` | 宋体 10pt | 宋体 9pt | 仿宋 14pt |

中文正文用宋体（plain / report）、仿宋（gongwen），是印刷文档的保底选择。字号阶梯
24 / 18 / 14 / 11.5 / 10.5，相邻两级至少 1.2 倍，否则 Word 里看不出层级。

**公文那一列的三条是硬约束，不是样式偏好**：标题二号、层级一律缩进 2 字、正文固定
28 磅。国标里 `一、` 是正文段而不是「章标题」，所以它跟正文同一行距、段前段后为 0——
这一条最容易按咨询报告的习惯做错。

### 公文字体是探测出来的，不是写死的

`build_template.py --format gongwen` 会先跑 `check_fonts.py` 的探测，再决定往 docx
里写哪个字体名。原因：Word 的 `w:rFonts` **只能给一个名字**，没有 CSS 那种降级链。

```
正文   仿宋_GB2312（本机有）→ 仿宋（兼容名）
二级   楷体_GB2312（本机没有）→ 楷体
标题   方正小标宋简体（本机有）→ 华文中宋 → 宋体
```

跑的时候会打印走了哪一档，例如：

```
   正文: 仿宋_GB2312  [规范字体]
   二级标题: 楷体  [降级（兼容名）]
   标题: 方正小标宋简体  [规范字体]
```

强制切换：`--gb2312` / `--compat` / `--title-font 宋体`。

**注意 Windows 字体装在两个地方**：`C:/Windows/Fonts`（系统）与
`~/AppData/Local/Microsoft/Windows/Fonts`（用户自己装的）。只查前者会漏——
本机的方正小标宋与仿宋_GB2312 都在用户目录里，第一次就没查到，误判成「本机没有」。

### 页眉

**只有 `report` 档有页眉**：`[logo 图 40mm] TAB [报告编号 8pt 右对齐]`，段落下边框
0.5pt 深蓝。tab stop 设在 156mm（= 210 − 28 − 26，正好是版心宽度），右对齐。40mm
宽时 logo 整体高 6.96mm、其中中文高 3.04mm（约 8.6pt）——再小就认不出字，再大就顶到正文。

`plain` 与 `gongwen` 都不设。过程稿不需要品牌抬头；**公文的版头（红头、发文字号）
是首页要素，不是每页重复的页眉**——塞进页眉每页一次，是最常见的「像公文但不对」。

### 页脚

三档都要页码，但形态不同：

| 档 | 字号与颜色 | 位置 |
|---|---|---|
| `plain` | 9pt 灰 | 居中 |
| `report` | 8pt 灰 | 居中 |
| `gongwen` | **宋体 14pt 黑** | **单页右、双页左**（§7.3.5） |

一律用 `PAGE` 域不用手写数字，否则增删页后要全文重编。

公文那档要奇偶页不同，靠两个开关配合，缺一个都不生效：

```python
doc.settings.odd_and_even_pages_header_footer = True   # settings.xml 的 evenAndOddHeaders
fp  = sec.footer.paragraphs[0]        # 奇数页：右对齐
efp = sec.even_page_footer.paragraphs[0]   # 偶数页：左对齐（开关没开时它是 default 的副本）
```

实测：只设 `even_page_footer` 而不开 `evenAndOddHeaders`，两个页脚指向同一元素，
页码全在右边。

## 三个不好绕的技术点

### 一、OOXML 子元素顺序是强校验的

`<w:pPr>`、`<w:rPr>`、`<w:tcPr>`、`<w:tblPr>` 里面的子元素必须按 ECMA-376 规定的顺序排。`pBdr` 必须排在 `spacing` / `ind` / `jc` 之前，`shd` 必须排在 `sz` 之后。

直接 `parent.append(elm)` 塞到末尾，如果后面还有 `jc` 或 `tblLook`，顺序就错了。Word 的表现是：**要么提示「文件已损坏，是否修复」，要么静默丢掉这个属性**——你打开看没问题，客户打开就是错的。

python-docx 只给常用元素提供了 `get_or_add_*`，边框和底纹没有。所以 `docx_helpers.py` 里按官方 `_tag_seq` 自己实现了 `insert_ordered()`，插之前先删同名旧元素，再插到第一个 successor 前面。

`lint_docx.py` 里有一份同样的顺序表用来校验——**这类错误人眼绝对看不出来，只能机械查**。

### 二、三线表要手写边框

Word 的表格样式默认是全框线网格。事务所报告用三线表：表格上下各 1pt、表头下 0.5pt、其余全无。

`set_table_three_line()` 设 `tblBorders`（top/bottom 有，left/right/insideH/insideV 全 none），再逐格给表头单元格加 `tcBorders` 的 bottom。表头底色 `#F4F4F4` 走 `shd`。

注意 `tblBorders` 里 `insideH` 必须显式设成 `none`，只设 top/bottom 不管用——表格样式会把内部横线补回来。

### 三、清空正文要留下 sectPr

```python
def clear_body_keep_sectpr(doc):
    body = doc.element.body
    sectpr = body.find(qn('w:sectPr'))
    for child in list(body):
        body.remove(child)
    if sectpr is not None:
        body.append(sectpr)
```

`<w:sectPr>` 里存着页眉页脚引用和页面设置。把它一起删了，新文档就是一张白纸——没有 logo、没有页码、边距回到默认。

## 预览器踩的坑

本机没有 Word 也没有 LibreOffice，所以写了 `preview_docx.py` 把 docx 按样式参数还原成 A4 HTML 看版式。

**坑**：`<p style="font-family:"Microsoft YaHei",sans-serif">` —— `style` 属性的值用双引号包裹，值里又出现双引号，浏览器在第二个引号处就把属性截断了，**整条内联样式全部失效**，页面退化成一堆默认样式的 `<p>`。

症状很有欺骗性：文字还在、段落还在，看起来"像是排版了"，实际上字号、缩进、行距一个都没生效。第一版截图里主标题和章标题看起来差不多大，就是这个原因。

修法：CSS 值里的字体名一律用单引号。

## 改版式怎么改

改 `build_template.py` 顶部的 `FORMATS` 字典，然后重跑 `build_template.py`，所有由它生成的文档自动跟着变。

要改单个文档而不影响其他，就别改模板——在 Word 里手工调那份文档。

## 字体为什么不用思源

`references/00-品牌规范.md` 规定正文 Noto Sans SC，那是屏幕物料的标准。Word 文档的终点是客户电脑、政务系统、打印店，字体缺失会静默回退，行宽和分页全变。

所以印刷文档用：宋体正文 + 黑体标题 + Times New Roman 数字。品牌感靠颜色、留白、细线维持。

如果要给客户一份"有设计感"的 PDF，那走 B 轨（HTML → PDF），那里可以用思源。
