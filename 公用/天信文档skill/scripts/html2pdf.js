/**
 * HTML → PDF（A4）
 *
 * 两个绕不开的点：
 *
 * 1. 页码只能靠 Chromium 的 footerTemplate。CSS 的 counter(page) 在
 *    Chromium 里对分页元素不生效，硬写会在每页印同一个数字。
 *
 * 2. 页眉必须走 headerTemplate，不能用 position:fixed —— 打印时 fixed
 *    是相对「页面内容区」定位而不是纸张，top:12mm 会落进正文第一行，
 *    把标题压住。
 *
 * 3. 封面不能带页眉，但 headerTemplate 是全局的。所以分两趟渲染
 *    （封面一趟、正文一趟），再用 pypdf 合并。
 *
 * 用法：
 *   node html2pdf.js 报告.html 报告.pdf --docno "天信咨字〔2026〕第 012 号" \
 *        [--cover] [--logo 路径]
 */
const EMPTY_HDR = '<div></div>';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

/* Playwright 的安装位置随机器变（全局 npm / 局部 node_modules / 用户目录），
   写死绝对路径换台机器就崩——原来这里就是写死的。按顺序找，全找不到才报错。 */
function loadPlaywright() {
  const tries = [
    'playwright',
    /* npm 全局装的位置：node.exe 同级的 node_modules（WorkBuddy 自带的 node 就是这种布局） */
    path.join(path.dirname(process.execPath), 'node_modules', 'playwright'),
    path.join(process.env.APPDATA || '', 'npm', 'node_modules', 'playwright'),
    path.join(process.env.LOCALAPPDATA || '', 'npm', 'node_modules', 'playwright'),
    path.join(__dirname, '..', 'node_modules', 'playwright'),
  ];
  for (const c of tries) {
    if (!c) continue;
    try { return require(c); } catch (e) { /* 换下一个 */ }
  }
  throw new Error(
    '未找到 playwright。装一次即可：npm i -g playwright\n' +
    '   浏览器可复用已下载的 ~/AppData/Local/ms-playwright（设 PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1）');
}
const { chromium } = loadPlaywright();

/* Playwright 版本与已下载的浏览器版本对不上时会直接崩（新装 playwright 要
   chromium_headless_shell-1248，本机只有 1208）。把「找一个能用的 Chromium」
   做成回退链，比让每个人去 npx playwright install 一次省事。 */
function findChromiumExe() {
  const base = path.join(process.env.LOCALAPPDATA || '', 'ms-playwright');
  try {
    const dirs = fs.readdirSync(base).filter(d => d.startsWith('chromium-')).sort().reverse();
    for (const d of dirs) {
      for (const sub of ['chrome-win64', 'chrome-win', 'chrome-linux']) {
        const p = path.join(base, d, sub, sub.startsWith('chrome-win') ? 'chrome.exe' : 'chrome');
        if (fs.existsSync(p)) return p;
      }
    }
  } catch (e) { /* 目录不存在就走系统浏览器 */ }
  for (const p of [
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  ]) {
    if (fs.existsSync(p)) return p;
  }
  return null;
}

async function launchBrowser() {
  try {
    return await chromium.launch();
  } catch (e) {
    const exe = findChromiumExe();
    if (!exe) throw e;
    console.log('   ⚠ Playwright 自带浏览器不可用，改用 ' + exe);
    return await chromium.launch({ executablePath: exe });
  }
}

const argv = process.argv.slice(2);
const input = argv[0];
const output = argv[1];
const flag = (name) => argv.includes(name);
const opt = (name, dflt) => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
};

if (!input || !output) {
  console.error('用法: node html2pdf.js 输入.html 输出.pdf [--docno ...] [--cover] [--format report|gongwen]');
  process.exit(1);
}

const docno = opt('--docno', '');
const hasCover = flag('--cover');
/* 版式：report 咨询报告 / gongwen 正式公文（GB/T 9704）。
   两档的差别只有三处：页边距、页眉有无、页码字号——版式本体在 CSS 里。
   公文页眉留空：版头（红头）是首页要素，不能塞进每页页眉重复。 */
const fmt = opt('--format', 'report');
const isGw = fmt === 'gongwen';
const logoPath = opt('--logo', path.join(__dirname, '..', 'assets', 'brand', 'logo-horizontal-color.png'));
const MARGIN = isGw
  ? { top: '37mm', bottom: '35mm', left: '28mm', right: '26mm' }  /* 版心 156×225mm */
  : { top: '45mm', bottom: '25mm', left: '26mm', right: '26mm' };
/* 封面没有页眉，不需要给页眉让出 45mm，用自己的上边距 */
const COVER_MARGIN = { top: '25mm', bottom: '25mm', left: '26mm', right: '26mm' };

function dataUri(p) {
  return 'data:image/png;base64,' + fs.readFileSync(p).toString('base64');
}

const logoUri = fs.existsSync(logoPath) ? dataUri(logoPath) : '';

/* headerTemplate 画在纸张上，但**不吃 page margin 的缩进** ——
   Chromium 给它的容器从纸张左边缘起算（实测 logo 落在 0mm），要用 margin 退回版心。

   布局只能用 table：这个渲染上下文里 flex 的 space-between 不生效、calc() 被忽略、
   position:absolute 的包含块也不对，编号统统会挤在 logo 旁边。
   只有表格会老老实实分配列宽。

   也不能用 padding 缩进：border-bottom 画在 padding box 外沿，细线会拉满整张纸。 */
/* headerTemplate 画在纸张上，但**不吃 page margin 的缩进**：Chromium 给它的
   容器从纸张左边缘起算（实测 logo 落在 0mm），所以要用 margin 退回版心。

   布局用 table + **固定列宽**：td 宽度不给值时会收缩到内容宽度，
   text-align:right 就没有多余空间可对齐，编号会紧贴 logo 后面。
   40mm + 116mm = 156mm，正好是版心宽度（210 - 28 - 26）。
   flex / calc / absolute 在这个渲染上下文里都不可靠，只有表格的固定列宽管用。 */
const headerTpl = `<div style="margin:21mm 26mm 0 28mm;">
  <table style="border-collapse:collapse;">
    <tr>
      <td style="width:40mm;border-bottom:0.5pt solid #1D3A5E;padding:0 0 1.5mm 0;vertical-align:bottom;">
        <img src="${logoUri}" style="width:40mm;display:block;">
      </td>
      <td style="width:116mm;border-bottom:0.5pt solid #1D3A5E;padding:0 0 1.5mm 0;
        text-align:right;vertical-align:bottom;font-size:8pt;color:#525252;
        font-family:'Noto Serif SC',SimSun,serif;">${docno}</td>
    </tr>
  </table>
</div>`;

const footerTpl = `<div style="width:100%;text-align:center;font-size:8pt;color:#525252;
  font-family:'Noto Serif SC',SimSun,serif;">— <span class="pageNumber"></span> —</div>`;

/* 公文页码：宋体四号 14pt，纯黑，一字线夹页码（GB/T 9704 §7.3.5）。
   ⚠ Chromium 打印没有奇偶页概念，footerTemplate 是全局的，做不到「单页右、双页左」。
     这里统一居中。要严格单右双左只能走 Word 轨——那边的 gongwen 页脚做到了。 */
const footerTplGw = `<div style="width:100%;text-align:center;font-size:14pt;line-height:1.2;
  font-family:'SimSun','宋体',serif;color:#000000;">— <span class="pageNumber"></span> —</div>`;

const EMPTY = '<div></div>';

(async () => {
  const browser = await launchBrowser();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('requestfailed', r => errors.push('资源缺失: ' + r.url().slice(0, 80)));

  const url = 'file:///' + path.resolve(input).replace(/\\/g, '/');
  await page.goto(url);
  await page.waitForTimeout(400);

  const tmpDir = path.dirname(path.resolve(output));
  const base = path.basename(output, '.pdf');

  const pdfOpts = (hdr, ftr, mg) => ({
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: hdr,
    footerTemplate: ftr || footerTpl,
    margin: mg || MARGIN,
  });

  const parts = [];

  if (hasCover) {
    // 封面：藏起正文，并解除 cover 的强制分页（否则只剩它时也会多出一张空白页）
    await page.addStyleTag({ content: `
      .chapter, .doc-title, .body { display: none !important; }
      .cover { break-after: auto !important; page-break-after: auto !important; }
      .page-head { display: none !important; }
    ` });
    const coverPdf = path.join(tmpDir, `_${base}-cover.pdf`);
    await page.pdf({ path: coverPdf, ...pdfOpts(EMPTY, EMPTY, COVER_MARGIN) });
    parts.push(coverPdf);
    await page.reload();
    await page.waitForTimeout(300);
    // 正文：藏起封面
    await page.addStyleTag({ content: '.cover { display: none !important; }' });
  }

  const bodyPdf = path.join(tmpDir, `_${base}-body.pdf`);
  await page.pdf({
    path: bodyPdf,
    ...pdfOpts(isGw ? EMPTY_HDR : headerTpl, isGw ? footerTplGw : null, MARGIN),
  });
  parts.push(bodyPdf);

  const info = await page.evaluate(() => ({
    imgs: Array.from(document.images).length,
    chapters: document.querySelectorAll('.chapter').length,
  }));

  await browser.close();

  // 合并
  if (parts.length > 1) {
    const args = ['-c', `
import sys
from pypdf import PdfWriter
w = PdfWriter()
for p in sys.argv[1:-1]:
    w.append(p)
w.write(sys.argv[-1])
w.close()
print('merged', len(sys.argv) - 2)
`, ...parts, path.resolve(output)];
    const py = execFileSync('python', args, { encoding: 'utf8' });
    console.log('   ' + py.trim());
    parts.forEach(p => fs.unlinkSync(p));
  } else {
    fs.renameSync(parts[0], output);
  }

  console.log(`✅ ${output}`);
  console.log(`   章节 ${info.chapters} · 图片 ${info.imgs} · 封面 ${hasCover ? '有' : '无'}`);
  if (errors.length) console.log('   ⚠ ' + errors.join('\n   ⚠ '));
})();
