# Source Evidence — Tianxin CPA Design System Extraction

> Documented on 2026-06-26. The brand tokens and component patterns in
> this design system were extracted from the production Tianxin CPA
> website (`tianxin-cpa.cn`) and the firm's internal materials.

---

## 1. Source sites scanned

| Source | Type | Role |
| --- | --- | --- |
| `tianxin-cpa.cn` (production) | Live marketing site | Color palette, typography, component geometry, copy voice |
| `tianxin-cpa-website-gh-pages/` | Static export of the above | The exact CSS `tokens.css` style block (the `index-*.css` bundle) |
| 内部 brand deck (referenced) | Print PDFs, report cover templates | Section-divider use, dark-hero treatment, tabular numerals in financial reports |

The bundled CSS in the GH-Pages export (`assets/index-*.css`) was the
primary token source. It declares the full `:root` block for the brand
on a Tailwind v4 / shadcn-style cascade. The `scanned.html` file in
this folder is the trimmed HTML from the GH-Pages export.

---

## 2. Tokens extracted (verbatim, from the source CSS `:root`)

```css
--brand-navy:        #00338D;
--brand-blue:        #0F62FE;
--brand-sky:         #4589FF;
--brand-gold:        #B8860B;
--brand-gold-hover:  #D4A017;
--brand-ice:         #F4F4F4;

--bg:                #FFFFFF;
--fg:                #161616;
--muted:             #F4F4F4;
--muted-fg:          #525252;
--border:            #E0E0E0;
--border-hover:      #E8E8E8;

--success:           #24A148;
--warning:           #B8860B;   /* reuses brand gold */
--danger:            #DA1E28;
--info:              #0F62FE;   /* reuses brand blue */

--hero-bg:           #161616;
--hero-fg:           #FFFFFF;
--hero-border:       #262626;

--font-sans:  "Noto Sans SC", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
--font-serif: "Noto Serif SC", "Source Han Serif SC", Georgia, "Times New Roman", STSong, SimSun, serif;

--radius: 0;  /* global sharp-corner commitment */
```

> Full source block in `source/scanned.html` (the original `<style>`
> extract) and `source/tokens.source.json` (machine-readable mirror).

---

## 3. Mapping decisions (where source name ≠ OD canonical)

The source brand uses `--brand-*` prefix. The OD `TOKEN_SCHEMA` reserves
plain `--bg / --fg / --accent / --radius-*` etc. The mapping applied in
`tokens.css`:

| Source | OD canonical | Notes |
| --- | --- | --- |
| `--brand-navy` | `--accent-deep` (B-slot) | Static authority. Not the action color. |
| `--brand-blue` | `--accent` (A1) | Primary action. The CTA fill. |
| `--brand-sky`  | `--accent-sky` (B-slot) | Secondary link / hover highlight. |
| `--brand-gold` | `--gold` (A1) | Authority stamp. Also bound to `--warn`. |
| `--brand-gold-hover` | `--gold-hover` (A2) | Gold hover state. |
| `--brand-ice` | `--surface` (A1) | Soft card field. |
| `--bg` / `--fg` / `--border` | unchanged | A1 identity. |
| `--muted-fg` | `--fg-2` (A1) | Secondary text. |
| `--border-hover` | `--border-soft` (B-slot) | Card hover field. |
| `--hero-bg` / `--hero-fg` / `--hero-border` | inline-bound in components | Dark scene only. Not exported as global tokens (over-allocates). |

The `--brand-blue-hover` does not exist in the source; the source
pattern is `--brand-navy` (rest) → `--brand-blue` (hover) → press
returns to navy. We replicate that rhythm in `--accent` /
`--accent-hover` / `--accent-active`.

---

## 4. Component extraction

Six source-side component patterns were captured:

1. **`.pill-btn`** (primary / outline / gold) — the firm's button
   language. Backing fields: `transition: background` only, no
   `transform` on hover. We bind this to `.btn / .btn-primary /
   .btn-outline / .btn-gold` in `components.html`.

2. **`.service-card`** — 1px border, 0 radius, 32px padding, hover
   background `--border-hover`. No shadow. Binds to `.card` in
   `components.html`.

3. **`.tag` / `.tag-blue` / `.tag-gold` / `.tag-navy`** — 4×12
   padding, 0 radius, 12px text. Binds to `.tag` family in
   `components.html`.

4. **`.form-field input`** — 1px border, 0 radius, 40px tall, 2px
   focus ring at `--brand-blue`. Binds to `.field input / .field
   textarea` in `components.html`.

5. **`.section-divider`** — 48px × 3px gold bar. The "印章感"
   signature. Binds to `.divider` in `components.html`.

6. **`.hero` / `.site-footer`** — `#161616` dark surface, white
   text, gold `h5` in footer columns, gold 创立年份 stat in hero.
   Binds to `.hero` / `.footer` in `components.html`.

---

## 5. Decisions we did NOT preserve

- **PNG logo variants.** The source folder shipped 4 PNG variants
  (`logo_dark.png`, `logo_hori_full.png`, `logo_modern.png`,
  `logo_seal.png`) — all generated at fixed resolutions. We
  rejected this asset model and ship **only `logo.svg`**, with dark
  scenes produced via CSS filter. Single-asset policy.
- **Inter as display.** The source CSS lists Inter in the
  `--font-sans` fallback chain. We bind `--font-display` to Noto
  Serif SC for any display context, so the chain naturally
  surfaces Chinese serif first.

---

## 6. Confidence

- All 7 brand hex values: **high** (sourced from the compiled
  production CSS, not from a screenshot).
- All neutral / semantic hex values: **high** (same).
- All OKLch conversions: **high** (mathematical from the hex).
- All component geometry: **high** (sourced from the compiled
  CSS, confirmed by manual HTML inspection).
- All copy patterns (recommended vs forbidden): **medium-high**
  (sourced from the brand-spec prose, cross-checked with the live
  site's published copy).
- Gold-budget rule (≤2 per screen): **high** (inferred from
  visual audit + confirmed by the brand-spec prose "印章感" rule).
