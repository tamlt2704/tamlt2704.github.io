# Chapter 9: Streaming on a Static Site

[← Chapter 8: Dark Mode](/blog/nextjs-ghpages/chapter-08-dark-mode) | [Chapter 10: Layout & Mobile →](/blog/nextjs-ghpages/chapter-10-layout-mobile)

---

## The Question

Next.js has streaming — React Server Components that send HTML in chunks, showing content progressively as it loads. `<Suspense>` boundaries, loading states, the whole deal.

But we're on GitHub Pages. Static HTML. No server. Can we still get streaming-like behavior?

**Short answer:** Not real streaming. But we can get the _experience_ of streaming — progressive rendering, skeleton states, and lazy-loaded heavy components that make the page feel fast even when content is large.

## What Real Streaming Is

With a Node.js server, Next.js streaming works like this:

```
Browser requests /blog/algorithms/chapter-01
    ↓
Server starts sending HTML immediately
    ↓
Shell (navbar, layout) arrives first → browser paints it
    ↓
<Suspense> boundary shows fallback (skeleton)
    ↓
Data resolves → server sends the chunk → replaces skeleton
```

The user sees _something_ instantly. Content fills in progressively.

## Why It Doesn't Work on Static

`output: "export"` means `next build` generates complete HTML files. There's no server to stream from. The browser gets the full page in one shot.

But "full page in one shot" doesn't mean "slow." Static pages are actually _faster_ than streamed ones for most content — there's no server processing time. The HTML is pre-built and served from a CDN.

The problem is **perceived performance** for pages with heavy interactive components (Pyodide, large visualizers, etc.).

## The Solution: Client-Side Progressive Loading

We can't stream from the server, but we can:

1. **Render the static content instantly** (it's already in the HTML)
2. **Lazy-load heavy components** with loading skeletons
3. **Progressively reveal sections** as they enter the viewport

This gives the _feeling_ of streaming without a server.

## Technique 1: Lazy Components with Suspense

Heavy components (CodePlayground with Pyodide, large visualizers) shouldn't block the initial page paint. `React.lazy()` splits them into a separate JavaScript file that loads only when needed.

```tsx
"use client";

import { lazy, Suspense } from "react";
// lazy: loads a component's code only when it's about to render (code splitting)
// Suspense: shows a fallback UI while the lazy component is loading

// lazy() takes a function that returns a dynamic import()
// The browser downloads CodePlayground's JS only when <LazyPlayground> renders
const CodePlayground = lazy(
  () =>
    import("./CodePlayground") // Dynamic import — creates a separate JS chunk
      .then((m) => ({ default: m.CodePlayground })), // Adapt named export to default
);

// Skeleton: a placeholder that mimics the component's shape while it loads
// animate-pulse = gentle opacity animation (Tailwind built-in)
function PlaygroundSkeleton() {
  return (
    <div className="my-6 animate-pulse overflow-hidden rounded-lg border border-gray-300">
      <div className="h-48 bg-gray-800" /> {/* Mimics the dark editor area */}
      <div className="h-10 bg-gray-100 dark:bg-gray-700" /> {/* Mimics the controls bar */}
    </div>
  );
}

// The wrapper component you actually use in MDX
// Suspense catches the "loading" state from lazy() and shows the skeleton
export function LazyPlayground(props: any) {
  return (
    <Suspense fallback={<PlaygroundSkeleton />}>
      <CodePlayground {...props} />
    </Suspense>
  );
}
```

**What happens at runtime:**

1. Page loads → reader sees article text immediately (static HTML)
2. Reader scrolls to the playground → React renders `<LazyPlayground>`
3. `<Suspense>` shows the skeleton while `CodePlayground`'s JS downloads
4. JS arrives → skeleton replaced with the real interactive component

The reader never waits for heavy components they haven't scrolled to yet.

Register `LazyPlayground` instead of `CodePlayground` in your MDX components:

```tsx
components={{
  CodePlayground: LazyPlayground,  // lazy-loaded with skeleton
  Quiz,                             // small, loads immediately
  StepVisualizer,                   // small, loads immediately
}}
```

The page renders instantly with the markdown content. The playground shows a skeleton, then pops in when its JavaScript loads. No blocking.

## Technique 2: Intersection Observer for Progressive Reveal

For long chapters, you can fade in sections as the reader scrolls to them. The `IntersectionObserver` API tells you when an element enters the viewport — no scroll event listeners needed (better performance).

```tsx
"use client";

import { useRef, useEffect, useState } from "react";

export function RevealOnScroll({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null); // Reference to the wrapper div
  const [visible, setVisible] = useState(false); // Has the element been seen?

  useEffect(() => {
    // IntersectionObserver watches an element and fires when it enters/exits the viewport
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          // Element is now visible (at least 10%)
          setVisible(true); // Trigger the fade-in
          observer.disconnect(); // Stop watching — only animate once
        }
      },
      { threshold: 0.1 }, // Fire when 10% of the element is visible
    );
    if (ref.current) observer.observe(ref.current); // Start watching
    return () => observer.disconnect(); // Cleanup when component unmounts
  }, []); // Empty deps = run once on mount

  return (
    <div
      ref={ref}
      // transition-all duration-500 = animate all properties over 500ms
      // When visible: full opacity, no vertical offset
      // When hidden: invisible, shifted down 16px (translate-y-4)
      className={`transition-all duration-500 ${
        visible ? "translate-y-0 opacity-100" : "translate-y-4 opacity-0"
      }`}
    >
      {children}
    </div>
  );
}
```

Use in markdown:

```markdown
<RevealOnScroll>

## Advanced: Time Complexity Proof

The recurrence relation T(n) = T(n/2) + O(1) solves to O(log n)...

</RevealOnScroll>
```

Content fades in as the reader reaches it. Feels alive without any server.

## Technique 3: Chunked Content Loading

For extremely long pages (50+ code blocks), split the markdown and load sections on demand:

```tsx
"use client";

import { useState } from "react";

export function LoadMore({
  children,
  preview,
}: {
  children: React.ReactNode;
  preview: React.ReactNode;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div>
      {preview}
      {expanded ? (
        children
      ) : (
        <button
          onClick={() => setExpanded(true)}
          className="mt-4 rounded border border-teal-200 px-4 py-2 text-sm text-teal-600 hover:bg-teal-50"
        >
          Show more ↓
        </button>
      )}
    </div>
  );
}
```

## Technique 4: Service Worker Pre-caching

For repeat visitors, a service worker can pre-cache adjacent chapters:

```typescript
// public/sw.js
self.addEventListener("install", (event) => {
  // Pre-cache the shell
});

self.addEventListener("fetch", (event) => {
  // Serve from cache, update in background
});
```

Register in your layout:

```tsx
useEffect(() => {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js");
  }
}, []);
```

When the reader finishes Chapter 3, Chapters 2 and 4 are already cached. Navigation feels instant.

## When You Actually Need a Server

If you outgrow static export, Next.js makes the transition easy:

1. Remove `output: "export"` from `next.config.ts`
2. Deploy to Vercel (free tier) or any Node.js host
3. Real streaming, ISR, server actions — all available

But for a blog with interactive components? Static + client-side progressive loading is more than enough. Your pages load in under 100ms from GitHub's CDN. No server can beat that.

## Summary

| Technique               | What It Does             | When to Use           |
| ----------------------- | ------------------------ | --------------------- |
| `lazy()` + `<Suspense>` | Defer heavy component JS | Pyodide, large libs   |
| IntersectionObserver    | Reveal on scroll         | Long chapters         |
| LoadMore                | Expand on click          | Optional deep content |
| Service Worker          | Pre-cache pages          | Multi-chapter series  |

Real streaming needs a server. But the _experience_ of progressive loading? That's just good client-side engineering. And it works perfectly on GitHub Pages.

---

## The Complete Series

You've built an interactive learning platform from scratch:

1. ✅ Static site on GitHub Pages
2. ✅ Markdown → pages pipeline
3. ✅ Syntax highlighting + typography
4. ✅ Quizzes for instant feedback
5. ✅ Code playgrounds (JS + Python)
6. ✅ Step-by-step visualizers
7. ✅ Navigation + SEO
8. ✅ Dark/light theme (no flash)
9. ✅ Progressive loading (streaming feel)

Total monthly cost: **$0**.
Total content files that need React knowledge: **0** (just markdown + component tags).
Total deploy steps: **`git push`**.

Your blog teaches back. Ship it. Write more. The platform handles the rest.
