# Chapter 14: Performance & Production — Shipping Fast CSS

[← Chapter 13: Plugins](chapter-13-plugins.md) | [Chapter 15: Full Build →](chapter-15-full-build.md)

---

## The Task

Kai: "The CSS file in development is huge. Are we shipping all of that to users?"

You: "No. Tailwind only ships what you use. Let me show you how."

---

## How Tailwind v4 Works

Tailwind v4 scans your source files for class names and generates only the CSS for classes it finds. No configuration needed — it auto-detects your content files.

```
Source files (scanned):          Generated CSS (shipped):
─────────────────────            ─────────────────────────
"bg-white"          →            .bg-white { background: #fff }
"p-6"               →            .p-6 { padding: 1.5rem }
"text-gray-900"     →            .text-gray-900 { color: #111827 }
"hover:bg-gray-50"  →            .hover\:bg-gray-50:hover { ... }

"bg-purple-300"     →            (not generated — never used)
"m-[47px]"          →            (not generated — never used)
```

Result: your production CSS only contains styles you actually use. Typical bundle: **5-15 KB** gzipped.

---

## Content Detection

Tailwind v4 automatically scans:
- All files in your project (excluding `node_modules`, `.git`, etc.)
- Looks for patterns that match utility class names

If you need to explicitly include or exclude paths:

```css
@import "tailwindcss";

/* Include additional sources */
@source "../shared-components/src";

/* Exclude paths */
@source not "./src/legacy";
```

---

## Common Mistakes That Break Tree-Shaking

### Dynamic class construction

```tsx
// ❌ Tailwind can't find these — they won't be in the CSS
const size = "lg";
<div className={`text-${size}`} />

// ✓ Use complete strings
const sizes = { sm: "text-sm", md: "text-base", lg: "text-lg" };
<div className={sizes[size]} />
```

### Classes in variables that aren't scanned

```tsx
// ❌ If this file isn't scanned, classes are missing
// config/theme.json
{ "primary": "bg-blue-500 text-white" }

// ✓ Keep class strings in source files Tailwind scans
// src/theme.ts
export const primary = "bg-blue-500 text-white";
```

### Safelist (force-include classes)

If you genuinely need dynamic classes (e.g., from a CMS), safelist them:

```css
@import "tailwindcss";

/* Force these classes to always be generated */
@utility safelist {
  /* This is a no-op but ensures the scanner sees these classes */
}
```

Or use the source directive to include the file containing the class names.

---

## Measuring Bundle Size

```bash
# Build for production
npm run build

# Check the CSS output size
ls -la dist/assets/*.css

# With gzip size
gzip -c dist/assets/index-*.css | wc -c
```

Typical results for a full dashboard app:

```
────────────────────────────────────────────────
 Metric              │ Value
────────────────────────────────────────────────
 Raw CSS             │ 25-50 KB
 Gzipped             │ 5-12 KB
 Brotli              │ 4-8 KB
────────────────────────────────────────────────
```

Compare to Bootstrap (~25 KB gzipped) or a hand-written CSS file that grows forever.

---

## Production Optimizations

### 1. Minification (automatic)

Vite/PostCSS minifies CSS in production builds automatically. No config needed.

### 2. Remove unused CSS variables

If you defined many theme values but only use a few:

```css
@theme {
  /* Only define what you actually use */
  --color-brand-500: #6366f1;
  --color-brand-600: #4f46e5;
  --color-brand-700: #4338ca;
  /* Don't define brand-50 through brand-400 if you never use them */
}
```

### 3. Avoid @apply in hot paths

`@apply` duplicates CSS. If you `@apply` the same 10 utilities in 5 places, that's 50 declarations instead of 10 shared utility classes.

```css
/* ❌ Duplicates CSS for every element matching .card */
.card {
  @apply bg-white rounded-lg p-6 border border-gray-200 shadow-sm;
}

/* ✓ Use utility classes directly — they're shared across all elements */
<div class="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
```

### 4. Lazy-load heavy pages

If a page uses many unique utilities (like a complex chart page), code-split it:

```tsx
// Only loads the CSS for this page when navigated to
const AnalyticsPage = lazy(() => import('./pages/Analytics'));
```

---

## Performance Checklist

```
────────────────────────────────────────────────────────────
 ✓ │ Check
────────────────────────────────────────────────────────────
 □ │ No dynamic class construction (use complete strings)
 □ │ No unused @theme values (only define what you use)
 □ │ Minimal @apply usage (prefer utility classes)
 □ │ CSS is minified in production (Vite does this)
 □ │ Fonts are preloaded (prevent layout shift)
 □ │ Critical CSS is inlined (framework handles this)
 □ │ Images use proper sizing (w-full + aspect ratio)
 □ │ Animations respect prefers-reduced-motion
────────────────────────────────────────────────────────────
```

---

## Font Loading Performance

Fonts can cause layout shift. Optimize:

```html
<!-- Preload critical fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
```

Use `font-display: swap` (Google Fonts does this by default) so text is visible immediately with a fallback font.

In Tailwind, match your fallback to prevent layout shift:

```css
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
}
```

---

## Image Performance with Tailwind

```html
<!-- Responsive images with proper aspect ratio -->
<img
  src="chart.png"
  alt="Revenue chart"
  class="w-full h-auto aspect-video rounded-lg"
  loading="lazy"
  decoding="async"
/>

<!-- Skeleton while loading -->
<div class="w-full aspect-video bg-gray-200 dark:bg-gray-800 animate-pulse rounded-lg" />
```

Key utilities:
- `aspect-video` → 16:9 aspect ratio (prevents layout shift)
- `aspect-square` → 1:1
- `object-cover` → image fills container without distortion
- `object-contain` → image fits within container

---

## Dev vs Production Comparison

```
────────────────────────────────────────────────────────────
 Metric              │ Development      │ Production
────────────────────────────────────────────────────────────
 CSS generation      │ On-demand (JIT)  │ Pre-built, minified
 File size           │ Large (all used) │ Small (minified)
 Source maps         │ Yes              │ No (or separate)
 Hot reload          │ Yes (instant)    │ N/A
 Browser caching     │ No               │ Yes (hashed filenames)
────────────────────────────────────────────────────────────
```

---

## Debugging Production CSS

If a class isn't working in production:

1. **Check the class is a complete string** in your source (not constructed dynamically)
2. **Check the file is being scanned** (is it in a directory Tailwind watches?)
3. **Check for typos** — `bg-grey-500` doesn't exist (it's `gray`)
4. **Check specificity** — is something else overriding it? (Use browser DevTools)
5. **Check the build** — is the CSS actually being generated? (Inspect the output file)

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concern                         │ Solution
────────────────────────────────┼──────────────────────────────────────
CSS too large                   │ It's not — check gzipped size
Class not working in prod       │ Ensure it's a complete static string
Need to include extra files     │ @source "../path"
Need to exclude files           │ @source not "./path"
Force-include a class           │ Safelist or ensure it's in a scanned file
Reduce @apply duplication       │ Use utility classes directly
Font layout shift               │ Preload + font-display: swap
Image layout shift              │ aspect-{ratio} + w-full
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "Everything is optimized. Now let's put it all together. Build the complete dashboard page — header, sidebar, cards, chart, table, dark mode, responsive, animated. The final boss."

The full build — combining everything into a production dashboard.

---

[← Chapter 13: Plugins](chapter-13-plugins.md) | [Chapter 15: Full Build →](chapter-15-full-build.md)
