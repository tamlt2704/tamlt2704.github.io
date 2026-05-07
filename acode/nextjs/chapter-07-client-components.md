# Chapter 7: Client Components — "use client"

[← Chapter 6: SEO](chapter-06-seo.md) | [Chapter 8: Server Actions & Forms →](chapter-08-server-actions.md)

---

## The Problem

You try to add a "Save Trail" button:

```tsx
// src/app/trails/[slug]/page.tsx
export default async function TrailDetailPage({ params }: Props) {
  const trail = await getTrail((await params).slug);

  const [saved, setSaved] = useState(false); // ❌ ERROR
  // "You're importing a component that needs useState. It only works in a Client Component"

  return <button onClick={() => setSaved(true)}>Save</button>; // ❌ ERROR
}
```

Server Components can't use hooks or event handlers. They run on the server — there's no browser to click buttons in.

---

## The Rule

| Server Component (default) | Client Component ("use client") |
|---|---|
| Runs on the server | Runs in the browser |
| Can `await` data | Can use hooks (useState, useEffect) |
| Can access secrets/env vars | Can handle events (onClick, onChange) |
| Ships 0 JS to browser | Ships JS to browser |
| Can't use hooks | Can't be async |
| Can't handle events | Can't access server-only resources |

---

## The Fix: Extract Interactive Parts

Keep the page as a Server Component (for data fetching + SEO). Extract interactive pieces into Client Components.

```tsx
// src/components/SaveButton.tsx
"use client";

import { useState } from "react";

export function SaveButton({ trailId }: { trailId: string }) {
  const [saved, setSaved] = useState(false);

  return (
    <button
      onClick={() => setSaved(!saved)}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        saved
          ? "bg-emerald-100 text-emerald-800"
          : "bg-stone-100 text-stone-700 hover:bg-stone-200"
      }`}
    >
      {saved ? "♥ Saved" : "♡ Save Trail"}
    </button>
  );
}
```

```tsx
// src/app/trails/[slug]/page.tsx (Server Component — no "use client")
import { SaveButton } from "@/components/SaveButton";

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);
  if (!trail) notFound();

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{trail.name}</h1>
        <SaveButton trailId={trail.id} /> {/* Client Component inside Server Component */}
      </div>
      <p className="mt-4">{trail.description}</p>
    </div>
  );
}
```

The page fetches data on the server (fast, SEO-friendly). The button runs in the browser (interactive). Best of both worlds.

---

## The Boundary

```
Server Component (page.tsx)
├── <h1>{trail.name}</h1>          ← server-rendered HTML, 0 JS
├── <p>{trail.description}</p>     ← server-rendered HTML, 0 JS
├── <SaveButton />                 ← "use client" — ships JS
└── <StarRating />                 ← "use client" — ships JS
```

Everything above the `"use client"` boundary is server-only. Everything below ships JavaScript. Push the boundary as low as possible — only the interactive leaf components should be client.

---

## Common Client Components

### Search Bar (Live Filtering)

```tsx
// src/components/SearchBar.tsx
"use client";

import { useState, useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function SearchBar() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  function handleSearch(term: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (term) params.set("q", term);
    else params.delete("q");

    startTransition(() => {
      router.push(`/trails?${params.toString()}`);
    });
  }

  return (
    <div className="relative">
      <input
        type="search"
        defaultValue={searchParams.get("q") ?? ""}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search trails..."
        className="w-full px-4 py-2 rounded-lg border border-stone-300 focus:ring-2 focus:ring-emerald-500"
      />
      {isPending && (
        <div className="absolute right-3 top-2.5 h-5 w-5 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
      )}
    </div>
  );
}
```

### Star Rating (Interactive Input)

```tsx
// src/components/StarRating.tsx
"use client";

import { useState } from "react";

export function StarRating({ value = 0, onChange }: { value?: number; onChange?: (n: number) => void }) {
  const [hover, setHover] = useState(0);

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(0)}
          onClick={() => onChange?.(star)}
          className={`text-2xl transition-colors ${
            star <= (hover || value) ? "text-amber-400" : "text-stone-300"
          }`}
        >
          ★
        </button>
      ))}
    </div>
  );
}
```

---

## Passing Server Data to Client Components

Server Components can pass data as props to Client Components:

```tsx
// Server Component
export default async function TrailPage({ params }: Props) {
  const trail = await getTrail((await params).slug);

  return (
    <div>
      <h1>{trail.name}</h1>
      {/* Pass server-fetched data to client component */}
      <WeatherWidget lat={trail.lat} lng={trail.lng} />
    </div>
  );
}
```

```tsx
// Client Component
"use client";
export function WeatherWidget({ lat, lng }: { lat: number; lng: number }) {
  const [weather, setWeather] = useState(null);
  useEffect(() => {
    fetch(`/api/weather?lat=${lat}&lng=${lng}`).then(r => r.json()).then(setWeather);
  }, [lat, lng]);
  // ...
}
```

The server fetches the trail (including coordinates). The client component uses those coordinates to fetch live weather. Server does the heavy lifting; client adds real-time interactivity.

---

## Rules of Thumb

1. **Default to Server Components** — only add "use client" when you need hooks or events
2. **Push the boundary down** — make the smallest possible component a Client Component
3. **Don't make the whole page "use client"** — you lose server rendering benefits
4. **Props cross the boundary** — server data flows down to client components via props
5. **Client Components can't import Server Components** — but Server Components can render Client Components

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Needs                           │ Use
────────────────────────────────┼──────────────────────────────────────
Data fetching, SEO, secrets     │ Server Component (default)
useState, useEffect             │ Client Component ("use client")
onClick, onChange, onSubmit     │ Client Component ("use client")
Browser APIs (localStorage)     │ Client Component ("use client")
Static content, no interactivity│ Server Component (default)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Mika: "Users need to submit reviews. A form with rating, text, and photo upload. Where does the form data go?"

Server Actions — functions that run on the server, called directly from forms.

---

[← Chapter 6: SEO](chapter-06-seo.md) | [Chapter 8: Server Actions & Forms →](chapter-08-server-actions.md)
