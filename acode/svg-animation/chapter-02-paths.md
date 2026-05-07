# Chapter 2: Path Commands — The Language of Curves

[← Ch 1: ViewBox & Shapes](chapter-01-viewbox-shapes.md) | [Ch 3: CSS Animation →](chapter-03-css-animation.md)

---

## Zara's Request

> "The logo is just a PNG. I need it as an SVG path so we can animate it drawing itself later. Basic shapes won't cut it — this has custom curves. You need to understand path commands."

She sends a Figma export: `M 12 2 C 6.48 2 2 6.48 2 12 s 4.48 10 10 10...` — what does any of this mean?

---

## The `<path>` Element

Every complex shape is ultimately a path. It uses single-letter commands in the `d` attribute:

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M 10 80 L 50 10 L 90 80 Z" fill="none" stroke="#6366f1" stroke-width="3"/>
</svg>
```

Move to (10,80), Line to (50,10), Line to (90,80), Close. A triangle.

---

## Core Commands

**Move (M)** — picks up the pen: `M 10 20`

**Line (L)** — straight line to target: `L 90 50`. Shorthand: `H 90` (horizontal), `V 50` (vertical).

**Close (Z)** — line back to start point.

**Cubic Bézier (C)** — the workhorse of curves:

```svg
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M 10 80 C 40 10, 65 10, 95 80" fill="none" stroke="#6366f1" stroke-width="3"/>
  <!-- Control points visualized -->
  <circle cx="40" cy="10" r="3" fill="#ef4444"/>
  <circle cx="65" cy="10" r="3" fill="#ef4444"/>
</svg>
```

`C x1 y1, x2 y2, x y` — two control points pull the curve, endpoint is the destination.

**Smooth Cubic (S)** — mirrors the previous control point automatically:
```
M 10 50 C 30 10, 50 10, 70 50 S 110 90, 130 50
```

**Quadratic Bézier (Q)** — one shared control point:
```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M 10 80 Q 50 10, 90 80" fill="none" stroke="#06b6d4" stroke-width="3"/>
</svg>
```

**Arc (A)** — elliptical arc, the most complex:

```
A rx ry x-rotation large-arc-flag sweep-flag x y
```

| Parameter | Meaning |
|-----------|---------|
| `rx`, `ry` | Ellipse radii |
| `large-arc-flag` | 0 = smaller arc, 1 = larger |
| `sweep-flag` | 0 = counter-clockwise, 1 = clockwise |

---

## Absolute vs Relative

Uppercase = absolute position. Lowercase = relative offset from current point.

| Uppercase | Lowercase | Difference |
|-----------|-----------|-----------|
| `M 50 50` | `m 50 50` | Absolute vs relative |
| `L 90 80` | `l 40 30` | To (90,80) vs 40 right, 30 down |

Relative commands are useful for reusable shapes that don't depend on starting position.

---

## Building Orbitly's Logo

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M 50 15 C 70 15, 85 30, 85 50 C 85 70, 70 85, 50 85
           C 30 85, 15 70, 15 50 C 15 30, 30 15, 50 15 Z"
        fill="none" stroke="#6366f1" stroke-width="3" stroke-linecap="round"/>
  <circle cx="85" cy="50" r="5" fill="#6366f1"/>
  <circle cx="50" cy="50" r="4" fill="#818cf8"/>
</svg>
```

---

## Common Mistakes

**Forgetting the starting M** — every path must begin with `M` or `m`.

**Mixing up arc flags** — large-arc and sweep are just 0/1, but wrong values give the mirror-image arc.

**Unmatched point counts** — if you plan to morph between paths (Ch 5), they need the same command structure. Plan ahead.

---

## Exercise

1. Create a checkmark: `M 20 55 L 40 75 L 80 25` with `stroke-linecap="round"`
2. Create a heart using two cubic Bézier curves — start at the bottom point, two `C` curves for left and right lobes
3. Trace the Orbitly logo path by hand: start with a circle approximation using 4 cubic Bézier segments (each covering 90° of arc)

---

## Visualizing Control Points

A helpful mental model: control points are "magnets" that pull the curve toward them without the curve actually passing through them.

```svg
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <!-- The curve -->
  <path d="M 20 80 C 50 10, 80 10, 110 80 S 170 150, 190 80"
        fill="none" stroke="#6366f1" stroke-width="2"/>
  <!-- Control point handles -->
  <line x1="20" y1="80" x2="50" y2="10" stroke="#ef4444" stroke-width="0.5" stroke-dasharray="3"/>
  <line x1="110" y1="80" x2="80" y2="10" stroke="#ef4444" stroke-width="0.5" stroke-dasharray="3"/>
  <circle cx="50" cy="10" r="3" fill="#ef4444"/>
  <circle cx="80" cy="10" r="3" fill="#ef4444"/>
</svg>
```

The red dots are control points. The dashed lines show their "pull" on the curve. Moving a control point reshapes the curve without changing the endpoints.

---

## Quick Reference

| Command | Name | Parameters | Example |
|---------|------|-----------|---------|
| `M`/`m` | Move | `x y` | `M 10 20` |
| `L`/`l` | Line | `x y` | `L 90 80` |
| `H`/`h` | Horizontal | `x` | `H 90` |
| `V`/`v` | Vertical | `y` | `V 50` |
| `C`/`c` | Cubic Bézier | `x1 y1, x2 y2, x y` | `C 20 10, 40 10, 50 50` |
| `S`/`s` | Smooth Cubic | `x2 y2, x y` | `S 80 90, 90 50` |
| `Q`/`q` | Quadratic | `x1 y1, x y` | `Q 50 10, 90 80` |
| `T`/`t` | Smooth Quad | `x y` | `T 130 50` |
| `A`/`a` | Arc | `rx ry rot large sweep x y` | `A 30 30 0 0 1 90 50` |
| `Z`/`z` | Close | — | `Z` |

---

[← Ch 1: ViewBox & Shapes](chapter-01-viewbox-shapes.md) | [Ch 3: CSS Animation →](chapter-03-css-animation.md)
