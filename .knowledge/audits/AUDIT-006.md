---
id: AUDIT-006
date: 2026-06-08
session: S35 (continued)
title: Mobile UI Polish — Button Overflow, Stat Card Word-Break, Grid Collapse
scope: CSS / Jinja2 templates
commit: 7f405e9
status: RESOLVED
---

# AUDIT-006 — Mobile UI Polish (Round 3)

## Source
User provided 3 device screenshots (nyayascribemobileissues02.zip):
- 1000036026.jpg: RBI Dashboard — button text cut off at left viewport edge, "ANSWERE D"/"ACCURAC Y" mid-word breaks
- 1000036027.jpg: UPSC Dashboard — 5-column stat grid, each cell ~63px, text wrapping per character
- 1000036028.jpg: UPSC State Overview — each state badge taking full viewport width (1 per row)

## Root Causes & Fixes

### RC-1 — Button text overflow (`.btn { white-space: nowrap }`)
Long action button labels like "🧠 Priority 1 MCQs — Smart Session" could not wrap
inside their button. With `flex:1` and two buttons side-by-side, each button got ~173px
but the text at 15px/char was ~295px. The button expanded to accommodate the text,
pushing the start off the left viewport edge — hence "riority 1 MCQs…" visible with P cut off.

**Fix:** `white-space: normal; line-height: 1.3` in the 600px mobile breakpoint + same
rule in the inline `<style>` block with `!important`. Short button labels ("Reset", "Quick
Verify") are unaffected since short text doesn't wrap.

### RC-2 — Metric label mid-word breaks ("ANSWERE D", "ACCURAC Y")
`.gem-card { overflow-wrap: anywhere }` tells the flex/grid algorithm that words can
be broken at ANY character. The algorithm therefore allocates less width to cells than
the words actually need (since it believes words can shrink to 1 char). At render time,
the word "ANSWERED" (~55px) is forced to break mid-word in a cell that's nominally wide
enough to hold it, but the layout engine had already committed to a narrower size.

Two-part fix:
1. `overflow-wrap: anywhere` → `overflow-wrap: break-word` on ALL card variants
   (gem-card, gem-card-sm, gem-card-accent, answer-section). `break-word` still handles
   long URL overflow but does NOT affect minimum content size calculation.
2. `.metric-label { word-break: normal; overflow-wrap: normal }` — explicit override
   so stat card labels never break mid-word regardless of container width.

### RC-3 — UPSC Dashboard 5-col inline grid
`style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;"` on the
metric row. On mobile (~358px content): each column = (358 - 4×10) / 5 = 63px.
With gem-card padding 16px 20px (40px total), content area = 23px. Completely unusable.

**Fix:** Added `.grid-5` utility class to style.css (mirrors .grid-6 pattern, collapses
to 3 columns at ≤900px and ≤600px). Updated upsc_dashboard.html line 19 to use
`class="grid-5"` instead of inline style.

### RC-4 — All grids collapsing to single column (grid-6 state overview)
Previous 600px rule: `.grid-2, .grid-3, .grid-4, .grid-6 { grid-template-columns: 1fr }`.
Every grid became single-column on mobile — state overview badges took full viewport width.

**New strategy:**
- `.grid-3, .grid-4` → `repeat(2, 1fr)` at 600px (2 items per row)
- `.grid-5, .grid-6` → `repeat(3, 1fr)` at 600px (3 items per row)
- `.grid-2` stays 2-col (was unchanged)

UPSC state overview (grid-6, 6 states) → 3×2 grid on mobile.
IES dashboard grid-6 (line 229) → same fix automatically.

### RC-5 — Gem-card padding too large for narrow mobile cells
`padding: 16px 20px` (40px horizontal per card) wasted too much width. Reduced to
`padding: 10px 12px` at 600px breakpoint — frees 16px per cell.

## Files Changed

| File | Change |
|------|--------|
| `web/static/style.css` | overflow-wrap fix; .metric-label; .grid-5 class; grid collapse strategy; .btn white-space; gem-card mobile padding |
| `web/templates/base.html` | `.btn { white-space: normal !important }` in inline critical CSS; ?v=5 cache-bust |
| `web/templates/login.html` | ?v=5 cache-bust |
| `web/templates/upsc_dashboard.html` | metric row: inline repeat(5,1fr) → class="grid-5" |

## CSS Version
CSS cache-busted to `?v=5` (was ?v=4).
