# Chapter 1: Your First Page

[← Overview](chapter-00-overview.md) | [Chapter 2: Dynamic Routes →](chapter-02-dynamic-routes.md)

---

## The Task

Raj: "I want to see 'TrailBlazer' in the browser by lunch. Home page, about page, a nav bar. Nothing fancy — just prove the framework works."

---

## Create the Project

```bash
npx create-next-app@latest trailblazer --typescript --tailwind --eslint --app --src-dir
cd trailblazer
npm run dev
```

The CLI asks questions. We chose: TypeScript, Tailwind, ESLint, App Router, `src/` directory.

```
  ▲ Next.js 15.x
  - Local:    http://localhost:3000
  - Ready in 1.2s
```

Open `http://localhost:3000`. You see the default Next.js page. Time to replace it.

---

## The App Router: Files Are Routes

This is the core mental model. No route configuration file. No `<Route>` components. The folder structure inside `src/app/` IS your routing:

```
src/app/
├── layout.tsx      → wraps ALL pages (the shell)
├── page.tsx        → / (home)
├── about/
│   └── page.tsx    → /about
└── globals.css     → global styles
```

**Rules:**
- `page.tsx` = a route (publicly accessible page)
- `layout.tsx` = a wrapper (persists across navigations)
- Folder name = URL segment
- No `page.tsx` in a folder = not a route (just organization)

---

## The Root Layout

Every Next.js app has one root layout. It wraps every page. It renders the `<html>` and `<body>` tags.

```tsx
// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: "TrailBlazer",
    template: "%s | TrailBlazer",
  },
  description: "Find your next hiking adventure",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen bg-stone-50 text-stone-900">
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-stone-200">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-8">
            <Link href="/" className="text-xl font-bold text-emerald-700">
              🥾 TrailBlazer
            </Link>
            <Link href="/trails" className="text-stone-600 hover:text-emerald-700 transition-colors">
              Trails
            </Link>
            <Link href="/about" className="text-stone-600 hover:text-emerald-700 transition-colors">
              About
            </Link>
            <Link href="/profile" className="ml-auto text-stone-600 hover:text-emerald-700 transition-colors">
              Profile
            </Link>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

### What's Happening

- `next/font/google` — downloads Inter at build time, self-hosts it. No external requests. No layout shift.
- `metadata` — sets `<title>` and `<meta>` tags. The `template` means child pages can set their own title and it'll append "| TrailBlazer".
- `Link` — Next.js's navigation component. Prefetches pages on hover. No full page reload.
- `{children}` — where the current page renders.

This layout renders ONCE and persists. When you navigate from `/` to `/about`, only the `{children}` part swaps. The nav doesn't re-render. No flash.

---

## The Home Page

```tsx
// src/app/page.tsx
export default function Home() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-16">
      <div className="text-center">
        <h1 className="text-5xl font-bold tracking-tight">
          Find Your Next
          <span className="text-emerald-600"> Adventure</span>
        </h1>
        <p className="mt-4 text-xl text-stone-600 max-w-2xl mx-auto">
          Discover trails, read reviews from real hikers, and plan your next
          outdoor experience.
        </p>
        <div className="mt-8">
          <Link
            href="/trails"
            className="inline-block bg-emerald-600 text-white px-8 py-3 rounded-lg
                       font-medium hover:bg-emerald-700 transition-colors"
          >
            Explore Trails
          </Link>
        </div>
      </div>
    </div>
  );
}
```

This is a **Server Component**. It runs on the server, sends HTML to the browser. No JavaScript shipped for this component. The browser gets static HTML — fast, SEO-friendly, zero bundle cost.

---

## The About Page

```tsx
// src/app/about/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",  // renders as "About | TrailBlazer" (template from layout)
};

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-bold">About TrailBlazer</h1>
      <p className="mt-4 text-stone-600 leading-relaxed">
        TrailBlazer is a community-driven platform for hikers. We believe the
        best trail recommendations come from people who've actually walked them —
        not algorithms.
      </p>
      <p className="mt-4 text-stone-600 leading-relaxed">
        Every review is from a verified hiker. Every photo is from the trail.
        No stock images. No sponsored content.
      </p>
    </div>
  );
}
```

Notice: `metadata` is exported as a constant. Next.js reads it at build/render time and injects the appropriate `<head>` tags. No `<Helmet>` library needed.

---

## How Rendering Works

When someone visits `http://localhost:3000`:

```
1. Next.js receives the request
2. Finds src/app/page.tsx (matches /)
3. Renders layout.tsx (the shell)
4. Renders page.tsx (the content) inside the layout
5. Sends complete HTML to the browser
6. Browser displays the page immediately
7. JavaScript loads → page becomes interactive (hydration)
```

The user sees content at step 6 — before JavaScript even loads. That's the power of server rendering.

---

## The File System = The Router

Let's add more structure:

```
src/app/
├── layout.tsx              → / (root layout, wraps everything)
├── page.tsx                → /
├── about/
│   └── page.tsx            → /about
├── trails/
│   ├── page.tsx            → /trails
│   └── [slug]/
│       └── page.tsx        → /trails/mount-rainier, /trails/olympic-coast, etc.
├── profile/
│   ├── layout.tsx          → wraps all /profile/* pages
│   ├── page.tsx            → /profile
│   └── reviews/
│       └── page.tsx        → /profile/reviews
└── admin/
    └── page.tsx            → /admin
```

| File/Folder | URL | Purpose |
|---|---|---|
| `app/page.tsx` | `/` | Home page |
| `app/about/page.tsx` | `/about` | About page |
| `app/trails/page.tsx` | `/trails` | Trail listing |
| `app/trails/[slug]/page.tsx` | `/trails/:slug` | Dynamic trail detail |
| `app/profile/page.tsx` | `/profile` | User profile |
| `app/profile/layout.tsx` | — | Sidebar for profile section |
| `app/admin/page.tsx` | `/admin` | Admin dashboard |

The `[slug]` folder with brackets = dynamic segment. We'll build that in Chapter 2.

---

## Special Files

Next.js reserves certain filenames for specific purposes:

| File | Purpose |
|---|---|
| `page.tsx` | The route's UI (required to make a folder a route) |
| `layout.tsx` | Shared wrapper (persists across child navigations) |
| `loading.tsx` | Loading UI (shown while page data loads) |
| `error.tsx` | Error UI (catches errors in this route segment) |
| `not-found.tsx` | 404 UI |
| `template.tsx` | Like layout but re-mounts on navigation |
| `route.ts` | API endpoint (no UI) |

We'll use each of these as we need them.

---

## Verify

```bash
npm run dev
```

- Visit `http://localhost:3000` → home page with hero section
- Visit `http://localhost:3000/about` → about page
- Click nav links → instant navigation, no full reload
- View source (Ctrl+U) → full HTML content visible (server-rendered)

That last point is key. View the page source. You'll see your actual content in the HTML — not an empty `<div id="root">`. Google sees this too.

Raj walks by. "Looks good. Now I need 500 trail pages. Each with its own URL, its own title, its own content."

That's dynamic routes. Chapter 2.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
src/app/page.tsx                │ Route at /
src/app/x/page.tsx              │ Route at /x
src/app/layout.tsx              │ Wraps all pages (persistent shell)
export const metadata           │ Sets <title>, <meta> tags
import Link from "next/link"    │ Client-side navigation (no reload)
next/font/google                │ Self-hosted fonts (no CLS)
Server Component (default)      │ Runs on server, ships 0 JS
────────────────────────────────┴──────────────────────────────────────
```

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Dynamic Routes →](chapter-02-dynamic-routes.md)
