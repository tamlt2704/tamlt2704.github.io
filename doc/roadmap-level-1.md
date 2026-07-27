# Level 1: Fill the Gaps — Essentials You'll Need Daily

---

## React Deep Dive

### useEffect — The Lifecycle Hook

`useEffect` runs code after your component renders. Think of it as: "after the screen updates, do this."

```tsx
useEffect(() => {
  // This runs after render

  return () => {
    // This runs on cleanup (component unmounts or before re-running)
  }
}, [dependencies])
```

**The dependency array controls WHEN it runs:**

| Dependency Array | When it runs |
|-----------------|-------------|
| `[]` (empty) | Once — when component first appears |
| `[count]` | Every time `count` changes |
| No array at all | Every single render (usually a mistake) |

**Common uses:**

```tsx
// Fetch data on mount
useEffect(() => {
  fetch("/api/data").then(...)
}, [])

// Subscribe to something, unsubscribe on cleanup
useEffect(() => {
  const handler = (e) => console.log(e)
  window.addEventListener("resize", handler)

  return () => window.removeEventListener("resize", handler)  // cleanup!
}, [])

// Timer with cleanup
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000)
  return () => clearInterval(id)  // stop timer when component unmounts
}, [])
```

**Why cleanup matters:**

Without cleanup, if your component unmounts (user navigates away), the timer/listener keeps running in the background — causing memory leaks, errors updating unmounted components, or duplicate subscriptions.

---

### useRef — Access DOM + Persist Values

`useRef` gives you two powers:

**Power 1: Access a DOM element directly**

```tsx
const inputRef = useRef<HTMLInputElement>(null)

// Focus the input programmatically
function handleClick() {
  inputRef.current?.focus()
}

return <input ref={inputRef} />
```

**Power 2: Store a value that survives re-renders WITHOUT causing a re-render**

```tsx
const renderCount = useRef(0)

useEffect(() => {
  renderCount.current += 1
  // This updates silently — no re-render triggered
})
```

**`useRef` vs `useState`:**

| | `useState` | `useRef` |
|-|-----------|---------|
| Triggers re-render? | ✅ Yes | ❌ No |
| Persists between renders? | ✅ Yes | ✅ Yes |
| Use for | Anything the UI shows | Timers, DOM refs, previous values, flags |

**Common use: stop a running animation/timer**

```tsx
const stopRef = useRef(false)

async function runAnimation() {
  for (let i = 0; i < 100; i++) {
    if (stopRef.current) return  // bail out
    await sleep(100)
  }
}

function stop() {
  stopRef.current = true  // doesn't re-render, just sets the flag
}
```

---

### useMemo / useCallback — Performance Optimization

**`useMemo`** — cache an expensive calculation:

```tsx
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value)  // expensive for large arrays
}, [data])  // only recalculate when `data` changes
```

Without `useMemo`, this sorts on EVERY render — even if `data` hasn't changed.

**`useCallback`** — cache a function reference:

```tsx
const handleClick = useCallback(() => {
  setCount(c => c + 1)
}, [])  // same function reference every render
```

**When to use them:**

| Use `useMemo` when | Use `useCallback` when |
|-------------------|----------------------|
| Sorting/filtering large arrays | Passing functions to child components that use `React.memo` |
| Complex calculations | Passing functions as dependencies to `useEffect` |
| Creating objects used as dependencies | Event handlers in lists with many items |

**When NOT to bother:** Simple operations, components that render fast anyway. Don't optimise prematurely — only add these when you notice slowness.

---

### Custom Hooks — Extract Reusable Logic

A custom hook is just a function that starts with `use` and can call other hooks.

**Pattern:** When you copy-paste the same `useState` + `useEffect` combo between components, extract it:

```tsx
// hooks/use-window-size.ts
import { useState, useEffect } from "react"

export function useWindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 })

  useEffect(() => {
    function handleResize() {
      setSize({ width: window.innerWidth, height: window.innerHeight })
    }

    handleResize()  // set initial size
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  return size
}
```

Usage:

```tsx
function MyComponent() {
  const { width } = useWindowSize()
  return <p>Window is {width}px wide</p>
}
```

**You already made one:** `useCsvData` in the dashboard doc is a custom hook.

**More useful custom hooks to build:**

| Hook | What it does |
|------|-------------|
| `useLocalStorage(key, initial)` | Like `useState` but persists to localStorage |
| `useDebounce(value, delay)` | Delays updates (for search inputs) |
| `useMediaQuery("(min-width: 768px)")` | Returns true/false for responsive logic in JS |
| `useOnClickOutside(ref, handler)` | Detect clicks outside a dropdown to close it |
| `useInterval(callback, delay)` | setInterval that respects React lifecycle |

---

### Context API — Share State Without Prop Drilling

You've used this — `ThemeProvider` is Context. Here's how to build your own:

```tsx
// context/game-context.tsx
"use client"

import { createContext, useContext, useState } from "react"

interface GameState {
  score: number
  level: number
  addScore: (points: number) => void
  nextLevel: () => void
}

const GameContext = createContext<GameState | null>(null)

export function GameProvider({ children }: { children: React.ReactNode }) {
  const [score, setScore] = useState(0)
  const [level, setLevel] = useState(1)

  return (
    <GameContext.Provider value={{
      score,
      level,
      addScore: (points) => setScore(s => s + points),
      nextLevel: () => setLevel(l => l + 1),
    }}>
      {children}
    </GameContext.Provider>
  )
}

export function useGame() {
  const context = useContext(GameContext)
  if (!context) throw new Error("useGame must be used within GameProvider")
  return context
}
```

Usage anywhere inside the provider:

```tsx
function ScoreDisplay() {
  const { score, level } = useGame()
  return <p>Level {level} — Score: {score}</p>
}
```

**When to use Context vs other state tools:**

| Situation | Use |
|-----------|-----|
| Theme, locale, auth (rarely changes) | Context ✓ |
| Form state in one page | `useState` ✓ |
| Data shared across many components, changes often | Zustand or Jotai |
| Server data (API responses) | TanStack Query |

---

### Error Boundaries — Catch Rendering Crashes

If a component throws an error, the whole page crashes. Error boundaries catch it gracefully:

```tsx
"use client"

import { Component, ReactNode } from "react"

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="p-8 text-center">
          <p className="text-lg text-foreground">Something went wrong.</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 rounded bg-primary px-4 py-2 text-primary-foreground"
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
```

Wrap risky components:

```tsx
<ErrorBoundary fallback={<p>Chart failed to load</p>}>
  <ComplexChart data={data} />
</ErrorBoundary>
```

> Note: Error boundaries must be class components (React limitation). But you only write it once.

---

### Suspense + Lazy Loading

Load heavy components only when needed:

```tsx
import { lazy, Suspense } from "react"

const HeavyChart = lazy(() => import("@/components/charts/heavy-chart"))

function Dashboard() {
  return (
    <Suspense fallback={<div className="h-[300px] animate-pulse bg-muted rounded-lg" />}>
      <HeavyChart />
    </Suspense>
  )
}
```

**What happens:**
1. Page loads fast (chart code not included in initial bundle)
2. `Suspense` shows the fallback (loading skeleton)
3. Chart component loads in the background
4. Once ready, skeleton is replaced with the actual chart

**When to use:** Heavy libraries (chart libraries, code editors, maps), routes the user might not visit.

---

## CSS / Layout Mastery

### Flexbox Deep Dive

You know `flex` and `gap`. Here's the rest:

**`flex-grow` / `flex-shrink` / `flex-basis`:**

```tsx
// Tailwind shorthand:
<div className="flex">
  <div className="flex-none w-20">Fixed sidebar</div>  {/* never grows/shrinks */}
  <div className="flex-1">Takes remaining space</div>   {/* grows to fill */}
  <div className="flex-none w-20">Fixed sidebar</div>
</div>
```

| Class | Meaning |
|-------|---------|
| `flex-1` | `flex: 1 1 0%` — grow and shrink equally |
| `flex-none` | `flex: none` — don't grow or shrink, use natural size |
| `flex-auto` | `flex: 1 1 auto` — grow/shrink based on content size |
| `flex-initial` | `flex: 0 1 auto` — can shrink but won't grow |

**`order`** — reorder visually without changing HTML:

```tsx
<div className="flex">
  <div className="order-2">Appears second</div>
  <div className="order-1">Appears first</div>
  <div className="order-3">Appears third</div>
</div>
```

### CSS Grid Deep Dive

Grid is for 2D layouts (rows AND columns). Flex is for 1D (row OR column).

**`grid-template-areas`** — name your layout regions:

```css
.dashboard {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar main   aside"
    "footer footer footer";
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: auto 1fr auto;
}
```

In Tailwind, use arbitrary values:

```tsx
<div className="grid grid-cols-[200px_1fr_200px] grid-rows-[auto_1fr_auto] gap-4">
```

**`auto-fit` + `minmax`** — responsive grid without media queries:

```tsx
<div className="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  {cards.map(card => <Card key={card.id} />)}
</div>
```

This means: "Make as many columns as fit, each at least 250px wide, grow to fill space." Cards automatically reflow on resize — no breakpoints needed.

### Container Queries

Style based on a component's container size, not the viewport:

```tsx
// Parent declares itself as a container
<div className="@container">
  {/* Child responds to the container's width */}
  <div className="@md:flex @md:gap-4">
    <img className="@md:w-1/3" />
    <p className="@md:w-2/3">...</p>
  </div>
</div>
```

`@md` means "when this container is medium-sized" — not the viewport. Useful for reusable components that might be in a sidebar or full-width.

---

## TypeScript (Beyond Basics)

### Generics

Make functions/components work with ANY type:

```tsx
// Without generics — only works for strings
function first(arr: string[]): string {
  return arr[0]
}

// With generics — works for anything
function first<T>(arr: T[]): T {
  return arr[0]
}

first([1, 2, 3])     // returns number
first(["a", "b"])    // returns string
```

**In React components:**

```tsx
interface ListProps<T> {
  items: T[]
  renderItem: (item: T) => React.ReactNode
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>
}

// Usage — TypeScript infers T from the items you pass
<List items={users} renderItem={(user) => <li>{user.name}</li>} />
```

### Utility Types

Built-in types that transform other types:

```tsx
interface User {
  id: number
  name: string
  email: string
  role: string
}

// Pick only some fields
type PublicUser = Pick<User, "id" | "name">
// → { id: number; name: string }

// Remove some fields
type UserWithoutRole = Omit<User, "role">
// → { id: number; name: string; email: string }

// Make all fields optional
type PartialUser = Partial<User>
// → { id?: number; name?: string; email?: string; password?: string }

// Make all fields required
type RequiredUser = Required<PartialUser>

// Key-value map
type Scores = Record<string, number>
// → { [key: string]: number }
```

### Union Types + Narrowing

```tsx
type Status = "loading" | "error" | "success"

interface ApiResponse {
  status: Status
  data?: any
  error?: string
}

function handleResponse(res: ApiResponse) {
  switch (res.status) {
    case "loading":
      return <Spinner />
    case "error":
      return <p>{res.error}</p>   // TypeScript knows error exists here
    case "success":
      return <Data data={res.data} />
  }
}
```

### `as const`

Makes TypeScript treat values as literal types:

```tsx
// Without as const: string[]
const colors = ["red", "blue", "green"]

// With as const: readonly ["red", "blue", "green"]
const colors = ["red", "blue", "green"] as const

type Color = (typeof colors)[number]  // "red" | "blue" | "green"
```

Useful for creating type-safe constants.

---

## Practice Projects for Level 1

| Project | What you'll practise |
|---------|---------------------|
| **Pomodoro timer** | `useEffect` cleanup, `useRef` for interval, `useCallback` |
| **Shopping cart** | Context API, `useReducer`, TypeScript generics |
| **Responsive image gallery** | CSS Grid `auto-fit`, container queries, lazy loading |
| **Drag-and-drop todo list** | Custom hooks, `useRef`, complex state |
| **Infinite scroll list** | Intersection Observer, `useMemo`, virtual scrolling |

---

## How to Know You've Mastered Level 1

- [ ] Can write `useEffect` with proper cleanup without looking it up
- [ ] Understand when `useRef` is better than `useState`
- [ ] Can extract logic into a custom hook naturally
- [ ] Grid layouts don't scare you — you reach for `auto-fit` + `minmax`
- [ ] TypeScript generics feel intuitive, not confusing
- [ ] You can explain the difference between `Partial`, `Pick`, `Omit`, `Record`
