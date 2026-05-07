# Chapter 18: SVG Optimization — Lean and Clean

[← Ch 17: Accessibility](chapter-17-accessibility.md) | [Ch 19: React Integration →](chapter-19-react-integration.md)

---

## Zara's Request

> "12 illustrations from Figma. Each is 180KB. That's 2MB of SVG. Page takes 4 seconds on 3G."

Dani: "Figma exports are full of editor metadata, redundant groups, unnecessary precision. SVGO handles most of it. But also think about reuse — symbols, sprites, inline vs external."

---

## SVGO

```bash
npm install -g svgo
svgo input.svg -o output.svg
svgo -f ./icons/ -o ./icons-optimized/
```

### What It Removes

| Bloat | Example | Safe? |
|-------|---------|-------|
| Editor metadata | `<metadata>`, Figma IDs | ✅ |
| XML declarations | `<?xml version="1.0"?>` | ✅ inline |
| Empty groups | `<g></g>` | ✅ |
| Excessive precision | `cx="49.99999847"` | ✅ |
| Comments | `<!-- Created with Figma -->` | ✅ |
| Unused defs | Unreferenced gradients | ✅ |

### Before (45KB) → After (0.3KB)

```svg
<!-- Before: Figma export -->
<?xml version="1.0" encoding="UTF-8"?>
<svg width="800px" height="600px" viewBox="0 0 800 600" version="1.1" xmlns="http://www.w3.org/2000/svg">
    <!-- Created with Figma --><title>Dashboard</title>
    <g id="Page-1" stroke="none" fill="none"><g id="Dashboard">
        <rect id="Background" fill="#FFFFFF" x="0.000000" y="0.000000" width="800.000000" height="600.000000" rx="12.000000"/>
    </g></g>
</svg>

<!-- After: SVGO -->
<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <rect fill="#fff" width="800" height="600" rx="12"/>
</svg>
```

---

## `<symbol>` and `<use>` — Define Once, Use Many

```svg
<!-- Define icons (hidden) -->
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="icon-check" viewBox="0 0 24 24">
    <path d="M20 6L9 17l-5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </symbol>
  <symbol id="icon-x" viewBox="0 0 24 24">
    <path d="M18 6L6 18M6 6l12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </symbol>
</svg>

<!-- Use anywhere, any size -->
<svg width="24" height="24"><use href="#icon-check"/></svg>
<svg width="16" height="16"><use href="#icon-x"/></svg>
```

`currentColor` inherits from parent CSS `color`. Single source of truth, lightweight references.

---

## SVG Sprite System

```svg
<!-- icons.svg (external sprite file) -->
<svg xmlns="http://www.w3.org/2000/svg">
  <symbol id="home" viewBox="0 0 24 24">
    <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3"/>
  </symbol>
  <symbol id="settings" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="3"/><path d="M10.3 21l-.2-2.5..."/>
  </symbol>
</svg>
```

```html
<svg width="24" height="24"><use href="/icons.svg#home"/></svg>
```

---

## Inline vs External

| Approach | Pros | Cons |
|----------|------|------|
| Inline | CSS/JS access, animatable | Bloats HTML |
| External `<img>` | Cached, clean HTML | No animation |
| External `<use>` | Cached sprite, reusable | CORS issues |
| Data URI | No extra request | Not readable |

**Decision:** Need to animate? → Inline. Static icon used many times? → Symbol/use. Illustration that doesn't change? → External `<img>`.

---

## Manual Optimization Tips

```svg
<!-- Reduce precision: 1-2 decimals sufficient -->
<path d="M 12.85 45.29 C 67.38 23.85 89.13 12.38 100.29 50.38"/>

<!-- Combine paths -->
<path d="M 10 10 L 50 10 M 10 20 L 50 20 M 10 30 L 50 30" stroke="#333"/>

<!-- Remove defaults, shorten colors -->
<rect width="100" height="100" fill="#000"/>
```

---

## SVGO Config for Animation Projects

```javascript
// svgo.config.js
module.exports = {
  plugins: [
    'removeDoctype', 'removeComments', 'removeMetadata',
    'cleanupAttrs', 'removeUselessDefs', 'cleanupNumericValues',
    'convertColors', 'removeEmptyContainers', 'sortAttrs',
    { name: 'cleanupIds', active: false },  // KEEP IDs for animation targets
    { name: 'removeViewBox', active: false } // NEVER remove viewBox
  ]
};
```

> **Warning:** Never remove `viewBox`. Never remove IDs you target in CSS/JS.

---

## Common Mistakes

**SVGO removes animation IDs** — disable `cleanupIds` or use class names.

**Removing viewBox** — breaks responsive scaling. Always keep it.

**Over-optimizing animated paths** — `mergePaths` changes point counts, breaking morphs.

**External sprites + CORS** — `<use href="/icons.svg#home"/>` fails cross-origin.

---

## Exercise

Optimize Orbitly's icon set:
1. Export 5 icons from Figma
2. Run SVGO with config preserving animation IDs
3. Create a `<symbol>` sprite sheet
4. Use each icon at 3 sizes (16, 24, 48px) via `<use>`
5. Compare: original export vs optimized sprite

Bonus: Build script that auto-optimizes SVGs and generates the sprite.

---

## Quick Reference

| Tool | Purpose | Command |
|------|---------|---------|
| SVGO | Optimize files | `svgo input.svg -o output.svg` |
| SVGR | SVG → React | Build plugin |
| svg-sprite | Generate sprites | `svg-sprite --mode symbol` |

| Optimization | Typical Savings |
|-------------|----------------|
| Remove metadata | 5–15% |
| Clean precision | 10–20% |
| Merge paths | 10–30% |
| Total (SVGO) | 40–70% |

---

[← Ch 17: Accessibility](chapter-17-accessibility.md) | [Ch 19: React Integration →](chapter-19-react-integration.md)
