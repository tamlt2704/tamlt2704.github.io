# Chapter 10: Image Optimization — next/image

[← Chapter 9: Authentication](chapter-09-auth.md) | [Chapter 11: Static Generation & ISR →](chapter-11-static-isr.md)

---

## The Problem

Mika opens the trail listing on her phone (4G). The page takes 8 seconds to load. Each trail image is 4MB, displayed in a 400×300 container. Layout shifts everywhere as images pop in.

The Lighthouse score: 34.

---

## next/image: Automatic Optimization

```tsx
import Image from "next/image";

export function TrailCard({ trail }: { trail: Trail }) {
  return (
    <div className="relative h-48 w-full overflow-hidden rounded-t-xl">
      <Image
        src={trail.image_url}
        alt={trail.name}
        fill
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        className="object-cover"
      />
    </div>
  );
}
```

### What It Does Automatically

| Feature | Before (plain `<img>`) | After (next/image) |
|---|---|---|
| File size | 4MB JPEG | 80KB WebP |
| Format | Whatever was uploaded | WebP or AVIF (modern, smaller) |
| Dimensions | 4000×3000 (full size) | Exact size needed for viewport |
| Lazy loading | No (all load immediately) | Yes (only visible images load) |
| Layout shift | Yes (image pops in) | No (space reserved) |
| Responsive | No (one size) | Yes (srcset with multiple sizes) |

### The `sizes` Prop

Tells the browser how wide the image will be at different viewport widths:

```tsx
sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
//      mobile: full width    tablet: half width    desktop: third width
```

Next.js generates multiple image sizes and the browser picks the best one.

---

## Fixed Size Images

For images with known dimensions (avatars, icons):

```tsx
<Image
  src={user.avatar_url}
  alt={user.name}
  width={48}
  height={48}
  className="rounded-full"
/>
```

No `fill`. Explicit width/height. Next.js reserves exactly that space — zero layout shift.

---

## Priority: Above-the-Fold Images

```tsx
// Hero image — load immediately, don't lazy-load
<Image
  src={trail.image_url}
  alt={trail.name}
  fill
  priority  // ← disables lazy loading, preloads the image
  sizes="100vw"
  className="object-cover"
/>
```

Use `priority` for the largest image visible on initial page load (LCP image). Only one or two images per page should have this.

---

## Blur Placeholder

Show a blurred preview while the full image loads:

```tsx
<Image
  src={trail.image_url}
  alt={trail.name}
  fill
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,/9j/4AAQ..." // tiny base64 from API
  sizes="(max-width: 768px) 100vw, 50vw"
  className="object-cover"
/>
```

The user sees a blurred version instantly, then the sharp image fades in. No blank space. No jump.

For local images (in your project), Next.js generates the blur automatically:

```tsx
import heroImage from "@/assets/hero.jpg";

<Image src={heroImage} alt="Hero" placeholder="blur" />
// blur generated at build time — no blurDataURL needed
```

---

## Configuring External Image Domains

By default, next/image only optimizes local images. For external URLs (Owen's API, CDN):

```ts
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.trailblazer.com",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "4000",
      },
    ],
  },
};

export default nextConfig;
```

---

## The Trail Hero (Full Example)

```tsx
// src/app/trails/[slug]/page.tsx
import Image from "next/image";

export default async function TrailDetailPage({ params }: Props) {
  const { slug } = await params;
  const trail = await getTrail(slug);
  if (!trail) notFound();

  return (
    <div>
      {/* Hero image */}
      <div className="relative h-72 md:h-96 w-full -mt-4">
        <Image
          src={trail.image_url}
          alt={trail.name}
          fill
          priority
          sizes="100vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
        <div className="absolute bottom-6 left-6">
          <h1 className="text-3xl md:text-4xl font-bold text-white">{trail.name}</h1>
          <p className="text-white/80 mt-1">{trail.location}</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* ... */}
      </div>
    </div>
  );
}
```

---

## Results

| Metric | Before | After |
|---|---|---|
| Total image weight (listing page) | 48MB | 1.2MB |
| LCP | 6.2s | 1.1s |
| CLS | 0.35 | 0 |
| Lighthouse Performance | 34 | 94 |

Mika: "Finally."

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Prop                            │ What It Does
────────────────────────────────┼──────────────────────────────────────
fill                            │ Image fills parent container
width + height                  │ Fixed dimensions (no fill)
sizes                           │ Responsive size hints for browser
priority                        │ Preload (above-the-fold images)
placeholder="blur"              │ Show blur while loading
blurDataURL                     │ Custom blur image (base64)
quality={75}                    │ Compression quality (default 75)
────────────────────────────────┼──────────────────────────────────────
next.config images.remotePatterns│ Allow external image domains
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Raj: "We have 500 trails. The detail pages are server-rendered on every request. That's 500 API calls per second at peak. Can we pre-build them?"

Static generation. ISR. Build once, serve forever (until the data changes).

---

[← Chapter 9: Authentication](chapter-09-auth.md) | [Chapter 11: Static Generation & ISR →](chapter-11-static-isr.md)
