# Chapter 17: View Counts That Work

[← Chapter 16: Supabase Setup](/blog/nextjs-ghpages/chapter-16-supabase-setup) | [Chapter 18: Auth & User Progress →](/blog/nextjs-ghpages/chapter-18-auth-progress)

---

## The Goal

Every chapter page shows "X views" — a small social proof that tells readers "other people found this useful." It increments on each visit and displays the count.

## The Component

Create `app/blog/components/ViewCount.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

interface Props {
  slug: string;
}

export function ViewCount({ slug }: Props) {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    // Increment and get the new count
    supabase.rpc("increment_view", { page_slug: slug }).then(({ data, error }) => {
      if (!error && data !== null) {
        setCount(data);
      }
    });
  }, [slug]);

  if (count === null) return null;

  return (
    <span className="text-sm text-gray-400 dark:text-gray-500">
      {count.toLocaleString()} {count === 1 ? "view" : "views"}
    </span>
  );
}
```

Simple: on mount, call the Supabase function, display the result.

## Add It to the Blog Page

In `app/blog/[...slug]/page.tsx`, add below the breadcrumb:

```tsx
import { ViewCount } from "@/app/blog/components/ViewCount";

// Inside the return, after breadcrumb:
<div className="mb-6 flex items-center gap-3 text-sm text-gray-500">
  <span>
    {seriesTitle} / {fileSlug}
  </span>
  <span>·</span>
  <ViewCount slug={`${series}/${fileSlug}`} />
</div>;
```

## Preventing Double-Counts

The current version increments on every page load — including refreshes. For more accurate counts, deduplicate by session:

```tsx
export function ViewCount({ slug }: Props) {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    // Only count once per session per page
    const key = `viewed:${slug}`;
    const alreadyViewed = sessionStorage.getItem(key);

    if (alreadyViewed) {
      // Just read the count without incrementing
      supabase
        .from("page_views")
        .select("count")
        .eq("slug", slug)
        .single()
        .then(({ data }) => {
          if (data) setCount(data.count);
        });
    } else {
      // First visit this session — increment
      supabase.rpc("increment_view", { page_slug: slug }).then(({ data, error }) => {
        if (!error && data !== null) {
          setCount(data);
          sessionStorage.setItem(key, "1");
        }
      });
    }
  }, [slug]);

  if (count === null) return null;

  return (
    <span className="text-sm text-gray-400 dark:text-gray-500">{count.toLocaleString()} views</span>
  );
}
```

`sessionStorage` resets when the browser tab closes. Same reader, same session = one count. New session = new count. Good enough for a blog.

## Popular Posts Widget

Show the most-read chapters on your blog index:

```tsx
// app/blog/components/PopularPosts.tsx
"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import Link from "next/link";

interface PageView {
  slug: string;
  count: number;
}

export function PopularPosts() {
  const [posts, setPosts] = useState<PageView[]>([]);

  useEffect(() => {
    supabase
      .from("page_views")
      .select("slug, count")
      .order("count", { ascending: false })
      .limit(5)
      .then(({ data }) => {
        if (data) setPosts(data);
      });
  }, []);

  if (posts.length === 0) return null;

  return (
    <aside className="mt-12">
      <h3 className="mb-3 text-sm font-semibold text-gray-500 uppercase">Most Read</h3>
      <ul className="space-y-2">
        {posts.map((post) => (
          <li key={post.slug}>
            <Link
              href={`/blog/${post.slug}`}
              className="text-sm text-gray-700 hover:text-teal-600 dark:text-gray-300"
            >
              {post.slug.split("/").pop()?.replace(/-/g, " ")}
            </Link>
            <span className="ml-2 text-xs text-gray-400">{post.count.toLocaleString()} views</span>
          </li>
        ))}
      </ul>
    </aside>
  );
}
```

## Real-Time View Count (Optional)

Want the count to update live when other readers are on the same page?

```tsx
useEffect(() => {
  // Subscribe to changes on this row
  const channel = supabase
    .channel(`views:${slug}`)
    .on(
      "postgres_changes",
      {
        event: "UPDATE",
        schema: "public",
        table: "page_views",
        filter: `slug=eq.${slug}`,
      },
      (payload) => {
        setCount(payload.new.count);
      },
    )
    .subscribe();

  return () => {
    supabase.removeChannel(channel);
  };
}, [slug]);
```

Now if two people are reading the same chapter, they both see the count tick up. A subtle "you're not alone" signal.

## Dashboard: Your Most Popular Content

Query your data anytime in the Supabase SQL editor:

```sql
-- Top 10 most viewed pages
select slug, count, last_viewed_at
from page_views
order by count desc
limit 10;

-- Total views across all pages
select sum(count) as total_views from page_views;

-- Views in the last 7 days (requires tracking timestamps per view)
select slug, count
from page_views
where last_viewed_at > now() - interval '7 days'
order by count desc;
```

---

## What's Next

View counts are anonymous. Chapter 18 adds authentication — readers can log in with GitHub, and you can save their quiz scores, reading progress, and preferences.
