# Framer Motion for Algorithm Visualisation — Step by Step

---

## Progress Log

| Date | What I did | Key takeaway |
|------|-----------|--------------|
| 2026-07-26 | Completed baby steps — installed, ran, made interactive changes | `Record<K,V>` for typed state maps, `Array.from({ length }, fn)` for grid init, double-buffer pattern for frame advance, `setGrid(advance)` is the whole tick |

### Concepts Clicked

- **State drives animation** — change state, Motion animates to new value. No manual keyframes.
- **`layout` prop** — just add it and position changes animate automatically.
- **Frame advance = pure function** — `advance(grid) → newGrid`, ~20 lines max, does one thing.
- **Data structures for frame advance**: double buffer (neighbor-dependent), delta list (sparse), event queue (complex systems).
- **Motion has no timeline** — use `useAnimate` + async/await for sequences, or GSAP if you need scrubbing.

---

## Step 1: Install Framer Motion

```bash
npm install motion
```

> Note: The package is called `motion` (v11+). Older tutorials may reference `framer-motion` — same library, new name.

---

## Step 2: Basic Concept

Framer Motion replaces HTML elements with animated versions:

```tsx
// Normal div — no animation
<div>Hello</div>

// Motion div — can animate
import { motion } from "motion/react"

<motion.div animate={{ opacity: 1 }}>Hello</motion.div>
```

Every HTML element has a `motion.` version: `motion.div`, `motion.span`, `motion.button`, etc.

---

## Step 3: Your First Animation

Create `app/algorithms/page.tsx`:

```tsx
"use client"

import { motion } from "motion/react"

export default function AlgorithmsPage() {
  return (
    <div className="flex flex-col items-center justify-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Algorithms</h1>

      <motion.div
        className="h-20 w-20 rounded-lg bg-primary"
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      />
    </div>
  )
}
```

**What each prop does:**

| Prop | What it does |
|------|-------------|
| `animate` | The end state — Framer Motion animates FROM current TO this |
| `transition` | How to get there — duration, easing, repeat |

---

## Step 4: Animate on Click (State-Driven)

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export default function AlgorithmsPage() {
  const [big, setBig] = useState(false)

  return (
    <div className="flex flex-col items-center justify-center gap-8 px-4 py-12">
      <motion.div
        className="h-20 w-20 cursor-pointer rounded-lg bg-primary"
        animate={{ scale: big ? 1.5 : 1 }}
        transition={{ type: "spring", stiffness: 300 }}
        onClick={() => setBig(!big)}
      />
      <p className="text-muted-foreground">Click the square</p>
    </div>
  )
}
```

**Key idea:** Change state → `animate` prop changes → Framer Motion animates to the new value. You never write keyframes manually.

---

## Step 5: Layout Animation (The Magic for Sorting)

This is the killer feature for algorithm visualisation. When elements reorder, Framer Motion animates them to their new position automatically.

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export default function AlgorithmsPage() {
  const [items, setItems] = useState([5, 3, 8, 1, 4])

  function shuffle() {
    setItems([...items].sort(() => Math.random() - 0.5))
  }

  return (
    <div className="flex flex-col items-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Layout Animation</h1>

      <div className="flex gap-2">
        {items.map((item) => (
          <motion.div
            key={item}
            layout
            className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold"
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          >
            {item}
          </motion.div>
        ))}
      </div>

      <button
        onClick={shuffle}
        className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground hover:bg-accent"
      >
        Shuffle
      </button>
    </div>
  )
}
```

**The magic:** Just add `layout` to a `motion.div`. When the array reorders, each element glides to its new position. No manual position calculation.

**Why it works:**
1. Each element has a unique `key` (the number itself)
2. `layout` tells Framer Motion to track this element's position
3. When React re-renders with a new order, Framer Motion sees the position changed
4. It animates from old position → new position

---

## Step 6: Bubble Sort Visualisation (Interactive Tutorial)

Build it piece by piece — display first, then sort.

### Step 6.1: Just Display Bars

Start with an array and show it as bars. Nothing animated yet.

```tsx
"use client"

export default function BubbleSortPage() {
  const array = [38, 27, 43, 3, 9, 82, 10, 55, 20, 45]

  return (
    <div className="flex flex-col items-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Bubble Sort</h1>

      <div className="flex items-end gap-1">
        {array.map((value, index) => (
          <div
            key={index}
            className="w-10 rounded-t-md bg-primary"
            style={{ height: `${value * 4}px` }}
          />
        ))}
      </div>

      {/* Numbers below bars */}
      <div className="flex gap-1">
        {array.map((value, index) => (
          <div key={index} className="w-10 text-center text-xs text-muted-foreground">
            {value}
          </div>
        ))}
      </div>
    </div>
  )
}
```

**What you see:** 10 vertical bars, taller = bigger number. That's it.

**Key idea:** `items-end` aligns bars at the bottom. `height: value * 4` maps data to pixels.

---

### Step 6.2: Make It State (So We Can Change It)

Move the array into `useState` so we can modify it later:

```tsx
"use client"

import { useState } from "react"

export default function BubbleSortPage() {
  const [array, setArray] = useState([38, 27, 43, 3, 9, 82, 10, 55, 20, 45])

  return (
    <div className="flex flex-col items-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Bubble Sort</h1>

      <div className="flex items-end gap-1">
        {array.map((value, index) => (
          <div
            key={index}
            className="w-10 rounded-t-md bg-primary"
            style={{ height: `${value * 4}px` }}
          />
        ))}
      </div>

      {/* Shuffle button to prove state works */}
      <button
        onClick={() => setArray([...array].sort(() => Math.random() - 0.5))}
        className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground"
      >
        Shuffle
      </button>
    </div>
  )
}
```

**What changed:** Array is in state. Click "Shuffle" — bars reorder (but no animation yet).

---

### Step 6.3: Add Framer Motion (Bars Animate When They Move)

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export default function BubbleSortPage() {
  const [array, setArray] = useState([38, 27, 43, 3, 9, 82, 10, 55, 20, 45])

  return (
    <div className="flex flex-col items-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Bubble Sort</h1>

      <div className="flex items-end gap-1">
        {array.map((value, index) => (
          <motion.div
            key={value}
            layout
            className="w-10 rounded-t-md bg-primary"
            style={{ height: `${value * 4}px` }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          />
        ))}
      </div>

      <button
        onClick={() => setArray([...array].sort(() => Math.random() - 0.5))}
        className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground"
      >
        Shuffle
      </button>
    </div>
  )
}
```

**What changed:**
- `div` → `motion.div`
- Added `layout` prop
- `key={value}` (not `key={index}`) — so Framer Motion tracks each bar by its VALUE

**Try it:** Click shuffle — bars now glide to their new positions. That's `layout` doing all the work.

---

### Step 6.4: Do ONE Swap

Before the full algorithm, just swap the first two elements on button click:

```tsx
function swapFirst() {
  const newArray = [...array]
  ;[newArray[0], newArray[1]] = [newArray[1], newArray[0]]
  setArray(newArray)
}

<button onClick={swapFirst}>Swap First Two</button>
```

**Try it:** The first two bars animate and swap positions. This proves the animation works for individual swaps.

---

### Step 6.5: Step-by-Step Sort (One Comparison at a Time)

Add state to track where we are in the algorithm, and a "Next Step" button:

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export default function BubbleSortPage() {
  const [array, setArray] = useState([38, 27, 43, 3, 9, 82, 10, 55, 20, 45])
  const [i, setI] = useState(0)         // outer loop (pass number)
  const [j, setJ] = useState(0)         // inner loop (comparison index)
  const [sorted, setSorted] = useState(false)

  function nextStep() {
    if (sorted) return

    const newArray = [...array]

    // Compare and swap if needed
    if (newArray[j] > newArray[j + 1]) {
      ;[newArray[j], newArray[j + 1]] = [newArray[j + 1], newArray[j]]
      setArray(newArray)
    }

    // Move to next comparison
    if (j < array.length - 1 - i) {
      setJ(j + 1)
    } else {
      // End of pass — start next pass
      if (i < array.length - 1) {
        setI(i + 1)
        setJ(0)
      } else {
        setSorted(true)
      }
    }
  }

  function reset() {
    setArray([38, 27, 43, 3, 9, 82, 10, 55, 20, 45])
    setI(0)
    setJ(0)
    setSorted(false)
  }

  return (
    <div className="flex flex-col items-center gap-8 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Bubble Sort</h1>

      {/* Status */}
      <p className="text-sm text-muted-foreground">
        Pass {i + 1} | Comparing index {j} and {j + 1}
      </p>

      {/* Bars */}
      <div className="flex items-end gap-1">
        {array.map((value, index) => (
          <motion.div
            key={value}
            layout
            className={`w-10 rounded-t-md ${
              index === j || index === j + 1
                ? "bg-yellow-400"           // currently comparing
                : index > array.length - 1 - i
                  ? "bg-green-500"           // already sorted
                  : "bg-primary"             // default
            }`}
            style={{ height: `${value * 4}px` }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          />
        ))}
      </div>

      {/* Numbers */}
      <div className="flex gap-1">
        {array.map((value, index) => (
          <div key={index} className="w-10 text-center text-xs text-muted-foreground">
            {value}
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="flex gap-4">
        <button
          onClick={nextStep}
          disabled={sorted}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
        >
          {sorted ? "Done!" : "Next Step"}
        </button>
        <button
          onClick={reset}
          className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground"
        >
          Reset
        </button>
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-sm text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded bg-yellow-400" /> Comparing
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded bg-green-500" /> Sorted
        </span>
      </div>
    </div>
  )
}
```

**What you get:** Click "Next Step" — one comparison happens. You see which two bars are being compared (yellow). If they swap, they animate. Green bars are in their final position.

---

### Step 6.6: Auto-Play (Run It Automatically)

Add a play/pause button that calls `nextStep` on an interval:

```tsx
const [playing, setPlaying] = useState(false)
const [speed, setSpeed] = useState(300)

useEffect(() => {
  if (!playing || sorted) return

  const timer = setInterval(() => {
    nextStep()
  }, speed)

  return () => clearInterval(timer)
}, [playing, sorted, j, i])  // re-run when j or i changes

<div className="flex gap-4">
  <button
    onClick={() => setPlaying(!playing)}
    className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
  >
    {playing ? "Pause" : "Play"}
  </button>
  <button onClick={nextStep} disabled={sorted || playing}>
    Next Step
  </button>
  <button onClick={reset}>Reset</button>
</div>

{/* Speed slider */}
<div className="flex items-center gap-2">
  <span className="text-sm text-muted-foreground">Speed:</span>
  <input
    type="range"
    min={50} max={1000} step={50}
    value={speed}
    onChange={(e) => setSpeed(Number(e.target.value))}
  />
  <span className="text-sm text-muted-foreground">{speed}ms</span>
</div>
```

**Now you have both:** Click "Next Step" to go one-by-one, or "Play" to watch it run automatically. Slider controls speed.

---

### Step 6.7: The Full Component (Everything Together)

```tsx
"use client"

import { useState, useEffect, useCallback } from "react"
import { motion } from "motion/react"

const INITIAL = [38, 27, 43, 3, 9, 82, 10, 55, 20, 45]

export default function BubbleSortPage() {
  const [array, setArray] = useState(INITIAL)
  const [i, setI] = useState(0)
  const [j, setJ] = useState(0)
  const [sorted, setSorted] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(300)
  const [swapCount, setSwapCount] = useState(0)
  const [compareCount, setCompareCount] = useState(0)

  const nextStep = useCallback(() => {
    if (sorted) return

    const newArray = [...array]
    setCompareCount((c) => c + 1)

    if (newArray[j] > newArray[j + 1]) {
      ;[newArray[j], newArray[j + 1]] = [newArray[j + 1], newArray[j]]
      setArray(newArray)
      setSwapCount((s) => s + 1)
    }

    if (j < array.length - 2 - i) {
      setJ(j + 1)
    } else {
      if (i < array.length - 2) {
        setI(i + 1)
        setJ(0)
      } else {
        setSorted(true)
        setPlaying(false)
      }
    }
  }, [array, i, j, sorted])

  useEffect(() => {
    if (!playing || sorted) return
    const timer = setTimeout(nextStep, speed)
    return () => clearTimeout(timer)
  }, [playing, sorted, j, i, nextStep, speed])

  function reset() {
    setArray(INITIAL)
    setI(0)
    setJ(0)
    setSorted(false)
    setPlaying(false)
    setSwapCount(0)
    setCompareCount(0)
  }

  function randomize() {
    setArray(Array.from({ length: 10 }, () => Math.floor(Math.random() * 80) + 10))
    setI(0)
    setJ(0)
    setSorted(false)
    setPlaying(false)
    setSwapCount(0)
    setCompareCount(0)
  }

  return (
    <div className="flex flex-col items-center gap-6 px-4 py-12">
      <h1 className="text-3xl font-bold text-foreground">Bubble Sort</h1>

      {/* Stats */}
      <div className="flex gap-6 text-sm text-muted-foreground">
        <span>Pass: {i + 1}</span>
        <span>Comparisons: {compareCount}</span>
        <span>Swaps: {swapCount}</span>
      </div>

      {/* Bars */}
      <div className="flex items-end gap-1">
        {array.map((value, index) => (
          <motion.div
            key={value}
            layout
            className={`w-10 rounded-t-md ${
              sorted
                ? "bg-green-500"
                : index === j || index === j + 1
                  ? "bg-yellow-400"
                  : index > array.length - 1 - i
                    ? "bg-green-500"
                    : "bg-primary"
            }`}
            style={{ height: `${value * 4}px` }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          />
        ))}
      </div>

      {/* Numbers */}
      <div className="flex gap-1">
        {array.map((value, index) => (
          <div
            key={index}
            className={`w-10 text-center text-xs ${
              index === j || index === j + 1 ? "font-bold text-foreground" : "text-muted-foreground"
            }`}
          >
            {value}
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="flex gap-3">
        <button
          onClick={() => setPlaying(!playing)}
          disabled={sorted}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
        >
          {playing ? "⏸ Pause" : "▶ Play"}
        </button>
        <button
          onClick={nextStep}
          disabled={sorted || playing}
          className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground disabled:opacity-50"
        >
          Step →
        </button>
        <button
          onClick={randomize}
          className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground"
        >
          🎲 Random
        </button>
        <button
          onClick={reset}
          className="rounded-md bg-secondary px-4 py-2 text-secondary-foreground"
        >
          ↺ Reset
        </button>
      </div>

      {/* Speed */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Speed:</span>
        <input
          type="range"
          min={50} max={800} step={50}
          value={speed}
          onChange={(e) => setSpeed(Number(e.target.value))}
          className="w-32"
        />
        <span className="text-sm text-muted-foreground">{speed}ms</span>
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-sm text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded bg-yellow-400" /> Comparing
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-3 rounded bg-green-500" /> Sorted
        </span>
      </div>

      {/* Explanation */}
      {!sorted && (
        <p className="max-w-md text-center text-sm text-muted-foreground">
          Comparing <strong>{array[j]}</strong> and <strong>{array[j + 1]}</strong>
          {array[j] > array[j + 1]
            ? ` → ${array[j]} > ${array[j + 1]}, swap!`
            : ` → ${array[j]} ≤ ${array[j + 1]}, no swap.`}
        </p>
      )}
      {sorted && (
        <p className="text-sm font-medium text-green-500">
          ✅ Sorted in {compareCount} comparisons and {swapCount} swaps!
        </p>
      )}
    </div>
  )
}
```

---

### What You Built (Step by Step Summary)

| Step | What was added |
|------|---------------|
| 6.1 | Static bars from an array |
| 6.2 | Move array to state + shuffle button |
| 6.3 | Add `motion.div` + `layout` (bars animate) |
| 6.4 | Single swap to prove animation works |
| 6.5 | "Next Step" button — one comparison at a time with color coding |
| 6.6 | Auto-play + speed slider |
| 6.7 | Full version: stats, random, explanation text |

---

## Step 7: Frame Advance Pattern (Baby Steps)

The "frame advance" pattern is how simulations work — Game of Life, physics, cellular automata. One tick = one step forward in time.

---

### Step 7.1: A Pure Function That Returns the Next State

This is the whole idea. One function. Takes grid in, returns new grid out.

```tsx
function advance(grid: string[][]): string[][] {
  return grid.map((row, r) =>
    row.map((cell, c) => nextCell(grid, r, c))
  )
}
```

That's it. No mutation. No side effects. ~5 lines.

---

### Step 7.2: The Cell Logic (Does ONE Thing)

Each cell decides its next state based on neighbors:

```tsx
function nextCell(grid: string[][], r: number, c: number): string {
  const alive = countNeighbors(grid, r, c)
  if (grid[r][c] === "alive") {
    return alive === 2 || alive === 3 ? "alive" : "dead"
  }
  return alive === 3 ? "alive" : "dead"
}
```

~6 lines. One responsibility: decide if this cell lives or dies.

---

### Step 7.3: Count Neighbors (Does ONE Thing)

```tsx
function countNeighbors(grid: string[][], r: number, c: number): number {
  let count = 0
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue
      const nr = r + dr
      const nc = c + dc
      if (nr >= 0 && nr < grid.length && nc >= 0 && nc < grid[0].length) {
        if (grid[nr][nc] === "alive") count++
      }
    }
  }
  return count
}
```

~12 lines. One responsibility: count how many alive neighbors a cell has.

---

### Step 7.4: Create the Initial Grid

```tsx
function createGrid(rows: number, cols: number): string[][] {
  return Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () =>
      Math.random() > 0.7 ? "alive" : "dead"
    )
  )
}
```

`Array.from({ length: N }, fn)` — creates N items, each from the callback. Inner one creates each row. 30% chance of alive.

---

### Step 7.5: Wire It Into React (One Click = One Tick)

```tsx
"use client"

import { useState } from "react"

export default function GameOfLife() {
  const [grid, setGrid] = useState(() => createGrid(10, 10))

  function tick() {
    setGrid(advance)
  }

  return (
    <div>
      <div className="inline-grid gap-[1px]"
        style={{ gridTemplateColumns: `repeat(10, 24px)` }}>
        {grid.flat().map((cell, i) => (
          <div key={i}
            className={`h-6 w-6 ${cell === "alive" ? "bg-primary" : "bg-muted"}`}
          />
        ))}
      </div>
      <button onClick={tick}>Next</button>
    </div>
  )
}
```

Click "Next" → `setGrid(advance)` → React re-renders with new grid. That's the whole frame advance.

---

### Step 7.6: Auto-Play (requestAnimationFrame or setInterval)

```tsx
const [playing, setPlaying] = useState(false)
const [speed, setSpeed] = useState(200)

useEffect(() => {
  if (!playing) return
  const timer = setInterval(() => setGrid(advance), speed)
  return () => clearInterval(timer)
}, [playing, speed])
```

Toggle `playing` → ticks happen automatically at `speed` ms intervals.

---

### Step 7.7: Add Framer Motion (Cells Animate on State Change)

```tsx
import { motion } from "motion/react"

<motion.div
  key={i}
  className={`h-6 w-6 rounded-sm ${cell === "alive" ? "bg-primary" : "bg-muted"}`}
  animate={{ scale: cell === "alive" ? 1 : 0.6, opacity: cell === "alive" ? 1 : 0.3 }}
  transition={{ duration: 0.15 }}
/>
```

Dead cells shrink and fade. Alive cells pop in. Motion handles the in-between.

---

### Summary: The Pattern

```
createGrid()  → initial state
advance(grid) → next state (pure function, no mutation)
setGrid(advance) → one tick
setInterval(tick, speed) → auto-play
```

Each piece is ~5–15 lines and does one thing. Compose them together.

---

## Step 8: Speed Control

Add a speed slider:

```tsx
const [speed, setSpeed] = useState(300)

// In the sleep calls:
await sleep(speed)

// Add a slider in the controls:
<div className="flex items-center gap-2">
  <span className="text-sm text-muted-foreground">Speed:</span>
  <input
    type="range"
    min={50}
    max={1000}
    step={50}
    value={speed}
    onChange={(e) => setSpeed(Number(e.target.value))}
    className="w-32"
  />
  <span className="text-sm text-muted-foreground">{speed}ms</span>
</div>
```

Lower value = faster animation.

---

## Step 9: Random Array Generator

```tsx
function generateArray(size: number = 10) {
  return Array.from({ length: size }, () => Math.floor(Math.random() * 80) + 10)
}

// Replace INITIAL_ARRAY usage:
const [array, setArray] = useState(() => generateArray())

// In reset:
function reset() {
  stopRef.current = true
  setRunning(false)
  setArray(generateArray())
  setComparing([])
  setSorted([])
}
```

---

## Framer Motion Cheat Sheet

| Prop | What it does | Example |
|------|-------------|---------|
| `animate` | Target state to animate to | `animate={{ x: 100 }}` |
| `initial` | Starting state (on mount) | `initial={{ opacity: 0 }}` |
| `exit` | State when removed from DOM | `exit={{ opacity: 0 }}` |
| `layout` | Auto-animate position/size changes | `layout` (boolean) |
| `transition` | How to animate | `transition={{ duration: 0.3 }}` |
| `whileHover` | Animate while hovered | `whileHover={{ scale: 1.1 }}` |
| `whileTap` | Animate while pressed | `whileTap={{ scale: 0.95 }}` |

### Transition types

| Type | Feel | Good for |
|------|------|----------|
| `{ type: "spring" }` | Bouncy, natural | UI elements, layout animations |
| `{ type: "tween" }` | Linear/eased, predictable | Fades, rotations |
| `{ duration: 0.3 }` | Fixed time | When you need exact timing |
| `{ stiffness: 300, damping: 25 }` | Control spring feel | Fine-tuning bounciness |

---

## Next Algorithms to Visualise

Once you have bubble sort working, the same pattern works for:

| Algorithm | What changes |
|-----------|-------------|
| **Selection Sort** | Highlight the minimum, swap it to the front |
| **Insertion Sort** | Highlight the element being inserted, shift others right |
| **Merge Sort** | Split array visually, merge halves back together |
| **Quick Sort** | Highlight pivot, partition into left/right groups |

The pattern is always:
1. Track state (`comparing`, `sorted`, `swapping`)
2. Use `async/await` + `sleep()` to pause between steps
3. Use `layout` on `motion.div` to animate position changes
4. Color-code what's happening (comparing, swapped, sorted)
