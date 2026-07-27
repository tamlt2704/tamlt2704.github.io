# Level 3: Performance & Architecture — Senior Level

---

## Performance

### Web Vitals — The Metrics That Matter

Google ranks your site based on these three metrics:

| Metric | Full Name | What it measures | Good | Bad |
|--------|-----------|-----------------|------|-----|
| **LCP** | Largest Contentful Paint | When the main content is visible | < 2.5s | > 4s |
| **INP** | Interaction to Next Paint | How fast clicks/taps respond | < 200ms | > 500ms |
| **CLS** | Cumulative Layout Shift | How much the page jumps around | < 0.1 | > 0.25 |

**How to measure:**
- Chrome DevTools → Lighthouse tab → run audit
- [PageSpeed Insights](https://pagespeed.web.dev) — enter your URL
- `next/web-vitals` — log in production

### Fixing LCP (Slow Main Content)

**Common causes + fixes:**

| Cause | Fix |
|-------|-----|
| Large hero image | Use `next/image` with `priority` prop, serve WebP/AVIF |
| Web fonts blocking render | Use `next/font` (already doing this!) |
| Render-blocking JS | Code split, defer non-critical scripts |
| Slow API before showing content | Cache data, show skeleton first |

```tsx
// Priority image — tells browser to load this first
import Image from "next/image"

<Image src="/hero.jpg" alt="..." width={1200} height={600} priority />
```

### Fixing CLS (Page Jumping)

**Common causes + fixes:**

| Cause | Fix |
|-------|-----|
| Images without width/height | Always set `width` + `height` on `<Image>` |
| Fonts loading and resizing text | `next/font` with `font-display: swap` |
| Dynamic content pushing things down | Reserve space with min-height or skeleton |
| Ads/embeds loading late | Set fixed dimensions on their container |

```tsx
// Reserve space for a chart while it loads
<div className="h-[300px]">
  {loading ? <Skeleton className="h-full" /> : <Chart />}
</div>
```

### Fixing INP (Slow Interactions)

**Common causes + fixes:**

| Cause | Fix |
|-------|-----|
| Heavy computation on click | Move to Web Worker or `requestIdleCallback` |
| Re-rendering huge lists | Virtualise with TanStack Virtual |
| Blocking the main thread | Break work into smaller chunks |
| Too many DOM nodes | Lazy render off-screen content |

### Bundle Analysis

See what's making your app big:

```bash
npm install -D @next/bundle-analyzer
```

Update `next.config.ts`:

```ts
import withBundleAnalyzer from "@next/bundle-analyzer"

const config = withBundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
})({
  // ... your config
})

export default config
```

Run:

```bash
ANALYZE=true npm run build
```

Opens a visual map showing which packages are biggest. Common offenders:
- `moment.js` → replace with `date-fns` or native `Intl`
- `lodash` → import individual functions: `import debounce from "lodash/debounce"`
- Unused icon libraries → import only icons you use

### Code Splitting

```tsx
import dynamic from "next/dynamic"

// Heavy chart only loads when this page is visited
const HeavyChart = dynamic(() => import("@/components/charts/heavy-chart"), {
  loading: () => <div className="h-[300px] animate-pulse bg-muted rounded-lg" />,
  ssr: false,  // don't render on server (chart needs browser APIs)
})
```

**Route-based splitting is automatic in Next.js** — each page is its own bundle. But large shared components still need manual splitting.

### Virtual Scrolling (Large Lists)

Rendering 10,000 DOM nodes crashes the browser. Virtual scrolling only renders visible items:

```bash
npm install @tanstack/react-virtual
```

```tsx
import { useVirtualizer } from "@tanstack/react-virtual"

function BigList({ items }: { items: string[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,  // estimated row height
  })

  return (
    <div ref={parentRef} className="h-[500px] overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: "relative" }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: "absolute",
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
              height: `${virtualItem.size}px`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  )
}
```

10,000 items → only ~20 DOM nodes at any time. Buttery smooth scrolling.

---

## Architecture

### Feature-Based Folder Structure

**Bad (grouped by type):**

```
components/
  Button.tsx
  Chart.tsx
  GameCard.tsx
  ScoreDisplay.tsx
hooks/
  useGame.ts
  useChart.ts
utils/
  math.ts
  format.ts
```

As the project grows, related files are scattered everywhere.

**Good (grouped by feature):**

```
features/
  games/
    components/
      GameCard.tsx
      ScoreDisplay.tsx
    hooks/
      useGame.ts
    utils/
      math.ts
    types.ts
  dashboard/
    components/
      Chart.tsx
      StatCard.tsx
    hooks/
      useChartData.ts
    utils/
      format.ts
    types.ts
components/         ← shared/reusable only
  ui/
    button.tsx
    card.tsx
```

**Rule:** If a component is used in ONE feature, it lives in that feature's folder. If used across features, it goes in shared `components/`.

### Component Design Patterns

**Compound Components** — components that work together:

```tsx
// Usage
<Select>
  <Select.Trigger>Choose a fruit</Select.Trigger>
  <Select.Content>
    <Select.Item value="apple">Apple</Select.Item>
    <Select.Item value="banana">Banana</Select.Item>
  </Select.Content>
</Select>
```

The parent manages state internally. Children just declare structure. shadcn/ui uses this pattern everywhere.

**Composition over configuration:**

```tsx
// ❌ Too many props (configuration)
<Card
  title="Users"
  subtitle="Active this month"
  icon={<Users />}
  value={1234}
  footer={<Link>View all</Link>}
  variant="outlined"
/>

// ✅ Composable (children control structure)
<Card>
  <Card.Header>
    <Users />
    <Card.Title>Users</Card.Title>
    <Card.Description>Active this month</Card.Description>
  </Card.Header>
  <Card.Content>
    <span className="text-3xl font-bold">1,234</span>
  </Card.Content>
  <Card.Footer>
    <Link>View all</Link>
  </Card.Footer>
</Card>
```

### Server Components vs Client Components

```
Server Components (default in Next.js App Router):
  ✅ Fetch data directly (no useEffect)
  ✅ Access backend resources (DB, filesystem)
  ✅ Keep secrets on server
  ✅ Reduce client JS bundle
  ❌ No useState, useEffect, event handlers
  ❌ No browser APIs (localStorage, window)

Client Components ("use client"):
  ✅ Interactive (clicks, inputs, animations)
  ✅ Browser APIs
  ✅ React hooks (state, effects, refs)
  ❌ Can't directly access DB/filesystem
  ❌ Adds to client JS bundle
```

**Rule of thumb:** Start as Server Component. Add `"use client"` only when you need interactivity.

**Pattern — push "use client" down:**

```tsx
// ❌ Whole page is client
"use client"
export default function Page() { ... }

// ✅ Only the interactive part is client
export default function Page() {            // Server Component
  return (
    <div>
      <h1>Dashboard</h1>                    {/* Server — no JS shipped */}
      <StaticInfo />                        {/* Server */}
      <InteractiveChart />                  {/* Client — only this ships JS */}
    </div>
  )
}
```

---

## Accessibility (a11y)

### Semantic HTML — The Foundation

```tsx
// ❌ Divs for everything
<div className="nav">
  <div className="link" onClick={...}>Home</div>
</div>

// ✅ Semantic elements
<nav>
  <a href="/">Home</a>
</nav>
```

| Instead of | Use | Why |
|-----------|-----|-----|
| `<div>` for navigation | `<nav>` | Screen readers announce "navigation" |
| `<div onClick>` | `<button>` | Keyboard accessible, announced as button |
| `<div>` for main content | `<main>` | Screen readers can jump to it |
| `<div>` for sections | `<section>` / `<article>` | Provides document structure |
| `<span>` for headings | `<h1>`-`<h6>` | Screen readers build page outline |

### ARIA — When HTML Isn't Enough

```tsx
// Toggle button — announce the current state
<button
  aria-expanded={open}
  aria-controls="menu"
  aria-label="Toggle navigation menu"
>
  <Menu />
</button>

// The thing it controls
<div id="menu" role="menu" aria-hidden={!open}>
  ...
</div>
```

**Rule:** Prefer semantic HTML first. Only add ARIA when there's no native element for what you're building.

### Keyboard Navigation

Everything clickable must be keyboard-accessible:

| Element | Keyboard | Automatic? |
|---------|----------|-----------|
| `<a>` | Enter | ✅ |
| `<button>` | Enter / Space | ✅ |
| `<div onClick>` | Nothing | ❌ Broken! |
| Custom dropdown | Arrow keys, Escape | You must build it |

**Focus management for modals:**

```tsx
// When modal opens: trap focus inside it
// When modal closes: return focus to the trigger button
// Escape key: closes the modal
```

shadcn/ui handles all of this for you in `Dialog`, `Sheet`, `DropdownMenu`. That's why you use component libraries.

### Color Contrast

| WCAG Level | Ratio | Where |
|-----------|-------|-------|
| AA (minimum) | 4.5:1 | Normal text |
| AA | 3:1 | Large text (18px+ or 14px+ bold) |
| AAA (ideal) | 7:1 | Normal text |

**Test:** Chrome DevTools → inspect element → check the color picker shows a contrast ratio.

### prefers-reduced-motion

Some people get motion sick from animations. Respect their setting:

```tsx
// Tailwind
<motion.div className="motion-safe:animate-bounce">

// Framer Motion
<motion.div
  animate={{ y: [0, -10, 0] }}
  transition={{
    repeat: Infinity,
    // Disable for users who prefer reduced motion
    ...(window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? { duration: 0 }
      : { duration: 1 }),
  }}
/>
```

Or globally in Framer Motion:

```tsx
import { MotionConfig } from "motion/react"

<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

---

## Practice Projects for Level 3

| Project | What you'll practise |
|---------|---------------------|
| **Performance audit your own site** | Lighthouse, bundle analysis, fix CLS/LCP |
| **Accessible component library** | Keyboard nav, ARIA, screen reader testing |
| **Dashboard with 10k rows** | Virtual scrolling, memoisation, code splitting |
| **Redesign with feature-based structure** | Refactor existing project into features/ |
| **Contribute to shadcn/ui** | Read source, understand compound component patterns |

---

## How to Know You've Mastered Level 3

- [ ] Can audit a site with Lighthouse and fix every issue
- [ ] Know how to reduce bundle size without breaking features
- [ ] Automatically think about keyboard and screen reader users
- [ ] Can architect a project that stays maintainable at 50+ components
- [ ] Understand Server vs Client Component tradeoffs in Next.js
- [ ] Can explain virtual scrolling, code splitting, and memoisation to a junior
