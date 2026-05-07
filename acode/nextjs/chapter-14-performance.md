# Chapter 14: Performance & Core Web Vitals

[← Chapter 13: API Routes](chapter-13-api-routes.md) | [Chapter 15: Deployment →](chapter-15-deployment.md)

---

## The Task

Raj: "Lighthouse audit. I want 95+. Find what's slow, fix it, prove it."

---

## Bundle Analysis

```bash
npm install -D @next/bundle-analyzer
```

```ts
// next.config.ts
import type { NextConfig } from "next";
import bundleAnalyzer from "@next/bundle-analyzer";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const nextConfig: NextConfig = {};

export default withBundleAnalyzer(nextConfig);
```

```bash
ANALYZE=true npm run build
```

Opens a visual treemap showing every module's size. Find the heavy ones. Kill them.

### Common Offenders

| Library | Size | Fix |
|---|---|---|
| moment.js | 300KB | Replace with `date-fns` (tree-shakeable) |
| lodash | 70KB | Import specific: `import debounce from "lodash/debounce"` |
| Large icon libraries | 200KB+ | Import individual icons |
| Unused dependencies | Varies | Remove from package.json |

---

## Dynamic Imports: Load Only When Needed

```tsx
import dynamic from "next/dynamic";

// Heavy component — only load when visible
const Map = dynamic(() => import("@/components/Map"), {
  loading: () => <div className="h-64 bg-stone-200 animate-pulse rounded-lg" />,
  ssr: false, // don't render on server (needs browser APIs)
});

// Heavy library — only load on interaction
const ReviewEditor = dynamic(() => import("@/components/ReviewEditor"), {
  loading: () => <p>Loading editor...</p>,
});
```

`ssr: false` — for components that use browser-only APIs (window, document, canvas). They render only in the browser.

---

## Server Components = Zero Client JS

The biggest performance win in Next.js: Server Components ship NO JavaScript to the browser.

```tsx
// This component adds 0 bytes to the client bundle
export default async function TrailStats({ slug }: { slug: string }) {
  const stats = await getTrailStats(slug);

  return (
    <div className="grid grid-cols-4 gap-4">
      <Stat label="Distance" value={`${stats.distance_km} km`} />
      <Stat label="Elevation" value={`${stats.elevation_m} m`} />
      <Stat label="Rating" value={`★ ${stats.rating}`} />
      <Stat label="Reviews" value={stats.review_count.toString()} />
    </div>
  );
}
```

Only add `"use client"` when you absolutely need interactivity. Every Client Component adds to the bundle.

---

## Optimizing Core Web Vitals

### LCP (Largest Contentful Paint)

The biggest visible element (usually the hero image). Make it load fast:

```tsx
// ✅ Priority loading for hero image
<Image src={trail.image_url} alt={trail.name} fill priority />

// ✅ Preload critical resources
// In layout.tsx or page.tsx metadata:
export const metadata = {
  other: {
    "link": [{ rel: "preload", href: "/critical-font.woff2", as: "font" }],
  },
};
```

### CLS (Cumulative Layout Shift)

Things jumping around as the page loads:

```tsx
// ✅ Always set dimensions on images
<Image src={url} alt="" width={400} height={300} />

// ✅ Reserve space for dynamic content
<div className="min-h-[200px]">
  <Suspense fallback={<Skeleton />}>
    <DynamicContent />
  </Suspense>
</div>

// ✅ Use next/font (no FOUT)
import { Inter } from "next/font/google";
```

### TBT (Total Blocking Time)

JavaScript blocking the main thread:

```tsx
// ❌ Heavy computation on render
export function ExpensiveComponent() {
  const result = heavyCalculation(); // blocks for 200ms
  return <div>{result}</div>;
}

// ✅ Move to server (zero client cost)
export default async function ExpensiveComponent() {
  const result = await heavyCalculation(); // runs on server
  return <div>{result}</div>;
}

// ✅ Or defer with dynamic import
const Heavy = dynamic(() => import("./Heavy"), { ssr: false });
```

---

## Measuring Performance

### Next.js Built-in Analytics

```tsx
// src/app/layout.tsx
import { SpeedInsights } from "@vercel/speed-insights/next";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights /> {/* Real user metrics */}
      </body>
    </html>
  );
}
```

### Web Vitals Reporting

```tsx
// src/app/layout.tsx
import { WebVitals } from "@/components/WebVitals";

// src/components/WebVitals.tsx
"use client";
import { useReportWebVitals } from "next/web-vitals";

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Send to your analytics
    console.log(metric.name, metric.value);
  });
  return null;
}
```

---

## Performance Checklist

```
✅ Server Components for static content (0 JS)
✅ next/image for all images (auto-optimization)
✅ next/font for fonts (no CLS)
✅ Dynamic imports for heavy client components
✅ Suspense boundaries for slow data
✅ generateStaticParams for known pages
✅ revalidate for ISR (reduce server load)
✅ Priority on LCP image
✅ No unnecessary "use client"
✅ Bundle analyzer to find bloat
```

---

## Results

| Metric | Before Optimization | After |
|---|---|---|
| LCP | 3.2s | 1.1s |
| CLS | 0.15 | 0.01 |
| TBT | 450ms | 80ms |
| First Load JS | 180KB | 87KB |
| **Lighthouse Score** | **68** | **97** |

Raj: "Ship it."

---

## What's Next

The app is fast, functional, and beautiful. Time to put it on the internet. Deploy to production.

---

[← Chapter 13: API Routes](chapter-13-api-routes.md) | [Chapter 15: Deployment →](chapter-15-deployment.md)
