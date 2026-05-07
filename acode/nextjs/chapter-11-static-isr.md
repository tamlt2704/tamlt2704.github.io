# Chapter 11: Static Generation & ISR

[← Chapter 10: Images](chapter-10-images.md) | [Chapter 12: Streaming & Suspense →](chapter-12-streaming.md)

---

## The Problem

500 trail pages. Each server-rendered on every request. At peak traffic (Sunday morning, hikers planning), that's 500 API calls per second to Owen's backend. Owen: "My server is dying. Can you cache these pages?"

---

## Static Generation: Build Once, Serve Forever

Tell Next.js which pages to pre-build at deploy time:

```tsx
// src/app/trails/[slug]/page.tsx

export async function generateStaticParams() {
  const res = await fetch("http://localhost:4000/api/trails");
  const trails = await res.json();

  return trails.map((trail: Trail) => ({
    slug: trail.slug,
  }));
}

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);
  if (!trail) notFound();
  // ... render
}
```

At build time:
1. `generateStaticParams()` returns 500 slugs
2. Next.js renders each page to static HTML
3. The HTML files are served from CDN — no server, no API call

Result: every trail page loads in <100ms. Owen's API gets zero traffic from page views.

---

## ISR: Incremental Static Regeneration

Static pages go stale. A new review is posted but the page still shows the old count. ISR solves this:

```tsx
async function getTrail(slug: string): Promise<Trail | null> {
  const res = await fetch(`http://localhost:4000/api/trails/${slug}`, {
    next: { revalidate: 60 }, // ← regenerate after 60 seconds
  });
  if (!res.ok) return null;
  return res.json();
}
```

### How ISR Works

```
Request 1 (0s):    Serve cached page → fresh
Request 2 (30s):   Serve cached page → still fresh (within 60s)
Request 3 (65s):   Serve cached page → stale, trigger background regeneration
Request 4 (66s):   Serve NEW page → fresh (regenerated in background)
```

The user at request 3 gets stale content (fast). The regeneration happens in the background. The NEXT user gets fresh content. No one waits.

---

## On-Demand Revalidation

ISR with a timer is good. But when a user submits a review, you want the page to update immediately — not wait 60 seconds.

```tsx
// In your Server Action (after submitting a review):
import { revalidatePath } from "next/cache";

export async function submitReview(slug: string, formData: FormData) {
  // ... submit to API ...

  revalidatePath(`/trails/${slug}`); // ← bust the cache NOW
  redirect(`/trails/${slug}`);
}
```

Or revalidate by tag:

```tsx
// When fetching:
const res = await fetch(url, { next: { tags: ["trail-" + slug] } });

// When invalidating:
import { revalidateTag } from "next/cache";
revalidateTag("trail-mount-rainier");
```

Tags let you invalidate multiple pages at once. Change a trail's name? Revalidate the tag and every page using that trail's data refreshes.

---

## Webhook-Based Revalidation

Owen's API can notify you when data changes:

```tsx
// src/app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const secret = request.headers.get("x-revalidate-secret");
  if (secret !== process.env.REVALIDATE_SECRET) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { tag } = await request.json();
  revalidateTag(tag);

  return NextResponse.json({ revalidated: true });
}
```

Owen calls this endpoint whenever a trail is updated. The page regenerates immediately.

---

## Dynamic vs Static: When to Use Which

| Strategy | Use When | Example |
|---|---|---|
| **Static (generateStaticParams)** | Content known at build time | Trail pages, blog posts |
| **ISR (revalidate: N)** | Content changes occasionally | Trail detail (new reviews) |
| **On-demand revalidation** | Content changes on user action | After review submission |
| **Dynamic (no-store)** | Content must be real-time | User profile, live weather |

```tsx
// Static: built at deploy time
export async function generateStaticParams() { ... }

// ISR: cached, refreshes every 5 minutes
fetch(url, { next: { revalidate: 300 } });

// Dynamic: always fresh
fetch(url, { cache: "no-store" });

// Force entire page to be dynamic
export const dynamic = "force-dynamic";

// Force entire page to be static
export const dynamic = "force-static";
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Feature                         │ How
────────────────────────────────┼──────────────────────────────────────
Static generation               │ generateStaticParams() + fetch with cache
ISR (time-based)                │ fetch(url, { next: { revalidate: 60 } })
On-demand revalidation          │ revalidatePath() or revalidateTag()
Force dynamic                   │ export const dynamic = "force-dynamic"
Tag-based caching               │ fetch(url, { next: { tags: ["x"] } })
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The trail page loads fast — but the reviews section is slow (100+ reviews, each with photos). The user waits for ALL data before seeing ANYTHING. Can we show the trail info immediately and stream the reviews in later?

---

[← Chapter 10: Images](chapter-10-images.md) | [Chapter 12: Streaming & Suspense →](chapter-12-streaming.md)
