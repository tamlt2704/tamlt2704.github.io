# Chapter 12: Streaming & Suspense

[← Chapter 11: Static & ISR](chapter-11-static-isr.md) | [Chapter 13: API Routes →](chapter-13-api-routes.md)

---

## The Problem

The trail detail page fetches trail info (fast, 100ms) AND reviews (slow, 2 seconds — 100+ reviews with photos). Right now, the user waits 2 seconds for everything. They can't even see the trail name until reviews finish loading.

Raj: "Show the trail info immediately. Stream the reviews in when they're ready."

---

## Suspense: Stream Parts of a Page

```tsx
// src/app/trails/[slug]/page.tsx
import { Suspense } from "react";
import { TrailHeader } from "./TrailHeader";
import { Reviews } from "./Reviews";
import { ReviewsSkeleton } from "./ReviewsSkeleton";

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug); // fast: 100ms
  if (!trail) notFound();

  return (
    <div>
      <TrailHeader trail={trail} /> {/* renders immediately */}

      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews slug={slug} /> {/* streams in when ready */}
      </Suspense>
    </div>
  );
}
```

```tsx
// src/app/trails/[slug]/Reviews.tsx
async function Reviews({ slug }: { slug: string }) {
  const reviews = await getReviews(slug); // slow: 2 seconds

  return (
    <section className="mt-12">
      <h2 className="text-xl font-bold">Reviews ({reviews.length})</h2>
      <div className="mt-4 space-y-4">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </div>
    </section>
  );
}
```

### What Happens

```
0ms    → Server starts rendering
100ms  → Trail data ready → TrailHeader HTML sent to browser
100ms  → ReviewsSkeleton HTML sent (placeholder)
100ms  → User sees trail name, stats, description + skeleton
2000ms → Reviews data ready → Reviews HTML streamed to browser
2000ms → Skeleton replaced with real reviews (no page reload)
```

The user sees content at 100ms instead of 2000ms. The reviews appear later without any flash or reload. This is HTTP streaming — the server sends HTML in chunks.

---

## Multiple Suspense Boundaries

```tsx
export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);
  if (!trail) notFound();

  return (
    <div>
      <TrailHeader trail={trail} />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
        <div className="md:col-span-2">
          <Suspense fallback={<ReviewsSkeleton />}>
            <Reviews slug={slug} />
          </Suspense>
        </div>

        <aside>
          <Suspense fallback={<WeatherSkeleton />}>
            <WeatherWidget slug={slug} />
          </Suspense>

          <Suspense fallback={<NearbyTrailsSkeleton />}>
            <NearbyTrails slug={slug} />
          </Suspense>
        </aside>
      </div>
    </div>
  );
}
```

Each Suspense boundary streams independently. Weather might load in 500ms, reviews in 2s, nearby trails in 1s. Each appears as soon as it's ready. No waterfall.

---

## loading.tsx vs Suspense

| Feature | loading.tsx | `<Suspense>` |
|---|---|---|
| Scope | Entire page | Specific section |
| Granularity | One loading state per route | Multiple per page |
| Placement | File convention (automatic) | Manual (you choose where) |
| Use when | Page-level loading | Section-level streaming |

`loading.tsx` is actually just a Suspense boundary around your entire page. For finer control, use `<Suspense>` directly.

---

## Parallel Data Fetching (No Streaming)

If you want all data before rendering (no skeleton), but still want parallel fetches:

```tsx
export default async function TrailPage({ params }: Props) {
  const { slug } = await params;

  // Start both fetches simultaneously
  const trailPromise = getTrail(slug);
  const reviewsPromise = getReviews(slug);

  // Wait for both
  const [trail, reviews] = await Promise.all([trailPromise, reviewsPromise]);

  // Render with all data (no streaming, but no waterfall either)
  return (
    <div>
      <h1>{trail.name}</h1>
      <p>{reviews.length} reviews</p>
    </div>
  );
}
```

Use `Promise.all` when you need all data before rendering. Use `Suspense` when you can show partial content early.

---

## Skeleton Components

```tsx
// src/app/trails/[slug]/ReviewsSkeleton.tsx
export function ReviewsSkeleton() {
  return (
    <div className="mt-12 animate-pulse">
      <div className="h-6 w-32 bg-stone-200 rounded mb-4" />
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white p-4 rounded-lg shadow-sm mb-4">
          <div className="flex gap-2 mb-2">
            <div className="h-4 w-24 bg-stone-200 rounded" />
            <div className="h-4 w-16 bg-stone-200 rounded" />
          </div>
          <div className="space-y-2">
            <div className="h-3 w-full bg-stone-200 rounded" />
            <div className="h-3 w-4/5 bg-stone-200 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}
```

Match the skeleton shape to the real content. Users perceive the page as loading faster when the skeleton resembles the final layout.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
<Suspense fallback={<Skel/>}>   │ Stream content, show skeleton first
  <AsyncComponent />            │ Renders when data is ready
</Suspense>                     │
────────────────────────────────┼──────────────────────────────────────
Promise.all([a, b])             │ Parallel fetch, wait for all
Suspense + async component      │ Parallel fetch, stream as ready
loading.tsx                     │ Page-level Suspense (automatic)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Owen: "I need a webhook endpoint. When a trail is updated in the CMS, it should hit our Next.js app and trigger revalidation. Also, the weather widget needs a proxy — the weather API requires a secret key that can't be in the browser."

API Routes (Route Handlers).

---

[← Chapter 11: Static & ISR](chapter-11-static-isr.md) | [Chapter 13: API Routes →](chapter-13-api-routes.md)
