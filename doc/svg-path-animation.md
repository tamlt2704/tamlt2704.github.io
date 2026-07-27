# SVG Path Drawing & Following — Framer Motion

---

## Part 1: Drawing Lines (pathLength)

### The Concept

Every SVG shape has a "length" (how far your pen travels to draw it). `pathLength` controls how much is drawn — from 0 (nothing) to 1 (complete).

### Draw a Line on Mount

```tsx
<svg width={500} height={100}>
  <motion.line
    x1={50}
    y1={50}
    x2={450}
    y2={50}
    stroke="hsl(var(--primary))"
    strokeWidth={3}
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 2 }}
  />
</svg>
```

### Control Progress with State

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export function DrawingDemo() {
  const [progress, setProgress] = useState(0)

  return (
    <div className="flex flex-col items-center gap-4">
      <svg width={500} height={100}>
        <motion.line
          x1={50} y1={50} x2={450} y2={50}
          stroke="hsl(var(--primary))"
          strokeWidth={3}
          strokeLinecap="round"
          animate={{ pathLength: progress }}
          transition={{ duration: 0.5 }}
        />
      </svg>

      <div className="flex gap-2">
        <button onClick={() => setProgress(0)} className="rounded bg-muted px-3 py-1">0%</button>
        <button onClick={() => setProgress(0.25)} className="rounded bg-muted px-3 py-1">25%</button>
        <button onClick={() => setProgress(0.5)} className="rounded bg-muted px-3 py-1">50%</button>
        <button onClick={() => setProgress(0.75)} className="rounded bg-muted px-3 py-1">75%</button>
        <button onClick={() => setProgress(1)} className="rounded bg-muted px-3 py-1">100%</button>
      </div>
    </div>
  )
}
```

### Draw a Curved Path

```tsx
<svg width={500} height={200}>
  <motion.path
    d="M 50 150 C 100 50, 200 50, 250 150 S 400 250, 450 150"
    fill="none"
    stroke="hsl(var(--primary))"
    strokeWidth={3}
    strokeLinecap="round"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 2, ease: "easeInOut" }}
  />
</svg>
```

### Draw Multiple Paths Sequentially

```tsx
const paths = [
  "M 50 50 L 200 50",
  "M 200 50 L 200 150",
  "M 200 150 L 350 150",
]

<svg width={400} height={200}>
  {paths.map((d, index) => (
    <motion.path
      key={index}
      d={d}
      fill="none"
      stroke="hsl(var(--primary))"
      strokeWidth={3}
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{
        duration: 0.8,
        delay: index * 0.8,  // each path starts after the previous finishes
      }}
    />
  ))}
</svg>
```

### Draw + Erase Loop

```tsx
<motion.path
  d="M 50 100 Q 250 20, 450 100"
  fill="none"
  stroke="hsl(var(--primary))"
  strokeWidth={3}
  animate={{ pathLength: [0, 1, 1, 0] }}
  transition={{
    duration: 3,
    times: [0, 0.4, 0.6, 1],  // draw 0-40%, hold 40-60%, erase 60-100%
    repeat: Infinity,
  }}
/>
```

### Works on Any SVG Shape

| Element | Example |
|---------|---------|
| `<line>` | Straight line between two points |
| `<path>` | Any shape — curves, complex paths |
| `<circle>` | Draws the circle outline progressively |
| `<rect>` | Draws the rectangle border |
| `<polyline>` | Connected line segments |
| `<polygon>` | Closed shape outline |

```tsx
// Circle drawing itself
<motion.circle
  cx={100} cy={100} r={50}
  fill="none"
  stroke="hsl(var(--primary))"
  strokeWidth={3}
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 1.5 }}
/>

// Rectangle drawing itself
<motion.rect
  x={50} y={50} width={200} height={100} rx={10}
  fill="none"
  stroke="hsl(var(--primary))"
  strokeWidth={3}
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 2 }}
/>
```

---

## Part 2: Following a Path (Object Moving Along a Line)

### The Concept

An element (dot, icon, car) moves along a predefined SVG path. The path acts as a track.

### Method 1: CSS offset-path (Simplest)

CSS has `offset-path` — place an element on a path and animate `offset-distance`:

```tsx
"use client"

import { motion } from "motion/react"

export function FollowPath() {
  const path = "M 50 200 C 100 50, 200 50, 250 200 S 400 350, 450 200"

  return (
    <div className="relative h-[400px] w-[500px]">
      {/* The path (visible guide line) */}
      <svg className="absolute inset-0" width={500} height={400}>
        <path
          d={path}
          fill="none"
          stroke="hsl(var(--border))"
          strokeWidth={2}
          strokeDasharray="5 5"
        />
      </svg>

      {/* The moving object */}
      <motion.div
        className="absolute h-6 w-6 rounded-full bg-primary"
        style={{
          offsetPath: `path("${path}")`,
          offsetRotate: "0deg",
        }}
        animate={{ offsetDistance: ["0%", "100%"] }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear",
        }}
      />
    </div>
  )
}
```

**Key CSS properties:**

| Property | What it does |
|----------|-------------|
| `offsetPath` | The path to follow (same `d` value as SVG path) |
| `offsetDistance` | How far along the path: 0% → 100% |
| `offsetRotate` | Rotate to face direction (`auto`) or fixed (`0deg`) |

### Method 2: `offsetRotate: "auto"` (Face the Direction)

```tsx
style={{
  offsetPath: `path("${path}")`,
  offsetRotate: "auto",  // element rotates to follow the curve
}}
```

This makes an arrow/car/character face the direction of travel — like a train on a track.

### Method 3: Manual Path Interpolation (Full Control)

When you need to control speed, pause, or react to events:

```tsx
"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "motion/react"

export function ManualFollowPath() {
  const pathRef = useRef<SVGPathElement>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!pathRef.current) return
    const path = pathRef.current
    const totalLength = path.getTotalLength()

    // Get point at current progress
    const point = path.getPointAtLength(totalLength * progress)
    setPosition({ x: point.x, y: point.y })
  }, [progress])

  // Animate progress from 0 to 1
  useEffect(() => {
    let frame: number
    let p = 0

    function step() {
      p += 0.005  // speed
      if (p > 1) p = 0  // loop
      setProgress(p)
      frame = requestAnimationFrame(step)
    }

    frame = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frame)
  }, [])

  const pathD = "M 50 200 C 100 50, 200 50, 250 200 S 400 350, 450 200"

  return (
    <svg width={500} height={400}>
      {/* The track */}
      <path
        ref={pathRef}
        d={pathD}
        fill="none"
        stroke="hsl(var(--border))"
        strokeWidth={2}
      />

      {/* The follower */}
      <motion.circle
        cx={position.x}
        cy={position.y}
        r={10}
        className="fill-primary"
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 0.5, repeat: Infinity }}
      />
    </svg>
  )
}
```

**The magic method:** `path.getPointAtLength(distance)` — give it a distance along the path, get back an `{x, y}` coordinate.

### Method 4: Multiple Objects on the Same Path

```tsx
const followers = [
  { id: 1, offset: 0 },      // start of path
  { id: 2, offset: 0.33 },   // 1/3 along
  { id: 3, offset: 0.66 },   // 2/3 along
]

{followers.map(f => {
  const adjustedProgress = (progress + f.offset) % 1
  const point = pathRef.current!.getPointAtLength(totalLength * adjustedProgress)

  return (
    <motion.circle
      key={f.id}
      cx={point.x}
      cy={point.y}
      r={8}
      className="fill-primary"
    />
  )
})}
```

Like a train with carriages — all following the same track, spaced apart.

---

## Part 3: Drawing + Following Combined

### Draw the Path, Then Follow It

```tsx
const [phase, setPhase] = useState<"drawing" | "following">("drawing")

{/* Path that draws itself */}
<motion.path
  d={pathD}
  fill="none"
  stroke="hsl(var(--primary))"
  strokeWidth={2}
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 2 }}
  onAnimationComplete={() => setPhase("following")}  // start following after drawing
/>

{/* Dot that follows the path (only after drawing completes) */}
{phase === "following" && (
  <motion.div
    style={{ offsetPath: `path("${pathD}")` }}
    animate={{ offsetDistance: ["0%", "100%"] }}
    transition={{ duration: 3, repeat: Infinity }}
  />
)}
```

### Draw Behind the Follower (Trail Effect)

The path draws as the dot moves — like the dot is leaving a trail:

```tsx
<motion.path
  d={pathD}
  fill="none"
  stroke="hsl(var(--primary))"
  strokeWidth={2}
  animate={{ pathLength: progress }}  // path draws up to where the dot is
  transition={{ duration: 0.1 }}
/>

<motion.circle
  cx={position.x}
  cy={position.y}
  r={8}
  className="fill-primary"
/>
```

---

## Part 4: Use Cases for Algorithm Visualisation

### Tree Traversal — Draw Edges as You Visit

```tsx
async function traverseAndDraw(node: TreeNode) {
  if (!node || !node.left) return

  // Draw edge from parent to child
  setEdgeProgress(prev => ({
    ...prev,
    [`${node.id}-${node.left!.id}`]: 0,
  }))

  // Animate the edge drawing
  for (let p = 0; p <= 1; p += 0.1) {
    setEdgeProgress(prev => ({
      ...prev,
      [`${node.id}-${node.left!.id}`]: p,
    }))
    await sleep(50)
  }

  // Then visit the child
  await traverseAndDraw(node.left)
}
```

### Graph — Highlight the Path Found

After BFS finds the shortest path, draw it:

```tsx
async function drawPath(path: string[]) {
  for (let i = 0; i < path.length - 1; i++) {
    const key = `${path[i]}-${path[i + 1]}`

    // Animate edge from 0 to 1
    for (let p = 0; p <= 1; p += 0.05) {
      setEdgeProgress(prev => ({ ...prev, [key]: p }))
      await sleep(30)
    }

    // Then highlight the destination node
    updateNode(path[i + 1], "path")
    await sleep(200)
  }
}
```

### Data Flow — Show Data Moving Between Services

```tsx
// Animate a packet moving from Service A → Queue → Service B
const steps = [
  { from: serviceA, to: queue, label: "Request" },
  { from: queue, to: serviceB, label: "Process" },
  { from: serviceB, to: serviceA, label: "Response" },
]

async function animateFlow() {
  for (const step of steps) {
    // Draw line from → to
    // Then animate a dot along that line
    // Then show the label
    await sleep(1000)
  }
}
```

---

## SVG Path `d` Cheat Sheet

| Command | Meaning | Example |
|---------|---------|---------|
| `M x y` | Move to (start point) | `M 50 50` |
| `L x y` | Line to | `L 200 50` |
| `H x` | Horizontal line to | `H 200` |
| `V y` | Vertical line to | `V 150` |
| `C x1 y1, x2 y2, x y` | Cubic bezier curve | `C 100 10, 200 10, 250 100` |
| `S x2 y2, x y` | Smooth cubic (mirrors previous handle) | `S 400 200, 450 100` |
| `Q x1 y1, x y` | Quadratic bezier | `Q 150 10, 250 100` |
| `A rx ry rot large sweep x y` | Arc | `A 50 50 0 0 1 200 200` |
| `Z` | Close path (line back to start) | `Z` |

**Uppercase = absolute coordinates. Lowercase = relative (offset from current point).**

### How to Get Path Data

| Method | When |
|--------|------|
| Write by hand | Simple lines, basic curves |
| Figma → Export as SVG → copy `d` | Complex shapes |
| [SVG Path Editor](https://yqnn.github.io/svg-path-editor/) | Interactive visual editor |
| Generate in code | Dynamic paths (e.g. graph edges) |

### Generate a Path Between Two Points (with a Curve)

```tsx
function curvedPath(x1: number, y1: number, x2: number, y2: number): string {
  const midX = (x1 + x2) / 2
  const midY = (y1 + y2) / 2
  const curveOffset = Math.abs(x2 - x1) * 0.2  // 20% curve

  return `M ${x1} ${y1} Q ${midX} ${midY - curveOffset}, ${x2} ${y2}`
}

// Usage: edge between two nodes
const d = curvedPath(nodeA.x, nodeA.y, nodeB.x, nodeB.y)
```
