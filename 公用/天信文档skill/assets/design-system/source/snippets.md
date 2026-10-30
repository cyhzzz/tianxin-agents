# Source Snippets — Tianxin CPA

> Curated excerpts from the source CSS / HTML that drove specific
> design decisions in this system. Kept for traceability.

---

## 1. The original `:root` block (verbatim)

From `tianxin-cpa-website-gh-pages/assets/index-B-jeETty.css`, the
`--font-family` declaration is followed by the brand's full
`--brand-*` and structural `--bg / --fg / --border` declarations,
plus the geometry commitment:

```css
--font-family:"Noto Sans SC", "Inter", -apple-system, BlinkMacSystemFont,
              "Segoe UI", "Helvetica Neue", Arial, sans-serif;
--font-serif:"Noto Serif SC", Georgia, "Times New Roman", serif;
--font-size-display:3.5rem;   /* 56px */
--font-size-headline:2rem;    /* 32px */
--font-size-title:1.375rem;   /* 22px */
--font-size-body:.9375rem;    /* 15px */
--font-size-label:.875rem;    /* 14px */
--font-size-small:.75rem;     /* 12px */
...
--brand-navy:#00338d; --brand-blue:#0f62fe; --brand-sky:#4589ff;
--brand-gold:#b8860b; --brand-gold-hover:#d4a017; --brand-ice:#f4f4f4;
--bg:#fff; --fg:#161616; --muted:#f4f4f4; --muted-foreground:#525252;
--border:#e0e0e0; --input:#e0e0e0; --ring:#0f62fe;
--primary:#00338d; --primary-foreground:#fff;
--accent:#b8860b; --accent-foreground:#161616;
--destructive:#da1e28;
--radius:0px;
--hero:#161616; --hero-foreground:#fff;
```

The source exposes `--accent: #b8860b` (the gold) — but in practice,
CTAs use `--brand-navy` / `--brand-blue`. We treat `--accent` in the
source as a misnomer and re-bind the canonical OD `--accent` to
`--brand-blue` (#0F62FE) in `tokens.css`. Gold moves to the dedicated
`--gold` slot.

---

## 2. Button geometry (the `.pill-btn` class)

```css
.pill-btn {
  transition: background var(--duration-normal) var(--ease-default),
              color var(--duration-normal) var(--ease-default);
  cursor: pointer;
  font-weight: 600;
  font-size: var(--font-size-label);
  letter-spacing: .02em;
  border-radius: 0;
  padding: .75rem 2rem;
  line-height: 1.5;
}
.pill-btn:hover { transform: none; }
.pill-btn-primary { background: var(--brand-navy); color: #fff; }
.pill-btn-primary:hover { background: var(--brand-blue); }
.pill-btn-gold { background: var(--brand-gold); color: #fff; }
.pill-btn-gold:hover { background: #d4a017; }
```

Key observations:
- `border-radius: 0` is **declared explicitly** on the button, not
  inherited from a global reset. The author wanted the rule
  visible at the call site.
- `:hover` swaps background only. **No `transform`, no
  `box-shadow`, no `translate`.**
- `transition-property` is limited to `background` and `color` —
  no other property animates.

---

## 3. Card geometry (the `.service-card` class)

```css
.service-card { transition: background var(--duration-normal) var(--ease-default); border: none; }
.service-card:hover { background: #e8e8e8; }
```

The card is actually a `border: none` on the source side — the
visible 1px border is drawn by the parent grid line, not by the
card itself. We replicate this in `components.html` by giving the
card an explicit `border: 1px solid var(--border)` so the
component is self-contained when used outside the source grid.

---

## 4. Section divider (the `.section-divider` class)

```css
.section-divider {
  background: var(--brand-gold);
  border-radius: 0;
  width: 48px;
  height: 3px;
}
```

The `border-radius: 0` is declared even though the divider is a
rectangle with no `border-radius` to set. The author wanted the
sharpness visible at the call site — a "this shape has no curve"
manifesto. We keep that explicit declaration in `components.html`.

---

## 5. Tag system

```css
.tag { letter-spacing: .32px; border-radius: 24px; padding: 4px 8px;
       font-size: .75rem; font-weight: 400; display: inline-block; }
.tag-blue { color: #0f62fe; background: #edf5ff; }
.tag-gold { color: #b8860b; background: #fef7e0; }
.tag-navy { color: #00338d; background: #edf5ff; }
```

The source ships `border-radius: 24px` on tags. **We override this
to 0** in the brand spec — it conflicts with the global
0-radius commitment. The brand-spec section 6.3 was rewritten to
`圆角 0` before this design system was extracted. Tags in
`components.html` therefore carry `border-radius: 0`, not 24px.

---

## 6. Hero / footer dark surface

```css
.hero { background: var(--hero); color: var(--hero-foreground);
        padding: var(--space-5xl) 0; }
.site-footer { background: var(--hero); color: var(--hero-foreground);
               padding: var(--space-4xl) 0 var(--space-2xl); }
```

Both are bound to `--hero` (`#161616`). The source's footer uses
`var(--sidebar)` for its dark surface; we collapse that into
`--hero` for the canonical system since the brand has only one
dark tone in active use.
