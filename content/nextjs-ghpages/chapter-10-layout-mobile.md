# Chapter 10: Layout & Mobile That Doesn't Suck

[← Chapter 9: Streaming on Static](/blog/nextjs-ghpages/chapter-09-streaming) | [Chapter 11: Performance →](/blog/nextjs-ghpages/chapter-11-performance)

---

## The Reality Check

You open your blog on your phone. The code block overflows. The sidebar crushes the content. The quiz buttons are too small to tap. The navbar takes up half the screen.

Desktop-first is a trap. 60% of web traffic is mobile. Your blog needs to work on a 375px screen as well as a 1440px monitor — and it needs to feel _native_ on both.

## The Layout System

Three zones. One layout. Responsive by default.

```
Desktop (≥1024px):
┌──────────┬────────────────────────┬──────────┐
│ Sidebar  │      Content           │  TOC     │
│ (chapters)│  (max-w-3xl, prose)   │ (sticky) │
└──────────┴────────────────────────┴──────────┘

Tablet (768–1023px):
┌────────────────────────────────────┐
│         Content (full width)       │
│         + hamburger for sidebar    │
└────────────────────────────────────┘

Mobile (<768px):
┌────────────────────────────────────┐
│  Sticky navbar (compact)           │
├────────────────────────────────────┤
│  Content (full bleed, small pad)   │
│  Code blocks scroll horizontally   │
└────────────────────────────────────┘
```

## The Root Layout

`app/layout.tsx`:

```tsx
import { ThemeScript } from "./theme-script";
import { ThemeToggle } from "./components/ThemeToggle";
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="min-h-screen bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100">
        <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur dark:border-gray-800 dark:bg-gray-900/80">
          <nav className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
            <Link href="/" className="text-lg font-bold">
              Blog
            </Link>
            <div className="flex items-center gap-3">
              <Link
                href="/blog"
                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                Series
              </Link>
              <ThemeToggle />
            </div>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

Key decisions:

- `sticky top-0` — navbar stays visible on scroll (important for mobile navigation)
- `backdrop-blur` — content shows through slightly, feels modern
- `h-14` — compact height, doesn't waste mobile screen space
- `max-w-6xl` — constrains on ultra-wide screens

## The Blog Layout with Sidebar

`app/blog/[...slug]/layout.tsx`:

```tsx
export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 lg:grid lg:grid-cols-[220px_1fr] lg:gap-8">
      {children}
    </div>
  );
}
```

On desktop: 220px sidebar + fluid content. On mobile: single column, sidebar hidden.

## The Mobile Sidebar (Drawer)

Create `app/blog/components/MobileSidebar.tsx`:

```tsx
"use client";

import { useState } from "react";
import Link from "next/link";

interface Props {
  series: string;
  chapters: string[];
  currentSlug: string;
}

export function MobileSidebar({ series, chapters, currentSlug }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Trigger — only visible on mobile */}
      <button
        onClick={() => setOpen(true)}
        className="fixed right-4 bottom-4 z-40 rounded-full bg-teal-600 p-3 text-white shadow-lg lg:hidden"
        aria-label="Open chapter list"
      >
        ☰
      </button>

      {/* Overlay */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="absolute top-0 bottom-0 left-0 w-72 overflow-y-auto bg-white p-6 shadow-xl dark:bg-gray-900">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-500 uppercase">
                {series.replace(/-/g, " ")}
              </h2>
              <button onClick={() => setOpen(false)} className="text-xl text-gray-400">
                ×
              </button>
            </div>
            <nav className="space-y-1">
              {chapters.map((ch) => {
                const slug = ch.replace(".md", "");
                const isActive = slug === currentSlug;
                const label = slug.replace("chapter-", "").replace(/-/g, " ");
                return (
                  <Link
                    key={ch}
                    href={`/blog/${series}/${slug}`}
                    onClick={() => setOpen(false)}
                    className={`block rounded px-3 py-2 text-sm ${
                      isActive
                        ? "bg-teal-50 font-medium text-teal-700 dark:bg-teal-900/30 dark:text-teal-300"
                        : "text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
                    }`}
                  >
                    {label}
                  </Link>
                );
              })}
            </nav>
          </aside>
        </div>
      )}
    </>
  );
}
```

A floating action button (bottom-right) opens a slide-in drawer on mobile. On desktop (`lg:`), it's hidden — the sidebar is always visible.

## Mobile Code Blocks

Code blocks are the #1 mobile layout breaker. Long lines overflow. The fix:

```tsx
// In MarkdownCode.tsx
<SyntaxHighlighter
  language={lang}
  style={isDark ? oneDark : oneLight}
  customStyle={{
    margin: "1rem 0",
    borderRadius: "0.5rem",
    fontSize: "0.8rem", // Slightly smaller on mobile
    lineHeight: 1.6,
    overflowX: "auto", // Horizontal scroll, not overflow
  }}
  wrapLongLines={false} // Don't wrap — scroll instead
>
  {code}
</SyntaxHighlighter>
```

Key: `overflowX: "auto"` + `wrapLongLines={false}`. The code block scrolls horizontally. The page layout stays intact.

Add a subtle scroll indicator:

```css
/* globals.css */
.prose pre {
  position: relative;
}
.prose pre::after {
  content: "";
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 30px;
  background: linear-gradient(to right, transparent, rgba(0, 0, 0, 0.1));
  pointer-events: none;
  border-radius: 0 0.5rem 0.5rem 0;
}
```

A fade on the right edge hints "there's more — scroll."

## Mobile Interactive Components

### Quiz — Bigger Tap Targets

```tsx
// Quiz.tsx — mobile-friendly buttons
<button
  className="w-full text-left px-4 py-4 rounded-md border text-sm
             min-h-[48px]  /* minimum tap target */
             active:scale-[0.98] transition"
>
```

48px minimum height. Full width. `active:scale` gives tactile feedback on tap.

### CodePlayground — Full Width

```tsx
<textarea
  className="w-full bg-gray-900 p-3 font-mono text-xs text-gray-100 sm:p-4 sm:text-sm"
  style={{ height: "150px" }} // Shorter on mobile
/>
```

Smaller font, less padding, shorter height on mobile. Still usable.

### StepVisualizer — Swipe Support

```tsx
// Add touch support for prev/next
const [touchStart, setTouchStart] = useState(0);

<div
  onTouchStart={(e) => setTouchStart(e.touches[0].clientX)}
  onTouchEnd={(e) => {
    const diff = touchStart - e.changedTouches[0].clientX;
    if (diff > 50) setCurrent(Math.min(steps.length - 1, current + 1));
    if (diff < -50) setCurrent(Math.max(0, current - 1));
  }}
>
  {/* visualizer content */}
</div>;
```

Swipe left = next step. Swipe right = previous. Natural on mobile.

## Responsive Typography

```css
/* globals.css */
.prose {
  font-size: 1rem; /* 16px base on mobile */
}

@media (min-width: 640px) {
  .prose {
    font-size: 1.125rem; /* 18px on tablet+ */
  }
}

.prose h1 {
  font-size: clamp(1.5rem, 4vw, 2.25rem);
}
.prose h2 {
  font-size: clamp(1.25rem, 3vw, 1.75rem);
}
```

`clamp()` scales headings fluidly between mobile and desktop. No breakpoint jumps.

## The Reading Progress Bar

A thin bar at the top showing how far through the chapter the reader is:

```tsx
"use client";

import { useEffect, useState } from "react";

export function ReadingProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const update = () => {
      const scrolled = window.scrollY;
      const total = document.body.scrollHeight - window.innerHeight;
      setProgress(total > 0 ? (scrolled / total) * 100 : 0);
    };
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);

  return (
    <div
      className="fixed top-14 left-0 z-50 h-0.5 bg-teal-500 transition-all duration-75"
      style={{ width: `${progress}%` }}
    />
  );
}
```

Sits just below the navbar. Gives the reader a sense of position in long chapters.

## Testing Mobile

Don't just resize your browser. Test with:

1. **Chrome DevTools** — Device toolbar (Ctrl+Shift+M)
2. **Real device** — `npm run dev`, open your local IP on your phone
3. **Lighthouse** — Accessibility audit catches tap target issues

Common mobile bugs to check:

- [ ] Code blocks don't break layout (horizontal scroll works)
- [ ] Quiz buttons are tappable (≥48px height)
- [ ] Navbar doesn't cover content on scroll
- [ ] Images scale down (max-width: 100%)
- [ ] No horizontal page scroll (nothing overflows the viewport)

---

## What's Next

The layout works on every screen. But is it _fast_? Chapter 11 digs into performance — bundle analysis, image optimization, font loading, and getting a 95+ Lighthouse score on a content-heavy site.
