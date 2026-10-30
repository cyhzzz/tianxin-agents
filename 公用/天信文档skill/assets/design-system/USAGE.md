# USAGE — Tianxin CPA Design System

> Agent-facing router. Read this before generating any artifact for the
> 天台天信会计师事务所 (Tianxin CPA) brand.

---

## 1. Where to start

Open `DESIGN.md` end-to-end. It is the **single source of truth** — every
decision (color, type, spacing, copy tone) is justified there with a *why*.

Open `tokens.css` second. The `:root` block is the **machine-readable
binding** of every DESIGN.md decision. Agents paste this block verbatim
into the first rule of their artifact's `<style>`, then reference every
value via `var(--name)`.

Open `design-tokens.json` for any tool that speaks W3C Design Tokens
(Storybook, Style Dictionary, design-token-cli).

Open `tailwind-v4.css` if the artifact is built with Tailwind v4. It
re-binds the tokens into `@theme` so utility classes (`bg-accent`,
`text-fg`, `p-4`) work out of the box.

Open `components.html` for the visual contract: button shapes, card
geometry, input focus, divider mark. Do not invent a new component — if
a need falls outside this file, escalate back to the human before
generating.

---

## 2. Hard rules (re-read before every artifact)

1. **Single logo asset.** Only `assets/logo.svg`. Dark scenes use
   `filter: brightness(0) invert(1);`. **Never** export to PNG/JPG and
   re-distribute.
2. **Radius is 0.** Every shape, every card, every button, every tag.
3. **Two golds per screen, max.** Pick the most important spot.
4. **Three weights, never four.** 400 / 500 / 600. `font-weight: 700`
   is a lint error.
5. **No indigo, no purple, no warm-pastel page bottoms.** `#6366f1`
   and family are auto-rejected.
6. **Tabular numerals everywhere money or year appears.** Set
   `font-variant-numeric: tabular-nums` on `body`.
7. **No emoji as icon.** Use mono-stroke SVG.
8. **Body 15px, never 14 or 16.** Noto Sans SC is metric-tuned around
   15 in this layout.

---

## 3. Typical artifact paste

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>天信 · {{ PAGE TITLE }}</title>
  <link rel="icon" type="image/svg+xml" href="./assets/logo.svg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600&family=Noto+Serif+SC:wght@400;600&display=swap"
    rel="stylesheet"
  />
  <style>
    /* Paste tokens.css :root here verbatim */
    :root {
      --bg: #ffffff;
      --surface: #f4f4f4;
      /* ...full block from tokens.css... */
    }
    body {
      font-family: var(--font-body);
      font-size: var(--text-base);
      line-height: var(--leading-body);
      color: var(--fg);
      background: var(--bg);
      font-variant-numeric: tabular-nums;
    }
  </style>
</head>
<body>
  <!-- Build with the components from components.html -->
</body>
</html>
```

---

## 4. What to escalate to the human

- New component shape not in `components.html` (modal, accordion, table).
- New color use not in `DESIGN.md §2` (third semantic, fourth brand
  hue, alternate dark surface).
- Any request for a PNG export of the logo. Refuse; explain the single-
  asset policy.
- Any request for emoji / icon set not already provided. Refuse unless
  the human supplies an SVG.
- Any request to add a `font-weight: 700` tier. Refuse; the system is
  3-weight.

---

## 5. Anti-slop checklist (run before submitting any artifact)

- [ ] No `#6366f1` or other indigo-family color anywhere in CSS.
- [ ] No `border-radius` ≥ 4px in computed styles.
- [ ] No `font-weight: 700` in any rule.
- [ ] No emoji in markup or copy.
- [ ] No more than 2 visible `--gold` (`#b8860b`) uses on the same
      scroll position.
- [ ] Body text ≥ 4.5:1 contrast against its background. (Brand
      defaults already pass.)
- [ ] Logo is `assets/logo.svg` only. No PNG / JPG copies in `assets/`.
- [ ] The 3px × 48px gold divider is present above every section
      title.
- [ ] `font-variant-numeric: tabular-nums` is set on `body`.
