# Chapter 1: The ViewBox and Basic Shapes

[← Ch 0: Overview](chapter-00-overview.md) | [Ch 2: Paths →](chapter-02-paths.md)

---

## Zara's Request

> "I need dashboard sidebar icons — home, settings, bell, avatar. Crisp at 16px AND 64px. No PNGs. Pure SVG so we can animate them later. Get the coordinate system right first. If the viewBox is wrong, everything downstream breaks."

---

## The SVG Coordinate System

The `viewBox` defines internal coordinates independent of rendered size:

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <!-- Internal: 0,0 to 100,100. Rendered: 200x200px -->
</svg>
```

Four values: `min-x min-y width height`. A circle at `cx="50"` is always centered — whether the SVG is 16px or 1600px wide. No pixelation. That's vector.

---

## Basic Shapes

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Rectangle: x, y, width, height, rx/ry for rounded corners -->
  <rect x="10" y="10" width="80" height="60" rx="8" fill="#818cf8" stroke="#4f46e5" stroke-width="2"/>

  <!-- Circle: cx, cy (center), r (radius) -->
  <circle cx="50" cy="50" r="40" fill="none" stroke="#06b6d4" stroke-width="3"/>

  <!-- Ellipse: cx, cy, rx (horizontal), ry (vertical) -->
  <ellipse cx="50" cy="50" rx="40" ry="25" fill="#f472b6" fill-opacity="0.3"/>

  <!-- Line: x1,y1 to x2,y2 -->
  <line x1="10" y1="80" x2="90" y2="20" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>

  <!-- Polygon: auto-closes -->
  <polygon points="50,5 95,35 80,90 20,90 5,35" fill="#fbbf24" stroke="#f59e0b" stroke-width="2"/>

  <!-- Polyline: open shape -->
  <polyline points="10,80 30,40 50,60 70,20 90,50" fill="none" stroke="#8b5cf6" stroke-width="3"/>
</svg>
```

---

## Fill and Stroke

| Property | What It Does | Example |
|----------|-------------|---------|
| `fill` | Interior color | `fill="#6366f1"` |
| `fill-opacity` | Interior transparency | `fill-opacity="0.5"` |
| `stroke` | Border color | `stroke="#4f46e5"` |
| `stroke-width` | Border thickness | `stroke-width="2"` |
| `stroke-linecap` | Line end style | `round`, `square`, `butt` |
| `stroke-linejoin` | Corner style | `round`, `miter`, `bevel` |
| `stroke-dasharray` | Dashed lines | `stroke-dasharray="5 3"` |

---

## Building Zara's Home Icon

```svg
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <polygon points="12,2 22,12 19,12 19,22 5,22 5,12 2,12"/>
  <rect x="9" y="14" width="6" height="8"/>
</svg>
```

Works at any size because the viewBox is fixed at 24×24 internal units.

### A Settings Gear

```svg
<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"
     fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="12" cy="12" r="3"/>
  <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33
           1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06
           a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15 1.65 1.65 0 003 14.08V14a2 2 0 014 0"/>
</svg>
```

The gear uses a combination of a circle (center) and a complex path (teeth). Both scale perfectly from 16px to 64px.

---

## Units and Sizing

SVG supports multiple unit systems, but inside the viewBox, everything is unitless:

```svg
<!-- These are equivalent when viewBox="0 0 100 100" -->
<rect x="10" y="10" width="80" height="80"/>
<rect x="10" y="10" width="80" height="80"/>  <!-- no "px" needed -->
```

The `width` and `height` on the `<svg>` element control rendered size. The viewBox controls the internal coordinate space. They're independent.

```html
<!-- Same SVG, different rendered sizes -->
<svg viewBox="0 0 24 24" width="16" height="16">...</svg>
<svg viewBox="0 0 24 24" width="48" height="48">...</svg>
<svg viewBox="0 0 24 24" style="width: 100%; max-width: 200px;">...</svg>
```

---

## Common Mistakes

**Forgetting the viewBox** — without it, no responsive scaling.

**Stroke bleeds outside** — a circle at `r="50"` with `stroke-width="4"` extends to 52px. Stroke paints half inside, half outside.

```svg
<!-- Fix: account for stroke width -->
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="48" stroke-width="4" stroke="#6366f1" fill="none"/>
</svg>
```

**Using pixel units inside viewBox** — coordinates are unitless. Write `x="10"`, not `x="10px"`.

**Aspect ratio mismatch** — if viewBox is `0 0 100 50` but the SVG renders at 200×200, the content gets letterboxed. Use `preserveAspectRatio` to control this behavior.

---

## Exercise

Build Orbitly's notification bell icon using only basic shapes:
1. A circle or ellipse for the bell body
2. A small circle for the clapper
3. A line or rect for the top hook
4. Use `viewBox="0 0 24 24"` — must work at both `width="16"` and `width="48"`

Bonus: Add a red notification badge circle at top-right.

---

## Quick Reference

| Element | Key Attributes | Notes |
|---------|---------------|-------|
| `<svg>` | `viewBox`, `width`, `height` | Always set viewBox |
| `<rect>` | `x`, `y`, `width`, `height`, `rx` | rx for rounded corners |
| `<circle>` | `cx`, `cy`, `r` | Center + radius |
| `<ellipse>` | `cx`, `cy`, `rx`, `ry` | Two radii |
| `<line>` | `x1`, `y1`, `x2`, `y2` | Needs stroke |
| `<polygon>` | `points` | Auto-closes |
| `<polyline>` | `points` | Open shape |

---

[← Ch 0: Overview](chapter-00-overview.md) | [Ch 2: Paths →](chapter-02-paths.md)
