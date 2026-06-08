---
id: AUDIT-005
date: 2026-06-08
session: S35
title: Mobile Layout Root-Cause Analysis — All 4 Regressions
scope: CSS / HTML / browser layout engine
commits: e735d71 (round 1, partial), ca37f51 (round 2, definitive fix)
status: RESOLVED
---

# AUDIT-005 — Mobile Layout Root-Cause Analysis

## Context
User reported mobile app as unusable after S34 deploy: login card tiny and centred,
sidebar icons bleeding onto every page, bottom nav disappearing after navigation,
all content zoomed out. Two rounds of fixes were attempted (e735d71). The symptoms
persisted after round 1 because that round addressed symptoms rather than root causes.

## Root Causes (in order of severity)

### RC-1 — Browser CSS cache (ca37f51)
`style.css` was served with no cache-busting query parameter. The phone's browser had
cached the pre-fix CSS indefinitely. All CSS changes in e735d71 were silently ignored.
**Fix:** `style.css?v=4` in both `base.html` and `login.html`.

### RC-2 — `min-width: auto` on `.main-content` (ca37f51) [THE SYSTEMIC CAUSE]
Flex items default to `min-width: auto`, which tells the browser "this item's minimum
size equals the minimum intrinsic width of its content." Any child element with a wide
`min-width` (e.g., `min-width: 200px` action buttons in rbi_dashboard.html) would
expand `.main-content`, which would expand `.app-layout`, which would push the page
width > 600px. On Samsung Internet (Galaxy default browser) this expands the LAYOUT
VIEWPORT past 600px, causing ALL `@media (max-width: 600px)` rules to stop firing.
This created a vicious cascade: sidebar shows → 220px margin-left on main-content →
content area only 170px → buttons overflow → viewport expands → media queries fail.

**Fix:** `min-width: 0` on `.main-content` (allows flex item to shrink to available
space); `width: 100%; overflow-x: hidden` on `.app-layout` (hard outer containment).

### RC-3 — CSS specificity race (e735d71, partially addressed)
`body.sidebar-collapsed .main-content { margin-left: 52px }` (specificity 0,2,1)
beat the 600px media query rule `.main-content { margin-left: 0 }` (specificity 0,1,0).
Addressed in e735d71 by adding matching-specificity overrides in the media query.
**Superseded by RC-4's !important approach.**

### RC-4 — No inline critical CSS (ca37f51)
Even with correct CSS rules in `style.css`, browser cache (RC-1) prevented them from
loading. The structural fix: inline `<style>` block in `<head>` of `base.html` with
`!important` overrides. Inline styles are part of the HTML document (not separately
cached), fire before first paint, and `!important` wins all specificity battles.

```html
<style>
@media (max-width: 600px) {
    .sidebar { display: none !important; }
    .main-content { margin-left: 0 !important; max-width: 100% !important; padding: 1rem 1rem 5rem !important; }
    body.sidebar-collapsed .main-content { margin-left: 0 !important; }
    .mobile-nav { display: flex !important; }
}
</style>
```

### RC-5 — Sidebar in DOM causing layout side-effects (ca37f51)
Even with `display: none`, `position: fixed` sidebar remained in DOM. JS sidebar
toggle could re-show it. Belt-and-suspenders fix: DOM removal on mobile.

```javascript
if (window.innerWidth <= 600) {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.remove();
    document.body.classList.remove('sidebar-collapsed');
}
```

### RC-6 — Login card not truly full-screen (ca37f51)
User wanted login to "fill up the whole page." Previous fix only changed vertical
alignment (`align-items: flex-start`). The card was still 380px max-width on a
390px viewport with 64px of padding on sides = 326px = not full screen.
**Fix:** `align-items: stretch`, `max-width: 100%`, `border-radius: 0`,
`min-height: 100vh` on `.login-card` at 600px breakpoint.

Note: login.html is STANDALONE (not extending base.html). It has its own viewport
meta and loads style.css directly. No sidebar, no .app-layout. The card being "tiny"
was purely the CSS cache issue — the card would have been full-width if new CSS loaded.

## Files Changed (ca37f51)

| File | Change |
|------|--------|
| `web/templates/base.html` | Inline critical CSS with `!important`; JS sidebar DOM removal; `?v=4` cache bust |
| `web/templates/login.html` | `?v=4` cache bust |
| `web/static/style.css` | `min-width: 0` on `.main-content`; `width: 100%; overflow-x: hidden` on `.app-layout`; login full-screen mobile CSS |
| `web/templates/rbi_dashboard.html` | Action button min-widths: 200px→140px, 160px→120px (removes immediate overflow trigger) |

## Patterns Discovered

- **CSS-MOB-001** — Flex `min-width: auto` expands layout viewport on Samsung Internet past CSS breakpoints. See `~/.claude/knowledge/patterns/CSS-MOB-001-flex-min-width-viewport.md`.
- **CSS-MOB-002** — Use inline `<style>` with `!important` in `<head>` for critical mobile layout rules that must survive browser CSS file caching.

## Remaining Watch Items
- Other pages with `min-width > 300px` in flex containers (ies_brief.html:29,
  rbi_prep.html:327, english.html:44) — all are inside `flex-wrap:wrap` containers
  so they stack rather than overflow. No action needed unless new overflow reports come in.
- Production confirmation pending: user to verify on device after Railway deploy.
