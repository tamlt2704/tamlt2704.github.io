# Chapter 19: Pro React & Next.js — Advanced Frontend Engineering

## What you'll learn

- React rendering model (why things re-render, how to prevent it)
- Memoization: `useMemo`, `useCallback`, `React.memo` — when they help and when they hurt
- State management patterns at scale
- Next.js caching layers (request, data, full route, router)
- Static vs dynamic rendering decisions
- Streaming and Suspense for perceived performance
- Bundle analysis and code splitting
- Core Web Vitals optimisation (LCP, CLS, INP)
- Patterns: optimistic updates, infinite scroll, prefetching

---

## PART 1: React Performance — Understanding Re-renders

## 19.1 Why components re-render

A component re-renders when:

1. **Its state changes** (`useState` setter called)
2. **Its parent re-renders** (props may or may not have changed)
3. **A context it consumes changes** (`useContext`)

A component does **NOT** re-render when:
- A sibling re-renders
- An unrelated state somewhere else changes
- A ref changes (`useRef`)

```tsx
function Parent() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>Click</button>
      <ExpensiveChild />  {/* ← Re-renders every click! Even though its props didn't change */}
    </div>
  );
}
```

**Rule: When a parent re-renders, ALL its children re-render by default.** React doesn't check if props changed — it just re-renders the entire subtree. This is usually fine (React is fast). It's only a problem when:
- A child does expensive computation
- A child renders thousands of DOM elements
- Re-renders happen at high frequency (typing, scrolling, dragging)

## 19.2 React.memo — skip re-renders when props haven't changed

```tsx
const ExpensiveChild = React.memo(function ExpensiveChild({ data }: { data: number[] }) {
  // This only re-renders if `data` reference changes
  const sorted = [...data].sort((a, b) => a - b); // expensive
  return <div>{sorted.join(", ")}</div>;
});
```

`React.memo` wraps a component and performs a **shallow comparison** of props. If all props are the same (by reference), the re-render is skipped.

**When to use `React.memo`:**
- Component renders expensively (heavy DOM, complex calculations)
- Parent re-renders frequently but this child's props rarely change
- You've measured the re-render is actually causing a performance issue

**When NOT to use it:**
- The component is simple (a few divs + text) — memo comparison cost > render cost
- Props always change (new objects/arrays created in parent every render)
- You haven't measured a problem (premature optimisation)

## 19.3 useMemo — cache expensive calculations

```tsx
function SortingVisualiser({ data, algorithm }: Props) {
  // ❌ Recalculates on EVERY render (even when only `currentStep` changes)
  const steps = generateSteps(data, algorithm);

  // ✅ Only recalculates when data or algorithm changes
  const steps = useMemo(() => generateSteps(data, algorithm), [data, algorithm]);

  const [currentStep, setCurrentStep] = useState(0);
  // ...
}
```

`useMemo` caches the **result** of a function. It only re-runs when dependencies change.

**Good uses:**
- Expensive computations (sorting, filtering large arrays, generating steps)
- Creating objects that are passed as props to memoized children
- Derived state (computed from other state/props)

**Bad uses:**
- Simple operations (adding two numbers, string concatenation)
- Everything by default "just in case" (adds memory overhead + comparison cost)

## 19.4 useCallback — stable function references

```tsx
function Parent() {
  const [count, setCount] = useState(0);

  // ❌ New function created every render — breaks React.memo on children
  const handleClick = () => console.log(count);

  // ✅ Same function reference unless `count` changes
  const handleClick = useCallback(() => console.log(count), [count]);

  return <MemoizedChild onClick={handleClick} />;
}
```

`useCallback` is `useMemo` for functions. It returns the **same function reference** between renders (unless dependencies change).

**Only useful when:**
- The function is passed as a prop to a `React.memo` child
- The function is a dependency of another hook (`useEffect`, `useMemo`)

**Pointless when:**
- The function isn't passed to a memoized component
- There's no performance issue to solve

## 19.5 The composition pattern (free performance)

Instead of memoization, restructure your components:

```tsx
// ❌ Problem: ExpensiveTree re-renders on every count change
function App() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(c => c + 1)}>+</button>
      <ExpensiveTree />
    </div>
  );
}

// ✅ Solution: Lift state into its own component
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  );
}

function App() {
  return (
    <div>
      <Counter />
      <ExpensiveTree />  {/* ← Never re-renders (App never re-renders) */}
    </div>
  );
}
```

**The children pattern:**

```tsx
// ✅ Even better — pass ExpensiveTree as children
function CounterLayout({ children }: { children: React.ReactNode }) {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(c => c + 1)}>+</button>
      {children}  {/* ← children don't re-render because they're created by the parent */}
    </div>
  );
}

function App() {
  return (
    <CounterLayout>
      <ExpensiveTree />
    </CounterLayout>
  );
}
```

`children` are created in `App` (which doesn't re-render), so `ExpensiveTree` keeps the same reference even when `CounterLayout` re-renders.

## 19.6 State management at scale

| Pattern | Best for | Examples |
|---------|----------|---------|
| `useState` | Component-local state | Form inputs, toggles, current step |
| `useReducer` | Complex state logic | Multi-field forms, state machines |
| Context + `useReducer` | Shared state across a subtree | Theme, auth, app settings |
| URL state (`useSearchParams`) | Shareable/bookmarkable state | Filters, pagination, sort order |
| Server state (React Query / SWR) | Remote data + cache | API responses, user data |
| Zustand / Jotai | Global client state | Shopping cart, multi-step wizards |

**Rules of thumb:**
- Start with `useState`. Upgrade when it hurts.
- If state is derived from a URL, put it IN the URL (`?sort=date&page=2`)
- If state comes from an API, use React Query or SWR (handles cache, refetch, stale data)
- If you're prop-drilling more than 3 levels, consider context or a store
- Context re-renders ALL consumers on any change — split contexts by update frequency

```tsx
// ❌ One big context — everything re-renders when anything changes
const AppContext = createContext({ user, theme, notifications, cart });

// ✅ Split contexts — only relevant consumers re-render
const UserContext = createContext(user);
const ThemeContext = createContext(theme);
const CartContext = createContext(cart);
```

## 19.7 useTransition — keep the UI responsive

When a state update triggers expensive rendering, `useTransition` marks it as low-priority:

```tsx
function SearchResults() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value); // HIGH priority — update input immediately

    startTransition(() => {
      // LOW priority — can be interrupted by new input
      setResults(filterLargeDataset(e.target.value));
    });
  }

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <Spinner />}
      <ResultsList results={results} />
    </div>
  );
}
```

The input stays snappy even if filtering 100,000 items. Without `useTransition`, every keystroke would freeze the UI until filtering completes.



---

## PART 2: Next.js Caching & Rendering Strategies

## 19.8 The Next.js caching layers

Next.js has multiple caching layers. Understanding them is the difference between a fast app and a frustratingly stale one.

```
Request → Router Cache → Full Route Cache → Data Cache → Origin (DB/API)
         (client)        (server/CDN)        (server)
```

| Layer | Where | What it caches | Duration | How to invalidate |
|-------|-------|---------------|----------|-------------------|
| **Router Cache** | Browser | RSC payload of visited routes | Session (auto) | `router.refresh()`, navigation, revalidation |
| **Full Route Cache** | Server/CDN | Complete HTML + RSC payload | Until revalidation | `revalidatePath()`, `revalidateTag()`, redeploy |
| **Data Cache** | Server | `fetch()` responses | Until revalidation | `revalidateTag()`, time-based `revalidate` |
| **Request Memoization** | Server (per-request) | Duplicate `fetch()` calls | Single request | Automatic (request ends) |

## 19.9 Static vs dynamic rendering

Next.js decides at **build time** whether a route is static or dynamic:

**Static** (default) — rendered at build time, cached, served from CDN:
```tsx
// This page is static — no dynamic data
export default function AboutPage() {
  return <div>About us</div>;
}
```

**Dynamic** — rendered on every request:
```tsx
// Any of these make a route dynamic:
import { cookies, headers } from "next/headers";
import { searchParams } from "next/navigation";

export default async function Page({ searchParams }) {
  const params = await searchParams;  // ← dynamic (depends on request)
  const cookieStore = await cookies(); // ← dynamic
  const headerList = await headers();  // ← dynamic

  // fetch with no-store
  const data = await fetch(url, { cache: "no-store" }); // ← dynamic
}
```

**Force static even with data fetching:**
```tsx
// Revalidate every 60 seconds (ISR — Incremental Static Regeneration)
export const revalidate = 60;

export default async function Page() {
  const data = await fetch("https://api.example.com/posts");
  // Served from cache, rebuilt in background every 60s
  return <PostList posts={data} />;
}
```

## 19.10 Data fetching patterns

```tsx
// 1. Static data (built once, cached forever until redeploy)
const data = await fetch("https://api.example.com/posts");

// 2. Revalidate on a timer (ISR)
const data = await fetch("https://api.example.com/posts", {
  next: { revalidate: 3600 }, // re-fetch at most every hour
});

// 3. Revalidate on demand (tag-based)
const data = await fetch("https://api.example.com/posts", {
  next: { tags: ["posts"] },
});
// Then in a Server Action:
import { revalidateTag } from "next/cache";
revalidateTag("posts"); // purges all fetches tagged "posts"

// 4. Always fresh (no cache)
const data = await fetch("https://api.example.com/posts", {
  cache: "no-store",
});

// 5. Parallel data fetching (avoid waterfalls)
const [posts, user, stats] = await Promise.all([
  fetch("/api/posts"),
  fetch("/api/user"),
  fetch("/api/stats"),
]);
```

## 19.11 Streaming and Suspense

Instead of waiting for ALL data before showing anything, stream content as it becomes available:

```tsx
import { Suspense } from "react";

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {/* These load instantly (static or fast) */}
      <Header />
      <Sidebar />

      {/* These stream in when ready */}
      <Suspense fallback={<CardSkeleton />}>
        <RevenueChart />  {/* Slow API — shows skeleton, then swaps in */}
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />  {/* Another slow query */}
      </Suspense>
    </div>
  );
}
```

**How it works:**
1. Next.js sends the HTML shell immediately (header, sidebar, skeletons)
2. Slow components render on the server in parallel
3. As each finishes, its HTML is streamed to the browser and swaps out the skeleton
4. No client-side JavaScript is needed for this — it's pure server streaming

**User perception:** The page appears instantly (LCP is fast), and content fills in progressively. Much better than a blank page waiting 3 seconds for all data.

## 19.12 `loading.tsx` — route-level Suspense

```
app/
  dashboard/
    page.tsx
    loading.tsx    ← Shown while page.tsx loads
```

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse space-y-4 p-4">
      <div className="h-8 bg-gray-200 rounded w-1/3" />
      <div className="h-64 bg-gray-200 rounded" />
      <div className="h-32 bg-gray-200 rounded" />
    </div>
  );
}
```

This wraps the entire route in a Suspense boundary automatically. Use it for page-level loading. Use `<Suspense>` directly for more granular control.

## 19.13 Server Components vs Client Components

| Feature | Server Component (default) | Client Component (`"use client"`) |
|---------|---------------------------|----------------------------------|
| Runs where | Server only | Server (initial) + Client (hydration + updates) |
| Access to | `fs`, `db`, env vars, `fetch` | Browser APIs, `useState`, `useEffect`, event handlers |
| Bundle size | Zero JS sent to client | JS sent to client |
| Can use hooks? | No | Yes |
| Can use `async`? | Yes (`async function Page()`) | No |

**Strategy: Server by default, Client only when needed.**

Push client components to the **leaves** of your component tree:

```tsx
// ✅ Server Component — no JS shipped
export default async function BlogPost({ params }) {
  const { slug } = await params;
  const post = await getPost(slug); // server-only data fetch

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
      <LikeButton postId={post.id} />  {/* ← Only this ships JS */}
    </article>
  );
}

// Client Component — only the interactive bit
"use client";
function LikeButton({ postId }: { postId: string }) {
  const [liked, setLiked] = useState(false);
  return <button onClick={() => setLiked(!liked)}>♥ {liked ? "Liked" : "Like"}</button>;
}
```

The entire blog post renders as static HTML (fast, cacheable, no JS). Only the Like button ships JavaScript.



---

## PART 3: Bundle Optimisation & Core Web Vitals

## 19.14 Code splitting — send only what's needed

Next.js automatically code-splits by route. But within a route, you can split further:

```tsx
import dynamic from "next/dynamic";

// Heavy component loaded only when needed
const ThreeScene = dynamic(() => import("@/components/ThreeScene"), {
  loading: () => <div className="h-[500px] bg-gray-100 animate-pulse rounded" />,
  ssr: false, // Three.js needs browser APIs — skip server rendering
});

export default function Page() {
  const [show3D, setShow3D] = useState(false);
  return (
    <div>
      <button onClick={() => setShow3D(true)}>Show 3D View</button>
      {show3D && <ThreeScene />}  {/* JS loaded only when shown */}
    </div>
  );
}
```

**What to dynamically import:**
- Heavy libraries (Three.js, D3, Monaco Editor, PDF viewers)
- Components below the fold (not visible on initial load)
- Conditional features (admin panels, export dialogs)
- Route-specific components that aren't on every page

## 19.15 Bundle analysis

```bash
npm install -D @next/bundle-analyzer
```

```js
// next.config.mjs
import bundleAnalyzer from "@next/bundle-analyzer";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

export default withBundleAnalyzer(nextConfig);
```

```bash
ANALYZE=true npm run build
# Opens a visual treemap of your bundle
```

**Common bundle problems:**
| Problem | Fix |
|---------|-----|
| Full `lodash` imported | Use `lodash-es` or `lodash/specific-function` |
| Moment.js (500KB) | Replace with `date-fns` (tree-shakeable) |
| Full `d3` imported | Import specific modules: `import { select } from "d3-selection"` |
| Icons library (all icons) | Import specific icons: `import { ArrowRight } from "lucide-react"` |
| Unused dependencies | Remove from `package.json`, verify with bundle analyzer |

## 19.16 Tree shaking — import only what you use

```tsx
// ❌ Imports entire d3 library (~500KB)
import * as d3 from "d3";

// ✅ Import only what you need (~30KB)
import { select, selectAll } from "d3-selection";
import { scaleLinear, scaleBand } from "d3-scale";
import { max } from "d3-array";
import { transition } from "d3-transition";
```

This works because each `d3-*` package is a separate ES module. The bundler can tree-shake unused exports.

## 19.17 Core Web Vitals — what Google measures

| Metric | What it measures | Target | Controlled by |
|--------|-----------------|--------|---------------|
| **LCP** (Largest Contentful Paint) | When the biggest visible element renders | < 2.5s | Image optimisation, SSR, streaming |
| **CLS** (Cumulative Layout Shift) | How much the page jumps while loading | < 0.1 | Image dimensions, font loading, dynamic content |
| **INP** (Interaction to Next Paint) | Responsiveness to user input | < 200ms | Main thread work, React re-renders, heavy JS |

## 19.18 Optimising LCP

LCP is usually your hero image, heading, or largest text block.

```tsx
// 1. Use Next.js Image with priority for above-the-fold images
import Image from "next/image";

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority  // ← Preloads this image (no lazy loading)
  sizes="100vw"
/>

// 2. Preload critical fonts (in layout.tsx)
import { Inter } from "next/font/google";
const inter = Inter({ subsets: ["latin"], display: "swap" });

// 3. Avoid client-side data fetching for above-the-fold content
// Use Server Components — content is in the initial HTML

// 4. Stream the shell early (loading.tsx gives immediate content)
```

## 19.19 Preventing CLS (Layout Shift)

```tsx
// 1. ALWAYS set width and height on images
<Image src="/photo.jpg" width={800} height={450} alt="" />
// This reserves space before the image loads

// 2. Use aspect-ratio for responsive containers
<div className="aspect-video relative">
  <Image src="/photo.jpg" fill alt="" className="object-cover" />
</div>

// 3. Reserve space for dynamic content
<div className="min-h-[200px]">  {/* Prevents collapse before content loads */}
  <Suspense fallback={<Skeleton className="h-[200px]" />}>
    <DynamicContent />
  </Suspense>
</div>

// 4. Font display: swap (already handled by next/font)
// Prevents invisible text while fonts load
```

## 19.20 Optimising INP (Responsiveness)

INP measures time from user interaction (click, tap, keypress) to the next visual update.

```tsx
// 1. Avoid blocking the main thread
// ❌ Heavy computation on click
function handleClick() {
  const result = heavySort(millionItems); // blocks UI for 500ms
  setData(result);
}

// ✅ Use useTransition for non-urgent updates
const [isPending, startTransition] = useTransition();
function handleClick() {
  startTransition(() => {
    setData(heavySort(millionItems)); // doesn't block input
  });
}

// 2. Debounce expensive operations
function SearchInput() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300); // custom hook

  useEffect(() => {
    if (debouncedQuery) search(debouncedQuery);
  }, [debouncedQuery]);

  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}

// 3. Virtualise long lists (only render visible items)
import { useVirtualizer } from "@tanstack/react-virtual";

function VirtualList({ items }: { items: string[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40, // estimated row height
  });

  return (
    <div ref={parentRef} className="h-[400px] overflow-auto">
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map(row => (
          <div
            key={row.key}
            style={{ height: row.size, transform: `translateY(${row.start}px)` }}
            className="absolute w-full"
          >
            {items[row.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 19.21 Image optimisation

```tsx
import Image from "next/image";

// Automatic optimisation: WebP/AVIF conversion, resizing, lazy loading
<Image
  src="/blog/hero.jpg"
  alt="Blog post hero image"
  width={1200}
  height={630}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
  quality={85}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,/9j/4AAQ..." // tiny base64 placeholder
/>

// For static export (GitHub Pages) — disable optimization
// next.config: images: { unoptimized: true }
// In this case, pre-optimize images yourself:
// - Use .webp format
// - Compress with tools like squoosh.app
// - Provide multiple sizes with <picture> / srcset
```

## 19.22 Font optimisation

```tsx
// next/font automatically:
// - Self-hosts fonts (no external requests to Google)
// - Eliminates layout shift (size-adjust CSS)
// - Subsets to only used characters

import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",      // show fallback font immediately, swap when loaded
  variable: "--font-inter",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
});

// In layout.tsx
<body className={`${inter.variable} ${mono.variable} font-sans`}>
```



---

## PART 4: Advanced Patterns

## 19.23 Optimistic updates — instant UI feedback

Don't wait for the server to confirm before updating the UI:

```tsx
"use client";

import { useOptimistic } from "react";

function LikeButton({ postId, initialLikes }: { postId: string; initialLikes: number }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    initialLikes,
    (current, _) => current + 1
  );

  async function handleLike() {
    addOptimisticLike(null); // Instantly show +1

    // Server request happens in background
    await fetch(`/api/posts/${postId}/like`, { method: "POST" });
    // If it fails, React reverts the optimistic update automatically
  }

  return (
    <button onClick={handleLike}>
      ♥ {optimisticLikes}
    </button>
  );
}
```

**Use for:** Like buttons, bookmark toggles, comment posting, form submissions. Anything where the expected outcome is almost always success.

## 19.24 Prefetching — load before the user clicks

Next.js `<Link>` prefetches by default (when visible in viewport). But you can also prefetch programmatically:

```tsx
"use client";

import { useRouter } from "next/navigation";

function PostCard({ slug }: { slug: string }) {
  const router = useRouter();

  return (
    <div
      onMouseEnter={() => router.prefetch(`/blog/${slug}`)}  // Prefetch on hover
      onClick={() => router.push(`/blog/${slug}`)}
    >
      ...
    </div>
  );
}
```

**Prefetch strategies:**
- **Viewport** (default for `<Link>`) — prefetch when link scrolls into view
- **Hover** — prefetch when user hovers (300ms before click typically)
- **Intent** — prefetch based on mouse trajectory prediction (advanced)

## 19.25 Parallel routes — multiple pages in one layout

Show different content sections that can load/error independently:

```
app/
  dashboard/
    @analytics/
      page.tsx         ← Analytics panel
      loading.tsx      ← Its own loading state
    @activity/
      page.tsx         ← Activity feed
      loading.tsx      ← Its own loading state
    layout.tsx         ← Composes both
    page.tsx           ← Main content
```

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  activity,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  activity: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <main className="col-span-2">{children}</main>
      <aside className="space-y-4">
        {analytics}
        {activity}
      </aside>
    </div>
  );
}
```

Each `@slot` is an independent route segment that:
- Loads in parallel (no waterfall)
- Has its own loading/error states
- Can be conditionally shown
- Navigates independently

## 19.26 Error boundaries — graceful failure

```tsx
// app/dashboard/error.tsx
"use client";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="p-6 border border-red-200 bg-red-50 rounded-lg">
      <h2 className="text-lg font-semibold text-red-800">Something went wrong</h2>
      <p className="text-sm text-red-600 mt-2">{error.message}</p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Try again
      </button>
    </div>
  );
}
```

**Error boundary hierarchy:**
- `app/error.tsx` — catches errors from the entire app
- `app/dashboard/error.tsx` — catches errors only in the dashboard
- Errors bubble UP until caught by the nearest error boundary
- The rest of the app remains functional

## 19.27 Route handlers — API endpoints

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get("page") || "1");

  const posts = await db.posts.findMany({
    take: 10,
    skip: (page - 1) * 10,
  });

  return NextResponse.json(posts, {
    headers: {
      "Cache-Control": "public, s-maxage=60, stale-while-revalidate=300",
    },
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const post = await db.posts.create({ data: body });
  return NextResponse.json(post, { status: 201 });
}
```

## 19.28 Server Actions — form handling without API routes

```tsx
// app/blog/new/page.tsx
import { redirect } from "next/navigation";

export default function NewPostPage() {
  async function createPost(formData: FormData) {
    "use server";

    const title = formData.get("title") as string;
    const content = formData.get("content") as string;

    await db.posts.create({ data: { title, content } });
    revalidatePath("/blog");
    redirect("/blog");
  }

  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Publish</button>
    </form>
  );
}
```

**Server Actions advantages:**
- No API route boilerplate
- Works without JavaScript (progressive enhancement)
- Automatic form validation with `useFormStatus`
- Type-safe with TypeScript

## 19.29 Middleware — intercept requests

```tsx
// middleware.ts (at project root)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Redirect /old-blog/* to /blog/*
  if (request.nextUrl.pathname.startsWith("/old-blog")) {
    return NextResponse.redirect(
      new URL(request.nextUrl.pathname.replace("/old-blog", "/blog"), request.url)
    );
  }

  // Add security headers
  const response = NextResponse.next();
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  return response;
}

export const config = {
  matcher: [
    // Match all paths except static files and _next
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
```

**Use cases:** Auth checks, redirects, A/B testing, geo-based routing, rate limiting headers.

> **Note:** Middleware runs on the Edge runtime — no Node.js APIs (no `fs`, no heavy npm packages). Keep it lightweight.

## 19.30 Performance checklist

```
□ Server Components by default (only "use client" for interactivity)
□ Suspense boundaries around slow data fetches
□ loading.tsx for route-level loading states
□ Images: next/image with width, height, sizes, priority (above fold)
□ Fonts: next/font with display: "swap"
□ Dynamic imports for heavy libraries (Three.js, editors, charts)
□ Parallel data fetching (Promise.all, not sequential awaits)
□ Appropriate cache strategy per data type:
    - Static content: build-time (default)
    - Semi-static: ISR (revalidate: 3600)
    - User-specific: no-store + client cache (React Query)
□ No layout shift: set dimensions on images, min-height on dynamic sections
□ useTransition for non-urgent updates (search, filters)
□ Virtual lists for 100+ items
□ Bundle analyzer: no giant unused dependencies
□ Tree shaking: import specific modules, not entire libraries
```

## Summary

✅ You understand React's re-render model and when to optimise
✅ You know when `useMemo`, `useCallback`, and `React.memo` actually help
✅ You can structure components to avoid unnecessary re-renders (composition pattern)
✅ You understand all Next.js caching layers and how to control them
✅ You know static vs dynamic rendering and how to choose
✅ You can stream content with Suspense for better perceived performance
✅ You know how to code-split, tree-shake, and analyse bundles
✅ You understand Core Web Vitals (LCP, CLS, INP) and how to optimise each
✅ You can implement optimistic updates, prefetching, and parallel routes
✅ You know Server Components vs Client Components — and where to draw the line

## Key takeaways

**Don't optimise until you measure.** React is fast by default. Add `React.memo`/`useMemo` only after you've identified an actual performance bottleneck with DevTools Profiler.

**Server Components are the biggest performance win.** Zero client JS for content that doesn't need interactivity. Push interactivity to the smallest possible component (leaves of the tree).

**Caching is a spectrum, not a binary.** Choose per-route and per-data-source: fully static → ISR (time-based) → ISR (on-demand) → always fresh. Most content is semi-static.

**Perceived performance > actual performance.** Streaming + skeletons make a 3-second load feel like 300ms. The page appears instantly, content fills in. Users don't notice the loading if they have something to look at.

---

→ [Back to Chapter 18: Three.js Fundamentals](./18-THREEJS-FUNDAMENTALS.md)
