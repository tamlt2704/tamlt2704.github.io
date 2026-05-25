# Chapter 11: Performance — The 95+ Lighthouse Score

[← Chapter 10: Layout & Mobile](chapter-10-layout-mobile.md)

---

## Why It Matters

Your reader is on a train. 3G connection. They tap a link to your binary search chapter. If it takes more than 3 seconds, they're gone. Back to Twitter. Your carefully written explanation — never read.

Performance isn't optimization for optimization's sake. It's *respect for the reader's time and bandwidth*.

The good news: static sites are inherently fast. But you can still mess it up with bloated bundles, unoptimized fonts, and render-blocking resources.

## Measure First

Run Lighthouse on your deployed site:

```bash
npx lighthouse https://yourusername.github.io/blog/algorithms/chapter-01-linear-search --view
```

Or use Chrome DevTools → Lighthouse tab. Check Performance, Accessibility, Best Practices, SEO.

Your baseline with our setup should already be 85+. Let's push it to 95+.

## The Bundle: What's Actually Shipping

Analyze your bundle:

```bash
npm install @next/bundle-analyzer
```

Update `next.config.ts`:

```typescript
import type { NextConfig } from "next";
import withBundleAnalyzer from "@next/bundle-analyzer";

const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
};

export default process.env.ANALYZE === "true"
  ? withBundleAnalyzer({ enabled: true })(nextConfig)
  : nextConfig;
```

Run:

```bash
ANALYZE=true npm run build
```

A treemap opens showing every module and its size. The usual suspects:

| Module | Size | Fix |
|--------|------|-----|
| `react-syntax-highlighter` | ~200KB | Only import languages you use |
| `pyodide` | 5MB+ | Already lazy-loaded (Chapter 5) |
| `framer-motion` | ~80KB | Use CSS animations instead |
| Unused Tailwind | varies | Purged automatically in production |

## Fix 1: Slim Down Syntax Highlighting

Instead of importing all 200+ languages:

```tsx
// BAD — imports everything
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
```

Import only what you need:

```tsx
// GOOD — tree-shakeable
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter";
import python from "react-syntax-highlighter/dist/esm/languages/prism/python";
import javascript from "react-syntax-highlighter/dist/esm/languages/prism/javascript";
import typescript from "react-syntax-highlighter/dist/esm/languages/prism/typescript";
import bash from "react-syntax-highlighter/dist/esm/languages/prism/bash";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

SyntaxHighlighter.registerLanguage("python", python);
SyntaxHighlighter.registerLanguage("javascript", javascript);
SyntaxHighlighter.registerLanguage("typescript", typescript);
SyntaxHighlighter.registerLanguage("bash", bash);
```

Savings: ~150KB. That's 1-2 seconds on 3G.

## Fix 2: Font Loading Strategy

System fonts load instantly. Custom fonts block rendering. Choose wisely:

```css
/* globals.css — use system font stack */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

code, pre {
  font-family: "SF Mono", "Fira Code", "Fira Mono", Menlo, Consolas, monospace;
}
```

If you *must* use a custom font (like Inter), use `next/font`:

```tsx
// app/layout.tsx
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",        // Show fallback immediately, swap when loaded
  preload: true,
});

<body className={inter.className}>
```

`display: "swap"` prevents invisible text while the font loads. The reader sees content immediately in a fallback font, then it swaps seamlessly.

## Fix 3: Image Optimization (Without Next.js Image)

Since we're static (`images: { unoptimized: true }`), Next.js won't optimize images. Do it yourself:

```bash
# Convert PNGs to WebP (60-80% smaller)
npx sharp-cli --input "public/**/*.png" --output "{dir}/{name}.webp" --format webp --quality 80
```

Use `<picture>` for fallback:

```tsx
export function OptimizedImage({ src, alt }: { src: string; alt: string }) {
  const webp = src.replace(/\.(png|jpg)$/, ".webp");
  return (
    <picture>
      <source srcSet={webp} type="image/webp" />
      <img
        src={src}
        alt={alt}
        loading="lazy"
        decoding="async"
        className="rounded-lg w-full"
      />
    </picture>
  );
}
```

- `loading="lazy"` — only loads when near viewport
- `decoding="async"` — doesn't block main thread
- WebP first, PNG fallback for old browsers

## Fix 4: Preload Critical Resources

In `app/layout.tsx`:

```tsx
<head>
  <ThemeScript />
  <link rel="preconnect" href="https://cdn.jsdelivr.net" />  {/* Pyodide CDN */}
  <link rel="dns-prefetch" href="https://cdn.jsdelivr.net" />
</head>
```

`preconnect` establishes the connection early. When the reader clicks "Run" on a Python playground, the Pyodide download starts faster.

## Fix 5: Route Prefetching

Next.js prefetches linked pages automatically with `<Link>`. But for the prev/next navigation, ensure you're using Next.js `Link`:

```tsx
import Link from "next/link";

// This prefetches on hover/viewport
<Link href={`/blog/${series}/${next}`}>Next →</Link>

// NOT this (no prefetch)
<a href={`/blog/${series}/${next}`}>Next →</a>
```

When the reader finishes reading, the next chapter is already cached. Click → instant.

## Fix 6: CSS Performance

Tailwind purges unused CSS in production automatically. But watch for:

```tsx
// BAD — dynamic classes can't be purged
<div className={`text-${color}-500`}>  // Tailwind can't detect this

// GOOD — full class names
<div className={color === "red" ? "text-red-500" : "text-blue-500"}>
```

Always use complete class strings. Tailwind's purge scans for full matches.

## Fix 7: Third-Party Scripts

If you add analytics (Plausible, Umami — privacy-friendly alternatives to Google Analytics):

```tsx
// Load after page is interactive
<script
  defer
  data-domain="yourusername.github.io"
  src="https://plausible.io/js/script.js"
/>
```

`defer` = loads in parallel, executes after HTML parsing. Never blocks rendering.

**Never** use Google Analytics on a performance-focused site. It adds 45KB+ and tracks your readers. Use Plausible (~1KB) or nothing.

## The Performance Checklist

Run through this before every deploy:

- [ ] Bundle size < 200KB first load (check with `next build` output)
- [ ] No layout shift (CLS < 0.1) — set explicit dimensions on images/embeds
- [ ] Largest Contentful Paint < 1.5s — text should paint immediately
- [ ] No render-blocking resources — fonts use `display: swap`, scripts use `defer`
- [ ] Code blocks use `PrismLight` with only needed languages
- [ ] Images are WebP with `loading="lazy"`
- [ ] Interactive components are lazy-loaded (`React.lazy`)

## Real Numbers

With all optimizations applied, a typical chapter page:

| Metric | Value | Rating |
|--------|-------|--------|
| First Contentful Paint | 0.4s | 🟢 |
| Largest Contentful Paint | 0.8s | 🟢 |
| Total Blocking Time | 10ms | 🟢 |
| Cumulative Layout Shift | 0.01 | 🟢 |
| Total JS (first load) | ~120KB | 🟢 |
| Lighthouse Performance | 98 | 🟢 |

Static HTML from a CDN + minimal JavaScript + lazy-loaded interactivity = fast everywhere.

## The Performance Mental Model

```
Static HTML (instant)
  + Tailwind CSS (tiny, purged)
  + Minimal JS (React hydration)
  + Lazy components (on demand)
  = Fast on any connection
```

Your reader on a train with 3G? They see the article text in under a second. The interactive components load when they scroll to them. The next chapter prefetches while they read.

That's performance. Not a number on a dashboard — a reader who stays.

---

## Series Complete

You've built a full interactive learning platform:

| Chapter | What You Built |
|---------|---------------|
| 1 | Live site on GitHub Pages |
| 2 | Markdown → pages pipeline |
| 3 | Syntax highlighting |
| 4 | Quiz component |
| 5 | Code playground (JS + Python) |
| 6 | Step visualizer |
| 7 | Navigation + SEO |
| 8 | Dark/light theme |
| 9 | Progressive loading |
| 10 | Responsive layout + mobile |
| 11 | Performance optimization |

**Cost:** $0/month.
**Content format:** Plain markdown + component tags.
**Deploy:** `git push`.
**Lighthouse:** 95+.

Write. Push. Teach. That's the whole workflow.
