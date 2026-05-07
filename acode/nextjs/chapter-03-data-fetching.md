# Chapter 3: Data Fetching — Server Components Are Async

[← Chapter 2: Dynamic Routes](chapter-02-dynamic-routes.md) | [Chapter 4: Styling →](chapter-04-styling.md)

---

## The Task

Raj: "The trail pages need real data. Name, description, difficulty, distance, elevation, rating. Owen's API is ready. Fetch it."

In Next.js, Server Components are `async`. They can `await` data directly — no `useEffect`, no `useState`, no loading spinners. The server fetches the data, renders the HTML, and sends a complete page.

---

## Fetching in a Server Component

```tsx
// src/app/trails/[slug]/page.tsx
import { notFound } from "next/navigation";
import type { Trail } from "@/types";

async function getTrail(slug: string): Promise<Trail | null> {
  const res = await fetch(`http://localhost:4000/api/trails/${slug}`);
  if (!res.ok) return null;
  return res.json();
}

interface Props {
  params: Promise<{ slug: string }>;
}

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);

  if (!trail) notFound();

  return (
    <div>
      <h1 className="text-3xl font-bold">{trail.name}</h1>
      <p className="text-stone-500 mt-1">{trail.location}</p>

      <div className="flex gap-6 mt-6 text-sm">
        <div>
          <span className="text-stone-400">Distance</span>
          <p className="font-medium">{trail.distance_km} km</p>
        </div>
        <div>
          <span className="text-stone-400">Elevation</span>
          <p className="font-medium">{trail.elevation_m} m</p>
        </div>
        <div>
          <span className="text-stone-400">Difficulty</span>
          <p className="font-medium capitalize">{trail.difficulty}</p>
        </div>
        <div>
          <span className="text-stone-400">Rating</span>
          <p className="font-medium">★ {trail.rating.toFixed(1)} ({trail.review_count})</p>
        </div>
      </div>

      <p className="mt-8 text-stone-700 leading-relaxed">{trail.description}</p>
    </div>
  );
}
```

### What Happens

```
1. User visits /trails/mount-rainier
2. Next.js server receives the request
3. Server calls Owen's API (server-to-server, fast, no CORS)
4. Server renders the component with the data
5. Browser receives complete HTML with trail name, stats, description
6. User sees content immediately — no loading spinner
```

No `useEffect`. No `useState`. No loading state. The component is a function that awaits data and returns JSX. Simple.

---

## Fetching Multiple Resources

The trail page also needs reviews:

```tsx
// src/app/trails/[slug]/page.tsx
import type { Trail, Review } from "@/types";

async function getTrail(slug: string): Promise<Trail | null> {
  const res = await fetch(`http://localhost:4000/api/trails/${slug}`);
  if (!res.ok) return null;
  return res.json();
}

async function getReviews(slug: string): Promise<Review[]> {
  const res = await fetch(`http://localhost:4000/api/trails/${slug}/reviews`);
  if (!res.ok) return [];
  return res.json();
}

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;

  // Fetch in parallel — don't waterfall
  const [trail, reviews] = await Promise.all([
    getTrail(slug),
    getReviews(slug),
  ]);

  if (!trail) notFound();

  return (
    <div>
      <h1 className="text-3xl font-bold">{trail.name}</h1>
      {/* ... trail details ... */}

      <section className="mt-12">
        <h2 className="text-xl font-bold">Reviews ({reviews.length})</h2>
        <div className="mt-4 space-y-4">
          {reviews.map((review) => (
            <div key={review.id} className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center gap-2">
                <span className="font-medium">{review.user_name}</span>
                <span className="text-amber-500">{"★".repeat(review.rating)}</span>
              </div>
              <p className="mt-2 text-stone-600">{review.text}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
```

`Promise.all` fetches trail and reviews simultaneously. Without it, they'd run sequentially (waterfall) — trail takes 200ms, then reviews takes 200ms = 400ms total. With `Promise.all`: 200ms total.

---

## Caching & Revalidation

By default, Next.js caches `fetch()` responses in Server Components. You control how long:

```tsx
// Cache forever (static — rebuilt only on deploy)
const res = await fetch(url);

// Cache for 60 seconds (ISR — revalidates in background)
const res = await fetch(url, { next: { revalidate: 60 } });

// Never cache (always fresh — SSR on every request)
const res = await fetch(url, { cache: "no-store" });
```

### Which to Use

| Strategy | When | Example |
|---|---|---|
| Default (cached) | Data rarely changes | About page content |
| `revalidate: 60` | Data changes occasionally | Trail details (new reviews) |
| `revalidate: 300` | Data changes infrequently | Featured trails list |
| `no-store` | Data must be real-time | User profile, live weather |

```tsx
// Trail detail: revalidate every 60 seconds
async function getTrail(slug: string) {
  const res = await fetch(`http://localhost:4000/api/trails/${slug}`, {
    next: { revalidate: 60 },
  });
  return res.json();
}

// Reviews: always fresh (users expect to see their review immediately)
async function getReviews(slug: string) {
  const res = await fetch(`http://localhost:4000/api/trails/${slug}/reviews`, {
    cache: "no-store",
  });
  return res.json();
}
```

---

## The Trail Listing Page (With Real Data)

```tsx
// src/app/trails/page.tsx
import Link from "next/link";
import type { Trail } from "@/types";

async function getTrails(): Promise<Trail[]> {
  const res = await fetch("http://localhost:4000/api/trails", {
    next: { revalidate: 300 }, // refresh every 5 minutes
  });
  return res.json();
}

export default async function TrailsPage() {
  const trails = await getTrails();

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-8">All Trails</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trails.map((trail) => (
          <Link
            key={trail.id}
            href={`/trails/${trail.slug}`}
            className="block bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden"
          >
            <img
              src={trail.image_url}
              alt={trail.name}
              className="h-48 w-full object-cover"
            />
            <div className="p-4">
              <h2 className="font-semibold">{trail.name}</h2>
              <p className="text-stone-500 text-sm mt-1">{trail.location}</p>
              <div className="flex justify-between mt-3 text-sm text-stone-600">
                <span>{trail.distance_km} km</span>
                <span className="text-amber-600">★ {trail.rating.toFixed(1)}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

This page fetches all trails on the server, renders them as HTML, and caches the result for 5 minutes. The first visitor triggers the fetch. Subsequent visitors get the cached HTML instantly — no server work, no API call.

---

## Error Handling

What if Owen's API is down?

```tsx
async function getTrail(slug: string): Promise<Trail | null> {
  try {
    const res = await fetch(`http://localhost:4000/api/trails/${slug}`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null; // network error, API down, etc.
  }
}
```

Or let it throw and catch with `error.tsx` (Chapter 5).

---

## The Types

```tsx
// src/types/index.ts
export interface Trail {
  id: string;
  slug: string;
  name: string;
  location: string;
  difficulty: "easy" | "moderate" | "hard" | "expert";
  distance_km: number;
  elevation_m: number;
  rating: number;
  review_count: number;
  image_url: string;
  description: string;
}

export interface Review {
  id: string;
  trail_id: string;
  user_id: string;
  user_name: string;
  rating: number;
  text: string;
  photos: string[];
  created_at: string;
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
async function Page()           │ Server Component (fetches on server)
await fetch(url)                │ Fetch data during render
{ next: { revalidate: N } }    │ Cache for N seconds, then refresh
{ cache: "no-store" }          │ Always fetch fresh (no cache)
Promise.all([...])              │ Parallel fetches (avoid waterfall)
notFound()                      │ Trigger 404 if data missing
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The pages work but look plain. Mika sends a Figma link: "Cards with gradients, responsive grid, dark mode, custom fonts. Make it beautiful."

---

[← Chapter 2: Dynamic Routes](chapter-02-dynamic-routes.md) | [Chapter 4: Styling →](chapter-04-styling.md)
