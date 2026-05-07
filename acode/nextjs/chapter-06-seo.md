# Chapter 6: SEO & Metadata — Making Google Happy

[← Chapter 5: Navigation](chapter-05-navigation.md) | [Chapter 7: Client Components →](chapter-07-client-components.md)

---

## The Task

Priya: "When someone Googles 'Mount Rainier hiking trail,' we should be the first result. When they share a trail on Twitter, I want a big image card with the trail name and rating. Fix it."

---

## generateMetadata: Dynamic Per-Page SEO

```tsx
// src/app/trails/[slug]/page.tsx
import type { Metadata } from "next";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const trail = await getTrail(slug);

  if (!trail) return { title: "Trail Not Found" };

  return {
    title: trail.name,
    description: `${trail.name} is a ${trail.distance_km}km ${trail.difficulty} trail near ${trail.location}. Rated ${trail.rating}/5 by ${trail.review_count} hikers.`,
    openGraph: {
      title: `${trail.name} — TrailBlazer`,
      description: trail.description.slice(0, 160),
      images: [{ url: trail.image_url, width: 1200, height: 630, alt: trail.name }],
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title: trail.name,
      description: `${trail.distance_km}km · ${trail.difficulty} · ★ ${trail.rating.toFixed(1)}`,
      images: [trail.image_url],
    },
  };
}
```

The HTML sent to the browser includes:

```html
<head>
  <title>Mount Rainier | TrailBlazer</title>
  <meta name="description" content="Mount Rainier is a 14km hard trail near..." />
  <meta property="og:title" content="Mount Rainier — TrailBlazer" />
  <meta property="og:image" content="https://..." />
  <meta name="twitter:card" content="summary_large_image" />
</head>
```

No JavaScript required. Crawlers see it immediately.

---

## Static Metadata (Simple Pages)

```tsx
// src/app/about/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
  description: "Learn about TrailBlazer — a community-driven hiking platform.",
};
```

For pages without dynamic data, export a `metadata` constant. For pages with dynamic data (trail detail), export a `generateMetadata` function.

---

## Sitemap

```tsx
// src/app/sitemap.ts
import type { MetadataRoute } from "next";

export default async function sitemap(): MetadataRoute.Sitemap {
  const res = await fetch("http://localhost:4000/api/trails");
  const trails = await res.json();

  const trailUrls = trails.map((trail: { slug: string; updated_at: string }) => ({
    url: `https://trailblazer.com/trails/${trail.slug}`,
    lastModified: new Date(trail.updated_at),
    changeFrequency: "weekly" as const,
    priority: 0.8,
  }));

  return [
    { url: "https://trailblazer.com", lastModified: new Date(), priority: 1 },
    { url: "https://trailblazer.com/trails", lastModified: new Date(), priority: 0.9 },
    { url: "https://trailblazer.com/about", lastModified: new Date(), priority: 0.3 },
    ...trailUrls,
  ];
}
```

Generates `/sitemap.xml` automatically. Submit to Google Search Console.

---

## robots.txt

```tsx
// src/app/robots.ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin/", "/profile/"],
    },
    sitemap: "https://trailblazer.com/sitemap.xml",
  };
}
```

---

## Structured Data (JSON-LD)

Rich snippets in Google (star ratings, breadcrumbs):

```tsx
// src/app/trails/[slug]/page.tsx
export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);
  if (!trail) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Place",
    name: trail.name,
    description: trail.description,
    image: trail.image_url,
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: trail.rating,
      reviewCount: trail.review_count,
      bestRating: 5,
    },
    geo: { "@type": "GeoCoordinates" },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {/* page content */}
    </>
  );
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Feature                         │ How
────────────────────────────────┼──────────────────────────────────────
Static metadata                 │ export const metadata: Metadata = {}
Dynamic metadata                │ export async function generateMetadata()
Title template                  │ title: { template: "%s | Site" }
Open Graph                      │ metadata.openGraph = { ... }
Twitter cards                   │ metadata.twitter = { ... }
Sitemap                         │ src/app/sitemap.ts
robots.txt                      │ src/app/robots.ts
JSON-LD                         │ <script type="application/ld+json">
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The trail page needs a "Save Trail" button, a star rating widget, and a search bar with live results. These need state, event handlers, and browser APIs. Server Components can't do that.

Time to learn the client/server boundary.

---

[← Chapter 5: Navigation](chapter-05-navigation.md) | [Chapter 7: Client Components →](chapter-07-client-components.md)
