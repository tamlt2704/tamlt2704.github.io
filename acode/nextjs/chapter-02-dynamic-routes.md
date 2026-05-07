# Chapter 2: Dynamic Routes — 500 Trail Pages From One File

[← Chapter 1: First Page](chapter-01-first-page.md) | [Chapter 3: Data Fetching →](chapter-03-data-fetching.md)

---

## The Task

Raj: "We have 500 trails. Each needs its own page: `/trails/mount-rainier`, `/trails/olympic-coast`, `/trails/appalachian-ridge`. I'm not writing 500 files."

You don't have to. One file handles all of them.

---

## Dynamic Segments: [slug]

```
src/app/trails/[slug]/page.tsx
```

The brackets mean "this segment is dynamic." Any URL matching `/trails/ANYTHING` renders this page, with `ANYTHING` available as a parameter.

```tsx
// src/app/trails/[slug]/page.tsx
interface Props {
  params: Promise<{ slug: string }>;
}

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold capitalize">
        {slug.replace(/-/g, " ")}
      </h1>
      <p className="mt-4 text-stone-600">
        Trail detail page for: {slug}
      </p>
    </div>
  );
}
```

Visit `/trails/mount-rainier` → shows "mount rainier"
Visit `/trails/olympic-coast` → shows "olympic coast"
Visit `/trails/anything-at-all` → shows "anything at all"

One file. Infinite pages.

### Why `params` is a Promise

In Next.js 15+, `params` is async. This allows the framework to start rendering the layout before the params are fully resolved (useful for streaming). Always `await` it.

---

## The Trail Listing Page

```tsx
// src/app/trails/page.tsx
import Link from "next/link";

// Hardcoded for now — we'll fetch from the API in Chapter 3
const trails = [
  { slug: "mount-rainier", name: "Mount Rainier", difficulty: "hard", distance: 14 },
  { slug: "olympic-coast", name: "Olympic Coast", difficulty: "moderate", distance: 8 },
  { slug: "enchantments", name: "The Enchantments", difficulty: "expert", distance: 29 },
  { slug: "rattlesnake-ledge", name: "Rattlesnake Ledge", difficulty: "easy", distance: 5 },
];

export default function TrailsPage() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-8">All Trails</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trails.map((trail) => (
          <Link
            key={trail.slug}
            href={`/trails/${trail.slug}`}
            className="block p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
          >
            <h2 className="font-semibold text-lg">{trail.name}</h2>
            <p className="text-stone-500 mt-1">{trail.distance} km · {trail.difficulty}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

Click any trail → navigates to `/trails/mount-rainier` → the dynamic page renders with that slug.

---

## Nested Dynamic Routes

Reviews live under trails: `/trails/mount-rainier/reviews`

```
src/app/trails/[slug]/
├── page.tsx              → /trails/:slug
├── reviews/
│   └── page.tsx          → /trails/:slug/reviews
└── layout.tsx            → wraps both pages
```

```tsx
// src/app/trails/[slug]/reviews/page.tsx
interface Props {
  params: Promise<{ slug: string }>;
}

export default async function ReviewsPage({ params }: Props) {
  const { slug } = await params;

  return (
    <div>
      <h2 className="text-2xl font-bold">Reviews for {slug.replace(/-/g, " ")}</h2>
      <p className="text-stone-600 mt-2">Reviews will load from the API in Chapter 3.</p>
    </div>
  );
}
```

### Trail Layout (Shared Between Detail + Reviews)

```tsx
// src/app/trails/[slug]/layout.tsx
import Link from "next/link";

interface Props {
  children: React.ReactNode;
  params: Promise<{ slug: string }>;
}

export default async function TrailLayout({ children, params }: Props) {
  const { slug } = await params;

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <nav className="flex gap-4 mb-8 border-b pb-4">
        <Link
          href={`/trails/${slug}`}
          className="text-emerald-700 font-medium hover:underline"
        >
          Overview
        </Link>
        <Link
          href={`/trails/${slug}/reviews`}
          className="text-emerald-700 font-medium hover:underline"
        >
          Reviews
        </Link>
      </nav>
      {children}
    </div>
  );
}
```

The tab navigation persists when switching between Overview and Reviews. The layout doesn't re-render — only `{children}` swaps. Smooth.

---

## Catch-All Routes

What if you need `/docs/getting-started/installation/step-1`? Arbitrary depth?

```
src/app/docs/[...segments]/page.tsx
```

```tsx
interface Props {
  params: Promise<{ segments: string[] }>;
}

export default async function DocsPage({ params }: Props) {
  const { segments } = await params;
  // /docs/getting-started/installation → segments = ["getting-started", "installation"]

  return <div>Path: {segments.join(" / ")}</div>;
}
```

`[...segments]` matches any number of URL segments. Useful for documentation, file browsers, or CMS-driven pages.

### Optional Catch-All

```
src/app/docs/[[...segments]]/page.tsx
```

Double brackets = also matches the root (`/docs` with no segments). `segments` will be `undefined` or an empty array.

---

## Route Groups: Organize Without Affecting URLs

You want to group routes logically without adding URL segments:

```
src/app/
├── (marketing)/
│   ├── page.tsx          → / (home)
│   ├── about/page.tsx    → /about
│   └── layout.tsx        → marketing layout (centered, simple)
├── (app)/
│   ├── trails/page.tsx   → /trails
│   ├── profile/page.tsx  → /profile
│   └── layout.tsx        → app layout (sidebar, nav)
└── layout.tsx            → root layout
```

Parentheses `()` = route group. The folder name is NOT part of the URL. `/about` still works — not `/(marketing)/about`.

Use this to apply different layouts to different sections without nesting URLs.

---

## Parallel Routes (Advanced)

Show multiple pages simultaneously in the same layout:

```
src/app/dashboard/
├── layout.tsx
├── page.tsx
├── @analytics/page.tsx    → slot: analytics panel
└── @activity/page.tsx     → slot: activity feed
```

```tsx
// src/app/dashboard/layout.tsx
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
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">{children}</div>
      <div className="space-y-6">
        {analytics}
        {activity}
      </div>
    </div>
  );
}
```

Each `@slot` loads independently. If analytics is slow, it shows its own loading state without blocking the rest. We'll use this in Chapter 12 (Streaming).

---

## Not Found: Custom 404

```tsx
// src/app/not-found.tsx
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="max-w-md mx-auto px-6 py-24 text-center">
      <h1 className="text-6xl font-bold text-stone-300">404</h1>
      <p className="mt-4 text-stone-600">This trail doesn't exist. Yet.</p>
      <Link
        href="/trails"
        className="mt-6 inline-block text-emerald-700 hover:underline"
      >
        ← Back to all trails
      </Link>
    </div>
  );
}
```

You can also trigger it programmatically:

```tsx
import { notFound } from "next/navigation";

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);

  if (!trail) notFound(); // renders not-found.tsx

  return <div>{trail.name}</div>;
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ URL Example
────────────────────────────────┼──────────────────────────────────────
app/trails/page.tsx             │ /trails
app/trails/[slug]/page.tsx      │ /trails/mount-rainier
app/trails/[slug]/reviews/page  │ /trails/mount-rainier/reviews
app/docs/[...path]/page.tsx     │ /docs/a/b/c (catch-all)
app/docs/[[...path]]/page.tsx   │ /docs OR /docs/a/b (optional catch-all)
app/(group)/page.tsx            │ / (group doesn't affect URL)
app/dashboard/@slot/page.tsx    │ parallel route (slot)
────────────────────────────────┼──────────────────────────────────────
params.slug                     │ dynamic segment value
params.path                     │ catch-all segments array
notFound()                      │ trigger 404 page
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The trail detail page shows the slug as text. Raj: "I need real data. Trail name, description, photos, difficulty rating. Fetch it from Owen's API."

Server-side data fetching. The thing that makes Next.js different from a plain React app.

---

[← Chapter 1: First Page](chapter-01-first-page.md) | [Chapter 3: Data Fetching →](chapter-03-data-fetching.md)
