# Framer Motion — Matrix, Graph, Tree, Physics

Beyond sorting arrays — how to animate complex data structures.

Each step introduces **one thing** and stays under ~20 lines of code.

---

## The Core Pattern (Same Every Time)

```
1. State holds your data structure (grid, graph, tree)
2. You change the state one step at a time
3. Framer Motion animates between the old and new state
```

You already know this from bubble sort. The only difference is the shape of the data.

| Data structure | Shape | Rendering |
|---------------|-------|-----------|
| Array | `number[]` | Bars (divs) |
| Grid/Matrix | `string[][]` | CSS Grid of cells |
| Graph | `{ nodes, edges }` | SVG circles + lines |
| Tree | Nested `{ left, right }` | SVG circles + lines |

---

## Matrix (2D Grid)

Good for: pathfinding (BFS, A*), Game of Life, flood fill.

---

### Step M1: Just Show a Grid

No state. No animation. Just squares on screen.

```tsx
"use client"

export default function MatrixPage() {
  const rows = 8
  const cols = 10

  return (
    <div className="inline-grid gap-[2px]"
      style={{ gridTemplateColumns: `repeat(${cols}, 28px)` }}
    >
      {Array.from({ length: rows * cols }, (_, i) => (
        <div key={i} className="h-7 w-7 rounded-sm bg-muted" />
      ))}
    </div>
  )
}
```

**Why `style` instead of Tailwind?** `cols` is a variable. Tailwind can't generate `grid-cols-10` at runtime — it needs to know at build time. So we use inline style for the dynamic part.

**Why `Array.from`?** Creates an array of the right length and maps each index to a cell. Same pattern as creating a grid for Game of Life.

---

### Step M2: Give Each Cell a State

Now each cell can be `"empty"`, `"wall"`, `"visited"`, etc. We store the grid as a 2D array.

```tsx
"use client"

import { useState } from "react"

type CellState = "empty" | "wall" | "visited" | "start" | "end"

const COLORS: Record<CellState, string> = {
  empty: "bg-muted",
  wall: "bg-foreground",
  visited: "bg-blue-400",
  start: "bg-green-500",
  end: "bg-red-500",
}

export default function MatrixPage() {
  const rows = 8
  const cols = 10

  const [grid, setGrid] = useState(() =>
    Array.from({ length: rows }, () =>
      Array.from({ length: cols }, (): CellState => "empty")
    )
  )

  return (
    <div className="inline-grid gap-[2px]"
      style={{ gridTemplateColumns: `repeat(${cols}, 28px)` }}
    >
      {grid.flat().map((cell, i) => (
        <div key={i} className={`h-7 w-7 rounded-sm ${COLORS[cell]}`} />
      ))}
    </div>
  )
}
```

**Why `Record<CellState, string>`?** It's a TypeScript type that says "an object with exactly one key for each CellState, and each value is a string." If you forget a color, TypeScript will complain.

**Why `grid.flat()`?** `grid` is 2D (array of arrays). CSS Grid is flat — it just needs all cells in order. `.flat()` turns `[[a,b],[c,d]]` into `[a,b,c,d]`.

---

### Step M3: Click to Draw Walls

One new thing: click a cell → toggle between empty and wall.

```tsx
function toggleCell(row: number, col: number) {
  setGrid(prev => {
    const next = prev.map(r => [...r])
    next[row][col] = next[row][col] === "wall" ? "empty" : "wall"
    return next
  })
}
```

And change the rendering to know each cell's position:

```tsx
{grid.map((row, r) =>
  row.map((cell, c) => (
    <div
      key={`${r}-${c}`}
      className={`h-7 w-7 rounded-sm cursor-pointer ${COLORS[cell]}`}
      onClick={() => toggleCell(r, c)}
    />
  ))
)}
```

**Why `prev.map(r => [...r])`?** Never mutate state directly in React. This creates a shallow copy of the grid, then we change one cell in the copy.

**Try it:** Click cells to draw walls. Click again to erase.

---

### Step M4: Click-and-Drag to Paint

One new thing: hold mouse down and drag to paint multiple walls.

```tsx
const [drawing, setDrawing] = useState(false)

<div
  key={`${r}-${c}`}
  className={`h-7 w-7 rounded-sm cursor-pointer ${COLORS[cell]}`}
  onMouseDown={() => { setDrawing(true); toggleCell(r, c) }}
  onMouseEnter={() => { if (drawing) toggleCell(r, c) }}
  onMouseUp={() => setDrawing(false)}
/>
```

Add `onMouseLeave={() => setDrawing(false)}` on the grid container so dragging outside stops painting.

**Why three events?** `mousedown` starts painting, `mouseenter` paints as you drag into each cell, `mouseup` stops. This is how every drawing app works.

---

### Step M5: Add Framer Motion (Cells Animate)

One new thing: cells "pop" when their state changes.

```tsx
import { motion } from "motion/react"

<motion.div
  key={`${r}-${c}`}
  className={`h-7 w-7 rounded-sm cursor-pointer ${COLORS[cell]}`}
  animate={{
    scale: cell === "visited" ? [1, 1.3, 1] : 1,
  }}
  transition={{ duration: 0.3 }}
  onMouseDown={() => { setDrawing(true); toggleCell(r, c) }}
  onMouseEnter={() => { if (drawing) toggleCell(r, c) }}
/>
```

**Why `scale: [1, 1.3, 1]`?** This is a keyframe array — the cell starts at normal size, grows to 1.3×, then shrinks back. It creates a "pop" effect when a cell becomes visited.

**Why `duration: 0.3`?** Controls how long the pop takes. 0.3 seconds is fast enough to feel responsive but slow enough to see.

---

### Step M6: BFS Algorithm (One Step at a Time)

Like bubble sort's "Next Step" button. One click = explore one cell.

First, the state we need to track BFS:

```tsx
const [queue, setQueue] = useState<[number, number][]>([[0, 0]])
const [visited, setVisited] = useState<Set<string>>(new Set(["0,0"]))
```

Then one step of BFS:

```tsx
function stepBFS() {
  if (queue.length === 0) return

  const [r, c] = queue[0]
  const newQueue = [...queue.slice(1)]
  const newVisited = new Set(visited)

  // Mark current cell
  setGrid(prev => {
    const next = prev.map(row => [...row])
    if (next[r][c] === "empty") next[r][c] = "visited"
    return next
  })

  // Add unvisited neighbors to queue
  for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
    const nr = r + dr, nc = c + dc
    const key = `${nr},${nc}`
    if (nr >= 0 && nr < 8 && nc >= 0 && nc < 10
      && !newVisited.has(key) && grid[nr][nc] !== "wall") {
      newVisited.add(key)
      newQueue.push([nr, nc])
    }
  }

  setQueue(newQueue)
  setVisited(newVisited)
}
```

**Why a queue?** BFS explores cells level-by-level (like ripples in a pond). The queue holds "cells to visit next." We always take from the front and add to the back.

**Why a Set for visited?** Fast lookup — `Set.has()` is O(1). We store `"row,col"` strings as keys.

---

### Step M7: Auto-Play

One new thing: run `stepBFS` on an interval.

```tsx
const [playing, setPlaying] = useState(false)
const [speed, setSpeed] = useState(100)

useEffect(() => {
  if (!playing || queue.length === 0) return
  const timer = setTimeout(stepBFS, speed)
  return () => clearTimeout(timer)
}, [playing, queue, speed])
```

**Why `setTimeout` not `setInterval`?** `setTimeout` runs once, then the effect re-fires when `queue` changes (because it's a dependency). This means each step waits for the previous one to finish. `setInterval` can pile up calls if a step takes too long.

**Why `return () => clearTimeout(timer)`?** Cleanup. If the component re-renders or `playing` becomes false, we cancel the pending timeout. Without this, old timers keep running.

Controls:

```tsx
<button onClick={() => setPlaying(!playing)}>
  {playing ? "⏸ Pause" : "▶ Play"}
</button>
<button onClick={stepBFS} disabled={playing}>Step →</button>
<input type="range" min={20} max={300} value={speed}
  onChange={(e) => setSpeed(Number(e.target.value))} />
```

---

### Matrix Summary

| Step | One thing added | Lines |
|------|----------------|-------|
| M1 | Static grid (CSS Grid) | ~12 |
| M2 | Cell state + color map | ~20 |
| M3 | Click to toggle walls | ~10 |
| M4 | Drag to paint | ~8 |
| M5 | Framer Motion pop animation | ~10 |
| M6 | BFS one-step-at-a-time | ~20 |
| M7 | Auto-play with setTimeout | ~12 |

---


## Graph (Nodes + Edges)

Good for: BFS/DFS traversal, Dijkstra, topological sort, connected components.

**Why SVG?** Graphs have lines between nodes. You can't draw a line between two `<div>`s. SVG gives you `<line>`, `<circle>`, and exact `x,y` positioning.

---

### Step G1: Define the Data

Just data — no rendering yet. Nodes have positions, edges connect node IDs.

```tsx
interface Node {
  id: string
  x: number
  y: number
}

interface Edge {
  from: string
  to: string
}

const nodes: Node[] = [
  { id: "A", x: 80, y: 150 },
  { id: "B", x: 220, y: 60 },
  { id: "C", x: 360, y: 60 },
  { id: "D", x: 220, y: 240 },
  { id: "E", x: 360, y: 240 },
  { id: "F", x: 500, y: 150 },
]

const edges: Edge[] = [
  { from: "A", to: "B" },
  { from: "A", to: "D" },
  { from: "B", to: "C" },
  { from: "D", to: "E" },
  { from: "C", to: "F" },
  { from: "E", to: "F" },
]
```

**Why give nodes `x, y`?** Graphs don't have a natural layout like grids. You choose where to place them. Later you could auto-layout, but manual positions are simplest to start.

---

### Step G2: Render Nodes (Circles)

One thing: draw circles with labels inside.

```tsx
"use client"

export default function GraphPage() {
  return (
    <svg width={580} height={300} className="rounded-lg border bg-card">
      {nodes.map((node) => (
        <g key={node.id}>
          <circle cx={node.x} cy={node.y} r={22} fill="hsl(var(--primary))" />
          <text x={node.x} y={node.y + 5} textAnchor="middle"
            fill="white" fontSize={14} fontWeight="bold">
            {node.id}
          </text>
        </g>
      ))}
    </svg>
  )
}
```

**Why `<g>`?** SVG group element — keeps the circle and text together as one unit. Like a `<div>` wrapper but for SVG.

**Why `y={node.y + 5}`?** Text in SVG is positioned by its baseline (bottom), not center. Adding 5px nudges it to look vertically centered inside the circle.

---

### Step G3: Render Edges (Lines)

One thing: draw lines between connected nodes.

```tsx
<svg width={580} height={300} className="rounded-lg border bg-card">
  {/* Edges FIRST — so they render behind nodes */}
  {edges.map((edge) => {
    const from = nodes.find(n => n.id === edge.from)!
    const to = nodes.find(n => n.id === edge.to)!
    return (
      <line key={`${edge.from}-${edge.to}`}
        x1={from.x} y1={from.y} x2={to.x} y2={to.y}
        stroke="grey" strokeWidth={2} opacity={0.4}
      />
    )
  })}

  {/* Nodes on top */}
  {nodes.map((node) => (
    <g key={node.id}>
      <circle cx={node.x} cy={node.y} r={22} fill="hsl(var(--primary))" />
      <text x={node.x} y={node.y + 5} textAnchor="middle"
        fill="white" fontSize={14} fontWeight="bold">
        {node.id}
      </text>
    </g>
  ))}
</svg>
```

**Why edges first?** SVG draws in order — later elements are on top. We want nodes to cover the line endpoints.

**Why `opacity={0.4}`?** Makes edges subtle so the nodes stand out. They'll become bright when traversed.

---

### Step G4: Add State (Color Nodes Differently)

One thing: each node can be `"default"`, `"visiting"`, or `"visited"`.

```tsx
import { useState } from "react"

type NodeState = "default" | "visiting" | "visited"

const NODE_COLORS: Record<NodeState, string> = {
  default: "hsl(var(--primary))",
  visiting: "#facc15",
  visited: "#3b82f6",
}

export default function GraphPage() {
  const [nodeStates, setNodeStates] = useState<Record<string, NodeState>>(
    Object.fromEntries(nodes.map(n => [n.id, "default"]))
  )

  // In the circle:
  // fill={NODE_COLORS[nodeStates[node.id]]}
}
```

**Why `Object.fromEntries`?** Turns `[["A","default"],["B","default"],...]` into `{ A: "default", B: "default", ... }`. Quick way to init a lookup object from an array.

**Why a separate `nodeStates` object instead of putting state inside the node data?** Keeps data (positions, IDs) separate from algorithm state (visiting/visited). Easier to reset.

---

### Step G5: Add Framer Motion (Nodes Pulse)

One thing: the "visiting" node scales up smoothly.

```tsx
import { motion } from "motion/react"

<motion.circle
  cx={node.x} cy={node.y} r={22}
  fill={NODE_COLORS[nodeStates[node.id]]}
  animate={{
    scale: nodeStates[node.id] === "visiting" ? 1.4 : 1,
  }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>
```

**Why `type: "spring"`?** Springs feel natural — they overshoot slightly then settle. A linear animation feels robotic.

**Why `stiffness: 300`?** Higher = snappier. 300 gives a quick pop. Try 100 for a slow wobble, 500 for instant snap.

**Why `damping: 20`?** Controls how fast the bounce stops. Low (5) = bounces forever. High (30) = barely bounces. 20 = one nice bounce then done.

---

### Step G6: BFS One Step at a Time

One thing: click "Step" to visit the next node in BFS order.

```tsx
const [queue, setQueue] = useState<string[]>(["A"])
const [visitedSet, setVisitedSet] = useState<Set<string>>(new Set(["A"]))

function getNeighbors(id: string): string[] {
  return edges
    .filter(e => e.from === id || e.to === id)
    .map(e => e.from === id ? e.to : e.from)
}

function stepBFS() {
  if (queue.length === 0) return

  const current = queue[0]
  const newQueue = queue.slice(1)

  // Mark current as visited
  setNodeStates(prev => ({ ...prev, [current]: "visited" }))

  // Add unvisited neighbors
  for (const neighbor of getNeighbors(current)) {
    if (!visitedSet.has(neighbor)) {
      visitedSet.add(neighbor)
      newQueue.push(neighbor)
      setNodeStates(prev => ({ ...prev, [neighbor]: "visiting" }))
    }
  }

  setQueue(newQueue)
  setVisitedSet(new Set(visitedSet))
}
```

**Why `queue.slice(1)`?** Removes the first element (the one we just processed). BFS always takes from the front of the queue.

**Why mark neighbors as "visiting"?** They're in the queue — discovered but not yet processed. Yellow = "I know about you, coming soon." Blue = "Done with you."

Add auto-play the same way as the matrix (setTimeout + playing state).

---

### Graph Summary

| Step | One thing added | Lines |
|------|----------------|-------|
| G1 | Define node/edge data | ~18 |
| G2 | Draw circles in SVG | ~14 |
| G3 | Draw lines between nodes | ~15 |
| G4 | State for node colors | ~12 |
| G5 | Framer Motion pulse | ~8 |
| G6 | BFS step-by-step | ~20 |

---


## Tree (Binary Tree)

Good for: BST insert/search, traversals (inorder, preorder, postorder), heap operations.

**The tricky part:** trees need calculated positions so children don't overlap. We'll do that one step at a time.

---

### Step T1: Define a Tree Node

Just the data. A node has a value, optional left/right children.

```tsx
interface TreeNode {
  id: string
  value: number
  left?: TreeNode
  right?: TreeNode
}

const sampleTree: TreeNode = {
  id: "1", value: 50,
  left: {
    id: "2", value: 30,
    left: { id: "4", value: 20 },
    right: { id: "5", value: 40 },
  },
  right: {
    id: "3", value: 70,
    left: { id: "6", value: 60 },
    right: { id: "7", value: 80 },
  },
}
```

**Why `id` separate from `value`?** Two nodes could have the same value. The `id` is a unique identifier for React's `key` prop and for tracking animation state.

---

### Step T2: Calculate Positions (Layout)

One thing: assign `x, y` to each node so the tree looks like a tree.

```tsx
interface PositionedNode {
  id: string
  value: number
  x: number
  y: number
  left?: PositionedNode
  right?: PositionedNode
}

function layoutTree(
  node: TreeNode | undefined,
  x: number,
  y: number,
  spread: number
): PositionedNode | undefined {
  if (!node) return undefined
  return {
    ...node,
    x,
    y,
    left: layoutTree(node.left, x - spread, y + 70, spread / 2),
    right: layoutTree(node.right, x + spread, y + 70, spread / 2),
  }
}

// Usage:
const tree = layoutTree(sampleTree, 300, 40, 120)
```

**Why `spread / 2` each level?** The root's children are 120px apart. Their children are 60px apart. This prevents overlap — lower levels have less horizontal room.

**Why `y + 70`?** Each level is 70px below the parent. Gives enough room for the circle + line.

---

### Step T3: Flatten the Tree for Rendering

SVG needs flat arrays — not nested objects. Extract all nodes and edges.

```tsx
function flattenTree(node: PositionedNode | undefined): {
  nodes: PositionedNode[]
  edges: { from: PositionedNode; to: PositionedNode }[]
} {
  if (!node) return { nodes: [], edges: [] }

  const nodes: PositionedNode[] = [node]
  const edges: { from: PositionedNode; to: PositionedNode }[] = []

  if (node.left) {
    edges.push({ from: node, to: node.left })
    const sub = flattenTree(node.left)
    nodes.push(...sub.nodes)
    edges.push(...sub.edges)
  }
  if (node.right) {
    edges.push({ from: node, to: node.right })
    const sub = flattenTree(node.right)
    nodes.push(...sub.nodes)
    edges.push(...sub.edges)
  }

  return { nodes, edges }
}
```

**Why flatten?** You can't `.map()` over a nested tree directly. Flattening gives you `nodes[]` and `edges[]` that you can loop over in JSX — same as the graph section.

---

### Step T4: Render the Tree (SVG)

Same as graph — lines for edges, circles for nodes.

```tsx
"use client"

export default function TreePage() {
  const positioned = layoutTree(sampleTree, 300, 40, 120)
  const { nodes, edges } = flattenTree(positioned)

  return (
    <svg width={600} height={320} className="rounded-lg border bg-card">
      {edges.map(({ from, to }) => (
        <line key={`${from.id}-${to.id}`}
          x1={from.x} y1={from.y} x2={to.x} y2={to.y}
          stroke="grey" strokeWidth={2} opacity={0.5}
        />
      ))}
      {nodes.map((node) => (
        <g key={node.id}>
          <circle cx={node.x} cy={node.y} r={20}
            fill="hsl(var(--primary))" />
          <text x={node.x} y={node.y + 5} textAnchor="middle"
            fill="white" fontSize={12} fontWeight="bold">
            {node.value}
          </text>
        </g>
      ))}
    </svg>
  )
}
```

**What you see:** A proper binary tree with 50 at the root, 30/70 below, 20/40/60/80 at the leaves.

---

### Step T5: Add Node State (Color by Visit Status)

Same pattern as graph — a lookup object mapping node ID → state.

```tsx
import { useState } from "react"

type NodeState = "default" | "visiting" | "visited"

const COLORS: Record<NodeState, string> = {
  default: "hsl(var(--primary))",
  visiting: "#facc15",
  visited: "#3b82f6",
}

const [nodeStates, setNodeStates] = useState<Record<string, NodeState>>(
  Object.fromEntries(nodes.map(n => [n.id, "default"]))
)

// In the circle:
<circle cx={node.x} cy={node.y} r={20}
  fill={COLORS[nodeStates[node.id]]} />
```

Nothing new here — exact same pattern as Step G4 for graphs.

---

### Step T6: Add Framer Motion (Nodes Pulse)

```tsx
import { motion } from "motion/react"

<motion.circle
  cx={node.x} cy={node.y} r={20}
  fill={COLORS[nodeStates[node.id]]}
  animate={{ scale: nodeStates[node.id] === "visiting" ? 1.4 : 1 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>
```

Same as Step G5 for graphs. The currently-visited node pops out.

---

### Step T7: Inorder Traversal (Step-by-Step)

One thing: walk the tree left → node → right, one step at a time.

The trick: recursive traversals don't naturally "pause." So we pre-compute the visit order, then step through it.

```tsx
function inorderSequence(node: PositionedNode | undefined): string[] {
  if (!node) return []
  return [
    ...inorderSequence(node.left),
    node.id,
    ...inorderSequence(node.right),
  ]
}

const [sequence] = useState(() => inorderSequence(positioned!))
const [step, setStep] = useState(0)

function nextStep() {
  if (step >= sequence.length) return

  // Mark previous as visited
  if (step > 0) {
    setNodeStates(prev => ({ ...prev, [sequence[step - 1]]: "visited" }))
  }
  // Mark current as visiting
  setNodeStates(prev => ({ ...prev, [sequence[step]]: "visiting" }))
  setStep(step + 1)
}
```

**Why pre-compute the sequence?** Recursive functions don't pause mid-execution. By computing the full order upfront `[4, 2, 5, 1, 6, 3, 7]`, we can step through it one-at-a-time with a simple index.

**Why mark previous as "visited"?** Each step: the old "visiting" node turns blue (done), the new one turns yellow (current). This shows the traversal moving through the tree.

Add auto-play with the same setTimeout + playing pattern from before.

---

### Tree Summary

| Step | One thing added | Lines |
|------|----------------|-------|
| T1 | Define tree data structure | ~16 |
| T2 | Calculate node positions | ~18 |
| T3 | Flatten tree into arrays | ~20 |
| T4 | Render with SVG | ~18 |
| T5 | Node state + colors | ~12 |
| T6 | Framer Motion pulse | ~6 |
| T7 | Inorder traversal stepping | ~16 |

---


## Physics Simulations

Good for: gravity, bouncing balls, springs, particles, pendulums.

**Two approaches:**
1. **Framer Motion springs** — for simple single-element physics (a button bounce, one draggable ball)
2. **Manual physics loop** — for multiple objects interacting (collisions, gravity on many objects)

---

### Step P1: Framer Motion Spring (Simplest Physics)

One thing: a ball that bounces when clicked.

```tsx
"use client"

import { motion, useSpring } from "motion/react"

export default function PhysicsPage() {
  const y = useSpring(0, { stiffness: 100, damping: 5 })

  return (
    <div className="relative h-[400px]">
      <motion.div
        className="absolute left-1/2 h-12 w-12 -translate-x-1/2 rounded-full bg-primary"
        style={{ y }}
        onClick={() => y.set(300)}
      />
    </div>
  )
}
```

**Why `useSpring`?** Creates an animated value that behaves like a physical spring. When you `.set(300)`, it doesn't jump — it springs to 300 and bounces.

**Why `stiffness: 100`?** How strongly the spring pulls toward the target. Low (30) = slow, floaty. High (500) = snappy.

**Why `damping: 5`?** How fast the bouncing stops. Low (2) = bounces forever. High (30) = barely bounces. 5 = several bounces before settling.

| stiffness | damping | Feels like |
|-----------|---------|-----------|
| 500 | 5 | Rubber ball |
| 500 | 30 | Snappy UI element |
| 50 | 5 | Slow jelly |
| 50 | 30 | Heavy, no bounce |

---

### Step P2: Define a Ball (Data for Manual Physics)

One thing: a ball has position + velocity.

```tsx
interface Ball {
  id: number
  x: number
  y: number
  vx: number  // velocity x (pixels per frame)
  vy: number  // velocity y (pixels per frame)
  radius: number
}
```

**Why velocity?** Position tells you WHERE the ball is. Velocity tells you where it's GOING. Each frame: `x += vx`, `y += vy`. That's motion.

---

### Step P3: One Ball Falling (Gravity)

One thing: each frame, add gravity to velocity, add velocity to position.

```tsx
"use client"

import { useState, useEffect, useRef } from "react"

export default function PhysicsPage() {
  const [ball, setBall] = useState({ x: 200, y: 50, vx: 0, vy: 0, radius: 20 })
  const frameRef = useRef<number>()

  useEffect(() => {
    function step() {
      setBall(prev => {
        const gravity = 0.5
        let { x, y, vx, vy, radius } = prev

        vy += gravity       // gravity pulls down
        x += vx             // move horizontally
        y += vy             // move vertically

        return { ...prev, x, y, vx, vy }
      })
      frameRef.current = requestAnimationFrame(step)
    }

    frameRef.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frameRef.current!)
  }, [])

  return (
    <div className="relative h-[400px] w-[400px] border rounded-lg bg-card">
      <div
        className="absolute rounded-full bg-primary"
        style={{
          width: ball.radius * 2,
          height: ball.radius * 2,
          left: ball.x - ball.radius,
          top: ball.y - ball.radius,
        }}
      />
    </div>
  )
}
```

**Why `requestAnimationFrame`?** Runs your function once per screen refresh (~60fps). Smoother than `setInterval` because it syncs with the browser's paint cycle.

**Why `return () => cancelAnimationFrame(...)`?** Cleanup — stops the loop when the component unmounts. Without this, the loop runs forever even after navigating away.

**Why `vy += gravity`?** Gravity is acceleration — it increases velocity each frame. The ball starts slow, gets faster. That's how real falling works.

---

### Step P4: Bounce Off the Floor

One thing: when the ball hits the bottom, reverse its velocity.

```tsx
const height = 400

// After moving:
if (y + radius > height) {
  y = height - radius     // push back inside
  vy = -vy * 0.8          // reverse + lose energy
}
```

**Why `y = height - radius`?** Without this, the ball clips through the floor for one frame. This snaps it back to the edge.

**Why `-vy * 0.8`?** Negating reverses direction (bounce). Multiplying by 0.8 means it loses 20% energy each bounce — so it eventually stops. 1.0 = infinite bounce. 0.5 = dies fast.

---

### Step P5: Bounce Off All Walls

Same idea for every edge:

```tsx
const width = 400
const height = 400
const bounce = 0.8

// Floor
if (y + radius > height) { y = height - radius; vy = -vy * bounce }
// Ceiling
if (y - radius < 0) { y = radius; vy = -vy * bounce }
// Right wall
if (x + radius > width) { x = width - radius; vx = -vx * bounce }
// Left wall
if (x - radius < 0) { x = radius; vx = -vx * bounce }
```

Now give it some horizontal velocity to start: `vx: 3` — and watch it bounce around the box.

---

### Step P6: Multiple Balls

One thing: store an array of balls, update them all each frame.

```tsx
const [balls, setBalls] = useState<Ball[]>([
  { id: 1, x: 100, y: 50, vx: 2, vy: 0, radius: 20 },
  { id: 2, x: 300, y: 80, vx: -1, vy: 1, radius: 15 },
  { id: 3, x: 200, y: 30, vx: 0, vy: 0, radius: 25 },
])

// In the physics step:
setBalls(prev => prev.map(ball => {
  let { x, y, vx, vy, radius } = ball
  vy += 0.5
  x += vx
  y += vy
  // ... bounce logic for each ball
  return { ...ball, x, y, vx, vy }
}))
```

**Why `.map()`?** Creates a new array with each ball updated. Same as updating a grid — never mutate, always return new state.

Render each ball:

```tsx
{balls.map(ball => (
  <div key={ball.id}
    className="absolute rounded-full bg-primary"
    style={{
      width: ball.radius * 2, height: ball.radius * 2,
      left: ball.x - ball.radius, top: ball.y - ball.radius,
    }}
  />
))}
```

---

### Step P7: Click to Add Balls

One thing: click anywhere in the box → spawn a ball there.

```tsx
function addBall(e: React.MouseEvent<HTMLDivElement>) {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  setBalls(prev => [...prev, {
    id: Date.now(),
    x,
    y,
    vx: (Math.random() - 0.5) * 6,
    vy: -3,
    radius: 10 + Math.random() * 15,
  }])
}

<div onClick={addBall} className="relative h-[400px] w-[400px] ...">
```

**Why `e.clientX - rect.left`?** Converts screen coordinates to coordinates inside the box. `clientX` is relative to the viewport, `rect.left` is where the box starts.

**Why `Math.random() - 0.5`?** Gives a random number between -0.5 and 0.5. Multiply by 6 → random velocity between -3 and 3. Some balls go left, some right.

---

### Step P8: Ball-to-Ball Collision (Advanced)

One thing: detect when two balls overlap, bounce them apart.

```tsx
function handleCollisions(balls: Ball[]): Ball[] {
  for (let i = 0; i < balls.length; i++) {
    for (let j = i + 1; j < balls.length; j++) {
      const dx = balls[j].x - balls[i].x
      const dy = balls[j].y - balls[i].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      const minDist = balls[i].radius + balls[j].radius

      if (dist < minDist) {
        // Normal direction
        const nx = dx / dist
        const ny = dy / dist

        // Relative velocity
        const dvx = balls[i].vx - balls[j].vx
        const dvy = balls[i].vy - balls[j].vy
        const dot = dvx * nx + dvy * ny

        // Swap velocity along collision axis
        balls[i].vx -= dot * nx
        balls[i].vy -= dot * ny
        balls[j].vx += dot * nx
        balls[j].vy += dot * ny
      }
    }
  }
  return balls
}
```

**Why `Math.sqrt(dx*dx + dy*dy)`?** Pythagorean theorem — the distance between two points. If it's less than both radii combined, they're overlapping.

**Why the dot product?** It calculates how much velocity is along the collision axis. We only swap velocity in that direction — tangent velocity stays the same. This is how elastic collisions work in real physics.

Call this in your physics step: `handleCollisions(updatedBalls)` before returning.

---

### Physics Summary

| Step | One thing added | Lines |
|------|----------------|-------|
| P1 | Framer Motion spring (click to bounce) | ~12 |
| P2 | Ball data structure | ~8 |
| P3 | One ball falling (gravity + rAF loop) | ~20 |
| P4 | Bounce off floor | ~4 |
| P5 | Bounce off all walls | ~8 |
| P6 | Multiple balls | ~12 |
| P7 | Click to spawn balls | ~14 |
| P8 | Ball-to-ball collision | ~20 |

---


## When to Use What

| Visualisation | Render with | Why |
|--------------|-------------|-----|
| Array sorting | `motion.div` + `layout` | Elements swap positions — `layout` handles it |
| Grid/Matrix | `motion.div` in CSS Grid | Color/scale changes per cell |
| Graph | SVG `motion.circle` + `motion.line` | Need lines between nodes |
| Tree | SVG (same as graph) | Need edges + precise positioning |
| Physics (1-3 objects) | Framer Motion `useSpring` | Simple, no collision needed |
| Physics (many objects) | `requestAnimationFrame` loop | Need full control of velocity/gravity |
| Particles (100+) | Canvas API | DOM can't handle 100+ elements smoothly |

### The Performance Boundary

| How many things moving? | Use |
|------------------------|-----|
| < 50 | `motion.div` (DOM) |
| 50–200 | SVG with `motion` |
| 200+ | Canvas |
| 10,000+ | WebGL (Three.js) |

---

## Project Ideas (Ordered by Difficulty)

| # | Project | Builds on |
|---|---------|-----------|
| 1 | Game of Life | Matrix (M1-M7) |
| 2 | Pathfinding maze (BFS → A*) | Matrix (M1-M7) |
| 3 | Binary tree builder (click to insert) | Tree (T1-T7) |
| 4 | Bouncing ball sandbox | Physics (P1-P8) |
| 5 | Graph traversal (DFS vs BFS side-by-side) | Graph (G1-G6) |
| 6 | Heap visualiser (tree + array dual view) | Tree + Array |
| 7 | Spring mesh (grid of connected particles) | Physics + Matrix |
| 8 | Sorting race (algorithms side-by-side) | Bubble sort × N |
