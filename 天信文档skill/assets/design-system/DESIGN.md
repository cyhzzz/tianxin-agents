# Design System — Tianxin CPA (天台天信会计师事务所)

> Category: Finance & Professional Services
> 浙江省台州市天台县本土会计师事务所 · 创立于 2001-04-17 · 二十四载执业经验。
> 这是一份「机构感优先」的克制设计系统：navy 为骨、亮蓝为动、金色为睛；方、稳、准。

---

## 1. Visual Theme & Atmosphere

The Tianxin brand reads as **institutional, restrained, and quietly authoritative** — a twenty-four-year-old local accounting firm should not look like a 2020 SaaS landing page, and it should not look like a cold law firm either. The visual gravity sits between the two: more polished than a 2001 storefront, more grounded than a 2024 startup.

The grammar is **IBM-Carbon-adjacent navy + bright blue, with one disciplined gold accent** and a hard **0-radius** commitment. Every visible edge is a hairline, every shape is a rectangle, every chromatic decision is rationed. The system rewards stillness over decoration: the eye should never be told where to look twice.

Across the full surface set (官网、审计报告封面、宣传册、社交卡片、合同封皮、名片) the rules hold:

- **Color**: 4 brand hues only — navy (#00338D), bright blue (#0F62FE), sky (#4589FF), gold (#B8860B). Neutrals are pure steps of gray. Semantics reuse gold for warning.
- **Geometry**: Zero radius, everywhere. Buttons, cards, tags, inputs, avatars. Sharpness is the signature.
- **Type**: Noto Sans SC body. Noto Serif SC strictly for the 印章 / 引言 / 报告扉页 register.
- **Logo**: One file (`logo.svg`). Dark-mode treatment is `filter: brightness(0) invert(1);` — no second asset.
- **Accent discipline**: Gold appears at most twice per visible screen, and only as a section divider or single highlighted datum.

**Key characteristics:**

- Binary section rhythm: pale ice / white field → near-black hero/footer (`#161616`).
- Single gold accent family used as a "stamp of authority" — never as a button fill, never as a link color.
- 0-radius system: sharpness = formality = contract-safety.
- Tabular numerals everywhere money or year appears (`font-variant-numeric: tabular-nums`).
- Three-weight type system (400/500/600). `font-weight: 700` is forbidden globally.
- Single SVG logo; dark-scene variant produced via CSS filter, not a second file.
- Card design is border-led, not shadow-led. 1px `--border` plus white space does the work.

---

## 2. Color Palette & Roles

### Brand
- **Brand Navy** (`#00338D` / `oklch(30.5% 0.155 264)`): Static authority. Page header band, primary CTAs, dark-mode foreground text. Stays the brand's anchor color.
- **Brand Blue** (`#0F62FE` / `oklch(54% 0.225 257)`): Action color. Primary CTA fill, focus ring, link color. Lifts to `--brand-blue` on hover from navy.
- **Brand Sky** (`#4589FF` / `oklch(63% 0.180 257)`): Secondary link / hover highlight. Lower-luminance step of the blue family.
- **Brand Gold** (`#B8860B` / `oklch(63% 0.130 80)`): Authority stamp. Section dividers, 创立年份, important figures. **Capped at ≤2 visible uses per screen.**
- **Brand Gold Hover** (`#D4A017` / `oklch(70% 0.150 80)`): Gold hover state. Slight luminance lift, no hue change.
- **Brand Ice** (`#F4F4F4` / `oklch(95% 0 0)`): Soft surface. Card fields, neutral backgrounds. Stands in for white without competing with it.

### Neutrals & Surface
- **Page White** (`#FFFFFF`): Default page background.
- **Ink Black** (`#161616` / `oklch(15% 0 0)`): Primary text. ≈ 18.7:1 against white.
- **Mid Gray** (`#525252` / `oklch(40% 0 0)`): Secondary text, helper copy, captions.
- **Hairline Gray** (`#E0E0E0` / `oklch(89% 0 0)`): Default border, divider, card edge.
- **Hairline Hover** (`#E8E8E8` / `oklch(91% 0 0)`): Card hover state. The only `hover` background in the neutral family.

### Semantic
- **Success** (`#24A148` / `oklch(60% 0.180 145)`): Audit pass, payment received, status "完成".
- **Warning** (`#B8860B` / `oklch(63% 0.130 80)`): Reuses brand gold. "待处理" / "需补充" / "过期".
- **Danger** (`#DA1E28` / `oklch(58% 0.220 25)`): Audit failure, risk flagged, destructive action.
- **Info** (`#0F62FE` / `oklch(54% 0.225 257)`): Reuses brand blue. Informational copy, secondary link.

### Hero / Dark Variants
- **Hero BG** (`#161616`): Dark hero and footer background. Pure ink.
- **Hero FG** (`#FFFFFF`): Text on dark scenes. Pure white.
- **Hero Border** (`#262626`): Hairline on dark scenes. Sits one stop above hero-bg.

### Color usage rules
- **One gold per scene, max two.** Section dividers, single highlighted year, 重要数字 — pick two, not three.
- **No purple.** `#6366f1` and any indigo-leaning hue is forbidden. No purple-to-blue gradient backgrounds.
- **No decorative glow.** No `filter: blur()` blob, no radial highlight behind text, no warm beige / peach / pink page bottoms.
- **Contrast**: Body text ≥ 4.5:1 (true, ≥ 12.6:1), UI elements ≥ 3:1. We never have to check at run time because the palette is pre-validated.

---

## 3. Typography Rules

### Font families
- **Sans (primary)**: `Noto Sans SC` — metric-stable Simplified Chinese sans, the institutional choice. Fallback chain: `Inter → -apple-system → "Segoe UI" → "PingFang SC" → "Microsoft YaHei"`.
- **Serif (decorative)**: `Noto Serif SC` — only used for hero 引言, 报告扉页, 印章-style stamps, and large quote treatments. Never for body.
- **Mono (numerals & code)**: `ui-monospace, "JetBrains Mono", "SF Mono", Menlo, Consolas`. Tabular numerals on via `font-variant-numeric: tabular-nums` as the page default — every digit is the same width.

### Type scale (px)
| Token | Size | Line | Use |
| --- | --- | --- | --- |
| `--text-display` | 56 | 1.05 | Hero / report cover title |
| `--text-headline` | 32 | 1.15 | Section title |
| `--text-title` | 22 | 1.30 | Card title, sub-section title |
| `--text-body` | 15 | 1.50 | Body copy, paragraph |
| `--text-label` | 14 | 1.40 | UI label, button, nav |
| `--text-small` | 12 | 1.50 | Caption, fine print, eyebrow |

> Body 15px is deliberate — not 14, not 16. It is the metric center of Noto Sans SC at the desktop read distance, and the only size that lets a single column hold 32 Chinese characters at the chosen 65ch measure.

### Weight (3-step, never 4)
| Token | Value | Use |
| --- | --- | --- |
| `--weight-regular` | 400 | Body, contract terms, paragraphs |
| `--weight-medium`  | 500 | UI label, button, nav |
| `--weight-semibold`| 600 | Title, emphasis, key figure |

**`font-weight: 700` is globally forbidden.** Bold is not a 强调 tool in this system.

### Tracking
- **Display / headline (≥ 32px)**: `letter-spacing: -0.02em` to `-0.03em`. Tightening.
- **Body (15px)**: `letter-spacing: 0`. Default.
- **Small (≤ 13px)**: `letter-spacing: 0.01em`. Slight open.
- **UI label / uppercase eyebrow**: `letter-spacing: 0.06em–0.08em`. Even spacing.

### Line length
- Body: `max-width: 65ch` (≈ 32 Chinese characters).
- No `text-align: justify` — rivers and orphans break the institutional tone.

---

## 4. Geometry & Layout

### Spacing (8-point grid)
| Token | Value | Use |
| --- | --- | --- |
| `--space-xs`   |  8px | Tight element spacing |
| `--space-sm`   | 12px | Label padding |
| `--space-md`   | 16px | Default spacing |
| `--space-lg`   | 24px | Block padding |
| `--space-xl`   | 32px | Block-to-block spacing |
| `--space-2xl`  | 40px | Section inner padding |
| `--space-3xl`  | 48px | Large block separator |
| `--space-4xl`  | 64px | Section spacing |
| `--space-5xl`  | 80px | Page-level separator |

### Radius — the brand signature
```css
--radius: 0;
```
**Every radius is 0.** Buttons, cards, tags, inputs, avatars, modals. The "方" (square) is the brand's most recognizable decision. A rounded version is a 5-second red flag that an AI generated the asset.

### Containers
- Page max width: 1280px desktop.
- Section padding: 80px top / bottom, 24px left / right.
- Grid: 12 columns.
- Breakpoints: 640 / 768 / 1024 / 1280 (sm / md / lg / xl).

### Elevation
- **Card**: no shadow. `1px var(--border)` hairline + spacing does the work.
- **Popover / modal**: `0 8px 24px rgba(0, 0, 0, 0.12)`. The only sanctioned shadow tier.

---

## 5. Logo System

### The single asset
| File | Format | Use |
| --- | --- | --- |
| `assets/logo.svg` | SVG (vector) | 全品牌唯一交付物 |

**No PNG, no JPG, no second variant.** The dark-scene version is generated via CSS:

```css
.logo-dark { filter: brightness(0) invert(1); }
```

Avoids the version-drift problem entirely — one file, one source of truth, every screen in sync.

### Size & clearance
- **Page / card hero use**: width ≥ 120px.
- **Page header**: width ≥ 32px.
- **Favicon / avatar**: 16 / 32 / 48px (rasterized from the same SVG at use time).
- **Clear space**: 0.5× logo height on every side. No element may enter.

### Forbidden
- ❌ No stretch, compress, skew, rotate, recolor.
- ❌ No drop shadow, outline, or other filter.
- ❌ No low-contrast background.
- ❌ No extracting the "天信" wordmark for separate use.
- ❌ **No re-exporting as PNG / JPG for distribution.**

---

## 6. Components

### Buttons (4 variants, 1 geometry)
| Variant | Background | Text | Border | Use |
| --- | --- | --- | --- | --- |
| `primary`   | `--brand-navy`        | `#fff` | none   | Primary CTA |
| `primary:hover` | `--brand-blue`    | `#fff` | none   | Hover |
| `gold`      | `--brand-gold`        | `#fff` | none   | 关键行动（预约咨询） |
| `gold:hover`| `#D4A017`             | `#fff` | none   | Hover |
| `outline`   | transparent           | `--brand-blue` | `1px solid --brand-blue` | Secondary |
| `ghost`     | transparent           | `--fg` | `1px solid --border` | Tertiary |
| `dark-outline` | transparent        | `#fff` | `1px solid rgba(255,255,255,0.4)` | On hero / footer |

- Padding: `14px 32px` (12-32 base unit).
- Weight 600. Size 14px. Tracking 0.02em. Radius 0.
- Hover: background-color change only. **No lift, no scale, no shadow.**
- One primary action per screen, max 3 in any action group.

### Cards (service card)
- `1px var(--border)` outline. Radius 0. **No shadow.**
- Inner padding 32px. Title 22px / 600. Body 15px / 400.
- Hover background: `--border-hover` (`#E8E8E8`). No transform.
- Card-to-card gap: 24px.

### Tags / Chips
| Variant | Text | Background |
| --- | --- | --- |
| `tag-navy` | `--brand-navy` | `#EDF5FF` |
| `tag-blue` | `--brand-blue` | `#EDF5FF` |
| `tag-gold` | `--brand-gold` | `#FEF7E0` |

- Padding `4px 12px`. Radius 0. Size 12px. Weight 400. Tracking 0.32px.
- Tags are 业务类型 / 行业 / 状态 标签. They are **never** used as the only element on a CTA.

### Inputs
- `1px var(--border)` outline. Radius 0. Height 40px. Padding `0 12px`.
- Focus: `2px --brand-blue` outline + `2px` offset.
- Placeholder: `--muted-fg`.

### Section divider
```css
.section-divider {
  width: 48px;
  height: 3px;
  background: var(--brand-gold);
}
```
Above every section title. Gold 3px × 48px bar — the "印章感" signature that ties the system together.

---

## 7. Voice & Copy

- Tone: restrained, professional, factual. **No** marketing-fluff superlatives ("最强", "全网第一", "极致").
- Second-person: 您, not 你.
- Short sentences. Subject-verb-object clear.
- Action: 立即咨询 / 获取方案. **Avoid** 马上试试 / 戳我一下.
- Numbers: always `1,286,500.00` (千分位 + 两位小数). 报告场景额外使用 大写金额栏.

---

## 8. Dark Mode

Default mode is light. Dark is reserved for:
- Hero (always `#161616` background).
- Footer.
- 报告扉页 / 合同封皮 / 名片背面 (optional).

In dark mode:
- Background `#161616` ↔ `#FFFFFF`.
- Text `#FFFFFF` ↔ `#161616`.
- Border `#262626` ↔ `#E0E0E0`.
- Soft surface `#262626` ↔ `#F4F4F4`.
- Brand colors (navy, blue, gold) unchanged.
- Logo: same SVG, `filter: brightness(0) invert(1)`.

---

## 9. Anti-slop Rules (Lint Gates)

The system is self-enforcing. The following patterns are auto-rejected:

- ❌ Indigo (`#6366f1` etc.) as primary or link color.
- ❌ Purple-to-blue gradient backgrounds.
- ❌ Any `border-radius` ≥ 4px.
- ❌ Emoji (✨🚀🎯⚡🔥💡) as icon or decoration — use mono-stroke SVG.
- ❌ Rounded card with a colored left bar.
- ❌ Decorative glow, blurred background, blob SVG, warm beige / peach / pink page bottoms.
- ❌ More than 2 visible `--brand-gold` uses per screen.
- ❌ Font size ≤ 11px (smallest allowed is 12px).
- ❌ `font-weight: 700` anywhere.
- ❌ Inter / Roboto / Arial as the only display face (must pair with Noto Serif SC).
- ❌ "+" / "..." in titles; "10× faster" / "99.9% uptime" without source.

---

## 10. How to Import (Open Design Quickstart)

1. **Copy this folder** (`tianxin-cpa/`) anywhere on disk.
2. In Open Design, open **Design Systems → Import**, point to the folder.
3. The picker validates `manifest.json` against `od-design-system-project/v1` and reads `tokens.css` as the canonical token source.
4. In any artifact, paste the `:root` block from `tokens.css` as the first rule of `<style>`. Then reference everything via `var(--name)`.
5. Use `assets/logo.svg` (or copy it into your artifact's `assets/`). Never export it to PNG for re-distribution.
