# Chapter 5: Navigation, Loading & Error States

[← Chapter 4: Styling](chapter-04-styling.md) | [Chapter 6: SEO & Metadata →](chapter-06-seo.md)

---

## The Problem

Mika clicks a trail card. The API takes 800ms. During that time — nothing. White screen. No feedback. "Is it broken? Did I click it?"

Raj: "Show a skeleton immediately. And if Owen's API is down, show a friendly error — not a crash."

---

## loading.tsx: Instant Feedback

Drop a `loading.tsx` file in any route folder. Next.js shows it automatically while the page's async data loads.

```tsx
// src/app/trails/[slug]/loading.tsx
export default function TrailLoading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 w-64 bg-stone-200 rounded mb-4" />
      <div className="h-4 w-48 bg-stone-200 rounded mb-8" />
      <div className="flex gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="space-y-2">
            <div className="h-3 w-16 bg-stone-200 rounded" />
            <div className="h-5 w-12 bg-stone-200 rounded" />
          </div>
        ))}
      </div>
      <div className="mt-8 space-y-3">
        <div className="h-4 w-full bg-stone-200 rounded" />
        <div className="h-4 w-5/6 bg-stone-200 rounded" />
        <div className="h-4 w-4/6 bg-stone-200 rounded" />
      </div>
    </div>
  );
}
```

Now when you navigate to `/trails/mount-rainier`:
1. The skeleton appears instantly (no white flash)
2. The server fetches data
3. The real content replaces the skeleton

Under the hood, Next.js wraps your page in a `<Suspense>` boundary with `loading.tsx` as the fallback. You don't write the Suspense yourself.

---

## error.tsx: Graceful Failures

```tsx
// src/app/trails/[slug]/error.tsx
"use client"; // error boundaries must be client components

import { useEffect } from "react";

export default function TrailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log to error reporting service (Sentry, etc.)
    console.error("Trail page error:", error);
  }, [error]);

  return (
    <div className="max-w-md mx-auto px-6 py-24 text-center">
      <h2 className="text-2xl font-bold text-stone-900">Something went wrong</h2>
      <p className="mt-2 text-stone-600">
        We couldn't load this trail. The server might be having issues.
      </p>
      <button
        onClick={reset}
        className="mt-6 bg-emerald-600 text-white px-6 py-2 rounded-lg hover:bg-emerald-700"
      >
        Try again
      </button>
    </div>
  );
}
```

If `getTrail()` throws an error, this component catches it. The `reset` function re-attempts the render. The rest of the app (nav, layout) stays intact — only the broken segment shows the error.

### Error Boundary Hierarchy

```
layout.tsx (always visible)
├── loading.tsx (shown while loading)
├── error.tsx (catches errors in page.tsx)
└── page.tsx (the actual content)
```

Errors bubble up. If `/trails/[slug]/error.tsx` doesn't exist, the error propagates to `/trails/error.tsx`, then to the root `error.tsx`.

---

## not-found.tsx: Custom 404

```tsx
// src/app/trails/[slug]/not-found.tsx
import Link from "next/link";

export default function TrailNotFound() {
  return (
    <div className="text-center py-24">
      <h2 className="text-2xl font-bold">Trail not found</h2>
      <p className="mt-2 text-stone-600">
        This trail doesn't exist or may have been removed.
      </p>
      <Link href="/trails" className="mt-4 inline-block text-emerald-700 hover:underline">
        ← Browse all trails
      </Link>
    </div>
  );
}
```

Triggered by calling `notFound()` in your page component when the API returns no data.

---

## Link: Smart Navigation

```tsx
import Link from "next/link";

// Basic link
<Link href="/trails">All Trails</Link>

// Dynamic link
<Link href={`/trails/${trail.slug}`}>{trail.name}</Link>

// Prefetch disabled (for rarely-visited links)
<Link href="/admin" prefetch={false}>Admin</Link>

// Replace history (back button skips this page)
<Link href="/trails" replace>Back to trails</Link>
```

### What Link Does

1. **Prefetches** — when the link enters the viewport, Next.js fetches the page data in the background
2. **Client-side navigation** — no full page reload, only the changed segment re-renders
3. **Preserves state** — layout components don't unmount, scroll position is maintained

### Active Link Styling

```tsx
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

export function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname.startsWith(href + "/");

  return (
    <Link
      href={href}
      className={clsx(
        "transition-colors",
        isActive ? "text-emerald-700 font-medium" : "text-stone-600 hover:text-emerald-700"
      )}
    >
      {children}
    </Link>
  );
}
```

---

## Programmatic Navigation

```tsx
"use client";
import { useRouter } from "next/navigation";

export function SearchForm() {
  const router = useRouter();

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const query = new FormData(e.currentTarget).get("q");
    router.push(`/trails?q=${query}`);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="q" placeholder="Search trails..." />
    </form>
  );
}
```

| Method | What It Does |
|---|---|
| `router.push(url)` | Navigate (adds to history) |
| `router.replace(url)` | Navigate (replaces current entry) |
| `router.back()` | Go back |
| `router.refresh()` | Re-fetch server components (no full reload) |
| `router.prefetch(url)` | Prefetch a route manually |

---

## The Loading Hierarchy

```
User clicks /trails/mount-rainier
  │
  ├─ Layout stays (nav, shell) ← no re-render
  │
  ├─ loading.tsx shows immediately ← instant feedback
  │
  ├─ Server fetches trail data (800ms)
  │
  └─ page.tsx replaces loading.tsx ← content appears
```

The user never sees a blank screen. The nav stays. The skeleton shows. Content streams in. Professional.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
File                            │ Purpose
────────────────────────────────┼──────────────────────────────────────
loading.tsx                     │ Shown while page data loads
error.tsx                       │ Catches errors (must be "use client")
not-found.tsx                   │ Custom 404 page
────────────────────────────────┼──────────────────────────────────────
<Link href="...">              │ Client-side navigation + prefetch
useRouter()                     │ Programmatic navigation
usePathname()                   │ Current URL path
useSearchParams()               │ Current query params
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Priya: "Google still can't find our trail pages properly. I need unique titles, descriptions, and social media previews for every trail. When someone shares a trail on Twitter, I want a big image card."

SEO and metadata.

---

[← Chapter 4: Styling](chapter-04-styling.md) | [Chapter 6: SEO & Metadata →](chapter-06-seo.md)
