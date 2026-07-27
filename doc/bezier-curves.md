# Bezier Curves — How They Work

---

## What Is a Bezier Curve?

A smooth curve defined by control points. You give it a start, an end, and 1-2 "magnet" points that pull the curve toward them without touching.

```
Straight line:     A ─────────────────── B

Quadratic bezier:  A ───╮           ╭─── B
(1 control point)       ╰─── C ───╯
                         (control point pulls the curve up)

Cubic bezier:      A ───╮               ╭─── B
(2 control points)      ╰─── C₁    C₂──╯
                         (two magnets shape the curve)
```

---

## Visual Intuition

### Quadratic (3 points: start, control, end)

```
        C (control — the "magnet")
        •
       ╱ ╲
      ╱   ╲ ← curve is pulled toward C
     ╱     ╲    but never touches it
    •       •
    A       B
  (start)  (end)
```

### Cubic (4 points: start, control1, control2, end)

```
    C₁         C₂
    •           •
   ╱             ╲
  ╱               ╲ ← two magnets shape an S-curve
 •                 •
 A                 B
```

Move the control points → curve reshapes. That's all there is to it.

---

## The Math (Simple Version)

A bezier curve is just **interpolation** done recursively.

### Linear Interpolation (lerp) — The Building Block

```
Given A and B, find a point t% of the way between them:

P = A + t × (B - A)

t = 0   → P = A (start)
t = 0.5 → P = midpoint
t = 1   → P = B (end)
```

```tsx
function lerp(a: number, b: number, t: number): number {
  return a + t * (b - a)
}
```

### Quadratic Bezier (3 points)

Lerp between pairs, then lerp the results:

```
Points: A, C (control), B
At time t:

Step 1: D = lerp(A, C, t)    ← point between A and C
Step 2: E = lerp(C, B, t)    ← point between C and B
Step 3: P = lerp(D, E, t)    ← point between D and E ← THIS is the curve point
```

```tsx
function quadraticBezier(
  A: { x: number; y: number },
  C: { x: number; y: number },
  B: { x: number; y: number },
  t: number
) {
  const dx = lerp(A.x, C.x, t)
  const dy = lerp(A.y, C.y, t)
  const ex = lerp(C.x, B.x, t)
  const ey = lerp(C.y, B.y, t)

  return {
    x: lerp(dx, ex, t),
    y: lerp(dy, ey, t),
  }
}
```

### Cubic Bezier (4 points)

Same idea, one more layer:

```
Points: A, C₁, C₂, B
At time t:

Step 1: D = lerp(A, C₁, t)
Step 2: E = lerp(C₁, C₂, t)
Step 3: F = lerp(C₂, B, t)
Step 4: G = lerp(D, E, t)
Step 5: H = lerp(E, F, t)
Step 6: P = lerp(G, H, t)     ← curve point
```

```tsx
function cubicBezier(
  A: { x: number; y: number },
  C1: { x: number; y: number },
  C2: { x: number; y: number },
  B: { x: number; y: number },
  t: number
) {
  const d = { x: lerp(A.x, C1.x, t), y: lerp(A.y, C1.y, t) }
  const e = { x: lerp(C1.x, C2.x, t), y: lerp(C1.y, C2.y, t) }
  const f = { x: lerp(C2.x, B.x, t), y: lerp(C2.y, B.y, t) }

  const g = { x: lerp(d.x, e.x, t), y: lerp(d.y, e.y, t) }
  const h = { x: lerp(e.x, f.x, t), y: lerp(e.y, f.y, t) }

  return {
    x: lerp(g.x, h.x, t),
    y: lerp(g.y, h.y, t),
  }
}
```

### Generate Points Along the Curve

```tsx
function getCurvePoints(A, C1, C2, B, steps = 100) {
  const points = []
  for (let i = 0; i <= steps; i++) {
    const t = i / steps
    points.push(cubicBezier(A, C1, C2, B, t))
  }
  return points
}
```

---

## In SVG

### Quadratic: `Q`

```
Q cx cy, ex ey
  │  │   │  │
  │  │   └──┘ end point
  └──┘ control point
```

```html
<path d="M 50 200 Q 200 50, 350 200" />
```

Start at (50,200), curve toward (200,50), end at (350,200).

### Cubic: `C`

```
C c1x c1y, c2x c2y, ex ey
  │    │    │    │   │  │
  └────┘    └────┘   └──┘
  control1  control2  end
```

```html
<path d="M 50 200 C 100 50, 300 50, 350 200" />
```

### Smooth Cubic: `S` (mirrors previous control point)

```html
<path d="M 50 200 C 100 50, 200 50, 250 200 S 400 350, 450 200" />
```

`S` auto-generates the first control point by mirroring the previous `C`'s second control point. Creates smooth S-curves without calculating the mirrored point yourself.

---

## Interactive Bezier Demo (Draggable Control Points)

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

interface Point {
  x: number
  y: number
}

export function BezierDemo() {
  const [start] = useState<Point>({ x: 50, y: 300 })
  const [end] = useState<Point>({ x: 450, y: 300 })
  const [c1, setC1] = useState<Point>({ x: 150, y: 50 })
  const [c2, setC2] = useState<Point>({ x: 350, y: 50 })

  const pathD = `M ${start.x} ${start.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${end.x} ${end.y}`

  return (
    <svg width={500} height={400} className="border rounded-lg bg-card">
      {/* Guide lines (control point → start/end) */}
      <line x1={start.x} y1={start.y} x2={c1.x} y2={c1.y}
        stroke="hsl(var(--muted-foreground))" strokeWidth={1} strokeDasharray="4 4" />
      <line x1={end.x} y1={end.y} x2={c2.x} y2={c2.y}
        stroke="hsl(var(--muted-foreground))" strokeWidth={1} strokeDasharray="4 4" />

      {/* The bezier curve */}
      <motion.path
        d={pathD}
        fill="none"
        stroke="hsl(var(--primary))"
        strokeWidth={3}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1 }}
        key={pathD}  // re-animate when path changes
      />

      {/* Start and End points */}
      <circle cx={start.x} cy={start.y} r={6} className="fill-green-500" />
      <circle cx={end.x} cy={end.y} r={6} className="fill-red-500" />

      {/* Draggable Control Points */}
      <motion.circle
        cx={c1.x} cy={c1.y} r={10}
        className="fill-yellow-400 cursor-grab"
        drag
        dragMomentum={false}
        onDrag={(_, info) => setC1({ x: c1.x + info.delta.x, y: c1.y + info.delta.y })}
        whileHover={{ scale: 1.3 }}
      />
      <motion.circle
        cx={c2.x} cy={c2.y} r={10}
        className="fill-yellow-400 cursor-grab"
        drag
        dragMomentum={false}
        onDrag={(_, info) => setC2({ x: c2.x + info.delta.x, y: c2.y + info.delta.y })}
        whileHover={{ scale: 1.3 }}
      />

      {/* Labels */}
      <text x={c1.x + 12} y={c1.y} className="fill-muted-foreground text-xs">C₁</text>
      <text x={c2.x + 12} y={c2.y} className="fill-muted-foreground text-xs">C₂</text>
    </svg>
  )
}
```

Drag the yellow dots → curve reshapes in real time. This is the best way to build intuition.

---

## Visualising the Construction (De Casteljau's Algorithm)

Show HOW the curve is built at a given `t`:

```tsx
"use client"

import { useState } from "react"

export function DeCasteljauDemo() {
  const [t, setT] = useState(0.5)

  const A = { x: 50, y: 300 }
  const C1 = { x: 150, y: 50 }
  const C2 = { x: 350, y: 50 }
  const B = { x: 450, y: 300 }

  // Level 1: lerp pairs
  const D = { x: lerp(A.x, C1.x, t), y: lerp(A.y, C1.y, t) }
  const E = { x: lerp(C1.x, C2.x, t), y: lerp(C1.y, C2.y, t) }
  const F = { x: lerp(C2.x, B.x, t), y: lerp(C2.y, B.y, t) }

  // Level 2: lerp pairs again
  const G = { x: lerp(D.x, E.x, t), y: lerp(D.y, E.y, t) }
  const H = { x: lerp(E.x, F.x, t), y: lerp(E.y, F.y, t) }

  // Level 3: final point on curve
  const P = { x: lerp(G.x, H.x, t), y: lerp(G.y, H.y, t) }

  return (
    <div className="flex flex-col items-center gap-4">
      <svg width={500} height={400} className="border rounded-lg bg-card">
        {/* The full curve (faded) */}
        <path
          d={`M ${A.x} ${A.y} C ${C1.x} ${C1.y}, ${C2.x} ${C2.y}, ${B.x} ${B.y}`}
          fill="none"
          stroke="hsl(var(--muted-foreground))"
          strokeWidth={2}
          opacity={0.3}
        />

        {/* Level 1 lines (green) */}
        <line x1={A.x} y1={A.y} x2={C1.x} y2={C1.y} stroke="green" strokeWidth={1} />
        <line x1={C1.x} y1={C1.y} x2={C2.x} y2={C2.y} stroke="green" strokeWidth={1} />
        <line x1={C2.x} y1={C2.y} x2={B.x} y2={B.y} stroke="green" strokeWidth={1} />

        {/* Level 2 lines (blue) */}
        <line x1={D.x} y1={D.y} x2={E.x} y2={E.y} stroke="blue" strokeWidth={1} />
        <line x1={E.x} y1={E.y} x2={F.x} y2={F.y} stroke="blue" strokeWidth={1} />

        {/* Level 3 line (red) */}
        <line x1={G.x} y1={G.y} x2={H.x} y2={H.y} stroke="red" strokeWidth={1} />

        {/* Points */}
        <circle cx={A.x} cy={A.y} r={5} fill="green" />
        <circle cx={C1.x} cy={C1.y} r={5} fill="green" />
        <circle cx={C2.x} cy={C2.y} r={5} fill="green" />
        <circle cx={B.x} cy={B.y} r={5} fill="green" />

        <circle cx={D.x} cy={D.y} r={4} fill="blue" />
        <circle cx={E.x} cy={E.y} r={4} fill="blue" />
        <circle cx={F.x} cy={F.y} r={4} fill="blue" />

        <circle cx={G.x} cy={G.y} r={4} fill="red" />
        <circle cx={H.x} cy={H.y} r={4} fill="red" />

        {/* THE CURVE POINT */}
        <circle cx={P.x} cy={P.y} r={8} fill="hsl(var(--primary))" />
      </svg>

      {/* Slider */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">t = {t.toFixed(2)}</span>
        <input
          type="range"
          min={0} max={1} step={0.01}
          value={t}
          onChange={(e) => setT(parseFloat(e.target.value))}
          className="w-64"
        />
      </div>
    </div>
  )
}

function lerp(a: number, b: number, t: number) {
  return a + t * (b - a)
}
```

**What this shows:**
- Green lines: the original 4 control points
- Blue lines: first level of interpolation (3 points)
- Red line: second level (2 points)
- The big dot: final curve point (1 point)

Drag the slider from 0 → 1 and watch the dot trace the curve. The nested interpolation IS the curve.

---

## Bezier in CSS (Easing Functions)

CSS `transition-timing-function` uses cubic bezier:

```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

The 4 numbers are the two control points (x1, y1, x2, y2) on a 0→1 graph:

```
        1 ─────────────────── •  (end)
          │               ╱
  output  │            ╱      ← steep = fast at the end
          │         ╱
          │      ╱
          │   •  C₂(0.2, 1)
          │  ╱
          │╱
        0 •─────────────────── 1
          (start)    input (time)
            C₁(0.4, 0)
```

**Common easings:**

| Name | Value | Feels like |
|------|-------|-----------|
| `ease` | `cubic-bezier(0.25, 0.1, 0.25, 1)` | Default — starts fast, slows at end |
| `ease-in` | `cubic-bezier(0.42, 0, 1, 1)` | Starts slow, ends fast (accelerate) |
| `ease-out` | `cubic-bezier(0, 0, 0.58, 1)` | Starts fast, ends slow (decelerate) |
| `ease-in-out` | `cubic-bezier(0.42, 0, 0.58, 1)` | Slow start and end |
| `linear` | `cubic-bezier(0, 0, 1, 1)` | Constant speed |

In Framer Motion:

```tsx
transition={{ ease: [0.4, 0, 0.2, 1] }}  // same as cubic-bezier(0.4, 0, 0.2, 1)
```

---

## Where Beziers Appear in Frontend

| Where | How |
|-------|-----|
| CSS animations | `cubic-bezier()` easing function |
| SVG paths | `C` and `Q` commands in `d` attribute |
| Figma / design tools | Every curved shape is bezier curves |
| Canvas drawing | `ctx.bezierCurveTo(c1x, c1y, c2x, c2y, x, y)` |
| Font rendering | Every letter is made of bezier curves |
| Graph edges | Curved lines between nodes |
| Motion paths | Objects following smooth trajectories |
| Data viz | Smooth line charts (D3 `d3.curveBasis`) |

---

## Summary

| Type | Points | SVG Command | Use |
|------|--------|-------------|-----|
| Linear | 2 (start, end) | `L` | Straight lines |
| Quadratic | 3 (start, control, end) | `Q` | Simple curves |
| Cubic | 4 (start, c1, c2, end) | `C` | Complex smooth curves |

**The mental model:** Control points are magnets. The curve is pulled toward them but never touches. More control points = more curve shaping power.
