# Chapter 8: Server Actions & Forms

[← Chapter 7: Client Components](chapter-07-client-components.md) | [Chapter 9: Authentication →](chapter-09-auth.md)

---

## The Task

Owen: "The review API is ready. POST to `/api/trails/:slug/reviews` with a JSON body. Auth token in the cookie. Go."

You need a form that: validates input, sends data to the server, shows errors, and refreshes the page with the new review. Server Actions handle all of this.

---

## Server Actions: Functions That Run on the Server

```tsx
// src/app/trails/[slug]/review/actions.ts
"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export async function submitReview(slug: string, formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  if (!token) redirect("/login");

  const rating = Number(formData.get("rating"));
  const text = formData.get("text") as string;

  // Server-side validation
  if (!rating || rating < 1 || rating > 5) {
    return { error: "Please select a rating (1-5)" };
  }
  if (!text || text.trim().length < 10) {
    return { error: "Review must be at least 10 characters" };
  }

  // Call Owen's API (server-to-server, token is safe)
  const res = await fetch(`http://localhost:4000/api/trails/${slug}/reviews`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ rating, text: text.trim() }),
  });

  if (!res.ok) {
    const body = await res.text();
    return { error: body || "Failed to submit review" };
  }

  // Bust the cache so the trail page shows the new review
  revalidatePath(`/trails/${slug}`);
  redirect(`/trails/${slug}`);
}
```

### What's Happening

1. `"use server"` — marks this file as server-only. These functions never ship to the browser.
2. `cookies()` — reads the auth token from the HTTP cookie (server-side only).
3. Validation runs on the server — can't be bypassed by the client.
4. `revalidatePath()` — tells Next.js to re-fetch the trail page data (so the new review appears).
5. `redirect()` — sends the user back to the trail page.

---

## The Form (Client Component)

```tsx
// src/app/trails/[slug]/review/ReviewForm.tsx
"use client";

import { useActionState } from "react";
import { submitReview } from "./actions";
import { StarRating } from "@/components/StarRating";
import { useState } from "react";

export function ReviewForm({ slug }: { slug: string }) {
  const [rating, setRating] = useState(0);
  const submitWithSlug = submitReview.bind(null, slug);
  const [state, formAction, isPending] = useActionState(submitWithSlug, null);

  return (
    <form action={formAction} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-stone-700 mb-2">
          Rating
        </label>
        <StarRating value={rating} onChange={setRating} />
        <input type="hidden" name="rating" value={rating} />
      </div>

      <div>
        <label className="block text-sm font-medium text-stone-700 mb-2">
          Your Review
        </label>
        <textarea
          name="text"
          rows={5}
          required
          minLength={10}
          placeholder="How was the trail? What should others know?"
          className="w-full px-4 py-3 rounded-lg border border-stone-300
                     focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
        />
      </div>

      {state?.error && (
        <p className="text-red-600 text-sm font-medium">{state.error}</p>
      )}

      <button
        type="submit"
        disabled={isPending || rating === 0}
        className="w-full bg-emerald-600 text-white py-3 rounded-lg font-medium
                   hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
      >
        {isPending ? "Submitting..." : "Submit Review"}
      </button>
    </form>
  );
}
```

### How It Works

```
1. User fills form, clicks Submit
2. FormData sent to server (like a traditional form POST)
3. Server Action runs: validates, calls API, revalidates cache
4. Returns error state OR redirects to trail page
5. If error: form re-renders with error message, input preserved
6. If success: user sees trail page with their new review
```

---

## The Review Page

```tsx
// src/app/trails/[slug]/review/page.tsx
import { ReviewForm } from "./ReviewForm";
import type { Metadata } from "next";

interface Props {
  params: Promise<{ slug: string }>;
}

export const metadata: Metadata = {
  title: "Write a Review",
};

export default async function WriteReviewPage({ params }: Props) {
  const { slug } = await params;

  return (
    <div className="max-w-lg mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold mb-8">Write a Review</h1>
      <ReviewForm slug={slug} />
    </div>
  );
}
```

---

## Progressive Enhancement

Server Actions work without JavaScript. If JS fails to load (slow connection, disabled, error), the form still submits as a regular HTML form POST. The page reloads with the result.

This is impossible with client-only forms (fetch + useState). It's a real advantage for accessibility and reliability.

---

## Other Server Action Patterns

### Inline Actions (Simple Cases)

```tsx
// src/app/trails/[slug]/page.tsx
import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";

export default async function TrailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);

  async function saveTrail() {
    "use server";
    const token = (await cookies()).get("token")?.value;
    await fetch(`http://localhost:4000/api/trails/${slug}/save`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    revalidatePath(`/trails/${slug}`);
  }

  return (
    <div>
      <h1>{trail.name}</h1>
      <form action={saveTrail}>
        <button type="submit">Save Trail</button>
      </form>
    </div>
  );
}
```

### Optimistic Updates

```tsx
"use client";
import { useOptimistic } from "react";

export function LikeButton({ likes, trailId }: { likes: number; trailId: string }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (current) => current + 1
  );

  async function handleLike() {
    addOptimisticLike(null); // show +1 immediately
    await likeTrail(trailId); // server action (may take time)
  }

  return (
    <form action={handleLike}>
      <button type="submit">♥ {optimisticLikes}</button>
    </form>
  );
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
"use server" (file)             │ All exports are server actions
"use server" (inline)           │ Single function is a server action
useActionState(action, init)    │ Track pending/error state
revalidatePath(path)            │ Bust cache for a specific page
revalidateTag(tag)              │ Bust cache for tagged fetches
redirect(url)                   │ Server-side redirect after action
cookies()                       │ Read/write HTTP cookies
Progressive enhancement         │ Forms work without JavaScript
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The review form requires authentication. But right now, anyone can access `/trails/mount-rainier/review`. Owen's API rejects unauthenticated requests, but the user sees a confusing error instead of a login page.

Time to add auth: login, sessions, and route protection.

---

[← Chapter 7: Client Components](chapter-07-client-components.md) | [Chapter 9: Authentication →](chapter-09-auth.md)
