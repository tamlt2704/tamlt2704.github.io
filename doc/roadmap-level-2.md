# Level 2: Real-World Skills — What Separates Juniors from Mids

---

## State Management

### When to Use What

```
Do I need to share state?
  ├── No → useState (local)
  ├── Between parent/child → props
  ├── Between siblings → lift state to parent
  ├── Across many components (rarely changes) → Context
  ├── Across many components (changes often) → Zustand
  └── From an API → TanStack Query
```

### Zustand — The Simplest Global State

```bash
npm install zustand
```

```tsx
// store/game-store.ts
import { create } from "zustand"

interface GameStore {
  score: number
  level: number
  addScore: (points: number) => void
  nextLevel: () => void
  reset: () => void
}

export const useGameStore = create<GameStore>((set) => ({
  score: 0,
  level: 1,
  addScore: (points) => set((state) => ({ score: state.score + points })),
  nextLevel: () => set((state) => ({ level: state.level + 1 })),
  reset: () => set({ score: 0, level: 1 }),
}))
```

Usage — no provider needed:

```tsx
function ScoreDisplay() {
  const score = useGameStore((state) => state.score)
  return <p>Score: {score}</p>
}

function GameControls() {
  const addScore = useGameStore((state) => state.addScore)
  return <button onClick={() => addScore(10)}>+10</button>
}
```

**Why Zustand over Context?**
- No Provider wrapping needed
- Only re-renders components that use the specific slice that changed
- Simpler API — no `createContext`, `useContext`, `Provider` boilerplate
- Works outside React (in utility functions)

### TanStack Query — Server State

```bash
npm install @tanstack/react-query
```

**The problem it solves:** Every time you fetch data, you write the same code — loading state, error handling, caching, refetching. TanStack Query does all of that.

**Setup once** in layout:

```tsx
"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

const queryClient = new QueryClient()

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

**Use anywhere:**

```tsx
import { useQuery } from "@tanstack/react-query"

function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["users"],
    queryFn: () => fetch("/api/users").then(res => res.json()),
  })

  if (isLoading) return <Skeleton />
  if (error) return <p>Error: {error.message}</p>

  return <ul>{data.map(user => <li key={user.id}>{user.name}</li>)}</ul>
}
```

**What you get for free:**
- Caching — same query on another page doesn't refetch
- Background refetch — data stays fresh
- Loading/error states — no manual `useState`
- Retry on failure — automatic
- Deduplication — 10 components requesting same data = 1 fetch

### useReducer — Complex Local State

When `useState` gets messy (many related pieces of state):

```tsx
interface State {
  questions: Question[]
  current: number
  score: number
  status: "idle" | "playing" | "finished"
}

type Action =
  | { type: "START" }
  | { type: "ANSWER"; correct: boolean }
  | { type: "NEXT" }
  | { type: "RESET" }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "START":
      return { ...state, status: "playing", current: 0, score: 0 }
    case "ANSWER":
      return { ...state, score: state.score + (action.correct ? 1 : 0) }
    case "NEXT":
      if (state.current + 1 >= state.questions.length) {
        return { ...state, status: "finished" }
      }
      return { ...state, current: state.current + 1 }
    case "RESET":
      return { ...state, status: "idle", current: 0, score: 0 }
  }
}

// In component:
const [state, dispatch] = useReducer(reducer, initialState)

dispatch({ type: "ANSWER", correct: true })
dispatch({ type: "NEXT" })
```

**When `useReducer` > `useState`:**
- 3+ related state values that change together
- State transitions follow rules (game states, forms with steps)
- You want to describe WHAT happened, not HOW to update state

---

## Forms

### react-hook-form + zod

```bash
npm install react-hook-form zod @hookform/resolvers
```

**Define the shape with zod:**

```tsx
import { z } from "zod"

const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  age: z.number().min(5).max(100),
  level: z.enum(["easy", "medium", "hard"]),
})

type FormData = z.infer<typeof formSchema>
```

**Build the form:**

```tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

export function SettingsForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  })

  function onSubmit(data: FormData) {
    console.log(data)  // fully typed + validated
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <div>
        <label className="text-sm font-medium text-foreground">Name</label>
        <input
          {...register("name")}
          className="mt-1 w-full rounded-md border border-border bg-card px-3 py-2"
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-500">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label className="text-sm font-medium text-foreground">Email</label>
        <input
          {...register("email")}
          className="mt-1 w-full rounded-md border border-border bg-card px-3 py-2"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-500">{errors.email.message}</p>
        )}
      </div>

      <button type="submit" className="rounded-md bg-primary px-4 py-2 text-primary-foreground">
        Save
      </button>
    </form>
  )
}
```

**Why this combo?**
- `zod` — define validation rules once, get TypeScript types for free
- `react-hook-form` — minimal re-renders, fast, handles complex forms
- `@hookform/resolvers` — connects them together

---

## Data Fetching Patterns

### Pattern Comparison

```tsx
// 1. Client-side (user-triggered, dynamic)
"use client"
const { data } = useQuery({ queryKey: ["search", term], queryFn: ... })

// 2. Server Component (static, SEO-friendly) — NOT for GitHub Pages
async function Page() {
  const data = await fetch("https://api.example.com/data")
  return <Chart data={data} />
}

// 3. Static file in public/ (your CSV approach — works with GitHub Pages)
fetch("/data/population.csv")

// 4. Build-time import (fastest — data baked into JS bundle)
import { data } from "@/data/population"
```

**For your project (GitHub Pages):** Options 3 and 4 are your main tools. TanStack Query is useful if you fetch from external APIs at runtime (like gov.data APIs).

---

## Authentication (Concepts)

Even if your current project doesn't need auth, understand the flow:

```
User clicks "Login with Google"
       ↓
Redirect to Google's login page
       ↓
User authenticates with Google
       ↓
Google redirects back with a code
       ↓
Your server exchanges code for tokens
       ↓
Server creates a session / JWT
       ↓
Client stores token (httpOnly cookie)
       ↓
Every request includes the token
       ↓
Server validates token → allows/denies access
```

**Key terms:**

| Term | What it means |
|------|--------------|
| **JWT** | JSON Web Token — a signed string that contains user info |
| **Access token** | Short-lived (15min) — used for API calls |
| **Refresh token** | Long-lived (days) — used to get a new access token |
| **OAuth** | Protocol for "Login with X" (Google, GitHub) |
| **Session** | Server remembers you — stored in a cookie |
| **Protected route** | A page that redirects to login if you're not authenticated |

**Library for Next.js:** `next-auth` (now called Auth.js) handles all of this.

---

## Testing

### The Testing Trophy

```
        ╱╲
       ╱ E2E ╲           Few — slow, expensive, test whole flows
      ╱────────╲
     ╱Integration╲       Some — test components working together
    ╱──────────────╲
   ╱   Component     ╲    Many — test individual components
  ╱────────────────────╲
 ╱      Unit Tests       ╲  Most — test logic functions
╱──────────────────────────╲
```

### Vitest — Unit Tests

```bash
npm install -D vitest
```

Test a pure function:

```tsx
// utils/math.test.ts
import { describe, it, expect } from "vitest"
import { generateQuestion } from "./math"

describe("generateQuestion", () => {
  it("generates a question with correct answer", () => {
    const q = generateQuestion(10)
    expect(q.answer).toBe(q.a + q.b)
  })

  it("has 4 options including the answer", () => {
    const q = generateQuestion(10)
    expect(q.options).toHaveLength(4)
    expect(q.options).toContain(q.answer)
  })

  it("keeps numbers within max", () => {
    const q = generateQuestion(10)
    expect(q.a).toBeLessThanOrEqual(10)
    expect(q.b).toBeLessThanOrEqual(10)
  })
})
```

### Testing Library — Component Tests

```bash
npm install -D @testing-library/react @testing-library/jest-dom
```

Test a component renders and responds to interaction:

```tsx
// components/stat-card.test.tsx
import { render, screen } from "@testing-library/react"
import { StatCard } from "./stat-card"

describe("StatCard", () => {
  it("displays title and value", () => {
    render(<StatCard title="Users" value="1,234" />)
    expect(screen.getByText("Users")).toBeInTheDocument()
    expect(screen.getByText("1,234")).toBeInTheDocument()
  })

  it("shows positive trend in green", () => {
    render(<StatCard title="Revenue" value="$500" change="+12%" trend="up" />)
    const change = screen.getByText(/\+12%/)
    expect(change).toHaveClass("text-green-500")
  })
})
```

### Playwright — E2E Tests

```bash
npm install -D @playwright/test
```

Test real user flows in a real browser:

```tsx
// e2e/game.spec.ts
import { test, expect } from "@playwright/test"

test("addition game flow", async ({ page }) => {
  await page.goto("/games/addition")

  // Start game
  await page.click("text=Start!")

  // Should see a question
  await expect(page.locator("text=?")).toBeVisible()

  // Click an answer
  const buttons = page.locator("button")
  await buttons.first().click()

  // Should show feedback
  await expect(page.locator("text=Correct").or(page.locator("text=It was"))).toBeVisible()
})
```

### What to Test (Practical Guide)

| Test this | Don't test this |
|-----------|----------------|
| Business logic functions | Implementation details |
| Component renders correct output | CSS classes (brittle) |
| User interactions (click, type) | Internal state values |
| Error states | Third-party library internals |
| Accessibility (labels, roles) | Exact DOM structure |
| Critical user flows (E2E) | Every possible combination |

---

## Practice Projects for Level 2

| Project | What you'll practise |
|---------|---------------------|
| **Weather app** | TanStack Query, API fetching, loading/error states |
| **Multi-step form** | react-hook-form, zod, useReducer, form state machine |
| **Todo app with sync** | Zustand, localStorage persistence, optimistic updates |
| **Blog with comments** | Auth (GitHub OAuth), protected routes, server actions |
| **E-commerce cart** | Complex state, Context vs Zustand comparison, testing |

---

## How to Know You've Mastered Level 2

- [ ] Can fetch, cache, and display API data without writing loading/error boilerplate (TanStack Query)
- [ ] Can build a complex form with validation that shows helpful error messages
- [ ] Know when to use Context vs Zustand vs TanStack Query
- [ ] Can write unit tests for logic and component tests for UI
- [ ] Understand auth flows even if you haven't built one from scratch
- [ ] Can explain the difference between server state and client state
